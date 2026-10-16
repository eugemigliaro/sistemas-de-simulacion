# TP4 — preparación de la resolución

Presentación: [borrador PDF/PPTX, fuente editable y guion](presentacion/README.md). Incluye los resultados de todos los puntos, con enlaces públicos de las animaciones y revisión/ensayo del grupo pendientes.

Estado: **sistema 1 implementado y verificado** (puntos 1.1–1.2), **motor del billar circular implementado**, estudios de energía 2.1.a, rendimiento 2.1.b, posición 2.2, rapidez 2.3, densidad 2.4.a y mapa 2.4.b ejecutados y verificados. En N=650 los tiempos de conversión siguen censurados a 300 s y se informan como cotas. Este archivo es una guía de trabajo local; no es el informe ni la presentación de la entrega.

## Ejecutar el sistema 1

Desde esta carpeta, con compilador C++20, Make y Python 3:

```bash
make python-env       # primera vez: entorno local con NumPy y Matplotlib
make test
make sanitize
make oscillator-study
```

Si ya hay un Python con esas dependencias, se puede usar sin instalar nada: `make test oscillator-study PYTHON=/ruta/al/python`. La verificación de esta sesión utilizó `PYTHON=../tp3-billar-metegol/python/.venv/bin/python`; no se modificó ese entorno ni el código del TP3. Las versiones efectivamente utilizadas quedan registradas en el manifiesto.

Una trayectoria individual:

```bash
make release
./cpp/build/release/tp4 oscillator --method beeman --steps 1000 --output /tmp/tp4-beeman.csv
./cpp/build/release/tp4 --help
```

Métodos: `beeman`, `verlet`, `velocity-verlet`, `euler-pc`. Opciones numéricas: `--steps`, `--duration`, `--mass`, `--stiffness`, `--damping`, `--x0`, `--v0`; sus valores predeterminados corresponden al estudio oficial. El paso se calcula como `duration/steps`; no hay redondeo del horizonte solicitado. La salida CSV contiene `step,time,position,velocity`, incluido el estado inicial. Los estados no finitos detienen la ejecución con error; si una corrida falla, su salida parcial no se considera válida.

El barrido se configura en `experiments/configs/oscillator.json`. El comando de estudio valida cada trayectoria antes de renombrarla de `.partial` a `.csv`, calcula ECM y error máximo, y escribe:

- [Resumen numérico](experiments/results/oscillator-summary.csv).
- [Figura comparativa PNG](experiments/figures/oscillator-ecm.png) y [SVG](experiments/figures/oscillator-ecm.svg).
- [Manifiesto de configuración, versiones y hashes](experiments/results/oscillator-manifest.json).

Las trayectorias completas quedan en `experiments/raw/oscillator/` (regenerables, ignoradas por Git). ECM y solución analítica están únicamente en el post-proceso. El detalle de decisiones y resultados está en [el registro técnico del estudio](experiments/README.md).

## Ejecutar el billar circular

```bash
make release
./cpp/build/release/tp4 billiard --n 100 --duration 1 --dt 0.00005 \
  --save-every 200 --obstacles 1 --obstacle-x 0.2 --seed 7 --output /tmp/tp4-billar.csv
make energy-study
```

El entorno Python se selecciona igual que para el oscilador. Para regenerar con el entorno usado en esta sesión: `make energy-study PYTHON=../tp3-billar-metegol/python/.venv/bin/python`.

Opciones: `--n`, `--duration`, `--dt` (o `--steps`, excluyentes), `--save-every`, `--seed`, `--obstacles 0|1`, `--obstacle-x`, `--radius`, `--particle-radius`, `--mass`, `--stiffness`, `--speed` y `--output`. La duración debe ser múltiplo de dt y la cantidad de pasos múltiplo de la cadencia de salida. Por defecto no hay obstáculos; con obstáculos, la posición predeterminada es x0=r.

El motor usa Verlet original y una grilla de ancho 2r reconstruida en cada paso para buscar contactos. Calcula las fuerzas y el cambio irreversible de estado, sin calcular energía, Fu ni tiempos medios. La pared se implementa mediante su fuerza radial equivalente a la partícula imagen de la consigna [TP04, p. 2] [TP04, p. 3].

