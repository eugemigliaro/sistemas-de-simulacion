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

## Decisiones pendientes

- Valores intermedio y alto de N para variar M.
- Cantidad de repeticiones: 10, 100 o 1000.
- Conjunto de al menos diez valores de N.
- Densidad elegida para la comparación fija.
- Regla de M en el experimento a densidad fija.
- Inclusión de ambas condiciones de contorno en todos los gráficos o en gráficos separados.
