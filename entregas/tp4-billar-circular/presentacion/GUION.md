# Guion orientativo para ensayo

Borrador para revisar y reformular entre los integrantes. Total previsto: **13 minutos**; los tiempos son objetivos de ensayo, no una duración medida.

Reparto propuesto, pendiente de acordar nombres: A, láminas 1–11 (4:12); B, 12–21 (4:30); C, 22–29 (4:18). Todos deben poder explicar toda la presentación [GPRES, p. 3].

## Lámina 1 · 10 s · 0:00–0:10

Presentar el objetivo: comparar integración, validar el paso y estudiar cómo la geometría y la densidad afectan la conversión del billar. Los autores y comisión se tomaron del TP3 y deben confirmarse antes de entregar.

Fuentes: TP04, pp. 1–4; portada del TP3.

## Lámina 2 · 3 s · 0:10–0:13

Transición breve a los fundamentos generales. No introducir todavía el radio del billar, su N ni sus obstáculos.

Fuentes: GPRES, p. 2; COR03, D3.

## Lámina 3 · 35 s · 0:13–0:48

En cuerpos idealizados con contacto elástico, el modelo representa la deformación mediante una superposición. Newton relaciona fuerza y aceleración. La fuerza normal es repulsiva y se anula fuera del contacto; e_ij apunta de i a j, por eso el signo negativo. No hay rozamiento ni disipación. A diferencia de discos rígidos ideales, el contacto dura un intervalo finito.

Fuentes: T04, p. 42; TP04, p. 2.

## Lámina 4 · 3 s · 0:48–0:51

Transición a cómo se integra el modelo. Esta sección describe el motor, sin introducir formatos de archivo o implementación del postproceso.

Fuentes: GPRES, p. 2; COR02.

## Lámina 5 · 45 s · 0:51–1:36

La grilla de ancho 2r reduce candidatos y cada fuerza de pares se evalúa una vez. Verlet original requiere posición anterior y fuerza actual. Se inicializa la posición anterior con Taylor de segundo orden. La velocidad centrada corresponde al mismo instante que la posición. La imagen radial de la pared se recalcula cada paso. El motor conserva el primer contacto como estado histórico y guarda trayectorias; energía, histogramas y tiempos agregados se obtienen después.

Fuentes: cpp/include/tp4/billiard.hpp; T04, pp. 13–14; TP04, pp. 2–3; COR02.

## Lámina 6 · 3 s · 1:36–1:39

Transición del modelo general a la configuración particular del billar.

Fuentes: GPRES, p. 2.

## Lámina 7 · 45 s · 1:39–2:24

Señalar R, r, la posición simétrica x0 y las velocidades en el esquema. Los dos obstáculos son fijos y del mismo radio que las partículas. La dirección inicial es uniforme y todas las velocidades tienen módulo unitario. El color cambia solo al primer contacto con un obstáculo; una usada sigue moviéndose e interactuando. Por tanto, la conversión no modifica N ni la densidad.

Fuentes: TP04, pp. 2–3.

## Lámina 8 · 50 s · 2:24–3:14

Fu promedia el indicador de usada entre las N partículas de UNA realización. Primero obtenemos t90 y t100 en cada corrida y recién entonces promediamos los tiempos entre realizaciones. Las barras son desvíos estándar muestrales, no errores estándar. El cruce de la curva Fu media no equivale al promedio de los cruces. Un tiempo no alcanzado queda censurado y no se elimina ni se reemplaza por un dato ficticio.

Fuentes: TP04, pp. 3–4; T00, p. 69; COR03, D14; python/performance_analysis.py.

## Lámina 9 · 25 s · 3:14–3:39

Distinguir parámetros físicos de controles numéricos y duración de observación. El benchmark dura 30 s y mantiene su paso validado. Los estudios largos usan un paso menor. Para N=650, el rechazo secuencial se sustituyó por red hexagonal y 500 barridos Monte Carlo: queda orden residual, así que no atribuimos toda diferencia solamente a N. La lista de semillas y el generador están en los manifiestos técnicos.

Fuentes: experiments/configs/; experiments/rendimiento-y-densidad.md; COR02; COR03.

## Lámina 10 · 3 s · 3:39–3:42

Transición a resultados. Para cada estudio se ofrece contexto físico, evolución estática y resultado escalar; la comparación del oscilador es la excepción exigida.

Fuentes: GPRES, p. 2; TP04, p. 2.

## Lámina 11 · 30 s · 3:42–4:12

Única lámina del oscilador: ECM de posición contra solución analítica, promedio entre todos los pasos temporales de una trayectoria. Beeman obtuvo el menor ECM en los siete pasos ensayados. Verlet original y Velocity Verlet prácticamente coinciden con las adaptaciones usadas para el amortiguamiento. Euler predictor-corrector converge con errores mayores en este rango. No añadir otra lámina del sistema 1.

