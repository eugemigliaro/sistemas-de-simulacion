# Derivado manual de B21

Fuente original: `material/externo/bibliografia-5/DrivenGranularGases.pdf`.
Stefan Luding (TU Delft; ICA1, Stuttgart), Raffaele Cafiero (PMMH, ESPCI, París) y Hans J. Herrmann (ICA1, Stuttgart), «Driven Granular Gases». Es un PDF de 23 páginas, tamaño carta, generado con Ghostscript 6.52. Tiene formato de capítulo («1 Driven Granular Gases», con secciones numeradas 1.x), pero el archivo no indica el libro ni el año; la referencia más reciente es de 2002.

La capa de texto del PDF es ilegible porque las fuentes están mal codificadas, así que `B21.txt` no sirve. Este derivado se armó mirando las páginas renderizadas y no reemplaza al original. Las citas usan la página del archivo PDF, que coincide con la numeración impresa.

Inspección visual: se miraron las páginas 1–23 completas a 100 dpi. Las páginas 5–9 y 15–20 se miraron además a 150 dpi, recortadas a la caja de texto, y las ecs. 1.18–1.19 de p. 15 a 300 dpi.

Relación con B20: las secciones §1.2–§1.5 de B21 reproducen casi palabra por palabra las §4–§5 de B20, con la numeración de ecuaciones cambiada. B21 no incluye el algoritmo dirigido por eventos (ED), el modelo TC, el tensor de tensiones, el enfriamiento libre ni la transición micro-macro de B20. A cambio, agrega un estudio analítico y numérico de la distribución de velocidades (§1.6).

## Contenido por página

