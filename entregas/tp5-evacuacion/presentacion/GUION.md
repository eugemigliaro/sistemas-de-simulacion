# Guion oral del TP5

Duración estimada: **20:32** sin el apéndice. Por pedido de la cátedra (consulta del 06/11), las diapositivas tienen escrita toda la información crucial: si no llegamos a presentar todo, no se pierde nada. Lo que sigue es lo que se dice; no hace falta repetir los números que están en la diapositiva. Las animaciones corren embebidas en el PPTX. Cada integrante tiene que poder presentar cualquier parte y responder sobre todo el trabajo, y nadie agrega nada a lo que acaba de decir otro [GPRES, p. 3].

| Parte | Integrante | Diapositivas | Tiempo |
|---|---|---|---|
| Sistema, modelo, EDMD y criterio del híbrido | Eugenio | 1 a 11 | 6:23 |
| Híbrido, simulaciones, validaciones y animaciones de a | Francisco | 12 a 25 | 7:06 |
| Puntos b a d, atascos, recuperación de v_d y conclusiones | Franco | 26 a 38 | 7:03 |
| Apéndice (solo si preguntan) | cualquiera | 39 a 42 | — |

## Eugenio — diapositivas 1 a 11 — 6:23

### 1. Portada — 0:20

Buenas tardes. Somos Eugenio Migliaro, Francisco Costa y Franco Branda, del grupo 07. Elegimos el problema 2: simular la evacuación de una sala con el Social Force Model sin fuerza social, combinando dinámica molecular por eventos y por paso temporal.

### 2. Introducción — 0:03

Empecemos por el sistema.

### 3. Evacuación por una puerta angosta — 0:40

Una sala de 50 metros con una puerta de 80 centímetros. Usamos 200 agentes en lugar de 500, como nos indicó la cátedra, para que terminen más corridas. Arrancan al azar y quieren salir a 1,5 metros por segundo. Lejos de la puerta van en línea recta, que es el terreno del EDMD; en el cuello de botella los contactos son continuos y conviene paso temporal. La idea es resolver cada agente con el esquema que le conviene sin cambiar la física.

### 4. Social Force Model sin fuerza social — 0:50

El término de deseo relaja la velocidad hacia la deseada en un tiempo tau. Solo hay fuerzas si dos agentes se superponen: un resorte normal y una fricción tangencial proporcional a la superposición. Sin fuerza social, nadie reacciona hasta tocarse, así que un agente libre y relajado va en línea recta. La masa proporcional al área es un apartamiento nuestro, que la cátedra aceptó.

### 5. Implementación — 0:03

Veamos la implementación.

### 6. TSDMD: Beeman predictor-corrector — 0:35

Como la fuerza depende de la velocidad, usamos Beeman predictor-corrector: se predice la velocidad, se calcula la aceleración y se corrige. Los contactos se buscan con celdas, y el paso de 2 milisegundos sale del test de convergencia que mostramos después.

### 7. EDMD puro: discos duros entre eventos — 0:35

En EDMD puro los agentes son discos duros que van en línea recta entre eventos: choques, cruces de celda, cruce de la puerta, retiro y patadas. Hay que diseñar dos cosas: el choque instantáneo equivalente al contacto del SFM, y cómo vuelve el agente a su velocidad deseada.

### 8. Choque en EDMD: velocidad relativa antes y después — 0:50

El dibujo muestra la velocidad relativa en la base normal y tangencial del contacto. La componente normal se refleja: el choque es elástico. La tangencial se multiplica por e sub t, que depende de la velocidad normal: cuanto más fuerte el choque, más se frena el deslizamiento. El cambio se reparte con las masas para conservar el momento, y contra una pared es la misma regla con masa infinita.

### 9. Choque en EDMD: de dónde sale la regla — 0:50

La regla sale de integrar un contacto aislado del SFM. El resorte normal no tiene amortiguamiento, así que después de medio período la normal sale invertida. La fricción frena la tangencial a una tasa proporcional a la superposición; integrando durante el contacto, el área bajo xi da justo dos veces mu por la velocidad normal sobre k, y la masa reducida se cancela. Supone contactos de a dos y que la normal no gira; lo validamos en Resultados.

### 10. EDMD: recuperar v_d después del choque — 0:47

En naranja, cómo recupera la velocidad el SFM; en azul, nuestras patadas: cada delta aplicamos la relajación exacta del SFM durante ese intervalo y entre patadas las trayectorias son rectas, así que los choques siguen siendo una cuadrática. La alternativa es la relajación analítica, con la trayectoria exponencial exacta, pero entonces los choques ya no son una cuadrática y hay que buscarlos con un avance conservador. Las comparamos al final.