Fuentes: experiments/results/oscillator-summary.csv; experiments/README.md; TP04, pp. 1–2; T04, p. 37.

## Lámina 12 · 15 s · 4:12–4:27

Reproducir la animación dentro del PPTX. Mostrar N=300 sin obstáculos para situar el estudio energético. Las partículas se solapan levemente durante contactos. El tiempo visible es físico y la reproducción es cuatro veces más lenta. No confundirlo con tiempo de ejecución.

Fuentes: presentacion/.build/media-manifest.json; TP04, p. 3.

## Lámina 13 · 35 s · 4:27–5:02

La cinética sola no se conserva durante un contacto: parte se almacena en resortes. Sumamos potencial de pares y pared, una vez por contacto. El escalar es el máximo error relativo sobre cuadros guardados. Reducir h mejora el balance; el máximo muestreado no garantiza el máximo continuo. Se hicieron controles de cadencia para evitar ocultar picos.

Fuentes: experiments/results/energy-summary.csv; experiments/billar-energia.md; T04, p. 42.

## Lámina 14 · 35 s · 5:02–5:37

El umbral del 0,1 % es una decisión local, no de la consigna. Aunque h=10^-4 s pasa el ensayo corto, falla a 30 s con 0,241 %. h=5×10^-5 s da 0,0602 % y se usa en el benchmark. Los pilotos de 100 s motivaron refinar los análisis largos a 1,25×10^-5 s. En las 154 nuevas corridas de densidad y mapa el máximo muestreado fue 0,0267 %. No extrapolar la validación a un horizonte no comprobado.

Fuentes: experiments/results/billiard-step-selection.json; position-step-validation.json; density-verification.json.

## Lámina 15 · 15 s · 5:37–5:52

Mostrar la misma geometría con N bajo y alto. El ejemplo denso parte de la condición inicial del benchmark. Es contexto del aumento de trabajo por paso, no un cronometraje de la animación.

Fuentes: presentacion/.build/media-manifest.json; experiments/rendimiento-y-densidad.md.

## Lámina 16 · 40 s · 5:52–6:32

Cada punto es el tiempo medio de diez corridas de 30 s y la barra su desvío. Ambos motores se recompilaron con C++20 y -O3 en la misma Apple M5 Pro. El reloj excluye generación y escritura. En el rango común eventos es más rápido para N=100 y 200, y paso temporal para N=400. El cruce queda entre 200 y 400, sin fijar su N exacto. No inferir una ley exponencial ni un exponente asintótico a partir de estos puntos.

Fuentes: experiments/results/performance-summary.csv; performance-manifest.json; COR03, D16 y D22.

## Lámina 17 · 15 s · 6:32–6:47

Reproducir el video de tres posiciones. Se mueve x0 simétricamente, manteniendo N=100. La fila muestra obstáculos juntos, posición intermedia y junto a la pared. Frescas azules, usadas rojas, obstáculos negros. Se muestran cinco segundos de una realización por posición, no un promedio.

Fuentes: experiments/results/position-animation-manifest.json; TP04, p. 3.

## Lámina 18 · 30 s · 6:47–7:17

Las curvas temporales son estáticas. A cada tiempo se promedian cinco fracciones Fu, con desvío entre corridas. La línea del 90 % ilustra el umbral, pero los t90 se extraen de cada historia individual. Las posiciones intermedias completan la conversión más rápido que los extremos en estos ejemplos.

Fuentes: experiments/results/position-fu.csv; COR03, D17–D21.

## Lámina 19 · 35 s · 7:17–7:52

Se recorrieron once posiciones en ambos N, cinco realizaciones por punto y 100 s. Todas alcanzaron t90. El mínimo observado es x0=0,16 m para N=100 y x0=0,3975 m para N=20. Las líneas solo guían la lectura. Los vecinos tienen dispersión y la grilla no localiza un óptimo continuo exacto. La comparación es compatible con un papel de la mezcla entre trayectorias, pero no se midió la frecuencia de choques.

Fuentes: experiments/results/position-summary.csv; experiments/posicion-obstaculos.md; TP04, p. 3.

## Lámina 20 · 15 s · 7:52–8:07

Volver a N=100 sin obstáculos. Todas las partículas comienzan con rapidez unitaria; los contactos redistribuyen energía cinética entre ellas. La animación muestra partículas, no un gráfico temporal animado.

Fuentes: presentacion/.build/media-manifest.json; TP04, pp. 3–4.

## Lámina 21 · 35 s · 8:07–8:42

Cada histograma instantáneo normaliza 100 velocidades de una corrida por N y ancho de bin; luego se promedian diez densidades. En t=0 hay una delta en v=1, representada por una línea vertical sin altura probabilística finita. Los bins cubren todas las colas. El ensayo de 30 s no satisfizo el criterio local; se amplió a 60 s y ventanas de 10 s. En [10,60) las distancias de variación total entre ventanas son menores que 0,011 y los cambios del ajuste menores que 0,85 %. Esta ventana compatible con estabilidad no determina el primer instante físico de relajación.

