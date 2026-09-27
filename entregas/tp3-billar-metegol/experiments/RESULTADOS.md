# Resultados experimentales del TP3

Todos los resultados se generaron con el motor C++ en modo `release`. Las
semillas, mediciones individuales y resúmenes se preservan en
`experiments/results/`; las trayectorias voluminosas quedan en
`experiments/raw/` y se regeneran con `scripts/run_experiments.py`.

**Regeneración del 2026-09-26.** El barrido de un disco reutilizaba
trayectorias guardadas por una versión anterior del motor, así que no se
reproducía semilla por semilla. Se borraron y se recalcularon con el motor
actual. Los números cambiaron dentro del error, y hoy todas las tablas se
reproducen exactamente con las semillas indicadas.

## 1.1 Tiempo de ejecución

La cátedra pidió subir `N` hasta que la simulación deje de terminar, con un
corte a los 10 minutos que cuenta como "no terminó". Se simula la mesa vacía
hasta `tf = 30 s` con el motor de cola, con diez semillas por `N`, en forma
secuencial y sin otros procesos pesados (`scripts/run_experiments.py
saturation`).

- Hasta `N = 430`, las posiciones son al azar. El muestreo por rechazo se traba
  cerca de 446 partículas (fracción de área ~0,53): con 10⁸ intentos no ubica
  la 447. En esa densidad el sistema todavía es un líquido de discos y el
  motor tarda ~30 s: no se satura.
- Desde `N = 450`, las partículas ocupan sitios elegidos al azar de la red
  triangular más espaciada que las contiene (`--layout triangular`). Esto
  llega hasta el empaquetamiento compacto (737 partículas), donde la
  frecuencia de choques diverge.
- La búsqueda se detiene en el primer `N` con dos corridas sin terminar.

| `N` | Posiciones | Tiempo de ejecución [s] |
|---:|---|---:|
| 100 | al azar | 0,08 |
| 200 | al azar | 0,78 ± 0,01 |
| 300 | al azar | 3,75 ± 0,13 |
| 400 | al azar | 15,6 ± 0,4 |
| 430 | al azar | 22,1 ± 0,2 |
| 450 | red triangular | 28,3 ± 0,3 |
| 500 | red triangular | 55,8 ± 0,5 |
| 550 | red triangular | 107 ± 2 |
| 600 | red triangular | 170 ± 3 |
| 625 | red triangular | 248 ± 9 |
| 650 | red triangular | 357 ± 7 |
| 675 | red triangular | 567 ± 11 |
| 700 | red triangular | no termina en 10 min (2 de 2) |

**El límite está entre 675 y 700 partículas.** Los dos métodos empalman sin
salto (`430` al azar ≈ `450` en red). Cerca del empaquetamiento compacto la
cantidad de eventos por segundo simulado se dispara, y también el costo de
cada evento, que es `O(N)` por los reagendados.

**Corridas repetidas.** El costo por evento es un buen control: a igual `N`,
todas las semillas procesan casi la misma cantidad de eventos. Catorce corridas
(las diez de `N = 430` y una de `300`, `350` y `650`) tardaron hasta el doble
por evento, porque coincidieron con compilaciones en la misma máquina. Se
borraron y se repitieron en aislamiento. Los datos contaminados quedaron
fuera de la tabla.

Resultados: `experiments/results/runtime_saturacion.csv`.

Protocolo anterior, hasta `N = 400` y solo al azar: `t ∝ N^3,30` en
`N >= 50` y `11,27 ± 0,04 s` para `N = 400` (`runtime.csv`).

## 1.2 Exploración de configuraciones

Se exploró sistemáticamente un único obstáculo circular sobre el eje
longitudinal de la mesa. Se variaron su posición `xk` y su radio `Rk`, se fijó
`yk = W/2 = 0,34 m`, y se compararon todos los puntos contra la mesa vacía. Se
usaron `N = 100`, `tmax = 100 s` y quince semillas independientes por punto,
por encima del mínimo de cinco realizaciones [TP03, p. 3].

La mejor configuración medida fue:

```text
0.60 0.34 0.34
```

| Configuración | `<t90>` [s] | Desvío [s] | Error estándar [s] |
|---|---:|---:|---:|
| Mesa vacía | 21,83 | 2,62 | 0,68 |
| Mejor disco | 15,15 | 1,73 | 0,45 |

La reducción de la media fue del `30,6 %`; también disminuyó la dispersión. El
obstáculo está contenido en el dominio, es tangente a las paredes largas y
permite generar las cien partículas.

### Disco central con radio variable (presentación)

Disco en `(0,60; 0,34)` con 11 radios entre `0,05` y `0,34 m`, más la mesa
vacía, con 20 semillas cada uno (`scripts/barridos_presentacion.py disco`).
`<t90>` baja casi de forma monótona con el radio, de `22,92 ± 0,53 s` (vacía)
a `15,33 ± 0,47 s` (`R = 0,34 m`). La figura muestra `<Fu(t)>` como mapa en
función de `t` y `R`.

### Segunda etapa: salas hechas con muchos discos

El óptimo anterior quedó en el borde del espacio explorado (`Rk = W/2`), así
que se pasó a `K > 1`. Todas las formas se construyen con discos de radio `r`,
se rellena el exterior y se verifica que no queden bolsillos sin arco. El
método está en `docs/decisiones.md` y el código en
`scripts/busqueda_elipses.py`. Cada búsqueda tuvo barrido, refinamiento y una
reevaluación final con semillas nuevas y `tmax = 100 s`.