Cada fila de salida tiene `step,time,id,x,y,vx,vy,used,first_contact_step`. Los IDs van de 0 a N−1 y cada cuadro contiene las N partículas. `used=0` significa fresca/azul y `used=1` usada/roja. `first_contact_step=-1` significa sin contacto con obstáculos; otro valor guarda el paso de la primera conversión, incluso si ocurrió entre dos cuadros. Posiciones y velocidades corresponden al mismo tiempo. El archivo adjunto `<salida>.json` registra parámetros, controles numéricos y generador.

La inicialización predeterminada usa rechazo secuencial uniforme en área y direcciones uniformes, con mt19937_64 y conversión explícita de 53 bits a [0,1). Tiene cota de intentos y falla si no puede ubicar N: nunca baja N ni acepta superposiciones. A alta densidad el rechazo puede agotarse aun cuando exista una configuración geométrica válida; para ese caso está disponible el generador denso descrito abajo. También se puede cargar un estado inicial mediante `--initial archivo.csv`, con cabecera `id,x,y,vx,vy` y una fila por partícula, sin superposiciones ni partículas usadas.

### Visualización independiente

```bash
python/.venv/bin/python python/billiard_view.py /tmp/tp4-billar.csv \
  --output /tmp/tp4-billar.gif --snapshot /tmp/tp4-billar.png --fps 25
```

Admite trayectorias comprimidas `.gz`, indicando su archivo JSON con `--metadata`. `--frame-stride` selecciona uno de cada varios cuadros para visualizar; no altera el paso del motor. La animación muestra únicamente el sistema físico, no gráficos de evolución temporal [COR03].

La demostración local usa N=60, x0=0,2 m, duración 1 s, dt=0,00005 s, semilla técnica 7 y cuadros cada 0,01 s: [animación GIF](experiments/figures/billiard-demo.gif) y [último cuadro](experiments/figures/billiard-demo.png). El GIF es un artefacto de revisión local; la entrega final exige fotograma y enlace a YouTube/Vimeo, y no entregar estos archivos [TP04, p. 1].

### Estudio del paso: 2.1.a

La configuración está en `experiments/configs/energy.json`; se ensayan seis pasos con N=300 sin obstáculos. Python calcula energía cinética y potencial de todos los contactos desde estados guardados, contando cada par una sola vez. El criterio local es máximo muestreado de error relativo ≤0,1 %, con comprobación de la cadencia de salida, otra semilla y una corrida prolongada de 30 s. No es un umbral impuesto por la cátedra.

**Paso seleccionado: dt=0,00005 s**. El máximo muestreado fue 0,06022 % en 30 s; el candidato dt=0,0001 s alcanzó 0,2414 % y se descartó. La selección corresponde a N=300 sin obstáculos: se revisará su validez para los siguientes estudios. Usar `--dt 0.00005` explícitamente; si se omiten dt y steps, el motor deriva el paso de los valores predeterminados `duration=2` y `steps=20000`, que corresponden al barrido exploratorio, no a esta selección.

- [Energía frente al tiempo](experiments/figures/billiard-energy-time.png).
- [Error energético frente al paso](experiments/figures/billiard-energy-error.png).
- [Resumen](experiments/results/energy-summary.csv), [selección y validaciones](experiments/results/billiard-step-selection.json) y [manifiesto](experiments/results/energy-manifest.json).

El estudio conserva trayectorias comprimidas regenerables en `experiments/raw/energy/` y series de energía en `experiments/results/`. Si ningún paso pasa los controles, el comando termina con error y no declara una selección válida. Ver [diseño y alcance](diseno-billar.md) y [registro técnico](experiments/billar-energia.md).

## Inicialización densa, rendimiento y densidad

El generador aprobado parte de una red hexagonal con orientación y traslación aleatorias, elige sitios y realiza movimientos Monte Carlo sin solapamientos. No reduce N ni cambia radios. Conserva orden residual: no se considera una muestra uniforme del conjunto de configuraciones. Las decisiones y el alcance se detallan en [el diseño del estudio](diseno-rendimiento.md).

Para generar un CSV válido para N=650 y utilizarlo en el motor:

```bash
python/.venv/bin/python python/benchmark_build.py
./cpp/build/release/benchmark generate 650 1 30 600000 500 /tmp/tp4-dense650.csv
./cpp/build/release/tp4 billiard --n 650 --duration 30 --dt 0.00005 \
  --save-every 1000 --obstacles 1 --initial /tmp/tp4-dense650.csv --output /tmp/tp4-650.csv
```

