# Guion oral del TP5

Duración estimada: **19:05** sin el apéndice. Por pedido de la cátedra, las diapositivas tienen escrita toda la información crucial: si no llegamos a presentar todo, no se pierde nada. Lo que sigue es lo que se dice; no hace falta leer los números que están en la diapositiva. Las animaciones corren embebidas en el PPTX. Cada integrante tiene que poder presentar cualquier parte y responder sobre todo el trabajo, y nadie agrega nada a lo que acaba de decir otro [GPRES, p. 3].

| Parte | Integrante | Diapositivas | Tiempo |
|---|---|---|---|
| Sistema, modelo, EDMD y criterio del híbrido | Eugenio | 1 a 11 | 5:56 |
| Resto del híbrido, simulaciones, validaciones y animaciones | Francisco | 12 a 24 | 6:21 |
| Resultados, recuperación de v_d y conclusiones | Franco | 25 a 36 | 6:48 |
| Apéndice (solo si preguntan) | cualquiera | 37 a 43 | — |

## Eugenio — diapositivas 1 a 11 — 5:56

### 1. Portada — 0:20

Buenas tardes. Somos Eugenio Migliaro, Francisco Costa y Franco Branda, del grupo 07. Elegimos el problema 2: simular la evacuación de una sala con el Social Force Model sin fuerza social, combinando dinámica molecular por eventos y por paso temporal.

### 2. Introducción — 0:03

Empecemos por el sistema.

### 3. Evacuación por una puerta angosta — 0:40

Una sala de 50 metros con una puerta de 80 centímetros. Usamos 60 agentes en lugar de 500: la cátedra nos pidió bajar N para que se note el híbrido, y elegimos 60 con un estudio que está en el apéndice. Arrancan al azar y quieren salir a 1,5 metros por segundo. Lejos de la puerta van en línea recta, que es el terreno del EDMD; en la puerta se forma una cola con contactos, y ahí conviene paso temporal. La idea es resolver cada agente con el esquema que le conviene sin cambiar la física.

### 4. Social Force Model sin fuerza social — 0:45

El término de deseo relaja la velocidad hacia la deseada en un tiempo tau. Solo hay fuerzas si dos agentes se superponen: un resorte normal y una fricción tangencial proporcional a la superposición. Sin fuerza social nadie reacciona hasta tocarse, así que un agente libre y relajado va en línea recta. La masa proporcional al área es un apartamiento nuestro, que la cátedra aceptó.

### 5. Implementación — 0:03

Veamos la implementación.

### 6. TSDMD: Beeman predictor-corrector — 0:35

Como la fuerza depende de la velocidad, usamos Beeman predictor-corrector: se predice la velocidad, se calcula la aceleración y se corrige. Los contactos se buscan con celdas, recorriendo solo las ocupadas, y el paso de 2 milisegundos sale del test de convergencia que mostramos después.

### 7. EDMD puro: discos duros entre eventos — 0:30

En EDMD puro los agentes son discos duros que van en línea recta entre eventos. Hay que diseñar dos cosas: el choque instantáneo equivalente al contacto del SFM, y cómo vuelve el agente a su velocidad deseada.

### 8. Choque en EDMD: velocidad relativa antes y después — 0:45

La velocidad relativa se descompone en la normal y la tangencial del contacto. La normal se refleja: el choque es elástico. La tangencial se multiplica por e sub t, que depende de la velocidad normal: cuanto más fuerte el choque, más se frena el deslizamiento. El cambio se reparte con las masas, y contra una pared es la misma regla con masa infinita.

### 9. Choque en EDMD: de dónde sale la regla — 0:45

La regla sale de integrar un contacto aislado del SFM. El resorte normal no tiene amortiguamiento, así que después de medio período la normal sale invertida. La fricción frena la tangencial a una tasa proporcional a la superposición; integrando durante el contacto, la masa reducida se cancela. Lo validamos en resultados.

### 10. EDMD: recuperar v_d después del choque — 0:40

Para volver a la velocidad deseada usamos patadas: cada delta aplicamos la relajación exacta del SFM, y entre patadas las trayectorias son rectas, así que los choques siguen siendo una cuadrática. La alternativa es la relajación analítica: la trayectoria exponencial exacta, con eventos de fin de relajación y de reapuntado, pero sin cuadrática para los choques. Las comparamos en resultados.

