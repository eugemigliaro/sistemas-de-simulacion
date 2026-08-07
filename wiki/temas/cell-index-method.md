# Cell Index Method y TP1

## Problema de vecindad

Para una interacción de corto alcance interesa identificar, para cada partícula, cuáles están dentro de un radio de corte. La fuerza bruta compara todos los pares y su costo crece como $N^2$. La teórica indica que el Cell Index Method (CIM) puede crecer linealmente con $N$ a densidad constante; si aumenta la densidad, el crecimiento vuelve a ser cuadrático, aunque con un prefactor menor [T01, p. 19].

El CIM divide el dominio en una grilla, asigna cada partícula a una celda según su posición y calcula distancias solo dentro de la celda propia y las celdas vecinas [T01, p. 21]. En un dominio cuadrado de lado $L$, dividido en $M×M$ celdas, el lado de celda es $l=L/M$. Para partículas puntuales y un barrido limitado a las ocho celdas adyacentes, la guía exige $L/M>r_c$ [T01, p. 22] [T01, p. 23].

La simetría $d_{ij}=d_{ji}$ permite evitar comparaciones duplicadas. En dos dimensiones, para una celda interior basta procesar la propia y una mitad consistente de sus vecinas; el ejemplo oficial usa cuatro celdas vecinas adicionales [T01, p. 25]. En los bordes, las condiciones periódicas conectan celdas de lados opuestos y obligan a comparar partículas a través del contorno [T01, p. 26].

## Estructura de datos

El extracto bibliográfico describe dos estrategias. Una lista de Verlet guarda vecinas dentro de un radio mayor que el corte y se reconstruye antes de que el desplazamiento agote la zona de seguridad [B03, p. 2] [B03, p. 3]. La estructura por celdas usa un arreglo `HEAD`, con la primera partícula de cada celda, y un arreglo `LIST`, que enlaza las partículas restantes de esa celda [B03, p. 5] [B03, p. 6].

En dos dimensiones, revisar la celda propia y ocho vecinas supone aproximadamente $9N_c$ candidatas por partícula, donde $N_c=N/M^2$ es la ocupación media; aprovechar simetría reduce el trabajo aproximadamente a la mitad. Para sistemas pequeños, mantener las listas puede costar más de lo que ahorra [B03, p. 5] [B03, p. 7].

## Alcance del TP1

La consigna pide implementar el CIM para partículas no superpuestas de radios no nulos. Las entradas son posiciones, radios y parámetros $N,L,M,r_c$; las salidas son la lista de vecinas por distancia borde a borde, el tiempo de ejecución y una figura que destaque una partícula y sus vecinas [TP01, p. 1]. Deben existir dos variantes: paredes y condiciones periódicas [TP01, p. 1].

La modificación del criterio de tamaño de celda para radios $r_i>0$ es una pregunta explícita de la consigna y no se resuelve aquí. Al trabajarla habrá que distinguir la distancia centro-centro de la distancia borde-borde y justificar qué alcance máximo debe cubrir el barrido de celdas [TP01, p. 1].

El estudio experimental tiene dos partes:

1. variar $M$ desde fuerza bruta hasta el máximo permitido, para dos valores de $N$, y medir promedio y desvío estándar del tiempo;
2. con el $M$ óptimo, variar $N$ y comparar el crecimiento a densidad libre con el crecimiento a densidad fija [TP01, p. 1] [TP01, p. 2].

## Formatos y datos de ejemplo

El formato estático comienza con $N$ y $L$, seguido por radio y propiedad de cada partícula. El dinámico comienza con el tiempo y luego registra posición y velocidad por partícula. Para este TP se usa un único estado temporal. La salida asocia cada identificador con los identificadores cuya distancia borde-borde es menor que $r_c$ [TP01, p. 2].

El paquete `EJ01` contiene ejemplos estático y dinámico para 100 partículas, un ejemplo parcial de vecinos y una especificación textual de la salida. Son datos de apoyo; la consigna `TP01` conserva prioridad sobre ellos [EJ01] [GPRES, p. 1].

## Lista de comprobación de la consigna

- generación sin superposición;
- validación del máximo de $M$;
- distancia borde-borde;
- paredes y periodicidad;
- lista simétrica sin duplicados;
- figura de una partícula y sus vecinas;
- mediciones repetidas con media y desvío;
- estudios de $M$, $N$ y densidad;
- demostración dinámica con parámetros variables [TP01, p. 1] [TP01, p. 2].
