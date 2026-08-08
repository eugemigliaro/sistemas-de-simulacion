# Protocolo experimental

Este documento fija desde el comienzo qué se medirá. Los valores concretos se completarán después de validar el algoritmo.

## Alcance del temporizador

Se incluirá:

- construcción o limpieza de la estructura de celdas;
- asignación de partículas a celdas;
- búsqueda de pares candidatos;
- evaluación geométrica;
- construcción de la lista de vecinos.

Se excluirá:

- generación de partículas;
- lectura y escritura de archivos;
- validación mediante fuerza bruta;
- análisis y visualización Python.

## Reglas para comparar métodos

- Compilar con optimizaciones de release.
- Usar el mismo conjunto de partículas para todos los valores de M comparados.
- Ejecutar al menos una repetición de calentamiento no medida.
- Consumir el resultado para impedir que el compilador elimine el cálculo.
- Comprobar la lista contra fuerza bruta fuera de la región temporizada.
- Guardar cada repetición individual; no escribir solo el promedio.
- Registrar semilla, parámetros, método y tipo de contorno.

## Columnas de metrics.csv

- seed: semilla de generación.
- boundary: walls o periodic.
- method: brute_force o cim.
- N, L, M, rc: parámetros del sistema.
- repetition: índice de repetición.
- time_ns: tiempo medido en nanosegundos.
- neighbor_pairs: cantidad de pares no dirigidos encontrados.
- distance_evaluations: cantidad de pares candidatos cuya distancia fue evaluada.

## Implementación disponible

El comando `benchmark-m` carga un único sistema, calcula automáticamente el máximo `M`, usa fuerza bruta para `M=1` y CIM para los valores restantes. Antes de cada grupo de repeticiones valida la lista completa contra fuerza bruta y ejecuta un calentamiento no medido. El archivo CSV se recrea y conserva cada repetición individual.

Las mediciones finales deben ejecutarse con la compilación release. La semilla y la cantidad de repeticiones se pasan explícitamente al comando.

El comando Python `plot-m` acepta uno o más CSV, valida que las repeticiones sean compatibles, calcula la media y el desvío estándar poblacional para cada `M`, escribe un resumen CSV y genera la figura con barras de error. Las escalas logarítmicas son opciones explícitas para aplicarlas cuando los valores cubran distintos órdenes de magnitud [TP01, p. 1].

El punto 3 se ejecutó con `N=500` y `N=1050`, semilla 42 y 100 repeticiones para paredes y periodicidad. El protocolo completo, los resultados y la selección de `M=13` como óptimo común están en `fase-7-experimento-m.md`.

## Decisiones pendientes

- Conjunto de al menos diez valores de N.
- Cantidad de repeticiones y semillas para variar N.
- Densidad elegida para la comparación fija.
- Regla de M en el experimento a densidad fija.
- Inclusión de ambas condiciones de contorno en todos los gráficos o en gráficos separados.
