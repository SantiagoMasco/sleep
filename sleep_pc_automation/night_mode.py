from __future__ import annotations

import subprocess

import screen_brightness_control as sbc


NIGHT_BRIGHTNESS = 10
REGISTRY_THEME_PATH = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
MonitorInfo = dict[str, object]


def log(message: str) -> None:
    print(f"[night-mode] {message}")


def describe_monitor(monitor: MonitorInfo, position: int) -> str:
    name = monitor.get("name") or monitor.get("model") or "Monitor sin nombre"
    method = normalize_method(monitor.get("method")) or "metodo desconocido"
    index = monitor.get("index", position)
    return f"{name} (index={index}, method={method})"


def normalize_method(method: object) -> str | None:
    if method is None:
        return None
    if isinstance(method, str):
        return method.lower()
    method_name = getattr(method, "__name__", None)
    if isinstance(method_name, str):
        return method_name.lower()
    return None


def get_monitors() -> list[MonitorInfo]:
    try:
        monitors = sbc.list_monitors_info()
        if not monitors:
            log("No se detectaron monitores para cambiar brillo.")
            return []

        log("Monitores detectados:")
        for position, monitor in enumerate(monitors):
            log(f"- {describe_monitor(monitor, position)}")
        return monitors
    except Exception as exc:
        log(f"No se pudieron detectar monitores: {exc}")
        return []


def set_monitor_brightness(monitor: MonitorInfo, level: int, position: int) -> None:
    label = describe_monitor(monitor, position)
    display = monitor.get("index", position)
    method = normalize_method(monitor.get("method"))

    try:
        if method:
            sbc.set_brightness(level, display=display, method=method)
        else:
            sbc.set_brightness(level, display=position)
        log(f"Brillo configurado en {level}% para {label}.")
    except Exception as exc:
        log(f"No se pudo cambiar el brillo de {label}: {exc}")


def set_brightness_for_all_monitors(level: int) -> None:
    monitors = get_monitors()
    if not monitors:
        return

    for position, monitor in enumerate(monitors):
        set_monitor_brightness(monitor, level, position)


def set_registry_dword(name: str, value: int) -> None:
    try:
        subprocess.run(
            [
                "reg",
                "add",
                REGISTRY_THEME_PATH,
                "/v",
                name,
                "/t",
                "REG_DWORD",
                "/d",
                str(value),
                "/f",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        log(f"{name} configurado en {value}.")
    except subprocess.CalledProcessError as exc:
        error = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        log(f"No se pudo configurar {name}: {error}")
    except Exception as exc:
        log(f"Error inesperado configurando {name}: {exc}")


def enable_dark_mode() -> None:
    set_registry_dword("AppsUseLightTheme", 0)
    set_registry_dword("SystemUsesLightTheme", 0)


def main() -> None:
    log("Iniciando modo noche.")
    set_brightness_for_all_monitors(NIGHT_BRIGHTNESS)
    enable_dark_mode()
    log("Modo noche finalizado. No se cerro ninguna aplicacion.")


if __name__ == "__main__":
    main()
