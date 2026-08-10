# Modelo y componentes

## Flujo de datos

    configuración
         |
         v
    generador C++ ----> static.txt + dynamic.txt
         |                         |
         v                         v
    buscador C++ -----> neighbors.txt + metrics.csv
                                   |
                                   v
                         visualizador Python
                                   |
                                   v
                           figuras y análisis

## Componentes C++ implementados

- Partícula, vector bidimensional y dominio.
- Validación básica de partículas y dominios.
- Geometría con paredes.
- Geometría periódica mediante imagen mínima.
- Distancia centro-centro y borde-borde.
- Predicado estricto de vecindad.
- Configuración validada de generación.
- Generador reproducible sin superposición.
- Lectores y escritores de static.txt y dynamic.txt.
- Comando generate con paredes y periodicidad.
- Búsqueda de vecinos por fuerza bruta.
- Búsqueda de vecinos mediante Cell Index Method.
- Validación y escritura de listas simétricas, ordenadas y sin duplicados.
- Comando neighbors con selección entre fuerza bruta y CIM, tiempo de búsqueda y cantidad de evaluaciones.
- Cálculo del máximo valor válido de M.
- Comando benchmark-m con calentamiento, validación y mediciones individuales en CSV.
- Comando benchmark-n con M explícito, calentamiento, validación y mediciones individuales en CSV.
- Comandos benchmark-random-m y benchmark-random-n con una semilla aleatoria única registrada por repetición.

## Componentes Python implementados

- Lector y validación de las métricas del barrido de M.
- Agregación de promedio y desvío estándar poblacional.
- CSV resumido y gráfico con barras de error del tiempo frente a M.
- Lectores validados de estático, dinámico y vecinos.
- Figura parametrizable de una partícula y sus vecinas.
- Explorador Matplotlib con selección de partículas mediante clic.
- Análisis conjunto de densidad libre y fija frente a N.
- Gráficos lineales y logarítmicos con ajuste empírico de exponente.
- Demostración reproducible que orquesta generación, búsqueda y figura.

## Principio de validación

La fuerza bruta y el CIM comparten las mismas operaciones geométricas. Para cada sistema medido se normalizan sus listas y se exige igualdad exacta antes de considerar una medición de rendimiento válida.

La generación y las búsquedas comparten la geometría implementada en cpp/include/tp1/geometry.hpp y cpp/src/geometry.cpp. Así, la condición de no solapamiento y la vecindad usan una única definición de distancia borde-borde.

La fuerza bruta compara cada par no dirigido exactamente una vez. Su salida es el oráculo de corrección: para cada sistema de prueba, el CIM debe producir una lista idéntica antes de que sus tiempos se consideren válidos.
