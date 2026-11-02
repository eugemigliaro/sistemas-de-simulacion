# DEL05 — descripción de las trayectorias de elusión 1 contra 1

Originales: `material/catedra/practica/elusion_1_contra_1.txt` (`DEL05`) y `material/catedra/practica/LEEME_elusion1contra1.txt` (`DEL05-LEEME`). Son los datos que la cátedra provee para el Problema 1 del TP5 [TP05, p. 2]. Este archivo es un derivado regenerable: resume formato y contenido, no reemplaza a los originales.

## Formato

- Encabezado: `# framerate: 15.0192 fps` y `# id frame x/m y/m markerID`. El intervalo de muestreo es $\Delta t_{\rm exp}=1/15{,}0192\approx0{,}0666$ s.
- Una fila por persona y cuadro: identificador, número de cuadro, posición en metros y número de marcador. 19 943 filas.
- 38 identificadores: 1–6, 9, 10, 12, 15–18, 20–30, 34–39, 42–48 y **1000**. En los 37 primeros el `markerID` coincide con el identificador. El 1000 tiene `markerID = -1` y 195 cuadros (20218–20412).
- Cuadros 19250 a 23148. Rango espacial: $x\in[0{,}08;\,11{,}40]$ m, $y\in[-0{,}69;\,3{,}73]$ m.
- No hay cuadros repetidos por persona. Hay huecos: varias personas tienen saltos de cuadro dentro de su serie.

## Contenido del LEEME

El LEEME declara 38 personas y 19 pruebas. En cada prueba, una persona sale de la fila izquierda y otra de la fila derecha (abajo a la derecha), y se cruzan cerca de $y\approx2$ m. La pareja es la que pasa más cerca, con asignación 1 a 1. Para cada prueba da los identificadores, el rango de cuadros y la distancia mínima [DEL05-LEEME].

En la prueba 2 la persona de la izquierda figura como `V?`.

## Verificaciones hechas al incorporar

Cálculos sobre los cuadros de cada persona dentro del rango de la prueba:

- **Inferencia:** `V?` es el identificador 1000. Es el único que falta para completar las 38 personas, su marcador es −1 (sin identificar) y la distancia mínima con la persona 25 en la prueba 2 da 0,88 m, igual que el LEEME.
- Cada una de las 38 personas participa en exactamente una prueba.
- Las 19 distancias mínimas del LEEME se reproducen con dos decimales, usando los cuadros comunes a ambas personas.
- Quien sale de la izquierda empieza en $x\approx0{,}5$–$0{,}8$ m y termina entre $x\approx8{,}0$ y $11{,}4$ m. Quien sale de la derecha empieza en $x\approx8{,}0$–$8{,}7$ m y termina en $x\approx0{,}1$–$1{,}5$ m.
- Las series no cubren necesariamente todo el rango de la prueba. En 12 de las 38 trayectorias el primer cuadro llega más de 5 cuadros después del inicio de la prueba (máximo 62 cuadros, unos 4 s).
- Los rangos de pruebas consecutivas se superponen. En cada rango aparecen entre 2 y 11 personas más que no forman parte de la pareja.
- Entre 92 y 252 cuadros por persona dentro de su prueba (mediana 174). La persona 36 (prueba 1) tiene 32 cuadros faltantes dentro de su tramo; la 10 (prueba 4), 16.
- Rapidez media por persona: entre 0,76 y 1,12 m/s si se divide el largo del camino por la duración (mediana 0,89), y entre 0,59 y 1,07 m/s si se divide el desplazamiento neto (mediana 0,78). Para una misma persona, el primer valor llega a ser 1,33 veces el segundo.
- La rapidez estimada con los dos primeros cuadros va de 0 a 0,93 m/s: varias personas arrancan casi detenidas.

## Tabla por prueba

| Prueba | Izq. | Der. | Cuadros | Dist. mín. (m) |
|---:|---:|---:|---|---:|
| 1 | 3 | 36 | 20068–20261 | 0,91 |
| 2 | 1000 (`V?`) | 25 | 20208–20391 | 0,88 |
| 3 | 43 | 1 | 20370–20540 | 0,60 |
| 4 | 10 | 5 | 20527–20734 | 0,54 |
| 5 | 4 | 12 | 20632–20853 | 0,49 |
| 6 | 9 | 6 | 20778–20971 | 0,80 |
| 7 | 20 | 44 | 20910–21142 | 0,56 |
| 8 | 27 | 37 | 21066–21298 | 0,83 |
| 9 | 16 | 39 | 21228–21380 | 0,78 |
| 10 | 17 | 42 | 21435–21635 | 0,63 |
| 11 | 23 | 24 | 21536–21804 | 0,91 |
| 12 | 22 | 18 | 21760–21960 | 0,64 |
| 13 | 15 | 35 | 21877–22098 | 0,87 |
| 14 | 30 | 28 | 22011–22206 | 0,92 |
| 15 | 46 | 34 | 22278–22481 | 0,76 |
| 16 | 47 | 48 | 22402–22639 | 0,68 |
| 17 | 2 | 45 | 22561–22726 | 0,57 |
| 18 | 26 | 21 | 22722–23000 | 0,57 |
| 19 | 29 | 38 | 22902–23074 | 0,61 |

Ver las consecuencias para la calibración en [Elusión, evacuación y TP5](../../wiki/temas/elusion-evacuacion-y-tp5.md).