### 11. Híbrido (1): un esquema por agente — 0:50

Cada agente está en un esquema. Pasa de EDMD a TSDMD si puede tener un contacto en menos de T estrella: contra agentes EDMD y paredes el tiempo es exacto; contra agentes TSDMD usamos una cota de la rapidez. Vuelve a EDMD solo si está aislado, relajado y sin contacto posible en el doble de T estrella, para evitar idas y vueltas. T estrella es el parámetro principal.

## Francisco — diapositivas 12 a 25 — 7:06

### 12. Híbrido (2): la grilla de delta t es el reloj maestro — 0:40

Los dos esquemas comparten el reloj de la grilla. En cada intervalo se procesan en orden los eventos EDMD, después un paso de Beeman de los TSDMD y, al final, las revisiones y los cambios de esquema. Los agentes EDMD no se integran: su posición es una recta que se evalúa cuando hace falta.

### 13. Híbrido (3): no perder contactos en el pase — 0:50

El dibujo muestra el peor caso: el agente TSDMD viene a la velocidad máxima hacia el EDMD. El tiempo seguro es la distancia libre sobre la suma de las rapideces. Revisamos la cota en la grilla y, con T estrella mayor o igual que delta t, el pase siempre ocurre antes de cualquier contacto posible: todo contacto lo resuelve el SFM. Verificamos la cota en cada paso y nunca se violó.

### 14. Híbrido (4): choques, recuperación y cota del ahorro — 0:35

En el híbrido no hay choques instantáneos: todos los contactos son del SFM, y la recuperación de v_d la hace el término de deseo. Relajar en forma analítica ahorraría menos del 1 % de los pasos, así que no lo implementamos. Y hay una cota: el híbrido solo ahorra el vuelo libre, que es menos del 10 % del tiempo-agente.

### 15. Arquitectura del motor — 0:25

El motor está en C++, con un módulo por esquema. Solo escribe estado; los observables y las animaciones se calculan aparte, en Python. El híbrido con T estrella enorme da exactamente las mismas salidas que TSDMD.

### 16. Simulaciones — 0:03

Pasemos a las simulaciones.

### 17. Estudios realizados — 0:40

Usamos 200 agentes en todo, salvo en el test del paso temporal, donde N no influye, y en el punto d, que barre N. Todas las variantes de un estudio usan las mismas condiciones iniciales, y cortamos una corrida si pasan 300 segundos sin salidas.

### 18. Observables — 0:40

El observable primario es la curva de población. De ella salen el tiempo de evacuación y el caudal, que promediamos sobre las corridas que terminan, y la fracción de corridas trabadas, con su intervalo de confianza. El tiempo de ejecución lo medimos de las que terminan, y como complemento el costo por segundo simulado de todas.

### 19. Resultados — 0:03

Vamos a los resultados.

### 20. Validación de la regla de choque — 0:40

Simulamos un choque aislado con el SFM blando y un paso muy chico, y lo comparamos con la regla de disco duro. La tangencial coincide en todo el rango; la normal solo pierde hasta un 5 % en los choques rasantes.

### 21. Paso temporal — 0:40

A la izquierda, el error del choque más exigente, el de los dos agentes más livianos: con 2 milisegundos es menor al 0,1 %. A la derecha, el caudal de la evacuación completa no cambia entre medio milisegundo y 2. Usamos 2 milisegundos.

### 22. (a) TSDMD puro — 0:25

TSDMD puro, con el color según la rapidez: se forma un semicírculo frente a la puerta que se va achicando a medida que salen.

### 23. (a) EDMD puro — 0:30

EDMD puro: el tapón se traba al principio y nadie más sale. Pasó en 29 de 30 corridas.

### 24. (a) Híbrido — 0:25

El híbrido, con los agentes EDMD en azul y los TSDMD en naranja: lejos de la puerta van por eventos, y los que se acercan a otro pasan a paso temporal antes de tocarlo.

### 25. (a) Agentes en cada esquema del híbrido — 0:30

En promedio, todos arrancan en EDMD y en unos 30 segundos ya no queda ninguno: después, el tapón es todo TSDMD.

## Franco — diapositivas 26 a 38 — 7:03

### 26. (b) Curvas de población — 0:30

TSDMD y el híbrido se superponen; las punteadas son las corridas trabadas. EDMD puro se corta casi siempre al principio.

