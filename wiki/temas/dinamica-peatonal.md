# Dinámica peatonal

## Regímenes de comportamiento

La teórica distingue dos regímenes [T06, p. 2] [T07, p. 2]:

- **Normal o cooperativo:** rigen normas sociales, hay poco o ningún contacto físico, y las densidades son bajas o medias.
- **Competitivo o de estrés:** lo opuesto. Domina el instinto de supervivencia, y las presiones altas pueden causar asfixia o aplastamiento.

### Régimen competitivo y *faster is slower*

El caso típico es la evacuación de un recinto. Las primeras simulaciones microscópicas se propusieron sin validación experimental [T06, p. 4]. El Social Force Model predice cualitativamente el efecto ***faster is slower*** (FIS): con más velocidad deseada, el tiempo medio de evacuación de 200 personas primero baja y después sube [T06, p. 5] [T06, p. 34].

El efecto también aparece en sistemas análogos:

- Un silo 2D de granos sobre un plano inclinado y vibrado [T06, p. 7] [T06, p. 8].
- Ovejas apuradas [T06, p. 9] [T06, p. 11].
- Personas evacuando con competitividad baja y alta [T06, p. 13]. En un simulacro, unos 95 peatones salieron por una puerta de 69 cm [T06, p. 14].

En el SFM, la obstrucción con arcos que bloquean la puerta aparece desde $v_0\gtrsim1{,}5$ m/s. Por encima de ese valor cae la eficiencia de la salida [B26, p. 2].

### Régimen cooperativo

Experimentos estudian los mecanismos de navegación: aceleraciones y trayectorias durante una elusión [T06, p. 17] [T06, p. 18], y la probabilidad de esquivar girando, frenando o con ambas maniobras [T06, p. 19].

## Observables

- **Diagrama fundamental:** velocidad media contra densidad. La teórica superpone datos de Weidmann (1993), Mori y Tsukaguchi (1987), Predtechenskii y Milinskii (1978), Hankin y Wright (1958), Older (1968) y Helbing (2007). Las curvas difieren mucho entre sí a densidades altas [T06, p. 20] [T06, p. 21].
- **Caudal específico:** peatones por unidad de tiempo y de ancho de puerta. Las regulaciones adoptan 1,33 p/(m·s) y los datos experimentales van de 1,25 a 2,0. En condiciones normales se asume que el caudal es proporcional al ancho [T06, p. 22]. La teórica tabula valores de distintas fuentes entre 1,25 y 1,97 [T06, p. 23].

Estos son los dos observables con que se valida un simulador [T07, p. 38]. Otros observables típicos son los tiempos de tránsito y evacuación, los tiempos de espera, las curvas de población, los mapas de densidad y la ocupación por sectores [T07, p. 40].

## Modelos microscópicos

Hay dos familias [T06, p. 25]:

- **Continuos o basados en fuerzas:** partículas newtonianas con posición y velocidad continuas.
- **Discretos o basados en reglas:** espacio en grilla y transiciones de estado por reglas (autómatas celulares).

La teórica desarrolla un ejemplo de cada tipo y uno híbrido: Social Force Model, autómata *bionics-inspired* y Contractile Particle Model [T06, p. 26].

### Social Force Model

Cada peatón obedece una ecuación de Newton; el sistema es de $N$ ecuaciones acopladas que se integran con dinámica molecular [T06, p. 28]:

$$m_i\ddot{\mathbf r}_i=\mathbf F_{\rm granular}+\mathbf F_{\rm social}+\mathbf F_{\rm deseo}.$$

Cada término, en la notación de la teórica (verificada sobre las láminas):

- **Contacto (granular)** [T06, p. 29]:
  $$\mathbf F_{Gi}=\sum_{j\neq i}\big[(-\varepsilon_{ij}k_n)\mathbf e^n_{ij}+(v^t_{ij}\varepsilon_{ij}k_t)\mathbf e^t_{ij}\big]g(\varepsilon_{ij}),\qquad \varepsilon_{ij}=r_{ij}-(R_i+R_j).$$
- **Social** [T06, p. 30]: $\mathbf F_{Si}=\sum_{j\neq i}A\exp(-\varepsilon_{ij}/B)\,\mathbf e^n_{ij}$.
- **Autopropulsión** hacia el target [T06, p. 31]: $\mathbf F_{Di}=m_i(v_{di}\mathbf e^{\rm target}_i-\mathbf v_i)/\tau_i$.

