# TP3 — Billar-Metegol

Resolución del Trabajo Práctico 3 de Sistemas de Simulación: dinámica molecular
dirigida por eventos sobre una mesa de metegol. El motor está implementado en
C++20; la animación y el análisis son programas independientes en Python 3, como
exige la consigna [TP03, p. 1].

## Estado

En cierre. Entrega: 28 de septiembre de 2026, 13:00. Solo faltan publicar las
dos animaciones y colocar sus URL explícitas en la presentación.

Fases completadas:

- [x] Fase 1 — geometría, modelo y validación de configuraciones
- [x] Fase 2 — generación de condiciones iniciales e I/O
- [x] Fase 3 — predicción y resolución de colisiones
- [x] Fase 4 — motor ingenuo (oráculo de correctitud)
- [x] Fase 5 — motor con cola de prioridad
- [x] Fase 6 — post-proceso (Fu, t90, DCM, D)
- [x] Fase 7 — experimentos 1.1, 1.2 y 1.3
- [ ] Fase 8 — animación y entregables (solo faltan publicar los videos y pegar sus URL)

## Separación de responsabilidades

La cátedra marcó como error importante en el TP2 que el motor calculara
observables dentro del bucle principal [COR02]. Acá la división es estricta:

| Componente | Responsabilidad |
|---|---|
| Motor C++ | Genera estado: tiempo, posiciones, velocidades y color |
| Post-proceso Python | `Ng(t)`, `Fu(t)`, `t90`, DCM, ajuste `E(c)`, `D` y barras de error |
| Animación Python | Módulo independiente que lee el archivo de texto |

El color fresca/usada es **estado**, no observable: la consigna pide imprimirlo
junto a posiciones y velocidades [TP03, p. 2].

## Convenciones principales

- Mesa de `L = 1.20` m por `W = 0.68` m; arcos de `d = 0.20` m centrados en las
  paredes cortas. Condición de gol: `|y - W/2| <= d/2` [TP03, p. 2].
- Partículas de `r = 0.0175` m, `m = 0.025` kg, `v0 = 1` m/s. Todas las
  colisiones son elásticas.
- Obstáculos circulares fijos de masa infinita, con `Rk >= r`, íntegramente
  dentro del dominio y sin solaparse [TP03, p. 3].
- El DCM se ajusta como `<|Δr|²> = 4Dt` (desplazamiento vectorial completo).

Las decisiones completas están en [`docs/decisiones.md`](docs/decisiones.md).

## Compilación y pruebas

```bash
make python-env   # una sola vez: crea python/.venv con numpy y matplotlib
make test         # tests de C++ y de Python
make sanitize
```

```bash
make debug && ./cpp/build/debug/tp3 --version
```

## Uso

Generar una condición inicial sobre la mesa vacía:

```bash
./cpp/build/debug/tp3 generate --n 100 --seed 1 --output data/generated/init.txt
```

Con obstáculos, desde un archivo con una línea `xk yk Rk` por obstáculo:

```bash
./cpp/build/debug/tp3 generate --n 100 --seed 1 --config experiments/configs/ejemplo.txt
```

Si la configuración no permite ubicar las `N` partículas, el motor falla con
error en lugar de reintentar para siempre o bajar `N` en silencio. La
restricción (ii) del punto 1.2 pone esa carga del lado de la configuración
[TP03, p. 3].

## Simulación

Correr la dinámica dirigida por eventos y escribir la trayectoria:

```bash
make release
./cpp/build/release/tp3 simulate \
  --n 100 --seed 1 --tmax 30 \
  --config experiments/configs/ejemplo.txt \
  --save-every 50 \
  --output data/generated/run.txt
```

`--engine` elige el motor: `queue` (default) o `naive`.

`--tmax` es el reloj absoluto de corte, `--save-every` la cadencia de cuadros
periódicos (`0` los desactiva) y `--max-events` un tope de seguridad. Ninguno
de los tres es un parámetro físico: el sistema no cambia de comportamiento al
variarlos [COR02].

Por salida de error va un resumen de una línea con los eventos procesados, los
cuadros escritos, el tiempo final y **el tiempo de ejecución en segundos**, que
es lo que mide el punto 1.1:

```text
engine queue particles 100 seed 1 events 25226 frames 96 final_time 30 runtime_seconds 0.0773757
```

Está separado de la trayectoria justamente para poder redirigirla a
`/dev/null` cuando solo interesa medir el tiempo de ejecución.

## Motores

Hay dos, y comparten la predicción y la resolución de choques:

| Motor | `--engine` | Costo por evento | Para qué |
|---|---|---|---|
| ingenuo | `naive` | `O(N² + N·K)` | oráculo de correctitud y curva lenta del punto 1.1 |
| con cola | `queue` (default) | `O(N log E)` | producción |

El ingenuo recalcula todos los tiempos de choque después de cada evento. El de
cola los agenda una sola vez y, después de cada choque, reagenda únicamente los
de las partículas que participaron; los eventos que quedaron invalidados no se
borran de la cola, se descartan al extraerlos comparando los contadores de
choque guardados contra los actuales [B16, pp. 1, 4].
**El ZIP de entrega incluye únicamente el motor final** [TP03, p. 1].

Medido en release sobre la mesa vacía hasta `tf = 30` s:

| `N` | eventos | `naive` (s) | `queue` (s) | aceleración |
|---|---|---|---|---|
| 25 | 2 159 | 0,0075 | 0,0022 | 3× |
| 50 | 6 729 | 0,082 | 0,011 | 7× |
| 100 | 25 226 | 1,27 | 0,077 | 16× |
| 200 | 115 787 | 24,7 | 0,72 | 34× |
| 400 | 811 525 | — | 10,9 | — |

