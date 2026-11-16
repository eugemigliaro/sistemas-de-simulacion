# Decisiones del TP5 — Problema 2: evacuación con esquema híbrido

Problema 2 del TP5, con el SFM sin fuerza social [TP05, p. 3] [B26]. Las decisiones en las que el grupo modificó la recomendación del agente están en [recomendaciones-modificadas.md](recomendaciones-modificadas.md); acá figuran todas, con su fuente o su justificación. Lo marcado como **inferencia** no está en la consigna ni en los papers.

## Sistema

- N = 500 agentes en una sala de L = 50 m, con una puerta de d = 0,8 m centrada en la pared y = 0; v_d = 1,5 m/s; radios uniformes en [0,18; 0,25] m [TP05, p. 3].
- SFM sin fuerza social: m dv/dt = m (v_d e − v)/τ + Σ f_ij + Σ f_iW, con contacto f_ij = k ξ n_ij + κ ξ Δv^t_ji t_ij y paredes análogas [B26, pp. 1–2]. τ = 0,5 s, k = 1,2·10⁵ N/m y κ = 2,4·10⁵ kg/(m·s) [B26, p. 2].
- **Masa proporcional al área:** m_i = 80 kg·(r_i/0,215 m)², con 80 kg para el radio medio. Apartamiento del paper, que usa 80 kg para todos [B26, p. 2]; se consulta con la cátedra. Es una opción de configuración (ver [recomendaciones-modificadas.md](recomendaciones-modificadas.md)).
- Paredes: segmentos sin espesor; los marcos de la puerta y las esquinas actúan como puntos.

## Targets, estado inicial y retiro

- **Primer target:** el punto del 60 % central de la puerta más cercano al agente. Es determinista y hace que un agente libre vaya en línea recta. La idea del 60 % central viene del paper del CPM [B28, p. 4].
- **Segundo target**, al cruzar la línea de la puerta (y = 0): se compara un target común en (L/2, −D), con D ∈ {1,25; 1,5; 2; 3; 5; 10; 20} m, contra una dirección propia de cada agente que lo aleja de la puerta lo más rápido posible (−ŷ debajo de la puerta). El estudio se corre con TSDMD puro, y los demás estudios usan la opción con menor t_evac.
- **Retiro:** cuando la distancia del centro del agente al segmento de la puerta llega a 1 m, del lado de afuera [TP05, p. 3].
- **Estado inicial:** posiciones uniformes sin superposición con agentes ni paredes [TP05, p. 3]; los agentes arrancan caminando con v = v_d e, ya relajados (inferencia: la relajación dura ~τ, despreciable frente a la evacuación).

## TSDMD

- Beeman predictor-corrector para fuerzas que dependen de la velocidad [T04, p. 20], como en el TP4. Al final del paso se reevalúa la aceleración con la velocidad corregida, reusando los contactos del paso.
- Celdas de lado ≥ 2 r_max para buscar contactos, como el CIM del TP1.
- dt elegido con un test de convergencia de dos partes: un choque frontal aislado contra su solución analítica, con el agente más liviano (~56 kg), y la distribución de t_evac para varios dt. La referencia de la teórica es 0,1·√(m/k) [T05, p. 19].

## EDMD puro

- **Choque**, derivado del SFM (inferencia): la componente normal es elástica, porque el resorte del SFM no tiene amortiguamiento, y la tangencial se multiplica por e_t = exp(−2κ|v_n|/k). Sale de integrar la fricción κξ durante medio período del resorte en un choque aislado; la masa se cancela. Contra paredes y marcos, lo mismo con masa infinita. Se valida contra choques del SFM blando.
- **Recuperación de v_d:** se comparan las patadas de relajación cada δ con la relajación analítica entre eventos, que necesita reapuntar la dirección con alguna tolerancia. El híbrido, que delega la recuperación en el SFM, queda como tercera referencia.
- **Relajado:** |v − v_d e| ≤ 0,01 v_d; en ese caso v se redondea a v_d e.

## Híbrido

- **Criterio por tiempo al contacto:** un agente es EDMD si está relajado, no tiene contactos y no tiene contacto posible en T*. Contra agentes EDMD y paredes el tiempo es exacto; contra agentes TSDMD se usa una cota V_max = 2 v_d = 3 m/s, verificada en cada paso. Pasa a TSDMD en el paso de la grilla anterior al alerta (requiere T* ≥ dt) y vuelve a EDMD solo si no hay contacto posible en 2T* (histéresis).
- La grilla de dt es el reloj maestro: entre t_n y t_{n+1} se procesan en orden los eventos EDMD, después se avanza un dt a los agentes TSDMD y al final se revisan los cambios de esquema.
- **Relajación analítica en el híbrido:** antes de implementarla se mide qué fracción de los pasos TSDMD se gasta en agentes aislados pero sin relajar. Si es significativa (> 10 %) se implementa y se compara.

## Corridas y estudios

- Corte de seguridad en t_max = 4000 s simulados. **Atasco:** si no sale nadie durante 300 s simulados con agentes adentro, la corrida termina y queda marcada como trabada (`clogged 1` en el pie). Las trabadas se reportan aparte y no entran en los promedios de t_evac.
- (b) ≥ 10 realizaciones por esquema, con las mismas condiciones iniciales en los tres.
- (c) Tiempo de ejecución medido dentro del motor, solo el bucle de simulación y sin escribir cuadros, en corridas secuenciales. Barrido T* ∈ {0,002; 0,005; 0,01; 0,02; 0,05; 0,1; 0,2; 0,5; 1} s, con 10 realizaciones cada uno: más fino abajo, porque con T* ≳ 0,2 s casi todos quedan en TSDMD desde el principio.
- **Estudio de la recuperación de v_d** (patadas con varios δ contra relajación analítica con varias tolerancias de reapuntado): en un sistema chico, N = 60 en una sala de 15 m (densidad parecida a la del enunciado), con 10 realizaciones; con N = 500 la analítica no es viable.
- (d) N ∈ {100, 200, 400, 600, 800, 1000}, a densidad constante (L = 50 m·√(N/500)) y a L constante, con 5 realizaciones por N.
- El motor escribe solo estado: cuadros cada dt₂ (posiciones, velocidades y modo), los instantes de salida de cada agente y los cambios de modo [COR02] [T05, p. 21]. Los observables se calculan en el post-proceso.

## Abierto: atascos permanentes

Con el SFM sin fuerza social, la puerta de 0,8 m y sin fluctuaciones, se forman arcos estáticos que no se rompen nunca. Las velocidades quedan exactamente en cero y el arco se sostiene solo con fuerzas normales, porque la fricción del SFM es viscosa (nula en reposo).

- **N = 500, TSDMD puro (dt = 1 ms):** 3 de 4 semillas quedaron trabadas hasta 3000 s. Sus últimas salidas fueron entre 748 y 897 s y dejaron entre 28 y 146 agentes adentro. La que terminó evacuó en 1015 s.
- **N = 60 en una sala de 15 m:** se trabaron 3 de 10 semillas, y 1 de 5 con 80 kg para todos.

**Decisión del grupo (2026-11-04):** consultarlo con la cátedra el 06/11. Mientras tanto:
- se implementa una fluctuación como opción, apagada por defecto;
- se avanza con lo que no depende de esto.

La fluctuación (elegida por el grupo entre tres formas) es una fuerza aleatoria que actúa solo sobre agentes en contacto ("empujones" dentro de la multitud), constante durante intervalos de duración τ_ξ, para que no dependa de dt. Solo en contacto para que no altere el vuelo libre que resuelve el EDMD. No figura en la bibliografía del curso: el SFM original de Helbing y Molnár (1995) tiene un término de fluctuaciones, pero es conocimiento externo.

## Resultados de las primeras corridas (2026-11-04)

Corridas exploratorias, no son todavía los estudios a–d.

