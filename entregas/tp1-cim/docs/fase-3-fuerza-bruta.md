# Fase 3 — Vecinos por fuerza bruta

## Objetivo

La fuerza bruta establece una referencia sencilla de corrección antes de introducir la grilla del Cell Index Method. Compara todos los pares de partículas y decide la vecindad mediante la distancia borde-borde estrictamente menor que rc requerida por la consigna [TP01, p. 1].

Para N partículas se evalúan exactamente:

    N * (N - 1) / 2

distancias. Cada par se procesa una vez, con índices i<j. Cuando el par es vecino, se agrega j a la lista de i e i a la lista de j.

## Contrato de la lista

La estructura y el archivo de salida cumplen estas invariantes:

- una lista por cada partícula;
- IDs desde 1 hasta N;
- relación simétrica;
- sin ID propio;
- sin duplicados;
- vecinas ordenadas de menor a mayor.

El formato textual usa comas como el ejemplo oficial [EJ01]:

    1,2,5
    2,1
    3

La tercera partícula no tiene vecinas, pero conserva su fila.

## Medición interactiva

El comando neighbors informa pares encontrados, evaluaciones de distancia y tiempo en nanosegundos. El cronómetro rodea únicamente la búsqueda; excluye lectura y escritura, en línea con el protocolo experimental del proyecto.

Desde entregas/tp1-cim, primero se genera el sistema:

    make cpp-run ARGS="generate --N 100 --L 20 --seed 42 --boundary walls --static data/generated/static.txt --dynamic data/generated/dynamic.txt"

Luego se buscan sus vecinos:

    make cpp-run ARGS="neighbors --method brute-force --static data/generated/static.txt --dynamic data/generated/dynamic.txt --rc 1 --boundary walls --output data/generated/neighbors.txt"

Para periodicidad se debe usar el mismo valor periodic tanto al generar como al buscar.

## Verificación

Las pruebas cubren:

- umbral inmediatamente menor, igual y mayor que rc;
- listas vacías;
- orden, simetría y duplicados;
- exclusión de la propia partícula;
- paredes y pares a través del contorno periódico;
- rc inválido y sistemas mal formados;
- cantidad N(N-1)/2 de evaluaciones;
- serialización exacta de neighbors.txt.

Como integración con los datos de cátedra, se procesaron Static100.txt y Dynamic100.txt con rc=6 y paredes. Todas las filas informadas en AlgunosVecinos_100_rc6.txt coincidieron exactamente con la salida calculada [EJ01].
