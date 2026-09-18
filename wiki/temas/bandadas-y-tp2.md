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

Una indicación oral posterior de la cátedra amplía específicamente el estudio de $S$: como en las densidades originales la componente gigante cambia poco, para sus gráficos también se deben considerar las densidades nominales $1/\pi$, $1/(2\pi)$ y $1/(3\pi)$ [N-2026-08-22-densidades-s-tp2]. Esta ampliación no figura en el enunciado publicado. Con $L=10$ requerirían respectivamente $N\approx31{,}83$, $15{,}92$ y $10{,}61$; para esta resolución se adoptan los enteros más cercanos $N=32$, $16$ y $11$, con densidades reales $0{,}32$, $0{,}16$ y $0{,}11$.

La simulación debe escribir archivos de texto y la animación debe ejecutarse como módulo independiente. Los entregables son presentación oral de 13 minutos, PDF de diapositivas, ZIP con solo la versión final del motor e informe. La fecha indicada es el 4 de septiembre de 2026 a las 13:00 [TP02, p. 1].

## Devolución de la entrega

La entrega del Grupo 7 obtuvo nota 6 y la cátedra la consideró en líneas generales correcta [COR02]. Las observaciones específicas de este trabajo, útiles si se retoma el código o se compara con futuros trabajos:

- El motor calculaba $v_a$ y $S$ en cada paso del bucle principal. Se marcó como error importante: el motor debe generar solo la trayectoria y los observables van en un post-proceso aparte [COR02]. El paquete entregado en `entregas/tp2-bandadas/` conserva esa arquitectura; su documentación lo declara y no fue refactorizado.
- La diapositiva de parámetros mezclaba parámetros físicos ($L$, $r_c$, $v$, $\Delta t$, $\rho$, $\eta$) con datos que no lo son ($T$, $t_0$, $M$). El $t_0$ del estacionario es un resultado, no una entrada [COR02].
- La diapositiva de observables definía $v_a(t)$ y $S(t)$ instantáneos sin explicitar cómo se obtienen media y desvío estándar entre realizaciones [COR02]. El informe sí lo hacía en su sección de promedios y barras de error; la presentación debía mostrarlo también.
- El cociente entre los ruidos $\eta_{1/2}$ de ambos modelos, presentado como "Vicsek tolera entre 7,7 y 15,9 veces más ruido", fue objetado por poco claro y porque estas relaciones no suelen ser lineales [COR02].
- En el informe: la figura de medias por bloques no debía estar en la introducción, la figura de evolución de $v_a$ no correspondía a la sección de componente gigante, y la tabla y la figura de tiempos del CIM duplicaban información [COR02].

Las lecciones generalizables están sintetizadas en [Comunicación científica](comunicacion-cientifica.md).
