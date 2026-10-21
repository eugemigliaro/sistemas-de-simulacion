# Guion orientativo para ensayo

Total previsto: **12:15**, con 45 s de margen sobre los 13 minutos; son objetivos de ensayo, no una duración medida.

Reparto orientativo: A, láminas 1–12 (4:22); B, 13–21 (4:00); C, 22–29 (3:53). Acordar el reparto y ensayar entre los integrantes [GPRES, p. 3].

## Lámina 1 · 10 s · 0:00–0:10

Presentar el objetivo: comparar integradores, validar el paso temporal y estudiar cómo la geometría y la densidad afectan la conversión del billar.

Fuentes: TP04, pp. 1–4

## Lámina 2 · 3 s · 0:10–0:13

Transición breve a los fundamentos generales. No introducir todavía el radio del billar, su N ni sus obstáculos.

Fuentes: GPRES, p. 2; COR03, D3.

## Lámina 3 · 35 s · 0:13–0:48

En cuerpos idealizados con contacto elástico, el modelo representa la deformación mediante una superposición. Newton relaciona fuerza y aceleración. La fuerza normal es repulsiva y se anula fuera del contacto; e_ij apunta de i a j, por eso el signo negativo. No hay rozamiento ni disipación. A diferencia de discos rígidos ideales, el contacto dura un intervalo finito.

Fuentes: T04, p. 42; TP04, p. 2.

## Lámina 4 · 3 s · 0:48–0:51

Transición a cómo se integra el modelo. Esta sección describe el motor, sin introducir formatos de archivo o implementación del postproceso.

Fuentes: GPRES, p. 2; COR02.

## Lámina 5 · 20 s · 0:51–1:11

UML de las relaciones principales del motor. Los bloques con generate(), simulate() y forces() representan funciones libres, no clases inventadas. Config contiene la configuración usada por simulate; generate crea el estado inicial de Particle; simulate actualiza las partículas mediante Verlet, llama a forces y usa su ForceResult. forces devuelve fuerzas y marcas de contacto. Particle y ForceResult contienen valores Vec. Las flechas discontinuas indican dependencias y los rombos composición. Se muestran nombres y traducciones como títulos, sin atributos ni métodos dentro de las estructuras. Se omite el namespace tp4::billiard porque organiza el código pero no explica una responsabilidad del motor. Es una vista simplificada: no se muestran todas las dependencias ni los helpers de validación. Para N=650 se usa una condición inicial hexagonal aleatorizada que conserva orden residual.

Fuentes: cpp/include/tp4/billiard.hpp; cpp/include/tp4/dense.hpp; COR02, D8; revisión del estudiante 2026-10-19.

## Lámina 6 · 35 s · 1:11–1:46

La grilla de ancho 2r reduce candidatos y cada fuerza de pares se evalúa una vez. Verlet original requiere posición anterior y fuerza actual. Se inicializa la posición anterior con Taylor de segundo orden. La velocidad centrada corresponde al mismo instante que la posición. La imagen radial de la pared se recalcula cada paso. El motor conserva el primer contacto como estado histórico y guarda trayectorias; energía, histogramas y tiempos agregados se obtienen después.

Fuentes: cpp/include/tp4/billiard.hpp; T04, pp. 13–14; TP04, pp. 2–3; COR02.

## Lámina 7 · 3 s · 1:46–1:49

Transición del modelo general a la configuración particular del billar.

Fuentes: GPRES, p. 2.

## Lámina 8 · 40 s · 1:49–2:29

Presentar la geometría y las reglas antes de sus valores: señalar R, r, x0 y la velocidad en el esquema. Los obstáculos son fijos, simétricos y del mismo radio r que las partículas. El estado inicial tiene N partículas sin solapamientos, rapidez común v0 y direcciones uniformes en [0,2π). Al primer contacto con un obstáculo, una partícula pasa de fresca a usada para siempre; sigue moviéndose e interactuando, por lo que N y la densidad se conservan. Los valores numéricos y rangos se concentran en D10, sin repetir aquí la tabla de constantes. D9 define cómo medir la conversión presentada en esta lámina.

