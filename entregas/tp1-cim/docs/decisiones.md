# Decisiones de diseño

Este registro separa decisiones confirmadas, supuestos de implementación y preguntas todavía abiertas. Las decisiones que afecten resultados experimentales deberán quedar cerradas antes de medir.

## Confirmadas

- El motor de simulación se implementará en C++20.
- La visualización, animación y el análisis se implementarán en Python 3.
- La consigna oficial no se duplica ni se modifica; se referencia desde el README.
- La simulación y el postproceso serán programas independientes [T01, p. 33].
- Se implementarán contornos con paredes y periódicos [TP01, p. 1].
- La vecindad usa una desigualdad estricta: distancia borde-borde menor que rc [TP01, p. 1].
- La semilla del generador será un parámetro explícito para asegurar reproducibilidad.
- La salida de vecinos será simétrica, sin duplicados y ordenada por identificador.
- La fuerza bruta será la referencia de corrección para validar el CIM [T01, p. 28].
- El tiempo medido abarcará la construcción de la estructura necesaria y la búsqueda de vecinos; excluirá generación, lectura, escritura y visualización.
- La implementación C++ básica no dependerá de bibliotecas externas.
- La identidad de cada partícula será el número de su fila, comenzando en 1.
- Las velocidades de configuraciones generadas para el TP1 serán cero.
- Las posiciones periódicas se representarán en el intervalo base [0,L).
- El escritor dinámico emitirá x, y, vx y vy; el lector también admitirá las dos columnas x, y presentes en el ejemplo oficial [EJ01].
- Los radios se sortearán uniformemente en el intervalo configurado; para la consigna se usarán 0.23 y 0.26 [TP01, p. 1].
- El generador rechazará posiciones cuyo disco se solape con uno ya ubicado y fallará explícitamente si agota el límite de intentos.
- La fuerza bruta recorrerá únicamente pares i<j y agregará cada relación en ambos sentidos.
- neighbors.txt tendrá una fila para cada ID y separará por comas el ID propio y sus vecinas, siguiendo el ejemplo oficial [EJ01].
- Toda lista serializada deberá ser simétrica, estar ordenada y no contener duplicados ni la propia partícula.
- El comando interactivo medirá solo la búsqueda de vecinos; la lectura y la escritura quedarán fuera del intervalo temporizado.

## Supuestos iniciales a validar

- La animación mostrará una secuencia de estados o configuraciones generadas por C++; no inventará una dinámica física ausente del enunciado.

## Preguntas abiertas

- Derivación exacta del tamaño seguro de celda para radios no nulos.
- Definición operativa del N más alto posible para el generador aleatorio.
- Definición de densidad para el punto 4.2: densidad numérica o fracción de área.
- En el estudio a densidad fija, mantener M fijo o mantener aproximadamente fijo el lado de celda óptimo.
- Cantidad final de semillas y repeticiones para cada experimento.
- Formato final de la demostración animada.
