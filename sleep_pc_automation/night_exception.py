from __future__ import annotations

import argparse
from datetime import datetime, time, timedelta
import json
from pathlib import Path
import subprocess
import sys
import time as time_module
import tkinter as tk
from tkinter import messagebox, ttk
from uuid import uuid4


BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / "night_override_state.json"
LOG_FILE = BASE_DIR / "night_override_log.jsonl"
NIGHT_START = time(23, 30)
MORNING_END = time(8, 30)
DURATIONS = {
    "30 minutos": timedelta(minutes=30),
    "1 hora": timedelta(hours=1),
    "2 horas": timedelta(hours=2),
    "Hasta las 08:30": None,
}


def now_local() -> datetime:
    return datetime.now().astimezone()


def is_night_window(moment: datetime) -> bool:
    return moment.time() >= NIGHT_START or moment.time() < MORNING_END


def next_morning(moment: datetime) -> datetime:
    result = moment.replace(hour=8, minute=30, second=0, microsecond=0)
    if moment.time() >= MORNING_END:
        result += timedelta(days=1)
    return result


def read_state() -> dict[str, str] | None:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError):
        return None


def read_override() -> dict[str, str] | None:
    state = read_state()
    if state is None:
        return None
    try:
        expires_at = datetime.fromisoformat(state["expires_at"])
    except (KeyError, ValueError):
        return None

    if expires_at > now_local():
        return state
    return None


def active_override_summary() -> str | None:
    state = read_override()
    if state is None:
        return None
    expires_at = datetime.fromisoformat(state["expires_at"])
    return expires_at.strftime("%d/%m %H:%M")


def clear_override() -> None:
    STATE_FILE.unlink(missing_ok=True)


def append_log(action: str, reason: str, expires_at: datetime | None = None) -> None:
    entry = {
        "timestamp": now_local().isoformat(timespec="seconds"),
        "action": action,
        "reason": reason,
    }
    if expires_at is not None:
        entry["expires_at"] = expires_at.isoformat(timespec="seconds")
    with LOG_FILE.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(entry, ensure_ascii=True) + "\n")


def apply_day_mode() -> None:
    import morning_mode

    morning_mode.main()


def apply_night_mode(reason: str) -> None:
    import night_mode

    clear_override()
    append_log("restored_night_mode", reason)
    night_mode.main(force=True)


def pythonw_executable() -> Path:
    executable = Path(sys.executable)
    candidate = executable.with_name("pythonw.exe")
    return candidate if candidate.exists() else executable


def launch_restore_watcher(token: str, expires_at: datetime) -> None:
    command = [
        str(pythonw_executable()),
        str(Path(__file__).resolve()),
        "--watch",
        token,
        "--expires-at",
        expires_at.isoformat(),
    ]
    kwargs: dict[str, object] = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    subprocess.Popen(command, cwd=BASE_DIR, **kwargs)


def start_exception(reason: str, duration_label: str) -> datetime:
    moment = now_local()
    requested_delta = DURATIONS[duration_label]
    morning_limit = next_morning(moment)
    expires_at = morning_limit if requested_delta is None else min(moment + requested_delta, morning_limit)
    token = str(uuid4())
    state = {
        "token": token,
        "created_at": moment.isoformat(timespec="seconds"),
        "expires_at": expires_at.isoformat(timespec="seconds"),
        "reason": reason,
    }
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=True), encoding="utf-8")
    append_log("temporary_day_mode", reason, expires_at)
    apply_day_mode()
    launch_restore_watcher(token, expires_at)
    return expires_at


def restore_when_due(token: str, expires_at: datetime) -> None:
    remaining = (expires_at - now_local()).total_seconds()
    if remaining > 0:
        time_module.sleep(remaining)

    state = read_state()
    if state is None or state.get("token") != token:
        return

    if is_night_window(now_local()):
        apply_night_mode("Fin automatico de la excepcion temporal")
    else:
        clear_override()
        append_log("expired_in_morning", "La excepcion llego al horario de manana")


class ExceptionWindow:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Modo noche - permiso temporal")
        self.root.resizable(False, False)
        self.reason = tk.StringVar()
        self.duration = tk.StringVar(value="2 horas")
        self.status = tk.StringVar()
        self._build()
        self.refresh_status()

    def _build(self) -> None:
        frame = ttk.Frame(self.root, padding=18)
        frame.grid()
        ttk.Label(frame, text="Permiso excepcional de colores", font=("Segoe UI", 13, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            frame,
            text="Usalo solo para trabajar o estudiar. El modo noche vuelve automaticamente.",
            wraplength=450,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 14))
        ttk.Label(frame, textvariable=self.status, foreground="#555555").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 14)
        )
        ttk.Label(frame, text="Motivo obligatorio:").grid(row=3, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.reason, width=52).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(4, 12)
        )
        ttk.Label(frame, text="Duracion maxima:").grid(row=5, column=0, sticky="w")
        ttk.Combobox(
            frame,
            textvariable=self.duration,
            values=list(DURATIONS),
            state="readonly",
            width=20,
        ).grid(row=6, column=0, sticky="w", pady=(4, 16))
        ttk.Button(frame, text="Habilitar colores temporalmente", command=self.enable_temporarily).grid(
            row=7, column=0, sticky="w"
        )
        ttk.Button(frame, text="Volver al modo noche ahora", command=self.restore_now).grid(
            row=7, column=1, sticky="e", padx=(18, 0)
        )

    def refresh_status(self) -> None:
        until = active_override_summary()
        if until:
            self.status.set(f"Colores habilitados temporalmente hasta {until}.")
        elif is_night_window(now_local()):
            self.status.set("Horario nocturno activo.")
        else:
            self.status.set("Fuera del horario nocturno (23:30 a 08:30).")

    def enable_temporarily(self) -> None:
        reason = self.reason.get().strip()
        if len(reason) < 8:
            messagebox.showwarning("Motivo requerido", "Escribi un motivo breve (al menos 8 caracteres).")
            return
        expires_at = start_exception(reason, self.duration.get())
        self.refresh_status()
        messagebox.showinfo(
            "Permiso temporal activado",
            f"Los colores quedan habilitados hasta las {expires_at:%H:%M}.\n"
            "Despues vuelve el modo noche automaticamente.",
        )

    def restore_now(self) -> None:
        apply_night_mode("Restaurado manualmente desde el interruptor")
        self.refresh_status()
        messagebox.showinfo("Modo noche", "Modo noche aplicado nuevamente.")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Permiso temporal para salir del modo noche.")
    parser.add_argument("--watch", help="Token interno para restaurar el modo noche.")
    parser.add_argument("--expires-at", help="Vencimiento ISO para el restaurador.")
    parser.add_argument("--status", action="store_true", help="Muestra si existe una excepcion vigente.")
    args = parser.parse_args()

    if args.status:
        until = active_override_summary()
        print(f"Excepcion activa hasta {until}." if until else "No hay excepcion activa.")
        return
    if args.watch and args.expires_at:
        restore_when_due(args.watch, datetime.fromisoformat(args.expires_at))
        return
    ExceptionWindow().run()


if __name__ == "__main__":
    main()
