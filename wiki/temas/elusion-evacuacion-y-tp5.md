# Elusión, evacuación y TP5

## Contrato de entrega

El enunciado se publicó en Campus el 30/10/2026. Hay que **elegir uno de dos problemas** para implementar, estudiar y presentar. Ambos usan uno de dos modelos de dinámica peatonal vistos en las teóricas: **SFM sin fuerza social** o **CPM** [TP05, p. 1]. Los modelos están en [Dinámica peatonal](dinamica-peatonal.md).

- **Paso temporal:** fijo e intrínseco de la simulación. Si hace falta, usar un $dt_2$ para imprimir el estado: posiciones, velocidades y, en CPM, radio. En CPM el $dt$ es parte de las reglas del modelo y no se cambia arbitrariamente [TP05, p. 1].
- **Salida y animación:** la simulación escribe archivos de texto; la animación es un módulo independiente que los lee [TP05, p. 1].
- **Por cada estudio:** una animación característica, la evolución temporal del observable primario, y la forma de calcular el observable escalar que después se grafica contra el parámetro de entrada [TP05, p. 1].
- **Entregables:** exposición de 13 minutos con las secciones de “Formato_Presentaciones.pdf”; PDF sin animaciones embebidas, con enlaces explícitos a YouTube o Vimeo (no Google Drive); ZIP con la versión final del motor, de unos pocos kB, sin post-proceso, historial, salidas, figuras, resultados ni otros documentos [TP05, p. 1].
- **Fecha:** PDF y ZIP por Campus antes del **16/11/2026 a las 13 h**, como `SdS_TP5_2026Q2GXXCSS_Presentación` y `SdS_TP5_2026Q2GXXCSS_Codigo`. XX es el grupo y SS la comisión (“S” o “S2”). La exposición es en la clase de ese mismo día [TP05, p. 1].

**Inferencia:** “Formato_Presentaciones.pdf” es el nombre con que las consignas citan la guía de presentaciones; en el repositorio está catalogada como GPRES. El TP2, TP3 y TP4 usan la misma referencia. A diferencia del TP4 [TP04, p. 4], el TP5 no menciona agentes de programación. Ver [dudas](../dudas-y-conflictos.md).

## Problema 1: calibración de una capa de elusión

### Consigna

La cátedra provee $M$ eventos experimentales. En cada uno, dos peatones caminan en curso de colisión, muestreados cada $\Delta t_{\rm exp}$; para el peatón $i$ del evento $m$ se conoce $\mathbf r_i^{\rm exp}(t_k)$, con $t_k=k\,\Delta t_{\rm exp}$ [TP05, p. 1].

SFM sin fuerza social y CPM no anticipan colisiones por sí solos. Hay que proponer una **capa de elusión con exactamente dos parámetros** $(p_1,p_2)$ que actúe **solo sobre la velocidad deseada, mediante un target temporal**. Al detectar una colisión futura con otro agente, reemplaza transitoriamente el target final por uno temporal; resuelto el conflicto, el agente vuelve al target final. **No puede agregar fuerzas ni modificar las reglas propias del modelo.** Se explica matemáticamente en la introducción y se calibra con los datos [TP05, p. 2]. La teórica presenta esta misma idea del “goal temporario” como capa de elusión reactiva sobre un modelo operacional [T07, p. 16] [T07, p. 17].

### Condiciones de cada simulación

- Cada agente arranca con la posición y la velocidad experimentales del instante inicial del evento.
- Su target final es la última posición experimental; $v_d$ es la rapidez media de su trayectoria.
- Se simula hasta el último instante experimental del evento.
- Radios: $r=0{,}25$ m en SFM; $r_{\min}=0{,}10$ m y $r_{\max}=0{,}25$ m en CPM.
- Los demás parámetros salen de los papers correspondientes [TP05, p. 2].

### Métricas

Para el peatón $i$ del evento $m$, con $N_m$ instantes experimentales [TP05, p. 2]:

$$E^{(1)}_i=\frac1{N_m}\sum_k\left|\mathbf r_i^{\rm exp}(t_k)-\mathbf r_i^{\rm sim}(t_k)\right|^2,$$

$$E^{(2)}_i=\frac1{N_m}\sum_k\min_j\left|\mathbf r_i^{\rm exp}(t_k)-\mathbf r_i^{\rm sim}(t_j)\right|^2.$$

