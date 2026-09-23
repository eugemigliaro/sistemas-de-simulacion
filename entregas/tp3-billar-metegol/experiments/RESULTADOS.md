# Resultados experimentales del TP3

Todos los resultados se generaron con el motor C++ en modo `release`. Las
semillas, mediciones individuales y resúmenes se preservan en
`experiments/results/`; las trayectorias voluminosas quedan en
`experiments/raw/` y se regeneran con `scripts/run_experiments.py`.

## 1.1 Tiempo de ejecución

Se simuló la mesa vacía hasta `tf = 30 s` con el motor de cola de prioridad,
para `N` en `{10, 25, 50, 75, 100, 150, 200, 300, 400}` y diez semillas por
punto. Cada punto del gráfico informa media y desvío estándar, como exige la
consigna [TP03, p. 3].

En el rango `N >= 50`, un ajuste log-log da `t ∝ N^3,30`. Para `N = 400`, el
tiempo fue `11,27 ± 0,04 s`. Este exponente describe solamente el rango medido:
no se interpreta como una complejidad asintótica universal.

## 1.2 Exploración de configuraciones

Se exploró sistemáticamente un único obstáculo circular sobre el eje
longitudinal de la mesa. Se variaron su posición `xk` y su radio `Rk`, se fijó
`yk = W/2 = 0,34 m`, y se compararon todos los puntos contra la mesa vacía. Se
usaron `N = 100`, `tmax = 100 s` y quince semillas independientes por punto,
por encima del mínimo de cinco realizaciones [TP03, p. 3].

La mejor configuración medida fue:

```text
0.60 0.34 0.34
```

| Configuración | `<t90>` [s] | Desvío [s] | Error estándar [s] |
|---|---:|---:|---:|
| Mesa vacía | 22,68 | 2,98 | 0,77 |
| Elegida | 15,54 | 1,55 | 0,40 |

La reducción de la media fue del `31,5 %`; también disminuyó la dispersión. El
obstáculo está contenido en el dominio, es tangente a las paredes largas y
permite generar las cien partículas. La configuración entregable está en
`experiments/configs/SdS_TP3_2026Q2G07CS_Config.txt` [TP03, p. 3].

## 1.3 Difusión

Para todas las configuraciones del barrido se realizaron cinco corridas de
`8 s`, guardando un cuadro cada veinte eventos. El DCM usa múltiples orígenes
temporales y se agrupa en intervalos de `0,05 s`. Se fijó una ventana común de
ajuste `[0,3; 1,5] s`, antes de comparar configuraciones, y se ajustó una recta
por el origen mediante el barrido de `E(c)` pedido por la Teórica 0 [TP03, p. 3]
[T00, pp. 79-81].

Para la configuración elegida se obtuvo
`<D> = (0,00752 ± 0,00036) m²/s`, donde la incertidumbre es el desvío entre
semillas. En el barrido completo, la correlación de Pearson entre `<D>` y
`<t90>` fue `r = 0,13`: no se observa una relación global relevante. Esta es
una conclusión experimental sobre esta familia de configuraciones; no implica
que `D` y `t90` sean independientes para cualquier geometría.

## Reproducción

```bash
make python-env
make test
make experiments
make assets
```

Los dos videos locales quedan en `videos/`. La consigna exige publicar las
animaciones en YouTube o Vimeo y colocar las URL explícitas en el PDF, sin
entregar los MP4 [TP03, p. 1].
