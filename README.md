# Integración Numérica — Regla del Trapecio Compuesto

Aplicación universitaria de la Unidad 3, Sesión 12 de Métodos Numéricos. Resuelve el ejercicio de estimación del tráfico acumulado de un servidor web mediante una implementación manual de la Regla del Trapecio Compuesto.

## Ejercicio oficial

La tasa de transferencia es

`R(t) = 10 + 5 sin(pi t / 4) + exp(0.15 t)`.

Se aproxima `integral_0^12 R(t) dt` con `n=4`. La aplicación muestra el paso, la malla, todas las evaluaciones, los pesos, la sustitución y el resultado `160.443697114248 Mb`.

La referencia analítica se calcula dinámicamente con

`F(t) = 10t - (20/pi)cos(pi t/4) + exp(0.15t)/0.15`.

Para `[0,12]`, el valor exacto es `166.39671187677126 Mb`.

## Arquitectura

- `metodos/trapecio.py`: algoritmo manual y traza matemática.
- `metodos/problema_servidor.py`: función oficial, primitiva y convergencia.
- `metodos/validaciones.py`: entradas finitas, intervalos y `n` entero positivo.
- `backend/app.py`: página y endpoint JSON.
- `backend/templates/index.html`: interfaz académica.
- `backend/static/`: estilos, interacción y dos gráficas Canvas.
- `tests/`: pruebas matemáticas, de validación, convergencia y API.

No se utiliza NumPy, SciPy, `trapz`, `trapezoid` ni otra rutina de integración.

## Ejecutar localmente

```powershell
Set-Location 'C:\Users\ismae\OneDrive\Documents\Universidad\Ingenieria_Sistemas\Ciclo_VI\Metodos Numericos\Proyectos de metodos\Unidad 3\Metodos Numericos - Integracion Numerica'
C:\Users\ismae\AppData\Local\Python\bin\python.exe -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m backend.app
```

Abrir `http://127.0.0.1:5003`.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall backend metodos tests
node --check backend/static/js/app.js
```

