# Material para la consulta del 06/11: atascos permanentes

Problema 2 del TP5 con el SFM sin fuerza social [TP05, p. 3] [B26]: N = 500, L = 50 m, puerta de 0,8 m, radios uniformes en [0,18; 0,25] m, v_d = 1,5 m/s, TSDMD con Beeman y dt = 1 ms.

## Qué pasa

- El 45 % de las corridas se traba para siempre: 9 de 20 semillas, IC 95 % de 23 a 68 % (Clopper-Pearson).
- Se forma un arco estático en la puerta, con velocidades exactamente nulas (`atasco.mp4`, `atasco.png`): dos agentes apoyados sobre la pared, uno a cada lado de la puerta, sostienen al resto.
- La fricción del SFM es viscosa (κ ξ Δv^t), así que en reposo no actúa: el arco se sostiene solo con fuerzas normales y, sin ninguna fluctuación, no se rompe.
- Las que evacúan tardan 1007 ± 43 s (11 corridas). Las trabadas se cortan cuando no sale nadie durante 300 s; la pausa más larga que terminó rompiéndose fue de 121 s.
- `curvas-poblacion-20-semillas.pdf` muestra las 20 curvas de agentes adentro: en azul las que evacúan, en naranja las que se traban (la cruz marca el corte).

## Por qué se traban tarde (hipótesis)

- Con TSDMD y con el híbrido (20 semillas más, 401 a 420, dt = 2 ms), 11 de las 15 corridas trabadas se traban al final, con 6 a 118 agentes adentro.
- `compresion.png`: superposición de los contactos a menos de 1,5 m de la puerta, en una corrida TSDMD, en función de cuántos quedan adentro. Con la sala llena la presión de la multitud comprime los contactos hasta 6–7 cm, un 15 % del diámetro, y los agentes se cuelan por la puerta de 0,8 m; cuando quedan pocos, la compresión baja a 1 cm y el arco aguanta.
- EDMD puro (discos duros, sin compresión) se traba en las 20 corridas y temprano: salen entre 10 y 192 agentes.
- Prueba: TSDMD con k diez veces mayor (1,2 × 10⁶ N/m, menos compresión) en tres semillas que con el k del paper evacúan completas. Las tres se trabaron temprano, como el EDMD: salieron 91, 75 y 177 agentes.

## Qué se probó

Una fuerza aleatoria solo sobre agentes en contacto ("empujones"), de 5, 10 y 20 % de la fuerza de deseo m v_d/τ, renovada cada 0,1 s. No redujo los atascos de forma detectable: 3/10, 5/10 y 3/10 (`probabilidad-atasco.pdf`, barras de IC 95 %).

## Preguntas para la cátedra

1. ¿Es esperable que el SFM sin fuerza social se trabe con esta puerta? ¿Cómo quieren que se reporte el tiempo de evacuación: condicional a que la corrida termine, junto con la probabilidad de atasco?
2. ¿Se admite agregar algún mecanismo que rompa los arcos (fluctuaciones más fuertes, ruido sobre todos los agentes, reapuntar al estar bloqueado)? Es un apartamiento del paper.
3. EDMD puro, con discos duros, se traba siempre al principio. ¿Alcanza con reportarlo así en los puntos a y b, o esperan otra cosa del EDMD puro?
4. La presentación con todos los estudios dura unos 20 minutos. ¿Se puede pasar de los 13 minutos de la consigna?
5. ¿Se admite que la masa sea proporcional al área (m_i = 80 kg·(r_i/0,215 m)²), en lugar de 80 kg para todos [B26, p. 2]?

## Otras animaciones

`hibrido.mp4`: los primeros 120 s del esquema híbrido (T* = 0,05 s). En azul, los agentes resueltos por eventos (vuelo libre); en naranja, los de paso temporal (contactos posibles en T*, y el tapón).

Se regenera con `python scripts/build_consulta.py` (figuras) y con las corridas de `scripts/run_atascos.py` y `experiments/raw/animaciones/`.