La métrica 1 compara posiciones en el mismo instante y penaliza forma y tiempo de paso; la 2 toma el punto simulado más cercano, aunque sea de otro instante, y compara solo la forma geométrica. Para cada métrica, $E_m$ promedia los dos peatones y el error poblacional promedia los eventos:

$$\langle E\rangle(p_1,p_2)=\frac1M\sum_m E_m(p_1,p_2).$$

Las fórmulas se verificaron sobre el original [TP05, p. 2].

### Puntos a resolver

| Punto | Pedido |
|---|---|
| a | Implementar el modelo con la capa de elusión. Animaciones que superpongan trayectorias experimentales y simuladas en algunos eventos. Dedicar a la descripción matemática de la capa más tiempo que el habitual para la introducción [TP05, p. 2]. |
| b | Calibración poblacional: el par que minimiza $\langle E\rangle$ con los mismos parámetros para todos los eventos, por separado para cada métrica. Describir el método de búsqueda. Mostrar $\langle E\rangle(p_1,p_2)$ (superficie sobre una grilla y/o cortes 1D con barras de error) marcando el óptimo, y comparar los óptimos de ambas métricas [TP05, p. 2]. |
| c | Calibración individual: el par óptimo de cada evento para cada métrica. Mostrar la distribución de óptimos individuales junto a los poblacionales; comparar la distribución de $E_m$ con parámetros poblacionales e individuales y discutir cuánto se gana al individualizar [TP05, p. 2] [TP05, p. 3]. |
| d | Validación cruzada: separar los eventos al azar en entrenamiento y validación, calibrar con el primero, reportar el error del segundo, repetir con distintas particiones y comparar con (b) [TP05, p. 3]. |

### Datos provistos

Las trayectorias están en DEL05 y su descripción en DEL05-LEEME. Resumen en [el derivado](../../material/extraido/DEL05.md):

- 19 pruebas ($M=19$) y 38 personas: cada persona participa en una sola prueba. Muestreo a 15,0192 cuadros/s, es decir $\Delta t_{\rm exp}\approx0{,}0666$ s [DEL05].
- Formato `id frame x y markerID`, posiciones en metros [DEL05].
- Cada prueba indica la persona de la fila izquierda, la de la fila derecha, el rango de cuadros y la distancia mínima entre ambas. La pareja es la que pasa más cerca, con asignación 1 a 1 [DEL05-LEEME].
- **Inferencia:** el `V?` de la prueba 2 es el identificador 1000, el único que tiene `markerID = -1`. Con él, la distancia mínima del LEEME (0,88 m) se reproduce.

Al incorporar los datos se verificaron estas propiedades, que pesan en el diseño de la calibración:

- Las 19 distancias mínimas del LEEME se reproducen con los datos. Van de 0,49 a 0,92 m.
- Hay otras personas en el registro durante cada prueba: los rangos de pruebas consecutivas se superponen. La consigna simula solo a los dos agentes del evento [TP05, p. 2].
- No todas las trayectorias empiezan en el primer cuadro de la prueba: en 12 de 38, el primer dato llega con más de 5 cuadros de retraso (hasta 62, unos 4 s). También hay cuadros faltantes dentro de algunas series.
- Varias personas arrancan casi detenidas: la rapidez estimada con los dos primeros cuadros va de 0 a 0,93 m/s.
- La “rapidez media” cambia según cómo se calcule: entre 0,76 y 1,12 m/s con largo del camino sobre duración, y entre 0,59 y 1,07 m/s con desplazamiento neto sobre duración.

**Inferencia:** en la prueba 5 la distancia mínima medida (0,49 m) es menor que la suma de radios del SFM ($2\times0{,}25=0{,}50$ m). Un peatón real no es un disco; aun la mejor capa de elusión no reproduciría exactamente ese evento sin contacto.

### Decisiones que hay que declarar

Ninguna está fijada por la consigna; ver [dudas](../dudas-y-conflictos.md):

1. **Inicio de cada agente:** usar el primer cuadro del evento o el primer cuadro de cada persona dentro del evento. Qué hacer con un agente que todavía no tiene datos.
2. **Velocidad inicial:** el estimador sobre datos ruidosos (diferencia de dos cuadros, ajuste sobre varios cuadros, suavizado).
3. **Rapidez media:** largo del camino o desplazamiento neto, sobre qué tramo, y si se suaviza antes.
4. **Huecos:** cómo cuenta $N_m$ con cuadros faltantes y en qué instantes se compara la métrica 1.
5. **Detección y fin del conflicto:** el criterio de “colisión futura” y el de “conflicto resuelto”, porque definen qué significan $p_1$ y $p_2$.

