# Guion oral del TP3

Duración objetivo: **12 minutos y 56 segundos**, con unos 4 segundos de margen sobre los 13 minutos de la consigna [TP03, p. 1]. Las dos animaciones corren embebidas en el PPTX mientras se habla: la de la mesa vacía dura 27 s y la de la elegida, 18 s. El reparto está balanceado entre los tres integrantes. Todos deberían poder presentar el guion completo y responder sobre cualquier sección [GPRES, p. 3].

## Eugenio - diapositivas 1 a 9 - 4:13

### 1. Portada - 0:20

Buenas tardes. Somos Eugenio Migliaro, Francisco Costa y Franco Branda, del grupo 07. En este trabajo simulamos un billar-metegol con dinámica molecular dirigida por eventos y buscamos la configuración de obstáculos que hace que el noventa por ciento de las partículas haga un gol lo antes posible.

### 2. Introducción - 0:05

Empecemos por el método de simulación.

### 3. Dinámica molecular dirigida por eventos - 0:40

La dinámica molecular dirigida por eventos sirve para sistemas de partículas rígidas, que solo interactúan cuando se tocan. Entre choques cada partícula sigue un movimiento rectilíneo uniforme, así que no hace falta integrar con un paso fijo: alcanza con calcular cuándo ocurre el próximo choque y saltar directamente a ese instante. El paso temporal es entonces variable. El enfoque vale cuando los choques son instantáneos, el tiempo de vuelo es mucho mayor que la duración del choque y la densidad es media o baja. Ejemplos típicos son los gases de esferas o discos rígidos y los medios granulares diluidos.

### 4. Tiempo de choque entre dos partículas - 0:45

La pieza central es el tiempo de choque entre dos partículas. Como las dos avanzan en línea recta, el contacto ocurre cuando la distancia entre sus centros es igual a la suma de los radios, sigma. Eso da una ecuación cuadrática en el tiempo. Si delta v escalar delta r es mayor o igual a cero, las partículas se alejan y no chocan. Si el discriminante d es negativo, se cruzan sin tocarse. En otro caso, el tiempo de choque es la raíz más chica de la cuadrática. Contra una pared la cuenta es más simple: la distancia a la pared, menos el radio, dividida por la velocidad perpendicular.

### 5. Choque elástico y próximo evento - 0:35

Cuando dos partículas chocan, intercambian un impulso J en la dirección que une sus centros. Su módulo depende de las masas y de la velocidad relativa proyectada sobre esa dirección. A cada velocidad se le suma o se le resta J sobre su masa. Un obstáculo fijo se trata como una partícula de masa infinita, que no se mueve. El próximo evento es el mínimo de todos los tiempos de choque: todas las partículas avanzan hasta ese instante y solo cambian las velocidades de las que chocaron.

### 6. Implementación - 0:05

Veamos cómo lo implementamos.

### 7. Arquitectura del motor - 0:30

El motor está escrito en C++. La línea de comandos lee la configuración, un módulo genera las condiciones iniciales y el motor dirigido por eventos usa los módulos de colisiones y de geometría. El motor solo escribe el estado del sistema: tiempo, posiciones, velocidades y color de cada partícula. Todo lo que calculamos después, la fracción de goles, t noventa, el desplazamiento cuadrático medio y el coeficiente de difusión, lo hace un posprocesamiento separado en Python.

### 8. Algoritmo de simulación - 0:40

En lugar de recalcular todos los choques en cada paso, los agendamos en una cola de prioridad ordenada por tiempo. En cada iteración sacamos el más próximo. Si alguna de las partículas involucradas ya chocó con otra desde que se agendó el evento, el evento quedó invalidado y se descarta: lo detectamos comparando contadores de choques. Si es válido, avanzamos todas las partículas hasta ese instante, resolvemos el choque y reagendamos solo los eventos de las partículas que participaron. Así, cada evento cuesta del orden de N en lugar de N al cuadrado.

### 9. Diagrama UML del motor - 0:33

El diagrama muestra la misma estructura desde el código. A la izquierda están los datos: el sistema contiene la mesa, N partículas y K obstáculos, y cada partícula guarda su posición, su velocidad, su estado y su contador de choques. En el centro, el módulo de simulación es dueño de la cola de eventos y modifica el sistema. A la derecha, el módulo de colisiones predice y resuelve los choques, y el de generación crea el sistema inicial. Francisco va a presentar el sistema particular que simulamos.

## Francisco - diapositivas 10 a 17 - 4:00

### 10. Simulaciones - 0:05

Pasemos al sistema que estudiamos.

### 11. Sistema particular - 0:35

La mesa mide uno coma veinte por cero coma sesenta y ocho metros. En el centro de cada pared corta hay un arco de veinte centímetros. Adentro podemos ubicar K obstáculos circulares fijos, de radio al menos igual al de las partículas. Todas las partículas arrancan frescas, en azul. La primera vez que una toca un arco, cuenta un gol y pasa a usada, en rojo. Las usadas siguen chocando, así que la cantidad de partículas y la densidad no cambian. El objetivo es encontrar la configuración que minimiza el t noventa medio.