### 11. Híbrido (1): un esquema por agente — 0:50

Cada agente está en un esquema. En EDMD va en línea recta a v_d. Pasa a TSDMD si puede tener un contacto en menos de T estrella; contra agentes TSDMD, cuyo futuro no conocemos, usamos una cota de la rapidez. Vuelve a EDMD cuando queda aislado y relajado, sin contacto posible en 2 T estrella. T estrella es el parámetro principal.

## Francisco — diapositivas 12 a 24 — 6:21

### 12. Híbrido (2): la grilla de delta t es el reloj maestro — 0:40

Los dos esquemas comparten el reloj de la grilla. En cada intervalo se procesan en orden los eventos EDMD, después un paso de Beeman de los TSDMD y, al final, las revisiones y los cambios de esquema. Los agentes EDMD no se integran: su posición es una recta que se evalúa cuando hace falta.

### 13. Híbrido (3): no perder contactos en el pase — 0:45

El dibujo muestra el peor caso: el agente TSDMD viene a la velocidad máxima hacia el EDMD. El tiempo seguro es la distancia libre sobre la suma de las rapideces. Con T estrella mayor o igual que delta t, el pase siempre ocurre antes de cualquier contacto posible: todo contacto lo resuelve el SFM, y la cota nunca se violó. Al pasar a TSDMD, las aceleraciones iniciales son las del deseo, exactas porque no hay contactos.

### 14. Híbrido (4): choques, recuperación y cota del ahorro — 0:50

En el híbrido no hay choques instantáneos. Para recuperar v_d probamos dos variantes. En la principal la relaja el SFM y el agente vuelve a EDMD recién relajado. La otra es la relajación analítica, que vuelve apenas queda aislado: la implementamos porque con 20 agentes dos tercios de los pasos TSDMD eran de agentes sueltos relajándose. Con 60 agentes gana la primera. La cota del ahorro es la cola: dos tercios del tiempo-agente son TSDMD.

### 15. Arquitectura del motor — 0:25

El motor está en C++, con un módulo por esquema. Solo escribe estado; los observables y las animaciones se calculan aparte, en Python. El híbrido con T estrella enorme da exactamente las mismas salidas que TSDMD, y recorrer solo las celdas ocupadas no cambió ni un bit de las salidas.

### 16. Simulaciones — 0:03

Pasemos a las simulaciones.

### 17. Estudios realizados — 0:35

Usamos 60 agentes en todo, salvo en el test del paso temporal, en el escalamiento con N y en la elección de N. Todas las variantes de un estudio usan las mismas condiciones iniciales, y cortamos una corrida si pasan 300 segundos sin salidas.

### 18. Observables — 0:35

El observable primario es la curva de población. De ella salen el tiempo de evacuación, el caudal y la fracción de corridas trabadas. El tiempo de ejecución lo medimos de las corridas que terminan, y como complemento el costo por segundo simulado, todo en la misma computadora.

### 19. Resultados — 0:03

Vamos a los resultados.

### 20. Validación de la regla de choque — 0:35

Comparamos un choque aislado del SFM blando con la regla de disco duro. La tangencial coincide en todo el rango; la normal solo pierde hasta un 5 % en los choques rasantes.

### 21. Paso temporal — 0:35

Con 2 milisegundos, el error del choque más exigente es menor al 0,1 %, y el caudal no cambia respecto de pasos más chicos. Usamos 2 milisegundos.

### 22. Animación: TSDMD puro — 0:25

TSDMD puro, con el color según la rapidez. En la puerta se forma una cola con contactos continuos.

### 23. Animación: EDMD puro — 0:25

EDMD puro: evacúa igual que TSDMD y se traba en una proporción parecida, pero cuesta casi el doble, por los choques en la cola.

### 24. Animación: híbrido — 0:25

El híbrido, con los agentes EDMD en azul y los TSDMD en naranja: van por eventos mientras vuelan libres y pasan a paso temporal al acercarse a la cola.

## Franco — diapositivas 25 a 36 — 6:48

### 25. Agentes en cada esquema del híbrido — 0:35