Fuentes: TP04, pp. 2–3.

## Lámina 9 · 45 s · 2:29–3:14

Fu promedia el indicador de usada entre las N partículas de UNA realización. Primero obtenemos t90 y t100 en cada corrida y recién entonces promediamos los tiempos entre realizaciones. Las barras son desvíos estándar muestrales, no errores estándar. El cruce de la curva Fu media no equivale al promedio de los cruces. Si una corrida no llega a p, su tiempo no se inventa: se explica en D25, único caso (N=650).

Fuentes: TP04, pp. 3–4; T00, p. 69; COR03, D14; python/performance_analysis.py.

## Lámina 10 · 30 s · 3:14–3:44

Izquierda, los cinco parámetros fijos del billar. Derecha, un renglón por estudio con lo que varía, el paso de integración, la cantidad de corridas y el tiempo simulado: la guía pide repeticiones y tiempos en esta sección. N ∈ [20,650] es el rango; los valores ensayados son discretos: rendimiento 20, 100, 200, 400 y 650; densidad agrega 50; mapa 20, 50, 100 y 200. Energía: seis pasos entre 2,5×10^-5 y 10^-3 s con una sola condición inicial durante 2 s, más el control de 30 s que se ve en D14. Rendimiento usa 5×10^-5 s, el paso elegido en 2.1.a para 30 s; los estudios de 60 a 600 s usan 1,25×10^-5 s. En densidad, tres corridas de N=400 se extendieron a 600 s para cerrar t100. Repeticiones y horizontes no son parámetros físicos: describen cómo se midió.

Fuentes: TP04, pp. 2–4; GPRES, p. 2; experiments/configs/; COR02; COR03

## Lámina 11 · 3 s · 3:44–3:47

Transición a resultados. Para cada estudio se ofrece contexto físico, evolución estática y resultado escalar; la comparación del oscilador es la excepción exigida.

Fuentes: GPRES, p. 2; TP04, p. 2.

## Lámina 12 · 35 s · 3:47–4:22

Única lámina del oscilador, como pide la consigna: una sola figura de ECM de posición contra la solución analítica, promediado sobre todos los pasos de una trayectoria de 5 s. Arriba, en log-log: Beeman, Verlet original y Velocity Verlet caen sobre la misma recta de pendiente 4, o sea error de orden 2 en h. Euler predictor-corrector tiene pendiente 2, es de orden 1, y queda entre 4 y 9 órdenes de magnitud arriba: es el de la teórica (T04 p. 23), que corrige con la aceleración predicha sin promediar pendientes. Abajo, el mismo ECM dividido por el de Verlet original. Beeman queda constante en ≈0,87: ≈13 % menos error en todos los pasos. Es el mejor, por un factor constante y no por un orden mayor. Velocity Verlet da 1 porque, con el amortiguamiento despejado, genera exactamente la misma sucesión de posiciones que Verlet original: es el mismo esquema escrito de otra forma. La mínima separación en h=5×10^-5 s es redondeo acumulado en 10^5 pasos (2,9×10^-10 m, frente a un error de 4,9×10^-8 m).

Fuentes: experiments/results/oscillator-summary.csv; experiments/README.md; TP04, pp. 1–2; T04, pp. 13, 17, 20, 23 y 37

## Lámina 13 · 30 s · 4:22–4:52

Una misma condición inicial N=300 se compara entre pasos, sin promediar realizaciones. Se muestra la variación porcentual con signo, 100[E(t)-E(0)]/E(0), con E(0)=3,75 J. La energía total es cinética más potencial de contactos: pares y pared, cada contacto una sola vez. La cinética sola no se conserva durante los choques. El máximo absoluto muestreado de estas curvas es el escalar de la lámina siguiente, también en porcentaje. La animación energética se retiró siguiendo la corrección del estudiante: TP04, p. 3 exige estas figuras y GPRES, p. 2 recomienda el contexto animado general.