- **Fluctuación en contacto (N = 500, TSDMD, semillas 1, 3 y 4, que sin fluctuación se trababan; muestra chica, ver el estudio con más semillas más abajo):**
  - 5 %: se trabaron 2 de 3.
  - 10 %: terminaron las 3, con t_evac de 942 a 990 s.
  - 20 %: terminaron 2 (936 y 1065 s); la otra quedó trabada con 257 salidas.
  - La fluctuación no destraba siempre ni mejora en forma monótona con la amplitud.
- **Híbrido (N = 500, T* = 0,05 s, fluctuación 10 %, semilla 1):**
  - t_evac = 1074 s; 498 cambios de esquema (casi todos de EDMD a TSDMD); ninguna violación de V_max.
  - Pasos TSDMD de agentes aislados pero sin relajar: 100 480 de 274,5 millones (0,04 %). **Por el criterio acordado (> 10 %), la relajación analítica no se implementa en el híbrido.**
- **Cascada con T* grande:** con la cota V_max = 3 m/s, el radio de seguridad contra un TSDMD es (v_d + V_max)·2T* (4,5 m con T* = 0,5 s), mayor que la separación típica (~2 m). Con T* ≳ 0,2 s casi todos quedan en TSDMD desde t = 0: es el límite T* → ∞ del barrido.
- **EDMD puro con patadas (N = 500, semilla 1):** también se traba. Desde t ≈ 40 s quedaron 479 adentro hasta t = 100 s, con unos 310 mil eventos por segundo simulado (1,4 s de reloj por segundo simulado). Llegar a 3000 s costaría ~70 min por corrida.
- **EDMD con relajación analítica (N = 60, sala de 15 m):** en el tapón cuesta ~70 µs por evento, frente a ~5 µs con patadas, y genera más choques. Con N = 500 no es viable.
- **dt (choque frontal aislado, agentes de 56 kg):** error en la restitución normal de 1,8 % con 5 ms, 0,09 % con 2 ms, 0,05 % con 1 ms y 0,007 % con 0,5 ms.

- **Fluctuación en EDMD puro** (si se activa en TSDMD): cada patada suma a los agentes que chocaron desde la patada anterior el impulso de la misma fuerza aleatoria, integrada durante δ. Así los tres esquemas tienen la misma física. No está implementada para la relajación analítica.

## Estudio de atascos con más semillas (2026-11-04)

`scripts/run_atascos.py` y `scripts/resumen_atascos.py`; resultados en `experiments/results/atascos.csv`. TSDMD puro, N = 500, corte por atasco de 300 s. Las semillas son nuevas (101 a 120). Las de las tres amplitudes son las mismas 101 a 110, así que la comparación es pareada. Intervalos de Clopper-Pearson del 95 %.

| Fluctuación | Trabadas | IC 95 % | t_evac de las que terminan |
|---|---|---|---|
| 0 % | 9/20 | 23 %–68 % | 1007 ± 43 s (11 corridas) |
| 5 % | 3/10 | 7 %–65 % | 1037 ± 151 s (7) |
| 10 % | 5/10 | 19 %–81 % | 969 ± 51 s (5) |
| 20 % | 3/10 | 7 %–65 % | 992 ± 58 s (7) |

- **Las 4 semillas del principio sobreestimaban los atascos:** 3 de 4 sugería ~75 %, y con 20 semillas da 45 %.
- **La fluctuación en contacto, de 5 a 20 %, no reduce los atascos de forma detectable.** Los intervalos se superponen por completo. En la comparación pareada no hay patrón: la semilla 104 se traba con todas las amplitudes, y otras se traban con una y no con otra. Las 3 de 3 que terminaron con 10 % en la primera prueba fueron casualidad.
- **El corte de 300 s es seguro:** la pausa más larga que terminó rompiéndose fue de 121 s (con 5 %); sin fluctuación, de 105 s.
- **Cuándo se traban:** las últimas salidas de las corridas trabadas van de 148 a 988 s, y quedan de 8 a 424 agentes adentro.

## Plan de los estudios (2026-11-04)

Respuestas del grupo; todas coinciden con lo recomendado.

1. **Modelo:** SFM sin fluctuación. Se reportan la probabilidad de atasco y el t_evac condicional a que la corrida termine; las trabadas van aparte.
2. **Punto b:** 20 realizaciones por esquema, para que terminen ~11.
3. **T\* para a, b y d:** se elige con el punto c (menor tiempo de ejecución). Para no esperar, una versión reducida de c corre en esta computadora solo para elegir T*.
4. **Segundo target:** 10 realizaciones por opción. Se elige la de menor t_evac; si las diferencias quedan dentro de las barras, se usa "alejarse" (−ŷ).
5. **dt:** 2, 1 y 0,5 ms con 10 semillas cada uno. Se usa el mayor dt cuyo caudal J no difiera significativamente del de 0,5 ms.
6. **Tiempos de ejecución (c y d):** 4 corridas a la vez, siempre con la misma carga, y declarado. Los corre un compañero con una computadora más potente, todos en esa misma computadora [TP05, p. 4], con el mismo commit y `-O3`, con `scripts/run_tiempos.py`, que registra procesador, núcleos, sistema y compilador.
7. **EDMD puro en d:** 3 realizaciones por N, con N ≤ 600. Para N mayores, solo TSDMD e híbrido.
8. **Para la consulta:**
   - animación de una corrida trabada con zoom al arco;
   - curvas de población de las 20 semillas;
   - probabilidad de atasco contra la amplitud de la fluctuación;
   - animación del híbrido coloreado por esquema.

Semillas por estudio, para no mezclarlas: dt 201–210, segundo target 301–310, punto b 401–420, punto c 501–510, punto d 601–605, recuperación 701–710. Dentro de cada estudio se usan las mismas semillas en todas las condiciones (comparación pareada).

## Paso temporal: dt = 2 ms (2026-11-04)

Test estadístico (`scripts/run_dt.py`, `scripts/resumen_dt.py`, `experiments/results/dt.csv`): TSDMD, N = 500, semillas 201 a 210.

| dt | Trabadas | Caudal J (p/s) | J − J(0,5 ms), IC 95 % | t_evac de las que terminan |
|---|---|---|---|---|
| 2 ms | 2/10 | 0,476 ± 0,026 | −0,009 ± 0,034 | 1018 ± 67 s (8) |
| 1 ms | 4/10 | 0,492 ± 0,070 | +0,011 ± 0,061 | 938 ± 54 s (6) |
| 0,5 ms | 5/10 | 0,485 ± 0,032 | referencia | 994 ± 61 s (5) |

Ninguna diferencia de J con el dt más chico es significativa, así que, por el criterio acordado, **dt = 2 ms**. En el choque aislado de los agentes más livianos, el error en la restitución normal con 2 ms es 0,09 %. Las barras son desvíos estándar entre realizaciones. El estudio de atascos y las animaciones de la consulta se hicieron con 1 ms; los estudios a–d usan 2 ms.

## Segundo target: "alejarse" (2026-11-04)

Estudio con TSDMD, N = 500, dt = 2 ms y semillas 301 a 310 (`scripts/run_segundo_target.py`, `scripts/resumen_segundo_target.py`, `experiments/results/segundo_target.csv`):

- Las ocho opciones dan t_evac entre 981 y 1064 s y caudales J entre 0,462 y 0,496 p/s, todos dentro de las barras.
- En todas se traban de 4 a 6 de 10 corridas.
- La de menor t_evac es el punto a D = 20 m (981 ± 50 s), y se superpone con "alejarse" (993 ± 61 s), así que, por la regla acordada, los demás estudios usan **"alejarse"**.
- **Inferencia:** el segundo target solo afecta el último metro, ya afuera; el cuello de botella está adentro, en la puerta.

## Medida del tiempo de ejecución (2026-11-04)

Decisión del grupo, coincide con lo recomendado. Se reportan dos medidas:

- **Principal, literal a la consigna:** el wall-clock de las corridas que terminan, es decir, de la simulación completa [TP05, p. 4].
- **Complementaria:** el costo por segundo simulado (wall-clock / tiempo simulado), que usa todas las corridas, incluidas las trabadas. **T\* se elige con esta medida**, porque con pocas semillas quedan muy pocas corridas que terminen.

## Corrección del híbrido: revisiones duplicadas (2026-11-04)

El primer barrido de T* mostró que, por cada paso de agente TSDMD, el híbrido costaba 80 % más que el TSDMD puro (~890 frente a 495 ns). Lo perfilé con gprof y encontré dos causas:

- **Revisiones duplicadas.** `schedule_check` se llamaba 7,2 millones de veces en 100 mil pasos (46 % del tiempo): cada cambio de esquema agregaba una cadena nueva de revisiones de la cota V_max por cada agente EDMD, y nunca se descartaban las anteriores. Ahora hay una sola revisión pendiente por agente, la más temprana.
- **Reintentos inútiles del pase a EDMD.** Los agentes TSDMD que no pueden volver a EDMD se reintentaban cada 10 pasos. Ahora se esperan el tiempo mínimo en que podrían cumplir el criterio: la brecha que falta no crece más rápido que 2 V_max, y la relajación no termina antes que con τ.

Las salidas del barrido viejo quedaron en `experiments/raw/descartadas/`. Las demás corridas del híbrido (prueba y animación de la consulta) son anteriores al arreglo. La deduplicación no cambia cuándo un agente pasa a TSDMD; la espera de los reintentos sí puede demorar algo la vuelta a EDMD y, con ella, cambiar un poco la trayectoria (el redondeo de v a v_d e ocurre en otro instante).

## Elección de T* = 0,05 s (2026-11-05)

- **Barrido reducido en paralelo** (`run_tstar.py`, 5 semillas, 7 corridas a la vez): no sirve para elegir. Una diferencia del 5 % queda tapada por la carga externa de la máquina, y el costo por segundo simulado depende de cuántos agentes quedaron trabados.
- **Benchmark corto controlado** (`scripts/bench_tstar.py`: corridas de a una, alternadas, los primeros 150 s, 3 repeticiones): tampoco distingue. La mediana de una misma configuración varió hasta 40 %. El menor mínimo fue el de T* = 0,2 s (10,20 s, contra 10,91 s del TSDMD puro), dentro del ruido.
- **Medición tranquila de 100 s** (5 repeticiones alternadas): TSDMD 6,87 s, híbrido con T* = 1 s 6,88 s (el arreglo dejó la maquinaria sin costo propio), híbrido con T* = 0,05 s 6,54 s, es decir 5 % más rápido.
- **Decisión del grupo:** T* = 0,05 s. Coincide con la medición tranquila, tiene casi el mínimo de pasos TSDMD (97,3 % del tiempo-agente) y deja agentes EDMD visibles en la animación del punto a. Se declara que el benchmark no distingue los T* chicos, y el punto c oficial (`run_tiempos.py`, en la computadora del compañero) lo confirma o lo corrige; si cambia, se rehacen a, b y d.
- **Inferencia (Amdahl):** el híbrido no puede ahorrar más que la fracción del tiempo-agente en vuelo libre, ~3 %, porque el tapón dura casi toda la evacuación.

## Presentación (2026-11-05)

- Mismo formato que el TP4: Beamer, PDF con fotogramas y enlaces, PPTX con los videos embebidos [GPRES, pp. 2–3], generados por script.
- Los estudios extra (dt, segundo target, regla de choque, recuperación de v_d, atascos) entran en el cuerpo; el grupo acepta pasarse de 13 minutos (ver [recomendaciones-modificadas.md](recomendaciones-modificadas.md)).
- Declaración de uso de IA al final, con un resumen de las recomendaciones del agente que el grupo modificó.
- Guion por integrante, en tres partes, con tiempos [GPRES, p. 3].

## Puntos a y b: TSDMD e híbrido (2026-11-05)

Corridas de `run_poblacion.py` (N = 500, semillas 401 a 420, dt = 2 ms, T* = 0,05 s), resumidas con `resumen_poblacion.py` en `experiments/results/poblacion.csv`. Las corridas se hicieron de a 7 en paralelo, así que los wall-clock no son los del punto c.

| Esquema | Trabadas | IC 95 % | t_evac (terminan) | J (terminan) |
|---|---|---|---|---|
| TSDMD | 7/20 | 15–59 % | 979 ± 65 s (13) | 0,500 ± 0,040 p/s |
| Híbrido | 8/20 | 19–64 % | 1006 ± 52 s (12) | 0,480 ± 0,026 p/s |

- Las diferencias están dentro de las barras: el híbrido no cambia la física.
- De las 15 trabadas, 11 se traban tarde, con 6 a 118 agentes adentro; 4 se traban temprano (quedan 251 a 456).
- **Esquemas en el híbrido:** todos los agentes arrancan en EDMD y en unos 30 s todos pasaron a TSDMD. En las 20 corridas hubo una sola vuelta de TSDMD a EDMD: una vez en el tapón, nadie vuelve a quedar aislado y relajado antes de salir.
- **Cota V_max:** ninguna violación; la rapidez máxima fue 1,91 m/s.
- **Relajación analítica en el híbrido (nueva medición):** los pasos de agentes aislados sin relajar son el 0,17 % de los pasos TSDMD con T* = 0,05 s (el 0,04 % de la primera medición era con otro T* y antes de la corrección de las revisiones). Sigue muy por debajo del 10 % acordado.
- **Fracción TSDMD:** el 97,4 % del tiempo-agente es TSDMD.

## EDMD puro en el punto a (2026-11-05)

Con discos duros, la regla de choque derivada y patadas cada δ = 0,05 s, las 20 corridas de N = 500 se traban, y temprano: salen entre 10 y 192 agentes, y después nadie más en 300 s (IC 95 % de la fracción trabada: 83–100 %). Cada corrida cuesta de 10 a 20 min de reloj: 1,48 s por segundo simulado, 20 veces TSDMD en las mismas condiciones (7 corridas en paralelo), con 100 a 190 millones de eventos. Queda para la consulta del 06/11, junto con los atascos del SFM.

**Hipótesis sobre por qué EDMD se traba temprano y TSDMD tarde (inferencia, 2026-11-05).** En el SFM la presión de la multitud se acumula a lo largo de las cadenas de contactos y comprime a los agentes que están frente a la puerta. En la corrida TSDMD de la semilla 401 (`animaciones/tsdmd_seed401.txt`), la superposición máxima a menos de 1,5 m de la puerta vale:

| t (s) | Adentro | ξ máx. | ξ medio de los contactos |
|---|---|---|---|
| 30 | 484 | 6,3 cm | 2,7 cm |
| 300 | 369 | 4,0 cm | 1,7 cm |
| 600 | 222 | 3,3 cm | 1,6 cm |
| 900 | 81 | 2,0 cm | 1,0 cm |
| 1000 | 27 | 1,0 cm | 0,4 cm |

Con superposiciones del 10–15 % del diámetro, los agentes se cuelan por la puerta de 0,8 m (dos diámetros medios son 0,86 m), y un arco no aguanta. Cuando quedan pocos adentro la compresión baja y el arco se vuelve estable: por eso casi todas las corridas TSDMD trabadas se traban al final. Los discos duros del EDMD no se comprimen: el arco es rígido desde el principio. **Verificación exploratoria:** TSDMD con k = 1,2 × 10⁶ N/m (diez veces mayor, menos compresión) y dt = 1 ms, en las semillas 401 a 403, que con el k del paper evacúan completas. Las tres se trabaron temprano: salieron 91, 75 y 177 agentes (`experiments/raw/exploracion/`). Es lo mismo que pasa con los discos duros del EDMD, y apoya la hipótesis. Son solo tres semillas: no es un estudio.

