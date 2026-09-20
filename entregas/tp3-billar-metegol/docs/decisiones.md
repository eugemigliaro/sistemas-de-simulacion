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

### Predicción y resolución de choques (fase 3)

- `predict_*` y `resolve_*` son funciones puras. La resolución devuelve las velocidades posteriores y **no toca posiciones ni contadores**: quien lleva la cuenta de eventos es el motor. Así se las puede testear contra casos con solución analítica sin construir un sistema entero.
- Las predicciones devuelven `infinito` en lugar de `optional` cuando no hay choque futuro. La búsqueda del próximo evento queda como un mínimo sin casos especiales.
- **Se aceptan tiempos de choque iguales a cero.** La invariante que lo vuelve seguro es que toda resolución deja a los participantes alejándose, de modo que un evento de tiempo cero no puede repetirse. Es necesario para las esquinas: al rebotar contra la pared corta, la larga queda a distancia cero, y descartar el cero haría que la partícula la atravesara. Con `t > 0` estricto el rebote de esquina pierde una de las dos componentes.
- Las paredes se nombran `Short` (x = 0 y x = L) y `Long` (y = 0 e y = W) en lugar de vertical y horizontal como en la teórica [T03, p. 19]. Son las cortas las que llevan arco, y nombrarlas por la consigna ata la condición de gol al mismo vocabulario que la define, en vez de obligar a recordar que L corre sobre x.
- La predicción contra pared devuelve además `on_goal`, evaluado sobre la `y` del **punto de contacto**, no sobre la posición actual. Es geometría del evento, no un observable: el motor la usa para cambiar el color, que es estado, y nunca para contar goles [COR02].
- Ante un empate exacto entre pared corta y larga se resuelve primero la corta. La larga queda predicha a tiempo cero y se resuelve en el evento siguiente, de modo que el rebote de esquina invierte ambas componentes en dos eventos consecutivos y no en uno solo.
- El choque entre partículas usa la fórmula de impulso de la teórica con `σ` en el denominador, no la distancia instantánea entre centros [T03, p. 20]. Son iguales en el contacto, que es el único momento en que el motor la invoca, y usar `σ` mantiene el código pegado a la fuente.
- El obstáculo se implementa como el límite `mj → ∞` de esa misma fórmula: `2 mi mj/(mi+mj) → 2 mi`, la masa de la partícula se cancela y queda una reflexión especular. Hay un test que lo compara contra una partícula quieta de masa `1e12` para que la equivalencia no sea solo un comentario.
- Un par de discos superpuestos y acercándose devuelve tiempo negativo, que se descarta. No se lo trata como caso a resolver: el solapamiento es una violación de invariante de la generación, no un estado físico del que haya que salir.

### Motor ingenuo (fase 4)

- El motor recibe un `FrameSink` en lugar de un `ostream`. No sabe dónde terminan escritos los cuadros, lo que deja que los tests los lean en memoria y que el punto 1.1, que solo mide tiempo de ejecución, corra sin tocar disco.
- `simulate_naive` recalcula **todos** los tiempos en cada evento: `O(N² + N·K)` por evento. Es deliberadamente simple para poder confiar en él como oráculo de la fase 5, y es además la curva lenta que pide el punto 1.1.
- Ante un empate exacto gana el primero en el orden de recorrido, que es fijo. La corrida queda reproducible a partir de la semilla, y hay un test que lo verifica corriendo dos veces.
- **El tiempo de ejecución sí lo mide el motor**, y se reporta por salida de error junto con los eventos procesados. No contradice [COR02]: es una propiedad del programa, no del sistema simulado, y es exactamente lo que pide el punto 1.1. Va por `stderr` para poder mandar la trayectoria a `/dev/null` cuando solo interesa el tiempo.
- La corrida termina avanzando en línea recta hasta `tmax` cuando el próximo evento cae más allá del horizonte, en vez de cortar en el último choque. El estado final queda completo y el post-proceso puede leer el último tramo.
- Se agregó el motivo de cuadro `final`. Sin él, el post-proceso no puede distinguir una realización que no alcanzó `Fu = 0.9` de un archivo truncado, y la consigna pide reportar explícitamente esas realizaciones [TP03, p. 3].
- `SimulationReport` expone `exhausted_events` para el caso en que no queden choques posibles. Con velocidades no nulas no debería ocurrir nunca; es una señal de error de implementación, no un final esperado.
- `Event` ya lleva los contadores de choque de los participantes aunque el motor ingenuo no los mire. Los necesita la cola de prioridad de la fase 5 para descartar eventos invalidados [B16, pp. 1, 4], y dejarlos ahora evita tocar la estructura después.

### Validación de la física

- Los tests verifican conservación de momento y energía en el choque oblicuo con masas distintas, que la resolución es simétrica al intercambiar el par, y que el obstáculo preserva la rapidez y la componente tangencial.
- Sobre corridas completas se verifica que ninguna partícula sale de la mesa, que ningún par se superpone y que ninguna queda dentro de un obstáculo.
- Control independiente sobre la trayectoria escrita: `N = 100` con tres obstáculos y `tmax = 30` s, 28 758 eventos, deriva relativa de energía de `2·10⁻¹⁰`. Ese número es una **cota**, no la deriva real del motor: el archivo se escribe con 9 cifras significativas, así que mide el ida y vuelta por disco. La deriva en memoria se controla aparte en los tests.

