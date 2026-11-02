# Derivado manual de B20

Fuente original: `material/externo/bibliografia-5/TehoryAndSimulationGranularMaterialsWithHardSpheres_StefanLuding.pdf`.
Stefan Luding, «Theory and simulation of granular materials with hard spheres». El PDF (14 páginas, A4, Ghostscript 5.50) no indica revista ni volumen; solo la fecha «06. Febuary 2003» y la afiliación del autor (TU Delft y Universidad de Stuttgart), en la página 1.

La capa de texto del PDF es ilegible porque las fuentes están mal codificadas, así que `B20.txt` no sirve. Este derivado se armó mirando las páginas renderizadas y no reemplaza al original. Las citas usan la página del archivo PDF, que acá coincide con la numeración impresa.

Inspección visual: se miraron las páginas 1–14 completas a 100 dpi. Las fórmulas centrales se verificaron a 170–200 dpi: página 4 (tensor de tensiones y ecuación de estado), página 5 (ecuación de estado densa y reglas de colisión normal), páginas 6–7 (forzado, ecuaciones de campo medio, completas a 170 dpi), página 8 (valores numéricos) y página 10 (ec. 25).

## Contenido por página

| Página | Sección | Contenido |
|---|---|---|
| 1 | Resumen, índice, §1, §1.1, §1.2 | Partículas que disipan energía y rotan por fricción. Algoritmo eficiente de dinámica molecular de esferas duras, transición micro-macro (tensor de tensiones) y gases granulares que se enfrían libremente o se calientan (traslación o rotación). *Clustering*: inestabilidad de densidad autoestabilizada; no confundirlo con el «colapso inelástico», que es la divergencia de la frecuencia de colisiones propia del modelo de esfera dura. Tipos de forzado: paredes móviles o fuente aleatoria homogénea. |
| 2 | §1.3, §1.4, §2, §2.1, §2.2 | Transición micro-macro: de simulaciones de una muestra pequeña se obtienen leyes macroscópicas, por ejemplo la presión en función de la densidad (ecuación de estado). Modelo de esfera dura y colisión instantánea, que habilitan la dinámica molecular dirigida por eventos (ED). Ecs. (1)–(2) más abajo. Arranca la técnica de esfera blanda dirigida por tiempo (*time-driven*). |
| 3 | §2.2–§2.4 | Esfera blanda: tres fuerzas (repulsión elástica proporcional al solapamiento, amortiguamiento viscoso normal proporcional a la velocidad relativa y fricción tangencial). Con resorte y amortiguador lineales, la duración de contacto $t_c$ y $r$ son constantes. Conexión entre esfera dura y blanda: colapso inelástico y modelo TC. Algoritmo ED con *double buffering* (estados «old» y «new»), actualización diferida, *heap* de tiempos de evento y *linked-cell*: costo total $O(N\log N)$; alrededor de $10^5$ partículas en una PC modesta. |
| 4 | §3, §3.1–§3.3, Fig. 1 | Tensor de tensiones: contribución cinética (gas ideal) más contribución de contactos, por desplazamiento virtual. Versión para esferas duras (ec. 6). Ecuación de estado 2D: $P$, $P_0$, $g_{2a}(\nu)$, $P_4$ y relación con la frecuencia de colisiones. Fig. 1: $P(\nu)$ en escala logarítmica, simulación contra $Q$, $Q_0$, $P_4$ y $P_{dense}$. |
| 5 | §3.3 (cont.), §4, §4.1, Fig. 2 | Para $\nu<0.65$ la simulación coincide con $P_0$. Cristalización en $\nu_c\approx0.7$. Divergencia en $\nu_{max}^{mono}=\pi/(2\sqrt3)$. Volumen libre $P_{fv}$, $P_{dense}$, ecuación de estado global $Q$ (ecs. 7–8). Modelo con fricción y forzado: $N$ esferas 3D confinadas a un plano 2D de lado $L$, con condiciones periódicas. Restitución normal constante $r$. Fig. 2: instantáneas del estado estacionario con $N=11025$, $r_t=-1$, $\delta=1$, $\nu=0.34$, $H_{dr}=1.0\,\mathrm{s^{-1}}$ y $r=0.999$, $0.97$, $0.6$. El pie de figura menciona un panel (d) que no aparece en esta página. |
| 6 | §4.1 (cont.), §4.2, §4.3, §5, Fig. 3 | Restitución tangencial $r_t$. Forzado traslacional multiplicativo (ecs. 9–10) y rotacional (ecs. 11–14). Temperaturas adimensionales traslacional y rotacional. Fig. 3: forzado rotacional con $N=11025$, $\nu=0.34$, $r_t=1$, $r=0.1$, $J=1.0\,\mathrm{s^{-1}}$. Inicio del campo medio (teoría de Huthmann–Zippelius). |
| 7 | §5–§5.4 | Ecuaciones de evolución de campo medio (ecs. 15–19). Partículas lisas (ecs. 20–22): temperatura estacionaria y tiempo de relajación. Partículas rugosas con forzado traslacional (ec. 23) y rotacional (ec. 24). Las simulaciones se equilibran primero de forma elástica ($r=1$, $r_t=-1$) hasta llegar a una distribución maxwelliana. |
| 8 | §5.4–§5.4.3, Figs. 4–5 | Parámetros: $\nu=0.34$; $N=1089$ ($f_{dr}=133\,\mathrm{s^{-1}}$) o $N=11025$ ($f_{dr}=67\,\mathrm{s^{-1}}$); $a=10^{-3}\,\mathrm m$; $H_{dr}=1.0\,\mathrm{s^{-1}}$. Con eso $G_r=3.1\times10^3\,\mathrm{s^{-1}}$, $T^{mf}=0.0358$ y $t_n^{-1}=2.9\times10^2\,\mathrm{s^{-1}}$ para $r=0.90$. Con forzado homogéneo ($\delta=0$) el sistema queda casi homogéneo, sin clusters y casi maxwelliano, lo que contradice los experimentos: el forzado de esos experimentos «no es el ruido blanco homogéneo» habitual. Fig. 4: el campo medio reproduce el transitorio ($N=11025$, $\delta=1$, $r=0.99$). Colapso de los tiempos de relajación. Fig. 5: $T^{eq}/T^{mf}$ en función de $r$ para distintos $\delta$. Con $\delta=-1$ el forzado es singular a baja velocidad. |
| 9 | §5.4.4–§5.4.6, Fig. 6 | Dependencia con el tamaño ($N=11025$ y $5476$). *Clustering* estacionario: con $r=0.999$ el sistema es homogéneo; con $r=0.97$ aparecen clusters densos, persistentes y cristalinos; con $r=0.6$ los clusters son más chicos y dinámicos. Con $\delta=1$ los clusters son estables, en equilibrio con una fase gaseosa; con $\delta\le0$ son transitorios. Forzado rotacional: con $r$ entre $0.99$ y $10^{-4}$ la desviación respecto del campo medio es de apenas un 10 %, mientras que con forzado traslacional ya es del 30–40 % en $r=0.6$. Fig. 6: $T_{rot}$ y $R=T_{rot}/T_{tr}$ en función de $r$. Muchos materiales reales cumplen $r_t\approx0.4$. |
| 10 | Fig. 7, §5.5, §6, §6.1 | Fig. 7: $R$ en función de $r_t$ con $r=0.1$. El campo medio falla cuando $r_t\to-1$ porque el acoplamiento $1+r_t$ es débil. Resumen del forzado: predice $T^{mf}\propto[\nu g(\nu)]^{-2/(3-2\delta)}$ como prueba experimental para estimar $\delta$. Enfriamiento libre: $N=99856=316^2$, $r=0.8$, $\nu=0.25$, $L=560$, $2a=1\,\mathrm{mm}$. Como $t_n^{-1}\gtrsim50\,\mathrm{s^{-1}}$ es mucho menor que $t_c^{-1}=10^5\,\mathrm{s^{-1}}$, el modelo TC afecta a muy pocas partículas. Enfriamiento homogéneo (ec. 25). |
| 11 | Figs. 8–9, §6.1 (cont.), §6.2, §6.3 | Fig. 8: instantáneas en $\tau=0.047$, $380$ y $12150$ (crecimiento de clusters). Fig. 9: $E(\tau)$ para $r=0.2$ a $0.95$. En el régimen homogéneo $t_n^{-1}\propto\sqrt E$. Desviaciones desde $\tau\approx1$–$40$. Ley de potencias a tiempos largos: pendiente $-2$ en enfriamiento homogéneo y algo menor que $-1$ en crecimiento de clusters ($-0.920$, $-0.927$ y $-0.941$ para $r=0.9$, $0.8$ y $0.6$, $\pm0.002$). Criterio de cluster: pares a distancia menor que $(1+S)d$ con $S=0.1$; se miden $\langle M\rangle$ y $M_{max}$. |
| 12 | Fig. 10, §6.3 (cont.), §7, Fig. 11 | Fig. 10: $\langle M\rangle$ y $M_{max}$ en función de $\tau$. Las simulaciones muy largas son posibles gracias al modelo TC, que reduce la disipación cuando los contactos son demasiado frecuentes. Micro-macro: grilla de $50\times50$ celdas con densidad $\nu(x,y)$, velocidad media $\boldsymbol v(x,y)$ y energía cinética de fluctuación $e(x,y)$. Isolíneas: $\nu<0.1$ (zonas casi vacías), $0.6<\nu<0.8$ (coexistencia) y $\nu>0.8$ (sólido triangular). Temperatura y densidad no se correlacionan de forma simple. |
| 13 | Fig. 12, §8, Referencias 1–23 | Fig. 12: campo de flujo con $N=99856$, $r=0.9$, $\nu=0.25$ y $\tau=1595$. El pie anuncia una instantánea arriba, pero solo se ve el campo de flujo. Los clusters no son estables: tienen modos internos de corte y compresión. Conclusión: la teoría predice bien la energía mientras el sistema se mantiene homogéneo; con disipación fuerte crecen los clusters y se pierde la homogeneidad. |
| 14 | Referencias 24–60 | Ref. 45: S. Luding y S. McNamara, «How to handle the inelastic collapse of a dissipative hard-sphere gas with the TC model», *Granular Matter* 1(3):113–128, 1998. Ref. 44: B. D. Lubachevsky, *J. Comp. Phys.* 94:255, 1991 (algoritmo ED). |

