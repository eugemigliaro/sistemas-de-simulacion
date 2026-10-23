# Billar circular y TP4

## Contrato de entrega

Entrega antes del **23/10/2026 a las 13:00**, por Campus. Exposición de 13 minutos; PDF `SdS_TP4_2026Q2GXXCSS_Presentación.pdf` y ZIP `SdS_TP4_2026Q2GXXCSS_Codigo.zip`, donde se reemplazan grupo y comisión según la consigna. El ZIP debe pesar menos de 100 KB e incluir únicamente la versión final del código fuente del motor; se excluyen post-proceso, resultados, figuras y documentación [TP04, p. 1].

Las animaciones se ejecutan desde archivos de texto producidos por la simulación. En el PDF se entrega un fotograma con enlace explícito a YouTube o Vimeo; no archivos de animación ni enlaces a esos archivos en Drive/Campus [TP04, p. 1].

La consigna permite agentes como asistentes de programación, exige explicitar agente, modelo y uso en una diapositiva extra al finalizar la exposición y no permite que produzcan presentaciones o reportes de forma independiente [TP04, p. 4]. Estos apuntes y la preparación local no son una presentación ni un informe entregable.

La [presentación](../../entregas/tp4-billar-circular/presentacion/README.md) se armó con asistencia de agentes, a pedido del estudiante, con el formato del TP3 y las correcciones de GPRES, COR02 y COR03; el uso está declarado en la última diapositiva. Tiene un guion por integrante. Faltan los enlaces públicos de las tres animaciones, la revisión del grupo y el ensayo.

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

## Implementación y resultados locales

El [desarrollo del TP4](../../entregas/tp4-billar-circular/README.md) se reescribió desde cero el 21/10/2026: un motor C++20 que solo escribe estado y un post-proceso en Python que calcula los observables. Las decisiones de modelado y análisis están en el [registro de decisiones](../../entregas/tp4-billar-circular/docs/decisiones.md). Son resultados del grupo, no afirmaciones de la cátedra; los errores son desvíos estándar entre realizaciones [T00, p. 69] [COR03].

- **Oscilador (1.1–1.2):** Beeman da el menor ECM en todo el rango, $\approx13\,\%$ menos que Verlet. Beeman, Verlet y Velocity Verlet tienen pendiente 4 en log–log (error global de orden 2) y Euler predictor-corrector, pendiente 2. Verlet y Velocity Verlet dan la misma recurrencia de posiciones; con $h\le2\times10^{-5}$ s Verlet original toca un piso de redondeo.
- **Paso (2.1.a):** con $N=300$, 300 s y cinco realizaciones, $\delta E=\max_t|E(t)-E(0)|/E(0)$ vale $(2{,}6\pm1{,}0)\times10^{-4}$ con $h=2\times10^{-5}$ s y $(1{,}4\pm0{,}4)\times10^{-3}$ con $5\times10^{-5}$ s; con $5\times10^{-4}$ s las cinco realizaciones divergen. Con el criterio propio $\delta E<10^{-3}$ se adopta $h=2\times10^{-5}$ s en todo el billar.
- **Rendimiento (2.1.b):** $x_0=r$, $t_f=30$ s, $N$ de 20 a 650 y diez realizaciones por $N$; un harness enlaza el motor del TP3 sin modificarlo y corre su punto 1.1, en forma secuencial y en la misma computadora (Intel Core i7-1165G7). En ambos se mide solo la integración. El TP4 crece en forma lineal: $\times1{,}8$ y $\times2{,}0$ al pasar de 100 a 200 y de 200 a 400 partículas, con $33{,}8\pm0{,}3$ s para $N=650$. El TP3 crece $\times9{,}7$ y $\times19$, porque aumentan los choques y el costo de cada uno. Es más rápido hasta $N=400$ ($13{,}8\pm0{,}5$ s frente a $17{,}9\pm0{,}4$ s), pero con $N=650$ tarda $346\pm3$ s, unas 10 veces más.
- **Densidad (2.4.a):** con $x_0=r$, 300 s y diez realizaciones por $N$; para $N=20$ a 300 son las corridas de 2.1.b continuadas. Se incluyen solo las $N$ en las que las diez realizaciones llegan a $F_u=1$: de 2.1.b quedan 20 a 300 y se agregan 5, 10, 15 y 30. Con $N=1$ ninguna se convierte, con $N=2$ y $N=350$ una no termina, y desde $N=400$ falta $t_{100}$ en alguna (desde 550, también $t_{90}$). **Hay una densidad óptima:** $\langle t_{90}\rangle$ es mínimo con $N=20$, $17\pm5$ s, y queda a menos de un desvío hasta $N=50$ ($20{,}5\pm2{,}4$ s); sube a $27\pm6$ s con $N=10$, $45\pm42$ s con $N=5$ y $57\pm3$ s con $N=300$. Con pocas partículas faltan choques: la fuerza de la pared es radial y conserva el momento angular respecto del centro, así que cada partícula mantiene su parámetro de impacto $b$ y solo puede tocar los obstáculos en contacto si $b<3r$, lo que pasa con el 12,8 % de las condiciones iniciales. Con muchas partículas, se estorban.
- **Posición (2.2) y mapa (2.4.b):** once $x_0$ entre $r$ y $R-r$, diez realizaciones y 100 s; todas llegan a $t_{90}$. Con $N=100$ el mínimo es $14{,}7\pm1{,}6$ s en $x_0=0{,}16$ m, con medias a menos de un desvío entre 0,16 y 0,30 m; en $x_0=r$ da 22,8 s y en $R-r$, 31,5 s. Con $N=20$ el mínimo, $11\pm3$ s en 0,40 m, es una meseta entre 0,11 y 0,40 m. El mapa agrega $N=50$ (mínimo en 0,16 m) y $N=200$ (en 0,255 m). La resolución de 0,0475 m en $x_0$ no permite ubicar un óptimo continuo exacto.
- **Rapidez (2.3):** $N=100$ sin obstáculos, 30 realizaciones de 60 s; el estacionario empieza en 1 s. Ajustando por barrido de $E(k_BT)$ [T00, pp. 79–80], $k_BT=(1{,}242\pm0{,}007)\times10^{-2}$ J y $m\langle v^2\rangle/2=(1{,}2323\pm0{,}0005)\times10^{-2}$ J: difieren en un 0,8 %, del orden del desvío entre realizaciones. Evaluar $f$ en el centro del bin sesga el ajuste en $\approx0{,}2\,\%$. La diferencia con $mv_0^2/2=1{,}25\times10^{-2}$ J es la energía potencial de los contactos, $1{,}77\times10^{-4}$ J por partícula.
