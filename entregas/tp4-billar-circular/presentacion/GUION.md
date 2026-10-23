# Guion oral del TP4

Duración objetivo: **12:40**, con 0:20 de margen sobre los 13 minutos de la consigna [TP04, p. 1]. Las tres animaciones corren embebidas en el PPTX mientras se habla. El reparto está balanceado. Igual, cada integrante tiene que poder presentar cualquier parte y responder sobre todo el trabajo, y nadie agrega nada a lo que acaba de decir otro [GPRES, p. 3].

| Parte | Integrante | Diapositivas | Tiempo |
|---|---|---|---|
| Modelo, implementación y simulaciones | Eugenio | 1 a 10 | 4:29 |
| Observables, sistema 1, paso temporal, rendimiento y densidad | Francisco | 11 a 19 | 4:08 |
| Posición, rapidez y conclusiones | Franco | 20 a 29 | 4:03 |

## Eugenio — diapositivas 1 a 10 — 4:29

### 1. Portada — 0:20

Buenas tardes. Somos Eugenio Migliaro, Francisco Costa y Franco Branda, del grupo 07. En este trabajo integramos las ecuaciones de movimiento con un paso temporal fijo: primero en un oscilador amortiguado, para comparar esquemas de integración contra la solución exacta, y después en un billar circular donde las partículas chocan a través de resortes.

### 2. Introducción — 0:03

Empecemos por el modelo.

### 3. Partículas con contactos elásticos — 0:45

El sistema real son discos rígidos que, al chocar, se deforman un poco, como los granos de un medio granular. A diferencia del TP3, el choque no es instantáneo: mientras dos discos se superponen, aparece una fuerza de resorte. La fuerza sobre cada partícula es la suma, sobre los cuerpos en contacto, de menos k por la superposición xi por el versor hacia el otro cuerpo. Xi es la suma de los radios menos la distancia entre centros; si es negativa, no hay contacto. El otro cuerpo puede ser una partícula o un obstáculo fijo. Sin fricción ni disipación, la energía total se conserva: la cinética más un medio de k xi cuadrado por cada contacto. Esa conservación la usamos para elegir el paso.

// me gusta mas asi:

Modelamos los choques mediante contactos elásticos de duración finita. La pequeña deformación de los cuerpos se representa permitiendo una superposición entre los discos.

Xi mide esa superposición: es la suma de los radios menos la distancia entre centros. Si es positiva, aparece una fuerza de resorte proporcional a xi. El versor apunta hacia el otro cuerpo y el signo negativo hace que la fuerza sea repulsiva, como se ve en el dibujo.

Sumando todos los contactos obtenemos la fuerza total y, por la segunda ley de Newton, la aceleración de cada partícula.

Durante el choque se intercambian energía cinética y potencial elástica. Como no hay fricción ni disipación, la energía total se conserva, y usamos esa conservación para evaluar el paso temporal.”

### 4. Implementación — 0:03

Veamos cómo lo implementamos.

### 5. Integración con paso temporal fijo — 0:40
//no lo tengo 100% CLARO

En el billar usamos Verlet original, como pide la consigna. La posición siguiente sale de las dos posiciones anteriores y de la fuerza actual. La velocidad no se integra: es la diferencia centrada entre la posición siguiente y la anterior. Para arrancar necesitamos la posición en menos delta t, que estimamos con un paso de Euler hacia atrás. Así hay una sola evaluación de fuerzas por paso. La velocidad en t recién se conoce cuando calculamos la posición en t más delta t, así que escribimos el estado en ese momento, con posición y velocidad sincronizadas. Guardamos un cuadro cada n pasos, o sea cada delta t dos.

### 6. Algoritmo del motor — 0:35

Este es el algoritmo. Generamos N partículas azules, sin superponerse y con rapidez v cero. En cada paso ubicamos las partículas en celdas de lado mayor o igual a 2r. Así cada una se compara solo con su celda y las ocho vecinas, y el costo crece en forma proporcional a N. Sumamos los resortes con las vecinas, con la pared y con los obstáculos. Si una partícula fresca se superpone con un obstáculo, pasa a roja. Avanzamos con Verlet y, cuando corresponde, escribimos el tiempo, las posiciones, las velocidades y los colores.
imp:
“Calculamos todos los pasos temporales, pero escribimos solo uno cada cierta cantidad de pasos para reducir el volumen de datos.”

### 7. Arquitectura del motor — 0:30

El motor está en C++. Main lee la línea de comandos y llama a la generación, a la simulación o al oscilador. Simulation hace Verlet y le pide las fuerzas a ForceField, que maneja las celdas; los dos usan los datos del billar. El módulo io escribe el estado en un archivo de texto. El motor no calcula observables: la energía, la fracción de usadas y las distribuciones se calculan después, en Python, leyendo esos archivos.

### 8. Simulaciones — 0:03

Pasemos al sistema que simulamos.

