# Dinámica molecular por paso temporal e integradores

## Alcance y fuentes

La dinámica molecular dirigida por paso temporal integra las ecuaciones de Newton con incrementos fijos $h=\Delta t$. Los contactos duran varios pasos y se representan mediante fuerzas; este enfoque es útil para interacciones persistentes o densidades altas [T04, p. 2] [T04, p. 3]. Se diferencia del avance hasta el próximo choque de la [simulación por eventos del TP3](eventos-y-tp3.md).

La fuente principal es T04. Heermann desarrolla esquemas de integración y sus costos [B19, p. 27] [B19, p. 29]; Gear presenta una formulación matricial de métodos multipaso y el tratamiento directo de ecuaciones de orden superior [B17, p. 1] [B17, p. 6]. Hou y Mišković estudian dinámica browniana con fricción y ruido: es bibliografía complementaria, no una modificación del modelo determinista del TP4 [B18, p. 1] [B18, p. 2] [TP04, p. 2].

Las citas de B19 indican la página del **archivo DjVu**, incluida la portada. Por ejemplo, las páginas 38 y 39 del archivo corresponden a las páginas impresas 28 y 29. El OCR facilita búsquedas, pero las fórmulas deben verificarse en el original.

## Verlet original y sincronización

Con $a_n=F_n/m$:

$$r_{n+1}=2r_n-r_{n-1}+h^2a_n,\qquad
v_n=\frac{r_{n+1}-r_{n-1}}{2h}.$$

La recurrencia calcula posiciones sin usar velocidades cuando la fuerza depende solo de posiciones. La velocidad centrada pertenece a $t_n$, aunque se obtiene después de calcular $r_{n+1}$; por eso hay que guardar $r_n$ y $v_n$ juntos, particularmente al calcular energía [T04, p. 13] [T04, p. 14] [B19, p. 38].

Se necesita inicialización. La teórica propone estimar el estado previo con Euler en $-h$; Heermann muestra el arranque hacia adelante $r_1=r_0+hv_0+h^2a_0/2$ [T04, p. 14] [B19, p. 39]. **Decisión pendiente de implementación:** declarar el arranque elegido y verificar cuánto afecta el ECM del oscilador.

## Velocity Verlet

$$r_{n+1}=r_n+hv_n+\frac{h^2}{2}a_n,\qquad
v_{n+1}=v_n+\frac h2(a_n+a_{n+1}).$$

Esta variante entrega posiciones y velocidades en el mismo instante [T04, p. 17] [B19, p. 39].

**Inferencia algebraica para el oscilador amortiguado:** con $a(r,v)=-(kr+\gamma v)/m$, la segunda ecuación contiene $v_{n+1}$ implícitamente. Si se conserva esa ecuación, puede despejarse:

$$v_{n+1}=\frac{v_n+\frac h2a_n-\frac{hk}{2m}r_{n+1}}{1+\frac{h\gamma}{2m}}.$$

No asumir que una implementación diseñada para fuerzas solo posicionales sirve sin adaptación para el amortiguamiento. La teórica distingue explícitamente el caso de fuerzas dependientes de la velocidad en Beeman y Gear [T04, p. 20] [T04, p. 29].

## Beeman con fuerza dependiente de velocidad

La variante predictor-corrector de la teórica usa:

$$r_{n+1}=r_n+hv_n+h^2\left(\frac23a_n-\frac16a_{n-1}\right),$$
$$v^p_{n+1}=v_n+h\left(\frac32a_n-\frac12a_{n-1}\right),$$
$$a^p_{n+1}=a(r_{n+1},v^p_{n+1}),\qquad
v_{n+1}=v_n+h\left(\frac13a^p_{n+1}+\frac56a_n-\frac16a_{n-1}\right).$$

Estas son las etapas de la diapositiva 20; la diapositiva 19 presenta la forma sin predictor de velocidad [T04, p. 19] [T04, p. 20]. El arranque de $a_{-1}$ y la evaluación de la aceleración que se conserva para el siguiente paso deben quedar explícitos en la implementación y su validación.

## Euler predictor-corrector de la cátedra

La diapositiva 23 define específicamente:

$$r^p_{n+1}=r_n+hv_n,\qquad v^p_{n+1}=v_n+ha_n,$$
$$a^p_{n+1}=a(r^p_{n+1},v^p_{n+1}),$$
$$v_{n+1}=v_n+ha^p_{n+1},\qquad r_{n+1}=r_n+hv_{n+1}.$$

Usar estas ecuaciones al identificar el método solicitado, o declarar y justificar cualquier variante. La diapositiva no usa el promedio trapezoidal de pendientes [T04, p. 23].

## Gear y bibliografía complementaria

Los predictor-corrector separan predicción, evaluación de fuerzas y corrección [T04, p. 22]. Gear conserva derivadas de la posición y corrige a partir de la diferencia de aceleración [T04, p. 25] [T04, p. 26] [T04, p. 27]. Los coeficientes dependen de si la fuerza incluye velocidad: no intercambiar las tablas de las páginas 28 y 29 [T04, p. 28] [T04, p. 29]. Gear no sustituye ninguno de los cuatro métodos obligatorios del TP4 [TP04, p. 1].

Heermann permite profundizar en diferencias finitas, métodos multipaso, costo de evaluar fuerzas y organización de la dinámica molecular [B19, p. 27] [B19, p. 29] [B19, p. 38]. El artículo B17 distingue error de un paso y error sobre un intervalo fijo; no conviene confundir el orden de un término de Taylor con el orden global del integrador [B17, p. 3]. B18 compara métodos para un oscilador con excitación estocástica y llega a distribuciones de equilibrio de posición y velocidad; sus conclusiones están condicionadas a ese modelo [B18, p. 24] [B18, p. 26] [B18, p. 27].

## Paso de integración, salida y validación

Separar $h$ de la cadencia de salida $h_{\rm salida}=nh$, con $n$ entero [T04, p. 33]. Comparar contra solución analítica cuando existe; para sistemas conservativos, verificar energía cinética más potencial; para sistemas no conservativos, estudiar convergencia al reducir el paso [T04, p. 35].

**Recomendación de implementación:** usar un contador entero de pasos para decidir cuándo escribir. Al verificar energía con Verlet original, sincronizar posiciones y velocidades y contar cada resorte entre dos partículas una sola vez. El potencial de un contacto es $k\xi^2/2$ [T04, p. 42].

Ver el [contrato del TP4](billar-circular-y-tp4.md) y las [lecciones de comunicación](comunicacion-cientifica.md).
