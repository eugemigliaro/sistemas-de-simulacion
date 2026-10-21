# Auditoría de código TP4 — 20/10/2026

Base revisada: `3e21eb7`, después de `git pull --ff-only`; no había cambios locales. Alcance: integradores, motor del billar, inicialización densa, salida, protocolo experimental, análisis y declaración de IA. El requerimiento adicional sobre prompts y discusión previa proviene del mensaje de cátedra transcripto por el estudiante en esta sesión; no tiene ID de fuente catalogada. No se modificaron algoritmos, resultados ni presentación durante esta auditoría.

## Dictamen

No encontré una discrepancia en los coeficientes de los integradores ni en las fuerzas del billar respecto de las ecuaciones verificadas. Los tests y los datos respaldan la implementación para los casos examinados. **No corresponde afirmar que todo es una copia literal de la teórica ni que la entrega está cerrada:** hay decisiones de inicialización, tratamiento del amortiguamiento y análisis que deben explicitarse; falta el anexo de prompts originales y queda una diferencia entre el resultado obligatorio de densidad y lo que muestra la presentación.

Las afirmaciones de equivalencia y validez numérica de este documento son conclusiones de auditoría, no aprobación de la cátedra. No hay evidencia en el repositorio de que las adaptaciones ya se hayan discutido en clase. La frase «diseño aprobado» en `diseno-oscilador.md` no acredita esa aprobación académica.

## Archivos que debe leer el grupo

Las rutas de esta tabla son relativas a `entregas/tp4-billar-circular/`. Los números son líneas iniciales de referencia en la versión auditada.

| Prioridad | Archivo y partes | Qué hay que poder explicar |
|---|---|---|
| 1 | `cpp/include/tp4/oscillator.hpp`: `Config` (19), arranque (43), Verlet (52), Velocity Verlet (71), Beeman (75), Euler PC (81) | Los cuatro métodos, la dependencia de la fuerza con la velocidad, el estado anterior y la aceleración que se guarda. |
| 1 | `cpp/include/tp4/billiard.hpp`: `generate` (54), `forces` (79), `simulate` (141) | Inicialización, búsqueda de contactos, signos de fuerzas, pared, integración y conversión irreversible. Es el núcleo físico del billar. |
| 1 | `cpp/include/tp4/dense.hpp`: `generate_dense` (10) | Cómo se obtuvo N=650 y por qué conserva orden de la red. El benchmark lo selecciona para N>400. |
| 1 | `python/analysis.py`: `exact_position` (7), `position_errors` (48) | Referencia analítica independiente y ECM temporal, excluyendo t=0. |
| 1 | `python/billiard_analysis.py`: `frames` (10), `Energy` (50), `maximum_relative_error` (85) | Qué valida el lector; energía cinética más potencial; cada par una vez; máximo energético muestreado. |
| 1 | `python/performance_analysis.py`: `conversion_times` (7), `summarize_density` (31); `python/position_analysis.py`; `python/density_analysis.py` | Primer cruce por realización, promedios y desvíos posteriores, censuras y mínimos de la grilla. |
| 1 | `python/speed_analysis.py`; `python/speed_study.py` | Histograma de rapidez, modelo 2D integrado en cada bin, ajuste con un parámetro y criterio descriptivo de estacionariedad. |
| 2 | `cpp/include/tp4/billiard_cli.hpp`; `cpp/src/main.cpp` | Cómo se fijan parámetros, paso y salida; CSV y metadatos. `main.cpp` despacha: las ecuaciones están en los headers. |
| 2 | `cpp/experiments/benchmark.cpp`; `python/benchmark_build.py`; `python/performance_study.py` | Qué se cronometra, mismas opciones de compilación y computadora; exclusión de generación y escritura. |
| 2 | `python/study.py`; `python/energy_study.py`; `python/position_study.py`; `python/density_study.py`; `python/density_followup.py`; `python/density_extra.py` | Configuración de cada estudio, pilotos, refinamientos, reutilización y separación de conjuntos. Leer junto con `experiments/configs/*.json`. |
| 2 | `cpp/tests/test_oscillator.cpp`; `cpp/tests/test_billiard.cpp`; `cpp/tests/test_dense.cpp`; `python/tests/test_*.py` | Evidencia independiente de fuerzas, colisiones, convergencia, energía, salida y estadísticas. |
| 2 | `diseno-oscilador.md`; `diseno-rendimiento.md`; `experiments/*.md` | Decisiones y limitaciones ya documentadas. Son registros técnicos, no transcripciones de prompts ni aprobaciones de cátedra. |
| 2 | `presentacion/SdS_TP4_2026Q2G07CS_Presentacion.tex` (364); `presentacion/GUION.md` (75); `python/presentation_assets.py` | Declaración de IA, explicación oral y transformación de resultados a figuras. |