### 9. Sistema 2: billar circular con dos obstáculos — 0:40

El billar es un círculo de 51 centímetros de radio, con dos obstáculos fijos del tamaño de una partícula en más y menos x cero; el esquema está a escala. Las partículas tienen 1,75 centímetros de radio y 25 gramos, y k vale diez a la cuatro newton por metro. Arrancan azules, a un metro por segundo en una dirección al azar. La primera vez que una toca un obstáculo pasa a roja, y sigue moviéndose e interactuando. Para la pared usamos una partícula imagen: un disco fijo sobre la normal, del otro lado de la pared, que recalculamos en cada paso. Así la fuerza de la pared es radial.

### 10. Estudios realizados — 0:50

Hicimos seis estudios. Para elegir el paso, 300 partículas sin obstáculos durante 300 segundos. Para el tiempo de ejecución, once valores de N entre 20 y 650 con los obstáculos en contacto, durante 30 segundos. Para la densidad continuamos hasta 300 segundos las de 20 a 300 partículas y agregamos 5, 10, 15 y 30: nos quedamos con los N en los que todas las realizaciones convierten todas las partículas. La posición de los obstáculos toma once valores entre r y R menos r, con 100 y 20 partículas, y con 50 y 200 completamos un mapa. Por último, la rapidez, con 100 partículas sin obstáculos. Con más de 430 partículas partimos de una red triangular desordenada, porque el sorteo no logra ubicarlas. Francisco sigue con los observables.

## Francisco — diapositivas 11 a 19 — 4:08

### 11. Observables — 0:45

Todos los observables se calculan sobre los estados guardados. Para la energía sumamos la cinética y la de cada resorte, y tomamos delta E: la máxima variación relativa respecto de la energía inicial. F u es la fracción de partículas usadas. En cada realización, t noventa es el primer cuadro con F u mayor o igual a 0,9, y t cien, el primero con F u igual a uno. Después promediamos entre realizaciones, con el desvío estándar como barra de error. Si alguna realización no llega, no damos un promedio: informamos cuántas no llegaron y su F u al final. La rapidez se mide con un histograma normalizado, con bins de 0,1 metros por segundo.

### 12. Resultados — 0:03

Vamos a los resultados.

### 13. Sistema 1: error de los esquemas de integración — 0:30

Primero, el oscilador amortiguado con los parámetros de la teórica: el error cuadrático medio respecto de la solución analítica en función del paso, en escala doble logarítmica. Euler predictor-corrector tiene pendiente 2, o sea que es de primer orden. Los otros tres tienen pendiente 4, de segundo orden, y están entre cuatro y diez órdenes de magnitud más abajo. En el recuadro se ve que Beeman queda por debajo: su error es un 13 % menor que el de Verlet en todo el rango.

### 14. Paso temporal: evolución de la energía — 0:25

Ahora el billar. Para elegir el paso simulamos 300 partículas sin obstáculos y miramos la variación relativa de la energía total, la cinética más la de los resortes. Debería conservarse, así que lo que vemos es el error de integración: crece con el paso y con el tiempo. Con cinco por diez a la menos cuatro segundos la energía diverge: una partícula termina atravesando la pared.

### 15. Paso temporal: elección de delta t — 0:35

Resumimos cada curva con delta E, el máximo en 300 segundos, promediado en cinco realizaciones. Con un paso más chico la energía se conserva mejor, pero el costo crece como uno sobre delta t. Pedimos que la energía total no varíe más de un 0,1 % en 300 segundos, la corrida más larga: así ese error queda muy por debajo de la dispersión de k B T entre realizaciones, del 0,6 %. El paso elegido es dos por diez a la menos cinco segundos, con delta E de 2,6 por diez a la menos cuatro.

### 16. Tiempo de ejecución en función de N — 0:35

Con ese paso medimos el tiempo para simular 30 segundos, con los dos motores en la misma computadora. Con paso temporal, el costo es proporcional a N: al duplicar las partículas se duplica el tiempo, porque con las celdas cada una tiene siempre pocas vecinas. En el TP3, dirigido por eventos, se multiplica por 10 a 20: hay más choques y cada uno cuesta más. Con pocas partículas el TP3 es mucho más rápido, pero desde 450 gana el TP4, y con 650 el TP3 tarda diez veces más.

### 17. Cantidad de partículas — 0:25

Ahora, el efecto de la densidad, con dos casos extremos: 20 partículas a la izquierda y 650 a la derecha. Arriba se ve F u y, cuando llega a 0,9, el t noventa. Con 20 se llega al 90 % en unos 15 segundos. Con 650, las partículas quedan casi en una red y solo se convierten las que rodean a los obstáculos: a los 30 segundos se usó apenas el 2 %.

### 18. Densidad: fracción de partículas usadas — 0:15

