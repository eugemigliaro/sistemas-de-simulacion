# Guion oral del TP2

Duración objetivo: **13 minutos**, incluyendo aproximadamente 30 segundos de animaciones. La distribución está balanceada entre los tres integrantes y sigue el orden pedido por la consigna: animación característica, evolución temporal y observable estacionario contra el parámetro de entrada [TP02, pp. 1-2]. Todos deberían poder presentar el guion completo y responder sobre cualquier sección [GPRES, p. 3].

## Eugenio - diapositivas 1 a 9 - 4:40

### 1. Portada - 0:20

Buenas tardes. Somos Eugenio Migliaro, Francisco Costa y Franco Branda, del grupo 07. En este trabajo estudiamos la transición al orden colectivo en bandadas autopropulsadas. Comparamos el modelo estándar de Vicsek con una variante tipo votante y analizamos cómo responden al ruido y a la densidad.

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

### 7. Arquitectura del motor - 0:50

La arquitectura se organiza alrededor del estado del sistema, que contiene el tiempo y las partículas con su posición y orientación. El coordinador ejecuta el ciclo completo. Primero invoca el Cell Index Method, que transforma las posiciones en una lista de relaciones entre vecinos. Esa misma lista alimenta dos componentes: el cálculo de observables y la dinámica. Los observables obtienen la polarización a partir del estado y la componente gigante a partir de la red de vecinos. La dinámica aplica la regla de Vicsek o del votante y construye el estado siguiente. Tanto el CIM como la actualización usan el servicio de geometría periódica para calcular distancias o envolver posiciones. De esta manera, sólo la dinámica modifica el estado y el coordinador controla el orden de las operaciones.

### 8. Diagrama de clases (UML) - 0:25

Este diagrama muestra la misma arquitectura desde el punto de vista del código. Arriba, el paquete Modelo agrupa los datos: el estado del sistema contiene sus partículas, y la configuración de dinámica selecciona el modelo. Abajo, el paquete Motor agrupa los módulos de funciones: el coordinador invoca vecinos, dinámica y observables; tanto vecinos como dinámica dependen del módulo de geometría. No hay clases con estado propio ni herencia: cada módulo opera sobre el modelo de datos que se muestra arriba.

### 9. Algoritmo de simulación - 0:50

El pseudocódigo reproduce ese recorrido. Inicializamos el estado y el generador con una semilla. En cada paso construimos los vecinos con el CIM y medimos ve sub a y ese sobre el estado corriente. Si todavía quedan pasos, creamos una copia para el estado siguiente. Para cada partícula elegimos la dirección base con la regla configurada: promedio local para Vicsek o copia de un vecino para el votante. La posición se actualiza usando el ángulo corriente y se aplica el contorno periódico; el nuevo ángulo resulta de sumar el ruido a la dirección base. Sólo después de recorrer todas las partículas reemplazamos el estado, garantizando la sincronía.

Validamos que el CIM coincidiera con fuerza bruta, que un estado alineado sin ruido mantuviera polarización uno y que cada semilla fuera reproducible. Con el modelo computacional definido, Francisco va a explicar cómo configuramos las simulaciones y los resultados para las densidades principales.

## Francisco - diapositivas 10 a 13 - 4:50

### 10. Simulaciones - 0:05

Pasemos entonces al protocolo experimental.

### 11. Flujo de trabajo del proyecto - 0:25

Antes de los parámetros, así se conecta todo el proyecto. El usuario dispara el barrido de experimentos, que ejecuta el motor en C++ una vez por combinación de parámetros; el motor escribe los datos crudos de cada corrida. Esos archivos alimentan dos caminos: el análisis estadístico, que produce los datos ya promediados, y el graficado, que además lee directamente los datos crudos para las animaciones. De ahí salen las figuras y animaciones que vamos a mostrar en Resultados.

### 12. Caja periódica y parámetros - 0:45

La caja tiene lado diez y fija la escala espacial del estudio. El contorno es periódico: una partícula que sale por un lado vuelve a entrar por el opuesto. Usamos radio de interacción uno, rapidez cero coma cero tres y paso temporal uno. Para el CIM dividimos cada lado en nueve celdas. Cada simulación dura diez mil pasos y descartamos los primeros cuatro mil como transitorio. Para cada combinación de modelo, densidad y ruido ejecutamos diez realizaciones independientes.

### 13. Observables y promediado - 0:50

Medimos dos propiedades distintas. La polarización, ve sub a, es el módulo de la suma de los versores velocidad dividido por la cantidad de partículas. Vale uno si todas se mueven en la misma dirección y queda cerca de cero en un estado desordenado.

El segundo observable es ese: la fracción de partículas que pertenece a la componente conexa más grande del grafo de vecinos. Para obtener un escalar estacionario, primero promediamos cada realización desde t cero igual a cuatro mil hasta el final. Después promediamos las diez realizaciones. Las barras de error representan la desviación estándar entre realizaciones, no el error de ajuste ni fluctuaciones instantáneas.

## Franco diapositivas 14 a 20
### 14. Resultados - 0:05

Ahora mostramos los resultados en el orden indicado por la consigna.

### 15. Fotogramas representativos - 0:45

[Reproducir aproximadamente 10 segundos de cada animación.]

Estas dos animaciones usan la misma densidad, el mismo ruido y el mismo instante. El color representa la orientación de cada velocidad. En Vicsek se observa una dirección dominante y un valor instantáneo de polarización alto. En el votante, para el mismo eta igual a cero coma veinticinco, las orientaciones están mucho más dispersas y la polarización es baja. El fotograma sirve como evidencia visual inicial; ahora cuantificamos esa diferencia.