### Motor con cola de prioridad (fase 5)

- `Event.time` pasó a ser el **instante absoluto** del choque, no el tiempo que falta. Con tiempos relativos una cola de prioridad ordena mal apenas avanza el reloj. Las funciones `predict_*` siguen devolviendo tiempos relativos, porque son geometría pura y no conocen el reloj; la conversión ocurre al agendar. La separación es deliberada: predicción relativa, evento agendado absoluto.
- Invalidación **perezosa**: los eventos que dejaron de valer no se buscan ni se borran de la cola. Se los descarta al extraerlos, comparando los contadores de choque guardados al agendar contra los actuales [B16, pp. 1, 4]. Borrar del montículo exigiría índices auxiliares y no compensa.
- Después de un choque se reagenda a **todos** los participantes contra todo el sistema, no solo su próximo evento. Agendar únicamente el mínimo parece más barato pero se rompe: cuando ese evento se invalida, la partícula queda sin ningún evento en la cola.
- Los duplicados que genera reagendar ambos participantes (el par `(i,j)` y el `(j,i)`) son inofensivos: al procesar el primero se incrementan los contadores y el otro queda invalidado.
- **No se agendan eventos posteriores a `max_time`.** Nunca se procesarían y solo harían crecer la cola. El costo es que la cola vacía deja de significar "no hay más choques", así que al vaciarse se confirma con un único barrido exhaustivo `O(N²)` antes de marcar `exhausted_events`. Es una vez por corrida, despreciable, y evita confundir el final normal con un error de implementación.
- El motor por defecto de la CLI es `queue`. El ingenuo queda accesible con `--engine naive` para el punto 1.1 y para reproducir el oráculo.

### Validación cruzada de los motores: por qué no se exige la misma trayectoria

- **Los dos motores son correctos y aun así divergen.** Predicen desde estados de referencia distintos —el ingenuo recalcula desde el instante actual, la cola conserva lo agendado en un instante anterior— y en aritmética exacta eso da lo mismo, pero en punto flotante difiere en el último bit.
- Un gas de discos rígidos es caótico, así que esa diferencia de `10⁻¹⁶` se amplifica exponencialmente: medido sobre `N = 100`, la separación máxima entre motores pasa de 0 en el primer evento a `9·10⁻¹⁵` m a los 100 eventos, `3·10⁻⁸` m a los 500 y 0,24 m a los 1 000, hasta saturar en el tamaño de la mesa. Alrededor de una década cada 60 eventos.
- En consecuencia **la misma semilla no identifica una realización entre motores**: identifica una condición inicial. Medido sobre 8 semillas, `t90` difiere hasta un 44 % entre motores para la misma semilla, mientras la energía coincide a 10 decimales en todas.
- La validación queda en tres niveles: (1) igualdad exacta en el primer evento y acuerdo a `10⁻¹⁰` en los primeros 100; (2) invariantes físicas —energía, contención, no solapamiento— en corridas largas de ambos motores; (3) acuerdo estadístico de `<t90>` dentro del error estándar.
- Esto refuerza, desde la implementación, la razón por la que el TP pide promediar sobre realizaciones: una corrida individual no es reproducible ni siquiera entre dos implementaciones correctas del mismo modelo. Vale la pena decirlo en la presentación.

### Dispersión de t90 y cuántas realizaciones hacen falta

Medido con el motor de cola, `N = 100`, `tmax = 100` s, 30 semillas por configuración:

| configuración | `<t90>` | desvío | rango | error estándar con 5 corridas |
|---|---|---|---|---|
| mesa vacía | 22,33 s | 3,81 s | 17,1 – 33,9 | 1,70 s |
| 1 obstáculo central `R = 0,10` | 20,49 s | 1,98 s | 16,0 – 24,7 | 0,88 s |
| 4 obstáculos en embudo | 23,02 s | 3,04 s | 17,8 – 32,9 | 1,36 s |

- **Las 5 realizaciones que pide la consigna son el mínimo, no lo suficiente.** Con la dispersión de la mesa vacía, el error estándar con 5 corridas es de 1,70 s, y la mejora del obstáculo central sobre la mesa vacía es de 1,84 s: apenas una barra de error. Para el barrido del punto 1.2 hay que subir el número de realizaciones, o el gráfico va a tener barras que se solapan y no va a permitir concluir nada.
- Un obstáculo bien puesto **reduce también la dispersión** (3,81 → 1,98 s), no solo la media. Para la competencia, que promedia apenas 5 realizaciones, la varianza baja vale tanto como la media baja.
- Dato preliminar en contra de la intuición: el arreglo tipo embudo que probamos a ojo quedó **peor** que la mesa vacía. Es una sola configuración de esa familia y no prueba nada sobre la familia, pero confirma que el punto 1.2 hay que hacerlo midiendo y no razonando.

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