## Transcripción de relaciones verificadas visualmente

Notación del original: $r$ es la restitución normal, $r_t$ la restitución tangencial, $a$ el radio y $\nu$ la fracción de volumen o de área.

- p. 2, esfera dura: $m=(4/3)\pi\rho a^3$.
  - (1) $\boldsymbol v'_{1,2}=\boldsymbol v_{1,2}\mp(1+r)\,\boldsymbol v_n/2$, con $\boldsymbol v_n\equiv[(\boldsymbol v_1-\boldsymbol v_2)\cdot\hat{\boldsymbol n}]\,\hat{\boldsymbol n}$.
  - (2) $\Delta\boldsymbol P=-m(1+r)\,\boldsymbol v_n/2$.
  - Energía perdida por colisión: $\Delta E=-m(1-r^2)\,v_n^2/4$; hay disipación cuando $r<1$.
- p. 2, esfera blanda: se reemplaza $\Delta\boldsymbol P$ de la ec. (2) por $\boldsymbol f(t)\,\Delta t_{MD}$.
- p. 3, modelo TC:
  - Con $r$ constante y tiempos entre eventos que tienden a cero, aparece el colapso inelástico: la frecuencia de colisiones diverge para unas pocas partículas. Es un artefacto del modelo.
  - Solución: reintroducir la duración física de contacto $t_c$. La restitución pasa a ser $r_n^{(i)}=1$ si $t_n^{(i)}\le t_c$, donde $t_n^{(i)}$ es el tiempo desde la última colisión de la partícula $i$.
  - Así la disipación por contacto queda acotada ($\Delta E\propto1-r^2$) y la tasa de disipación es finita.
  - En sistemas densos reales aparece el «detachment effect» (la disipación se vuelve ineficaz), que el modelo con $r$ constante no reproduce.
  - El modelo TC no afecta observables como la energía si $t_c$ es razonablemente chico (ref. 45).
