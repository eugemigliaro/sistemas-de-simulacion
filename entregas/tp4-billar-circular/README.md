# TP4 — Dinámica molecular regida por el paso temporal

Grupo 07, comisión S: Eugenio Migliaro, Francisco Costa y Franco Branda. Entrega: PDF de la presentación y ZIP del motor, por campus, antes del 23/10/2026 a las 13 h [TP04, p. 1].

- **Sistema 1:** oscilador amortiguado integrado con Beeman, Verlet original, Velocity Verlet y Euler predictor-corrector. Se compara con la solución analítica.
- **Sistema 2:** billar circular con contactos elásticos, integrado con Verlet original.

El motor está en C++20. El post-proceso y las animaciones son programas aparte, en Python, que leen los archivos de texto que escribe el motor [TP04, p. 1] [COR02].

## Estructura

| Carpeta | Contenido |
|---|---|
| `cpp/include/tp4`, `cpp/src` | Motor: modelo, oscilador, condiciones iniciales, fuerzas con celdas, Verlet, E/S y CLI |
| `cpp/tests` | Pruebas del motor (C++ y CLI) |
| `cpp/bench` | Harness del punto 2.1.b: cronometra el TP4 y el motor del TP3; no se entrega |
| `python/src/tp4analysis` | Lectura de salidas, ECM, energía, Fu y t90, histogramas y ajuste, estadística y animación |
| `python/tests` | Pruebas del post-proceso |
| `scripts` | Corridas de cada estudio, figuras, videos, presentación y empaquetado |
| `experiments/results` | Resultados por realización y resúmenes (`experiments/raw` y `experiments/logs` no se versionan) |
| `presentacion` | Fuente Beamer, figuras, videos, PPTX para exponer y guion |
| `entrega-final` | Los dos archivos que se suben al campus |
| `docs/decisiones.md` | Decisiones de modelado, implementación y análisis |

## Uso

```bash
make release           # motor
make test              # pruebas de C++, de la CLI y de Python
make sanitize          # pruebas con AddressSanitizer y UBSan
make experiments       # todos los estudios menos el tiempo de ejecución
make benchmark         # 2.1.b: secuencial, con la computadora sin otras tareas
make figures videos presentation package
```

Python usa `python/.venv` (`make python-env`). Si no existe, usa el entorno del TP3, que tiene las mismas dependencias. Las corridas se pueden interrumpir: al volver a lanzarlas se saltean las salidas ya escritas. `TP4_WORKERS` fija cuántas corren en paralelo.

```bash
cpp/build/release/tp4 oscillator --integrator beeman --dt 1e-4 --output beeman.txt
cpp/build/release/tp4 billiard --n 100 --dt 2e-5 --tf 100 --output-every 2500 --x0 0.0175 --seed 1 --output billar.txt
```

`tp4 --help` lista todas las opciones. El billar escribe una cabecera `#` con los parámetros y, cada `output-every` pasos, un cuadro `frame <paso> <tiempo>` seguido de N líneas `x y vx vy color`, con color 0 para fresca y 1 para usada.

## Entrega

`make package` arma `entrega-final/SdS_TP4_2026Q2G07CS_Codigo.zip` solo con el motor (`cpp/Makefile`, headers y fuentes) y comprueba que pese menos de 100 KB y que compile y corra desde una carpeta vacía. `make presentation` escribe el PDF con el nombre oficial en la misma carpeta y el PPTX con los videos en `presentacion/`.
