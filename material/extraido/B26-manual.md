# B26 — derivado manual por inspección visual

Fuente original: `material/externo/bibliografia-6-7/SFM_2000.pdf`. Helbing, D., Farkas, I. y Vicsek, T., “Simulating dynamical features of escape panic”, *Nature* 407, 487–490 (28 de septiembre de 2000).

La capa de texto del PDF es ilegible: `B26.txt` contiene caracteres sin mapeo de fuente y no sirve para buscar ni citar. Este derivado se elaboró por inspección visual de renders de las cuatro páginas: página completa a 110 dpi y recortes a 220 dpi de ecuaciones, parámetros y epígrafes. No reemplaza el original. Las citas usan la página del archivo PDF (1–4), que corresponde a las páginas impresas 487–490.

El artículo no tiene recuadro de *Methods* ni notas metodológicas separadas. Las ecuaciones y los parámetros están en el cuerpo del texto (páginas 1–3) y en los epígrafes de las figuras. **El artículo no especifica integrador numérico ni paso temporal Δt.**

## Contenido por página

- Página 1 (impresa 487): la columna izquierda, hasta la línea de puntos, es el final de otra carta de *Nature*, ajena a este artículo: referencias astronómicas sobre cefeidas, agradecimientos y correspondencia a “B.F.L.”. El artículo empieza debajo: título, autores y afiliaciones (Collegium Budapest; TU Dresden; Universidad Eötvös), resumen en negrita. En la columna derecha hay nueve rasgos empíricos del pánico de multitudes. Uno de ellos es que las presiones pueden llegar a 4.450 N m⁻¹. Siguen el planteo del modelo de fuerzas generalizado, la ecuación (1), la fuerza psicológica, la fuerza de cuerpo y la fricción deslizante.
- Página 2 (impresa 488): vector tangencial, diferencia de velocidad tangencial, ecuación (2), función g(x), ecuación (3) para paredes, valores de parámetros, irregularidad en los diámetros y fenómeno (1), la transición a la incoordinación por obstrucción. La figura 1 corresponde a una habitación de 15 m × 15 m con una puerta de 1 m: (a) instantánea; (b) tiempos de salida según v₀; (c) tiempo de salida de 200 personas y cantidad de heridos según v₀; (d) flujo J/v₀ según v₀. El epígrafe incluye el criterio de heridos y la ecuación de impaciencia.
- Página 3 (impresa 489): fenómeno (2), el efecto *faster-is-slower*; condiciones para la obstrucción; ensanchamientos de la ruta; fenómeno (3), el comportamiento de masa o *herding*, con la ecuación (4). La figura 2 muestra un corredor con ensanchamiento y la eficiencia E en función del ángulo φ.
- Página 4 (impresa 490): figura 3, una habitación con humo y dos salidas invisibles, estudiada según el parámetro de pánico p. Siguen las conclusiones, un pedido de datos empíricos, la fecha de recepción (2 de junio de 2000) y aceptación (31 de agosto de 2000), las referencias 1–20 y los agradecimientos.

## Ecuaciones (transcripción verificada visualmente)

Notación: negrita del original indicada como vector; `·` es producto escalar.

- Página 1, ecuación (1), aceleración:
  `m_i dv_i/dt = m_i [v_i^0(t) e_i^0(t) − v_i(t)] / τ_i + Σ_{j(≠i)} f_ij + Σ_W f_iW`,
  con `v_i(t) = dr_i/dt`. v_i^0 es la rapidez deseada, e_i^0 la dirección deseada y τ_i el tiempo característico de adaptación.
- Página 1, fuerza de interacción psicológica (repulsiva):
  `A_i exp[(r_ij − d_ij)/B_i] n_ij`, con A_i y B_i constantes.
  `d_ij = ||r_i − r_j||` es la distancia entre centros de masa. `n_ij = (n_ij^1, n_ij^2) = (r_i − r_j)/d_ij` es el versor normalizado que apunta de j hacia i. `r_ij = r_i + r_j` es la suma de radios. Hay contacto si `d_ij < r_ij`.
- Página 1, fuerzas de contacto inspiradas en medios granulares:
  “fuerza de cuerpo” `k (r_ij − d_ij) n_ij`, que contrarresta la compresión;
  “fuerza de fricción deslizante” `κ (r_ij − d_ij) Δv_ji^t t_ij`, que se opone al movimiento tangencial relativo.
- Página 2: `t_ij = (−n_ij^2, n_ij^1)` es la dirección tangencial y `Δv_ji^t = (v_j − v_i)·t_ij` la diferencia de velocidad tangencial. k y κ son “constantes grandes”.
- Página 2, ecuación (2):
  `f_ij = { A_i exp[(r_ij − d_ij)/B_i] + k g(r_ij − d_ij) } n_ij + κ g(r_ij − d_ij) Δv_ji^t t_ij`.
  g(x) vale cero si los peatones no se tocan (`d_ij > r_ij`) y, en caso contrario, es igual al argumento x.
- Página 2, ecuación (3), paredes (tratamiento análogo):
  `f_iW = { A_i exp[(r_i − d_iW)/B_i] + k g(r_i − d_iW) } n_iW − κ g(r_i − d_iW) (v_i·t_iW) t_iW`.
  d_iW es la distancia a la pared W, n_iW la dirección perpendicular a la pared y t_iW la tangencial.
- Página 2, epígrafe de la figura 1, impaciencia:
  `v_i^0(t) = [1 − p_i(t)] v_i^0(0) + p_i(t) v_i^max`,
  `p_i(t) = 1 − v̄_i(t)/v_i^0`.
  v_i^0(0) es la rapidez deseada inicial, v_i^max la máxima y v̄_i(t) la rapidez media en la dirección deseada de movimiento.
