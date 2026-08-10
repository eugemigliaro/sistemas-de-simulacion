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

Cada tiempo corresponde a encontrar las listas de vecinos del sistema completo de `N` partículas. La partícula elegida en la visualización no restringe ni modifica el alcance del cronómetro [TP01, p. 1].

## Reglas para comparar métodos

- Compilar con optimizaciones de release.
- Usar el mismo conjunto de partículas para todos los valores de M comparados.
- Ejecutar al menos una repetición de calentamiento no medida.
- Consumir el resultado para impedir que el compilador elimine el cálculo.
- Comprobar la lista contra fuerza bruta fuera de la región temporizada.
- Guardar cada repetición individual; no escribir solo el promedio.
- Registrar semilla, parámetros, método y tipo de contorno.
- Generar una semilla aleatoria distinta para cada repetición y conservarla en la misma fila que su tiempo.

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

El comando `benchmark-random-m` genera un sistema nuevo por repetición con una semilla aleatoria única, calcula automáticamente el máximo `M`, usa fuerza bruta para `M=1` y CIM para los valores restantes. Dentro de una repetición, todos los `M` usan el mismo sistema para que la comparación sea justa. Antes de medir valida la lista completa contra fuerza bruta y ejecuta un calentamiento no medido.

Las mediciones finales deben ejecutarse con la compilación release. La semilla y la cantidad de repeticiones se pasan explícitamente al comando.

El comando Python `plot-m` acepta uno o más CSV, valida que las repeticiones sean compatibles, calcula la media y el desvío estándar poblacional para cada `M`, escribe un resumen CSV y genera la figura con barras de error. Las escalas logarítmicas son opciones explícitas para aplicarlas cuando los valores cubran distintos órdenes de magnitud [TP01, p. 1].

El punto 3 se ejecutó con `N=500` y `N=1050` y 100 semillas aleatorias únicas para paredes y periodicidad. El protocolo completo, los resultados y la selección de `M=13` como óptimo común están en `fase-7-experimento-m.md`.

El punto 4 se ejecutó para once valores de `N` entre 10 y 1050 y 100 semillas aleatorias únicas por punto. La densidad libre mantiene `L=20` y `M=13`. La densidad fija mantiene `N/L²=1.25` y escala `M` para conservar aproximadamente el lado de celda `20/13`. Los resultados completos se presentan en `../informe-final.md`.

## Decisiones pendientes

No quedan decisiones experimentales pendientes para el alcance actual.