Fuentes: experiments/results/energy-summary.csv; experiments/billar-energia.md; T04, p. 42.

## Lámina 14 · 35 s · 4:52–5:27

El umbral del 0,1 % es una decisión local, no de la consigna. Aunque h=10^-4 s pasa el ensayo corto, falla a 30 s con 0,241 %. h=5×10^-5 s da 0,0602 % y se usa en el benchmark. Los pilotos de 100 s motivaron refinar los análisis largos a 1,25×10^-5 s. En las 154 nuevas corridas de densidad y mapa el máximo muestreado fue 0,0267 %. No extrapolar la validación a un horizonte no comprobado.

Fuentes: experiments/results/billiard-step-selection.json; position-step-validation.json; density-verification.json.

## Lámina 15 · 15 s · 5:27–5:42

Mostrar la misma geometría con N bajo y alto. El ejemplo denso parte de la condición inicial del benchmark. Es contexto del aumento de trabajo por paso, no un cronometraje de la animación.

Fuentes: presentacion/.build/media-manifest.json; experiments/rendimiento-y-densidad.md.

## Lámina 16 · 40 s · 5:42–6:22

Cada punto es el tiempo medio de diez corridas de 30 s y la barra su desvío. Ambos motores se compilaron con C++20 y -O3 en la misma computadora; el reloj excluye generación y escritura. Eventos es más rápido para N=100 y 200, y paso temporal desde N=400: el cruce queda entre 200 y 400, sin fijar su N exacto. Al duplicar N de 100 a 200 y a 400, el TP4 tarda ×2,4 y ×2,7: casi lineal, porque la grilla de celdas mantiene acotado el trabajo por partícula. El TP3 tarda ×10 y ×19, porque la cantidad de eventos crece mucho más rápido que N (de 2,5×10^4 a 8,1×10^5 eventos entre N=100 y 400). Con N=650 el TP3 tarda 273 s y el TP4 7,8 s: ×35. Ahí el TP3 procesa 6,7×10^6 eventos; de N=600 a 650 sus eventos crecen ×1,7 y su tiempo ×2,1. Es una comparación descriptiva en este intervalo, no una ley asintótica. Si preguntan por el paso: aquí se usa 5×10^-5 s, que cumple el criterio en 30 s; con 1,25×10^-5 s el TP4 haría cuatro veces más pasos.

Fuentes: experiments/results/performance-summary.csv; performance-manifest.json; ../tp3-billar-metegol/experiments/results/performance-summary.csv; COR03, D16 y D22

## Lámina 17 · 15 s · 6:22–6:37

Reproducir el video de tres posiciones. Se mueve x0 simétricamente, manteniendo N=100. La fila muestra obstáculos juntos, posición intermedia y junto a la pared. Frescas azules, usadas rojas, obstáculos negros. Se muestran cinco segundos de una realización por posición, no un promedio.

Fuentes: experiments/results/position-animation-manifest.json; TP04, p. 3.

## Lámina 18 · 25 s · 6:37–7:02

Las curvas temporales son estáticas. A cada tiempo se promedian cinco fracciones Fu, con desvío entre corridas. La línea del 90 % ilustra el umbral, pero los t90 se extraen de cada historia individual. Las posiciones intermedias completan la conversión más rápido que los extremos en estos ejemplos.

Fuentes: experiments/results/position-fu.csv; COR03, D17–D21.

## Lámina 19 · 35 s · 7:02–7:37

Se recorrieron once posiciones en ambos N, cinco realizaciones por punto y 100 s. Todas alcanzaron t90. El mínimo observado es x0=0,16 m para N=100 y x0=0,3975 m para N=20. Las líneas solo guían la lectura. Los vecinos tienen dispersión y la grilla no localiza un óptimo continuo exacto. Para la pregunta de la consigna: con N=20 hay muchos menos choques entre partículas que con N=100, y el mínimo se corre de 0,16 m a 0,40 m; la posición de menor t90 depende de la frecuencia de choques. Por qué se corre hacia la pared no se midió por separado.

