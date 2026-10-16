# Registro técnico — rendimiento 2.1.b y densidad 2.4.a

Fecha: 2026-10-16. Es un registro de código, pruebas y datos, no una presentación entregable.

## Protocolo y procedencia

Se ejecutaron 110 corridas completas de tf=30 s en la misma computadora, identificada localmente como **Apple M5 Pro**: 50 del TP4 y 60 del TP3. Cada N tiene diez realizaciones, con semillas técnicas 1–10. TP4 usa el billar circular con obstáculos en contacto, x0=r, h=0,00005 s y N={20,100,200,400,650}. TP3 usa su mesa vacía y el rango histórico N={10,25,50,100,200,400}. Se cumple el requisito N>600 del TP4 [TP04, p. 3].

El harness enlaza los motores reales con C++20, -O3 y -DNDEBUG. No se modifica el TP3 ni se sobrescriben sus resultados históricos. Se cronometra la llamada al simulador con steady_clock; se excluyen generación y escritura para ambos. La copia del último estado en el callback del TP4 queda dentro de su llamada; la escritura posterior queda fuera. Se incluyen las verificaciones y la planificación que cada motor realiza internamente. Se ejecuta una corrida por vez, sin paralelismo entre mediciones.

Estos valores del TP3 fueron **recalculados**, no mezclados con sus mediciones históricas, que incluían serialización a /dev/null. La comparación corresponde a los dos sistemas de la consigna, con áreas casi iguales; no prueba dos motores sobre una geometría idéntica. Las diferencias de frecuencias de contacto y de implementación también influyen en el costo.

## Configuraciones densas

El estudiante eligió red hexagonal más aleatorización Monte Carlo. Para N=650 se sortean orientación/traslación y sitios de una red válida; se hacen 500 barridos de N propuestas de desplazamiento sin solapamientos y finalmente se sortean direcciones de rapidez unitaria. Para N≤400 se conserva el rechazo secuencial.

La configuración piloto de N=650 y semilla 1 tiene 711 sitios candidatos, aceptación del 8,78 % y desplazamiento RMS aproximado de 0,01089 m respecto de los sitios iniciales. Su orden hexagonal global de seis vecinos es aproximadamente 0,572 y el promedio del módulo local aproximadamente 0,706: **queda orden residual**. No se afirma equilibrio ni muestreo uniforme de todas las configuraciones posibles. El cambio de familia de inicialización debe considerarse al interpretar N=650; no atribuir todo cambio únicamente a densidad.

Se verificaron N exacto, paredes/obstáculos/pares sin superposiciones, velocidades, reproducibilidad y variación entre semillas. Las pruebas C++ y Python y los sanitizadores pasaron. El piloto denso de 0,5 s con salida cada 10 pasos dio error energético máximo muestreado aproximado 0,00904 %. El piloto de 30 s dio diferencia relativa de energía final aproximada 0,04089 %. Entre las 50 corridas del benchmark, el mayor error de energía **final respecto de inicial** fue 0,08797 %, inferior al criterio local del 0,1 %; no confundir este control de extremos con un máximo temporal de todas las corridas.

## Rendimiento

Media ± desvío estándar muestral (ddof=1), calculados entre diez realizaciones por N, en segundos:

| N | TP4: paso temporal | TP3: eventos |
|---:|---:|---:|
| 20 | 0,144 ± 0,005 | No medido en este N |
| 100 | 0,617 ± 0,006 | 0,0492 ± 0,0004 |
| 200 | 1,490 ± 0,011 | 0,488 ± 0,004 |
| 400 | 3,90 ± 0,05 | 8,49 ± 0,06 |
| 650 | 7,145 ± 0,025 | No medido en este N |

La [figura de comparación](figures/runtime-comparison.png) incluye también los N menores del TP3 y las barras de desvío estándar. En el rango común, eventos es más rápido en N=100 y 200, mientras que paso temporal es más rápido en N=400. Se observa un cruce entre 200 y 400, pero estos puntos no determinan el N exacto del cruce. No se ajustó una exponencial ni se atribuyó una ley asintótica a partir de pocos puntos [COR03].

El paso temporal realiza 600000 pasos para todos los N; aumenta el trabajo de búsqueda y contacto al aumentar N. En eventos, además del costo de gestionar/recalcular candidatos, crece la frecuencia de choques con la densidad. Esta explicación de implementación no reemplaza las mediciones ni demuestra por sí sola un exponente de escalamiento.