## Corrección de la relajación analítica del EDMD (2026-11-05)

Las corridas del estudio de recuperación con relajación analítica quedaron 11 h sin avanzar. Con la semilla 701 (N = 60, L = 15 m) el tiempo simulado se frenaba en t = 5,6357 s, con el mismo choque entre dos agentes repetido millones de veces en el mismo instante. La causa: después de un choque suave, la velocidad quedaba a menos del 1 % de v_d e y `set_trajectory` la redondeaba a v_d e. El redondeo deshacía el rebote, los agentes volvían a acercarse y el choque se repetía.

- **Arreglo:** un agente que queda relajado después de un evento sigue en línea recta con su velocidad, sin redondearla. Solo el evento de fin de relajación fija v = v_d e (si en ese instante hay un contacto, el choque se resuelve y ya no se redondea).
- **Tope:** si hay 10 millones de eventos seguidos sin que avance el tiempo, la corrida termina con un error en lugar de quedar colgada.
- **Prueba:** `test_schemes` corre esa configuración hasta t = 6 s.
- **Qué no cambia:** el EDMD con patadas (no usa ese redondeo) ni el híbrido (motor aparte). Las corridas de los demás estudios siguen valiendo.
- Con el arreglo, la relajación analítica cuesta entre 40 s y más de 5 min de reloj por corrida, contra unos 3 s con patadas.

## Recuperación de v_d en EDMD puro (2026-11-05)

`run_recuperacion.py` con el motor corregido (N = 60, L = 15 m, semillas 701 a 710), resumido en `experiments/results/recuperacion.csv`. J − J_TSDMD es la diferencia de caudal con el TSDMD de la misma semilla (corridas que llegan al 90 % de las salidas). Costos medidos con 7 corridas en paralelo.

| Variante | Trabadas | J − J_TSDMD (p/s) | Costo (ms por s simulado) |
|---|---|---|---|
| Patadas δ = 0,01 s | 5/10 | −0,01 ± 0,09 (4) | 61 |
| Patadas δ = 0,02 s | 3/10 | +0,08 ± 0,14 (6) | 28 |
| Patadas δ = 0,05 s | 2/10 | +0,01 ± 0,23 (7) | 18 |
| Patadas δ = 0,1 s | 2/10 | +0,07 ± 0,16 (7) | 10 |
| Patadas δ = 0,2 s | 2/10 | +0,07 ± 0,24 (7) | 7 |
| Analítica, tolerancia 0,003 rad | 2/10 | +0,13 ± 0,12 (7) | 1056 |
| Analítica, tolerancia 0,01 rad | 3/10 | +0,16 ± 0,11 (7) | 2170 |
| Analítica, tolerancia 0,03 rad | 9/10 | +0,05 (1) | 1788 |
| Analítica, tolerancia 0,1 rad | 4/10 | −0,12 ± 0,24 (5) | 2338 |
| TSDMD | 1/10 | 0 | 11 |
| Híbrido (T* = 0,05 s) | 3/10 | −0,01 ± 0,05 (7) | 10 |

- **Patadas:** ninguna difiere del SFM de forma significativa; el costo baja con δ. δ = 0,05 s, la de las corridas de a y b, cuesta menos que 2 veces TSDMD en este sistema chico.
- **Relajación analítica:** de 94 a 207 veces el costo de TSDMD (el avance conservador de cada par) y, con 0,003 y 0,01 rad, un caudal mayor que el del SFM (con 0,01 rad la diferencia pareada es +0,16 ± 0,11 en 7 pares: error estándar 0,04). El 9/10 de trabadas con 0,03 rad no sigue la tendencia de las otras tolerancias y queda sin explicar.
- **Conclusión:** en el EDMD puro conviene patadas. En el híbrido la recuperación la hace el SFM, al costo de TSDMD, y la relajación analítica ahorraría a lo sumo el 0,17 % de los pasos.

## Puntos c y d: tiempos de ejecución (2026-11-06)

Medidos por Francisco en una Apple M5 Pro (macOS, `g++` es Apple clang 21.0.0, -O3), con 4 corridas a la vez, sobre el commit d3f5e57 (`experiments/results/maquina.json`). Las salidas crudas están en `experiments/raw/tiempos` (no van al repositorio); `resumen_tiempos.py` las reproduce exactamente.

- **Muchas corridas se traban**, así que el wall-clock de las que terminan se promedia sobre pocas: en c terminan 5 a 7 de 10 por T*; en d, algunos grupos tienen 1 o 2 de 5 (en la figura, marcador hueco cuando termina una sola). EDMD puro solo termina con N = 100: para EDMD solo hay costo por segundo simulado. Por eso se muestran las dos medidas acordadas.
- **c, agregado:** el híbrido tarda 5,9 a 6,4 s con cualquier T*, y TSDMD 6,2 ± 0,2 s: todo dentro de las barras. EDMD puro cuesta 237 ms por segundo simulado, 38 veces TSDMD (6,3 ms).
- **c, pareado por semilla** (`tiempos-c-pareado.csv`): con T* = 0,5 y 1 s nadie llega a EDMD, las salidas son idénticas a las de TSDMD en las 10 semillas y el híbrido cuesta 1,1–1,4 % más (el costo fijo del esquema). Con T* ≤ 0,2 s la relación de costos con el TSDMD de la misma semilla va de 0,96 a 1,16 en promedio, con desvíos del 10 al 35 %, porque las trayectorias divergen: no se distingue ninguna ganancia. Es lo esperado: el ahorro posible es a lo sumo el 2,6 % del tiempo-agente (vuelo libre).
- **T\*:** ningún valor se distingue de otro, así que queda T* = 0,05 s y no se rehacen a, b ni d.
- **d:** con densidad constante, el costo por segundo simulado crece como N^1,2 para TSDMD e híbrido y como N^2,3 para EDMD; con L = 50 m, N^0,7 y N^2,4. El wall-clock de las que terminan crece como N^2,2 (densidad constante), porque también crece el tiempo de evacuación.
- **Inferencia:** el exponente menor con la sala fija se explicaría por el costo fijo de recorrer las celdas de una sala grande con pocos agentes (con N = 100 cuesta 2,5 ms/s con L = 50 m y 1,0 ms/s con L = 22 m).

## Consulta con la cátedra (06/11)

- **Masa proporcional al área:** aceptada.
- **Presentación:** casi sin prosa, todo en bullets, pero con toda la información crucial escrita; seguramente no se llegue a presentar todo, así que nada importante puede quedar solo para decirlo. Los experimentos extra sin efecto significativo van a un apéndice al final. Agregar dibujos explicativos de la implementación, en particular de cómo se modelan los choques en EDMD.
- **N = 200** en prácticamente todo el TP (la consigna dice N = 500 [TP05, p. 3]), salvo donde N no influye, como la elección del dt o los experimentos de tiempo de cómputo: así se ve más la diferencia con el híbrido y terminan muchas más corridas. Una vez elegido, N se mantiene en todo el TP; 200 fue el primer número que propuso el profesor.
- **Choques en EDMD:** se puede probar otra forma de modelarlos, más fiel al SFM, aunque quizás no haga falta con N = 200. Si EDMD puro sigue trabándose, la conclusión puede ser simplemente que EDMD no sirve para este sistema (aclaración explícita del profesor).

## Plan después de la consulta (2026-11-09)

Decisiones del grupo (preguntas 1 a 10 de esa fecha):

