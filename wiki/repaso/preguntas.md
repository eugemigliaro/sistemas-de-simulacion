# Preguntas de repaso

## Sistemas y modelos

1. ¿Qué decisiones separan al sistema real, el modelo físico-matemático, el modelo computacional y la simulación?
2. ¿Por qué un modelo es una aproximación no única?
3. ¿Qué información debe contener el estado para determinar la salida futura?
4. ¿Cómo se distinguen modelos estáticos y dinámicos, lineales y no lineales, deterministas y estocásticos?
5. ¿Qué diferencia una simulación de tiempo discreto de una basada en eventos?
6. ¿Por qué una animación no es equivalente a una simulación?

## Estadística y resultados

7. ¿Cómo cambian las normalizaciones de un histograma, una distribución discreta y una densidad de probabilidad?
8. ¿Por qué una simulación estocástica debe repetirse con semillas distintas?
9. ¿Qué información debe acompañar una barra de error?
10. ¿Cómo se eligen las cifras significativas de un promedio y su error?
11. ¿Qué función de error usa la teórica para ajustar un parámetro y qué significa minimizarla?
12. ¿Por qué la cátedra rechaza interpolaciones arbitrarias sin modelo teórico?

## Muchas partículas y materia activa

13. ¿Por qué las interacciones de corto alcance permiten evitar el cálculo de todos los pares?
14. ¿Qué distingue a la materia activa de otros sistemas fuera del equilibrio?
15. ¿Cómo pueden interacciones locales simples producir comportamiento emergente?
16. ¿Qué tres reglas forman el modelo de bandadas de Reynolds?
17. ¿Cómo surgen *freezing by heating* y *faster is slower* en modelos de peatones?

## Cell Index Method y TP1

18. ¿Cómo se asigna una partícula a una celda y qué celdas deben revisarse en dos dimensiones?
19. ¿Qué relación debe haber entre $L/M$ y el alcance de interacción si solo se revisan celdas adyacentes?
20. ¿Cómo se aprovecha la simetría $d_{ij}=d_{ji}$ sin omitir pares?
21. ¿Qué cambia en los bordes cuando se usan condiciones periódicas?
22. ¿Qué almacenan los arreglos `HEAD` y `LIST`?
23. ¿Por qué el mejor valor de $M$ no es necesariamente el máximo posible?
24. ¿Qué experimentos pide el TP1 para separar el efecto de $N$ del efecto de la densidad?
25. ¿Qué datos mínimos deben contener los archivos estático, dinámico y de salida?

## Comunicación

26. ¿Por qué informe y presentación deben ser autocontenidos aunque describan el mismo trabajo?
27. ¿Qué diferencia hay entre el tratamiento de figuras y referencias en un informe y en una presentación?
28. ¿Qué secuencia propone la guía para convertir evolución temporal en resultados paramétricos?
29. ¿Qué condiciones debe cumplir una afirmación para aparecer como conclusión?
30. ¿Cómo se prepara una exposición grupal para evitar partes desbalanceadas o respuestas superpuestas?

## Autómatas celulares y fluidos en retícula

31. ¿Qué propiedades definen un autómata celular y qué papel cumplen $k$ y $r$?
32. ¿Cómo se distinguen las vecindades de von Neumann y Moore?
33. ¿Cuáles son las reglas del Juego de la Vida y por qué ilustran emergencia?
34. ¿Qué caracteriza las cuatro clases cualitativas de Wolfram?
35. ¿Por qué el modelo FHP usa una retícula hexagonal?
36. ¿Qué ocurre en las etapas de propagación y colisión?
37. ¿Qué magnitudes deben conservar las colisiones para recuperar hidrodinámica macroscópica?
38. ¿Por qué hacen falta promedios espaciales y temporales para obtener campos macroscópicos?

## Bandadas y TP2

39. ¿Cómo actualiza posición y orientación una partícula en el modelo de Vicsek?
40. ¿Por qué el promedio angular debe calcularse con seno, coseno y `atan2`?
41. ¿Qué mide la polarización $v_a$ y cuáles son sus valores límite?
42. ¿Cuál es la diferencia exacta entre el modelo estándar y el modelo votante?
43. ¿Cómo se define el cluster más grande y el observable $S$ en el TP2?
44. ¿Cómo determinarías el comienzo del estacionario sin elegirlo arbitrariamente?
45. ¿Qué comparaciones deben mantenerse en las mismas figuras para aislar modelo, densidad y ruido?
46. ¿Por qué el simulador y la animación deben ser módulos independientes?

## Simulación dirigida por eventos y TP3

47. ¿Cuándo es válido representar una colisión como un evento instantáneo?
48. ¿Qué diferencia operativa hay entre avanzar con un $\Delta t$ fijo y avanzar hasta el próximo evento?
49. ¿Qué seis etapas forman el ciclo de una simulación de discos rígidos dirigida por eventos?
50. ¿Cómo se calcula el tiempo candidato de choque con una pared y qué casos deben descartarse?
51. ¿Qué significan $\Delta\mathbf r$, $\Delta\mathbf v$, $\sigma$ y el discriminante $d$ en la predicción de una colisión binaria?
52. ¿Por qué $\Delta\mathbf v\cdot\Delta\mathbf r\geq0$ permite descartar una colisión futura?
53. ¿Qué magnitudes deben conservarse al resolver una colisión elástica?
54. ¿Cómo puede detectarse que un evento guardado en una cola de prioridad quedó invalidado?
55. ¿Cómo se define un gol, la fracción $F_u(t)$ y el tiempo $t_{90}$ en el TP3?
56. ¿Qué restricciones geométricas debe satisfacer una configuración de obstáculos?
57. ¿Por qué $t_{90}$ debe obtenerse por realización antes de calcular su promedio y su barra de error?
58. ¿Qué referencia experimental debe acompañar siempre a las configuraciones con obstáculos?
59. ¿Cómo se estima el coeficiente de difusión a partir del DCM y qué convención dimensional debe aclararse?
60. ¿Qué archivos se entregan y qué contenido debe excluirse del ZIP de código?

## Lecciones de la devolución del TP2

61. ¿Qué debe producir el motor de simulación y qué debe quedar para el post-proceso?
62. ¿Con qué criterio se decide si un dato es un parámetro físico del sistema o solo configuración de la corrida?
63. ¿Por qué el inicio del estacionario es un resultado y no un parámetro?
64. ¿Qué falta en una diapositiva que define $v_a(t)$ y $S(t)$ pero no dice cómo se obtienen los puntos y las barras de error de las curvas?
65. ¿Por qué un cociente entre umbrales de ruido de dos modelos puede confundir más que aclarar?
