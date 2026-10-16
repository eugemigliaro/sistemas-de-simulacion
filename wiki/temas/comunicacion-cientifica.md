# Comunicación científica

## Regla de prioridad

Cada enunciado de trabajo práctico tiene prioridad sobre las teóricas y guías genéricas. Antes de preparar una entrega hay que leerlo completo, cubrir todos sus puntos y respetar formatos y nombres pedidos [GPRES, p. 1].

## Informe escrito

El informe y la presentación son documentos independientes y autocontenidos. El informe debe numerar secciones y subsecciones, usar lenguaje técnico coherente y sostener un hilo analítico; no puede consistir en figuras sueltas. La estructura habitual es Introducción, Modelo, Implementación, Simulaciones, Resultados y Conclusiones [GINF, p. 1].

Las figuras y ecuaciones deben numerarse y ser referidas desde el texto. Las figuras de resultados deben identificar el observable, la entrada o parámetro, las condiciones, el promedio y las barras de error cuando correspondan [GINF, p. 2]. Los escalares se escriben en itálica sin negrita, los vectores en negrita sin itálica y unidades y números sin ninguna de las dos [GINF, p. 2] [GINF, p. 3].

El informe lleva una sección final no numerada de referencias y solo debe incluir obras citadas en el cuerpo [GINF, p. 3].

## Presentación

La presentación debe numerar diapositivas, respetar el tiempo y evitar párrafos extensos. Las figuras llevan ejes con nombres y unidades, tipografía legible y parámetros fijos junto a la figura; a diferencia del informe, no llevan *caption* debajo. Los datos deben expresarse con notación científica y cifras significativas coherentes con el error [GPRES, p. 1].

La secuencia pedida es:

1. introducción, sistema real y modelo matemático;
2. implementación y arquitectura del simulador;
3. configuración de las simulaciones y definición matemática de observables;
4. resultados y análisis;
5. conclusiones basadas solo en resultados mostrados [GPRES, p. 2] [GPRES, p. 3].

Una hipótesis no probada no debe presentarse como conclusión. Tampoco son conclusiones lo que quedó pendiente o los intentos descartados [GPRES, p. 3].

La presentación no lleva una sección bibliográfica: cuando haga falta, se usa una cita abreviada en la diapositiva correspondiente [GPRES, p. 1]. Las animaciones se muestran embebidas durante la exposición, pero el PDF entregado usa un fotograma estático y un enlace; no se entregan archivos de animación aparte [GPRES, p. 2] [GPRES, p. 3].

## Lecciones de la devolución del TP2

La cátedra devolvió la entrega del TP2 con nota 6 y señaló tres ejes a corregir en las próximas entregas: cómo presentar los resultados, cómo diagramar sin saturar las diapositivas y qué es un parámetro y qué no [COR02]. Las observaciones que trascienden ese trabajo son:

**Arquitectura del simulador.** El motor debe limitarse a generar el estado del sistema, es decir la trayectoria. Los observables se calculan en un post-proceso separado sobre esa salida. Calcularlos dentro del bucle principal fue marcado como error importante tanto en la presentación como en el código, y la cátedra remite a la teórica 0 [COR02] [T00, p. 20]. Ver [Sistemas, modelos y simulación](sistemas-y-modelos.md).

**Parámetros frente a datos de configuración.** Un dato es parámetro físico solo si el comportamiento o la salida del sistema cambia al variarlo. La duración $T$, el inicio del estacionario y la cantidad de celdas $M$ del CIM no lo son y no deben listarse como parámetros. El inicio del estacionario, además, no se conoce a priori: depende de cuándo se alcanza el régimen y es parte de los resultados [COR02].

**Observables y promediado.** Definir un observable instantáneo no alcanza. Hay que explicitar cómo se obtienen promedios y desvíos estándar a partir de varias realizaciones [COR02]; esto complementa la convención $\mu\pm\sigma$ de la teórica [T00, p. 69].