El orden de argumentos del harness es `tp4|tp3|generate N seed tf steps sweeps output`. Los 500 barridos corresponden a la inicialización, no al tiempo físico. El modo `generate` guarda posiciones y velocidades; informa aceptación y desplazamiento respecto de la red. Los modos de benchmark excluyen inicialización y escritura de su cronómetro.

Para repetir el estudio completo:

```bash
python/.venv/bin/python python/performance_study.py
python/.venv/bin/python python/performance_plot.py
```

Si el sandbox no deja identificar la CPU, proporcionar el modelo previamente verificado. Esta sesión usó `TP4_CPU_DESCRIPTION='Apple M5 Pro'` y el intérprete `../tp3-billar-metegol/python/.venv/bin/python`. No reutilizar esa descripción en otra computadora sin comprobarla.

La configuración está en `experiments/configs/performance.json`: TP4 con N={20,100,200,400,650}, TP3 con su rango histórico N={10,25,50,100,200,400}, diez semillas por N, tf=30 s. Los motores se enlazan en un harness C++20 con las mismas opciones release y se ejecutan secuencialmente en la misma computadora. La medición incluye la llamada al simulador y excluye generación y escritura para ambos; por eso se recalcula el TP3 y no se mezclan sus tiempos históricos de otro protocolo. No se modifican el código ni los resultados del TP3.

El ejecutor guarda cada caso terminado y verifica huella de fuentes/configuración/hardware y hashes antes de reutilizarlo. Repetir el comando tras una interrupción continúa con los casos faltantes; un cambio de protocolo provoca un error en lugar de mezclar mediciones.

Se conservan los estados inicial y final, con el paso del primer contacto por partícula, para reutilizar las salidas en 2.4.a. Si un tiempo no se alcanza en 30 s, queda como censurado: no se publica una media ordinaria del grupo descartando esas realizaciones. El resumen distingue cantidad de censuras, media condicional de los observados y cota inferior de la media completa. Las barras de los grupos completos son desvíos estándar muestrales entre diez realizaciones [COR03].

Se completaron **110 corridas**: 50 TP4 y 60 TP3. En N=400, el tiempo medio fue 3,90 ± 0,05 s para TP4 y 8,49 ± 0,06 s para TP3 (desvíos entre diez realizaciones); en N=100 y 200 fue más rápido el motor por eventos. El caso N=650 del TP4 dio 7,145 ± 0,025 s. Ver [comparación de rendimiento](experiments/figures/runtime-comparison.png).

Para densidad, t90 se observó en las diez realizaciones de N=20: 21,1 ± 4,2 s. Hay censura en otros grupos y en t100; el horizonte de 30 s no permite estimar sus medias completas. Ver [figura con cotas inferiores](experiments/figures/conversion-vs-density.png) y [registro técnico con resultados y limitaciones](experiments/rendimiento-y-densidad.md).

Artefactos del estudio completo: `experiments/results/performance-summary.csv`, `density-summary.csv`, `density-raw.csv`, `performance-manifest.json`; figuras `runtime-comparison.png` y `conversion-vs-density.png` en `experiments/figures/`. Los registros por realización están en `experiments/results/performance-cases/`; las trayectorias regenerables están en `experiments/raw/performance/`. El segundo comando de reproducción mejora la legibilidad de las cotas coincidentes sin repetir mediciones.

## Posición de obstáculos: 2.2

El [diseño del estudio](diseno-posiciones.md) fija once posiciones equiespaciadas entre x0=r y x0=R−r, cinco realizaciones por posición, N=100 y N=20 y un horizonte de 100 s. La configuración reproducible está en `experiments/configs/obstacle-position.json`.

```bash
make release
python/.venv/bin/python python/position_study.py
python/.venv/bin/python python/position_animations.py
```

Se puede reemplazar el intérprete por uno con NumPy y Matplotlib, como en los estudios anteriores. No se vuelve a calcular rendimiento: este ejecutor estudia respuesta física. Conserva checkpoints por corrida y detecta cambios en fuentes, configuración o trayectorias antes de reutilizarlos.

El paso de 0,00005 s utilizado en el benchmark no cumplió el criterio energético local del 0,1 % en los dos pilotos N=100 de 100 s. Se validó 0,000025 s en los cuatro pilotos de extremos y ambos N; el barrido usa **0,0000125 s** como margen uniforme. Los pilotos y la decisión se registran en `experiments/results/position-step-validation.json`, sin reescribir los estudios anteriores.