1. **Sala:** L = 50 m con N = 200 (densidad menor, más vuelo libre).
2. **Punto c:** se rehace con N = 200, en la computadora de Francisco.
3. **Punto d:** se rehace entero con el T* y la regla de choque finales; la variante de densidad constante pasa a referirse al sistema nuevo: L = 50 m·√(N/200).
4. **T\*:** se elige con un benchmark rápido en esta computadora; el punto c oficial viene después (ver [recomendaciones-modificadas.md](recomendaciones-modificadas.md)).
5. **a y b:** 30 realizaciones por esquema.
6. **Otra regla de choque en EDMD:** primero EDMD puro con N = 200 y la regla actual. Se prueba la alternativa solo si EDMD se traba significativamente más que TSDMD (intervalos de Clopper–Pearson del 95 % sin superponerse). Si la alternativa tampoco se acerca a TSDMD, la conclusión es que EDMD no sirve para este sistema.
7. **Alternativa:** núcleo duro reducido, con distancia de choque r_i + r_j − ξ̄ (y r_i − ξ̄/2 contra paredes), donde ξ̄ es la compresión media de los contactos en el tapón de TSDMD con N = 200.
8. **Recuperación de v_d:** se rehace con N = 200 y L = 50 m, con la regla final y las mismas variantes. Antes, una corrida analítica piloto: si tarda más de 30 min, la analítica se corre solo con 0,01 rad.
9. **Apéndice:** fluctuación en contacto (30 semillas por amplitud) y segundo target, rehechos con N = 200. En el cuerpo: regla de choque, dt y recuperación de v_d; atascos y compresión, solo si con N = 200 sigue habiendo atascos.
10. **dt:** se mantiene el estudio con N = 500, en una diapositiva del cuerpo.

## N = 200: TSDMD y EDMD puro, y la regla alternativa (2026-11-09)

- **TSDMD** (semillas 401 a 430): se traban 8 de 30 (IC 95 %: 12–46 %); las 22 que terminan tardan 374 ± 33 s, con J = 0,51 ± 0,04 p/s.
- **EDMD puro con la regla actual:** se traban 29 de 30 (IC 95 %: 83–100 %), casi todas al principio. Los intervalos no se superponen: por la decisión 6, se prueba la regla alternativa.
- **ξ̄ para la alternativa** (`medir_compresion.py`, corrida TSDMD de la semilla 401 con N = 200): promedio de los 12 371 contactos a menos de 1,5 m de la puerta, un cuadro por segundo: ξ̄ = 1,06 cm (mediana 0,92 cm, máximo 4,95 cm). Con N = 500 era mayor (hasta 6 cm), porque empuja más gente.
- **Benchmark de T\*** (`bench_tstar.py`, N = 200, horizonte 150 s, 5 repeticiones): inconcluso por carga externa (carga media de 15 en 8 núcleos). Mínimos: TSDMD 4,82 s, T* = 0,005 s 4,79 s, T* = 0,05 s 4,83 s; se repite con la máquina tranquila (`experiments/logs/bench_tstar-cargado.log`).
- **Regla alternativa (núcleo reducido en ξ̄ = 1,06 cm):** se traban 26 de 30 (IC 95 %: 69–96 %); las 4 que terminan tardan 425 ± 81 s. Sigue sin superponerse con TSDMD y la mejora frente a la regla original (29 de 30) no es significativa. Por la decisión 6, **la conclusión es que EDMD puro no sirve para este sistema**. Para c, d y la recuperación de v_d se usa la regla original (sin parámetros calibrados); la alternativa va al apéndice, por no tener efecto significativo (pauta de la consulta del 06/11).
- **Benchmark de T\* con la máquina más tranquila** (carga media ~4): mínimos de 5 repeticiones de 150 s simulados con la semilla 501: TSDMD 4,53 s; T* = 0,002: 4,69; 0,005: 4,58; **0,01: 4,51**; 0,02: 4,75; 0,05: 4,55; 0,1: 5,09; 0,2: 4,83; 0,5: 4,65; 1: 4,96 s. Por la regla del benchmark (menor mínimo, decisión 4) se usa **T\* = 0,01 s**. La diferencia con T* = 0,05 s (0,04 s, menos del 1 %) está dentro del ruido; el punto c oficial lo confirma o lo corrige.

## N = 200: híbrido, apéndice y piloto de la recuperación (2026-11-09)

- **Híbrido (T* = 0,01 s, semillas 401 a 430):** se traban 10 de 30 (IC 95 %: 17–53 %); las 20 que terminan tardan 392 ± 59 s, J = 0,49 ± 0,08 p/s. Equivalente a TSDMD (8 de 30; 374 ± 33 s). Hubo 9 vueltas de TSDMD a EDMD en 30 corridas.
- **Tiempos medidos acá:** el híbrido costó 42,6 ms por segundo simulado y TSDMD 71,6, pero TSDMD corrió con la máquina muy cargada por otros procesos (carga media ~15) y el híbrido con carga ~4. No se usan: los tiempos oficiales son los del punto c.
- **Prueba de la compresión con N = 200:** TSDMD con k = 1,2 × 10⁶ N/m y dt = 1 ms en las semillas 401, 403 y 404 (con el k del paper evacúan completas): las tres se trabaron temprano, con 87, 56 y 84 salidas.
- **Apéndice, fluctuación** (semillas 401 a 430): trabadas 8, 7, 6 y 6 de 30 con 0, 5, 10 y 20 %; intervalos superpuestos, sin efecto significativo.
- **Apéndice, segundo target** (semillas 301 a 310): ninguna opción se distingue de "alejarse", que se mantiene (regla de la nota 4).
- **Piloto de la relajación analítica** (tolerancia 0,01 rad, semilla 701): no terminó en 9 h 27 min y se detuvo. Avanza cada vez más lento al formarse el tapón: los primeros 10 s simulados cuestan 0,2 s de reloj, de 10 a 20 s cuestan 44 s y de 20 a 30 s más de 76 s. La decisión 8 no cubre este caso (ni con 0,01 rad es viable): queda consultado con el grupo.
- **Decisión del grupo sobre la analítica (opción a):** recuperación con N = 200 completa para patadas (δ = 0,01 a 0,2 s), TSDMD e híbrido; además, una ventana de los primeros 30 s simulados con las mismas variantes y la relajación analítica (0,01 rad), para comparar el costo por segundo simulado en la misma ventana. La conclusión esperada es que la analítica no es viable con N = 200.

## Recuperación de v_d con N = 200 (2026-11-09)

`run_recuperacion.py` (semillas 701 a 710), resumido en `recuperacion.csv` y `recuperacion-ventana.csv`. Costos medidos con 7 corridas en paralelo y carga externa variable: sirven para comparar órdenes de magnitud, no para el punto c.

- **Corridas completas:** con patadas se traban 10, 9, 9, 8 y 8 de 10 (δ = 0,01; 0,02; 0,05; 0,1; 0,2 s), como EDMD puro en a y b; TSDMD y el híbrido, 3 de 10. Casi no hay pares que terminen, así que el caudal ya no se puede comparar.
- **Ventana de 30 s:** la relajación analítica (0,01 rad) cuesta 27 ± 19 s de reloj por segundo simulado: 220 veces las patadas con δ = 0,05 s (0,12 s) y 508 veces TSDMD (0,054 s). Las patadas cuestan de 0,27 s (δ = 0,01 s) a 0,04 s (δ = 0,2 s) por segundo simulado.
- **Conclusión:** en EDMD puro, patadas; la relajación analítica no es viable con N = 200. En el híbrido la recuperación la hace el SFM.

## Puntos c y d con N = 200 (2026-11-09)

Medidos por Francisco en la Apple M5 Pro (Apple clang 21.0.0, -O3), con 4 corridas a la vez, sobre 085af60. El zip de las salidas crudas reproduce exactamente sus tres CSV.