Fuentes para leer al lado del código: `material/catedra/teoria/Teorica_4.pdf`, páginas 13–14, 17, 19–20, 23, 33, 35, 37 y 42; `material/catedra/practica/TP4_Enunciado_2026Q2.pdf`, sus cuatro páginas; `Teorica_0.pdf`, páginas de archivo 79–80. Se inspeccionaron visualmente los renders conservados de las fórmulas de T04 pp. 13, 17, 20, 23, 37 y TP04 p. 3, además de sus extracciones y apoyos manuales. La consigna remite a la diapositiva 36 para el oscilador; los parámetros están en la 37.

## Integradores: comparación con la teórica

En lo que sigue, h es el paso y a(x,v)=−(kx+γv)/m. Los valores m=70, k=10000, γ=100, x0=1, v0=−5/7 y tf=5 coinciden con [T04, p. 37].

### Verlet del oscilador

Parte de x[n+1]=2x[n]−x[n−1]+h²a[n] y de v[n]=(x[n+1]−x[n−1])/(2h). Es la recurrencia de posiciones de [T04, p. 13] con velocidad centrada. Sustituir esa velocidad en la fuerza amortiguada y despejar da, con d=γh/(2m):

`x[n+1] = ((2−kh²/m)x[n] − (1−d)x[n−1])/(1+d)`.

Es exactamente la expresión de las líneas 55–56. **La adaptación es cerrar la fuerza dependiente de velocidad usando la diferencia centrada**, no copiar un algoritmo exclusivo de fuerzas posicionales. No usa la velocidad del paso anterior en la fricción. La velocidad escrita es del mismo tiempo que la posición; el paso auxiliar más allá de tf solo permite calcular la última velocidad y no agrega una muestra al ECM.

### Velocity Verlet

La posición cumple x[n+1]=x[n]+hv[n]+h²a[n]/2. La ecuación v[n+1]=v[n]+h(a[n]+a[n+1])/2 de [T04, p. 17] contiene v[n+1] en a[n+1]. Se despeja:

`v[n+1] = (v[n]+h*a[n]/2 − h*k*x[n+1]/(2m))/(1+h*γ/(2m))`.

Coincide con líneas 72–74. **Es un tratamiento algebraico de la fricción implícita que debe declararse.** No corresponde trasladar al oscilador disipativo la afirmación de preservación de volumen del caso conservativo. Con este cierre y arranque, eliminar las velocidades recupera la recurrencia anterior: que Verlet y Velocity Verlet den posiciones prácticamente iguales es esperable, no evidencia de que se haya omitido un método.

### Beeman

Las líneas 77–80 implementan, en orden, posición con coeficientes 2/3 y −1/6; velocidad predicha con 3/2 y −1/2; evaluación a(x[n+1],v_pred); corrección de velocidad con 1/3, 5/6 y −1/6. Coinciden con la variante para fuerza dependiente de velocidad [T04, p. 20], no solo con la forma posicional de p. 19.

Después se recalcula a(x[n+1],v_corregida) para iniciar el siguiente paso y se conserva a[n] como aceleración anterior. Esa política de almacenamiento debe explicarse porque la diapositiva no desarrolla ese detalle de implementación.