- Página 3, ecuación (4), mezcla de comportamiento individual y de manada:
  `e_i^0(t) = Norm[(1 − p_i) e_i + p_i ⟨e_j^0(t)⟩_i]`, con `Norm(z) = z/||z||`. ⟨e_j^0(t)⟩_i es la dirección media de los vecinos j dentro de un radio R_i. Un p_i bajo da comportamiento individualista y uno alto, de manada.
- Página 3, epígrafe de la figura 2, eficiencia relativa: `E = ⟨v_i·e_i^0⟩ / v_0`, entre 0 y 1.
- Página 4, epígrafe de la figura 3: la fuerza del efecto manada crece con p y con `h = π R² ρ`, donde `ρ = N/A` es la densidad.

## Parámetros (todos los valores numéricos legibles)

Página 2, salvo indicación:

| Magnitud | Valor | Comentario del artículo |
|---|---|---|
| m | 80 kg | “un hincha de fútbol promedio” |
| v_i^0 (rango) | puede superar 5 m s⁻¹ (hasta 10 m s⁻¹) | rapidez deseada posible |
| v_i^0 observada al salir de una habitación | ≈0,6 m s⁻¹ (relajado); ≈1 m s⁻¹ (normal); ≲1,5 m s⁻¹ (nervioso) | según la referencia 13 |
| τ_i | 0,5 s | estimación razonable del tiempo de aceleración |
| A_i | 2 × 10³ N | junto con B_i, reproduce la distancia mantenida a velocidades deseadas normales y ajusta los flujos medidos en cuellos de botella |
| B_i | 0,08 m | ídem |
| Flujo de calibración | 0,73 personas/s por una puerta efectiva de 1 m con v_i^0 ≈ 0,8 m s⁻¹ | dato medido (referencia 14) |
| k | 1,2 × 10⁵ kg s⁻² | junto con κ, determina los efectos de obstrucción en interacciones físicas |
| κ | 2,4 × 10⁵ kg m⁻¹ s⁻¹ | ídem |
| Diámetros 2r_i | uniformes en [0,5 m; 0,7 m] | irregularidad para evitar artefactos de configuraciones simétricas; aproxima anchos de hombros. Equivale a r_i ∈ [0,25; 0,35] m |

Todos los parámetros son idénticos para todos los peatones, para minimizar el número de parámetros (página 2). La única irregularidad introducida es la de los diámetros.

Escenarios y umbrales:

- Figura 1 (página 2): habitación de 15 m × 15 m, salida de 1 m, rapidez deseada idéntica `v_i^0 = v_0`, 200 personas en el panel (c). Desde v₀ ≥ 1,5 m s⁻¹ aparece salida irregular por obstrucción, con arcos que bloquean la salida y avalanchas al romperse. Por encima de 1,5 m s⁻¹ cae la eficiencia de salida, debido a empujones y fricción adicional. Alrededor de v₀ = 5 m s⁻¹ hay heridos, que pasan a ser obstáculos inmóviles, si la suma de las magnitudes de las fuerzas radiales dividida por la circunferencia supera 1.600 N m⁻¹ (referencia 5). Lectura aproximada de las curvas, no informada como número en el texto: el tiempo de salida de 200 personas tiene un mínimo de unos 115–120 s cerca de v₀ ≈ 1,5–1,8 m s⁻¹, y J/v₀ alcanza un máximo de ≈1,3 cerca de v₀ ≈ 1 m s⁻¹.
- Página 3: el efecto *faster-is-slower* aparece “si el parámetro de fricción κ es suficientemente grande”. Como la fricción no desacelera en promedio, la obstrucción requiere a la vez frenado por un cuello de botella y fricción interpersonal fuerte.
- Figura 2 (página 3): `v_i^0 = v_0 = 2 m s⁻¹`. Corredor de 3 m de ancho y 15 m de largo; las piezas triangulares centrales miden 2 × 3 m = 6 m. Flujo de entrada `J = 5,5 s⁻¹ m⁻¹`. Con un ensanchamiento, la eficiencia cae alrededor de 20 %.
- Figura 3 (página 4): N = 90 peatones en una habitación de A = 15 m × 15 m, con dos puertas invisibles de 1,5 m y `v_i^0 = v_0 = 5 m s⁻¹`. Radio de vecinos `R_i = R = 5 m`. La dirección se refleja al llegar a un borde. Si una salida está a menos de 2 m, el peatón abandona la habitación. En las figuras 3b–c el óptimo está en p = 0,4: unas 73,5 personas escapan en 30 s y 80 personas salen en un mínimo de unos 37 s. Ambos valores son lecturas de los gráficos.

## Observaciones del derivado (no son afirmaciones del artículo)

- Signos: en (2) la fricción usa `Δv_ji^t = (v_j − v_i)·t_ij`. En (3), para una pared inmóvil, la expresión equivalente es `−(v_i·t_iW)`. Por eso el término de pared lleva signo menos. Es una lectura de consistencia.
- Si se anula la fuerza social (A_i = 0), quedan el término de relajación hacia `v_i^0 e_i^0` con τ_i y las fuerzas de cuerpo y de fricción, que solo actúan con contacto (`g = 0` si `d_ij > r_ij`). El artículo no trata ese caso.
- No se leyó ningún valor de paso temporal, integrador, ruido ni tamaño de celda. Todo lo transcripto arriba se leyó sin ambigüedades.
