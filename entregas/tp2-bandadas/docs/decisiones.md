# Decisiones del TP2

## Confirmadas

- El motor será C++20; visualización y análisis serán Python 3, de acuerdo con `materia.yaml`.
- La entrega vive en `entregas/tp2-bandadas/` y no modifica la solución del TP1.
- Se modelan partículas puntuales en una caja cuadrada periódica de lado `L = 10` [TP02, p. 1] [T02, p. 40].
- La rapidez es `v = 0.03`, el radio de interacción `rc = 1` y el paso `dt = 1` [T02, pp. 40–42].
- Las densidades `2`, `4` y `8` corresponden a `N = 200`, `400` y `800`.
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

## Pendientes experimentales

- Cantidad final de pasos por corrida.
- Inicio estacionario para cada región de parámetros.
- Cantidad de realizaciones independientes.
- Malla gruesa y refinada de valores de `eta`.
- Convención definitiva de barras para `va`; para `S` la consigna pide desvío [TP02, p. 2].
