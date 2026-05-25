# Sleep PC Automation

Proyecto pequeno en Python para automatizar un modo noche y un modo manana en una computadora personal con Windows.

El objetivo es hacer ajustes visuales simples para dormir mejor:

- De noche: baja el brillo al 10%, activa modo oscuro y aplica color calido.
- A la manana: sube el brillo al 60%, conserva modo oscuro y aplica color apenas calido.

El script NO cierra aplicaciones, NO mata procesos y NO usa `taskkill`. No cierra Slack, navegador, VS Code, juegos, Discord, Telegram ni ninguna otra app.

## Requisitos

- Windows.
- Python 3.
- Dependencia incluida en `requirements.txt`:

```powershell
pip install -r requirements.txt
```

## Ejecutar modo noche manualmente

Desde la carpeta del proyecto:

```powershell
python night_mode.py
```

Esto intenta:

- Detectar los monitores disponibles.
- Bajar el brillo a `NIGHT_BRIGHTNESS = 10` en cada monitor detectado.
- Configurar `AppsUseLightTheme = 0`.
- Configurar `SystemUsesLightTheme = 0`.
- Aplicar el perfil calido nocturno (`3300 K`) en ambos monitores.

## Ejecutar modo manana manualmente

Desde la carpeta del proyecto:

```powershell
python morning_mode.py
```

Esto intenta:

- Detectar los monitores disponibles.
- Subir el brillo a `MORNING_BRIGHTNESS = 60` en cada monitor detectado.
- Mantener `AppsUseLightTheme = 0`.
- Mantener `SystemUsesLightTheme = 0`.
- Aplicar el perfil diurno apenas calido (`6000 K`) en ambos monitores.

## Permiso temporal para estudiar o trabajar

Para salir del modo noche sin apagar la rutina diaria, ejecuta:

```powershell
pythonw night_exception.py
```

La ventana solicita un motivo obligatorio y permite habilitar colores por `30 minutos`,
`1 hora`, `2 horas` o hasta las `08:30`. Aplica el color diurno suave mientras dure
la excepcion y aumenta el brillo, pero el tema de Windows queda siempre oscuro. Al
vencer el permiso, el brillo bajo y color nocturno se restauran automaticamente si
todavia es horario nocturno. Tambien hay un boton para volver al modo noche
inmediatamente.

Las excepciones se registran localmente en `night_override_log.jsonl`. Si la tarea de
las `23:30` se ejecuta durante un permiso vigente, lo respeta y no vuelve a oscurecer
la pantalla antes de tiempo.

## Configuracion editable

En `night_mode.py`:

```python
NIGHT_BRIGHTNESS = 10
```

En `morning_mode.py`:

```python
MORNING_BRIGHTNESS = 60
```

## Limitaciones

- La programacion nativa de Luz nocturna se apaga al aplicar un perfil para evitar superponer filtros.
- Algunas notebooks o monitores pueden no permitir cambiar brillo por software.
- El modo oscuro o claro puede requerir reiniciar algunas apps para que se vea aplicado.

## Color calido

`screen_temperature.py` aplica la temperatura directamente sobre ambos monitores, sin
depender de que `Luz nocturna` de Windows refresque correctamente. Windows tenia
guardada una intensidad nocturna de `75%`. En estas dos placas el perfil calido mas
intenso aceptado directamente es `3300 K` (a `3200 K` Windows lo rechaza). El perfil
diurno queda apenas calido en `6000 K`.

Si la programacion nativa de `Luz nocturna` llegara a encenderse, los modos la apagan
antes de aplicar su propio perfil para evitar superponer dos filtros.

## Si solo cambia un monitor

Algunos monitores externos no permiten cambiar brillo por software. Si solo cambia el brillo de una pantalla, revisa el menu fisico del monitor externo y busca una opcion llamada `DDC/CI`. Si existe, activala.

Si el monitor no soporta DDC/CI, puede que el brillo solo se pueda cambiar manualmente desde los botones del monitor.

## Automatizacion

Este proyecto no crea servicios en background, no deja loops corriendo y no programa tareas por si mismo. Para ejecutarlo por horario, usa el Programador de tareas de Windows siguiendo `setup_tasks_windows.md`.