Todos arrancan en EDMD y pasan a TSDMD al llegar a la cola. Casi nunca vuelven: en la cola nadie queda aislado y relajado. Desde unos 35 segundos están todos en TSDMD.

### 26. Curvas de población — 0:25

Las curvas de los tres esquemas se superponen; las punteadas son las corridas trabadas.

### 27. Tiempo de evacuación y atascos — 0:35

Los tres tardan lo mismo, y los intervalos de las corridas trabadas se superponen: los tres se traban igual. Los atascos están en el apéndice.

### 28. Tiempo de ejecución en función de T estrella — 0:45

Medimos los tiempos en una sola computadora. En lleno, la variante que relaja con el SFM; en hueco, la analítica. Las dos son más baratas que TSDMD con casi todos los T estrella, y EDMD puro es el más caro. Elegimos el T estrella de menor tiempo medio.

### 29. Tiempo de evacuación en función de T estrella — 0:25

Si el pase no pierde contactos, el tiempo de evacuación no depende de T estrella, y así es para las dos variantes.

### 30. Tiempo de ejecución: comparación con TSDMD semilla por semilla — 0:50

Comparando cada corrida con el TSDMD de su misma semilla, el híbrido cuesta el 84 % de TSDMD; si miramos solo los pares en que terminan los dos, el 71 %. El desvío es grande porque una semilla que se traba en un esquema y no en el otro rompe el pareo. La analítica cuesta más porque en la cola entra y sale de EDMD.

### 31. Tiempo de ejecución en función de N — 0:35

Con densidad constante y con la sala de 50 metros. EDMD puro solo termina con pocos agentes: con más, se traba.

### 32. Costo por segundo simulado en función de N — 0:40

Con 20 agentes el híbrido cuesta un cuarto de TSDMD, pero con 1000 cuesta casi lo mismo: el ahorro es el vuelo libre, y con muchos agentes casi todo es cola. EDMD puro es el más barato con 20 agentes, pero su costo crece muy rápido.

### 33. Recuperación de v_d en EDMD puro — 0:35

En EDMD puro, patadas y relajación analítica dan el mismo caudal que TSDMD; la analítica cuesta de 15 a 94 veces más. En EDMD puro conviene usar patadas.

### 34. Conclusiones — 0:03

Para cerrar.

### 35. Conclusiones — 0:55

Con 60 agentes el modelo se traba en casi una de cada cinco corridas, y lo que manda es la fricción relativa a la rigidez. El híbrido reproduce TSDMD sin perder contactos y cuesta el 84 % de TSDMD; con 60 agentes es el más barato de los tres. EDMD puro evacúa igual, pero cuesta casi el doble y con más agentes se traba siempre.

### 36. Declaración de uso de IA — 0:25

Usamos Claude Code con Claude Opus 5.5 para el código, las corridas, los gráficos y el borrador de la presentación. Las decisiones las tomamos nosotros, y listamos las veces en que no seguimos la recomendación del agente.

## Apéndice — diapositivas 37 a 43 (solo si preguntan)

### 38. Elección de N

Barrimos N de 20 a 100 en la sala de 50 metros. Solo con 60 el híbrido es más barato que los dos por más de tres errores estándar. Hasta 40, EDMD puro es más barato; con 50 y desde 70, la ventaja sobre TSDMD no es significativa, porque casi todo es cola.

### 39. Atascos con N = 60: arco

Un arco estático en la puerta: la fricción del SFM es viscosa y en reposo no actúa, y el modelo no tiene fluctuaciones.

### 40. Atascos con N = 60: rigidez y fricción

Con k diez veces mayor no se traba ninguna y evacúan en la mitad del tiempo; con k y kappa diez veces mayores se comporta igual que con los del paper. Lo que manda es kappa sobre k.

### 41. Compresión: N = 60 contra N = 200

Con 200 agentes los contactos se comprimían más y la hipótesis era que los agentes se colaban comprimidos; con 60, la compresión es chica y no explica los atascos.

### 42. Atascos con N = 200: EDMD con núcleo reducido

Con 200 agentes, chocar a una distancia menor casi no cambió nada. Con 60, EDMD no se traba más que TSDMD, así que no hizo falta.

### 43. Segundo target

Ningún target común afuera de la puerta cambió el tiempo de evacuación.