### 12. Parámetros fijos y variables - 0:35

Las dimensiones de la mesa, el arco, el radio, la masa y la rapidez inicial de las partículas quedan fijos. Variamos cuatro cosas. Para el tiempo de ejecución, la cantidad de partículas, de diez a setecientas treinta y siete, con la mesa vacía. Con cien partículas estudiamos el radio de un disco central, entre cinco y treinta y cuatro centímetros, varias familias de salas armadas con discos y la profundidad de la sala elegida. El motor escribe el estado en cada gol y cada cierto número de eventos.

### 13. Goles y tiempo característico - 0:35

La fracción de partículas usadas, F sub u, es la cantidad acumulada de goles dividida por N. En cada realización tomamos t noventa como el primer instante en que F sub u llega a cero coma nueve, y recién después promediamos entre realizaciones. Usamos veinte realizaciones por radio del disco, veinticuatro por profundidad y cien para la comparación final entre configuraciones. Las barras de error son el error estándar. Si una corrida no llegaba al noventa por ciento, la informábamos en lugar de descartarla.

### 14. Difusión - 0:35

Para la difusión calculamos el desplazamiento cuadrático medio en función del tiempo, medido desde el estado inicial y promediado sobre todas las partículas, frescas y usadas. En la ventana difusiva crece como cuatro D t. Para ajustar barremos la pendiente candidata c, calculamos el error cuadrático E de c y tomamos el mínimo, como en la Teórica 0. Usamos diez realizaciones de ocho segundos por configuración y la misma ventana, de cero coma tres a uno coma cinco segundos, para todas.

### 15. Resultados - 0:05

Vamos a los resultados.

### 16. Tiempo de ejecución en función de N - 0:55

Primero, el tiempo de ejecución, con la mesa vacía y treinta segundos simulados. Subimos N hasta que la corrida dejó de terminar, con un corte de diez minutos. Con posiciones al azar la mesa se llena antes: cerca de cuatrocientas cuarenta y seis partículas el muestreo ya no encuentra lugar, y el motor tarda apenas unos treinta segundos. Para seguir, desde cuatrocientas cincuenta ubicamos las partículas en sitios al azar de una red triangular, que admite hasta setecientas treinta y siete. Con seiscientas setenta y cinco la corrida tarda nueve minutos y medio, y con setecientas ya no termina. A la derecha separamos los dos factores del tiempo total: arriba, los choques por partícula y por segundo, que se disparan hacia el empaquetamiento compacto; abajo, el costo de cada evento, que crece con N.

### 17. Mesa vacía: dinámica y F sub u - 0:35

*[Arranca la animación, de 27 segundos.]*

Esta es la mesa vacía con cien partículas, en tiempo real: un segundo de video es un segundo simulado. Debajo se dibuja F sub u, que crece en escalones, uno por cada gol. Al principio los goles son rápidos, porque hay muchas partículas frescas cerca de los arcos. Después se hacen más lentos: las que quedan tienen que llegar desde lejos. En esta realización, t noventa es veintidós coma siete segundos, cerca del promedio de la mesa vacía. Franco va a mostrar cómo lo mejoramos.

## Franco - diapositivas 18 a 26 - 4:43

### 18. Disco central: F sub u según el radio - 0:45

Empezamos con un disco en el centro de la mesa. Cada fila del mapa es un radio y los grises muestran la fracción de goles promedio a lo largo del tiempo. La zona naranja es donde la curva promedio ya pasó el noventa por ciento, y los puntos azules son el t noventa promedio de cada radio. A medida que el disco crece, todo se corre hacia la izquierda: t noventa baja de casi veintitrés segundos con la mesa vacía a quince coma tres con un radio de treinta y cuatro centímetros, cuando el disco toca las dos paredes largas. Como el mejor valor quedó en el borde del rango, pasamos a usar varios obstáculos.

### 19. Búsqueda de la configuración - 0:45

Con discos del radio mínimo armamos salas de distintas formas y rellenamos el resto de la mesa, para que ninguna partícula quede encerrada sin arco. Primero probamos elipses con un foco en el centro de la mesa y otro en el arco, pensando en el reflejo hacia el foco. Dieron diecinueve segundos: el foco no actúa, porque las partículas chocan entre sí cada pocos centímetros. Una pared que solo separa las dos mitades casi no ayuda. Lo que sí baja t noventa es quitar el área lejana a los arcos sin angostar la entrada. Así llegamos a las elipses separadas y a la superelipse, con trece coma seis segundos, por debajo de los quince coma seis del mejor disco.

### 20. Profundidad de la sala - 0:35

Para elegir el tamaño de la sala barrimos su profundidad, dejando fijos el ancho y la forma. Hay un óptimo plano entre veintitrés y treinta centímetros, y ahí tomamos la configuración elegida. Con salas más chicas las cien partículas quedan apretadas y chocan tanto entre sí que tardan más en salir. Con salas más grandes vuelve a aparecer área lejos del arco. Salvo la más chica, todas las salas le ganan al disco central, marcado con la línea punteada.

