# B19 — localización y apoyo de lectura

Original: Computer Simulation Methods in Theoretical Physics, Dieter W. Heermann, segunda edición, Springer (1990 según créditos, página 2 del archivo).

Todas las citas usan página del archivo DjVu. El archivo tiene 155 páginas; la numeración impresa incorpora preliminares. La extracción usa OCR embebido, con errores de reconocimiento y bytes inválidos reemplazados por U+FFFD. No equivale a una transcripción corregida del libro entero.

Inspección visual: portada (página 1), diferencias centrales/multipaso (29), Verlet (38) y arranque/Velocity Verlet (39). Renders conservados en `material/figuras/tp4/`.

| Página del archivo | Impresa | Contenido relevante |
|---|---|---|
| 9 | XI | Índice general |
| 27 | 17 | Esquemas de integración y costo de evaluar fuerzas |
| 28 | 18 | Diferencias hacia adelante/atrás; error de discretización |
| 29 | 19 | Diferencias centrales; métodos multipaso y predictor-corrector |
| 38 | 28 | Verlet y velocidades centradas |
| 39 | 29 | Arranque y Velocity Verlet |

Transcripción de las relaciones centrales verificadas visualmente:

- p. 29: u'(t) = [u(t+h)−u(t−h)]/(2h) + O(h²); u''(t) = [u(t+h)−2u(t)+u(t−h)]/h² + O(h²).
- p. 38: r_i^(n+1) = 2 r_i^n − r_i^(n−1) + F_i^n h²/m; v_i^n = [r_i^(n+1)−r_i^(n−1)]/(2h). La velocidad calculada pertenece al paso n, no al n+1.
- p. 39: r_i^1 = r_i^0 + h v_i^0 + h² F_i^0/(2m); Velocity Verlet usa r_i^(n+1) = r_i^n + h v_i^n + h² F_i^n/(2m) y v_i^(n+1) = v_i^n + h(F_i^(n+1)+F_i^n)/(2m).

El resto del libro queda buscable en B19.txt, pero no fue transcrito ni verificado visualmente página por página. Priorizar T04 y TP04 para las decisiones del trabajo.

Control de cobertura: las páginas 4, 6, 8, 10 y 146 no producen texto; se renderizaron y verificaron visualmente como páginas en blanco. No son omisiones de la extracción.
