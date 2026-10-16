# Billar circular y TP4

## Contrato de entrega

Entrega antes del **23/10/2026 a las 13:00**, por Campus. Exposición de 13 minutos; PDF `SdS_TP4_2026Q2GXXCSS_Presentación.pdf` y ZIP `SdS_TP4_2026Q2GXXCSS_Codigo.zip`, donde se reemplazan grupo y comisión según la consigna. El ZIP debe pesar menos de 100 KB e incluir únicamente la versión final del código fuente del motor; se excluyen post-proceso, resultados, figuras y documentación [TP04, p. 1].

Las animaciones se ejecutan desde archivos de texto producidos por la simulación. En el PDF se entrega un fotograma con enlace explícito a YouTube o Vimeo; no archivos de animación ni enlaces a esos archivos en Drive/Campus [TP04, p. 1].

La consigna permite agentes como asistentes de programación, exige explicitar agente, modelo y uso en una diapositiva extra al finalizar la exposición y no permite que produzcan presentaciones o reportes de forma independiente [TP04, p. 4]. Estos apuntes y la preparación local no son una presentación ni un informe entregable.

Existe un [borrador local de presentación](../../entregas/tp4-billar-circular/presentacion/README.md) solicitado por el estudiante, con el formato del TP3 y revisión de GPRES/COR02/COR03. La asistencia para producir ese borrador está declarada; quedan pendientes elaboración final y revisión de los estudiantes, ensayo y cinco enlaces públicos de animaciones. No se considera una entrega final aprobada por el grupo.

## Sistema 1: comparación con solución analítica

Se comparan **Beeman, Verlet original, Velocity Verlet y Euler predictor-corrector**, para $h<10^{-2}\,\mathrm{s}$ [TP04, p. 1]. Los parámetros están en la **página 37 de T04**, aunque la consigna remite a la 36:

$$m=70\,\mathrm{kg},\quad k=10^4\,\mathrm{N/m},\quad
\gamma=100\,\mathrm{kg/s},\quad t_f=5\,\mathrm{s},$$
$$m\ddot r=-kr-\gamma\dot r,\qquad r(0)=1\,\mathrm m,
\qquad v(0)=-\frac{A\gamma}{2m},$$
$$r(t)=A e^{-\gamma t/(2m)}\cos\left(\sqrt{\frac{k}{m}-\frac{\gamma^2}{4m^2}}\,t\right).$$

La fórmula y los parámetros se verificaron visualmente [T04, p. 37]. **Inferencia:** $A=r(0)=1\,\mathrm m$ y $v(0)=-5/7\,\mathrm{m/s}$.

El ECM promedia diferencias de posición al cuadrado en todos los pasos temporales, no entre partículas ni entre realizaciones:

$$\operatorname{ECM}(h)=\frac1M\sum_{n=1}^{M}[r_n-r(t_n)]^2.$$

La notación explicita la normalización pedida; excluir $t=0$ es una convención propuesta que debe mantenerse para todos los métodos. Graficar ECM contra $h$ con ambos ejes logarítmicos y decidir con los resultados qué esquema funciona mejor. Para este sistema la exposición debe tener **una sola diapositiva**, únicamente con esa figura comparativa [TP04, p. 1] [TP04, p. 2]. Las ecuaciones de los métodos están en [integradores](paso-temporal-e-integradores.md).

## Sistema 2: modelo y estado

Dominio circular de radio $R=0{,}51\,\mathrm m$, partículas con $r=0{,}0175\,\mathrm m$, $m=0{,}025\,\mathrm{kg}$ y módulo inicial $v_0=1\,\mathrm{m/s}$. Las posiciones son aleatorias sin solapamientos y las direcciones uniformes en $[0,2\pi)$. Cuando están presentes, los dos obstáculos tienen radio $r$, masa infinita y centros $(\pm x_0,0)$ [TP04, p. 2].

Los contactos son resortes normales sin fricción ni disipación, con $k=10^4\,\mathrm{N/m}$. Para $\xi_{ij}=r_i+r_j-|\mathbf r_j-\mathbf r_i|>0$:

$$\widehat{\mathbf e}_{ij}=\frac{\mathbf r_j-\mathbf r_i}{|\mathbf r_j-\mathbf r_i|},\qquad
\mathbf F_i=\sum_j-k\xi_{ij}\widehat{\mathbf e}_{ij}.$$

La dirección va de $i$ a $j$; el signo negativo hace repulsiva la fuerza [TP04, p. 2]. Para la pared se recalcula cada paso:

$$\widehat{\mathbf n}=\frac{\mathbf r_i}{|\mathbf r_i|},\quad
\mathbf r_{\rm img}=(R+r)\widehat{\mathbf n},\quad
\xi_{iw}=|\mathbf r_i|+r-R.$$

Se aplica la fuerza solo si $\xi_{iw}>0$. La imagen es una construcción virtual para calcular el contacto, no otra partícula móvil [TP04, p. 3].

Todas las partículas comienzan frescas (azules). El primer contacto con cualquiera de los obstáculos las convierte en usadas (rojas) para siempre; siguen interactuando y $N$ permanece constante. Se pide Verlet con paso fijo y salida de posiciones, velocidades y color cada $h_{\rm salida}=nh$ [TP04, p. 2] [TP04, p. 3].

$$F_u(t)=N_u(t)/N,\qquad t_{90}=\inf\{t:F_u(t)\geq0{,}9\}.$$

La forma con primer cruce explicita la definición de la consigna [TP04, p. 3]. **Inferencia para el post-proceso:** $t_{100}$ es el primer instante con $N_u=N$, no el final de la corrida.

## Matriz de estudios obligatorios

| Punto | Configuración y repeticiones | Resultado exigido |
|---|---|---|
| 1.1–1.2 | Oscilador, 4 métodos, $t_f=5$ s, $h<10^{-2}$ s | ECM frente a $h$ en log–log; comparación en una sola diapositiva. |
| 2.1.a | Sin obstáculos, $N=300$, varios $h<10^{-2}$ s | Energía total frente al tiempo; escalar de error energético frente a $h$ para justificar el paso. |
| 2.1.b | Obstáculos en contacto, $x_0=r$, $t_f=30$ s; distintos $N$, al menos un $N>600$; al menos 10 realizaciones por $N$ | Tiempo de ejecución medio y desvío estándar; misma figura que TP3 1.1, medido en la misma computadora. |
| 2.2 | $N=100$, $t_{\max}=100$ s, $x_0\in[r,R-r]$; al menos 5 realizaciones por posición | Pocas curvas representativas de $F_u(t)$; $\langle t_{90}\rangle$ y barras frente a $x_0$; reportar corridas que no llegan y su $F_u(t_{\max})$; comparar con menor densidad, por ejemplo $N=20$. |
| 2.3 | Sin obstáculos, $N=100$, varias realizaciones | Distribuciones de rapidez en distintos tiempos hasta el estacionario; ajuste Maxwell–Boltzmann 2D con un único parámetro libre $k_BT$. |
| 2.4.a | Reutilizar salidas de 2.1.b | $\langle t_{90}\rangle$ y $\langle t_{100}\rangle$ frente a densidad; discutir posible óptimo. |
| 2.5 | Registro durante el desarrollo | Declarar agente, modelo y forma de uso. |

Requisitos del sistema 1 [TP04, p. 1] [TP04, p. 2]; estudios 2.1–2.3 [TP04, p. 3]; ajuste, densidad y declaración [TP04, p. 4]. El mapa de calor de $\langle t_{90}\rangle$ o $\langle t_{100}\rangle$ sobre $(x_0,N)$ es **opcional** (2.4.b) [TP04, p. 4].

## Energía, distribución y promediado

**Derivación para el post-proceso:** sumando los potenciales elásticos de contacto [T04, p. 42],

$$E(t)=\sum_i\frac m2|\mathbf v_i|^2+
\sum_{i<j}\frac k2[\max(0,\xi_{ij})]^2+
\sum_{i,o}\frac k2[\max(0,\xi_{io})]^2+
\sum_i\frac k2[\max(0,\xi_{iw})]^2.$$