| Página | Sección | Contenido |
|---|---|---|
| 1 | Título, resumen, §1.1 | Gas granular 2D de esferas inelásticas y rugosas con forzado. Puede forzarse la traslación, de forma proporcional a $|v(\boldsymbol x)|^\delta$, o la rotación, al azar. Con $\delta=1$ se reproducen observaciones experimentales que el forzado homogéneo ($\delta=0$) no reproduce. Con $\delta<0$ el sistema se homogeneiza aun con disipación fuerte. El forzado rotacional aleatoriza el sistema e impide los clusters. PACS 45.70, 47.50+d, 51.10.+y, 47.11.+j. |
| 2 | §1.1 | *Clustering*, que no hay que confundir con el colapso inelástico (divergencia de la frecuencia de colisiones del modelo de esfera dura). Tipos de forzado: paredes móviles o fuente homogénea aleatoria; en los experimentos 2D vibrados la energía horizontal entra indirectamente. Modelo de esfera dura inelástica (IHS) con forzado multiplicativo proporcional a $|v(\boldsymbol x)|^\delta$, que incluye como caso particular el homogéneo $\delta=0$. Con $\delta>0$ las partículas lentas, por ejemplo las de un cluster, reciben poca energía. |
| 3 | §1.1 (cont.), §1.2 | Con $\delta=1$: el *clustering* empieza antes, los clusters son estables y conviven con un gas, y las distribuciones de velocidad tienen exponentes distintos de $3/2$. Se propone forzar las rotaciones, por ejemplo con partículas magnéticas en un campo variable. Plan del trabajo. Nomenclatura: «estado estacionario» significa estado estacionario fuera del equilibrio (NESS), y «equilibrio» significa que la energía que entra compensa la que se pierde. |
| 4 | Fig. 1.1, §1.2, §1.2.1 | Fig. 1.1 (a–c): $N=11025$ partículas lisas ($r_t=-1$), $\delta=1$, $\nu=0.34$, $H_{dr}=1.0\,\mathrm{s^{-1}}$ y $r=0.999$, $0.97$, $0.6$. Fig. 1.1 (d): forzado rotacional con $N=11025$, $\nu=0.34$, $r_t=1$, $r=0.1$, $J=1.0\,\mathrm{s^{-1}}$. Modelo: $N$ esferas 3D de radio $a$ y masa $m$ con potencial de núcleo duro, confinadas a un plano de lado $L$ con condiciones periódicas. Variables: $\boldsymbol r_i$, $\boldsymbol v_i$ y $\boldsymbol\omega_i$. Restitución normal $r$ constante. |
| 5 | §1.2.1 (cont.), §1.2.2 | Reglas de colisión normal y tangencial, y forzado traslacional (ecs. 1.1–1.2). |
| 6 | §1.2.3, §1.3 | Forzado rotacional (ecs. 1.3–1.6). Ecuaciones de campo medio para $T_{tr}$ y $T_{rot}$ (ecs. 1.7–1.8), según Huthmann–Zippelius. |
| 7 | §1.3 (cont.), §1.3.1 | Ecs. 1.9–1.13. |
| 8 | §1.3.1 (cont.), §1.3.2, §1.3.3 | Ecs. 1.14–1.16. Tiempo de relajación. |
| 9 | §1.3.3 (cont.), §1.4–§1.4.2 | Detalles numéricos de la ED, iguales a B20 p. 8. Las figs. 1.2a–d comparan la ec. 1.13 con simulaciones para $r=0.99$, $0.995$, $0.997$ y $0.998$. |
| 10 | Fig. 1.2, §1.4.2 (cont.), §1.4.3 | Transitorio de $T(t)$: simulación contra campo medio. Los datos colapsan, lo que confirma que $t_{relax}$ no depende de la inelasticidad cuando $\delta=1$. Con $\delta<0$ el acuerdo se extiende a $r$ chicos. Con $\delta=-1$ el forzado es singular a baja velocidad. |
| 11 | Figs. 1.3–1.4, §1.4.4 | $T(t)/T^{eq}$ colapsado. $T^{eq}/T^{mf}$ en función de $r$ para $\delta=0$, $-0.25$, $-0.5$ (a) y para $\delta=1$, $0$ (b). Efecto del tamaño del sistema. |
| 12 | Fig. 1.5, §1.4.5, §1.5 | Tamaños $N=11025$ y $5476$ con $\delta=-0.25$. Clustering estacionario: el mismo texto de B20 p. 9. |
| 13 | Fig. 1.6, §1.5 (cont.) | $T_{rot}/T_{rot}^{mf}(r=0)$ y $R=T_{rot}/T_{tr}$ en función de $r$ ($N=11025$, $\nu=0.34$, $r_t=1$). El acuerdo con el campo medio es de alrededor del 10 % incluso con $r=10^{-4}$; con forzado traslacional la desviación ya es del 30–40 % en $r=0.6$. |
| 14 | Fig. 1.7, §1.5 (cont.) | $R$ en función de $r_t$ con $r=0.1$: buen acuerdo si $r_t>0$ y falla cuando $r_t\to-1$, porque el acoplamiento $1+r_t$ es débil. Muchos materiales cumplen $r_t\approx0.4$ (ref. 44). El forzado rotacional mantiene la homogeneidad: no favorece colisiones y genera corte entre partículas. |
| 15 | §1.6 | Estudio analítico de la distribución de velocidades: ecuación de Enskog–Boltzmann con un término de difusión de Fokker–Planck multiplicativo, ecuaciones de momentos y cola de alta velocidad (ecs. 1.17–1.23). |
| 16 | §1.6 (cont.), §1.6.1, §1.6.2 | Solución de cola $\tilde f(c)\propto\exp(-Bc^\alpha)$. Simulaciones con $\delta=1$ y $\nu=0.34$: unas $10^3$ corridas con $N=1089$ y unas 200 con $N=11025$. Ajuste $f_\alpha(v_x)$. Valores de $\alpha$ para $\delta=1$ y $\delta=0.5$. |
| 17 | Figs. 1.8–1.9 | $\alpha$ en función de $r$ para $\delta=1$ y $\delta=0.5$, con *insets* de $f(v_x)$. Pie de Fig. 1.8: $N=1089$, $r=0.9$, $f_0=7.6$, $B=18.9$, $\alpha=1.05(9)$. Pie de Fig. 1.9: $r=0.6$, $f_0=3.1$, $B=1.1$, $\alpha=1.12(5)$. Con $\delta=-0.25$ y $-0.5$ la distribución es casi gaussiana. |
| 18 | Fig. 1.10, texto | $\alpha(r)$ para $\delta=-0.25$ y $-0.5$ ($N=11025$). Con $r$ chico, $\delta=-0.5$, $-0.25$ y $0.5$ dan $\alpha=1.99(3)$, $1.77(3)$ y $1.08(3)$; la teoría de cola predice $2.0$, $7/4$ y $1$. Con $\delta=-0.5$ la distribución es gaussiana pero no maxwelliana: su varianza es anómala. |
| 19 | §1.6.2 (cont.), §1.6.3, §1.7 | Argumento heurístico: cuando hay inhomogeneidades, el forzado depende de la velocidad térmica local $v_0(\boldsymbol x)$ y de la densidad local $n(\boldsymbol x)$, y la realimentación entre forzado y disipación vuelve no universal a $f(v)$. Con forzado rotacional y $r=0.1$ se ajusta $f(x)=A\exp(-B|(x-\langle x\rangle)/\sigma|^\alpha)$: $\alpha=1.92(6)$ para $\omega$ y $\alpha=1.41(6)$ para $v$, cerca del $3/2$ teórico (ref. 31). Resumen. |
| 20 | Fig. 1.11, §1.7 (cont.) | $P(\omega)$ y $P(v_x)$ con $N=11025$, $\nu=0.34$, $r_t=1.0$, $r=0.1$, comparadas con una maxwelliana. Prueba experimental propuesta: $T^{mf}\propto[\nu g(\nu)]^{-2/(3-2\delta)}$. Tanto el forzado rotacional como $\delta<0$ mantienen la homogeneidad si $r_t>0$. |
| 21 | §1.7 (cont.), Agradecimientos, Referencias 1–4 | Las desviaciones respecto de la maxwelliana no están necesariamente ligadas al *clustering*. Experimento propuesto: esferas muy rugosas con una pequeña barra magnética y pulsos magnéticos homogéneos y periódicos sobre un plano liso. |
| 22–23 | Referencias 5–45 | Ref. 31: van Noije y Ernst, «Velocity distributions in homogeneously cooling and heated granular fluids», *Granular Matter* 1(2):57–64, 1998. Ref. 40: van Noije y Ernst, «Ring kinetic theory for an idealized granular gas», *Physica A* 251:266–283, 1998. |

