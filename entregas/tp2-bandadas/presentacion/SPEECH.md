# Guion oral del TP2

Duración objetivo: **13 minutos**, incluyendo aproximadamente 30 segundos de animaciones. La distribución está balanceada entre los tres integrantes y sigue el orden pedido por la consigna: animación característica, evolución temporal y observable estacionario contra el parámetro de entrada [TP02, pp. 1-2]. Todos deberían poder presentar el guion completo y responder sobre cualquier sección [GPRES, p. 3].

## Eugenio - diapositivas 1 a 8 - 4:15

### 1. Portada - 0:20

Buenas tardes. Somos Eugenio Migliaro, Francisco Costa y Franco Branda, del grupo 7. En este trabajo estudiamos la transición al orden colectivo en bandadas autopropulsadas. Comparamos el modelo estándar de Vicsek con una variante tipo votante y analizamos cómo responden al ruido y a la densidad.

### 2. Introducción - 0:05

Primero vamos a presentar el sistema real y las reglas que modelamos.

### 3. Sistema real - 0:40

Una bandada es un ejemplo de comportamiento colectivo emergente: no hay un líder que determine el movimiento global, sino agentes que se autopropulsan y sólo interactúan con vecinos cercanos. A escala microscópica tenemos decisiones locales; a escala macroscópica puede aparecer un movimiento coordinado. En el modelo, el ruido compite con esa tendencia al alineamiento. La pregunta central del trabajo es qué cambia cuando cada agente usa toda la información de su vecindario o cuando copia solamente a uno de sus vecinos.

### 4. Dinámica común - 0:50

Los dos modelos comparten la misma dinámica espacial. Cada partícula tiene una posición, una orientación y una rapidez constante. Durante un paso, la posición avanza usando la orientación del estado corriente. En paralelo se calcula la orientación del paso siguiente como una dirección de interacción, que llamamos theta mayúscula, más un ruido angular.

Normalizamos el ruido con eta entre cero y uno. La perturbación se sortea uniformemente entre menos eta por pi y más eta por pi. Entonces, eta igual a cero representa ausencia de ruido y eta igual a uno cubre todo el rango angular. La única diferencia entre los modelos es cómo se obtiene la dirección de interacción.

### 5. Reglas de interacción - 0:55

En Vicsek, cada partícula calcula el promedio vectorial de las orientaciones de todas las partículas de su vecindario. Usamos atan2 sobre las sumas de senos y cosenos para obtener el ángulo sin ambigüedad de cuadrante.

En el modelo del votante no se promedia. Cada partícula elige uniformemente una sola partícula del vecindario y copia su orientación. En ambos casos el vecindario incluye a la propia partícula. Por lo tanto, la dinámica espacial y el ruido son iguales; lo que cambia es la cantidad de información local usada para decidir la dirección siguiente.

### 6. Implementación - 0:05

Con esas reglas construimos un único motor capaz de ejecutar ambos modelos.

### 7. Modelo computacional - 0:45

El estado contiene la posición y la orientación de cada partícula, además del generador aleatorio asociado a la realización. Los vecindarios se calculan con el Cell Index Method bajo condiciones periódicas. La actualización es sincrónica: ninguna partícula puede leer un valor ya actualizado de otra partícula. Los observables se calculan sobre el mismo estado de la simulación y cada semilla permite reproducir exactamente una realización.

### 8. Paso sincrónico - 0:55

En cada paso construimos el CIM con las posiciones actuales y medimos la polarización y la componente gigante. Después calculamos todas las orientaciones nuevas y sus ruidos, pero todavía sin reemplazar el estado anterior. Las posiciones avanzan con la orientación corriente, se aplica el contorno periódico y recién al final se intercambia el estado completo.

Validamos tres aspectos: los vecinos obtenidos con CIM coincidieron con fuerza bruta; un estado inicialmente alineado y sin ruido mantuvo polarización uno; y una misma semilla reprodujo los resultados. Con el modelo computacional definido, Francisco va a explicar cómo configuramos las simulaciones y los resultados para las densidades principales.

## Francisco - diapositivas 9 a 11 - 4:25

### 9. Simulaciones - 0:05

Pasemos entonces al protocolo experimental.

### 10. Caja periódica y parámetros - 0:45