| Familia | Mejor `<t90>` [s] | Semillas de la medición |
|---|---:|---|
| Elipses con focos en el centro y en el arco | 19,34 ± 0,36 | 40 nuevas |
| Solo una pared de discos en `x = L/2` | 21,43 ± 0,49 | 40 nuevas |
| Elipses separadas hacia los arcos (`b = 0,30`, `δ = 0,39`) | 13,76 ± 0,18 | 100 nuevas |
| **Superelipse (adoptada)** | **13,61 ± 0,17** | 100 nuevas |
| Disco único `(0.60, 0.34, 0.34)` | 15,60 ± 0,17 | 100 nuevas |

Conclusiones del punto:

- El efecto de foco de la elipse no actúa: variar la precisión del espejo no
  cambia `<t90>`.
- Separar las mitades casi no ayuda. Lo que baja `<t90>` es sacar área lejos
  de los arcos y dejar ancha la entrada al arco.
- Elipse separada y superelipse son equivalentes dentro del error. Todas las
  formas buenas son salas de ~0,27 m de fondo abiertas a casi todo el ancho de
  la pared corta.

La configuración entregada es la superelipse de profundidad `0,277 m`,
semiancho `0,268 m`, exponente `4,72` y centro `0,113 m` detrás de la pared,
con 87 obstáculos. Mejora un 12,8 % al disco único y un 40 % a la mesa vacía.
Está en `experiments/configs/SdS_TP3_2026Q2G07CS_Config.txt` [TP03, p. 3].

### Profundidad de la sala

Con semiancho, exponente y retroceso fijos, se barrió la profundidad entre
`0,17` y `0,40 m`, con 24 semillas por punto y `tmax = 100 s`
(`scripts/barridos_presentacion.py profundidad`). Aparece un óptimo plano entre
`0,23` y `0,30 m` (`13,7`–`13,9 s`), y la elegida (`0,277 m`) cae adentro.
Hacia salas más chicas crece la densidad (`16,5 s` en `0,17 m`); hacia salas
más grandes vuelve el área lejos del arco (`14,9 s` en `0,40 m`).

## 1.3 Difusión

Para cada configuración se hacen diez corridas de `8 s`, guardando un cuadro
cada veinte eventos. La cátedra pidió el DCM en función del **tiempo**, así que
se calcula `DCM(t) = <|r(t) − r(0)|²>` con origen en `t = 0`, agrupado en
intervalos de `0,05 s`. Antes se usaban cinco corridas y múltiples orígenes en
función del desfasaje. Se mantiene la ventana común de ajuste `[0,3; 1,5] s` y
el barrido de `E(c)` de la Teórica 0 [TP03, p. 3] [T00, pp. 79-81].

Para el mejor disco se obtuvo `<D> = (0,0071 ± 0,0008) m²/s`, donde la
incertidumbre es el desvío entre semillas. En ese barrido, la correlación de
Pearson entre `<D>` y `<t90>` fue `r = 0,20`.

### Configuraciones de la segunda etapa

Se aplicó el mismo protocolo a las 158 configuraciones de los barridos
elípticos y superelípticos, más la adoptada y la mejor elipse separada. Con
las 36 del disco único y la mesa vacía suman 195. Las tablas están en
`experiments/results/elipses/difusion_todas.csv`.

| Configuración | `<D>` [m²/s] | `<t90>` [s] |
|---|---:|---:|
| Mesa vacía | 0,0223 ± 0,0019 | 21,83 |
| Disco único | 0,0071 ± 0,0008 | 15,15 |
| Elipse separada | 0,0057 ± 0,0006 | 13,76 |
| **Superelipse (adoptada)** | **0,0053 ± 0,0006** | **13,61** |

| Familia | Configuraciones | Pearson `r(D, t90)` |
|---|---:|---:|
| Disco único | 36 | +0,20 |
| Elipses con focos fijos | 26 | −0,72 |
| Elipses separadas | 54 | +0,47 |
| Superelipses | 78 | +0,32 |
| Todas | 195 | +0,38 (Spearman +0,61) |

No hay una relación universal entre `D` y `t90`: la correlación cambia de
signo según la familia. Globalmente es positiva, lo contrario de "más difusión,
goles más rápidos". Las mejores configuraciones son salas chicas y densas,
donde `D` es bajo. Las elipses con focos fijos tienen correlación negativa
porque las chicas son tubos angostos que además tapan parte del arco.

**Salvedad del ajuste**: en las salas chicas el DCM ya se curva dentro de la
ventana `[0,3; 1,5] s`, porque las partículas empiezan a sentir las paredes. En
la adoptada, `DCM/4t` baja un ~25 % a lo largo de la ventana. Se mantuvo la
ventana común para poder comparar. El `D` de estas geometrías es entonces un
coeficiente efectivo que mezcla difusión y confinamiento.

## Reproducción

```bash
make python-env
make test
make experiments                                   # 1.1 viejo, barrido de un disco y D
python/.venv/bin/python scripts/run_experiments.py saturation   # 1.1 nuevo: horas, sola
python/.venv/bin/python scripts/barridos_presentacion.py todo   # disco, profundidad, animaciones
python/.venv/bin/python scripts/busqueda_elipses.py difusion    # D de las 195 configuraciones
make assets                                        # figuras de la presentación
```

Las animaciones de la presentación son `videos/anim-goles-vacia.mp4` y
`videos/anim-goles-elegida.mp4`: van en tiempo real, con `Fu(t)` debajo y `t90`
marcado. La consigna exige publicarlas en YouTube o Vimeo y colocar las URL
explícitas en el PDF, sin entregar los MP4 [TP03, p. 1].