Se reconstruye Fu(t) desde el historial de primer contacto de cada partícula. Las curvas muestran el promedio de fracciones entre cinco realizaciones para x0={0,0175;0,255;0,4925} m; las bandas son desvíos estándar, limitadas visualmente al intervalo físico [0,1], no intervalos de confianza. Cada t90 se obtiene por realización antes de calcular su media y desvío. Si no se alcanza el umbral en 100 s, se conserva la censura y Fu final; la media ordinaria del grupo no se inventa.

Los resultados se guardan como `position-summary.csv`, `position-raw.csv`, `position-fu.csv`, `position-best-sampled.json` y `position-manifest.json` en `experiments/results/`. Las figuras son `position-fu.png` y `position-t90.png`. La animación física compara las tres posiciones típicas durante 5 s de una realización: `position-demo.gif` y `position-demo.png`, con procedencia en `position-animation-manifest.json`. Es un artefacto local para revisión; no es una presentación ni un archivo para entregar.

Se completaron las **110 corridas** y todas alcanzaron t90 antes de 100 s. Las menores medias de la grilla fueron x0=0,16 m para N=100 (13,6±1,0 s) y x0=0,3975 m para N=20 (9,2±1,1 s). Son mínimos muestreados, no óptimos exactos ni pruebas de significancia frente a todos los vecinos. Ver [registro técnico](experiments/posicion-obstaculos.md), [t90 frente a posición](experiments/figures/position-t90.png), [Fu(t)](experiments/figures/position-fu.png) y [animación](experiments/figures/position-demo.gif).

## Fuentes y decisiones de partida

- [Consigna completa](../../material/catedra/practica/TP4_Enunciado_2026Q2.pdf) [TP04].
- [Contrato y matriz de estudios](../../wiki/temas/billar-circular-y-tp4.md).
- [Teoría e integradores](../../wiki/temas/paso-temporal-e-integradores.md).
- [Correcciones del TP3 integradas](../../wiki/temas/comunicacion-cientifica.md) [COR03].
- [Dudas y conflictos](../../wiki/dudas-y-conflictos.md).

La tecnología configurada es C++20 para simulación y Python 3 para visualización y análisis (`materia.yaml`). El motor produce estados en texto; animación y observables se calculan en programas independientes [TP04, p. 1] [COR02].

## Orden de resolución propuesto

1. **Oscilador:** implementar y contrastar los cuatro métodos con la solución exacta de T04 p. 37. Fijar ecuaciones, inicialización y tratamiento de la fuerza dependiente de velocidad antes de comparar ECM. La exposición mostrará solo una diapositiva con ECM frente a paso [TP04, p. 1] [TP04, p. 2].
2. **Billar mínimo:** geometría circular, inicialización sin superposiciones, fuerzas de pares, obstáculos e imagen de pared; integración Verlet y salida sincronizada de posición, velocidad y color [TP04, p. 2] [TP04, p. 3].
3. **Validación y paso (2.1.a):** colisión binaria, contacto con obstáculo, pared radial/oblicua y energía total para N=300 sin obstáculos. Elegir el paso con evidencia y comprobar sensibilidad de los observables al paso de salida [T04, p. 35] [TP04, p. 3].
4. **Rendimiento y densidad (2.1.b y 2.4.a):** corridas con x0=r, tf=30 s, al menos diez realizaciones por N e incluir N>600. Conservar todas las trayectorias necesarias para reutilizar conversiones; registrar hardware, compilación, generador, semillas y alcance del cronómetro. Comparar con TP3 en la misma máquina [TP04, p. 3] [TP04, p. 4].
5. **Posición de obstáculos (2.2):** barrer x0 entre r y R-r para N=100, al menos cinco realizaciones por punto, tmax=100 s; comparar con N menor. Registrar realizaciones sin cruce [TP04, p. 3].
6. **Rapidez (2.3):** N=100 sin obstáculos, varias realizaciones, histogramas en tiempos representativos y ajuste de un único parámetro a Maxwell–Boltzmann 2D siguiendo T00 [TP04, p. 3] [TP04, p. 4].
7. **Revisión del estudiante:** discutir resultados, preparar exposición, revisar cifras significativas y composición del ZIP, y completar declaración de uso de IA. La consigna reserva a los estudiantes la elaboración de presentación y reporte [TP04, p. 4].