En el artículo original, con $d_{ij}=|\mathbf r_i-\mathbf r_j|$, $r_{ij}=r_i+r_j$ y $\mathbf n_{ij}$ de $j$ hacia $i$ [B26, p. 1] [B26, p. 2]:

$$\mathbf f_{ij}=\left\{A\,e^{(r_{ij}-d_{ij})/B}+k\,g(r_{ij}-d_{ij})\right\}\mathbf n_{ij}+\kappa\,g(r_{ij}-d_{ij})\,\Delta v^t_{ji}\,\mathbf t_{ij}.$$

- $g(x)=x$ si hay contacto y 0 si no.
- $\mathbf t_{ij}=(-n^2_{ij},n^1_{ij})$ y $\Delta v^t_{ji}=(\mathbf v_j-\mathbf v_i)\cdot\mathbf t_{ij}$.
- Las paredes tienen una expresión análoga, con fricción $-\kappa\,g\,(\mathbf v_i\cdot\mathbf t_{iW})\mathbf t_{iW}$ [B26, p. 2].

En la lámina, $\varepsilon<0$ indica contacto y $g$ no está definida. Ver [dudas](../dudas-y-conflictos.md).

**Parámetros.** La teórica usa un ejemplo de evacuación [T06, p. 33]:

- 200 peatones en una habitación de 20×20 m, con diámetros de 0,50 a 0,58 m y una puerta de 1,2 m.
- $v_d$ entre 0,8 y 6 m/s.
- $A=2000$ N, $B=0{,}08$ m, $k_n=1{,}2\times10^5$ N/m, $k_t=2{,}4\times10^5$ kg/(m·s) y $\tau=0{,}5$ s.

El artículo usa los mismos $A$, $B$, $k$, $\kappa$ y $\tau$, con $m=80$ kg y diámetros uniformes entre 0,5 y 0,7 m. Su habitación es de 15×15 m, con una puerta de 1 m. No especifica integrador ni paso temporal [B26, p. 2].

**Fenómenos que reproduce cualitativamente:**

- Formación de carriles.
- Oscilaciones en cuellos de botella.
- Ineficiencia en ensanchamientos [T06, p. 32].
- El efecto FIS [T06, p. 33].

