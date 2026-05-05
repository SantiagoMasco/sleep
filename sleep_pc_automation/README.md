# Sleep PC Automation

Proyecto pequeno en Python para automatizar un modo noche y un modo manana en una computadora personal con Windows.

El objetivo es hacer ajustes visuales simples para dormir mejor:

- De noche: baja el brillo al 10% y activa modo oscuro de Windows.
- A la manana: sube el brillo al 60% y activa modo claro de Windows.

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

## Ejecutar modo manana manualmente

Desde la carpeta del proyecto:

```powershell
python morning_mode.py
```

Esto intenta:

- Detectar los monitores disponibles.
- Subir el brillo a `MORNING_BRIGHTNESS = 60` en cada monitor detectado.
- Configurar `AppsUseLightTheme = 1`.
- Configurar `SystemUsesLightTheme = 1`.

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

- Windows Night Light / Luz nocturna conviene configurarla manualmente desde Windows.
- Algunas notebooks o monitores pueden no permitir cambiar brillo por software.
- El modo oscuro o claro puede requerir reiniciar algunas apps para que se vea aplicado.

## Luz azul / Luz nocturna

Bajar brillo no es lo mismo que reducir luz azul. El brillo reduce la intensidad general de la pantalla, pero no cambia necesariamente la temperatura de color.

El modo oscuro ayuda a que la computadora sea menos estimulante, pero no reemplaza Windows Night Light / Luz nocturna. Automatizar Night Light desde Python puede ser fragil, asi que lo recomendado es configurarla manualmente desde Windows:

Configuracion -> Sistema -> Pantalla -> Luz nocturna -> Programar.

Horario sugerido:

```text
23:30 a 08:30
```

Intensidad sugerida:

```text
70% a 100%
```

## Si solo cambia un monitor

Algunos monitores externos no permiten cambiar brillo por software. Si solo cambia el brillo de una pantalla, revisa el menu fisico del monitor externo y busca una opcion llamada `DDC/CI`. Si existe, activala.

Si el monitor no soporta DDC/CI, puede que el brillo solo se pueda cambiar manualmente desde los botones del monitor.

## Automatizacion

Este proyecto no crea servicios en background, no deja loops corriendo y no programa tareas por si mismo. Para ejecutarlo por horario, usa el Programador de tareas de Windows siguiendo `setup_tasks_windows.md`.
