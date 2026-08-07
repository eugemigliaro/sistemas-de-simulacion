# Fase 1 — Modelo y geometría

## Modelo implementado

- Vec2: par de coordenadas o componentes de velocidad.
- Particle: identidad, posición, velocidad, radio y propiedad.
- Domain: lado del cuadrado y condición de contorno.
- BoundaryCondition: Walls o Periodic.

La identidad comienza en 1 porque el formato oficial usa el número de fila como identidad de la partícula [T01, p. 36] [T01, p. 37].

## Distancias

Con paredes, el desplazamiento entre centros es:

    delta = posición_j - posición_i

La distancia centro-centro es la norma euclídea de ese desplazamiento.

La distancia borde-borde implementada es:

    d_borde = d_centros - radio_i - radio_j

Esta es la definición provista por los archivos oficiales de ejemplo [EJ01].

Dos partículas de identidades distintas son vecinas si:

    d_borde < rc

La desigualdad es estricta porque la consigna pide distancia menor que rc [TP01, p. 1].

## Contorno periódico

Decisión de implementación: cada componente del desplazamiento se reduce mediante la convención de imagen mínima:

    delta_min = delta - L * round(delta / L)

Esto permite que partículas próximas a bordes opuestos se comparen con la separación corta indicada por la teórica [T01, p. 26].

## Pertenencia al dominio

- Walls: el disco completo debe quedar dentro del cuadrado; el centro debe estar entre su radio y L menos su radio.
- Periodic: el centro se representa en el intervalo base [0,L) para ambas coordenadas.

## Validaciones

Se rechazan mediante validación:

- identidad cero;
- coordenadas, velocidades o propiedad no finitas;
- radio no positivo;
- lado del dominio no positivo;
- contorno desconocido;
- radio de interacción negativo o no finito.

## Pruebas incorporadas

- triángulo 3-4-5 con paredes;
- umbral estricto por debajo, igual y por encima de rc;
- exclusión de la propia partícula;
- simetría de distancias y vecindad;
- periodicidad a través de un borde;
- periodicidad a través de una esquina;
- discos justo sobre el límite permitido por paredes;
- intervalo base periódico;
- entradas inválidas y excepciones esperadas.