## Densidad: datos observados y censura

Se reutilizaron las 50 salidas del TP4. Cada estado final conserva first_contact_step por partícula, por lo que el post-proceso obtiene los primeros cruces de Fu a 0,9 y 1 con resolución h. Primero se calcula cada tiempo por realización; después se agregan realizaciones [COR03].

| N | Densidad (m⁻²) | No alcanzan t90 en 30 s | No alcanzan t100 en 30 s | Promedio de Fu(30 s) |
|---:|---:|---:|---:|---:|
| 20 | 24,48 | 0/10 | 7/10 | 0,950 |
| 100 | 122,38 | 1/10 | 10/10 | 0,929 |
| 200 | 244,76 | 10/10 | 10/10 | 0,8435 |
| 400 | 489,52 | 10/10 | 10/10 | 0,5413 |
| 650 | 795,47 | 10/10 | 10/10 | 0,02369 |

Para N=20, la media observada completa de t90 es **21,1 ± 4,2 s** (desvío entre diez realizaciones). En N=100, la media condicional de las nueve que sí alcanzan el umbral es 25,06 s; **no es la media completa**. La cota inferior de la media completa es 25,56 s. En N≥200 la cota inferior de la media de t90 es 30 s. Por tanto, entre estos grupos muestreados N=20 tiene la menor media muestral de t90 incluso comparándola con las cotas de los otros grupos; esto no identifica un óptimo global ni prueba una diferencia poblacional con un análisis de incertidumbre.

No se puede ordenar las medias completas de t100 a partir de estas salidas: incluso N=20 tiene siete tiempos desconocidos. Se conserva la media condicional de los tres observados (21,91 s), claramente identificada, y una cota inferior de la media completa (27,57 s); no se reporta ninguna de ellas como la media ordinaria de diez corridas.

La [figura de densidad](figures/conversion-vs-density.png) diferencia media ± desvío estándar de **cota inferior**. Los triángulos no son tiempos medidos ni reemplazos de los tiempos desconocidos. Los triángulos huecos de t90 y pequeños rellenos de t100 permiten ver las cotas coincidentes.

**Actualización del cierre de 2.4.a–b:** las salidas obligatorias de 30 s y sus limitaciones se conservan. Se agregaron corridas refinadas hasta 300 s, tres seguimientos selectivos N=400 a 600 s, un grupo exploratorio N=50 con diez realizaciones y el mapa de posiciones. El [registro de cierre](densidad-y-mapa.md) contiene las medias completas para los N ensayados hasta 400, y censura/cotas para N=650, que no alcanza los umbrales a 300 s. Los nuevos mínimos muestrales dependen del criterio: t90 favorece N=50 en la grilla ampliada y t100 favorece N=20. No se altera el horizonte ni el cronometraje del benchmark ni se afirma aceptación oficial de un tratamiento de censura sin aclaración de cátedra [TP04, p. 3] [TP04, p. 4].

## Reproducción, resultados y verificaciones

Desde la raíz del TP4, con NumPy y Matplotlib disponibles:

```bash
python/.venv/bin/python python/performance_study.py
python/.venv/bin/python python/performance_plot.py
```

En esta sesión se usó el intérprete ya instalado `../tp3-billar-metegol/python/.venv/bin/python` y `TP4_CPU_DESCRIPTION='Apple M5 Pro'`, dato obtenido con consulta autorizada. No usar esa descripción en otra computadora sin verificarla. El segundo comando revisa únicamente la figura de censura y actualiza su procedencia; no repite el benchmark.

- [Configuración](configs/performance.json) y [contrato](results/performance-contract.json).
- [Resumen de rendimiento](results/performance-summary.csv), [densidad](results/density-summary.csv) y [tiempos por realización](results/density-raw.csv).
- [Manifiesto](results/performance-manifest.json): fuentes, compilador, hardware, comandos y hashes; [checkpoints por realización](results/performance-cases/).
- Trayectorias inicial/final y metadatos en `experiments/raw/performance/`, regenerables e ignorados por Git.

Se probaron los umbrales de conversión, el desvío muestral y la ausencia de medias ordinarias ante censura. Los checkpoints permiten reanudar únicamente con la misma huella de protocolo/fuentes/hardware y validan la integridad de las trayectorias. Las figuras fueron inspeccionadas visualmente.
