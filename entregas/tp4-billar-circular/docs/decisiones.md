# Decisiones del TP4

Registro breve de las decisiones de modelado, implementación y análisis. Las citas siguen el catálogo de `material/`.

## Motor

- **Separación motor / post-proceso.** El motor C++ solo escribe estado: tiempo, posiciones, velocidades y color. Energía, Fu, t90, histogramas y ajustes se calculan en Python leyendo esos archivos, como marcó la cátedra en el TP2 [COR02] [TP04, p. 1].
- **Oscilador.** Parámetros de la teórica: m = 70 kg, k = 10⁴ N/m, γ = 100 kg/s, r(0) = 1 m, v(0) = −γ/2m, tf = 5 s [T04, p. 37].
  - *Verlet original:* r(t+dt) = 2r(t) − r(t−dt) + dt² a(t), con a(t) evaluada en v(t) = [r(t+dt) − r(t−dt)]/2dt. Como la fuerza es lineal, la ecuación se despeja exactamente para r(t+dt) [T04, p. 13].
  - *Velocity Verlet:* v(t+dt) aparece en a(t+dt); también se despeja [T04, p. 17].
  - *Beeman:* variante predictor-corrector para fuerzas que dependen de la velocidad [T04, p. 20].
  - *Euler predictor-corrector:* las tres etapas de la diapositiva 23, sin promedio de pendientes [T04, p. 23].
  - *Arranque:* el estado en −dt se estima con Euler hacia atrás [T04, pp. 13-14].
  - *Consecuencia:* al eliminar las velocidades, Verlet y Velocity Verlet dan la misma recurrencia de posiciones. Sus ECM coinciden hasta que, con dt ≤ 2·10⁻⁵ s, la recurrencia de dos pasos de Verlet acumula redondeo.
- **Billar.** Verlet original, como pide la consigna [TP04, p. 2]. La velocidad centrada v(t) se conoce después de calcular r(t+dt), así que el estado de t se escribe en ese momento y posiciones y velocidades quedan sincronizadas.
- **Fuerzas.** F = −k ξ ê para ξ > 0 con partículas, obstáculos fijos y la partícula imagen de la pared [TP04, pp. 2-3]. Con la imagen en (R + r) r/|r|, ξ = |r| + r − R y la fuerza es radial; se recalcula en cada paso. Los pares se buscan con celdas de lado ≥ 2r sobre [−(R + r), R + r] y cada par se recorre una vez.
- **Conversión.** Una partícula fresca pasa a usada en el primer paso en que se superpone con un obstáculo, y no vuelve atrás [TP04, p. 3].
- **Condiciones iniciales.** Posiciones uniformes en área por rechazo secuencial, sin superposición con la pared, los obstáculos ni otras partículas, y dirección de la velocidad uniforme en [0, 2π) [TP04, p. 2]. El rechazo se traba cerca de una fracción de área de 0,55: con obstáculos en contacto llega hasta N ≈ 430. Para N > 430 se eligen N sitios al azar de una red triangular con orientación y traslación aleatorias y se desordenan con 500 barridos de Monte Carlo de discos rígidos; es el mismo criterio que usó el TP3 para su punto 1.1. A esas densidades las partículas quedan casi ordenadas: no hay lugar para otra cosa.
- **Generador.** mt19937_64 con conversión explícita a [0, 1): la misma semilla da las mismas condiciones iniciales en cualquier biblioteca estándar.

## Estudios

- **Paso temporal (2.1.a).** N = 300 sin obstáculos, dt entre 10⁻⁵ y 5·10⁻⁴ s, 5 realizaciones y 300 s, que es el horizonte más largo del trabajo. Observable: δE = máx |E(t) − E(0)| / E(0) sobre los cuadros guardados cada 0,1 s. Criterio adoptado (no viene de la consigna): δE < 10⁻³. Resultado: dt = 2·10⁻⁵ s, que se usa en todos los demás estudios del billar. Con dt = 5·10⁻⁴ s todas las realizaciones divergen antes de 300 s.
- **Tiempo de ejecución (2.1.b).** Un harness (`cpp/bench`) enlaza el motor del TP4 y el del TP3 sin modificarlo, y cronometra solo la integración. La generación y la escritura quedan afuera. El TP3 corre su punto 1.1 (mesa vacía, tf = 30 s, red triangular por encima de 430 partículas). Las corridas son secuenciales y se hacen en la misma computadora [TP04, p. 3] [TP03, p. 3].
- **Densidad (2.4.a).** Se usan las mismas N, semillas, x0 = r y dt que en 2.1.b, así que los primeros 30 s son las mismas trayectorias. Como con N ≥ 200 ninguna llega a Fu = 0,9 en 30 s, se continúan hasta 300 s [TP04, p. 4].
- **Posición (2.2) y mapa (2.4.b).** Once x0 equiespaciados entre r y R − r, 10 realizaciones y 100 s. El mapa agrega N = 50 y N = 200 a las corridas de N = 20 y N = 100 del punto 2.2.
- **Resolución temporal.** Fu, t90 y t100 se calculan sobre los cuadros guardados (cada 0,05 s o 0,1 s). Es mucho menor que la dispersión entre realizaciones.
- **Rapidez (2.3).** N = 100 sin obstáculos, 30 realizaciones de 60 s. Bins de 0,1 m/s centrados en múltiplos de 0,1, para que v0 = 1 m/s caiga en el centro de un bin. El estacionario empieza en la primera ventana de 1 s a partir de la cual el kBT ajustado en cada ventana queda dentro de ±3 desvíos de la segunda mitad de la corrida. El ajuste sigue la Teórica 0: se barre kBT y se minimiza E(kBT) = Σ [f_i − f(v_i)]² sobre los centros de los bins del histograma promedio [T00, pp. 79-80]. El error de kBT es el desvío entre los ajustes de cada realización.
- **Estadística.** Cada observable escalar se calcula por realización y después se promedia. El error es el desvío estándar muestral entre realizaciones [T00, p. 69] [COR03]. Si alguna realización no llega a un umbral, no se informa una media: se informa cuántas no llegaron y Fu(tf).