### Euler predictor-corrector

Las líneas 83–85 evalúan a(x+hv,v+ha), corrigen v con esa aceleración y luego x con la velocidad corregida. Coinciden con las tres etapas y su orden en [T04, p. 23]. No hay promediado de pendientes. El nombre predictor-corrector por sí solo no prueba orden global dos: en este caso el ECM observado escala aproximadamente como h² y el error de posición como h.

### Arranques: diferencia que debe declararse

Se usa x[−1]=x0−hv0+h²a0/2, **Taylor de segundo orden**, mientras [T04, p. 14] propone que el estado anterior puede estimarse con Euler hacia −h. En Beeman se estima además v[−1]=v0−ha0+h²j0/2, con j0=−(kv0+γa0)/m, y se calcula a[−1] desde ese estado. No se usa la solución exacta para favorecer el arranque. Está documentado en `diseno-oscilador.md` y `experiments/README.md`.

En el billar el mismo arranque de posición está en línea 147; como las condiciones iniciales admitidas no tienen superposiciones, la fuerza inicial es cero y el término de segundo orden se anula. El arranque sigue debiendo identificarse, aunque allí no produzca una diferencia frente a Euler en el estado previo.

## Motor del billar

- **Contacto entre partículas:** `delta=rj−ri`; fuerza sobre i `−k(2r−d)delta/d`, solo para d<2r. Se suma la opuesta sobre j. Es repulsiva y cumple acción/reacción [TP04, p. 2].
- **Grilla:** lado 2r y búsqueda en la celda propia más ocho adyacentes. Un par con distancia menor a 2r no puede estar separado por más de una celda en alguna coordenada. `j>i` evita duplicarlo. Se reconstruye cada paso; el test compara las fuerzas con todos los pares, sin grilla. Es una optimización de búsqueda que no cambia la ley física.
- **Pared:** usa ξ=|ri|+r−R y fuerza `−kξ ri/|ri|`. Es la simplificación algebraica de la imagen `(R+r)ri/|ri|`, recalculada desde la posición actual cada paso. No hay una imagen fija durante todo el choque [TP04, p. 3]. La guarda que detiene centros fuera de R+r evita continuar en un régimen donde esa construcción dejaría de ser válida; es un control numérico, no una nueva ley de rebote.
- **Obstáculos:** centros ±x0, radio r, sin integración ni velocidad propia. Solo se mueve la partícula; es consistente con masa infinita [TP04, p. 2].
- **Verlet original:** líneas 153–154 implementan posición futura y velocidad centrada del instante actual. Las fuerzas se evalúan con todas las posiciones actuales antes de avanzar cualquier partícula. La salida se emite antes de reemplazar posiciones: energía recibe r y v sincronizadas [T04, pp. 13–14].
- **Conversión:** `first_contact_step` cambia de −1 a un paso no negativo una sola vez. No elimina partículas ni modifica sus fuerzas. `used` es una codificación de color. Conservar el primer contacto permite recuperar cruces con resolución h aunque se guarden pocos cuadros [TP04, pp. 2–3]. Esto no equivale a resolver el instante continuo exacto de contacto.
- **Inicialización ordinaria:** radio sorteado como `(R−r)*sqrt(U)`, ángulo uniforme, rechazo de solapamientos y rapidez inicial común. La raíz evita concentrar posiciones en el centro. El rechazo es secuencial: no se afirma que produzca una distribución uniforme de configuraciones completas de muchos discos.
- **Inicialización densa:** red hexagonal, orientación/traslación aleatorias, selección de sitios y 500 barridos Monte Carlo; luego velocidades de dirección uniforme. Respeta geometría y rapidez, pero no demuestra pérdida de memoria de la red ni equilibrio. Es una adaptación al pedido de posiciones aleatorias [TP04, p. 2] que debe discutirse, especialmente antes de atribuir la conversión lenta de N=650 exclusivamente a densidad.
- **Salida:** precisión de 17 dígitos, estados CSV y metadatos; paso y cadencia controlados mediante enteros y `step % save_every`. Respeta la distinción entre paso de integración y salida [T04, p. 33]. La animación y los observables se calculan desde archivos, por separado [TP04, pp. 1–2].

