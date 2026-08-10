# TP1 — Búsqueda eficiente de partículas vecinas

Espacio de trabajo reproducible para resolver el TP1 mediante un motor de simulación en C++20 y herramientas de visualización y análisis en Python 3.

## Fuentes

- [Enunciado oficial TP01](../../material/catedra/practica/TP1_Enunciado.pdf).
- [Síntesis del Cell Index Method y alcance del TP1](../../wiki/temas/cell-index-method.md).
- [Archivos oficiales de ejemplo](../../material/extraido/EJ01/README.md).

Los originales permanecen en material/. Esta carpeta solo contiene decisiones, implementación, pruebas y resultados propios.

## Separación de responsabilidades

- C++: generación de partículas, validación geométrica, fuerza bruta, Cell Index Method y medición de tiempos.
- Python: lectura de resultados, figuras, exploración interactiva y análisis estadístico.
- Python no vuelve a calcular vecinos: consume la salida producida por C++.

## Contratos de archivos

### static.txt

1. Cantidad total de partículas N.
2. Longitud L del lado del dominio.
3. N filas con radio y propiedad de cada partícula.

La identidad de una partícula es su posición, comenzando en 1, dentro de las filas de partículas.

### dynamic.txt

1. Tiempo del estado.
2. N filas con x, y, vx y vy.

El TP1 usa un único estado temporal. Las velocidades se conservan por compatibilidad con el formato general, aunque la búsqueda de vecinos no las utiliza.

### neighbors.txt

Una fila por partícula: identificador, seguido por los identificadores de sus vecinas ordenados de menor a mayor y separados por comas. Una lista vacía conserva igualmente la fila de su partícula.

### metrics.csv

Cada medición incluirá como mínimo:

    seed,boundary,method,N,L,M,rc,repetition,time_ns,neighbor_pairs,distance_evaluations

La especificación detallada se mantiene en docs/protocolo-experimental.md.

## Estado actual

- Fase 0 completada: estructura, contratos, build mínimo y pruebas de humo.
- Fase 1 completada: modelo de partículas y dominio, geometría con paredes y periodicidad, distancia borde-borde y pruebas unitarias.
- Fase 2 completada: generación reproducible sin superposición, lectura y escritura de los formatos oficiales y comando generate.
- Fase 3 completada: búsqueda por fuerza bruta, salida simétrica de vecinos, tiempo de búsqueda y comando neighbors.
- Fase 4 completada: núcleo del Cell Index Method, validación del tamaño de celda, paredes, periodicidad y pruebas diferenciales contra fuerza bruta.
- Fase 5 completada: integración del CIM con neighbors y barrido reproducible de M con mediciones CSV.
- Fase 6 completada: lectura y validación de métricas, promedio, desvío estándar poblacional y figura de tiempo frente a M.
- Fase 7 completada: N intermedio y alto reproducible, mediciones finales para ambos contornos, selección de M óptimo y figuras de partículas vecinas.
- Fase 8 completada: benchmark de N para once tamaños, con L constante y densidad numérica constante, en ambos contornos.
- Fase 9 completada: análisis de escalamiento, gráficos lineales y logarítmicos, demostración parametrizable e informe final.

El alcance solicitado por la consigna está implementado. El [informe final](informe-final.md) presenta el problema desde cero, justifica cada parámetro y discute todos los resultados. El detalle técnico de la fase 7 se conserva en [docs/fase-7-experimento-m.md](docs/fase-7-experimento-m.md).

## Simulación interactiva

Todos los comandos siguientes se ejecutan desde `entregas/tp1-cim`.

### Preparación inicial

Este bloque se ejecuta una vez para crear el entorno Python, instalar Matplotlib y compilar el motor C++ optimizado:

    python3.12 -m venv python/.venv
    python/.venv/bin/pip install -r python/requirements.txt
    make release

### Comando completo

El siguiente comando genera un sistema, calcula todas las listas de vecinos y abre la ventana nativa de Matplotlib. Dentro de la ventana se seleccionan partículas únicamente haciendo clic sobre sus discos.

    python/.venv/bin/python scripts/demo.py \
      --N 500 \
      --L 20 \
      --M 13 \
      --rc 1 \
      --r-min 0.23 \
      --r-max 0.26 \
      --attempts 100000 \
      --repetitions 100 \
      --boundary periodic \
      --output experiments/raw/demo \
      --interactive

En macOS aparecerá el ícono de Matplotlib en el Dock. La terminal permanecerá ocupada hasta cerrar la ventana.

### Parámetros del comando

| Opción | Significado | Valor de ejemplo |
|---|---|---:|
| `--N` | Cantidad total de partículas. | `500` |
| `--L` | Longitud del lado del dominio cuadrado. | `20` |
| `--M` | Cantidad de celdas por lado; la grilla tiene `M*M` celdas. | `13` |
| `--rc` | Distancia máxima borde a borde para considerar dos partículas vecinas. | `1` |
| `--r-min` | Menor radio posible al generar partículas. | `0.23` |
| `--r-max` | Mayor radio posible al generar partículas. | `0.26` |
| `--attempts` | Intentos máximos de colocación por partícula. No es una repetición temporal. | `100000` |
| `--repetitions` | Cantidad de sistemas aleatorios independientes que se generan y miden. | `100` |
| `--boundary` | `walls` para paredes o `periodic` para contorno periódico. | `periodic` |
| `--output` | Carpeta para `static.txt`, `dynamic.txt`, `neighbors.txt` y el PNG. | `experiments/raw/demo` |
| `--interactive` | Abre la ventana de Matplotlib y habilita selección con clic. | Sin valor |

