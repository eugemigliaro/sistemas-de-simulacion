# Hallazgos del piloto

Estado: **calibración provisional; no usar como resultado final**.

Configuración: dos semillas, 1000 pasos, `eta = 0, 0.25, 0.5, 0.75, 1`, `rho = 2, 4, 8`, ambos modelos y `M = 9`. Se compararon promedios posteriores a `t = 500` y `t = 800`.

## Qué permitió decidir

- Vicsek mantiene polarización alta en `eta = 0.25`, presenta valores intermedios alrededor de `eta = 0.5` y queda desordenado en `eta = 0.75`. La calibración debe refinar aproximadamente `[0.5,0.75]`.
- El votante queda mayormente desordenado ya en `eta = 0.25`; necesita valores mucho más cercanos a cero, coherentemente con que la transición de la referencia depende de la rapidez [B09, p. 1].
- El votante con `eta = 0` seguía aumentando su polarización al comparar los intervalos que empiezan en 500 y 800, sobre todo para `rho = 8`. Mil pasos no alcanzan para fijar su estacionario.
- Para ruido positivo, la mayoría de las diferencias entre los cortes 500 y 800 fueron pequeñas, pero dos semillas son insuficientes para estimar barras finales.
- En las densidades pedidas, `S` resultó cercano a uno en gran parte del piloto. Esto no autoriza a omitir el observable: la consigna exige su evolución, media, desvío y relación con `va` [TP02, p. 2].
- Una indicación oral posterior agrega densidades bajas nominales `1/pi`, `1/(2*pi)` y `1/(3*pi)` específicamente para que el estudio de `S` sea informativo [N-2026-08-22-densidades-s-tp2].

## Siguiente calibración

- Vicsek: refinar `eta` entre `0.5` y `0.75`.
- Votante: explorar `eta` entre `0` y `0.25`, con especial resolución por debajo de `0.1`.
- Extender las corridas y comparar medias por bloques antes de elegir `t_inicio`.
- Aumentar realizaciones solamente después de fijar duración y malla.

Los CSV crudos regenerados con metadatos completos están en `experiments/raw/pilot-metadata-v2/` y permanecen fuera de Git. Los pilotos del esquema anterior no se usan en el análisis actual.