**Sin fuerza social** (variante del TP5) quedan la autopropulsión y el contacto, con $m$, $\tau$, $k_n$, $k_t$ y el radio como parámetros. Desaparecen $A$ y $B$. **Inferencia:** sin contacto, cada agente solo relaja exponencialmente hacia $v_d\mathbf e^{\rm target}$, con escala $\tau$. No hay interacción a distancia y por eso el modelo no anticipa colisiones, como dice la consigna [TP05, p. 2]. El paso temporal se elige como en [medios granulares](medios-granulares.md#paso-temporal-y-salida) y se valida con un test de convergencia, porque el artículo no lo da.

### Autómata celular *bionics-inspired*

Es el modelo de Kirchner y Schadschneider (2002). El espacio se divide en celdas, cada una vacía u ocupada por una partícula, y en cada paso cada partícula puede moverse con cierta probabilidad a una celda vecina libre [T06, p. 36]. Las probabilidades dependen de dos *floor fields* [T06, p. 37]:

- **Campo estático $S$:** depende solo de la geometría, queda fijo durante la simulación y crece hacia la puerta según la distancia más corta [T06, p. 38].
- **Campo dinámico $D$:** es un rastro virtual que dejan las partículas al pasar. Arranca en $D_{ij}=0$ y suma 1 cada vez que una partícula sale de una celda. En cada paso decae con probabilidad $\delta$ y se difunde con probabilidad $\alpha$ hacia una celda vecina [T06, p. 39] [T06, p. 40].

$$p_{ij}=N\exp(k_DD_{ij})\exp(k_SS_{ij})(1-n_{ij})\,\xi_{ij},$$

- $n_{ij}\in\{0,1\}$: ocupación.
- $\xi_{ij}=0$ en celdas prohibidas (paredes).
- $k_S$, $k_D$: sensibilidades.
- $N$: normaliza.

Fórmula según [T06, p. 41].

Las reglas se aplican a todas las partículas a la vez (actualización paralela) [T06, p. 41] [T06, p. 42]:

1. Actualizar $D$.
2. Calcular $p_{ij}$.
3. Cada partícula elige su destino.
4. Los conflictos entre partículas que eligen la misma celda se resuelven al azar.
5. Las partículas que se mueven incrementan $D$.

La teórica muestra un proceso típico de evacuación [T06, p. 43].

### Contractile Particle Model

El CPM (Baglietto y Parisi, 2011) es un autómata en espacio continuo. Las posiciones y velocidades son continuas, pero no se calculan fuerzas [B28, p. 2]. Cada partícula tiene un radio variable entre $r_{\min}$ (máxima compresión) y $r_{\max}$ (espacio personal para desplazarse). La rapidez deseada depende del radio [T06, p. 45] [B28, p. 2]:

$$v_d=v_d^{\max}\left[\frac{r-r_{\min}}{r_{\max}-r_{\min}}\right]^\beta,\qquad \mathbf v_d=v_d\,\mathbf e_{\rm target},\qquad \mathbf e_{\rm target}=\frac{\mathbf x_{\rm target}-\mathbf x}{|\mathbf x_{\rm target}-\mathbf x|}.$$

**Sin contacto** [T06, p. 49] [T06, p. 50]:

$$\mathbf x(t+\Delta t)=\mathbf x(t)+\mathbf v_d\Delta t,\qquad r(t+\Delta t)=r(t)+\frac{r_{\max}}{\tau/\Delta t}\ \text{(si }r<r_{\max}).$$

**Con contacto:** el radio colapsa a $r_{\min}$ y, durante ese paso, la partícula se mueve con una velocidad de escape [T06, p. 48] [T06, p. 51]:

$$\mathbf x(t+\Delta t)=\mathbf x(t)+\mathbf v_e\Delta t,\qquad |\mathbf v_e|=v_e=v_d^{\max}.$$

- **Dirección de escape:** suma de los versores que se alejan de cada contacto, $\mathbf v_e=v_e\sum_j\mathbf e^{ij}/|\sum_j\mathbf e^{ij}|$, con $\mathbf e^{ij}=(\mathbf x^i-\mathbf x^j)/|\mathbf x^i-\mathbf x^j|$. Para una pared, $\mathbf x^j$ es el punto de la pared más cercano [B28, p. 2]. Elegir $v_e=v_d^{\max}$ corresponde a la ec. (9) [B28, p. 3].
- **Paso temporal:** el modelo lo fija como $\Delta t=r_{\min}/[2\max(v_d^{\max},v_e)]$ [B28, p. 2]. **Inferencia:** así nadie avanza más de $r_{\min}/2$ por paso. Por eso el TP5 dice que el $dt$ es parte de las reglas [TP05, p. 1].
- **$\tau=0{,}5$ s:** es el tiempo para recuperar el radio máximo, tomado del SFM [B28, p. 2].
- **Algoritmo por paso** [B28, p. 3] [T06, p. 53]:
  1. Detectar contactos y calcular $\mathbf v_e$.
  2. Ajustar radios.
  3. Calcular dirección y módulo de $\mathbf v_d$.
  4. Usar $\mathbf v=\mathbf v_d$ si $r>r_{\min}$ o $\mathbf v_e$ si $r=r_{\min}$, y actualizar posiciones.
- **Parámetros libres:** $r_{\min}$, $r_{\max}$ y $\beta$; $v_d^{\max}$ es la velocidad libre [B28, p. 3]. Con una pista circular y distinto número de partículas se construye el diagrama fundamental [T06, p. 53]. Dos ajustes con $\beta=0{,}9$ [T06, p. 54] [T06, p. 55] [B28, p. 4]:
  - $v_d^{\max}=1{,}55$ m/s, $r_{\min}=0{,}15$ m, $r_{\max}=0{,}32$ m.
  - $v_d^{\max}=0{,}95$ m/s, $r_{\min}=0{,}10$ m, $r_{\max}=0{,}37$ m.
- **Bondades:** reproduce caudal específico y diagrama fundamental, y es unas 50 veces más rápido que el SFM [T06, p. 52] [T06, p. 56].
- **Evacuación en el paper:** el target de cada agente está dentro del 60 % central de la puerta y, al cruzarla, se reemplaza por uno exterior [B28, p. 4].

El target deseado puede ser único, una lista, o dinámico: una función de las posiciones y velocidades de vecinos y obstáculos [T06, p. 57]. El CPM no ubica targets por sí mismo; eso queda para algoritmos de nivel superior, como la elusión [B28, p. 2].

**Inferencia para el TP5:** con $r_{\min}=0{,}10$ m y $v_e=v_d^{\max}$, la ec. (2) da $\Delta t\approx0{,}033$ s para $v_d=1{,}5$ m/s. Los papers posteriores del mismo grupo no siempre usan esa ecuación: B32 toma $\Delta t=1/33$ s para coincidir con su captura de movimiento [B32, p. 4].

## Elusión de colisiones

SFM, el autómata y CPM son modelos del **nivel operativo**. La lámina ubica los mecanismos de elusión entre el nivel táctico y el operativo [T07, p. 37]. La idea común de la teórica es un **“goal temporario”** que varía en el tiempo según las posiciones y velocidades de otros agentes: una capa de elusión reactiva sobre un modelo operacional [T07, p. 16] [T07, p. 17].

### Elusión predictiva (Karamouzas et al., 2009)

Un ejemplo es $m_i\mathbf a_i=\mathbf F_g+\mathbf F_e$, con fuerza al objetivo y fuerza evasiva [T07, p. 5]. El objetivo atrae con $\mathbf F_g=(u^{\rm pref}\mathbf n_g-\mathbf v)/\tau$ [T07, p. 6] [B29, p. 4].

- **Espacio personal:** cada peatón tiene un disco de radio $\rho_i>r_i$. Habrá colisión si existe $t_c\ge0$ tal que $d_{ij}\le\rho_i+r_j$ [T07, p. 7] [B29, p. 4].
- **Predicción** [T07, p. 9] [B29, p. 5]:
  - Velocidad deseada hipotética: $\mathbf v_i^{des}=\mathbf v_i+\mathbf F_g\Delta t$.
  - Extrapolación lineal: $\mathbf x_i'=\mathbf x_i+t\mathbf v_i^{des}$ y $\mathbf x_j'=\mathbf x_j+t\mathbf v_j$, solo para los vecinos visibles.
  - Se resuelve la cuadrática del encuentro, la misma que en la [simulación por eventos](eventos-y-tp3.md#predicción-de-colisiones). Solo cuenta si $t_c\le t_\alpha$, el tiempo de anticipación.
- **Selección:** se toman los vecinos con menor $t_c$, cinco según la teórica y entre 2 y 5 según el paper [T07, p. 10] [B29, p. 6].
- **Maniobra** [T07, p. 11] [B29, p. 6] [B29, p. 7]:
  - Con las posiciones al instante de choque, $\mathbf c_i=\mathbf x_i+t_c\mathbf v_i^{des}$ y $\mathbf c_j=\mathbf x_j+t_c\mathbf v_j$, la fuerza evasiva apunta de $\mathbf c_j$ a $\mathbf c_i$.
  - Su módulo es una función por tramos $f(D)$, con $D=\|\mathbf c_i-\mathbf x_i\|+(\|\mathbf c_i-\mathbf c_j\|-r_i-r_j)$ y umbrales $d_{\min}$, $d_{\rm mid}$ y $d_{\max}$.
- **Combinación:** las fuerzas se suman ponderadas según la inminencia del choque, o se procesan en secuencia, empezando por la más inminente [T07, p. 12].
- **Comparación con el SFM:** en un pasillo con 100 agentes, el modelo predictivo da trayectorias más cortas, rápidas y suaves [T07, p. 13] [T07, p. 14] [B29, p. 10].
- **Limitaciones:** el paper no informa valores numéricos de sus parámetros y no se calibra con datos reales [B29, p. 11].

### Heurística cognitiva (Moussaïd, Helbing y Theraulaz, 2011)

Usa peatones circulares con radio, masa, posición y velocidad, como el SFM [T07, p. 19]. En vez de repulsiones, cada peatón “mira” su campo visual:

- **Campo visual:** para cada dirección $\alpha\in[-\phi,\phi]$ calcula $f(\alpha)$, la distancia hasta la primera colisión si caminara a $v^0$. Tiene en cuenta las velocidades de los demás y las oclusiones. Si no hay colisión, $f(\alpha)=d_{\max}$ [T07, p. 20] [B27, p. 2].
- **Primera heurística (dirección):** elegir $\alpha_{des}$ que minimice $d(\alpha)=d_{\max}^2+f(\alpha)^2-2d_{\max}f(\alpha)\cos(\alpha_0-\alpha)$, con $\alpha_0$ la dirección del destino. Es un compromiso entre ir libre de choques y desviarse lo menos posible [T07, p. 21] [B27, p. 2].
- **Segunda heurística (rapidez):** mantener un tiempo a colisión de al menos $\tau$, es decir $v_{des}=\min(v^0,d_h/\tau)$, con $d_h$ la distancia al primer obstáculo en la dirección elegida [T07, p. 22] [B27, p. 2].
- **Dinámica:** $d\mathbf v_i/dt=(\mathbf v_{des}-\mathbf v_i)/\tau$, más fuerzas de contacto solo cuando hay contacto físico [T07, p. 23] [T07, p. 24].
- **Parámetros** para trayectorias individuales: $\tau=0{,}5$ s, $\phi=75°$, $d_{\max}=10$ m y $v^0=1{,}3$ m/s [B27, p. 3].
- **Datos de comparación:** trayectorias medias en un corredor de 7,88×1,75 m, esquivando a una persona quieta (148 repeticiones) y a otra que viene de frente (123) [T07, p. 25] [B27, p. 3] [B27, p. 5].
- **Otros resultados:** el modelo reproduce el diagrama fundamental y la turbulencia de multitudes, y se aplicó al desastre de la Love Parade (Duisburgo, 2010) [T07, p. 25] [T07, p. 26] [B27, p. 4].

### Elusión por huecos (Wang et al., 2015)

Quita la fuerza social repulsiva y elude cambiando la dirección y la rapidez deseadas [B30, p. 1] [B30, p. 2]:

- **Percepción:** campo visual de 180°, con los huecos entre vecinos dentro de un radio de percepción.
- **Rapidez:** depende del ancho del hueco y se limita prediciendo el choque con un horizonte $\tau$.
- **Dirección:** se elige el hueco que maximiza el avance hacia la meta [B30, p. 3] [B30, p. 4] [B30, p. 5].
- **Validación:** diagrama fundamental, caudales por puertas de 0,8 a 1,6 m y trayectorias individuales [B30, p. 6] [B30, p. 7] [B30, p. 8].

La teórica lo lista entre los modelos de elusión [T07, p. 37].

### CPM con elusión

La teórica modifica el CPM sumando a la dirección del target un término de elusión del vecino visible más cercano [T07, p. 28] [T07, p. 29]:

$$\mathbf n_c^i=\mathbf e^{ij}A_p\,e^{-d_{ij}/B_p}\cos\theta_j,\qquad
\mathbf e_a^i=\frac{\mathbf n_c+\mathbf e_t^i}{|\mathbf n_c+\mathbf e_t^i|},\qquad
\mathbf v_d=v_d\,\mathbf e_a^i.$$

- $\theta_j$: ángulo entre la dirección al target y la del vecino.
- Solo se aplica sin contacto.

La lámina corta la fórmula después de $\cos\theta_j$ [T07, p. 28].

Dos papers desarrollan esta familia:

- **Juego humano–zombi** [B31, p. 2] [B31, p. 3]:
  - Sobre el CPM, reemplaza el target fijo por uno dinámico solo cuando no hay contacto.
  - El target de un humano es la suma de términos $\mathbf e^{ij}A\,e^{-d_{ij}/B}$ de zombis, otros humanos y paredes. Es reactivo, no predictivo.
  - El paper afirma que la capa sirve para cualquier modelo con velocidad deseada [B31, p. 1].
  - No usa datos experimentales: es un juego matemático [B31, p. 2].
- **AA-CPM** (Martin y Parisi, 2024):
  - Agrega anisotropía (solo cuentan los contactos frontales) y **maniobras evasivas mediante cambios de la velocidad deseada, usando targets temporales y dinámicos** [B32, p. 3].
  - Para cada vecino al frente compara la velocidad relativa con la dirección al target. Si el vecino se aleja, no lo esquiva. Si no, rota el versor de separación según el ángulo de aproximación y lo pesa con $A_pe^{-d_{ij}/B_p}$ [B32, p. 4].
  - **Calibración:** con trayectorias experimentales de pares que se cruzan, inicializadas con la posición y velocidad experimentales y con el target en el último punto, obtiene $A_p=1{,}1$ y $B_p=2{,}1$ con error $E=0{,}24$ m [B32, p. 4] [B32, p. 5].
  - Su métrica promedia, para cada punto simulado, la distancia al punto experimental más cercano [B32, p. 4].

### Comparación

| Mecanismo | Qué modifica | Detección | Parámetros principales |
|---|---|---|---|
| Elusión predictiva | Agrega una fuerza evasiva | Tiempo a colisión con espacio personal y $t_\alpha$ | $\rho$, $t_\alpha$, $N$, $d_{\min}$, $d_{\rm mid}$, $d_{\max}$ (sin valores) [B29, p. 5] |
| Heurística cognitiva | Dirección y rapidez deseadas | Distancia a colisión en el campo visual | $\phi$, $d_{\max}$, $\tau$ [B27, p. 3] |
| Huecos (Wang) | Dirección y rapidez deseadas | Huecos en 180° y choque a horizonte $\tau$ | radio de percepción, $\tau$, territorio [B30, p. 6] |
| Humano–zombi | Target dinámico | Distancia actual (no predictiva) | $A$, $B$ por especie [B31, p. 3] |
| AA-CPM | Target temporal | Velocidad relativa y geometría frontal | $A_p$, $B_p$ calibrados [B32, p. 5] |

Cómo se aplican estas ideas a la consigna está en [Elusión, evacuación y TP5](elusion-evacuacion-y-tp5.md#material-de-apoyo-para-diseñar-la-capa).

## Simulación guiada por datos

En lugar de proponer un modelo, se busca en los datos experimentales el estado más parecido al de la simulación [T07, p. 31] [T07, p. 32]:

1. El estado del agente se describe con posiciones y velocidades relativas y el target final.
2. Se busca en los datos el estado más similar.
3. Se mira cuál fue la posición siguiente en los datos.
4. Se interpola y se mueve al agente.

El esquema de Martín y Parisi (2020) usa dos redes neuronales de regresión generalizada (GRNN): una para la rapidez y otra para el ángulo de la velocidad siguiente [T07, p. 33].

Ventajas que da la teórica [T07, p. 34]:

- Simulaciones validadas experimentalmente por definición.
- Camino directo de los datos a la simulación.
- Relevancia creciente con la inteligencia artificial.
- Un paso temporal mayor que el de los modelos de fuerzas.

## Software y aplicaciones

La navegación peatonal tiene tres niveles [T07, p. 36]:

- **Estratégico:** elección y programa de actividades.
- **Táctico:** elección del área de actividad y del camino.
- **Operativo:** desplazamiento e interacción con otros agentes, según la geometría y los obstáculos.

Un simulador se valida con caudales y diagrama fundamental en condiciones normales [T07, p. 38]. Sus entradas son la geometría, la demanda, los servidores y tiempos de proceso, la matriz origen–destino y el plan de evacuación [T07, p. 39].

Ejemplos de aplicación:

- Filas simples [T07, p. 42].
- Cambios de *layout* [T07, p. 43].
- Secuencias de evacuación de edificios [T07, p. 44] [T07, p. 45] [T07, p. 46].
- Distancia social en un supermercado según la ocupación permitida [T07, p. 47] [T07, p. 51] [T07, p. 52].

Simular permite evaluar cambios operativos o geométricos sin intervenir la infraestructura real, y obtener trayectorias de cada peatón para calcular indicadores [T07, p. 53]. La teórica lista códigos genéricos (VisWalk, Legion, MassMotion, PedSim, Vadere) y de evacuación (Pathfinder, Exodus, PedGo) [T07, p. 56] [T07, p. 57].

Relación con temas previos: el SFM ya se presentó como ejemplo de [muchas partículas](sistemas-de-muchas-particulas.md#dos-familias-de-modelos), y su término de contacto es el de [medios granulares](medios-granulares.md#leyes-de-fuerza).