## Transcripción de relaciones verificadas visualmente

Notación del original: $r$ es la restitución normal, $r_t$ la restitución tangencial y $a$ el radio. En 2D, $\nu=\pi a^2N/V$.

- p. 5, colisión:
  - $\boldsymbol v_c'^{(n)}=-r\,\boldsymbol v_c^{(n)}$, con cambio de momento de la partícula $i$ igual a $-(m/2)(1+r)\boldsymbol v_c^{(n)}$.
  - $\boldsymbol v_c^{(n)}=[(\boldsymbol v_i-\boldsymbol v_j)\cdot\boldsymbol n]\boldsymbol n$, con $\boldsymbol n=(\boldsymbol r_i-\boldsymbol r_j)/|\boldsymbol r_i-\boldsymbol r_j|$.
  - Tangencial: $\boldsymbol v_c'^{(t)}=-r_t\,\boldsymbol v_c^{(t)}$.
  - Disipación $\propto1-r^2$ (normal) y $\propto1-r_t^2$ (tangencial); acoplamiento $\propto1+r_t$. $r\in[0,1]$; $r_t\in[-1,+1]$, de liso a rugoso.
  - No se define explícitamente $\boldsymbol v_c^{(t)}$.
- p. 5, forzado traslacional cada $\Delta t=f_{dr}^{-1}$:
  - (1.1) $v_i'^{x}(t)=v_i^x(t)+r_i^x|\boldsymbol v_i(t)|^\delta v_r^{1-\delta}$, y lo mismo en $y$.
  - $v_r=1\,\mathrm{m\,s^{-1}}$, $T=E/(NT_r)$, $E=(m/2)\sum\boldsymbol v_i^2$ y $T_r=mv_r^2$. La varianza de las gaussianas $r_i^{x,y}$ es $T_{dr}$.
  - (1.2) $\Delta T/\Delta t=H_{dr}T^\delta$, con $H_{dr}=f_{dr}T_{dr}$.
  - Se usa $f_{dr}\sim100\,\mathrm{s^{-1}}$, del orden de los experimentos, y no $f_{dr}\gg t_n^{-1}$.
