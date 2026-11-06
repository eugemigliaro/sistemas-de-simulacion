# Guion oral del TP5

Duración estimada: **23:40**. El grupo decidió que la presentación puede superar los 13 minutos de la consigna [TP05, p. 1] para incluir los estudios extra en el cuerpo (ver `docs/recomendaciones-modificadas.md`); conviene confirmarlo en la consulta del 06/11. Las animaciones corren embebidas en el PPTX mientras se habla. Cada integrante tiene que poder presentar cualquier parte y responder sobre todo el trabajo, y nadie agrega nada a lo que acaba de decir otro [GPRES, p. 3].

| Parte | Integrante | Diapositivas | Tiempo |
|---|---|---|---|
| Sistema, modelo e implementación | Eugenio | 1 a 12 | 7:01 |
| Arquitectura, simulaciones, estudios previos y esquemas puros en a | Francisco | 13 a 26 | 8:06 |
| Híbrido en a, puntos b a d, recuperación de v_d y conclusiones | Franco | 27 a 39 | 8:33 |

## Eugenio — diapositivas 1 a 12 — 7:01

### 1. Portada — 0:20

Buenas tardes. Somos Eugenio Migliaro, Francisco Costa y Franco Branda, del grupo 07. Elegimos el problema 2: simulamos la evacuación de una sala con el Social Force Model sin fuerza social, y combinamos en una misma simulación dinámica molecular por eventos y por paso temporal.

### 2. Introducción — 0:03

Empecemos por el sistema.

### 3. Evacuación por una puerta angosta — 0:40

Hay 500 agentes en una sala cuadrada de 50 metros, con una sola puerta de 80 centímetros en el centro de una pared. Arrancan en posiciones al azar, sin superponerse, y todos quieren salir a 1,5 metros por segundo. En la misma evacuación conviven dos regímenes. Lejos de la puerta, casi todos van en línea recta sin tocar a nadie: ahí la dinámica por eventos es exacta y barata. Frente a la puerta se forma un tapón con contactos permanentes, donde conviene el paso temporal. La pregunta del trabajo es si podemos resolver a cada agente con el esquema que le corresponde, sin cambiar la física.

### 4. Social Force Model sin fuerza social — 0:50

Usamos el modelo de Helbing, Farkas y Vicsek sin la fuerza social. El primer término relaja la velocidad hacia la deseada, v_d por el versor al target, con un tiempo tau de medio segundo. Las fuerzas de contacto aparecen solo si dos agentes se superponen, o sea si xi es positivo: una fuerza normal de resorte, k por xi, y una fricción tangencial proporcional a la superposición y a la velocidad relativa tangencial. Con las paredes es igual, y los marcos de la puerta se tratan como puntos. Como no hay fuerza social, nadie reacciona a otro hasta tocarlo: un agente libre y relajado va en línea recta. Tomamos los parámetros del paper, salvo la masa: la hicimos proporcional al área, con 80 kilos para el radio medio. Es un apartamiento nuestro y lo declaramos. Adentro, cada agente apunta al punto más cercano del 60 % central de la puerta; al cruzarla, se aleja en menos y.

### 5. Implementación — 0:03

Veamos cómo lo implementamos.

### 6. TSDMD: Beeman predictor-corrector — 0:40

Las fuerzas dependen de la velocidad, por el término de deseo y por la fricción, así que usamos Beeman predictor-corrector. Se avanza la posición, se predice la velocidad, se calcula la aceleración con esa predicción y se corrige la velocidad. Después reevaluamos la aceleración con la velocidad corregida, reusando los contactos del paso. Los contactos se buscan con celdas, como en el CIM. El paso es de 2 milisegundos, elegido con el test de convergencia que vamos a mostrar. Guardamos cuadros cada delta t dos y el instante de salida de cada agente, interpolado dentro del paso.

### 7. EDMD puro: discos duros entre eventos — 0:50

