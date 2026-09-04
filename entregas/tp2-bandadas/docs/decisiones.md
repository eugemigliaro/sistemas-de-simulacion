# Decisiones del TP2

## Confirmadas

- El motor será C++20; visualización y análisis serán Python 3, de acuerdo con `materia.yaml`.
- La entrega vive en `entregas/tp2-bandadas/` y no modifica la solución del TP1.
- Se modelan partículas puntuales en una caja cuadrada periódica de lado `L = 10` [TP02, p. 1] [T02, p. 40].
- La rapidez es `v = 0.03`, el radio de interacción `rc = 1` y el paso `dt = 1` [T02, pp. 40–42].
- Las densidades `2`, `4` y `8` corresponden a `N = 200`, `400` y `800`.
- Para estudiar `S`, una indicación oral de la cátedra agrega las densidades nominales `1/pi`, `1/(2*pi)` y `1/(3*pi)` [N-2026-08-22-densidades-s-tp2]. Con `L = 10` se adoptan los enteros más cercanos `N = 32`, `16` y `11`, cuyas densidades reales son `0.32`, `0.16` y `0.11`. Las figuras mostrarán las densidades reales para mantener una notación uniforme.
- Dos partículas distintas son vecinas cuando su distancia centro-centro periódica es menor o igual que `rc`.
- La lista geométrica del CIM no contiene a la propia partícula. Cada regla de alineación la agrega explícitamente para separar geometría de dinámica.
- Vicsek promedia los vectores dirección de todas las vecinas geométricas y de la propia partícula [T02, p. 42].
- El votante elige uniformemente entre las vecinas geométricas y la propia partícula. Esta variante fue solicitada para la resolución; `B09` contempla el caso sin vecinas y, por tanto, no coincide literalmente con este detalle [B09, p. 3].
- `eta` pertenece a `[0,1]` y cada perturbación es uniforme en `[-eta*pi, eta*pi]`, siguiendo la normalización de `B09` [B09, p. 3]. Para una comparación homogénea se aplica a ambos modelos, aunque `T02` presenta otra escala para Vicsek [T02, p. 42].
- La posición siguiente usa la velocidad anterior; el ángulo siguiente se calcula con los ángulos anteriores [T02, p. 42].
- Las actualizaciones son paralelas: ningún cálculo del tiempo `t+1` lee valores ya actualizados de otra partícula.
- Si la suma vectorial de un vecindario Vicsek se cancela numéricamente, la partícula conserva su ángulo anterior antes de agregar ruido. La fuente no define este caso degenerado; se adopta para evitar una dirección artificial.
- Los ángulos internos se normalizan al intervalo `[-pi,pi)`.
- `va` se calcula como el módulo de la suma de direcciones unitarias dividido por `N` [T02, p. 44].
- `S` es el tamaño de la mayor componente conexa de la red geométrica dividido por `N` [TP02, p. 2].
- El CIM se validará por igualdad exacta de listas contra fuerza bruta, como en el TP1.
- Con una grilla que solo revisa la celda propia y las ocho adyacentes se exige `L/M > rc`; para `L = 10` y `rc = 1`, el valor predeterminado será `M = 9`.
- Los CSV de observables y trayectoria guardan la configuración física completa (`N`, `L`, `M`, `rc`, `v` y `dt`) además de modelo, densidad, ruido y semilla. Python acepta únicamente este esquema para impedir mezclas silenciosas con corridas antiguas.
- El análisis estacionario promedia primero en el tiempo dentro de cada semilla y luego calcula media y desvío muestral entre semillas. No toma instantes correlacionados como realizaciones independientes [T00, p. 69].
- El inicio estacionario puede definirse globalmente o por combinación `(modelo, densidad, eta)`. Antes de fijarlo se inspeccionan las series y las medias de bloques temporales completos.
- La animación se sincroniza con el CSV de observables y muestra `va(t)` y `S(t)` en tiempo real. Su valor predeterminado es `5 fps`; la velocidad simulada depende también del intervalo con que se guardó la trayectoria.
- La comparación temporal del CIM con TP1 se considera orientativa porque las configuraciones físicas y el trabajo realizado por paso no son idénticos.
- El ZIP de entrega del motor se genera desde una lista blanca de fuentes C++ y excluye binarios, pruebas, resultados y herramientas Python.

## Pendientes experimentales

- Cantidad final de pasos por corrida.
- Inicio estacionario para cada región de parámetros.
- Cantidad de realizaciones independientes.
- Malla gruesa y refinada de valores de `eta`.
- Confirmar, luego de la calibración, si diez semillas alcanzan para estabilizar los desvíos. Tanto `va` como `S` se informarán con desvío muestral entre semillas; la consigna lo exige explícitamente para `S` [TP02, p. 2].