- p. 6, forzado rotacional:
  - (1.3) $\omega_i'(t)=\omega_i(t)+r_i^\omega\omega_0$.
  - (1.4) $T_{tr}=E_{tr}/(NT_0)$ y (1.5) $T_{rot}=2E_{rot}/(NT_0)$, con $E_{rot}=(qma^2/2)\sum\omega_i^2$, $q=2/5$, $T_0=mv_0^2$ y $v_0=a\omega_0$.
  - (1.6) $\Delta T_{rot}/\Delta t=J_{dr}$, con $J_{dr}=f_{dr}T_{dr}^\omega$.
- pp. 6–7, campo medio:
  - (1.7) $\frac d{dt}T_{tr}=G[-AT_{tr}^{3/2}+BT_{tr}^{1/2}T_{rot}]+H_{dr}T^\delta$.
  - (1.8) $\frac d{dt}T_{rot}=2G[BT_{tr}^{3/2}-CT_{tr}^{1/2}T_{rot}]+J_{dr}$.
  - (1.9) $G=8\nu g_{2a}(\nu)/(a\sqrt{\pi m})$, con $g_{2a}(\nu)=(1-7\nu/16)/(1-\nu)^2$.
  - (1.10) $A=(1-r^2)/4+\eta(1-\eta)/2$ y $B=\eta^2/(2q)$.
  - (1.11) $C=\eta(1-\eta/q)/(2q)$, con $\eta=q(1+r_t)/(2q+2)$.
- p. 7, partículas lisas:
  - (1.12) $\frac d{dt}T=-G_rAT^{3/2}+H_{dr}T^\delta$, con $G_r=8an\sqrt{\pi T_r/m}\,g(\nu)$ y $A=(1-r^2)/4$.
  - (1.13) $T^{mf}=(H_{dr}/(G_rA))^{2/(3-2\delta)}$, que generaliza la solución de Enskog. El exponente vale $2/3$ si $\delta=0$ y $2$ si $\delta=1$. Para $\delta\ge3/2$ no hay equilibrio estable, y $\delta=3/2$ es inestable frente a fluctuaciones de densidad.
- p. 8, relajación y partículas rugosas:
  - (1.14) $T^{mf}-T(t+t_0)=T(t_0)\exp\{-[3At_n^{-1}+\delta H_{dr}(T^{mf})^{\delta-1}]t\}$, con $t_n^{-1}=G_r\sqrt{T^{mf}}/2$ (frecuencia de Enskog).
  - Para $\delta=1$: $t_{relax}^{-1}=(5/2)H_{dr}$, que no depende de $A$.
  - (1.15) Forzado traslacional ($J_{dr}=0$, $\delta=0$): $T_{rot}^{mf}=(H_{dr}/(G\Gamma_{tr}))^{2/3}$ y $T_{tr}^{mf}=T_{rot}^{mf}/R$, con $\Gamma_{tr}=(C/B^3)^{1/2}(CA-B^2)$ y $R=B/C$.
  - (1.16) Forzado rotacional ($H_{dr}=0$): $T_{rot}^{mf}=(J_{dr}/(G\Gamma_{rot}))^{2/3}$ y $T_{tr}^{mf}=T_{rot}^{mf}/R$, con $\Gamma_{rot}=2(B/A^3)^{1/2}(CA-B^2)$ (p. 9) y $R=A/B$.
