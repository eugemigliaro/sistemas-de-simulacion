# Fase 6 — Análisis estadístico de M

## Objetivo

Esta fase implementa el postproceso de las mediciones producidas por `benchmark-m`. La consigna pide repetir la búsqueda, registrar los tiempos y graficar su promedio con el desvío estándar como barra de error [TP01, p. 1].

La herramienta prepara ese análisis, pero no completa todavía el punto 3: el archivo actual es una corrida piloto y aún deben elegirse un valor intermedio y el valor más alto posible de `N`.

## Comando

Desde `entregas/tp1-cim`:

    make python-run ARGS="plot-m experiments/raw/metrics-m.csv \
      --summary experiments/raw/summary-m.csv \
      --figure experiments/figures/time-vs-m.png"

Se pueden pasar varios CSV antes de las opciones. Cada curva queda identificada por `N`, semilla, contorno, `L` y `rc`, de modo que sistemas diferentes no se mezclan silenciosamente.

Las opciones `--log-x` y `--log-y` activan escalas logarítmicas cuando los datos cubren distintos órdenes de magnitud, como indica la consigna [TP01, p. 1].

## Estadística

Para cada combinación de parámetros y cada `M` se calculan:

- cantidad de repeticiones;
- media aritmética del tiempo;
- desvío estándar poblacional del tiempo;
- cantidad de pares vecinos;
- promedio de evaluaciones de distancia.

Se usa el desvío poblacional, dividiendo por la cantidad `R` de repeticiones. Esta convención interpreta las mediciones registradas como el conjunto cuya dispersión se muestra mediante `media ± desvío`. La consigna no distingue entre desvío poblacional y muestral, por lo que la elección queda declarada explícitamente [TP01, p. 1].

El gráfico convierte nanosegundos a microsegundos para facilitar la lectura. La línea une los puntos únicamente como guía visual; los valores medidos se identifican con marcadores y barras de error.

## Validaciones

El lector exige las columnas de `metrics-m.csv` y rechaza:

- valores numéricos o categorías inválidos;
- repeticiones duplicadas para el mismo experimento;
- menos de dos repeticiones por grupo;
- cambios en `neighbor_pairs` entre repeticiones;
- `M=1` con un método distinto de fuerza bruta;
- `M>1` con un método distinto de CIM.

Estas condiciones evitan obtener una figura aparentemente válida a partir de mediciones incompatibles.

## Salidas

`summary-m.csv` conserva una fila por valor de `M` con las columnas:

    seed,boundary,N,L,rc,M,method,samples,mean_time_ns,stddev_time_ns,neighbor_pairs,mean_distance_evaluations

Los CSV de mediciones y resúmenes permanecen en `experiments/raw/` y están ignorados por Git porque son regenerables. Las figuras seleccionadas se guardan en `experiments/figures/` y pueden versionarse.
