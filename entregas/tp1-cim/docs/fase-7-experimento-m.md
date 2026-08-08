# Fase 7 — Experimento final de variación de M

## Objetivo

Esta fase completa el punto 3 de la consigna: para un valor intermedio y uno alto de `N`, recorre `M` desde fuerza bruta hasta el máximo geométrico, repite cada búsqueda y grafica el promedio con un desvío estándar [TP01, p. 1]. Se estudiaron por separado paredes y condiciones periódicas.

## Significado de los parámetros

- `N`: cantidad total de partículas.
- `L`: longitud del lado del dominio cuadrado.
- `M`: cantidad de celdas por lado; la grilla completa contiene `M*M` celdas.
- `L/M`: lado de una celda.
- `ri`: radio de la partícula `i`.
- `r_max`: mayor radio presente en el sistema.
- `rc`: distancia de interacción medida borde a borde.
- `seed`: semilla que permite regenerar las mismas partículas.
- `boundary`: `walls` para paredes o `periodic` para contorno periódico.
- `repetition`: número de una medición del mismo sistema y algoritmo.
- `time_ns`: tiempo de búsqueda medido en nanosegundos.
- `neighbor_pairs`: cantidad de pares no dirigidos que cumplen la condición de vecindad.
- `distance_evaluations`: cantidad de pares candidatos cuya distancia fue calculada.

## Criterio del tamaño de celda

La distancia borde a borde es:

    d_borde = d_centros - ri - rj

Dos partículas son vecinas cuando `d_borde < rc`, por lo que:

    d_centros < rc + ri + rj

Como `ri <= r_max` y `rj <= r_max`, el mayor alcance posible entre centros es:

    R = rc + 2*r_max

Si el lado de celda satisface `L/M > R`, dos centros vecinos no pueden quedar separados por una celda completa. Alcanza entonces con revisar la celda propia y las ocho adyacentes [T01, p. 23] [TP01, p. 1]. Para `L=20`, `rc=1` y `r_max=0.26`:

    R = 1 + 2*0.26 = 1.52
    M=13: L/M = 20/13 = 1.538... > 1.52, válido
    M=14: L/M = 20/14 = 1.428... < 1.52, inválido

Por eso el barrido termina en `M=13`. `M=1` se define como el caso especial de fuerza bruta.

## Selección de N

La consigna no define operacionalmente “el más alto posible”. Se adoptó como `N` alto el mayor múltiplo de 50 generado sin superposiciones para las tres semillas `42`, `31415` y `20260807`, con 100.000 intentos máximos por partícula. La condición debía cumplirse con paredes y periodicidad.

- `N=1050` se generó correctamente en las seis combinaciones.
- `N=1100` falló al menos con la semilla 42 para paredes y con la semilla 31415 para periodicidad.
- Se fijó `N_alto=1050` y `N_intermedio=500`.

La búsqueda completa y sus fallos quedan registrados en `experiments/configs/phase7-calibration.json`. Este valor es un máximo reproducible del generador aleatorio y del límite de intentos declarados, no un límite teórico de empaquetamiento.

## Protocolo

- `L=20`, `rc=1` y radios uniformes en `[0.23,0.26]` [TP01, p. 1].
- Sistemas finales generados con semilla 42.
- Ejecutable C++ compilado con `-O3 -DNDEBUG`.
- 100 repeticiones por cada `M`.
- Una validación exacta contra fuerza bruta y un calentamiento antes de medir cada `M`.
- El temporizador incluye construcción de grilla y búsqueda; excluye generación, archivos y validación.
- Media `t_media = sum(t_i)/100`.
- Desvío estándar poblacional `sigma = sqrt(sum((t_i-t_media)^2)/100)`.
- Las barras de error muestran `t_media +/- sigma`.

Las mediciones se realizaron en un Apple M2 Pro con macOS 15.7.3 y Apple clang 17.0.0. Los tiempos absolutos dependen de la máquina; la tendencia y la reducción de candidatos son los resultados comparables.

## Resultados

| Contorno | N | M con menor media | Tiempo medio | Desvío | Fuerza bruta | Aceleración | Evaluaciones en el óptimo |
|---|---:|---:|---:|---:|---:|---:|---:|
| Paredes | 500 | 13 | 222.35 us | 9.80 us | 2002.00 us | 9.00x | 6168 |
| Paredes | 1050 | 13 | 874.27 us | 31.02 us | 8490.67 us | 9.71x | 26262 |
| Periódico | 500 | 12 | 254.01 us | 13.30 us | 2226.57 us | 8.77x | 7655 |
| Periódico | 1050 | 13 | 988.26 us | 26.38 us | 9632.01 us | 9.75x | 28887 |

Los resúmenes completos están en `experiments/results/summary-m-walls.csv` y `experiments/results/summary-m-periodic.csv`. Las figuras finales son `experiments/figures/time-vs-m-walls.png` y `experiments/figures/time-vs-m-periodic.png`.

## Interpretación

Para `M=1`, fuerza bruta evalúa todos los pares: `N*(N-1)/2`. Esto produce 124.750 evaluaciones para `N=500` y 550.725 para `N=1050`.

Al aumentar `M`, cada celda contiene menos partículas y el CIM descarta pares lejanos sin calcular su distancia. En los óptimos, las evaluaciones se reducen entre 16.30 y 20.97 veces, mientras los tiempos mejoran entre 8.77 y 9.75 veces. La aceleración temporal es menor que la reducción de distancias porque construir y recorrer la grilla también tiene un costo.

Con periodicidad, `M=2` y `M=3` casi no filtran candidatos: al envolver las ocho celdas adyacentes, terminan alcanzando toda la grilla pequeña. A partir de `M=4` aparece la reducción marcada. Además, la periodicidad requiere envolver índices y aplicar imagen mínima, por lo que resulta algo más costosa que paredes.

Para periodicidad y `N=500`, `M=12` tiene la menor media, pero `M=13` difiere solo 1.48 us y sus barras de error se superponen. Para continuar con un único valor común se adopta `M=13`: es el mínimo en los otros tres casos y es estadísticamente indistinguible del mínimo periódico pequeño.

Cuando `N` aumenta de 500 a 1050 manteniendo `L=20`, también aumenta la densidad. El tiempo óptimo crece aproximadamente 3.9 veces, cercano al crecimiento de la cantidad de pares vecinos. Esto no es todavía el estudio de escalabilidad del punto 4; ese punto requiere variar `N` con al menos diez valores y comparar densidad libre contra densidad fija [TP01, pp. 1-2].

## Visualización de vecinos

Python lee `static.txt`, `dynamic.txt` y `neighbors.txt`, dibuja cada partícula con su radio real y resalta una partícula elegida y sus vecinas. El círculo punteado marca `radio_seleccionada + rc`: una partícula es vecina cuando su disco intersecta esa región.

- `experiments/figures/neighbors-walls.png`: partícula 113 y sus 15 vecinas.
- `experiments/figures/neighbors-periodic.png`: partícula 4 y sus 11 vecinas; seis aparecen junto al borde opuesto por la condición periódica.

La figura periódica conserva las coordenadas en el dominio base. Por eso algunas vecinas aparecen visualmente en el lado derecho aunque la partícula seleccionada esté sobre el borde izquierdo: ambos bordes están conectados por la imagen mínima.