- **c, promedios:** el híbrido tarda 1,16 a 1,26 s con cualquier T* (5 a 9 de 10 terminan); TSDMD 1,26 ± 0,13 s. Todo dentro de las barras. El menor es T* = 0,01 s, como en el benchmark: **queda T\* = 0,01 s** y no se rehace nada. t_evac no depende de T* dentro de las barras.
- **c, pareado:** con T* = 1 s las salidas son idénticas a las de TSDMD en las 10 semillas y el costo también (1,001 ± 0,019). Con T* ≤ 0,2 s, el costo por segundo simulado sobre el del TSDMD de la misma semilla va de 0,96 a 1,00 (promedio 0,976: un 2,4 % más barato); el más preciso, T* = 0,05 s: 0,973 ± 0,039 (error estándar 0,012). Con N = 500 no se distinguía; con N = 200 el vuelo libre es el 7 % del tiempo-agente.
- **EDMD puro en c:** 25,6 ms por segundo simulado, 7,6 veces TSDMD (3,4 ms). En estas semillas (501 a 510) terminan 3 de 10.
- **d:** el costo por segundo simulado crece como N^1,1 (densidad constante) y N^0,7 (L = 50 m) para TSDMD e híbrido, y como N^1,9 y N^2,5 para EDMD puro (hasta N = 600).

## Segunda consulta con la cátedra (2026-11-14)

- El profesor pidió bajar N de nuevo, a algo como 50, o incluso 20 si hace falta, para que se note más la mejora del híbrido. Con N = 200 el ahorro pareado fue de solo un 2,4 %, porque el vuelo libre es el 7 % del tiempo-agente.

Decisiones del grupo (preguntas 1 a 9 del 2026-11-14):

1. **N:** prueba rápida con N = 50 (10 semillas, híbrido contra TSDMD de la misma semilla). Si el ahorro es de al menos 20 % y está a más de 3 errores estándar de 0, N = 50; si no, N = 20.
2. **Sala:** L = 50 m.
3. **a y b:** 50 realizaciones por esquema.
4. **T\*:** Francisco corre primero el punto c con el N nuevo y se elige T* con esos datos, con la medida principal del tiempo de ejecución (menor tiempo medio de las corridas que terminan). Después corre d con ese T*.
5. **Punto d:** N ∈ {20, 50, 100, 200, 500, 1000}, en las dos variantes; densidad constante referida al sistema nuevo, L = 50 m·√(N/N_base); EDMD puro con 3 semillas y hasta N = 600.
6. **EDMD puro:** primero la regla original; si se traba significativamente más que TSDMD, núcleo reducido con el ξ̄ del N nuevo; si tampoco se acerca, EDMD no sirve.
7. **Recuperación de v_d:** piloto analítico con el N nuevo; si tarda menos de 30 min, estudio completo con las 4 tolerancias; si no, ventana de 30 s.
8. **Apéndice:** fluctuación, segundo target y prueba con k mayor, rehechos con el N nuevo.
9. **Resultados de N = 200:** se reemplazan (N = 200 aparece en el barrido de d).

## N = 20 (2026-11-14)

- **Prueba de N** (`piloto_n.py`, semillas 801 a 810, corridas de a una, T* = 0,01 s): con N = 50 el híbrido cuesta 0,856 ± 0,057 veces TSDMD por segundo simulado (ahorro de 14,4 %, error estándar 1,8 %): no llega al 20 % acordado. Con N = 20: 0,667 ± 0,103 (ahorro de 33 %, error estándar 3,3 %). **Queda N = 20.**
- **TSDMD y EDMD puro con N = 20** (semillas 401 a 450): ninguna corrida se traba en ninguno de los dos (0 de 50; IC 95 %: 0–7 %). t_evac = 35 ± 2 s en ambos y J = 0,71 ± 0,08 p/s. Por la decisión 6, no hace falta la regla alternativa: EDMD puro usa la regla original. En esta computadora EDMD puro costó 0,2 ms por segundo simulado y TSDMD 19,5: los tiempos oficiales son los del punto c.
- **Costo de la grilla de celdas en salas grandes:** la grilla cubre toda la sala y en cada paso se recorren todas las celdas, aunque estén vacías. En el punto d con densidad constante (L = 50 m·√(N/20), hasta 354 m con N = 1000) ese término crece con el área, es decir, como N.
- **Recuperación de v_d con N = 20** (semillas 701 a 710): el piloto analítico tardó 0,02 s, así que el estudio va completo (decisión 7). Ninguna corrida se traba. Patadas (δ = 0,01 a 0,2 s) y analítica (0,003 a 0,1 rad) dan el mismo caudal que TSDMD, dentro de las barras. Costos en esta computadora: patadas 0,06 a 0,37 ms por segundo simulado, analítica 0,25 a 1,6 (1,9 a 12,5 veces las patadas con δ = 0,05 s), TSDMD 21, híbrido 13,5 (con T* = 0,01 s; se rehace si el punto c elige otro T*).
- **Atascos con N = 20 (decisión del grupo, opción a):** ninguna corrida se traba, así que todo lo que estudiaba atascos (arco, compresión, k mayor, fluctuación y núcleo reducido de EDMD) va al apéndice con los datos de N = 200, aclarado como "Atascos con N = 200". En el cuerpo queda el contraste: con N = 20 no se traba ninguna corrida; con N = 200, TSDMD se trababa en 8 de 30. El segundo target sí se rehizo con N = 20 (sin diferencias; se usa "alejarse").

## Punto c con N = 20 y elección de T* (2026-11-15)

Medido por Francisco en la Apple M5 Pro, 4 corridas a la vez, sobre ada2851; el zip de las salidas crudas reproduce exactamente `tiempos-c.csv` y `tiempos-c-pareado.csv`. Ninguna corrida se traba.

- **Tiempo de ejecución medio** (las 10 terminan): crece con T*, de 47,2 ± 6,0 ms (T* = 0,002 s) a 59,2 ± 3,3 ms (T* = 1 s); TSDMD 71,9 ± 6,0 ms; EDMD puro 0,5 ± 0,2 ms. t_evac = 35,0 ± 1,9 s con cualquier esquema.
- **Pareado:** el híbrido cuesta 0,660 ± 0,098 veces TSDMD con T* = 0,002 s y 0,827 ± 0,062 con T* = 1 s; EDMD puro, 0,007 ± 0,003.
- **Decisión 4:** se usa **T\* = 0,002 s** (menor tiempo medio), que es el mínimo permitido (T* ≥ Δt). Entre 0,002 y 0,02 s las diferencias son menores que el desvío.
- **Observación:** con T* = 0,002 s solo el 11,6 % del tiempo-agente es TSDMD, pero el híbrido cuesta el 66 % de TSDMD. El motor saltea el paso de Beeman cuando no hay ningún agente TSDMD, pero si hay al menos uno el paso recorre la grilla de celdas de toda la sala: el costo depende de la fracción de pasos con algún agente TSDMD, no del tiempo-agente.
- Francisco corrió además el punto c con N = 50 (`experiments/results/n50`).

## Relajación analítica en el híbrido (2026-11-15)

Con N = 20, el 87 % de los cuadros de agentes TSDMD del híbrido (corrida animada de la semilla 401) son de agentes sin contactos que todavía no se relajaron. El 41 % está afuera de la sala: al cruzar la puerta, el target cambia a −ŷ y el agente sigue en TSDMD hasta retirarse. El 100 % de los agentes pasa alguna vez a TSDMD, al llegar a la puerta. El contador del motor (`isolated_unrelaxed_steps`) sobreestimaba: sumaba de una vez los pasos proyectados hasta la relajación y dio 111 %. Por el criterio acordado (> 10 %), la relajación analítica se implementa en el híbrido.

Decisiones del grupo:
1. **Variante principal:** el punto c se corre con las dos variantes del híbrido (recuperación por el SFM y relajación analítica); si dan la misma física, la más barata pasa a ser la principal en a, b, d y la recuperación.
2. **T\*:** se rehace el barrido de c con la variante principal y se elige el menor tiempo medio de las corridas que terminan.
3. **c y d se miden en esta computadora**, con 4 corridas a la vez; el punto c de la M5 (N = 20) queda solo como antecedente.
4. **Contador:** se corrige en el motor: en cada paso, los agentes TSDMD sin contactos y sin relajar.

