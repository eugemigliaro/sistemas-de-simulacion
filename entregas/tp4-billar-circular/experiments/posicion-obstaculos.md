# Registro técnico — posición de obstáculos (2.2)

Fecha: 2026-10-16. Registro de código, pruebas y datos; no es una presentación entregable.

## Protocolo y control numérico

Se completaron **110 corridas principales**: once posiciones entre r=0,0175 m y R−r=0,4925 m, cinco realizaciones por posición y N={100,20}, con horizonte de 100 s [TP04, p. 3]. El paso espacial es 0,0475 m. Se conserva el modelo e inicialización por rechazo del motor validado; usar la misma semilla entre geometrías no garantiza posiciones idénticas porque cambian los rechazos.

Se hicieron ocho pilotos de 100 s: ambos N, extremos del intervalo y dos pasos. Con h=0,00005 s, los máximos energéticos muestreados para N=100 fueron 0,1035 % y 0,1163 %, mayores al criterio local de 0,1 %. Con h=0,000025 s los cuatro pilotos cumplieron: máximos entre 0,02249 % y 0,04558 %. El guardado fue cada 0,05 s; se trata de máximos muestreados, no de una garantía sobre el máximo continuo.

El barrido usó uniformemente **h=0,0000125 s**, mitad del paso validado, como margen numérico. En las 110 corridas se controlaron trayectorias completas y estados inicial/final; el mayor error de energía final fue **0,01221 %**. Ese control de extremos no reemplaza un máximo temporal de cada corrida. La decisión está en [position-step-validation.json](results/position-step-validation.json). No se modificaron el motor ni los estudios anteriores.

## Qué se promedia

Python obtiene cada t90 desde el primer instante en que al menos ceil(0,9N) partículas fueron convertidas, usando first_contact_step del estado final. La resolución del cruce es h. Después se promedian **los cinco tiempos por realización**, no se busca el cruce de la curva Fu promediada [COR03]. Las barras son desvíos estándar muestrales (ddof=1).

Las evoluciones temporales promedian cinco fracciones Fu(t), consultadas cada 0,1 s. Las bandas son desvíos entre realizaciones, limitados gráficamente a [0,1]; no son intervalos de confianza ni dispersión entre partículas de una sola corrida.

Las 110 realizaciones alcanzaron Fu≥0,9 antes de 100 s: todas las medias de t90 son completas, sin censura. Una corrida (N=100, x0=r, semilla técnica 1) terminó con Fu=0,99; las otras 109 llegaron a 1. El último contacto faltante no impide observar t90.

## Resultados

| N | Posición con menor media de la grilla (m) | Media ± desvío de t90 (s) |
|---:|---:|---:|
| 100 | 0,16 | 13,6 ± 1,0 |
| 20 | 0,3975 | 9,2 ± 1,1 |

Los extremos resultaron más lentos que esos puntos:

| N | Obstáculos juntos, x0=r | Contra la pared, x0=R−r |
|---:|---:|---:|
| 100 | 25,6 ± 3,3 s | 32,8 ± 3,4 s |
| 20 | 22,9 ± 4,2 s | 23,6 ± 5,4 s |

La [figura de t90 frente a posición](figures/position-t90.png) contiene todas las medias y barras. Sus líneas guían la lectura: no son ajustes teóricos. La grilla no determina un óptimo exacto; cinco realizaciones tampoco demuestran significancia frente a cada punto vecino. Por ejemplo, N=100 y x0=0,2075 m da 14,32±0,41 s, próximo al mínimo muestral. Las barras de desvío estándar no constituyen un test de hipótesis ni incertidumbre de la coordenada del óptimo.

La [figura de Fu(t)](figures/position-fu.png) compara obstáculos juntos, posición intermedia x0=0,255 m y contacto con pared para ambos N. Los gráficos temporales son estáticos [COR03].

## Comparación con menor densidad

Al bajar N de 100 a 20, el mínimo muestral se desplaza hacia afuera y cambia la forma de la curva. A x0=0,3975 m se obtienen 16,5±2,4 s para N=100 y 9,2±1,1 s para N=20. La posición de menor media observada no es universal en estos grupos; esto no localiza el mínimo poblacional exacto.

**Inferencia mecánica compatible con el modelo:** la fuerza radial de la pared circular no ejerce torque respecto del centro; sin otros contactos, se conserva el momento angular individual. Los contactos entre partículas modifican las trayectorias individuales, mientras que desplazar los obstáculos cambia qué regiones de esas trayectorias interceptan. La reducción de N modifica la mezcla producida por encuentros entre partículas, lo que permite interpretar una respuesta distinta a la posición [TP04, p. 2] [TP04, p. 3].

No se registró directamente la frecuencia de colisiones ni se la aisló como variable independiente. No se afirma haber medido esa frecuencia o probado una relación causal exclusiva. Los datos son compatibles con esa explicación; precisar los mínimos requiere refinar posiciones y aumentar realizaciones.

## Reproducción y artefactos

Desde la raíz del TP4, con NumPy y Matplotlib:

```bash
make release
python/.venv/bin/python python/position_study.py
python/.venv/bin/python python/position_animations.py
```

En esta sesión se usó `../tp3-billar-metegol/python/.venv/bin/python`, sin modificar el TP3. El ejecutor reanuda solo con fuentes, binario y configuración compatibles; no repite casos válidos.

- [Animación local](figures/position-demo.gif) y [fotograma](figures/position-demo.png): cinco segundos de una realización N=100 en tres posiciones típicas, no un promedio. No son archivos para entregar a Campus [TP04, p. 1].
- [Resumen](results/position-summary.csv), [realizaciones](results/position-raw.csv), [curvas](results/position-fu.csv) y [mínimos muestreados](results/position-best-sampled.json).
- [Manifiesto](results/position-manifest.json) y [procedencia de animación](results/position-animation-manifest.json).
- Pilotos, trayectorias y metadatos regenerables: `experiments/raw/obstacle-position/`.

Pasaron las pruebas C++ y **17 pruebas Python**, incluidas reconstrucción de Fu en el contacto exacto, desvío muestral y censura. Las figuras y el fotograma se inspeccionaron visualmente. El código contempla corridas sin cruce aunque no aparezcan en este barrido.