En el EDMD puro los agentes son discos duros. Los eventos son los choques entre agentes, que se predicen con la cuadrática del TP3; los choques con paredes y marcos; los cruces de celda; el cruce de la puerta, donde cambia el target; el retiro a un metro, y las patadas de relajación. La regla de choque la derivamos del SFM. En un contacto aislado, el resorte normal no tiene amortiguamiento, así que la componente normal se refleja: el choque es elástico. La fricción, integrada durante el medio período del resorte, multiplica la tangencial por una exponencial de menos dos kappa por la velocidad normal sobre k. La masa reducida se cancela, así que vale para masas distintas y contra las paredes.

### 8. Recuperar v_d en EDMD — 0:40

Después de un choque, el agente tiene que volver a su velocidad deseada. Con patadas, cada delta aplicamos a todos los agentes sin relajar la relajación exacta del SFM durante ese intervalo, con el versor fijo. Entre patadas van en línea recta y los choques siguen siendo una cuadrática. La alternativa es la relajación analítica: la trayectoria exponencial exacta, con eventos propios para el fin de la relajación y para reapuntar al target. Pero entonces los choques ya no son una cuadrática y hay que buscarlos con un avance conservador, que es más caro. Las comparamos al final.

### 9. Híbrido (1): un esquema por agente — 0:50

En el híbrido, cada agente está en uno de los dos esquemas. En EDMD va relajado y en línea recta. Pasa a TSDMD si puede tener un contacto en menos de T estrella. Contra agentes EDMD y paredes ese tiempo es exacto. Contra un agente TSDMD no conocemos su futuro, así que usamos una cota: nadie va a más de dos v_d, y el tiempo seguro es la distancia libre sobre la suma de las rapideces. Vuelve a EDMD solo si está aislado, relajado y sin contacto posible en dos T estrella; esa histéresis evita pases de ida y vuelta. T estrella es el parámetro del esquema: si es enorme, todo es TSDMD; si es chico, cada agente queda en EDMD hasta el último momento. Tiene que ser al menos delta t.

### 10. Híbrido (2): la grilla de delta t es el reloj maestro — 0:45

Los dos esquemas comparten el reloj de la grilla de delta t. En cada intervalo procesamos en orden los eventos EDMD: las alertas T estrella antes de un contacto posible, los cruces de puerta y los retiros. Después damos un paso de Beeman a los agentes TSDMD y, al final del intervalo, revisamos la cota y hacemos los cambios de esquema. Los agentes EDMD no se integran: su posición es una recta que se evalúa cuando hace falta. Los TSDMD interactúan solo entre ellos y con las paredes, porque nunca hay un agente EDMD en contacto.

### 11. Híbrido (3): no perder contactos en el pase — 0:45

La revisión de la cota se hace siempre en instantes de la grilla, con las posiciones TSDMD exactas, y al menos un paso después de la anterior. Si el tiempo seguro ya es menor que T estrella, el agente pasa a TSDMD; si no, se vuelve a revisar justo antes de que pueda serlo. Con T estrella mayor o igual que delta t, el pase siempre ocurre antes de cualquier contacto posible, y el contacto lo resuelve el SFM. La cota se verifica en cada paso: en el punto a, la rapidez máxima fue 1,91 metros por segundo, sin violaciones. Al pasar a TSDMD, las aceleraciones anteriores valen cero, lo que es exacto porque iba relajado y sin contactos. Al volver a EDMD, redondeamos la velocidad a v_d por el versor.

### 12. Híbrido (4): choques y recuperación — 0:35

Por eso en el híbrido no hay choques instantáneos: todos los contactos son blandos, del SFM, y la recuperación de v_d la hace el término de deseo. Medimos si convenía agregar la relajación analítica: los agentes aislados pero sin relajar son el 0,17 % de los pasos TSDMD, así que no la implementamos. Y hay una cota para el ahorro: el 97,4 % del tiempo-agente es TSDMD, porque el tapón dura casi toda la evacuación.

## Francisco — diapositivas 13 a 26 — 8:06

### 13. Arquitectura del motor — 0:30