La caja tiene lado diez y fija la escala espacial del estudio. El contorno es periódico: una partícula que sale por un lado vuelve a entrar por el opuesto. Usamos radio de interacción uno, rapidez cero coma cero tres y paso temporal uno. Para el CIM dividimos cada lado en nueve celdas. Cada simulación dura diez mil pasos y descartamos los primeros cuatro mil como transitorio. Para cada combinación de modelo, densidad y ruido ejecutamos diez realizaciones independientes.

### 11. Observables y promediado - 0:50

Medimos dos propiedades distintas. La polarización, ve sub a, es el módulo de la suma de los versores velocidad dividido por la cantidad de partículas. Vale uno si todas se mueven en la misma dirección y queda cerca de cero en un estado desordenado.

El segundo observable es ese: la fracción de partículas que pertenece a la componente conexa más grande del grafo de vecinos. Para obtener un escalar estacionario, primero promediamos cada realización desde t cero igual a cuatro mil hasta el final. Después promediamos las diez realizaciones. Las barras de error representan la desviación estándar entre realizaciones, no el error de ajuste ni fluctuaciones instantáneas.

## Franco diapositivas 12 a 18
### 12. Resultados - 0:05

Ahora mostramos los resultados en el orden indicado por la consigna.

### 13. Fotogramas representativos - 0:45

[Reproducir aproximadamente 10 segundos de cada animación.]

Estas dos animaciones usan la misma densidad, el mismo ruido y el mismo instante. El color representa la orientación de cada velocidad. En Vicsek se observa una dirección dominante y un valor instantáneo de polarización alto. En el votante, para el mismo eta igual a cero coma veinticinco, las orientaciones están mucho más dispersas y la polarización es baja. El fotograma sirve como evidencia visual inicial; ahora cuantificamos esa diferencia.

### 14. Evolución temporal - 0:50

Estas series muestran la polarización para densidad cuatro. La línea vertical marca el comienzo del intervalo estacionario usado para promediar. Sin ruido, ambos modelos llegan al estado alineado. En Vicsek, eta igual a cero coma cinco mantiene una polarización intermedia, aunque con caídas prolongadas. En el votante, un ruido de sólo cero coma cero cinco ya genera fluctuaciones fuertes, y con cero coma veinticinco la polarización permanece baja. Esto justifica tanto el descarte inicial como el uso de un intervalo largo de seis mil pasos.

### 15. Orden frente al ruido - 0:55

- Al promediar las diez realizaciones aparece la diferencia principal. Las curvas continuas de Vicsek pierden el orden en valores de ruido mucho mayores que las curvas punteadas del votante.
- Para resumirlo calculamos eta un medio, el ruido donde la polarización cruza cero coma cinco. Según la densidad, Vicsek alcanza valores entre cero coma cuarenta y siete y cero coma cincuenta y cinco; el votante, entre cero coma cero treinta y cinco y cero coma cero sesenta y uno. La razón entre ambos va de siete coma siete a quince coma nueve. 
- Además, al aumentar la densidad Vicsek resiste más ruido, mientras que el votante resiste menos.
lo que podemos comentar aca que es interesante es que al aumentar la densidad el visek aguanta mas porque posee mas informacion y logra promediar mejor mientras que en el votante es al revez resiste menos y disminuye mas rapido la polarizacion pues aumenta mas el randomess por cada particula la probabilidad de que tomen la misma direccion es mas baja.

### 16. Efecto de la densidad - 0:35

- Para Vicsek con eta igual a cero coma cinco, la densidad también modifica las fluctuaciones temporales. 
- En densidad dos aparecen las caídas más profundas de polarización. 
- Esas caídas coinciden temporalmente con reducciones de la componente gigante lo que tiene sentido porque, cuando el sistema pierde conectividad, se forman grupos que dejan de intercambiar información de orientación y pueden moverse en direcciones distintas.
- En densidades cuatro y ocho, ambos observables son más estables.

### 17. Conectividad en densidades principales - 0:35

Sin embargo, al promediar en las densidades pedidas, la componente gigante permanece por encima de cero coma nueve para ambos modelos y para todo el rango de ruido. Entonces la gran diferencia de polarización entre Vicsek y votante no puede atribuirse simplemente a que la red se desconecte. Para hacer informativo el análisis de conectividad estudiamos también densidades menores. Franco presenta esa parte y el cierre.

