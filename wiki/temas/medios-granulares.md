# Medios granulares

## Definición y propiedades

Un medio granular es un sistema de muchas partículas macroscópicas: granos, pellets, arena o polvo. Interactúan por contacto, con fuerzas normales (deformación viscoelástica) y tangenciales (rozamiento). Las interacciones son muy disipativas: el sistema llega al reposo si no recibe energía externa (gravedad, vibración del recipiente) o propia (autopropulsión). Su comportamiento difiere del de sólidos, líquidos y gases; por ejemplo, la presión no depende de la altura de la columna [T05, p. 2].

### Silos y ley de Janssen

En el vaciado gravitatorio de un silo, el tipo de flujo (en masa o restringido, con zonas estancas) depende de la geometría y de las propiedades de paredes y material. Se distinguen cinco zonas: flujo en masa o pistón, transición, convergencia, caída libre y estancamiento [T05, p. 3].

La **ley de Janssen (1895)** dice que la presión crece asintóticamente con la profundidad $z$, medida desde la superficie libre:

$$P(z)\propto1-\exp\left(-\frac{4\mu_pKz}{D}\right),$$

con $\mu_p$ el coeficiente de fricción con la pared, $D$ el diámetro del contenedor y $K$ la constante de Janssen, que relaciona tensión radial y vertical ($\sigma_{rr}=K\sigma_{zz}$) [T05, p. 4].

### Ley de Beverloo

El caudal de descarga de un silo es constante e independiente de la altura de la columna [T05, p. 5]. La **ley de Beverloo (1961)** surge de análisis dimensional:

$$Q\approx n_p\sqrt g\,(d-cr)^{2{,}5}=B\,(d-cr)^{2{,}5}.$$

- $n_p$: partículas por unidad de volumen.
- $d$: diámetro de la apertura de salida.
- $r$: radio medio de las partículas.
- $c$: factor adimensional que descuenta la parte del orificio que no se usa.
- El exponente 2,5 vale en silos 3D; en 2D es 1,5.

Fórmula y rótulos verificados sobre la diapositiva [T05, p. 5].

## Simulación por elementos discretos

En sistemas densos el tiempo de choque es mucho mayor que el de vuelo ($t_{\rm choque}\gg t_{\rm vuelo}$). Por eso se usa el **método de elementos discretos (DEM)**: dinámica molecular para granulares, con contactos blandos que duran varios pasos. Un modelo pionero es el de Cundall y Strack (1979) [T05, p. 7]. Es la misma familia de métodos que el [paso temporal del cuarto práctico](paso-temporal-e-integradores.md); las colisiones instantáneas del [tercer práctico](eventos-y-tp3.md) son el límite opuesto.

### Ecuaciones de movimiento

Se integran, acopladas, traslaciones y rotaciones de las $N$ partículas [T05, p. 10]:

$$m_i\ddot{\mathbf r}_i=\sum_{j\in\text{contactos}}\mathbf F_{ij}+\mathbf F_g,\qquad
I_i\ddot\theta_i=\sum_{j\in\text{contactos}}M_{ij},\qquad \mathbf M=\mathbf R\times\mathbf F.$$

### Geometría del contacto

- Superposición entre partículas: $\xi_{ij}=R_i+R_j-|\mathbf r_j-\mathbf r_i|$, con contacto si $\xi_{ij}>0$. Velocidad relativa: $\dot{\mathbf r}_{\rm rel}=\dot{\mathbf r}_i-\dot{\mathbf r}_j$. La gravedad apunta en $-\hat y$ [T05, p. 8].
- Superposición con una pared: $\xi=R_i-|\mathbf r_{ip}|$, con $\mathbf r_{ip}$ el vector desde el centro de la partícula hasta la pared. Velocidad relativa: $\dot{\mathbf r}_i$ [T05, p. 9].
- Versores entre partículas: $\hat{\mathbf e}_n=(\mathbf r_j-\mathbf r_i)/|\mathbf r_j-\mathbf r_i|$, de $i$ hacia $j$; $\hat{\mathbf e}_t=(-e_{ny},e_{nx})$ [T05, p. 11].
- Versores de pared: constantes para cada pared y definidos por el ángulo $\alpha$ entre la normal y el eje $x$ [T05, p. 12].

### Leyes de fuerza

Opciones de la teórica, verificadas sobre el original [T05, p. 15]:

| Dirección | Opción | Expresión |
|---|---|---|
| Normal | N.1, resorte y amortiguador | $\mathbf F_N=[-k_n\xi-\gamma\dot\xi]\,\hat{\mathbf n}$ |
| Normal | N.2, resorte | $\mathbf F_N=-k_n\xi\,\hat{\mathbf n}$ |
| Tangencial | T.1, resorte limitado por Coulomb | $\mathbf F_T=\min\{-\mu\lvert\mathbf F_N\rvert\operatorname{sgn}(\dot{\mathbf r}_{\rm rel}\cdot\hat{\mathbf t})\,\hat{\mathbf t},\,-k_T\xi_T\,\hat{\mathbf t}\}$, con $\xi_T=\sum_t\Delta t\,\dot{\mathbf r}^c_{\rm rel}(t)$ |
| Tangencial | T.2, Coulomb | $\mathbf F_T=-\mu\lvert\mathbf F_N\rvert\operatorname{sgn}(\dot{\mathbf r}_{\rm rel}\cdot\hat{\mathbf t})\,\hat{\mathbf t}$ |
| Tangencial | T.3, viscosa proporcional a la superposición | $\mathbf F_T=-k_T\,\xi\,[\dot{\mathbf r}_{\rm rel}\cdot\hat{\mathbf t}]\,\hat{\mathbf t}$ |