Fuentes: experiments/results/position-summary.csv; experiments/posicion-obstaculos.md; TP04, p. 3.

## Lámina 20 · 15 s · 7:37–7:52

Volver a N=100 sin obstáculos. Todas las partículas comienzan con rapidez unitaria; los contactos redistribuyen energía cinética entre ellas. La animación muestra partículas, no un gráfico temporal animado.

Fuentes: presentacion/.build/media-manifest.json; TP04, pp. 3–4.

## Lámina 21 · 30 s · 7:52–8:22

Cada histograma instantáneo normaliza las 100 rapideces de una corrida por N y por ancho de bin; luego se promedian diez densidades. Los bins están centrados en múltiplos de 0,1 m/s, así v0=1 m/s cae en el centro de [0,95;1,05): en t=0,1 s la barra alta son las partículas que todavía no chocaron, alrededor del 35 %. En t=0 hay una delta en v=1, marcada con la línea punteada. Desde t≈0,5 s la forma ya es parecida a la estacionaria. El ensayo de 30 s no satisfizo el criterio local de estabilidad; se amplió a 60 s y a ventanas de 10 s.

Fuentes: experiments/results/speed-snapshots.csv; speed-windows.csv; experiments/rapidez.md; COR02

## Lámina 22 · 45 s · 8:22–9:07

Izquierda: el histograma estacionario, con 10 corridas y 500 cuadros por corrida entre 10 y 60 s, y Maxwell–Boltzmann 2D con el kBT ajustado. Las barras son el desvío entre las diez densidades. Derecha: el método de la Teórica 0, el error del ajuste S en función del único parámetro kBT; su mínimo es el mejor ajuste. g_b es la integral del modelo en cada bin dividida por su ancho, sin pesos. Resultado: kBT=1,240×10^-2 J. Comparación que pide la consigna: en 2D la equipartición da una energía cinética media kBT por partícula, así que kBT se compara con m⟨v²⟩/2 medida en la ventana, 1,232×10^-2 J: difieren 0,65 %. Contra mv0²/2=1,250×10^-2 J la cinética es 1,4 % menor: esa energía está guardada en los resortes de contacto, 1,76×10^-4 J por partícula, y cinética más potencial vuelve a 1,250×10^-2 J. Los primeros 10 s se descartan porque la distribución todavía cambia; desde ahí, entre ventanas de 10 s, la distancia de variación total es menor que 0,011 y kBT cambia menos de 0,85 %. No se hizo una prueba formal de bondad de ajuste.

Fuentes: TP04, p. 4; T00, pp. 79–80; experiments/results/speed-summary.json; speed-stationary.csv; speed-objective.csv; speed-windows.csv

## Lámina 23 · 15 s · 9:07–9:22

Comparar N=50 y 650 con obstáculos juntos. La configuración física es la misma salvo N y la familia de inicialización del caso denso, ya aclarada. No describir N=650 como inmóvil: sus partículas se desplazan, aunque la conversión sea lenta.

Fuentes: presentacion/.build/media-manifest.json; experiments/densidad-y-mapa.md.

## Lámina 24 · 25 s · 9:22–9:47

Las corridas de 30 s del estudio de rendimiento no alcanzan t90 con N ≥ 200, y t100 casi nunca; por eso se simuló hasta 300 s con h=1,25×10^-5 s. N=20 y 200 llegan a conversión completa; N=650 llega en promedio a solo 4,32 % a los 300 s, y ninguna de sus diez corridas alcanza el 90 %. Las curvas son medias de Fu con bandas de desvío. El benchmark de 30 s se conserva aparte; este seguimiento no se concatena con él.