Fuentes: experiments/results/speed-snapshots.csv; speed-windows.csv; experiments/rapidez.md; COR02.

## Lámina 22 · 50 s · 8:42–9:32

La forma teórica es Maxwell–Boltzmann 2D. Solo theta=kBT es libre. g_b es la integral del modelo en cada bin dividida por su ancho. Se minimiza la suma sin pesos de errores cuadrados mediante grilla logarítmica y sección áurea. El histograma estacionario usa 500 cuadros por corrida y diez corridas; los cuadros no son realizaciones independientes. Las barras son desvíos entre diez densidades. El ajuste a la media da 0,0123986 J, 0,81 % menor que 0,0125 J inicial. La cinética es 0,0123234 J y el potencial 0,0001765 J por partícula. El potencial explica la reducción cinética; no explica por sí solo la diferencia entre mínimos cuadrados y segundo momento. No se realizó una prueba formal de bondad de ajuste ni se informa temperatura en kelvin.

Fuentes: TP04, p. 4; T00, pp. 79–80; experiments/results/speed-summary.json; speed-stationary.csv.

## Lámina 23 · 15 s · 9:32–9:47

Comparar N=50 y 650 con obstáculos juntos. La configuración física es la misma salvo N y la familia de inicialización del caso denso, ya aclarada. No describir N=650 como inmóvil: sus partículas se desplazan, aunque la conversión sea lenta.

Fuentes: presentacion/.build/media-manifest.json; experiments/densidad-y-mapa.md.

## Lámina 24 · 25 s · 9:47–10:12

Los primeros 300 s muestran que N=20 y 200 avanzan hacia conversión completa mientras N=650 llega en promedio a solo 4,32 %. Los tiempos siguen censurados para las diez realizaciones N=650. Las curvas son medias de Fu, con bandas de desvío. El benchmark original de 30 s se conserva; este seguimiento usa h refinado y no se concatena con él.

Fuentes: experiments/results/density-final-fu.csv; density-complete-cases.json; TP04, p. 4.

## Lámina 25 · 45 s · 10:12–10:57

Cada círculo es una media completa de diez tiempos y cada triángulo una cota inferior, sin barras inventadas para tiempos desconocidos. El eje vertical es logarítmico. Se extendieron tres casos N=400 a 600 s para observar sus últimos contactos; su t100 medio es 267±61 s. N=50 se añadió de forma exploratoria tras el indicio del mapa y se completaron diez realizaciones. El menor t90 medio de la grilla es 20,4±3,5 s para N=50. El menor t100 medio es 41±14 s para N=20, muy próximo a 42,5±8,1 s para N=50. No se demuestra una diferencia poblacional ni una densidad óptima global única.

Fuentes: experiments/results/density-complete-summary.csv; density-best-tested.json; density-followup-contract.json; density-extra-contract.json.

## Lámina 26 · 35 s · 10:57–11:32

El mapa representa t90 medio frente a DOS parámetros independientes, x0 y N, por eso aquí sí corresponde un mapa de calor. Hay 44 celdas, cinco realizaciones por celda y todas alcanzaron t90 antes de 100 s. Los recuadros marcan los mínimos muestrales. Las posiciones elegidas no siguen una ley monótona con N. No confundir cinco realizaciones por celda con las diez del estudio de densidad, ni un mínimo de grilla con un óptimo continuo o estadísticamente significativo.

Fuentes: TP04, p. 4; experiments/results/density-heatmap-summary.csv; density-best-positions.json; COR03, D18.

## Lámina 27 · 3 s · 11:32–11:35

Transición breve. La conclusión solo recoge resultados que ya se mostraron, sin introducir explicaciones causales no probadas.

Fuentes: GPRES, p. 3.

## Lámina 28 · 50 s · 11:35–12:25

Recapitular el cruce de costos entre N=200 y 400, el cambio de posición de menor media con N, el valor térmico ajustado y la diferencia entre minimizar t90 y t100. La censura N=650 es un límite cuantificado del resultado, no una media estimada. No presentar la frecuencia de choques como una causa exclusiva medida. No añadir otros resultados del oscilador: su única diapositiva ya se mostró.

Fuentes: Figuras de las diapositivas 16, 19, 22, 25 y 26; GPRES, p. 3; TP04, p. 2.

## Lámina 29 · 35 s · 12:25–13:00

Declarar de forma fiel la asistencia usada, incluyendo este borrador de presentación. La consigna permite asistencia de programación y exige participación de los estudiantes en la elaboración final. El grupo debe revisar las explicaciones, modificar y validar el borrador, completar enlaces públicos y ensayar. No afirmar que una revisión del grupo o una aprobación de cátedra ya ocurrió.

Fuentes: TP04, p. 4; registro de uso de IA en README.md.