En 2.1.a no hay término de obstáculos. Con estado inicial sin superposiciones, $E(0)=Nm v_0^2/2$. **Propuesta**, no imposición de la cátedra: usar $\varepsilon_E(h)=\max_t|E(t)-E(0)|/E(0)$, declarar horizonte y cadencia de muestreo y comprobar que esta no oculta máximos durante contactos. No fijar el paso definitivo antes de este estudio [TP04, p. 3].

La distribución exigida es

$$f(v;\theta)=\frac{mv}{\theta}\exp\left(-\frac{mv^2}{2\theta}\right),\qquad \theta=k_BT,$$

con un solo parámetro libre. Comparar el valor ajustado con $m\langle v^2\rangle/2=mv_0^2/2$ [TP04, p. 4]. **Inferencia numérica:** la referencia inicial es $0{,}0125\,\mathrm J$. Con contactos activos, parte de la energía está almacenada en los resortes; comprobar por separado energía cinética y potencial antes de interpretar diferencias con esa referencia.

El ajuste debe seguir el método de T00, que presenta una función de error y su minimización, no una curva elegida por apariencia [T00, p. 79] [T00, p. 80] [TP04, p. 4].

**Propuesta de agregación explícita:** construir un histograma normalizado por realización y tiempo con bins compartidos, luego promediar densidades entre realizaciones; si se muestran barras, indicar su definición. Obtener cada tiempo de cruce por realización antes de agregar. Esto responde a la devolución sobre precisar qué partículas y realizaciones se promedian [COR03].

**Tratamiento propuesto de corridas incompletas:** guardar tiempo de corte, umbral alcanzado y $F_u$ final. No reemplazar tiempos no observados por 30 o 100 s, ni descartarlos silenciosamente para calcular una media. Si se informa la media solo de quienes alcanzaron el umbral, identificarla como condicional y dar cuántos faltaron. Ver [dudas y conflictos](../dudas-y-conflictos.md).

## Preparación local y continuidad del TP3

El [desarrollo del TP4](../../entregas/tp4-billar-circular/README.md) reúne requisitos, orden de resolución y criterios de validación. El sistema 1 ya tiene implementación C++20 y post-proceso Python, con 28 corridas verificadas: ver el [registro técnico del oscilador](../../entregas/tp4-billar-circular/experiments/README.md). **Resultado local, no afirmación de la cátedra:** Beeman obtuvo el menor ECM en los siete pasos ensayados con las variantes acordadas; esto no determina por sí solo el paso del billar. Las [correcciones de comunicación](comunicacion-cientifica.md) se aplican desde el diseño de cada estudio. La comparación de rendimiento debe revisar el protocolo y la procedencia de las mediciones existentes del TP3 antes de reutilizarlas.

**Actualización local del sistema 2:** el motor del billar y el [estudio energético 2.1.a](../../entregas/tp4-billar-circular/experiments/billar-energia.md) están implementados y verificados. Se seleccionó inicialmente h=0,00005 s con tolerancia local de error energético máximo muestreado del 0,1 %; en la comprobación de 30 s el error fue 0,06022 %. Esto es evidencia de la implementación para N=300 sin obstáculos, no un umbral oficial ni garantía para los barridos restantes. El paso del primer contacto se conserva en el estado para el futuro post-proceso de conversiones.

**Actualización local 2026-10-16:** se completaron 50 corridas TP4 hasta N=650 y se recalcularon 60 corridas TP3 con el mismo protocolo de cronometraje en Apple M5 Pro; ver [registro de rendimiento y densidad](../../entregas/tp4-billar-circular/experiments/rendimiento-y-densidad.md). Las salidas se reutilizaron para conversiones: N=20 tiene media muestral completa de t90=21,1±4,2 s; varios grupos no alcanzan los umbrales en 30 s. Se informan censuras y cotas inferiores, sin estimar medias ordinarias de tiempos incompletos. La inicialización N=650 conserva orden residual de la red hexagonal aleatorizada; no se la presenta como una muestra de equilibrio ni como evidencia de un óptimo global.