### 21. Configuración elegida: dinámica y F sub u - 0:30

*[Arranca la animación, de 18 segundos.]*

Esta es la configuración elegida. Son ochenta y siete discos que forman una sala superelíptica alrededor de cada arco, abierta a casi todo el ancho de la pared corta, con el centro de la mesa relleno. Cada partícula está siempre cerca de su arco. En esta realización, t noventa es trece coma seis segundos, y el promedio sobre cien realizaciones nuevas da trece coma sesenta y uno más o menos cero coma diecisiete.

### 22. Coeficiente de difusión - 0:35

A la izquierda está el desplazamiento cuadrático medio en función del tiempo. En la mesa vacía crece casi en línea recta dentro de la ventana, y el coeficiente de difusión da cero coma cero dos dos metros cuadrados por segundo. En la elegida es cuatro veces menor, porque la sala es chica y está más poblada, y la curva ya se dobla dentro de la ventana al sentir las paredes. A la derecha, el error E de c, con su mínimo en la pendiente ajustada.

### 23. Difusión y tiempo al 90 % - 0:28

Calculamos D para ciento noventa y cinco configuraciones y lo comparamos con su t noventa. La correlación cambia de signo según la familia: es negativa para las elipses de focos fijos y positiva para las demás. En conjunto es positiva, lo contrario de lo que uno esperaría: las mejores configuraciones son salas chicas y densas, donde D es bajo. D por sí solo no predice t noventa.

### 24. Conclusiones - 0:05

Para cerrar.

### 25. Conclusiones - 0:55

Primero, el tiempo de ejecución se dispara cerca del empaquetamiento compacto porque el espacio libre entre partículas tiende a cero: el tiempo entre choques se achica, avanzar el mismo tiempo simulado exige cada vez más eventos y cada evento cuesta más, porque hay que reagendar contra más partículas. Por eso la simulación por eventos rinde solo a densidad media o baja.

Segundo, como las partículas se mueven en forma difusiva, cuanto más lejos de un arco están, más tardan en llegar. El disco central funciona porque quita la zona más alejada de los arcos; una pared que solo separa las mitades casi no cambia nada.

Tercero, la superelipse lleva esa idea al límite. Su profundidad óptima equilibra el área lejana de una sala grande con la densidad de una sala chica, y baja t noventa un cuarenta por ciento.

Por último, el coeficiente de difusión no alcanza para predecir t noventa.

### 26. Gracias - 0:05

Muchas gracias. Quedamos a disposición para preguntas.

## Preguntas probables

- **¿Por qué la red triangular en el punto 1.1?** Con posiciones al azar la mesa admite como máximo ~446 partículas, y ahí el sistema todavía es un líquido: el motor tarda ~30 s y no se satura. La red permite llegar al empaquetamiento compacto, donde la frecuencia de choques diverge. Solo se usa por encima de 430 partículas y solo en ese punto; en la competencia las posiciones son al azar.
- **¿Por qué el motor ingenuo no está en el ZIP?** La consigna pide solo la versión final del motor. El ingenuo quedó en el repositorio como oráculo para validar la cola.
- **¿Cómo sabemos que las animaciones no interpolan?** El ZIP trae el código que las generó (`python -m tp3analysis.animar`). Cada cuadro del video muestra el último estado que el motor escribió en un evento anterior o igual a ese instante; no se calculan posiciones intermedias.
- **¿El foco de la elipse no ayuda nada?** No. Con la elipse fija, cambiamos el tamaño de los discos del contorno, y con eso la precisión del espejo, y `t90` no cambió (20,7, 19,9 y 20,4 s).
- **¿Cómo evitaron que queden partículas encerradas?** Rellenamos el exterior de las salas con discos, hasta que no entra ningún centro de partícula, y verificamos con un relleno por inundación que toda el área accesible tenga camino a un arco.
- **¿Por qué 100 realizaciones para la comparación final?** Elegir y medir con las mismas semillas sobreestima la mejora. La reevaluación con semillas nuevas corrigió ventajas aparentes de hasta 0,7 s.
- **¿Por qué los puntos de `t90` no caen justo sobre el borde naranja del mapa?** Son dos medidas distintas. Los puntos son el promedio de los `t90` de cada realización, que es lo que informamos. El borde es el instante en que la curva promedio de `Fu` llega a 0,9. Como `Fu` crece cada vez más lento al acercarse a 1, en el instante `⟨t90⟩` las corridas lentas quedan más por debajo de 0,9 que lo que las rápidas quedan por encima, y la curva promedio cruza 0,9 entre 0,1 y 0,9 s después.
- **¿Por qué el `D` de la elegida no es "el" coeficiente de difusión?** En salas chicas el desplazamiento cuadrático medio se curva dentro de la ventana de ajuste: es un coeficiente efectivo, que mezcla difusión y confinamiento. Mantuvimos la misma ventana para poder comparar configuraciones.
