# Fase 4 — Núcleo del Cell Index Method

## Objetivo

Esta fase implementa el buscador mediante Cell Index Method (CIM) y lo valida contra la fuerza bruta. La integración con la interfaz de línea de comandos y los experimentos de rendimiento quedan fuera de este alcance.

La fuerza bruta continúa siendo el oráculo de corrección: para el mismo sistema, radio de interacción y condición de contorno, ambos métodos deben producir exactamente la misma lista de vecinos [T01, p. 28].

## Tamaño seguro de celda

La condición de vecindad entre dos partículas es:

    d_borde = d_centros - r_i - r_j < rc

Por lo tanto:

    d_centros < rc + r_i + r_j

Si `r_max` es el mayor radio presente en el sistema, un alcance conservador entre centros es:

    R = rc + 2*r_max

Cuando el lado de celda `l=L/M` satisface:

    L/M > rc + 2*r_max

dos partículas vecinas no pueden tener sus centros separados por una celda completa. En consecuencia, alcanza con revisar la celda propia y las ocho adyacentes. Se conserva la desigualdad estricta usada por la teórica para partículas puntuales y se incorpora el diámetro máximo para cubrir partículas de radio no nulo [T01, p. 23] [TP01, p. 1].

`M=1` es un caso especial: existe una sola celda y se comparan todos los pares, por lo que equivale a fuerza bruta y no necesita satisfacer el límite anterior [TP01, p. 1]. Para todo `M>1`, un valor que no cumpla el criterio produce un error explícito.

## Estructura y asignación

La grilla se representa mediante un vector de `M*M` celdas. Cada celda guarda índices de partículas, no copias. Esta representación hace explícito el flujo posición-celda-candidatos y no introduce una estructura pública adicional.

Para una posición `(x,y)` se calcula:

    columna = floor(x / (L/M))
    fila    = floor(y / (L/M))
    celda   = fila*M + columna

Las posiciones ya fueron validadas por la geometría común. El índice calculado se limita a `M-1` como protección ante redondeos de punto flotante junto al extremo superior del dominio.

## Búsqueda de candidatos

Para cada celda se procesan:

1. todos sus pares internos con índices `i<j`;
2. cada celda adyacente cuyo identificador sea mayor;
3. todos los pares cruzados entre ambas celdas.

Con paredes se descartan desplazamientos que salen de la grilla. Con periodicidad, los índices se envuelven hacia el lado opuesto [T01, p. 26]. Los identificadores adyacentes se deduplican antes de comparar partículas: esto evita repetir pares cuando `M=1` o `M=2` hacen que distintos desplazamientos conduzcan a la misma celda.

Cada par candidato incrementa `distance_evaluations` una sola vez y se evalúa mediante `are_neighbors`. Así, CIM y fuerza bruta comparten imagen mínima, distancia borde-borde y umbral estricto. Al terminar se ordena cada lista de vecinos.

## Verificación

Las pruebas incorporadas cubren:

- pares dentro de una celda y entre celdas horizontales, verticales y diagonales;
- desigualdad estricta en el radio de interacción;
- paredes y periodicidad a través de bordes y esquinas;
- `M=1` y `M=2` sin evaluaciones duplicadas;
- rechazo de `M=0`, de la igualdad en el límite y de valores mayores;
- comparación diferencial con fuerza bruta para ambas condiciones de contorno, cuatro semillas y cinco valores válidos de `M`.

Una ejecución se considera correcta únicamente si las listas completas y la cantidad de pares coinciden exactamente con fuerza bruta y la salida conserva simetría, orden y ausencia de duplicados.