**Diagramas y esquemas.** Un UML con letra pequeña es inútil en una exposición. El esquema del sistema debe llevar etiquetas en el propio dibujo: por ejemplo, una flecha con $L$ en el borde de la caja y un círculo de radio $r_c$ alrededor de una partícula [COR02].

**Animaciones.** Conviene una barra de color, o la leyenda al costado, en lugar de una rueda de colores, para dejar más espacio a la animación. Es preferible mostrar un modelo con dos valores de ruido, completar todo su análisis y recién después repetir para el otro modelo [COR02].

**Afirmaciones cuantitativas.** Evitar cocientes del tipo "tolera entre 7,7 y 15,9 veces más ruido": no queda claro cómo se calculan ni cuál es la afirmación, y esas relaciones no suelen ser lineales [COR02]. Es preferible mostrar la comparación directa en la figura.

**Informe.** No van resultados en la introducción; cada figura debe corresponder al observable de la sección donde aparece; no duplicar la misma información en una tabla y un gráfico; toda figura debe analizarse, y cuando dos figuras son análogas hay que explicitar sus diferencias. Se valoraron positivamente la introducción completa, las figuras con análisis y conclusiones que no agregan información nueva [COR02].

## Lecciones de la devolución del TP3

La devolución aportada del TP3 (G7, nota 6,5) identifica mejoras aplicables a los siguientes trabajos [COR03]:

- **Fundamentos:** presentar teoría general; la configuración particular del sistema pertenece a su descripción, no a fundamentos (D3–D5).
- **Promedios:** especificar si se promedian partículas de una realización, una partícula entre realizaciones o ambas cosas. La fórmula abstracta de esperanza no reemplaza esta definición (D14).
- **Secuencia de cada estudio:** primero situación y variable a estudiar con una animación, después evolución temporal estática y finalmente entrada frente al observable escalar (D18, D20–D21). Respetar excepciones explícitas de la nueva consigna: el oscilador del TP4 lleva solo una figura de ECM, en una diapositiva [TP04, p. 2].
- **Figuras:** no animar gráficos de evolución temporal; no usar mapas de calor para una evolución temporal que admite una representación simple. Reservarlos para un observable escalar frente a dos parámetros independientes (D17–D18).
- **Densidad visual:** reducir cantidad de gráficos y texto; evitar párrafos redactados. Las figuras accesorias de D16 no se pedían; la devolución sugiere combinarlas con doble eje si se incluyen, una indicación específica de ese caso (D16, D20–D21).
- **Configuración y reproducibilidad:** expresar claramente la parametrización. Una semilla aislada no es información reproducible sin identificar el generador; conservar generador y semillas en el registro técnico y no usar el número de semilla como parámetro físico en las diapositivas (D21).
- **Ajustes y precisión:** no tapar curvas con valores ajustados; ubicarlos fuera de la figura y revisar cifras significativas. Justificar cuantitativamente cualquier afirmación de crecimiento exponencial (D22).

La devolución también valora el estudio de rendimiento hasta $N=700$; los artefactos locales disponibles deben revisarse antes de usarlos como evidencia de ese rango [COR03]. Estas reglas complementan, sin sustituir, la consigna del TP4 y las guías [TP04, p. 1].

## Exposición oral

La guía externa recomienda adaptar el nivel a la audiencia, reservar tiempo suficiente para la introducción, respetar estrictamente la duración y limitar ecuaciones y elementos visuales a los que sostienen las ideas principales [B02, p. 1] [B02, p. 2]. También recomienda ensayar en voz alta, mantener contacto visual y repetir o reformular las preguntas para toda la sala [B02, p. 3] [B02, p. 4].

Para una exposición grupal, las partes deben estar equilibradas, todos deben conocer el trabajo completo y las respuestas a preguntas deben coordinarse sin superposiciones [GPRES, p. 3].