Para el oscilador, Beeman obtuvo el menor ECM en los siete pasos ensayados con las variantes y arranques acordados. El paso del billar se eligió con su estudio de energía y se refinó para los 100 s del punto 2.2. Se identificaron las posiciones con menor media muestral para ambos N. El punto 2.3 está implementado y ejecutado: diez realizaciones sin obstáculos, ventana compatible con estacionariedad [10,60) s y ajuste térmico de 0,0123986 J, frente a la referencia inicial 0,0125 J. Ver [registro de rapidez](experiments/rapidez.md), [evolución](experiments/figures/speed-evolution.png) y [ajuste](experiments/figures/speed-fit.png). El cierre de 2.4 preserva el benchmark de 30 s, agrega seguimiento hasta 300/600 s y N=50 exploratorio, y completa el mapa de cuatro N y once posiciones. Las medias de N=650 no son identificables a 300 s; se reportan censura y cotas, sin extrapolar. No se determinó un óptimo global de densidad.

Para reproducir 2.3, ejecutar `python/.venv/bin/python python/speed_study.py` después de `make release`, con NumPy y Matplotlib. Configuración: `experiments/configs/speed.json`. El ejecutor recupera checkpoints y rechaza fuentes/configuraciones incompatibles. Se conserva además el ensayo exploratorio de 30 s que motivó ampliar el estudio; ver [diseño](diseno-rapidez.md).

### Cierre de densidad y mapa (2.4.a–b)

Ver [registro técnico](experiments/densidad-y-mapa.md), [tiempos frente a densidad](experiments/figures/density-final-times.png), [Fu(t)](experiments/figures/density-final-fu.png), [mapa de calor](experiments/figures/density-position-heatmap.png) y [cortes con desvíos](experiments/figures/density-position-cuts.png). Se ejecutaron 154 corridas nuevas y se preservaron los datos originales.

En el complemento de densidad hay diez realizaciones para N={20,50,100,200,400,650}, con x0=r. El menor t90 medio muestreado es N=50 (20,4±3,5 s); el menor t100 medio es N=20 (41±14 s), muy próximo a N=50 (42,5±8,1 s). No demuestra óptimos poblacionales ni una única densidad óptima para ambos criterios. N=650 convirtió en promedio solo el 4,32 % a 300 s; en sus diez realizaciones t90 y t100 son mayores que 300 s.

El mapa comprende 220 realizaciones: N={20,50,100,200}, once posiciones y cinco semillas. Todas alcanzaron t90 antes de 100 s. Las posiciones de menor media son, respectivamente, x0={0,3975;0,3025;0,16;0,2075} m. Son mínimos de la grilla, no coordenadas óptimas exactas ni diferencias estadísticas demostradas.

Reproducción: `python/density_study.py`, `python/density_followup.py`, `python/density_extra.py`, `python/density_plot.py` y `python/density_verify.py`, en ese orden y con un intérprete que tenga las dependencias. Se preservan los conjuntos de 30 s y 300 s, el seguimiento selectivo a 600 s y el grupo exploratorio N=50. El resumen combinado final es `experiments/results/density-complete-summary.csv`; la auditoría está en `density-verification.json` del mismo directorio. No se alteró el motor ni el benchmark de rendimiento.

## Criterios de validación propuestos

| Aspecto | Comprobación |
|---|---|
| Inicialización | N exacto, partículas dentro del dominio, sin solapamientos y velocidades de módulo v0. Fallar con un diagnóstico si no se puede ubicar N. |
| Fuerzas | Nulas sin contacto; repulsivas con contacto; acción y reacción para cada par móvil; obstáculos inmóviles. |
| Pared | Imagen radial actualizada cada paso y fuerza hacia el interior; evitar normalizar un vector nulo en el centro. |
| Integración | Convergencia de la trayectoria del oscilador al reducir h; instantes de posición y velocidad coherentes. |
| Energía | Incluir energía de todos los contactos; contar cada par una vez; medir error respecto a E(0). |
| Conversión | Fresca→usada una sola vez; sin eliminación de partículas; registrar cruces y censura por realización. |
| Estadística | Declarar qué se promedia, número de realizaciones y significado de las barras; no confundir desvío con error estándar. |
| Distribución | Histograma de rapidez normalizado, bins compartidos y ajuste con un solo parámetro energético. |
| Reproducibilidad | Guardar configuración, generador y semillas en metadatos técnicos, sin presentar la semilla aislada como parámetro físico [COR03]. |

Estos criterios son propuestas de trabajo derivadas del modelo; no resultados experimentales ni requisitos textuales adicionales.

## Reutilización del TP3

Revisados sin modificar:

- [`experiments/README.md`](../tp3-billar-metegol/experiments/README.md): protocolo de rendimiento, tf=30 s, mesa vacía, salida a `/dev/null`.
- [`performance.json`](../tp3-billar-metegol/experiments/configs/performance.json) y [`performance-manifest.json`](../tp3-billar-metegol/experiments/results/performance-manifest.json): diez semillas y N={10,25,50,100,200,400}.

El cronómetro de ese protocolo excluye generación inicial y apertura de archivo. Para comparar costos, documentar y armonizar el alcance de medición. COR03 valora el rango hasta N=700, pero ese rango no aparece en estos artefactos; tampoco hay evidencia suficiente allí de la computadora utilizada. Los datos no están validados aún como referencia final del TP4.

## Reglas heredadas para cada estudio

Aplicar desde el principio: teoría general separada del sistema; situación y variable explicadas antes de mostrar resultados; animación del sistema, evolución temporal estática y curva paramétrica; promedios definidos; pocos gráficos legibles; cifras significativas acordes al error y afirmaciones cuantitativamente justificadas [COR03]. La diapositiva única del oscilador es una excepción explícita [TP04, p. 2].

## Uso de IA durante esta preparación

Fecha: 2026-10-15. Agente: Codex, basado en GPT-6 según la identificación disponible en la sesión. Intervención: clasificación de fuentes, extracción local, síntesis con citas, identificación de conflictos y preparación del orden de resolución. No se generaron resultados experimentales ni presentación o informe entregable. Ampliar este registro con las intervenciones posteriores; la declaración final deberá reflejar el uso real [TP04, p. 4].

Actualización de la misma sesión: con diseño aprobado, el agente implementó el motor del oscilador y su post-proceso, escribió y ejecutó pruebas, ejecutó 28 corridas y generó datos y una figura de análisis. El estudiante eligió el despeje algebraico para el amortiguamiento. No se elaboró presentación ni informe entregable; los resultados deberán ser revisados y explicados por los estudiantes.

Actualización del billar: por pedido del estudiante se implementaron geometría, inicialización, contactos elásticos, Verlet original, conversión y salida; post-proceso de energía, estudio del paso y animación independiente. Se agregaron pruebas físicas, del formato y de preservación del primer contacto, y controles con sanitizadores. La tolerancia energética del 0,1 % es una decisión local documentada. El material generado es código, datos y visualizaciones de desarrollo; no una presentación o informe entregable.

2026-10-16: el estudiante eligió red hexagonal y aleatorización Monte Carlo para las configuraciones densas. El agente implementó y probó el generador N=650, el harness con ambos motores y el ejecutor con checkpoints, estadística y censura. La CPU Apple M5 Pro se identificó con consulta local autorizada. Los resultados son artefactos de análisis y deberán ser revisados por los estudiantes para su presentación.

Continuación del punto 2.2: el agente implementó y probó Fu, barrido de once posiciones para dos N y cinco realizaciones, controles de paso a 100 s, estadísticas, checkpoints y animación comparativa. Ejecutó ocho pilotos y 110 corridas principales, y produjo datos y figuras para revisión de los estudiantes. No elaboró la presentación entregable.

Continuación del punto 2.3: el agente implementó y probó histogramas de rapidez, comprobación descriptiva de estabilidad y mínimos cuadrados para Maxwell–Boltzmann 2D con un único parámetro. Ejecutó diez corridas exploratorias de 30 s y diez principales de 60 s, preservó ambas etapas y generó datos y figuras para revisión. No elaboró la presentación entregable.

Cierre de 2.4.a–b: el agente implementó y probó análisis de censura, cotas, tiempos restringidos y mínimos sobre grillas; ejecutó 154 corridas nuevas, incluyendo seguimiento selectivo y N=50 exploratorio; generó el mapa, curvas y datos con auditoría independiente. Se actualizaron los resultados locales y sus límites. No se elaboró la presentación entregable.

2026-10-16, preparación de la presentación por pedido explícito del estudiante: Codex (GPT-6, identificación disponible de la sesión) analizó la guía, las correcciones TP2/TP3 y el formato anterior; produjo un borrador Beamer/PDF y un PPTX con animaciones, figuras derivadas de los resultados, notas y guion de 13 minutos. Esta intervención también debe declararse. No se afirma revisión o autoría final de los estudiantes: falta su participación en la elaboración y validación final conforme a [TP04, p. 4]. No se publicaron animaciones; cinco URL quedan pendientes.