`M` debe respetar `L/M > rc + 2*r_max`. Un valor inválido produce un error antes de mostrar resultados.

### Paredes o periodicidad

Para usar paredes:

    --boundary walls

Para conectar los bordes opuestos mediante periodicidad:

    --boundary periodic

La condición elegida se usa tanto al generar partículas como al calcular y visualizar vecinas.

Ningún disco atraviesa el marco, tampoco en modo periódico: todos los centros se generan entre `ri` y `L-ri`. La periodicidad se aplica únicamente al calcular distancias entre bordes opuestos. Cuando una partícula seleccionada tiene alcance a través de un borde, el círculo punteado de interacción se proyecta en el extremo contrario para explicar por qué partículas aparentemente lejanas son vecinas.

### Uso de la ventana

1. Esperar a que se abra la ventana con todas las partículas en gris.
2. Hacer clic sobre cualquier disco.
3. La partícula elegida pasa a azul y sus vecinas a naranja.
4. El título muestra el ID seleccionado y la cantidad de vecinas.
5. Hacer clic sobre otro disco para cambiar inmediatamente la selección.
6. Cerrar la ventana para finalizar el comando.

Python no recalcula vecinos al hacer clic. Consume la lista completa producida previamente por C++ y solo cambia la representación visual.

### Qué tiempo informa

El tiempo mostrado corresponde al promedio de `--repetitions` búsquedas de las listas de vecinos de las `N` partículas del sistema completo. En cada repetición se genera automáticamente una semilla aleatoria diferente y un sistema nuevo. Con el valor predeterminado se miden 100 configuraciones independientes y se informa `media +/- desvío estándar`. La partícula seleccionada con clic se usa exclusivamente para la visualización y no modifica la medición.

El comando no recibe `--seed`: las semillas deben cambiar en todas las repeticiones. Cada fila de `metrics.csv` registra la semilla exacta utilizada, por lo que cualquier configuración puede reconstruirse posteriormente. El sistema mostrado en la ventana reutiliza la semilla de la primera medición y la imprime en la terminal.

El cronómetro incluye construcción de la grilla, asignación a celdas, recorrido de candidatas, cálculo de distancias y construcción de listas. Excluye generación aleatoria, archivos, validación contra fuerza bruta, calentamiento y Python.

### Salidas generadas

El comando deja en la carpeta indicada por `--output`:

| Archivo | Contenido |
|---|---|
| `static.txt` | `N`, `L`, radios y propiedades. |
| `dynamic.txt` | Tiempo `t0`, posiciones y velocidades. |
| `neighbors.txt` | Lista completa y simétrica de vecinos para cada ID. |
| `metrics.csv` | Una fila por repetición, con tiempo, parámetros y semilla aleatoria usada. |
| `neighbors.png` | Imagen estática de una selección representativa. |

Para generar y abrir solamente el PNG en Preview se reemplaza `--interactive` por `--open`. Ambas opciones son excluyentes.

### Ayuda del comando

    python/.venv/bin/python scripts/demo.py --help

## Experimentos reproducibles

La calibración del `N` alto, el estudio de variación de `N` y sus configuraciones están documentados en [scripts/README.md](scripts/README.md).

Para regenerar las 44 configuraciones de densidad libre y fija:

    python/.venv/bin/python scripts/run_n_experiments.py \
      --binary cpp/build/release/tp1 \
      --config experiments/configs/phase8-n.json \
      --output-root experiments/raw/phase8-random \
      --results-root experiments/results

Los comandos C++ individuales están disponibles mediante:

    ./cpp/build/release/tp1 --help
    ./cpp/build/release/tp1 generate --help
    ./cpp/build/release/tp1 neighbors --help
    ./cpp/build/release/tp1 benchmark-m --help
    ./cpp/build/release/tp1 benchmark-n --help
    ./cpp/build/release/tp1 benchmark-random-m --help
    ./cpp/build/release/tp1 benchmark-random-n --help

## Pruebas

La batería normal incluye pruebas unitarias e integración C++ y Python:

    make test

La batería instrumentada detecta accesos inválidos a memoria y comportamiento indefinido en C++:

    make sanitize

Para borrar ejecutables y cachés regenerables:

    make clean

## Ver resultados

En macOS, desde esta carpeta:

    open experiments/figures/time-vs-m-walls.png
    open experiments/figures/time-vs-m-periodic.png
    open experiments/figures/neighbors-walls.png
    open experiments/figures/neighbors-periodic.png
    open experiments/figures/time-vs-n-walls.png
    open experiments/figures/time-vs-n-periodic.png
    open experiments/figures/time-vs-n-walls-log.png
    open experiments/figures/time-vs-n-periodic-log.png
    open informe-final.md

Los valores numéricos seleccionados están en `experiments/results/`. Las mediciones individuales y los sistemas generados quedan en `experiments/raw/phase7/` y `experiments/raw/phase8/`; son regenerables y no se versionan.