El ingenuo va como `N⁴` (los eventos crecen como `N²` y cada uno cuesta `N²`);
el de cola como `N³` (los mismos `N²` eventos, pero cada uno cuesta `O(N)`
reagendados). Por eso la aceleración crece con `N` en vez de ser un factor
constante.

### Por qué los dos motores no dan la misma trayectoria

Los dos son correctos y **aun así divergen**. Predicen desde estados de
referencia distintos: el ingenuo recalcula todo desde el instante actual,
mientras que la cola conserva tiempos calculados en un instante anterior. Son
iguales en aritmética exacta, pero difieren en el último bit. Un gas de discos
rígidos es caótico, así que esa diferencia de `10⁻¹⁶` se amplifica
exponencialmente:

| eventos | separación máxima entre motores |
|---|---|
| 1 | 0 (exacta) |
| 10 | `5·10⁻¹⁶` m |
| 100 | `9·10⁻¹⁵` m |
| 200 | `6·10⁻¹³` m |
| 500 | `3·10⁻⁸` m |
| 1 000 | 0,24 m |
| 2 000 | 0,94 m (tamaño de la mesa) |

Alrededor de una década por cada 60 eventos, hasta saturar en el tamaño del
dominio. **No tiene sentido validar la cola exigiendo la trayectoria completa
del ingenuo.** La validación es en tres niveles:

1. acuerdo exacto en el primer evento y a `10⁻¹⁰` en los primeros 100, mientras
   el redondeo todavía es despreciable;
2. invariantes físicas en corridas largas: energía, contención y no
   solapamiento, en ambos motores;
3. acuerdo estadístico: `<t90>` compatible dentro del error estándar.

Esto no es un defecto de la implementación, es una propiedad del sistema, y es
además la razón de fondo por la que el TP pide promediar sobre realizaciones en
lugar de mirar una corrida.

## Formato de la trayectoria

```
# tp3-trajectory 1
# length 1.2
# ...
# max_time 30
# max_events 0
# obstacle 0.6 0.34 0.05
# frame_columns x y vx vy state
frame 0 0 0 initial
0.801620613 0.042329024 0.154643474 0.987970342 0
...
```

Cada cuadro trae una línea por partícula, en orden de id. El estado es `0` para
fresca y `1` para usada. El motivo (`initial`, `periodic`, `color`, `final`)
indica por qué se guardó el cuadro: los cuadros `color` dejan que el
post-proceso reconstruya `Ng(t)` y `t90` con precisión exacta sin que el motor
cuente goles, y el cuadro `final` marca hasta dónde llegó el reloj, que es lo
que distingue una realización que no alcanzó `Fu = 0.9` de un archivo truncado.

Con esto alcanza para el análisis: en una corrida de `N = 100` con tres
obstáculos y `tmax = 30` s, los 95 cuadros `color` dan directamente
`t90 = 19,40` s sin que el motor calcule un solo observable.

`max_time` y `max_events` los escribe solo `simulate`. Sirven para distinguir
una realización que llegó a `tmax` sin alcanzar `Fu = 0.9` de una cortada por
el tope de eventos.

## Post-proceso

El paquete `python/src/tp3analysis` lee las trayectorias y escribe tablas CSV.
No corre simulaciones ni grafica.

```bash
export PYTHONPATH=python/src
PY=python/.venv/bin/python

# t90 por realización y su promedio (con desvío y error estándar)
$PY -m tp3analysis t90 data/generated/run_seed*.txt --output experiments/results/t90.csv

# Ng(t) y Fu(t) de una realización, para graficar
$PY -m tp3analysis goals data/generated/run_seed1.txt --output experiments/results/goals.csv

# DCM con múltiples orígenes y coeficiente de difusión
$PY -m tp3analysis diffusion data/generated/run_seed*.txt \
  --window 0.3 1.5 --bin-width 0.02 --max-lag 5 \
  --output-dir experiments/results/diffusion
```

Todas las realizaciones que se promedian tienen que ser del mismo sistema y
tener semillas distintas; si no, el comando falla.

| Comando | Qué calcula | Salida |
|---|---|---|
| `t90` | `t90` exacto por realización, `<t90>` sobre las que alcanzaron el 90 %, goles al final (criterio de desempate de la competencia) | una fila por realización |
| `goals` | `Ng(t)` y `Fu(t)` como escalones en los instantes de gol | `time, goals, used_fraction` |
| `diffusion` | DCM por realización y promediado, `D` con sus tres estimaciones | `msd_seed*.csv`, `msd_pooled.csv`, `ec_*.csv` (curvas `E(c)`), `diffusion.csv` |

Para el DCM, `--save-every 10` con `N = 100` da un cuadro cada ~12 ms, de
sobra para una ventana de ajuste de décimas de segundo. Los criterios están en
[`docs/decisiones.md`](docs/decisiones.md#post-proceso-fase-6).

## Resultados y entrega

El protocolo, los resultados numéricos y su interpretación están documentados
en [`experiments/RESULTADOS.md`](experiments/RESULTADOS.md). La configuración
elegida tiene un obstáculo en `(0.60, 0.34)` de radio `0.34 m` y redujo
`<t90>` un 31,5 % respecto de la mesa vacía en el barrido realizado.

```bash
make assets   # figuras, fotogramas y MP4 locales
make package  # PDF, Config.txt y ZIP del motor (< 100 KB)
```

Los MP4 no se incluyen en la entrega: deben publicarse en YouTube o Vimeo y
sus enlaces explícitos deben incorporarse al PDF [TP03, p. 1].