### 27. (b) Tiempo de evacuación y atascos — 0:35

Entre TSDMD y el híbrido no hay diferencias fuera de las barras, ni en el tiempo de evacuación ni en la fracción de trabadas: el híbrido no cambia la física. EDMD puro se traba casi siempre.

### 28. Atascos permanentes — 0:30

Un atasco: dos agentes apoyados en la pared sostienen un arco quieto. La fricción del SFM es viscosa, así que en reposo no actúa, y el modelo no tiene fluctuaciones que lo rompan.

### 29. Atascos: por qué a veces sí y a veces no — 0:40

Nuestra hipótesis es la compresión: con la sala llena, la presión de la multitud comprime los contactos y los agentes se cuelan por la puerta; cuando quedan pocos, el arco aguanta. Lo probamos con un k diez veces mayor, o sea con menos compresión: las tres semillas que evacuaban se trabaron al principio, como los discos duros del EDMD. Por eso EDMD puro no sirve para este sistema: probamos además una regla con un núcleo duro más chico y tampoco alcanzó; está en el apéndice.

### 30. (c) Tiempo de ejecución en función de T estrella — 0:40

Los tiempos de c y d son todos de la misma computadora, una Apple M5 Pro. A la izquierda, el tiempo de ejecución de las corridas que terminan; a la derecha, el costo por segundo simulado de todas, con EDMD puro arriba. Con cualquier T estrella, el híbrido tarda lo mismo que TSDMD dentro de las barras: alrededor de 1,2 segundos.

### 31. (c) Tiempo de evacuación en función de T estrella — 0:25

Si el pase no pierde contactos, el tiempo de evacuación no depende de T estrella, y así es: todos quedan dentro de la banda de TSDMD.

### 32. (c) Comparación con TSDMD semilla por semilla — 0:40

Como las variantes comparten condiciones iniciales, comparamos cada corrida con el TSDMD de su misma semilla. Con T estrella de 1 segundo nadie llega a EDMD: las salidas son idénticas y el costo también. Con T estrella más chicos, el híbrido sale en promedio un 2,4 % más barato; con T estrella de 0,05 la diferencia está a más de dos errores estándar. Es lo que permite la cota: el vuelo libre es un 7 % del tiempo-agente.

### 33. (d) Tiempo de ejecución en función de N — 0:30

A la izquierda, densidad inicial constante; a la derecha, la sala de 50 metros. TSDMD y el híbrido se superponen en todo el rango; EDMD puro solo termina con 100 agentes.

### 34. (d) Costo por segundo simulado en función de N — 0:30

El costo por segundo simulado de TSDMD y del híbrido crece casi linealmente con N, gracias a las celdas; el de EDMD puro crece casi como N al cuadrado, porque el tapón concentra los choques.

### 35. Recuperación de v_d en EDMD puro — 0:45

A la izquierda, el costo en los primeros 30 segundos: la relajación analítica cuesta unas 200 veces más que las patadas y no llega a terminar ninguna corrida completa. A la derecha, con patadas casi todas las corridas se traban, como en el punto a. Conviene usar patadas en EDMD puro; en el híbrido, la recuperación la hace el SFM.

### 36. Conclusiones — 0:03

Para cerrar.

### 37. Conclusiones — 0:50

El SFM sin fuerza social a veces se traba en esta puerta, y la compresión de los contactos explica cuándo. El híbrido reproduce al TSDMD sin perder contactos. EDMD puro se traba casi siempre, también con la regla alternativa: no sirve para este sistema. El ahorro del híbrido está acotado por el vuelo libre: con 200 agentes es de un 2 o 3 %, mientras que EDMD puro cuesta casi 8 veces más que TSDMD.

### 38. Declaración de uso de IA — 0:25

Usamos Claude Code con Claude Opus 5.5 para el código, las corridas, los gráficos y el borrador de la presentación. Las decisiones las tomamos nosotros, y listamos las veces en que no seguimos la recomendación del agente.

## Apéndice — diapositivas 39 a 42 (solo si preguntan)

### 40. EDMD con núcleo duro reducido

Probamos chocar a una distancia menor, restando la compresión media del tapón de TSDMD. Mejoró poco: se siguió trabando casi siempre.

### 41. Fluctuación en contacto

Una fuerza aleatoria sobre los agentes en contacto no cambió la fracción de trabadas.

### 42. Segundo target

Ningún target común afuera de la puerta cambió el tiempo de evacuación: el cuello de botella está adentro.