- p. 4, tensor de tensiones:
  - Contribución cinética: $k_BT=2E/(DN)$ y $p=nk_BT$, con $n=N/V$.
  - Vector rama $\boldsymbol l=\boldsymbol r_1-\boldsymbol r_2$, con $l=2a$ y $\hat{\boldsymbol n}=\boldsymbol l/l$. Deformación $\boldsymbol\Delta=\boldsymbol l-2a\hat{\boldsymbol n}$.
  - (3) $\delta\boldsymbol\Delta=\boldsymbol\Delta'-\boldsymbol\Delta\approx\delta\boldsymbol l=\boldsymbol\varepsilon\cdot\boldsymbol l$.
  - $u=k\Delta^2/(2V)$.
  - (4) $\delta u=\frac kV(\boldsymbol\Delta\cdot\delta\boldsymbol\Delta+\frac12(\delta\boldsymbol\Delta)^2)\approx\frac kV\boldsymbol\Delta\cdot\delta\boldsymbol l^n$, con $\delta\boldsymbol l^n=\hat{\boldsymbol n}(\hat{\boldsymbol n}\cdot\boldsymbol\varepsilon\cdot\boldsymbol l)$.
  - (5) $\boldsymbol\sigma=\partial u/\partial\boldsymbol\varepsilon=\frac kV\boldsymbol\Delta\otimes\boldsymbol l=\frac1V\boldsymbol f\otimes\boldsymbol l$, con $\boldsymbol f=k\boldsymbol\Delta$.
  - (6) $\boldsymbol\sigma=\frac1V\left[\sum_i m_i\boldsymbol v_i\otimes\boldsymbol v_i-\frac1{\Delta t}\sum_n\sum_j\boldsymbol p_j\otimes\boldsymbol l_j\right]$. Acá $\boldsymbol p_j$ es el cambio de momento y $\boldsymbol l_j$ el vector centro-contacto de la partícula $j$ en la colisión $n$; la primera suma de la derecha recorre las colisiones del intervalo $\Delta t$. Es decir, la fuerza de (5) se reemplaza por $\boldsymbol f=\boldsymbol p_j/\Delta t$.
