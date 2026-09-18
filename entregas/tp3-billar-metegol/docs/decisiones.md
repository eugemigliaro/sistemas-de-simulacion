# Decisiones del TP3

## Confirmadas

### Arquitectura

- El motor es C++20 y el post-proceso y la animación son Python 3, de acuerdo con `materia.yaml`.
- La entrega vive en `entregas/tp3-billar-metegol/` y no modifica las soluciones del TP1 ni del TP2.
- **El motor solo genera el estado del sistema** (tiempo, posiciones, velocidades y color). Todos los observables (`Ng`, `Fu`, `t90`, DCM, `D`) se calculan en un post-proceso aparte sobre el archivo de salida. La cátedra marcó lo contrario como error importante en el TP2 [COR02].
- El color fresca/usada **es estado, no observable**: la consigna pide imprimirlo junto a posiciones y velocidades [TP03, p. 2]. El motor lo mantiene; no cuenta goles ni calcula fracciones.
- La animación se ejecuta como módulo independiente y toma el archivo de texto como entrada [TP03, p. 1].
- `prediction` y `resolution` se implementan como funciones puras sin estado, para poder testearlas contra casos con solución analítica.
- Se implementan dos motores: uno ingenuo que recalcula todos los tiempos en cada evento y uno con cola de prioridad e invalidación por contadores de colisión. El ingenuo sirve de oráculo de correctitud y provee la curva lenta del punto 1.1. **El ZIP de entrega incluye únicamente el motor final** [TP03, p. 1].

### Modelo

- Mesa de `L = 1.20` m (eje x) por `W = 0.68` m (eje y), con paredes fijas e indeformables [TP03, p. 2].
- Arcos de largo `d = 0.20` m centrados en las paredes cortas `x = 0` y `x = L`. La condición de gol es `|y - W/2| <= d/2`, que con estos valores da `y` en `[0.24, 0.44]`.
- Para una pared vertical el punto de contacto comparte la coordenada `y` con el centro de la partícula, así que la condición de arco se evalúa directamente sobre `y`.
- El arco **no es un agujero**: la partícula rebota normalmente. `N` y la densidad permanecen constantes [TP03, p. 2].
- Partículas de radio `r = 0.0175` m, masa `m = 0.025` kg y rapidez inicial `v0 = 1` m/s con ángulo uniforme en `[0, 2π)` [TP03, p. 2].
- Todas las colisiones son elásticas: `cn = ct = 1`, sin pérdida de energía [TP03, p. 2].
- Los obstáculos son discos fijos de masa infinita. Su resolución es el límite `mj → ∞` de la fórmula de impulso entre partículas [T03, pp. 20-21].
- **La mesa vacía (`K = 0`) es una configuración válida del motor.** La restricción `K > 0` pertenece a la configuración presentada a la competencia, no al simulador: el punto 1.1 simula el sistema sin obstáculos y los puntos 1.2 y 1.3 usan la mesa vacía como referencia obligatoria [TP03, p. 3]. Por eso la validación está separada en `validate_obstacles` (geométrica, acepta la lista vacía) y `validate_competition_obstacles` (agrega `K > 0`).

### Convenciones numéricas

- Dos discos se solapan cuando la distancia entre centros es **estrictamente menor** que la suma de radios. El caso tangente no se considera solapamiento.
- Un disco está contenido en la mesa cuando no sobresale; tocar la pared de forma tangente se admite.
- `is_on_goal` compara contra las mismas cotas que expone `goal_lower_bound` / `goal_upper_bound`, para no tener dos criterios separados por el error de representación. El borde nominal `0.24` no es representable en doble precisión y cae del lado de afuera; es un caso de medida nula.
- El DCM se ajusta con el desplazamiento vectorial completo: `<|Δr|²> = 4Dt`, no la versión por componente `<z²> = 2Dt` de la teórica [T03, p. 25]. Ver `wiki/dudas-y-conflictos.md`.
- El ajuste lineal sigue el método de barrido de `E(c)` de la Teórica 0, tal como exige la consigna: se reporta el gráfico de `E(c)` con su mínimo además de los datos con la recta ajustada [T00, pp. 79-81] [TP03, p. 3].
- La recta del DCM **no lleva ordenada al origen**: `DCM(0) = 0` por definición. El modelo tiene un único parámetro libre y es `D` [T00, p. 82].

### Generación de condiciones iniciales

