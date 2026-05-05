# Programar tareas en Windows

Este proyecto debe automatizarse con el Programador de tareas de Windows. Los scripts no crean servicios, no quedan corriendo en segundo plano y no cierran aplicaciones.

Adapta las rutas de los ejemplos a tu usuario y a la ubicacion real del proyecto.

Ejemplo de carpeta:

```text
C:\Users\santi\OneDrive\Escritorio\sleep\sleep_pc_automation
```

## Tarea 1: modo noche a las 23:30

1. Abre el Programador de tareas de Windows.
2. Selecciona "Crear tarea basica...".
3. Nombre sugerido: `Sleep PC - Modo noche`.
4. En desencadenador, elige "Diariamente".
5. Configura la hora: `23:30`.
6. En accion, elige "Iniciar un programa".
7. En "Programa o script", escribe la ruta a Python.

Ejemplo:

```text
python
```

Si Windows no encuentra `python`, usa la ruta completa. Ejemplo:

```text
C:\Users\santi\AppData\Local\Programs\Python\Python312\python.exe
```

8. En "Agregar argumentos", escribe:

```text
night_mode.py
```

9. En "Iniciar en", escribe la carpeta del proyecto.

Ejemplo:

```text
C:\Users\santi\OneDrive\Escritorio\sleep\sleep_pc_automation
```

10. Guarda la tarea.

## Tarea 2: modo manana a las 08:30

1. Abre el Programador de tareas de Windows.
2. Selecciona "Crear tarea basica...".
3. Nombre sugerido: `Sleep PC - Modo manana`.
4. En desencadenador, elige "Diariamente".
5. Configura la hora: `08:30`.
6. En accion, elige "Iniciar un programa".
7. En "Programa o script", escribe la ruta a Python.

Ejemplo:

```text
python
```

Si Windows no encuentra `python`, usa la ruta completa. Ejemplo:

```text
C:\Users\santi\AppData\Local\Programs\Python\Python312\python.exe
```

8. En "Agregar argumentos", escribe:

```text
morning_mode.py
```

9. En "Iniciar en", escribe la carpeta del proyecto.

Ejemplo:

```text
C:\Users\santi\OneDrive\Escritorio\sleep\sleep_pc_automation
```

10. Guarda la tarea.

## Notas

- El campo "Iniciar en" debe ser la carpeta donde estan `night_mode.py` y `morning_mode.py`.
- Si usas un entorno virtual, en "Programa o script" puedes poner la ruta al `python.exe` de ese entorno.
- Puedes probar cada tarea manualmente con clic derecho sobre la tarea y luego "Ejecutar".

## Luz azul / Luz nocturna

Bajar brillo no es lo mismo que reducir luz azul. El brillo baja la intensidad general de la pantalla, pero no reemplaza un filtro de temperatura de color.

El modo oscuro ayuda a que la computadora sea menos estimulante, pero tampoco reemplaza Windows Night Light / Luz nocturna. No se recomienda automatizar Night Light desde Python porque puede ser fragil entre versiones de Windows.

Configura manualmente Windows Night Light:

```text
Configuracion -> Sistema -> Pantalla -> Luz nocturna -> Programar
```

Horario sugerido:

```text
23:30 a 08:30
```

Intensidad sugerida:

```text
70% a 100%
```