## Punto c con N = 20 en esta computadora (2026-11-15)

Intel Core i7-1165G7, 4 corridas a la vez, con el motor de esta fecha: d4ff391 más la relajación analítica en el híbrido, todavía sin commit (huella de las fuentes `cpp/src/*.cpp cpp/include/tp5/*.hpp`: 5dc7e8a682d587dc). El punto c de la M5 quedó en `experiments/results/n20-m5` y `experiments/raw/tiempos/base20-m5`.

- **Pareado (costo sobre el del TSDMD de la misma semilla):** variante SFM, de 0,64 (T* = 0,002 a 0,01 s) a 0,87 (T* = 1 s); variante analítica, de 0,28 ± 0,16 (T* = 0,002 s) a 0,79 (T* = 1 s); EDMD puro, 0,006.
- **Tiempo medio de las corridas que terminan** (terminan todas): analítica con T* = 0,002 s, 41 ± 22 ms; SFM con T* = 0,01 s, 92 ± 15 ms; TSDMD, 147 ± 29 ms; EDMD puro, 0,9 ± 0,4 ms.
- **t_evac = 35 ± 2 s** con cualquier esquema, variante y T*: la misma física.
- **Decisión 1:** la variante analítica pasa a ser la principal del híbrido (a, b, d y la recuperación).
- **Decisión 2:** con la variante analítica, el menor tiempo medio es con **T\* = 0,002 s**, que se mantiene.
- Con la relajación analítica, el tiempo-agente TSDMD baja del 11,6 % al 4,3 %.

## Punto d con N_base = 20 (2026-11-15)

Esta computadora, 4 corridas a la vez, el mismo motor que el punto c. N ∈ {20, 50, 100, 200, 500, 1000}; densidad constante con L = 50 m·√(N/20) (hasta 354 m) y sala de 50 m; híbrido con relajación analítica y T* = 0,002 s; EDMD puro hasta N = 500, con 3 semillas.

- **Costo por segundo simulado del híbrido sobre TSDMD (densidad constante):** 0,26 con N = 20 y 0,98 con N = 1000. El ahorro es el vuelo libre: con muchos agentes casi todo el tiempo es tapón.
- **EDMD puro:** el más barato con pocos agentes, pero su costo crece mucho más rápido (ajuste N^3,1 con densidad constante, contra N^1,0 de TSDMD y N^1,4 del híbrido) y desde N ≈ 100–200 se traba.
- **Atascos:** con N ≥ 200 se traban TSDMD y el híbrido en parte de las corridas, y EDMD puro en todas.

## Estudio para elegir N (2026-11-15)

Objetivo (pedido del grupo): un N en el que EDMD puro se encarezca por la densidad en la puerta, TSDMD la resuelva y el híbrido sea el más barato de los tres por usar EDMD en las zonas de baja densidad. El estudio va al apéndice y el N elegido rige todo el TP. Pista del punto d (sala de 50 m, 5 corridas sin parear): con N = 50 EDMD puro es el más barato (1,0 ms/s contra 3,9 del híbrido y 4,5 de TSDMD); con N = 100 el híbrido ya es el más barato (5,6 contra 6,2 y 7,8).

Decisiones del grupo:
1. **N ∈ {20, 30, …, 100}**, sala de 50 m, los tres esquemas; híbrido con relajación analítica y T* = 0,002 s.
2. **Criterio:** por semilla, costo del híbrido sobre el de TSDMD y sobre el de EDMD puro. Califican los N donde las dos relaciones están por debajo de 1 por más de 3 errores estándar; entre ellos se elige el de mayor margen sobre el segundo mejor, 1 − máx(relación con TSDMD, relación con EDMD).
3. **Atascos:** sin restricción; se reportan.
4. **20 semillas por N** (901 a 920), comparadas semilla por semilla con el costo por segundo simulado (vale también para las corridas trabadas). En esta computadora, 4 corridas a la vez.
5. Con el N elegido se rehace todo: a, b, c (T*), d con esa base, recuperación de v_d y segundo target.

**Resultado del estudio (`resumen_elegir_n.py`, `experiments/results/elegir-n.csv`):** por semilla, el híbrido cuesta sobre TSDMD 0,22 (N = 20), 0,52 (30), 0,76 (40), 0,87 (50), 0,88 (60), 0,90 (70), 0,96 (80), 0,96 (90) y 0,93 ± 0,02 (100); sobre EDMD puro, 41, 48, 17, 3,7, 2,2, 1,5, 1,07, 0,78 y 0,63 ± 0,05. EDMD puro es el más barato hasta N = 70; el híbrido es el más barato desde N ≈ 80–90 y solo con N = 100 lo es por más de 3 errores estándar frente a los dos: **califica N = 100**, con un margen de 6,8 % sobre TSDMD. Trabadas con N = 100: TSDMD 4, híbrido 3 y EDMD 13 de 20. Tensión observada: donde el híbrido es el mejor de los tres, su ventaja sobre TSDMD es chica, porque casi todo el tiempo es tapón; donde ahorra mucho frente a TSDMD (N chico), EDMD puro es más barato todavía.

**Decisión del grupo:** N = 100, como indica el criterio; se rehace todo. Como con N = 100 hay atascos, vale lo acordado el 09/11: atascos y compresión en el cuerpo, rehechos con el N nuevo (fluctuación, compresión, prueba con k mayor y, si EDMD se traba significativamente más que TSDMD, núcleo reducido).

## Grilla de celdas dispersa y nuevo estudio de N (2026-11-15)

**Punto c con N = 100 y la grilla completa** (10 semillas, 501 a 510; archivado en `experiments/results/grilla-completa/n100` y `experiments/raw/grilla-completa/tiempos-base100`): el híbrido cuesta lo mismo que TSDMD semilla por semilla (de 0,98 a 1,26 según T* y la variante, con desvíos de hasta ±0,6), y EDMD puro se traba en 9 de 10. Dos causas:
- **Física:** con N = 100, el 81 % del tiempo-agente del híbrido es TSDMD (semilla 501: 3,42 M de 4,22 M pasos-agente). Casi todo es cola en contacto en la puerta; el híbrido solo ahorra en los primeros ~30 s de vuelo libre.
- **Implementación:** la grilla de celdas del CIM se vaciaba y se recorría entera en cada paso (~11 000 celdas de 0,5 m en la sala de 50 m), aunque hubiera un solo agente TSDMD. Ese costo fijo (~10 µs por paso) dominaba a TSDMD y al híbrido con pocos agentes, y no lo pagaba EDMD puro: empujó el estudio de N hacia N grandes.

Decisiones del grupo:
1. **Grilla dispersa:** solo se vacían y se recorren las celdas ocupadas, ordenadas, así que los pares se visitan en el mismo orden que antes. Las salidas son idénticas bit a bit (verificado contra corridas de c); solo cambia el tiempo: TSDMD es 3 veces más rápido con N = 100 y 13 veces con N = 20. Las pruebas pasan. Huella de las fuentes: bd189d5c53060d7a.
2. **Se rehace el estudio de N** con el motor nuevo, con el mismo criterio, las mismas semillas y el mismo rango, y se adopta el N que salga. Si ninguno califica, se toma el de mayor margen y se aclara que no es significativo.
3. **Punto c con 20 semillas** (501 a 520): con atascos, el pareo es ruidoso.

**Resultado del estudio con la grilla dispersa** (`experiments/results/elegir-n.csv`; el anterior quedó en `experiments/results/grilla-completa/elegir-n.csv`). El híbrido sobre TSDMD:

| N | Híbrido/TSDMD |
|---|---|
| 20 | 0,39 |
| 30 | 0,56 |
| 40 | 0,69 |
| 50 | 0,89 |
| 60 | 0,85 ± 0,03 (ee) |
| 70 | 0,92 |
| 80 | 0,96 |
| 90 | 0,90 |
| 100 | 0,86 |