- p. 9, parámetros:
  - $\nu=0.34$; $N=1089$ ($f_{dr}=133\,\mathrm{s^{-1}}$) o $N=11025$ ($f_{dr}=67\,\mathrm{s^{-1}}$); $a=10^{-3}\,\mathrm m$; $H_{dr}=1.0\,\mathrm{s^{-1}}$.
  - $G_r=8\nu v_rg(\nu)/(\sqrt\pi a)=3.1\times10^3\,\mathrm{s^{-1}}$, $T^{mf}=0.0358$ y $t_n^{-1}=2.9\times10^2\,\mathrm{s^{-1}}$ para $r=0.90$.
  - Antes de encender la disipación y el forzado, el sistema se equilibra de forma elástica ($r=1$, $r_t=-1$) hasta llegar a una maxwelliana.
- p. 15, distribución de velocidades:
  - (1.17) $\partial_tf(\boldsymbol v_1,t)=g(2a)I(f,f)+\frac{H_{dr}}{2m}\frac{\partial^2}{\partial\boldsymbol v_1^2}[v_1^{2\delta}f(\boldsymbol v_1,t)]$.
  - Escalamiento: $f(v)=(n/v_0^2)\tilde f(c)$, con $c=v/v_0$.
  - (1.18) $\frac{H_{dr}}{2v_0^3g(\nu)na}p^2\langle c^{p-2+2\delta}\rangle=\mu_p$.
  - (1.19) Para $\delta=1$, $p=2$ y $d=2$: $\frac{H_{dr}^{1-\delta}}{2v_0^3g(\nu)na}2\langle c^2\rangle=\mu_2$. El exponente $1-\delta$ sobre $H_{dr}$ está impreso así (verificado a 300 dpi), aunque con $\delta=1$ no concuerda con (1.18) ni con (1.20).
  - (1.20) $v_0=H_{dr}/(g(\nu)\mu_2an)$.
  - (1.21) $\langle c^{2\delta}\rangle=[\langle c^2\rangle]^\delta=v_0^{2\delta}$, supuesto sin justificación salvo para $\delta=0$ y $\delta=1$.
  - (1.22) $\tilde I(\tilde f,\tilde f)\approx-\beta_1c_1\tilde f(c_1)$, con $\beta_1=\pi^{1/2}$ en 2D.
  - (1.23) $-\beta_1c\tilde f(c)+\frac{\mu_2}{2d}\left(\frac{d^2}{dc^2}+\frac{d-1}{c}\frac{d}{dc}\right)[c^{2\delta}\tilde f(c)]=0$.
- p. 16, cola de la distribución:
  - $\tilde f(c)\propto\exp(-Bc^\alpha)$, con $\alpha=(3-2\delta)/2$ y $B=\frac2{3-2\delta}\sqrt{2d\beta_1/\mu_2}$.
  - Con $\delta=1$ da $\alpha=1/2$, frente a $\alpha=0.49(3)$ medido con $r$ bajo. Existe una velocidad de cruce $c^*$, que baja cuando baja $r$.
  - Ajuste: $f_\alpha(v_x)=f_0\exp(-B|v_x-\langle v_x\rangle|^\alpha)$.
  - Con $\delta=1$, $\alpha$ va de $0.49(3)$ a $1.99(3)$. Con $N=1089$ y $r=0.9$, $\alpha=1.05(4)$ (el pie de Fig. 1.8, p. 17, dice $1.05(9)$). Con $N=11025$ y $r=0.95$, $\alpha=1.02(3)$: una distribución casi exponencial, como en los experimentos con monocapas vibradas (refs. 13, 17, 18).
  - Con $\delta=0.5$, $\alpha$ va de $1.08(3)$ a $1.99(3)$. Para parecerse a los experimentos hace falta $r=0.6$, lejos del $r\sim0.9$ típico, así que $\delta=1$ es el que mejor ajusta.

## Limitaciones

- No se identificó la publicación de origen (libro o actas): el PDF no la indica.
- Las figuras se describen por su pie y por lo que se ve, no por valores leídos de los ejes.
- No se transcribieron las referencias completas.