El motor está en C++, separado en módulos: la sala y los parámetros, el estado inicial, las fuerzas con celdas y Beeman, la predicción de eventos y la regla de choque, un módulo por esquema y la salida. El motor solo escribe estado: cuadros con posición, velocidad y esquema de cada agente, los instantes de salida y los cambios de esquema. Los observables se calculan aparte, en Python. Como validación, el híbrido con T estrella enorme da exactamente las mismas salidas que el TSDMD puro.

### 14. Simulaciones — 0:03

Pasemos a las simulaciones.

### 15. Estudios realizados — 0:45

Antes de los puntos de la consigna hicimos cuatro estudios con TSDMD puro: el paso temporal, los atascos, una fluctuación para romperlos y el segundo target. Después, los puntos a y b con los tres esquemas y 20 realizaciones; el c, barriendo T estrella; el d, con N de 100 a 1000 en dos variantes, y la comparación de las formas de recuperar v_d en el EDMD puro, en un sistema chico. Todas las variantes de un estudio usan las mismas condiciones iniciales. Cortamos una corrida si pasan 300 segundos sin salidas: la consideramos trabada.

### 16. Observables — 0:50

El observable primario es la curva de población: cuántos agentes quedan adentro en cada instante. De ahí sale el tiempo de evacuación, la salida del último agente, si la corrida termina, y el caudal, que son las salidas entre el 10 y el 90 % sobre el tiempo que tardan. Una corrida se traba si nadie sale durante 300 segundos; informamos la fracción con un intervalo de Clopper-Pearson del 95 %. En el híbrido contamos además cuántos agentes hay en cada esquema. El tiempo de ejecución es el wall-clock del bucle de las corridas completas, y como complemento el costo por segundo simulado, que incluye las trabadas. Cada realización aporta un valor y promediamos entre realizaciones, con el desvío estándar como barra de error.

### 17. Resultados — 0:03

Vamos a los resultados.

### 18. Validación de la regla de choque — 0:40

Simulamos un choque aislado de dos agentes, sin término de deseo, con el SFM blando y un paso muy chico, y lo comparamos con la regla de disco duro. En el eje horizontal está la velocidad normal de acercamiento y en el vertical, cuánto queda de la tangencial. La curva negra es la regla y los puntos, el SFM, para tres parámetros de impacto. La tangencial coincide en todo el rango. En los choques rasantes, con b igual a 0,8 sigma, la normal del SFM pierde hasta un 5 %, que la regla no tiene.

### 19. Paso temporal — 0:40

A la izquierda, el error en la restitución normal del choque frontal de los dos agentes más livianos, de 56 kilos, en función del paso. A 2 milisegundos es menor al 0,1 %. A la derecha, el caudal de la evacuación completa con 10 realizaciones por paso: no cambia entre medio milisegundo y 2. Por eso usamos 2 milisegundos.

### 20. Atascos permanentes — 0:45

Lo primero que encontramos es que muchas corridas no terminan. En la animación se ve un arco estático en la puerta: dos agentes apoyados en la pared, a los costados de la puerta, sostienen al resto y nadie más sale. No se rompe porque la fricción del SFM es viscosa: si nadie se mueve, no actúa. Y el modelo no tiene fluctuaciones que lo perturben.

### 21. Atascos: por qué a veces sí y a veces no — 0:45

Nuestra hipótesis es la compresión. El gráfico muestra la superposición de los contactos frente a la puerta en una corrida, en función de cuántos agentes quedan adentro. Con la sala llena, la presión de la multitud se acumula a lo largo de las cadenas de contactos y los comprime hasta 6 centímetros: los agentes se cuelan por la puerta y ningún arco aguanta. Cuando quedan pocos, la compresión baja a 1 centímetro y el arco se sostiene. Lo probamos con un k diez veces mayor, o sea con menos compresión: tres semillas que evacuaban completas se trabaron al principio, igual que el EDMD con discos duros.

### 22. Atascos: curvas de población — 0:40

Con 20 realizaciones se traban 9; las que evacúan tardan unos 1000 segundos. Cada cruz marca el corte de una corrida trabada. El corte de 300 segundos sin salidas es conservador: la pausa más larga que terminó rompiéndose fue de 121 segundos.