## Análisis y protocolos

**Oscilador:** la solución general de `exact_position` se reduce a la fórmula de [T04, p. 37] con las condiciones iniciales oficiales. El ECM usa n=1,…,M y divide por M; no promedia partículas ni realizaciones. Se recalcularon los 28 ECM desde sus CSV y coinciden exactamente con `oscillator-summary.csv` en el entorno de auditoría. Los siete pasos son menores a 0,01 s [TP04, p. 1].

**Energía:** `Energy.components` suma m|v|²/2, potenciales kξ²/2 de pares i<j, pared y obstáculos cuando existen. No cuenta dos veces los pares ni exige conservar solo la energía cinética [T04, pp. 35, 42]. La métrica max|E/E0−1| y el umbral 0,1 % son elecciones locales. La selección inicial h=5e−5 s incluye otro estado inicial, 30 s de comprobación y comparación entre salida a cada paso y submuestreo en un piloto corto; no garantiza el máximo continuo en todos los estudios. En rendimiento y en los casos principales de posición se verifican energía inicial y final; los pilotos dan controles temporales adicionales, pero **no hay un control del máximo durante toda cada corrida de esos dos conjuntos**.

**Rendimiento:** el harness usa `steady_clock` alrededor de `simulate`, con inicialización y escritura fuera del intervalo. Incluye validaciones internas y una copia final TP4 en el callback. TP3 y TP4 se compilan con el mismo compilador y flags y el registro identifica la misma computadora; no se repitieron las mediciones de rendimiento en esta auditoría. Es comparación de los sistemas/implementaciones pedidos, no un experimento que aísle únicamente el efecto del integrador [TP04, p. 3].

**Conversión y censura:** t90 es el contacto de orden ceil(0,9N); t100, el último contacto si se convirtieron todas. Se calculan por realización y después se agregan. Los desvíos usan ddof=1. Un tiempo no observado se conserva como `None`; no se lo inventa como 30, 100 o 300 s. Las cotas inferiores y medias restringidas tienen nombres y significados distintos. Es coherente con los primeros cruces y con reportar corridas incompletas [TP04, pp. 3–4].

**Dos pasos diferentes:** el benchmark obligatorio de 30 s usa h=5e−5 s. Los estudios largos usan h=1,25e−5 s, refinado por controles energéticos. El post-proceso conserva el conjunto original de 30 s y las mismas condiciones iniciales cuando repite a otro paso; no afirma que sean la misma trayectoria. Debe explicarse porque 2.4.a exige tomar los outputs de 2.1.b [TP04, p. 4].

**Rapidez:** se histograman módulos, no componentes; bins compartidos y normalización por cantidad de muestras y ancho. El modelo es la densidad Maxwell–Boltzmann 2D, integrada en cada bin y dividida por su ancho. Se minimiza una suma de residuos cuadrados con θ=kBT como único parámetro libre; no se ajusta amplitud. La grilla logarítmica y sección áurea son elecciones de optimización que implementan el criterio de [T00, pp. 79–80] y [TP04, p. 4]. Se forman histogramas por realización y luego se promedian; los cuadros de una misma trayectoria no se presentan como realizaciones independientes. Recalculé el ajuste desde los diez NPZ: θ=0,012398622713835118 J, idéntico al resumen.

La selección de [10,60) s usa ventanas de 10 s, límites de variación total 0,05 y cambio relativo de θ de 2 %, con tres comparaciones consecutivas. Es un criterio descriptivo local, no prueba de equilibrio ni determinación exacta de relajación. Las barras son desvíos entre realizaciones, no incertidumbre del ajuste. El potencial de contacto explica la diferencia entre cinética media y energía inicial; no explica por sí solo la diferencia entre el estimador por ajuste y el segundo momento.

## Pendientes detectados