El híbrido sobre EDMD puro: 5,7 (N = 20); 5,6 (30); 2,4 (40); 0,68 (50); 0,47 ± 0,05 (60); 0,37 (70); 0,32 (80); 0,24 (90); 0,22 (100).

- EDMD puro es el más barato hasta N = 40.
- **Califica solo N = 60**, con un margen de 15,3 % sobre el segundo mejor (TSDMD). N = 50 no califica: la relación con TSDMD no baja de 1 por 3 errores estándar.
- Trabadas con N = 60: TSDMD 1, híbrido 2 y EDMD puro 6 de 20.

**N = 60 en todo el TP**, salvo el estudio del dt y el punto d. Con N = 60 hay atascos, así que vale lo acordado el 09/11: atascos y compresión en el cuerpo, rehechos con N = 60.

## Punto c con N = 60: variante del híbrido y T* (2026-11-15)

Mismo motor (grilla dispersa), 20 semillas (501 a 520), 4 corridas a la vez (`experiments/results/tiempos-c*.csv`, `experiments/raw/tiempos/base60/c`).

**Tiempo medio de las corridas que terminan:**
- TSDMD: 98,1 ± 22,8 ms (16 de 20).
- EDMD puro: 176 ± 69 ms (17).
- Híbrido, variante SFM: 69 a 75 ms con T* de 0,005 a 0,5; 92 ms con T* = 1. El mínimo es 69,0 ± 16,9 ms con T* = 0,005 (20 de 20).
- Híbrido, variante analítica: 73,5 a 91 ms; el mínimo es 73,5 ± 17,9 ms con T* = 0,005 (19).

**Por semilla, costo sobre el de TSDMD:**
- Con todas las corridas: de 0,78 a 0,88 (SFM) y de 0,86 a 0,99 (analítica). Los desvíos son de ±0,3 a ±0,4, porque una semilla que se traba en un esquema y no en el otro rompe el pareo.
- Solo con los pares que terminan: 0,71 ± 0,15 (SFM, T* = 0,005) y 0,80 ± 0,23 (analítica, T* = 0,005).

**Por qué con N = 60 la analítica ya no ahorra:**
- En la variante SFM, cada agente cambia una sola vez de esquema: 60 cambios por corrida. Pasa a TSDMD al llegar a la cola y ahí se queda.
- En la analítica, los agentes de la cola entran y salen de EDMD: 287 cambios y 882 eventos por corrida con T* = 0,002, contra 60 y 18 en la SFM. Los eventos con trayectorias curvas cuestan el avance conservador.
- El tiempo-agente en TSDMD baja apenas: 52 % contra 58 % del de TSDMD puro.

**Por la regla acordada:** la variante principal es la más barata, la **SFM**, con la misma física (tiempo de evacuación de 82 s, contra 85 s de TSDMD). **T* = 0,005 s** es el de menor tiempo medio de las corridas que terminan. Entre 0,005 y 0,2 s las diferencias están dentro del ruido.

El estudio de N se hizo con la variante analítica y T* = 0,002 s. Con la SFM, el híbrido con N = 60 sale igual o más barato, así que la elección de N se mantiene.

## a, b, recuperación, d y atascos con N = 60 (2026-11-15 y 2026-11-16)

Motor con la grilla dispersa; híbrido con la variante SFM y T* = 0,005 s.

**a y b** (`resumen_poblacion.py`; 50 semillas, de 401 a 450):

| Esquema | Trabadas | IC 95 % | t_evac (de las que terminan) | Costo |
|---|---|---|---|---|
| TSDMD | 9/50 | 9–31 % | 83 ± 13 s | 1,6 ms/s |
| Híbrido | 5/50 | 3–22 % | 80 ± 10 s | 1,2 ms/s |
| EDMD puro | 11/50 | 12–36 % | 79 ± 13 s | 3,3 ms/s |

Con la variante SFM, en el híbrido hay 2 vueltas de TSDMD a EDMD en las 50 corridas. Los intervalos de EDMD puro y TSDMD se superponen, así que por la decisión 6 del 2026-11-09 no se corre el núcleo reducido con N = 60.

**Recuperación de v_d** (`resumen_recuperacion.py`; 10 semillas, de 701 a 710, 4 corridas a la vez):
- Piloto: la analítica más cara tarda de 31 a 84 s por corrida, así que se corrió el estudio completo (7 min).
- Caudal: todas las variantes coinciden con TSDMD dentro del ruido.
- Costo: las patadas cuestan de 0,8 a 8,1 ms/s (δ de 0,2 a 0,01 s); la analítica, de 36 a 234 ms/s.
- Conclusión: en EDMD puro conviene usar patadas.

**Punto d con base 60** (`resumen_tiempos.py d`; 4 corridas a la vez, unos 12 min):
- Con 20 agentes en la sala de 50 m, el híbrido cuesta 0,1 ms/s, TSDMD 0,4 y EDMD puro menos de 0,05.
- Con 1000 agentes, el híbrido y TSDMD cuestan lo mismo (~31 ms/s).
- EDMD puro se traba en todas las corridas desde N = 200, con un costo de 38 a 541 ms/s.

**Atascos con N = 60:**

*Compresión* (TSDMD, semilla 401, contactos a menos de 1,5 m de la puerta, cuadro por cuadro):

| N | ξ medio por cuadro | Máximo por cuadro (mediana) | Máximo en toda la corrida |
|---|---|---|---|
| 60 | 0,1–1,0 cm (promedio 0,42) | 0,9 cm | 2,5 cm |
| 200 | 0,1–1,9 cm (promedio 1,04) | 2,4 cm | 5,0 cm |

Las corridas trabadas quedan con 17 a 48 agentes adentro.

Corrección del 2026-11-16: al consultar al grupo se dijo "máximo ≤ 2 cm; con N = 200, 4–6 cm". Esos números eran imprecisos; la tabla tiene los medidos. El contraste, unas 2,5 veces más compresión con N = 200, se mantiene. La hipótesis de la compresión con N = 200 (los agentes comprimidos se cuelan y el arco aguanta cuando quedan pocos) no explica los atascos con N = 60.

*Prueba de rigidez y fricción* (`run_exploracion.py`, `resumen_rigidez.py`, `experiments/results/rigidez.csv`; las semillas 401 a 450, con dt = 1 ms en las variantes):

| Variante | Trabadas | IC 95 % | t_evac (de las que terminan) |
|---|---|---|---|
| Paper | 9/50 | 9–31 % | 82,7 ± 12,6 s |
| k × 10 | 0/50 | 0–7 % | 42,1 ± 2,5 s (por semilla, −41 ± 12 s) |
| k y κ × 10 | 13/50 | 15–40 % | 82,4 ± 12,3 s (por semilla, −0,5 ± 14,7 s) |

El efecto de k mayor viene de la fricción: la fricción del SFM es κ ξ Δv_t, y con ξ ∝ F/k, por unidad de fuerza normal escala con κ/k. Con la misma κ/k, el sistema se comporta como con los parámetros del paper. Con N = 200, k × 10 se trababa antes (tres semillas): ahí dominaba la compresión.

*Fluctuación* (`resumen_atascos.py`): trabadas 9, 3, 6 y 5 de 50 con 0, 5, 10 y 20 %, con intervalos que se superponen: sin efecto.

**Decisiones del grupo (2026-11-16):**
1. La prueba de k mayor se hace con 50 semillas y se agrega la de k y κ × 10.
2. Atascos: todo al apéndice. En el cuerpo queda solo la fracción de trabadas de a y b.
3. Apéndice, como contraste, sin duplicados: compresión y k mayor con N = 200, y el núcleo reducido de EDMD con N = 200. El arco y la rigidez y fricción, con N = 60.
4. El estudio de fluctuación sale de la presentación.

**Atasco animado:** la semilla 415, la que se traba más temprano (última salida a los 21 s, con 48 adentro).
