# TP5 — Dinámica peatonal: evacuación con esquema híbrido (problema 2)

Grupo 07, comisión S: Eugenio Migliaro, Francisco Costa y Franco Branda. Entrega: PDF de la presentación y ZIP del motor, por Campus, antes del 16/11/2026 a las 13 h [TP05, p. 1].

Evacuación de N = 500 agentes de una sala de 50 m con una puerta de 0,8 m, con el SFM sin fuerza social [TP05, p. 3] [B26], resuelta con tres esquemas: TSDMD puro, EDMD puro e híbrido EDMD + TSDMD [TP05, p. 4]. El motor está en C++20; el post-proceso y las animaciones son programas aparte, en Python, que leen los archivos de texto que escribe el motor [TP05, p. 1].

## Estructura

| Carpeta | Contenido |
|---|---|
| `cpp/include/tp5`, `cpp/src` | Motor: modelo y sala, condiciones iniciales, fuerzas del SFM con celdas, Beeman, EDMD (patadas o relajación analítica), híbrido, choque aislado, E/S y CLI |
| `cpp/tests` | Pruebas del motor |
| `python/src/tp5analysis` | Lectura de salidas, observables (población, t_evac, caudal, modos), estadística, estilo de figuras y animación |
| `python/tests` | Pruebas del post-proceso |
| `scripts` | Corridas de cada estudio, resúmenes y material de la consulta |
| `experiments/results` | Resúmenes de los estudios (`experiments/raw` y `experiments/logs` no se versionan) |
| `consulta` | Figuras y animaciones para la consulta del 06/11 sobre los atascos |
| `docs/decisiones.md` | Decisiones de modelado, implementación y análisis, con sus resultados |
| `docs/recomendaciones-modificadas.md` | Decisiones en las que el grupo modificó la recomendación del agente de programación |

## Uso

```bash
make release          # motor
make test             # pruebas de C++ y de Python
make dt               # cada estudio: corre lo que falta y resume (ver Makefile)
```

```bash
cpp/build/release/tp5 evacuate --scheme hybrid --t-star 0.05 --dt 2e-3 --seed 1 --output-dt 0.1 --output corrida.txt
cpp/build/release/tp5 collision --dt 1e-3 --offset 0.5
```

`tp5 --help` lista todas las opciones. La salida tiene una cabecera `#` con los parámetros y un renglón `agent <id> <radio> <masa>` por agente. Después vienen, en orden de tiempo:

- cuadros `frame <t> <adentro>`, cada `--output-dt`, con un renglón `<id> x y vx vy modo` por agente (modo 0 = TSDMD, 1 = EDMD);
- los instantes de salida `exit <t> <id>`;
- los cambios de modo `mode <t> <id> <modo>`.

El pie resume la corrida e incluye `clogged 1` si terminó por atasco (300 s sin salidas). Python usa `python/.venv` (`make python-env`) o, si no existe, el entorno del TP3. `TP5_WORKERS` fija cuántas corridas van en paralelo.

## Tiempos de ejecución (puntos c y d)

Se miden todos en una misma computadora, con el mismo commit, sin otras tareas y con 4 corridas a la vez: `make tiempos-c` y `make tiempos-d`. El script guarda los datos del equipo en `experiments/results/maquina.json`.