- p. 4, ecuación de estado 2D:
  - $p=(\sigma_1+\sigma_2)/D$ y $P=pV/E-1$ (solo la parte colisional).
  - $P_0=2\nu g_{2a}(\nu)$, con $g_{2a}(\nu)=(1-7\nu/16)/(1-\nu)^2$ y $\nu=N\pi a^2/V$.
  - $P_4=P_0(1-a_g\nu^4)$, con $a_g=0.1$.
  - $t_n^{-1}=4\nu g_{2a}(\nu)\sqrt{T/(\pi a^2m)}=2P\sqrt{T/(\pi a^2m)}$.
- p. 5, ecuación de estado densa:
  - $P_{fv}=(\sqrt{\nu_{max}/\nu}-1)^{-1}$.
  - $P_{dense}=[1+a_d(\nu_{max}-\nu)^{a_p}]P_{fv}$, con $a_d=0.340$ y $a_p=1.09$.
  - (7) $Q=P_4+m(\nu)[P_{dense}-P_4]$.
  - (8) $m(\nu)=[1+\exp(-(\nu-\nu_c)/m_0)]^{-1}$.
  - Pie de Fig. 1 (p. 4): $\nu_c=0.701$, $\nu_{max}=0.9069$, $m_0=0.00928$.
  - Discrepancia: para $Q_0$ el pie de Fig. 1 dice $m_0=0.0015$ y el texto de p. 5 dice $m_0=0.015$. Las dos lecturas se verificaron a 200 dpi.
- p. 5, colisión normal entre partículas $i$ y $j$:
  - $\boldsymbol v_c'^{(n)}=-r\,\boldsymbol v_c^{(n)}$ y cambio de momento $-(m/2)(1+r)\boldsymbol v_c^{(n)}$.
  - $\boldsymbol v_c^{(n)}=[(\boldsymbol v_i-\boldsymbol v_j)\cdot\boldsymbol n]\boldsymbol n$, con $\boldsymbol n=(\boldsymbol r_i-\boldsymbol r_j)/|\boldsymbol r_i-\boldsymbol r_j|$.
- p. 6, colisión tangencial:
  - $\boldsymbol v_c'^{(t)}=-r_t\,\boldsymbol v_c^{(t)}$.
  - Disipación $\propto1-r^2$ (normal) y $\propto1-r_t^2$ (tangencial); acoplamiento rotación-traslación $\propto1+r_t$.
  - $r$ va de 0 (inelástico) a 1 (elástico); $r_t$ va de $-1$ (liso) a $+1$ (rugoso).
  - B20 no define explícitamente $\boldsymbol v_c^{(t)}$ (no aparece la contribución de $\omega$ al punto de contacto).
- p. 6, forzado traslacional multiplicativo, aplicado cada $\Delta t=f_{dr}^{-1}$:
  - (9) $v_i'^{x}(t)=v_i^x(t)+r_i^x|\boldsymbol v_i(t)|^\delta v_r^{1-\delta}$, y lo mismo en $y$, con $r_i^{x,y}$ gaussianos de media cero.
  - $v_r=1\,\mathrm{m\,s^{-1}}$, $T=E/(NT_r)$, $E=(m/2)\sum\boldsymbol v_i^2$ y $T_r=mv_r^2$. La varianza de $r_i^{x,y}$ es la temperatura de forzado $T_{dr}$.
  - (10) $\Delta T/\Delta t=H_{dr}T^\delta$, con $H_{dr}=f_{dr}T_{dr}$.
  - Para forzado homogéneo se suele suponer $f_{dr}\gg t_n^{-1}$; acá se usa $f_{dr}\sim100\,\mathrm{s^{-1}}$, como en los experimentos.
