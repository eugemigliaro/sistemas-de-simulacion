G7

Nota: 6



General:



En líneas generales el trabajo está bien. Hay varios cambios a tener en

cuenta para las próximas entregas: cómo presentar los resultados, cómo

diagramar la información sin saturar las diapositivas, y qué es un parámetro

y qué no.



-D7) IMPORTANTE: calculan va y S online, en cada paso del loop principal del



motor. El motor solo debe generar el estado del sistema (trayectoria); los

observables se calculan después, en un post-proceso aparte.



-D8) Diagrama UML con letra muy chica, imposible de apreciar durante la

presentación.





-D11) El esquema de la caja está bien pero le faltan etiquetas. Indicar ahí

mismo qué representa cada variable (una flecha con "L" en el borde, un

círculo de radio r_c alrededor de una partícula).

El T_0 de la simulacion no es parametro que se conoce a priori, depende de cuando se llegue al estacionario así que sería mas bien, parte de los resultados.



-Datos que no son parámetros del sistema: T, t_estacionario, M. Si el

comportamiento u output del sistema no cambia al variar ese dato, no es un



parámetro físico.



- D12) IMPORTANTE: Esos son observables instantaneos, Falta explicitar como se calculan promedios y desvio estandar a partir de varias realizaciones.



- D14) mejor que rueda de colores, una barra, o al costado, para aprovechar mejor el espacio y mostrar animaciones mas grandes.

De todas formas, mejor seria mostrar Vicsek con dos valores de ruido y luego de todo el analisis para Vicsek repetir para Votante.





-D16) "Vicsek tolera entre 7,7 y 15,9 veces más ruido que el votante": no

queda claro cómo se calculó ni cual es la afirmación. Ojo con este tipo de relaciones, no suelen ser

lineales y confunden más de lo que aclaran.



CODIGO:

-IMPORTANTE: va y S lo calcularon ONLINE, dentro del loop principal. El



motor debe limitarse a generar el estado del sistema. El cálculo de

observables va en un post-proceso aparte, sobre esa salida. Esto no es lo que se indico en la teorica 0.



INFORME:

- Valen para el informe todas las correcciones de la presentación que

Apliquen.



- Perlas blancas: introducción completa, buen uso de figuras con su análisis

(salvo la Fig. 4, que podría analizarse un poco más, explicitando diferencias de estas curvas con la de la fig 3.). Conclusiones que no agregan info nueva, bien.

- Perlas negras: la Fig. 1 no debería estar en la introducción (ahí no van

resultados); la Fig. 6 muestra un observable (va) que no corresponde a esa

sección (5.4, componente gigante); no duplicar información entre tabla y gráfico (Fig. 13 y Tabla 3

dicen lo mismo).
