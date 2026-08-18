# Bandadas autopropulsadas y TP2

## Modelo estándar de Vicsek

El modelo se desarrolla en una caja cuadrada continua de lado $L$ con contorno periódico. Cada partícula puntual tiene rapidez constante $v$, orientación $\theta$ y radio de interacción $r=1$; el paso temporal es $\Delta t=1$ [T02, p. 40]. La cátedra usa posiciones y orientaciones iniciales aleatorias y $v=0{,}03$ [T02, p. 41].

La posición y la orientación se actualizan como

$$
\mathbf{x}_i(t+1)=\mathbf{x}_i(t)+\mathbf{v}_i(t)\Delta t,
$$

$$
\theta_i(t+1)=\operatorname{atan2}\!\left(\langle\sin\theta(t)\rangle_r,\langle\cos\theta(t)\rangle_r\right)+\Delta\theta,
$$

donde el promedio incluye a la propia partícula y a las vecinas dentro de $r$, y $\Delta\theta$ es uniforme en $[-\eta/2,\eta/2]$ [T02, p. 42]. Usar `atan2` evita la ambigüedad de cuadrante del cociente entre seno y coseno.

Las variables de control destacadas son rapidez $v$, densidad $\rho=N/L^2$ y amplitud de ruido $\eta$. La polarización

$$
v_a=\frac{1}{Nv}\left|\sum_{i=1}^{N}\mathbf{v}_i\right|
$$

tiende a 0 en desorden y a 1 cuando las partículas están alineadas [T02, p. 44]. El artículo original interpreta la pérdida de polarización al aumentar el ruido como una transición cinética orden–desorden [B14, p. 2] [B14, p. 3].

## Interacción tipo votante

En el modelo estándar cada partícula adopta el promedio angular de todas sus vecinas. En el modelo votante elige al azar una sola vecina y copia su dirección, agregando luego ruido; esa es la diferencia operativa central exigida por el TP2 [TP02, p. 2]. Sin ruido, la versión votante forma dominios de orientación y llega a consenso polar; el tiempo de consenso depende no monótonamente de la densidad porque la movilidad y la formación de clusters alteran la dinámica de imitación [B07, p. 1] [B07, p. 3] [B07, p. 4]. Con ruido, el movimiento permite una fase ordenada y una transición a ruido crítico positivo, a diferencia del caso estático en el límite termodinámico [B09, p. 1].

La evidencia empírica advierte que las bandadas reales no necesariamente usan una vecindad métrica fija: para estorninos se infieren interacciones topológicas con un número aproximadamente fijo de vecinos, independientemente de la distancia [B06, p. 3] [B11, p. 3]. Esta ampliación externa no cambia la regla que debe implementarse en el TP.

## Contrato del TP2

El sistema pedido tiene $L=10$, contorno periódico y densidades $\rho=2,4,8$. Se deben estudiar los modelos estándar y votante en función de $\eta$ [TP02, p. 1]. Para cada modelo y densidad hay que producir:

- animaciones con vectores velocidad coloreados por ángulo;
- evolución temporal de $v_a$, marcando el inicio del estacionario;
- $v_a$ estacionario contra $\eta$ con barras de error;
- evolución y promedio estacionario de $S$, la fracción de partículas del cluster más grande;
- $v_a$ contra $S$;
- comparaciones directas entre ambos modelos;
- tiempos del CIM comparables con los del TP1 [TP02, p. 2].

La simulación debe escribir archivos de texto y la animación debe ejecutarse como módulo independiente. Los entregables son presentación oral de 13 minutos, PDF de diapositivas, ZIP con solo la versión final del motor e informe. La fecha indicada es el 4 de septiembre de 2026 a las 13:00 [TP02, p. 1].
