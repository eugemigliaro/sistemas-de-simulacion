# Posición de obstáculos — punto 2.2

Se continúa el orden de resolución acordado: estudiar posición antes de distribución de velocidades. Se mantienen motor, modelo y separación de observables ya verificados; no se modifican los estudios anteriores.

## Experimento

Se usan N=100 y N=20, cinco semillas independientes por posición y un horizonte máximo de 100 s [TP04, p. 3]. La grilla de posiciones contiene once valores igualmente espaciados desde r=0,0175 m hasta R−r=0,4925 m: paso espacial 0,0475 m. Son 110 corridas. Se mantienen la inicialización por rechazo uniforme en área y direcciones uniformes; una misma semilla no garantiza posiciones iniciales idénticas entre geometrías porque cambian los rechazos.

El paso previamente elegido para 30 s era 0,00005 s. En cuatro pilotos de 100 s (ambos N y extremos del intervalo), ese paso produjo errores energéticos máximos muestreados de aproximadamente 0,1035 %, 0,1163 %, 0,0704 % y 0,0630 %. En particular, los dos casos N=100 superaron el criterio local de 0,1 %. Con 0,000025 s los cuatro pilotos cumplieron. El barrido emplea uniformemente **0,0000125 s**, mitad del paso validado, como margen para las posiciones intermedias. La selección y sus datos se conservan por separado, sin reescribir el benchmark de 30 s.

Los pilotos guardan estados cada 0,05 s para el post-proceso energético: se informa un máximo **muestreado**, no una garantía de máximo continuo. Cada corrida principal controla también energía inicial y final. Los umbrales de error y el margen son decisiones locales, no exigencias cuantitativas de la consigna.

## Observables

El motor sigue generando solo estado. El estado final conserva first_contact_step por partícula; Python reconstruye Fu(t), t90 y censura a resolución h. Se reconstruyen curvas de Fu(t) en una grilla de consulta de 0,1 s, que no cambia la resolución de los tiempos de cruce.

Cada t90 se obtiene por realización antes de calcular medias y desvíos entre las cinco realizaciones de cada (N,x0) [COR03]. Las medias ordinarias y barras de desvío estándar solo se informan si todas las corridas del grupo alcanzan 0,9. Si hay censura, se registra la cantidad de corridas incompletas y Fu(100 s), y se informa una cota inferior de la media, sin reemplazar tiempos desconocidos por 100 s. Las curvas típicas corresponden a x0={r;0,255;R−r}; se promedian fracciones entre realizaciones y las bandas representan desvíos estándar, no intervalos de confianza.

Se busca la menor media entre posiciones muestreadas completas. No se presenta ese punto como óptimo exacto ni se usa el solapamiento/no solapamiento de barras de desvío estándar como prueba de significancia. La comparación N=20 frente a N=100 permite discutir sensibilidad a densidad; el motor no registra frecuencias de colisión, por lo que no se afirmará haber medido directamente esa frecuencia.

## Validación y entrega de resultados

El ejecutor guarda checkpoints por realización con huellas de configuración, binario y fuentes, valida trayectorias completas y permite reanudar sin repetir corridas válidas. Se prueban reconstrucción de Fu y cruces exactos, normalización, desvío muestral y tratamiento de censura.

Se generan figuras estáticas de Fu(t) y t90 frente a posición, datos por realización, resúmenes y manifiesto. Una animación independiente del sistema físico con tres posiciones típicas se genera desde trayectorias guardadas; no se animan gráficos temporales. Son artefactos de revisión local, no una presentación independiente [COR03] [TP04, p. 1].