### 16. Evolución temporal - 0:50

Estas series muestran la polarización para densidad cuatro. La línea vertical marca el comienzo del intervalo estacionario usado para promediar. Sin ruido, ambos modelos llegan al estado alineado. En Vicsek, eta igual a cero coma cinco mantiene una polarización intermedia, aunque con caídas prolongadas. En el votante, un ruido de sólo cero coma cero cinco ya genera fluctuaciones fuertes, y con cero coma veinticinco la polarización permanece baja. Esto justifica tanto el descarte inicial como el uso de un intervalo largo de seis mil pasos.

### 17. Orden frente al ruido - 0:55

- Al promediar las diez realizaciones aparece la diferencia principal. Las curvas continuas de Vicsek pierden el orden en valores de ruido mucho mayores que las curvas punteadas del votante.
- Para resumirlo calculamos eta un medio, el ruido donde la polarización cruza cero coma cinco. Según la densidad, Vicsek alcanza valores entre cero coma cuarenta y siete y cero coma cincuenta y cinco; el votante, entre cero coma cero treinta y cinco y cero coma cero sesenta y uno. La razón entre ambos va de siete coma siete a quince coma nueve. 
- Además, al aumentar la densidad Vicsek resiste más ruido, mientras que el votante resiste menos.
lo que podemos comentar aca que es interesante es que al aumentar la densidad el visek aguanta mas porque posee mas informacion y logra promediar mejor mientras que en el votante es al revez resiste menos y disminuye mas rapido la polarizacion pues aumenta mas el randomess por cada particula la probabilidad de que tomen la misma direccion es mas baja.

### 18. Efecto de la densidad - 0:35

- Para Vicsek con eta igual a cero coma cinco, la densidad también modifica las fluctuaciones temporales. 
- En densidad dos aparecen las caídas más profundas de polarización. 
- Esas caídas coinciden temporalmente con reducciones de la componente gigante lo que tiene sentido porque, cuando el sistema pierde conectividad, se forman grupos que dejan de intercambiar información de orientación y pueden moverse en direcciones distintas.
- En densidades cuatro y ocho, ambos observables son más estables.

### 19. Conectividad en densidades principales - 0:35

Sin embargo, al promediar en las densidades pedidas, la componente gigante permanece por encima de cero coma nueve para ambos modelos y para todo el rango de ruido. Entonces la gran diferencia de polarización entre Vicsek y votante no puede atribuirse simplemente a que la red se desconecte. Para hacer informativo el análisis de conectividad estudiamos también densidades menores. Franco presenta esa parte y el cierre.

## Negro - diapositivas 20 a 26 - 4:20

### 20. Baja densidad - 0:45

[Reproducir aproximadamente 10 segundos de la animación.]

En este caso usamos sólo treinta y dos partículas, que corresponden a una densidad real de cero coma treinta y dos. La animación permite ver grupos espacialmente separados. Mientras permanecen desconectados, esos grupos no intercambian orientación. Este régimen amplía el estudio solicitado para el observable S y permite analizar valores de conectividad que no están concentrados cerca de uno.

### 21. Fragmentación temporal - 0:50

Para Vicsek, con eta igual a cero coma veinticinco, mostramos treinta y dos, dieciséis y once partículas. La polarización fluctúa con fuerza y la componente gigante cambia de forma escalonada, porque una unión o separación involucra una fracción apreciable del sistema. Ambas magnitudes varían en escalas temporales comparables. La línea punteada vuelve a indicar el mismo inicio del promedio estacionario, t cero igual a cuatro mil.

### 22. Componente gigante frente al ruido - 0:45

Al promediar las realizaciones, el observable S deja de estar cerca de uno y recorre una parte amplia de su rango. Estas curvas corresponden a las densidades nominales uno sobre pi, uno sobre dos pi y uno sobre tres pi; con lado diez usamos respectivamente treinta y dos, dieciséis y once partículas. Para ambos modelos, S disminuye al aumentar el ruido y al reducir la cantidad de partículas. Además, para un mismo tamaño y un mismo ruido, el votante presenta en general una componente gigante menor que Vicsek. Las barras muestran nuevamente el desvío entre las diez realizaciones.

### 23. Orden y conectividad - 0:50

Acá relacionamos directamente los dos observables, como pide la consigna. A la izquierda están las densidades principales: ese cambia poco, aunque la polarización recorre casi todo su rango. Esto confirma que, en ese régimen, orden y conectividad pueden desacoplarse.

A la derecha están los sistemas de baja densidad. Allí sí aparece una asociación clara: los puntos con una componente conectada mayor también presentan mayor polarización media. No afirmamos causalidad a partir de esta figura; mostramos la relación observada entre ambos promedios.

### 24. Desempeño del CIM - 0:45

Finalmente comparamos los tiempos del Cell Index Method con mediciones del TP1 para cantidades de partículas semejantes. El tiempo total crece con N en todos los casos. Para separar parte de las diferencias de carga, también calculamos el costo por evaluación de distancia: en el TP2 se mantuvo entre dieciséis y veinte nanosegundos, frente a treinta y cinco a cuarenta y cuatro en el TP1. La comparación es orientativa, porque la geometría y el trabajo realizado por paso no son idénticos; no la interpretamos como un factor universal de aceleración.

### 25. Conclusiones - 0:05

Con esto llegamos a las conclusiones respaldadas por los resultados mostrados.

### 26. Conclusiones - 1:05

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
