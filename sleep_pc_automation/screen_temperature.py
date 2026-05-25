from __future__ import annotations

import ctypes
from ctypes import wintypes
import math


DAY_TEMPERATURE_K = 6000
# Both active adapters accept 3300 K; a stronger 3200 K ramp is rejected.
NIGHT_TEMPERATURE_K = 3300
GAMMA = 1.0
Ramp = ctypes.c_ushort * (256 * 3)
DISPLAY_DEVICE_ATTACHED_TO_DESKTOP = 0x00000001


class DisplayDevice(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("DeviceName", wintypes.WCHAR * 32),
        ("DeviceString", wintypes.WCHAR * 128),
        ("StateFlags", wintypes.DWORD),
        ("DeviceID", wintypes.WCHAR * 128),
        ("DeviceKey", wintypes.WCHAR * 128),
    ]


def log(message: str) -> None:
    print(f"[screen-temperature] {message}")


def temperature_rgb(kelvin: int) -> tuple[float, float, float]:
    temperature = max(1000, min(40000, kelvin)) / 100
    if temperature <= 66:
        red = 255
        green = 99.4708025861 * math.log(temperature) - 161.1195681661
        blue = 0 if temperature <= 19 else 138.5177312231 * math.log(temperature - 10) - 305.0447927307
    else:
        red = 329.698727446 * ((temperature - 60) ** -0.1332047592)
        green = 288.1221695283 * ((temperature - 60) ** -0.0755148492)
        blue = 255
    channels = (red, green, blue)
    return tuple(max(0, min(255, channel)) / 255 for channel in channels)


def build_ramp(kelvin: int) -> Ramp:
    red, green, blue = temperature_rgb(kelvin)
    ramp = Ramp()
    for channel_position, channel_factor in enumerate((red, green, blue)):
        for value in range(256):
            normalized = (value / 255) ** (1 / GAMMA)
            ramp[channel_position * 256 + value] = min(65535, int(65535 * normalized * channel_factor))
    return ramp


def apply_temperature(kelvin: int) -> int:
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    user32.EnumDisplayDevicesW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.POINTER(DisplayDevice),
        wintypes.DWORD,
    ]
    user32.EnumDisplayDevicesW.restype = wintypes.BOOL
    gdi32.CreateDCW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.c_void_p]
    gdi32.CreateDCW.restype = wintypes.HDC
    gdi32.SetDeviceGammaRamp.argtypes = [wintypes.HDC, ctypes.c_void_p]
    gdi32.SetDeviceGammaRamp.restype = wintypes.BOOL
    gdi32.DeleteDC.argtypes = [wintypes.HDC]
    gdi32.DeleteDC.restype = wintypes.BOOL
    ramp = build_ramp(kelvin)
    applied = 0
    position = 0
    while True:
        device = DisplayDevice()
        device.cb = ctypes.sizeof(device)
        if not user32.EnumDisplayDevicesW(None, position, ctypes.byref(device), 0):
            break
        position += 1
        if not device.StateFlags & DISPLAY_DEVICE_ATTACHED_TO_DESKTOP:
            continue
        device_context = gdi32.CreateDCW("DISPLAY", device.DeviceName, None, None)
        if not device_context:
            continue
        try:
            if gdi32.SetDeviceGammaRamp(device_context, ctypes.byref(ramp)):
                log(f"Perfil aplicado en {device.DeviceName} ({device.DeviceString}).")
                applied += 1
        finally:
            gdi32.DeleteDC(device_context)
    if not applied:
        raise RuntimeError("Windows no acepto el perfil de color para ningun monitor.")
    log(f"Temperatura {kelvin} K aplicada en {applied} monitor(es).")
    return applied


def apply_day_profile() -> int:
    return apply_temperature(DAY_TEMPERATURE_K)


def apply_night_profile() -> int:
    return apply_temperature(NIGHT_TEMPERATURE_K)


if __name__ == "__main__":
    apply_night_profile()