## Negro - diapositivas 18 a 24 - 4:20

### 18. Baja densidad - 0:45

[Reproducir aproximadamente 10 segundos de la animación.]

En este caso usamos sólo treinta y dos partículas, que corresponden a una densidad real de cero coma treinta y dos. La animación permite ver grupos espacialmente separados. Mientras permanecen desconectados, esos grupos no intercambian orientación. Este régimen amplía el estudio solicitado para el observable S y permite analizar valores de conectividad que no están concentrados cerca de uno.

### 19. Fragmentación temporal - 0:50

Para Vicsek, con eta igual a cero coma veinticinco, mostramos treinta y dos, dieciséis y once partículas. La polarización fluctúa con fuerza y la componente gigante cambia de forma escalonada, porque una unión o separación involucra una fracción apreciable del sistema. Ambas magnitudes varían en escalas temporales comparables. La línea punteada vuelve a indicar el mismo inicio del promedio estacionario, t cero igual a cuatro mil.

### 20. Conectividad en baja densidad - 0:45

Al promediar las realizaciones, el observable S deja de estar cerca de uno y recorre una parte amplia de su rango. Para ambos modelos disminuye al aumentar el ruido y al reducir la cantidad de partículas. Además, para un mismo tamaño y un mismo ruido, el votante presenta en general una componente gigante menor que Vicsek. Las barras muestran nuevamente el desvío entre las diez realizaciones.

### 21. Orden y conectividad - 0:50

Acá relacionamos directamente los dos observables, como pide la consigna. A la izquierda están las densidades principales: ese cambia poco, aunque la polarización recorre casi todo su rango. Esto confirma que, en ese régimen, orden y conectividad pueden desacoplarse.

A la derecha están los sistemas de baja densidad. Allí sí aparece una asociación clara: los puntos con una componente conectada mayor también presentan mayor polarización media. No afirmamos causalidad a partir de esta figura; mostramos la relación observada entre ambos promedios.

### 22. Desempeño del CIM - 0:45

Finalmente comparamos los tiempos del Cell Index Method con mediciones del TP1 para cantidades de partículas semejantes. El tiempo total crece con N en todos los casos. Para separar parte de las diferencias de carga, también calculamos el costo por evaluación de distancia: en el TP2 se mantuvo entre dieciséis y veinte nanosegundos, frente a treinta y cinco a cuarenta y cuatro en el TP1. La comparación es orientativa, porque la geometría y el trabajo realizado por paso no son idénticos; no la interpretamos como un factor universal de aceleración.

### 23. Conclusiones - 0:05

Con esto llegamos a las conclusiones respaldadas por los resultados mostrados.

### 24. Conclusiones - 1:05

Primero, Vicsek toleró entre siete coma siete y quince coma nueve veces más ruido que el modelo del votante, según el criterio de polarización cero coma cinco. Segundo, la densidad produjo tendencias opuestas: aumentó la resistencia al ruido de Vicsek y redujo la del votante.

Tercero, para las densidades dos, cuatro y ocho, la componente gigante permaneció por encima de cero coma nueve. Por lo tanto, en ese rango la pérdida de orden puede ocurrir sin una desconexión global de la red. En cambio, al reducir la densidad, la conectividad recorrió un rango amplio y quedó asociada al orden promedio.

Por último, el CIM sostuvo un costo de dieciséis a veinte nanosegundos por evaluación de distancia en este sistema, con la salvedad de que la comparación con el TP1 se hizo bajo geometrías diferentes.

En síntesis, cambiar una sola regla local, promediar a todos los vecinos o copiar a uno, produjo respuestas colectivas muy distintas frente al ruido y la densidad.

## Orden para responder preguntas

1. Responde primero quien presentó el tema preguntado.
2. Si necesita ayuda, hace una pausa y cede explícitamente la palabra.
3. Evitar completar o corregir al compañero mientras está respondiendo.

Reparto sugerido:

- Eugenio: modelo, actualización sincrónica y validaciones.
- Francisco: protocolo, promediado y resultados de densidades principales.
- Franco: baja densidad, relación entre observables, CIM y conclusiones.

Todos deben poder responder por qué se eligió $t_0=4000$, qué significan las barras de error, cómo se define un vecino bajo periodicidad y por qué la comparación temporal con TP1 es sólo orientativa.