Con las corridas completas, de 300 segundos, miramos F u para cinco valores de N. Con 5 partículas la conversión es lenta y a saltos; con 20 es la más rápida, y desde ahí se hace más lenta a medida que crece N.

### 19. Densidad: tiempos de conversión — 0:35

Acá están t noventa y t cien medios en función de la densidad. Hay una densidad óptima: t noventa es mínimo con 20 partículas, unos 17 segundos, y hasta 50 queda a menos de un desvío. Con menos partículas faltan choques: la pared conserva el momento angular, y sin choques solo un 13 % llega a los obstáculos; las demás necesitan que otra las desvíe. Con más, se estorban: cada una avanza menos entre choques. Solo mostramos los N en los que todas las realizaciones convierten todas las partículas en 300 segundos. Franco sigue con la posición.

## Franco — diapositivas 20 a 29 — 4:03

### 20. Posición de los obstáculos — 0:20

Ahora movemos los obstáculos, con 100 partículas: en contacto en el centro, a la mitad del radio y contra la pared. Primero llega al 90 % el del medio, a los 13 segundos; después el del centro, a los 23, y por último el de la pared, a los 33.

### 21. Posición: fracción de partículas usadas — 0:25

Estas son las curvas de F u para esas tres posiciones, promediadas en diez realizaciones; la zona sombreada es el desvío. Con los obstáculos a la mitad del radio, F u llega a 0,9 cerca de los 15 segundos; en el centro, cerca de los 23; y contra la pared, cerca de los 32. En todas las realizaciones se usan todas las partículas antes de los 100 segundos.

### 22. Posición: tiempo al 90 % — 0:35

Este es t noventa medio en función de la posición, con 100 y con 20 partículas. Con 100 hay un mínimo amplio: entre 0,16 y 0,30 metros el promedio queda a menos de un desvío del menor, de unos 15 segundos; en los extremos es mucho más lento. La consigna pregunta si esto depende de la frecuencia de choques: con 20 partículas, que chocan mucho menos, los extremos siguen siendo los peores, pero entre 0,11 y 0,40 metros las diferencias quedan dentro del desvío y el mínimo deja de estar definido.

### 23. Posición y densidad — 0:30

Juntamos posición y densidad en un mapa: el color es t noventa medio y el círculo marca la mejor posición para cada N. Con 50, 100 y 200 partículas el mínimo está entre 0,16 y 0,26 metros, cerca de la mitad del radio. Con 20 aparece más afuera, pero ahí vimos que el mínimo es poco marcado. Para cualquier posición, el tiempo crece con N: el mejor t noventa pasa de unos 11 segundos con 20 partículas a 20 segundos con 200.

### 24. Distribución de rapideces — 0:20

Para la distribución de rapideces sacamos los obstáculos y dejamos 100 partículas. Todas arrancan con la misma rapidez, por eso tienen el mismo color. El video va en cámara lenta, porque todo pasa en el primer segundo: enseguida aparecen partículas casi quietas y otras al doble de v cero.

### 25. Rapidez: evolución de f(v) — 0:30

El histograma lo armamos con las 100 partículas de 30 realizaciones. A 0,1 segundos todavía queda un pico en v cero; a 0,2 segundos ese pico bajó a la mitad, y desde 0,5 segundos ya no se distingue de la distribución estacionaria. Para fijar desde cuándo es estacionaria, ajustamos k B T en ventanas de un segundo: desde 1 segundo, todos los valores quedan dentro de las fluctuaciones del de la segunda mitad de la corrida.

### 26. Rapidez: ajuste de Maxwell–Boltzmann — 0:30

A la izquierda, el histograma estacionario promediado entre realizaciones, con la Maxwell–Boltzmann en dos dimensiones ajustada. Usamos el método de la Teórica 0: a la derecha está el error del ajuste en función de k B T, el único parámetro libre, y su mínimo da el mejor ajuste: 1,242 por diez a la menos dos joules. Lo esperado es m v cero al cuadrado sobre dos, 1,250: difieren en un 0,7 %, del orden del desvío entre realizaciones.

### 27. Conclusiones — 0:03

Para cerrar, las conclusiones.

### 28. Conclusiones — 0:40

En el oscilador, Beeman tiene el menor error. En el billar, con un paso de dos por diez a la menos cinco segundos la energía total varía menos del 0,1 % en 300 segundos, y el costo crece en forma lineal con N: con muchas partículas le gana al TP3. La conversión es más rápida con densidades intermedias, de 20 a 50 partículas: con menos faltan choques y con más se estorban. La mejor posición de los obstáculos está entre un tercio y la mitad del radio. Por último, en un segundo las rapideces llegan a una Maxwell–Boltzmann, con k B T muy cerca de m v cero al cuadrado sobre dos.

### 29. Declaración de uso de IA — 0:10

Para el código, las pruebas, las corridas y los gráficos usamos Codex con GPT-6.1 Sol y Claude Code con Claude Opus 5.5. Muchas gracias.
