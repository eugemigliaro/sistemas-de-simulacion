# Registro técnico — billar circular y energía (2.1.a)

Código y datos de desarrollo. Este registro no es el informe ni la presentación entregable.

## Implementación y validación física

Se implementó el sistema de [TP04, p. 2] y [TP04, p. 3]: discos con contacto normal elástico, obstáculos fijos opcionales en (±x0,0), pared circular mediante fuerza radial equivalente a su partícula imagen y conversión irreversible fresca→usada al primer contacto con obstáculo. La fuerza no incluye fricción ni disipación.

El avance usa Verlet original con posición previa de Taylor y velocidad centrada. La grilla de lado 2r se reconstruye en cada paso y los pares se visitan una sola vez; sus fuerzas se contrastaron con un oráculo independiente O(N²). El motor no calcula energía, Fu ni tiempos medios [COR02]. Guarda por partícula el paso del primer contacto para preservar esa información entre cuadros; una prueba compara guardado cada paso y cada 1000 pasos y obtiene el mismo instante de conversión.

Pasaron pruebas de inicialización reproducible sin superposiciones, módulo inicial de velocidad, energía inicial, acción y reacción, colisión binaria y duración analítica del contacto, reflexión por obstáculo, pared radial/oblicua, momento angular y energía en el contacto oblicuo, conversión irreversible, formato, entradas inválidas y detección de trayectorias incompletas. Pasaron también los tests previos del oscilador, AddressSanitizer y UndefinedBehaviorSanitizer.

La inicialización por rechazo secuencial tiene límite de intentos y puede agotarse a alta densidad. Se admite un CSV inicial externo validado. La preparación de condiciones iniciales para N>600 sigue pendiente antes del estudio de rendimiento 2.1.b; no se lo considera resuelto por este estudio.

Actualización 2026-10-16: se implementó y probó por separado la inicialización hexagonal con movimientos Monte Carlo elegida por el estudiante, y se completó el benchmark N=650. Ver [rendimiento y densidad](rendimiento-y-densidad.md). Se conserva arriba el alcance del estudio energético original.

## Protocolo de energía

N=300, sin obstáculos, R=0,51 m, r=0,0175 m, m=0,025 kg, k=10000 N/m y v0=1 m/s [TP04, p. 2]. Cada corrida comienza en la misma configuración generada con mt19937_64, semilla técnica 1 y conversión explícita de los 53 bits altos a [0,1). No se varían las condiciones iniciales al comparar pasos.

Se ensayan seis pasos menores a 0,01 s durante 2 s. Se guardan cuadros cada max(h,0,0005 s), siempre después de un número entero de pasos. La energía inicial es 3,75 J. Python calcula sobre cada cuadro energía cinética más potencial de todos los pares y pared; el código también admite potencial de obstáculos para otras corridas. Cada par se cuenta una sola vez y cada potencial es kξ²/2 [T04, p. 42].

El observable escalar propuesto es εE=max_muestreado |E(t)−E(0)|/E(0). Es un máximo temporal de cada corrida, no un promedio entre partículas o realizaciones. La tolerancia local elegida es 0,1 %; la consigna pide elegir y justificar el paso pero no impone ese umbral [TP04, p. 3].

## Resultados del barrido

| h (s) | Error energético máximo muestreado (%) |
|---:|---:|
| 0,001 | 143,9 |
| 0,0005 | 2,630 |
| 0,00025 | 0,2811 |
| 0,0001 | 0,07914 |
| 0,00005 | 0,01439 |
| 0,000025 | 0,002172 |

Los valores completos están en [el resumen CSV](results/energy-summary.csv). No son barras de incertidumbre ni estadísticas entre realizaciones. La energía total y el error frente al paso se representan en dos figuras estáticas, conforme a las correcciones de TP3 [COR03].

## Selección y comprobaciones adicionales

Se selecciona **h=0,00005 s**, el mayor candidato que pasó las comprobaciones siguientes:

- La corrida de 2 s con semilla técnica 2 obtuvo error máximo muestreado **0,02099 %**.
- La corrida prolongada de 30 s obtuvo **0,06022 %**. El candidato mayor, h=0,0001 s, alcanzó **0,2414 %** en 30 s y fue rechazado, aunque había pasado el barrido corto.
- Una corrida de 0,5 s guardada en **cada paso** obtuvo **0,01068 %**. Al submuestrear esa misma trayectoria cada 0,0005 s se obtiene **0,01034 %**: la diferencia es **0,0003434 puntos porcentuales**, menor a 0,01 puntos porcentuales, el máximo admitido en este control. Ambos máximos cumplen la tolerancia.

Se ejecutaron 12 corridas de energía: seis del barrido y tres comprobaciones para cada uno de los dos candidatos. Todas terminaron con estados finitos y trayectorias completas. Que una corrida termine no significa que conserve suficientemente la energía; por eso el estado `ok` del resumen no equivale a cumplir la tolerancia.

La decisión y sus valores exactos están en [billiard-step-selection.json](results/billiard-step-selection.json). Es una selección inicial para continuar el trabajo: dos condiciones iniciales a N=300 sin obstáculos no garantizan el mismo error a otra densidad, con otra geometría o hasta 100 s. Revalidar el criterio al preparar esos estudios; no confundir este control numérico con la convergencia de sus observables físicos.

## Artefactos y reproducción

Desde la raíz del TP4: `make energy-study` con NumPy y Matplotlib instalados. En esta sesión se usó `make energy-study PYTHON=../tp3-billar-metegol/python/.venv/bin/python`, sin modificar el TP3.

- Configuración: `experiments/configs/energy.json`.
- [Energía frente al tiempo](figures/billiard-energy-time.png) y [error frente al paso](figures/billiard-energy-error.png), inspeccionados visualmente.
- Series de energía por corrida en `experiments/results/energy-*.csv`.
- Trayectorias completas comprimidas y metadatos en `experiments/raw/energy/`, regenerables e ignorados por Git.
- [Manifiesto](results/energy-manifest.json) con comandos, constantes, generador, código, binario, versiones y hashes de cada trayectoria/serie/figura.

La demostración de animación es independiente: N=60, obstáculos en ±0,2 m, semilla técnica 7, h=0,00005 s y duración de 1 s. El [GIF local](figures/billiard-demo.gif) muestra el sistema físico, no gráficos temporales; el [fotograma final](figures/billiard-demo.png) incluye escala y leyenda. No es uno de los barridos de la consigna ni un archivo para entregar. La presentación final deberá respetar su política de enlaces [TP04, p. 1].
