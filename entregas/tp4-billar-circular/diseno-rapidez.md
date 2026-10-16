# Diseño implementado — rapidez (TP4, 2.3)

Continuación del plan de TP4 autorizado por el estudiante. Artefacto de desarrollo; no es la presentación entregable.

## Contrato y método

N=100 sin obstáculos, velocidades iniciales de módulo 1 m/s, diez realizaciones con semillas 1–10. Motor C++ existente, Verlet original, h=0,0000125 s. Postproceso Python de estados guardados cada 0,1 s. No se reajustan velocidades ni se agrega termostato [TP04, pp. 2–4].

Cada histograma divide el conteo por la cantidad de velocidades y por el ancho del bin. Los bins comunes de 0,1 m/s cubren **todos** los valores observados, con un bin adicional; no se descartan colas. Primero se obtiene una densidad por realización; luego se promedian las diez densidades con igual peso. En ventanas temporales, todas las realizaciones aportan igual cantidad de cuadros. Los cuadros de una misma corrida no se consideran realizaciones independientes. Las barras son desvíos estándar entre diez densidades por realización, no errores estándar [T00, pp. 68–70] [COR03].

Se minimiza E(theta)=sum_i [hist_i−modelo_i(theta)]² sin pesos, con theta=kBT como único parámetro. Para respetar los bins, el modelo es la **densidad teórica promediada dentro de cada bin**, calculada integrando exactamente Maxwell–Boltzmann 2D. No se ajusta amplitud, offset ni masa; tampoco se renormaliza la curva teórica truncada al rango graficado. Búsqueda en log(theta) mediante grilla y refinamiento por sección áurea; se rechazan mínimos en los extremos [TP04, p. 4] [T00, pp. 79–80].

## Comprobación de estabilidad

Un ensayo de 30 s con ventanas de 5 s no satisfizo el límite local de cambio térmico del 2 % en la última comparación. Se preservan código, configuración, checkpoints y diagnóstico en `experiments/results/speed-pilot-30/`; sus trayectorias están en `experiments/raw/speed-pilot-30/`. Los caminos internos de aquel contrato son los originales anteriores al archivo.

El estudio principal amplía el horizonte a 60 s y las ventanas a 10 s para reducir el ruido del histograma. Se mantiene el criterio de TV≤0,05 (distancia de variación total entre histogramas medios adyacentes) y cambio relativo del theta ajustado≤2 %. Se exige un sufijo completo con al menos tres comparaciones consecutivas que cumplan ambos límites. La primera ventana se excluye siempre del ajuste estacionario porque contiene el estado inicial singular.

Estos umbrales y la anchura temporal son decisiones locales, no requisitos de cátedra. Es un diagnóstico descriptivo y de resolución temporal gruesa: no demuestra equilibrio exacto ni identifica el instante mínimo de relajación. Si el criterio falla, el programa guarda el diagnóstico y no produce un ajuste declarado estacionario. El cambio de horizonte/ventana se informa para no ocultar el ensayo exploratorio [COR02].

## Validación y procedencia

El lector verifica cuadros completos, IDs, tiempos y horizonte. Se controla energía total en cada cuadro guardado, incluyendo potencial de pares y pared; tolerancia local 0,1 % respecto al estado inicial. El máximo es muestreado, no continuo. Se comparan theta ajustado, m⟨v²⟩/2 medido y mv0²/2=0,0125 J. La energía potencial durante contactos puede hacer que la energía cinética por partícula difiera de la referencia inicial.

Se preservan muestras de rapidez y componentes energéticas en NPZ, hashes de trayectorias, código y binario, metadatos, resultados por realización y manifiesto de artefactos. El ejecutor rechaza checkpoints incompatibles. Pruebas: normalización y rechazo de colas fuera de rango, integral teórica conocida, recuperación de theta sintético y exigencia de comparaciones estables consecutivas.

## Alcance

Se generan datos, figuras y documentación técnica para revisión y aprendizaje. La elaboración de la presentación por los estudiantes y la declaración del uso real de IA siguen siendo necesarias [TP04, p. 4].