1. **Anexo de prompts ausente.** La diapositiva de IA declara agente/modelo y alcance, pero no incluye las instrucciones originales para construir el motor. No encontré ese registro en los archivos revisados del TP4 ni en la búsqueda de prompts del repositorio. Deben recuperarse de los chats originales con su orden y contexto relevante; los documentos `diseno-*.md` no los reemplazan. No se inventó ni reconstruyó una transcripción. Este documento es una auditoría posterior, no ese anexo. El mensaje nuevo pide agregarlo a la declaración; no al ZIP del motor, que excluye documentación [TP04, p. 1].
2. **Discusión académica pendiente de acreditar.** Llevar a clase el cierre centrado de Verlet, el despeje de Velocity Verlet, arranques Taylor, aceleración conservada por Beeman y generación densa. Incluir también el refinamiento del paso y el tratamiento complementario de densidad. Documentar una decisión local no acredita que ya se discutió con la cátedra.
3. **Explicación del ECM en el guion:** `presentacion/GUION.md:75` dice «misma pendiente (orden 2)». Las pendientes recalculadas con los dos pasos menores son 4,00013 (Beeman), 3,98811 (Verlet), 4,00000 (Velocity Verlet) y 1,98997 (Euler PC). Debe decir pendiente aproximadamente 4 para el ECM de los tres primeros, compatible con error de posición de orden 2; para Euler, pendiente aproximadamente 2 y error de posición de orden 1. No hay un error detectado en los datos de la figura; el problema es su explicación oral. La ventaja de Beeman es aproximadamente 13 % en ECM, dependiente de las variantes y pasos ensayados, no un orden mayor.
4. **Densidad obligatoria no visible:** la presentación sigue mostrando el complemento refinado y N=50, sin una figura explícita de `density-baseline-summary.csv` de las corridas obligatorias de 30 s. Los datos originales sí están conservados y auditados. Deben mostrarse y diferenciarse del complemento para sostener el cumplimiento literal de 2.4.a.
5. **Manifiesto local de figuras desactualizado:** después del pull, `presentacion/.build/figures-manifest.json` conserva el hash del constructor anterior y difiere de 14 archivos de figuras actuales. Sus 14 tablas fuente siguen coincidiendo. Es un caché local desactualizado; no prueba resultados científicos incorrectos. Regenerar/verificar al cerrar la presentación, sin confundirlo con los contratos científicos que sí se verificaron.

## Verificaciones ejecutadas

- `make test PYTHON=/private/tmp/tp4-audit-venv/bin/python`: tres ejecutables C++ y 25 pruebas Python, todo aprobado. El primer intento con Python del sistema falló por ausencia de NumPy; se usó un entorno temporal con NumPy y Matplotlib, sin cambiar dependencias del repositorio.
- `make sanitize`: los tres tests C++ pasan con AddressSanitizer y UndefinedBehaviorSanitizer.
- `python/density_verify.py`: aprobado; verifica integridad, cobertura, historias de contacto, energía, censuras, estadísticas y mínimos; 154 casos generados, 50 casos base, 60 casos finales de densidad y 220 del mapa (con reutilizaciones).
- Recalculados los 28 ECM desde trayectorias y el ajuste de rapidez desde diez archivos de muestras: coinciden con los resúmenes.
- Verificados hashes de fuentes en manifiestos/contratos de oscilador, energía, rendimiento, posición, rapidez y densidad, y 160 entradas de la procedencia de densidad. Sin discrepancias en esas entradas. Artefactos declarados de oscilador y energía también coinciden.
- Verificados trayectorias/muestras registradas en 110 checkpoints de rendimiento (50 TP4 y 60 TP3; TP3 no almacena trayectoria en este protocolo), 110 de posición y diez de rapidez; cruces recalculados desde estados finales TP4 y posición sin discrepancias.

No se repitieron todos los barridos largos ni se midió convergencia estadística de t90/t100 frente a h para toda la grilla. Conservación energética, tests y hashes son evidencia complementaria; no constituyen demostración universal de exactitud ni aprobación académica.