**Posición, punto 2.2:** el [barrido local de obstáculos](../../entregas/tp4-billar-circular/experiments/posicion-obstaculos.md) comprende once posiciones, N=100 y N=20, cinco realizaciones por punto y 100 s: 110 corridas. Tras controles energéticos se usó h=0,0000125 s. Todas alcanzaron t90; las menores medias de la grilla fueron x0=0,16 m con 13,6±1,0 s para N=100, y x0=0,3975 m con 9,2±1,1 s para N=20 (desvíos entre cinco realizaciones). Son resultados locales, no una localización exacta ni una prueba de significancia del óptimo. La comparación es compatible con un efecto de la mezcla por colisiones, cuya frecuencia no se midió directamente. Se generaron curvas Fu(t) estáticas y una animación física independiente, con promedios identificados [COR03].

**Rapidez, punto 2.3:** el [estudio local sin obstáculos](../../entregas/tp4-billar-circular/experiments/rapidez.md) reúne diez realizaciones N=100 de 60 s, precedidas por un ensayo preservado de 30 s. Se comprobó estabilidad descriptiva entre ventanas de 10 s y se ajustó el histograma medio de [10,60) s por mínimos cuadrados, con kBT como único parámetro [TP04, p. 4] [T00, pp. 79–80]. El ajuste da 0,0123986 J; los ajustes individuales tienen media ± desvío de 0,01240±0,00008 J. La referencia inicial es 0,0125 J; la cinética media medida es 0,0123234 J y el potencial medio por partícula 0,0001765 J. La energía almacenada en contactos explica por qué la cinética no tiene que coincidir con la referencia inicial; no explica por sí sola la diferencia entre mínimos cuadrados y segundo momento. La ventana elegida no identifica el primer instante exacto de relajación. Las barras representan desvíos entre realizaciones, no una incertidumbre formal del ajuste a la media [COR02] [COR03].

**Densidad y mapa, cierre local de 2.4.a–b:** el [registro reproducible](../../entregas/tp4-billar-circular/experiments/densidad-y-mapa.md) conserva las 50 salidas obligatorias de 30 s y agrega seguimiento refinado hasta 300 s, extensión selectiva de tres casos N=400 a 600 s y un grupo exploratorio N=50 completado a diez realizaciones. Se ejecutaron 154 corridas nuevas y se verificó conservación energética máxima muestreada inferior a 0,02671 %, con criterio local 0,1 %. No se modificó el benchmark de rendimiento.

Con x0=r y diez realizaciones por N={20,50,100,200,400,650}, el menor t90 medio observado es N=50: 20,4±3,5 s; el menor t100 medio es N=20: 41±14 s, frente a 42,5±8,1 s para N=50. Son mínimos muestrales por criterio, no prueba de óptimos poblacionales o globales. N=650 mantiene diez censuras en ambos umbrales a 300 s, con Fu medio 4,32 %; sus tiempos completos no se extrapolan. El DCM radial a 100 s es menor que en N=400, compatible con menor transporte radial; el sistema no está inmóvil. La frecuencia de choques y una causa exclusiva no se midieron; además cambia la familia de inicialización para N=650 [TP04, pp. 2–4] [COR03].

El [mapa de calor](../../entregas/tp4-billar-circular/experiments/figures/density-position-heatmap.png) usa t90, N={20,50,100,200}, once posiciones y cinco realizaciones: 220 casos, todos con t90 observado antes de 100 s. Las menores medias por fila están en x0={0,3975;0,3025;0,16;0,2075} m, respectivamente. La resolución 0,0475 m y la dispersión no permiten afirmar óptimos continuos exactos ni una ley monótona de la posición óptima con N. Los [cortes con desvíos](../../entregas/tp4-billar-circular/experiments/figures/density-position-cuts.png) muestran la variabilidad entre realizaciones [TP04, p. 4] [COR03].