En T.1, el mínimo se toma entre los módulos. $\xi_T$ es el desplazamiento tangencial acumulado durante el contacto; $\dot{\mathbf r}^c_{\rm rel}$ es la velocidad relativa de las superficies en el punto de contacto, que incluye las rotaciones [T05, p. 10] [T05, p. 15]. La lámina 14 dibuja el resorte con amortiguador normal y los elementos tangenciales [T05, p. 14].

Para sumar contribuciones conviene proyectar cada par $(F_N,F_T)$ en cartesianas [T05, p. 17] [T05, p. 18]:

$$F_x=F_Ne_{nx}-F_Te_{ny},\qquad F_y=F_Ne_{ny}+F_Te_{nx},$$
$$\mathbf F_i^{\rm Tot}=m_i\mathbf g+\sum_j\mathbf F_{N,ij}+\sum_j\mathbf F_{T,ij}.$$

**Inferencia de signos:** con $\hat{\mathbf n}$ de $i$ hacia $j$, $-k_n\xi\hat{\mathbf n}$ empuja a $i$ lejos de $j$ (repulsión), igual que en el [billar del cuarto práctico](billar-circular-y-tp4.md#sistema-2-modelo-y-estado). En T.3, la fuerza se opone al deslizamiento relativo de $i$ respecto de $j$.

### Paso temporal y salida

Como referencia, que depende del integrador [T05, p. 19]:

$$\Delta t\approx0{,}1\sqrt{m/k_n}.$$

Hay que distinguir el paso de integración $\Delta t$ del paso de guardado $\Delta t_2=k\,\Delta t$, con $k\in\mathbb N$. La lámina guarda el estado cuando $t/\Delta t_2=\operatorname{round}(t/\Delta t_2)$ [T05, p. 20]. Para medir caudales con la máxima precisión ($\Delta t$), se guarda la lista de tiempos de salida de cada partícula [T05, p. 21].

**Inferencia:** comparar `t/Δt2` con su redondeo en punto flotante es frágil, porque $t$ acumula errores de suma. Es más seguro contar pasos enteros y guardar cada $k$.

## Esferopolígonos

Un esferopolígono representa una partícula de forma arbitraria como la **suma de Minkowski** de un polígono y un disco, $P+Q=\{x+y\mid x\in P,\,y\in Q\}$: es lo que barre un conjunto arrastrado alrededor del perfil del otro [T05, p. 24]. El ejemplo es una “vaca de Minkowski”: un disco alrededor de un polígono de 62 lados, frente a 726 discos para representar lo mismo [T05, p. 24] [B23, p. 3]. El método es de Alonso-Marroquín [T05, p. 23].

La interacción suma contribuciones vértice–lado de un polígono contra el otro y viceversa [T05, p. 25] [T05, p. 26]:

$$\delta(V,E)=\langle r_i+r_j-d(V,E)\rangle,\qquad
\mathbf F_{ij}=-\mathbf F_{ji}=\sum_{V_i,E_j}\mathbf F(V_i,E_j)+\sum_{V_j,E_i}\mathbf F(V_j,E_i).$$

- $r_i$, $r_j$: radios de los discos.
- $d(V,E)$: distancia euclídea del vértice al segmento.
- $\langle x\rangle$: vale $x$ si $x>0$ y 0 en otro caso.

Fuerza con fricción [T05, p. 27]:

$$\mathbf F(V,E)=k_n\delta\,\mathbf N+k_t\delta_t\,\mathbf T.$$

Las partículas no son esféricas, así que hay que integrar rotaciones. El torque usa el punto medio de la superposición como punto de aplicación [T05, p. 28] [T05, p. 29]:

$$m_i\ddot{\mathbf r}_i=\sum_j\mathbf F_{ij}-m_ig\,\hat y,\qquad I_i\ddot\varphi_i=\sum_j\tau_{ij}.$$

La teórica cierra comparando la descarga de un silo 2D con discos y con vacas de Minkowski [T05, p. 30].

**Discrepancia de fuentes:** la lámina define el desplazamiento tangencial como $\delta_t=\delta\,[\dot{\mathbf r}_{\rm rel}\cdot\mathbf T]$, “como en la diapositiva 15” (opción T.3) [T05, p. 27]. El paper lo define como un desplazamiento elástico que cumple la condición de deslizamiento $|F_t|<\mu F_n$, con $k_n=10^7$ N/m, $k_t=0{,}1\,k_n$, $\mu=0{,}5$ y $\Delta t=10^{-5}$ s (opción T.1) [B23, p. 4]. Ver [dudas](../dudas-y-conflictos.md).

### Ampliación en la bibliografía de esferopolígonos

- **Eficiencia** [B23, p. 4] [B23, p. 6]:
  - Sin optimizar, la detección de contactos cuesta $O(N^2M^2)$, con $M$ vértices por partícula.
  - Con lista de vecinos (distancia de Verlet), lista de contactos vértice–lado y celdas, baja a $O(N)$. La integración usa un predictor-corrector de Gear.
  - Los discos simulan unas 50 veces más rápido que las vacas de Minkowski, y estas unas 40 veces más rápido que las vacas hechas de racimos de discos.
- **Validación** [B23, p. 5] [B23, p. 6]:
  - Sin fricción, la energía se conserva con error menor que 0,0001 %. Igual se transfiere momento angular, porque la fuerza no apunta al centro de masa.
  - En una tolva, las partículas no convexas se atascan con aberturas menores que 30 m.
- **Ajuste de formas reales** [B24, p. 3] [B24, p. 6]:
  - El paso estable escala como $\Delta t\propto\sqrt{m/k_n}$. Como $k_n$ crece al achicar el esferorradio $r$, el costo crece con el número de vértices y al bajar $r$.
  - Para guijarros o conchas, unos 6 vértices dan un error razonable; con 20 o más y $r$ chico el error baja a cerca de 1 %.
- **Tres dimensiones** [B25, p. 1] [B25, p. 2]:
  - Los esferopoliedros suman contactos arista–arista y vértice–cara. Sumar todos los pares evita las fuerzas discontinuas de un modelo de contacto único.
  - En una tolva sin fricción, las formas no convexas se atascan: la forma sola produce fricción macroscópica.

## Esferas duras inelásticas y gases granulares

Esta sección es bibliografía complementaria; la teórica trata los granulares con contactos blandos.

En el límite diluido, un medio granular se simula por eventos, como en el [tercer práctico](eventos-y-tp3.md), pero con choques inelásticos.

### Reglas de colisión

- **Restitución normal $r$:** $\mathbf v'_{1,2}=\mathbf v_{1,2}\mp(1+r)\mathbf v_n/2$, con $\mathbf v_n$ la componente normal de la velocidad relativa. Cada choque pierde $\Delta E=-m(1-r^2)v_n^2/4$ [B20, p. 2].
- **Restitución tangencial $r_t\in[-1,1]$:** va de partículas lisas a muy rugosas y acopla traslación y rotación [B20, p. 6].
- **Coulomb:** B22 da la regla rugosa completa, que distingue contacto pegado de deslizante [B22, p. 26] [B22, p. 27].

### Colapso inelástico

Con $r$ constante, unas pocas partículas pueden sufrir infinitas colisiones en tiempo finito. Es un artefacto del modelo de esfera dura [B20, p. 3]. Hay dos remedios:

- **Modelo TC:** reintroduce una duración de contacto $t_c$. Si una partícula vuelve a chocar antes de $t_c$, ese choque es elástico ($r=1$), y la tasa de disipación queda finita [B20, p. 3].
- **Restitución dependiente de la velocidad:** tiende a 1 para velocidades normales bajas, lo que también coincide con los experimentos [B22, p. 28].

### Algoritmo y observables

- **Algoritmo** [B20, p. 3]:
  - Cola de prioridad (*heap*) de eventos: $O(1)$ para el próximo y $O(\log N)$ para actualizar.
  - Actualización diferida de las dos partículas que chocan.
  - Celdas para buscar compañeros.
  - Costo total $O(N\log N)$.
- **Enfriamiento libre:** la energía sigue la ley de Haff, $E(\tau)=1/(1+\tau)^2$, hasta que aparecen *clusters* y el decaimiento se vuelve más lento [B20, p. 10] [B20, p. 11].
- **Tensor de tensiones:** se calcula con un término cinético y uno de colisiones; es un ejemplo de transición micro–macro sobre una grilla de celdas [B20, p. 4] [B20, p. 12].

### Forzado

- **Ruido homogéneo:** no forma *clusters* y deja una distribución casi maxwelliana, a diferencia de los experimentos [B21, p. 9].
- **Forzado $\propto|\mathbf v|^\delta$ con $\delta=1$:** forma *clusters* estables y colas de distribución casi exponenciales, más cercanas a lo observado [B21, p. 12] [B21, p. 16].
- **Ecuaciones de campo medio:** describen la evolución de las temperaturas traslacional y rotacional [B21, p. 6] [B21, p. 7].
- **Experimentos:** en mezclas binarias, cada especie mantiene su propia temperatura granular (no equipartición) [B22, p. 38] [B22, p. 41]. En el experimento 3D vibrado, la distribución de velocidades se ensancha con la densidad [B22, p. 69] [B22, p. 70].

La “temperatura granular” es una medida de la agitación, no una temperatura termodinámica. Su normalización cambia entre fuentes [B22, p. 22] [B22, p. 62]. Declarar siempre la definición usada.

Los derivados `B20-manual.md` y `B21-manual.md` reemplazan, para búsqueda, la capa de texto ilegible de esos PDF.