Fuentes: experiments/results/density-final-fu.csv; density-summary.csv; density-complete-cases.json; TP04, p. 4

## Lámina 25 · 40 s · 9:47–10:27

Cada círculo es la media de diez tiempos con su desvío. El triángulo es N=650: ninguna de las diez corridas llegó al 90 % en 300 s (terminan con Fu≈4 %), así que solo sabemos que su tiempo es mayor que 300 s; por eso no tiene barra. El eje vertical es logarítmico. Tres corridas de N=400 se extendieron a 600 s para observar sus últimos contactos; su t100 medio es 267±61 s. N=50 se agregó tras el indicio del mapa. Respuesta a la consigna: no hay un óptimo marcado. t90 es mínimo y casi igual entre N=20 y 100 (20 a 25 s, dentro de un desvío) y crece rápido desde N=200; t100 se comporta igual. A alta densidad las partículas casi no se desplazan: con N=650 ocupan el 77 % del área, N(r/R)², y en la animación de D23 solo convierten las vecinas a los obstáculos. A baja densidad hay pocos choques que cambien las trayectorias, y t100 queda limitado por las últimas partículas en pasar cerca del centro; es una interpretación compatible con los datos, no un resultado medido por separado.

Fuentes: experiments/results/density-complete-summary.csv; density-best-tested.json; density-followup-contract.json; density-extra-contract.json

## Lámina 26 · 30 s · 10:27–10:57

El mapa representa t90 medio frente a DOS parámetros independientes, x0 y N, por eso aquí sí corresponde un mapa de calor. Hay 44 celdas, cinco realizaciones por celda y todas alcanzaron t90 antes de 100 s. Los recuadros marcan los mínimos muestrales. Las posiciones elegidas no siguen una ley monótona con N. No confundir cinco realizaciones por celda con las diez del estudio de densidad, ni un mínimo de grilla con un óptimo continuo o estadísticamente significativo.

Fuentes: TP04, p. 4; experiments/results/density-heatmap-summary.csv; density-best-positions.json; COR03, D18.

## Lámina 27 · 3 s · 10:57–11:00

Transición breve. La conclusión solo recoge resultados que ya se mostraron, sin introducir explicaciones causales no probadas.

Fuentes: GPRES, p. 3.

## Lámina 28 · 55 s · 11:00–11:55

Recorrer las respuestas a la consigna con lo ya mostrado. Integradores (D12): Beeman es el mejor por un factor constante, ≈13 %; los tres de orden 2 se separan del Euler predictor-corrector, de orden 1. Paso (D13–D14): 5×10^-5 s alcanza para 30 s; para 100–600 s se usó 1,25×10^-5 s. Costo (D16): paso temporal crece casi linealmente y eventos mucho más rápido, por eso hay un cruce entre N=200 y 400; con N=650, eventos tarda ×35 más. Posición (D19): sí existe una posición de menor ⟨t90⟩ en la grilla, y los extremos son los más lentos; con N=100 está en 0,16 m y con N=20, con muchos menos choques, se corre a 0,40 m. La respuesta depende de la frecuencia de choques. Rapidez (D22): kBT ajustado coincide con m⟨v²⟩/2 y la diferencia con mv0²/2 es energía de contacto. Densidad (D25): la densidad óptima es baja; desde N=200 la conversión se frena y con N=650 casi se detiene. No presentar causas no medidas como conclusiones.

Fuentes: Figuras de las diapositivas 12, 14, 16, 19, 22 y 25; GPRES, p. 3; TP04, pp. 1–4

## Lámina 29 · 20 s · 11:55–12:15

Declarar las herramientas: Codex con GPT-6.1 Sol y Claude Code con Claude Opus 5.5. Se usaron para programar el motor y el post-proceso, escribir pruebas, ejecutar corridas y generar gráficos, y para un borrador de diapositivas que el grupo revisó y corrigió.

Fuentes: TP04, p. 4; registro de uso de IA en README.md