- p. 6, forzado rotacional:
  - (11) $\omega_i'(t)=\omega_i(t)+r_i^\omega\omega_0$ (componente $z$).
  - (12) $T_{tr}=E_{tr}/(NT_0)$ y (13) $T_{rot}=2E_{rot}/(NT_0)$, con $E_{rot}=(qma^2/2)\sum\omega_i^2$, $q=2/5$, $T_0=mv_0^2$ y $v_0=a\omega_0$.
  - (14) $\Delta T_{rot}/\Delta t=J_{dr}$, con $J_{dr}=f_{dr}T_{dr}^\omega$.
- p. 7, campo medio:
  - (15) $\frac{d}{dt}T_{tr}=G[-AT_{tr}^{3/2}+BT_{tr}^{1/2}T_{rot}]+H_{dr}T^\delta$.
  - (16) $\frac{d}{dt}T_{rot}=2G[BT_{tr}^{3/2}-CT_{tr}^{1/2}T_{rot}]+J_{dr}$.
  - (17) $G=8\nu g_{2a}(\nu)/(a\sqrt{\pi m})$.
  - (18) $A=(1-r^2)/4+\eta(1-\eta)/2$ y $B=\eta^2/(2q)$.
  - (19) $C=\eta(1-\eta/q)/(2q)$, con $\eta=q(1+r_t)/(2q+2)$.
- p. 7, partículas lisas:
  - (20) $\frac{d}{dt}T=-G_rAT^{3/2}+H_{dr}T^\delta$, con $G_r=8an\sqrt{\pi T_r/m}\,g(\nu)$ y $A=(1-r^2)/4$.
  - (21) $T^{mf}=(H_{dr}/(G_rA))^{2/(3-2\delta)}$. El exponente vale $2/3$ si $\delta=0$ y $2$ si $\delta=1$. Para $\delta\ge3/2$ no hay equilibrio estable.
  - (22) $T^{mf}-T(t+t_0)=T(t_0)\exp\{-[3At_n^{-1}+\delta H_{dr}(T^{mf})^{\delta-1}]t\}$, con $t_n^{-1}=G_r\sqrt{T^{mf}}/2$.
  - Para $\delta=1$: $t_{relax}^{-1}=(5/2)H_{dr}$, que no depende de $A$, es decir, de la inelasticidad.
- p. 7, partículas rugosas:
  - (23) Forzado traslacional ($J_{dr}=0$, $\delta=0$): $T_{rot}^{mf}=(H_{dr}/(G\Gamma_{tr}))^{2/3}$ y $T_{tr}^{mf}=T_{rot}^{mf}/R$, con $\Gamma_{tr}=(C/B^3)^{1/2}(CA-B^2)$ y $R=B/C$.
  - (24) Forzado rotacional ($H_{dr}=0$): $T_{rot}^{mf}=(J_{dr}/(G\Gamma_{rot}))^{2/3}$ y $T_{tr}^{mf}=T_{rot}^{mf}/R$, con $\Gamma_{rot}=2(B/A^3)^{1/2}(CA-B^2)$ y $R=A/B$.
- p. 8: impreso como «$G_r=8\nu v_r/\sqrt\pi a g(\nu)$». Según la ec. de p. 7, debe leerse $8\nu v_rg(\nu)/(\sqrt\pi a)$.
- p. 10, enfriamiento homogéneo:
  - (25) $E(\tau)=1/(1+\tau)^2$, con $\tau=(1-r^2)t/(4t_E)$.
  - $t_E^{-1}=8\nu g(\nu)\bar v/(\sqrt\pi d)$ y $\bar v=\sqrt{K(t)/(Nm)}$.
  - Con $1-r^2=0.36$, $g(\nu)\approx1.5833$ y $\bar v=0.02883\,\mathrm{m/s}$ queda $t_E^{-1}(0)=51.5\,\mathrm{s^{-1}}$.
- p. 12, campos por celda $c$:
  - $\nu(x,y)=n_c\pi a^2/V_c$ y $\boldsymbol v(x,y)=\sum_{i\in c}\boldsymbol v_i/n_c$.
  - $e(x,y)=(m/2)\sum_{i\in c}[\boldsymbol v_i-\boldsymbol v(x,y)]^2/n_c$.

## Limitaciones

- No se transcribieron las referencias completas; solo se señalan las más relevantes.
- Las figuras se describen por su pie y por lo que se ve, no por valores leídos de los ejes.
- Las secciones §4–§5 son casi idénticas a §1.2–§1.5 de B21 (Luding, Cafiero y Herrmann, «Driven Granular Gases»).
