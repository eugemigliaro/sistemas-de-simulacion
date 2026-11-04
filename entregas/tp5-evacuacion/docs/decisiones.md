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

- **Fluctuación en contacto (N = 500, TSDMD, semillas 1, 3 y 4, que sin fluctuación se trababan):**
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