- El muestreo es **por rechazo**: se sortea una posición uniforme en el área disponible y se descarta si solapa. Es lo que preserva la uniformidad que exige la consigna ("a azar en toda el área disponible" [TP03, p. 3]); por eso no se usa el atajo de una grilla perturbada, que sería más rápido pero no uniforme.
- El bucle de rechazo está **acotado** por `max_placement_attempts` por partícula. Al agotarlo, el motor **falla con `std::runtime_error`** indicando cuántas partículas llegó a ubicar.
- Se descartan las alternativas de reintentar indefinidamente (un barrido del punto 1.2 se colgaría en silencio al generar una configuración demasiado densa) y de reducir `N` avisando (cambiaría la densidad, que es justamente el parámetro que debe permanecer fijo para comparar configuraciones).
- La justificación es de la propia consigna: la restricción (ii) exige `Rk >= r` **y tal que permita la generación de las N partículas** [TP03, p. 3]. Una configuración donde la generación no termina es inválida, no un problema que el motor deba salvar.
- El algoritmo no puede distinguir "imposible" de "muy improbable": desde adentro del bucle ambos casos se ven igual. Por eso el tope es necesario y no solo conveniente.

### Salida

- Formato de trayectoria: cabecera de líneas `#` con los parámetros del sistema y la lista de obstáculos, y después cuadros `frame <índice> <tiempo> <eventos> <motivo>` seguidos de una línea `x y vx vy state` por partícula, en orden de id. El estado es `0` para fresca y `1` para usada.
- El motivo del cuadro (`initial`, `periodic`, `color`) le permite al post-proceso encontrar los cambios de color sin recorrer todo el archivo.
- La precisión de escritura es de 9 cifras significativas: resolución del orden del nanómetro para posiciones en metros, y archivos compactos.
- Se guarda el estado cada `n` eventos y, además, **siempre que un evento cambie un color**. Así el post-proceso reconstruye `Ng(t)` y `t90` con precisión exacta sin que el motor calcule observables y sin llenar el disco [TP03, p. 2].
- El archivo de configuración de obstáculos tiene una línea `xk yk Rk` por obstáculo, en metros y separados por espacios [TP03, p. 3].

### Parámetros vs. no-parámetros

Siguiendo el criterio de [COR02] ("si el output del sistema no cambia al variar ese dato, no es un parámetro físico"):

- **Son parámetros del sistema**: `N`, `L`, `W`, `d`, `r`, `m`, `v0` y la configuración de obstáculos `(K, xk, yk, Rk)`.
- **No son parámetros**: `tmax`, la cadencia de guardado, el tipo de cola, la grilla de celdas y la semilla.

### Método experimental

- `t90` se calcula **por realización** y recién después se promedia. Nunca se promedian las curvas `Fu(t)` para extraer el 0.9 de la curva promedio.
- `D` se ajusta **por realización** y se reporta `<D> ± σ` sobre semillas independientes. La dispersión entre partículas dentro de una misma corrida no es una barra de error válida: las partículas interactúan y no son muestras independientes.
- Las realizaciones que no alcanzan `Fu = 0.9` antes de `tmax` se reportan explícitamente, no se descartan [TP03, p. 3].

## Pendientes experimentales

- Rango final de `N` para el punto 1.1. Punto de partida propuesto: `N` en `{10, 25, 50, 100, 200, 400}`, a ajustar tras el piloto.
- Cadencia de guardado `n` para las corridas de DCM. La ventana difusiva estimada es angosta (del orden de 0.3 s a 1.5 s), así que hace falta resolución temporal fina al principio de la corrida.
- Familias paramétricas concretas a explorar en el punto 1.2.
- Cantidad de realizaciones por punto: la consigna pide un mínimo de 10 para 1.1 y de 5 para 1.2 [TP03, p. 3].
- Si hace falta búsqueda espacial de vecinas (CIM). Con `N = 100` la fracción de área ocupada es ~11.8 %, densidad baja; se decide después de medir el punto 1.1.

## Estimaciones de referencia

Cálculos propios de teoría cinética, no provenientes del material de la cátedra. Sirven de control de la implementación:

- Camino libre medio en 2D con `N = 100`: `λ = 1/(√2 · n · 4r) ≈ 0.082` m, con `n = N/A = 122.5 m⁻²`. Tiempo medio entre choques `τ ≈ 0.082` s.
- Coeficiente de difusión de orden `D ≈ v0·λ/2 ≈ 0.04 m²/s`.
- Saturación del DCM en una caja finita: `<|Δr|²>∞ = (L² + W²)/6 ≈ 0.32 m²`. **Test de implementación**: si el DCM se estanca cerca de ese valor, las partículas están confinadas correctamente.
