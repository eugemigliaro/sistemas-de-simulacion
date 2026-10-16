# T04 — apoyo manual de fórmulas

Derivado de inspección visual de las páginas 13, 17, 19, 20, 23, 28, 29, 37 y 42. Renders en `material/figuras/tp4/`. La extracción automática pierde símbolos y coeficientes; el original sigue siendo la autoridad.

Las ecuaciones verificadas de Verlet, Velocity Verlet, Beeman y Euler predictor-corrector están transcritas en `wiki/temas/paso-temporal-e-integradores.md`; las del oscilador en `wiki/temas/billar-circular-y-tp4.md`.

## Gear: tablas no recuperadas por el texto automático

Coeficientes alpha_0,...,alpha_5; un guion indica que la columna no se utiliza para ese orden.

Página 28, fuerza solo posicional:

| Orden | alpha_0 | alpha_1 | alpha_2 | alpha_3 | alpha_4 | alpha_5 |
|---|---|---|---|---|---|---|
| 2 | 0 | 1 | 1 | — | — | — |
| 3 | 1/6 | 5/6 | 1 | 1/3 | — | — |
| 4 | 19/120 | 3/4 | 1 | 1/2 | 1/12 | — |
| 5 | 3/20 | 251/360 | 1 | 11/18 | 1/6 | 1/60 |

Página 29, fuerza dependiente de posición y velocidad: mismas columnas, pero alpha_0 vale 19/90 para orden 4 y 3/16 para orden 5. Los otros coeficientes permanecen como en la tabla anterior.

Página 37: m=70 kg, k=10^4 N/m, gamma=100 kg/s, tf=5 s, r(0)=1 m, v(0)=−A gamma/(2m). La solución es A exp(−gamma t/(2m)) cos(sqrt(k/m−gamma²/(4m²)) t). La diapositiva 36 es portada, no contiene estos parámetros.

Página 42: fuerza normal F_N = −k_n xi e_n y energía potencial E_pot = k_n xi²/2.