### 23. Atascos y fluctuaciones — 0:40

Probamos agregar una fuerza aleatoria solo sobre los agentes en contacto, gaussiana, de 5, 10 y 20 % de m v_d sobre tau, renovada cada 0,1 segundos. La fracción de corridas trabadas no baja de forma detectable: todos los intervalos se superponen. Por eso mantuvimos el modelo sin fluctuación y reportamos el tiempo de evacuación de las corridas que terminan.

### 24. Segundo target — 0:40

Comparamos un target común, en un punto a distancia D afuera de la puerta, con que cada agente se aleje en menos y. Todas las opciones quedan dentro de las barras: el cuello de botella está adentro de la sala, no afuera. Usamos alejarse.

### 25. (a) TSDMD puro — 0:30

Esta es una evacuación completa con TSDMD puro, treinta veces más rápida que el tiempo real, con el color según la rapidez. En los primeros segundos se forma un semicírculo alrededor de la puerta, que se va achicando a medida que salen.

### 26. (a) EDMD puro — 0:35

Este es el EDMD puro, con discos duros y patadas cada 0,05 segundos. Se traba en las 20 corridas, y al principio: salen entre 10 y 192 agentes y después nadie más. Es lo que esperábamos por la hipótesis de la compresión: los discos duros no se comprimen y el arco es rígido desde el primer momento. Además es caro: en el punto c, cada segundo simulado cuesta 237 milisegundos de reloj, 38 veces más que con TSDMD, porque los contactos permanentes se convierten en millones de choques.

## Franco — diapositivas 27 a 39 — 8:33

### 27. (a) Híbrido — 0:35

Este es el híbrido, con T estrella de 0,05 segundos, durante los primeros 60 segundos. En azul, los agentes EDMD; en naranja, los TSDMD. Lejos de la puerta casi todos van por eventos. Los que se acercan a otro pasan a paso temporal antes de tocarlo, y el tapón es todo naranja.

### 28. (a) Fracción de agentes en cada esquema — 0:35

Promediando las 20 realizaciones, al principio todos están en EDMD. A medida que llegan al tapón pasan a TSDMD, y en unos 30 segundos ya no queda ninguno por eventos. Después casi nadie vuelve: en las 20 corridas hubo una sola vuelta a EDMD. El resto de la evacuación, unos 1000 segundos, es todo paso temporal.

### 29. (b) Curvas de población — 0:40

Estas son las curvas de población: para TSDMD y el híbrido, la media y el desvío de las corridas que terminan, y en línea punteada las trabadas, que terminan en una cruz. Las dos curvas se superponen. Las de EDMD puro, en azul, se cortan todas al principio.

### 30. (b) Tiempo de evacuación y atascos — 0:40

A la izquierda, el tiempo de evacuación de las que terminan: 979 más menos 65 segundos con TSDMD y 1006 más menos 52 con el híbrido. A la derecha, la fracción de trabadas: 7 de 20, 8 de 20 y, con EDMD puro, las 20. Entre TSDMD y el híbrido las diferencias están dentro de las barras: el híbrido no cambia la física.

### 31. (c) Tiempo de ejecución en función de T estrella — 0:50

Los tiempos de c y d los medimos todos en la misma computadora, una Apple M5 Pro, con cuatro corridas a la vez. A la izquierda, el tiempo de ejecución de las corridas que terminan, que son entre 5 y 7 de 10; a la derecha, el costo por segundo simulado de todas, en escala logarítmica. Las líneas horizontales son los esquemas puros. Con cualquier T estrella, el híbrido tarda lo mismo que TSDMD, unos 6,2 segundos: todas las diferencias quedan dentro de las barras. EDMD puro, arriba, cuesta 38 veces más.

### 32. (c) Tiempo de evacuación en función de T estrella — 0:30

Si el pase no pierde contactos, el tiempo de evacuación no debería depender de T estrella, y así es: todos los valores quedan dentro de la banda de TSDMD. Abajo, cuántas corridas terminan con cada T estrella.

