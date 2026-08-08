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
                           figuras y animaciones

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

## Componentes C++ planificados

- Comando benchmark-n y configuración de los estudios finales.

## Componentes Python planificados

- Animación de una secuencia producida por C++.
- Gráfico de tiempo frente a N.

## Componentes Python implementados

- Lector y validación de las métricas del barrido de M.
- Agregación de promedio y desvío estándar poblacional.
- CSV resumido y gráfico con barras de error del tiempo frente a M.
- Lectores validados de estático, dinámico y vecinos.
- Figura parametrizable de una partícula y sus vecinas.

## Principio de validación

La fuerza bruta y el CIM compartirán las mismas operaciones geométricas. Para cada sistema de prueba se normalizarán sus listas y se exigirá igualdad exacta antes de considerar una medición de rendimiento válida.

La generación y las búsquedas comparten la geometría implementada en cpp/include/tp1/geometry.hpp y cpp/src/geometry.cpp. Así, la condición de no solapamiento y la vecindad usan una única definición de distancia borde-borde.

La fuerza bruta compara cada par no dirigido exactamente una vez. Su salida será el oráculo de corrección: para cada sistema de prueba, el futuro CIM deberá producir una lista idéntica antes de que sus tiempos se consideren válidos.
