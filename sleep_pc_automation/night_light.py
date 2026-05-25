from __future__ import annotations

from pathlib import Path
import subprocess
import winreg


# Read the Night Light state from CloudStore, then toggle it through Windows Settings
# so Windows applies the visible color-temperature change immediately.
REGISTRY_PATH = (
    r"Software\Microsoft\Windows\CurrentVersion\CloudStore\Store\DefaultAccount\Current"
    r"\default$windows.data.bluelightreduction.bluelightreductionstate"
    r"\windows.data.bluelightreduction.bluelightreductionstate"
)
VALUE_NAME = "Data"
HEADER = b"\x43\x42\x01\x00"
ENABLED_FIELD = b"\x10\x00"
TOGGLE_SCRIPT = Path(__file__).resolve().with_name("toggle_night_light.ps1")


def _log(message: str) -> None:
    print(f"[night-light] {message}")


def _read_varint(data: bytes, position: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while position < len(data):
        byte = data[position]
        position += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, position
        shift += 7
    raise ValueError("Blob de Luz nocturna incompleto.")


def _read_data() -> bytes:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_PATH) as key:
        data, value_type = winreg.QueryValueEx(key, VALUE_NAME)
    if value_type != winreg.REG_BINARY or not isinstance(data, bytes):
        raise ValueError("El estado de Luz nocturna no es REG_BINARY.")
    return data


def _parse_enabled(data: bytes) -> bool:
    inner_start = data.find(HEADER, len(HEADER))
    if inner_start < 3 or data[inner_start - 3 : inner_start - 1] != b"\x2b\x0e":
        raise ValueError("No se encontro el payload esperado de Luz nocturna.")
    inner_size, payload_start = _read_varint(data, inner_start - 1)
    if payload_start != inner_start:
        raise ValueError("Longitud inesperada del payload de Luz nocturna.")
    inner = data[inner_start : inner_start + inner_size]
    if not inner.startswith(HEADER):
        raise ValueError("Encabezado inesperado de Luz nocturna.")
    return inner[len(HEADER) : len(HEADER) + len(ENABLED_FIELD)] == ENABLED_FIELD


def is_enabled() -> bool:
    return _parse_enabled(_read_data())


def disable() -> bool:
    if not is_enabled():
        _log("Luz nocturna de Windows ya estaba apagada.")
        return False
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(TOGGLE_SCRIPT),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    output = result.stdout.strip()
    _log(output or "Luz nocturna de Windows apagada.")
    return True


if __name__ == "__main__":
    print("encendida" if is_enabled() else "apagada")