**Propuesta, no exigencia de la cátedra:** usar los mismos instantes $t_k$ en ambas métricas y para los dos agentes, y escribir las cinco decisiones en la diapositiva del método de calibración.

### Material de apoyo para diseñar la capa

T07 presenta varios mecanismos de anticipación:

- **Elusión predictiva:** tiempo de anticipación, espacio personal y posiciones futuras al instante de choque [T07, p. 7] [T07, p. 9] [T07, p. 11].
- **Heurística cognitiva:** dirección que minimiza la distancia al destino dentro del campo visual, y rapidez limitada por el tiempo hasta el primer obstáculo [T07, p. 21] [T07, p. 22].
- **CPM con elusión:** dirección deseada que combina el target con un término repulsivo del vecino visible más cercano [T07, p. 28] [T07, p. 29].

Esas variantes modifican directamente la dirección deseada o agregan fuerzas. La consigna exige otra cosa: **solo un target temporal y exactamente dos parámetros**. Hay que adaptar la idea, no copiarla. Los detalles y parámetros de cada paper están en [Dinámica peatonal](dinamica-peatonal.md#elusión-de-colisiones).

En la bibliografía, el antecedente más cercano es **AA-CPM** [B32, p. 3] [B32, p. 4] [B32, p. 5]:

- Elude mediante targets temporales y dinámicos.
- Tiene dos parámetros calibrados, $A_p=1{,}1$ y $B_p=2{,}1$.
- Inicializa cada agente con la posición y la velocidad experimentales y le pone el target en el último punto, como pide la consigna.

Diferencias que impiden reusar sus resultados tal cual:

- **Datos:** B32 usa 40 pares de voluntarios que parten de un círculo de 3 m de radio, más 10 trayectorias que esquivan un obstáculo fijo [B32, p. 2]. Su paso es de 1/33 s, igual a la frecuencia de captura [B32, p. 4]. Los datos de la cátedra son 19 cruces de frente a 15 cuadros/s [DEL05-LEEME] [DEL05].
- **Métrica:** B32 recorre los puntos simulados y promedia la distancia, sin elevarla al cuadrado [B32, p. 4]. La métrica 2 del TP recorre los puntos experimentales y promedia distancias al cuadrado [TP05, p. 2].
- **Modelo:** B32 usa un CPM anisótropo; el TP pide el CPM de la referencia [2] sin modificar sus reglas [TP05, p. 2].

**Inferencias:**

- Los valores de $A_p$ y $B_p$ de B32 sirven como punto de partida de la grilla, no como resultado.
- En CPM la capa puede escribirse como un target temporal $\mathbf T_i=\mathbf x_i+\ell\,\mathbf e_a$. Solo importa su dirección, porque $\mathbf v_d=v_d\mathbf e_{\rm target}$ [B28, p. 2]. Si se recalcula cada paso, $\ell$ no es un tercer parámetro.
- Cualquier otra constante de la capa (cantidad de vecinos considerados, criterio de fin del conflicto) cuenta para la regla de “exactamente dos parámetros”. Hay que fijarla y declararla.

Otras opciones de detección:

- **Predictiva:** con tiempo de anticipación y espacio personal, que darían los dos parámetros [B29, p. 4] [B29, p. 5].
- **Reactiva:** como el target dinámico del juego humano–zombi [B31, p. 3].

En CPM el paso temporal no es libre: con la ec. (2) del modelo, $\Delta t=r_{\min}/(2\max(v_d^{\max},v_e))$ [B28, p. 2]. **Inferencia:** como $\Delta t_{\rm exp}\approx0{,}067$ s no coincide con ese paso, para la métrica 1 hay que interpolar la trayectoria simulada en los instantes $t_k$.

## Problema 2: evacuación con esquema híbrido

### Sistema

- $N=500$ agentes en una habitación cuadrada de lado $L=50$ m, con una puerta de ancho $d=0{,}8$ m en el centro de una pared.
- Posiciones iniciales al azar en toda la habitación, sin superposiciones con otros agentes ni con las paredes (densidad baja).
- Target: la puerta; $v_d=1{,}5$ m/s. Paredes rígidas que interactúan si un agente las choca.
- Un agente que cruza la puerta sale de la simulación cuando se aleja 1 m de ella, lo que exige un segundo target.
- Radios: uniformes en $[0{,}18;\,0{,}25]$ m en SFM; $r_{\min}=0{,}10$ m y $r_{\max}=0{,}25$ m en CPM. Los demás parámetros, de los papers [TP05, p. 3].

En la zona diluida los agentes van en línea recta y casi no interactúan: conviene **EDMD**, que avanza hasta el próximo evento (contacto entre agentes, con paredes, llegada a la puerta). En el cuello de botella las interacciones son continuas: conviene **TSDMD** [TP05, p. 3] [TP05, p. 4]. Ver [simulación por eventos](eventos-y-tp3.md) e [integradores](paso-temporal-e-integradores.md).

### Qué describir matemáticamente

Un esquema híbrido que separe ambos métodos **por etapas y por partícula**, con [TP05, p. 4]:

- Criterios de pasaje EDMD ↔ TSDMD (por ejemplo, densidad local, número de vecinos, tiempo al próximo contacto o distancia a la puerta).
- Convivencia de ambos esquemas: sincronización entre eventos y pasos $dt$; cálculo de eventos entre una partícula EDMD y una TSDMD; garantía de que no se pierdan contactos ni aparezcan superposiciones al cambiar de esquema.
- En EDMD puro y en el híbrido: tratamiento de las colisiones agente–agente y agente–pared, y mecanismo para recuperar la velocidad deseada después de una colisión.

### Puntos a resolver

| Punto | Pedido |
|---|---|
| a | Implementar TSDMD puro, EDMD puro e híbrido. Animación de cada uno; en el híbrido, colorear según el esquema de cada partícula en cada instante. Fracción de partículas en cada esquema contra el tiempo. Dedicar a la descripción del híbrido más tiempo del habitual [TP05, p. 4]. |
| b | Para los tres: curvas de población (agentes dentro contra tiempo) y tiempo de evacuación (salida del último). Al menos 10 realizaciones; tiempos medios con barras de error. Discutir diferencias con TSDMD puro como referencia [TP05, p. 4]. |
| c | Tiempo de ejecución (wall-clock) de la simulación completa de los tres, en la misma computadora y con barra de error. En el híbrido, variar el parámetro principal del criterio de pasaje y graficar ejecución y evacuación contra ese parámetro, con TSDMD y EDMD puros como referencias [TP05, p. 4]. |
| d | Escalamiento del tiempo de ejecución con $N$ (por ejemplo, $N\in[100,1000]$): (a) aumentando $L$ a densidad inicial constante; (b) a $L$ constante, aumentando la densidad [TP05, p. 4]. |

**Inferencia:** en CPM el $dt$ es parte de las reglas [TP05, p. 1] y el radio se recupera a razón de $r_{\max}/(\tau/\Delta t)$ por paso [T06, p. 49]. Un tramo EDMD de un agente CPM tiene que reproducir la misma dinámica que esos pasos, o el híbrido deja de ser comparable con TSDMD puro. Ver [el modelo CPM](dinamica-peatonal.md#contractile-particle-model).

Antecedentes en la bibliografía:

- **SFM:** en el paper original, la evacuación se vuelve irregular y aparecen arcos que bloquean la puerta desde $v_0\gtrsim1{,}5$ m/s, con una puerta de 1 m [B26, p. 2]. **Inferencia:** el $v_d=1{,}5$ m/s del TP5 está en ese umbral y la puerta es más angosta (0,8 m), así que el cuello de botella será denso.
- **CPM:** los agentes apuntan a un punto dentro del 60 % central de la puerta y, al cruzarla, reciben un target exterior [B28, p. 4]. El caudal específico simulado queda dentro del rango experimental de 1,25 a 2 p/(m·s) [B28, p. 5].
- **Recuperar la velocidad deseada tras un choque:** en SFM sin fuerza social, la relajación hacia $v_d$ es exponencial con escala $\tau$ [T06, p. 31]. En CPM, el radio crece paso a paso [T06, p. 49]. **Inferencia:** en EDMD, la primera admite una solución analítica entre eventos; la segunda obliga a respetar la grilla de pasos del modelo.

## Referencias de la consigna

- [1] SFM: Helbing, Farkas y Vicsek, *Nature* 407, 487–490 (2000), catalogado como B26.
- [2] CPM: Baglietto y Parisi, *Phys. Rev. E* 83, 056117 (2011), catalogado como B28 [TP05, p. 4].