### 33. (c) Comparación con TSDMD semilla por semilla — 0:50

Como todas las variantes usan las mismas condiciones iniciales, comparamos cada corrida con el TSDMD de su misma semilla. Con T estrella de medio segundo o más nadie llega a estar en EDMD: las salidas son idénticas a las de TSDMD en las 10 semillas, y el híbrido cuesta un 1,1 % más. Ese es el costo fijo del esquema. Con T estrella más chicos, las trayectorias divergen, y la relación de costos varía entre semillas del 10 al 35 %: no se distingue ninguna ganancia. La razón es la cota que vimos antes: lo único que el híbrido puede ahorrar es el vuelo libre, a lo sumo un 2,6 % del tiempo-agente. Es del orden del costo fijo y mucho menor que la dispersión.

### 34. (d) Tiempo de ejecución en función de N — 0:40

A la izquierda, con densidad inicial constante, agrandando la sala; a la derecha, con la sala de 50 metros. Son las corridas que terminan; el marcador hueco indica que terminó una sola. TSDMD y el híbrido se superponen en todo el rango. El tiempo crece más o menos como N al cuadrado, porque tanto el tiempo de evacuación como el costo de cada paso crecen con N. EDMD puro solo termina con 100 agentes.

### 35. (d) Costo por segundo simulado en función de N — 0:40

El costo por segundo simulado sí está definido para todas las corridas, incluidas las trabadas. Con densidad constante, TSDMD y el híbrido crecen como N a la 1,2, casi lineal gracias a las celdas. Con la sala fija crece más lento, como N a la 0,7, porque con pocos agentes pesa el costo fijo de recorrer las celdas. EDMD puro crece como N a la 2,3: con más agentes el tapón es más grande y hay muchos más choques por segundo.

### 36. Recuperación de v_d en EDMD puro — 1:00

Comparamos las formas de recuperar v_d en un sistema chico, de 60 agentes en una sala de 15 metros, porque con 500 la relajación analítica no es viable. Cada punto es una variante: patadas con distintos delta, en azul, y relajación analítica con distintas tolerancias de reapuntado, en violeta. En el eje horizontal está el costo y en el vertical, la diferencia de caudal con el TSDMD de la misma semilla. Las patadas cuestan entre 7 y 61 milisegundos por segundo simulado y dan el mismo caudal que el SFM. La relajación analítica cuesta de 94 a 207 veces más que TSDMD, porque los choques ya no son una cuadrática, y además da un caudal mayor: con la tolerancia de 0,01 radianes, 0,15 más menos 0,11 agentes por segundo. En el EDMD puro conviene usar patadas; en el híbrido, la recuperación la hace el SFM, al costo de TSDMD.

### 37. Conclusiones — 0:03

Para cerrar.

### 38. Conclusiones — 1:00

Con la puerta de 80 centímetros, el SFM sin fuerza social se traba en cerca del 40 % de las corridas: se forman arcos estáticos que la fricción viscosa no rompe, y la compresión de los contactos explica por qué casi siempre se traban al final. El esquema híbrido reproduce al TSDMD: el mismo tiempo de evacuación, el mismo caudal y la misma fracción de atascos, sin violaciones de la cota. El EDMD puro, con discos duros, se traba siempre al principio, y para recuperar v_d las patadas son más baratas y más fieles que la relajación analítica. Por último, el ahorro del híbrido está acotado por el tapón: el 97 % del tiempo-agente se resuelve con paso temporal, y en la práctica el híbrido cuesta lo mismo que TSDMD, mientras que EDMD puro cuesta 38 veces más y escala peor con N.

### 39. Declaración de uso de IA — 0:30

Usamos Claude Code con Claude Opus 5.5 para escribir el código en C++ y Python, las pruebas, las corridas, los gráficos, las animaciones y un borrador de esta presentación. Las decisiones de diseño las tomamos nosotros, y registramos las veces en que no seguimos la recomendación del agente: elegimos el SFM en lugar del CPM, la masa proporcional al área, un estudio formal del segundo target, comparar las formas de recuperar v_d y una presentación más larga.
