# TP1 — Búsqueda eficiente de partículas vecinas

Espacio de trabajo reproducible para resolver el TP1 mediante un motor de simulación en C++20 y herramientas de visualización y análisis en Python 3.

## Fuentes

- [Enunciado oficial TP01](../../material/catedra/practica/TP1_Enunciado.pdf).
- [Síntesis del Cell Index Method y alcance del TP1](../../wiki/temas/cell-index-method.md).
- [Archivos oficiales de ejemplo](../../material/extraido/EJ01/README.md).

Los originales permanecen en material/. Esta carpeta solo contiene decisiones, implementación, pruebas y resultados propios.

## Separación de responsabilidades

- C++: generación de partículas, validación geométrica, fuerza bruta, Cell Index Method y medición de tiempos.
- Python: lectura de resultados, figuras, animaciones y análisis estadístico.
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

    seed,boundary,method,N,L,M,rc,repetition,time_ns,neighbor_pairs

La especificación detallada se mantiene en docs/protocolo-experimental.md.

## Estado actual

- Fase 0 completada: estructura, contratos, build mínimo y pruebas de humo.
- Fase 1 completada: modelo de partículas y dominio, geometría con paredes y periodicidad, distancia borde-borde y pruebas unitarias.
- Fase 2 completada: generación reproducible sin superposición, lectura y escritura de los formatos oficiales y comando generate.
- Fase 3 completada: búsqueda por fuerza bruta, salida simétrica de vecinos, tiempo de búsqueda y comando neighbors.
- Fase 4 completada: núcleo del Cell Index Method, validación del tamaño de celda, paredes, periodicidad y pruebas diferenciales contra fuerza bruta.

La próxima fase integrará el Cell Index Method con el comando neighbors mediante los parámetros --method cim y --M. Los comandos benchmark-m y benchmark-n corresponden a fases posteriores.

## Comandos

Desde esta carpeta:

    make debug
    make release
    make test
    make sanitize
    make cpp-run ARGS="--help"
    make cpp-run ARGS="generate --N 100 --L 20 --seed 42 --boundary walls --static data/generated/static.txt --dynamic data/generated/dynamic.txt"
    make cpp-run ARGS="neighbors --method brute-force --static data/generated/static.txt --dynamic data/generated/dynamic.txt --rc 1 --boundary walls --output data/generated/neighbors.txt"
    make python-run ARGS="--help"
    make clean

El mismo comando admite --boundary periodic. Si no se indican opciones, generate usa N=100, L=20, radios uniformes entre 0.23 y 0.26, semilla 0 y paredes. Los archivos de data/generated/ son resultados regenerables y no se versionan.

Las pruebas actuales no requieren dependencias externas. Antes de desarrollar las figuras se creará python/.venv y se instalará python/requirements.txt.
