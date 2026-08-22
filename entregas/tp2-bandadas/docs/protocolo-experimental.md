# Protocolo experimental

Este protocolo separa la implementación terminada de las decisiones empíricas que todavía deben calibrarse. Evita elegir un descarte o una cantidad de semillas solo porque producen una figura razonable.

## 1. Verificación del motor

1. Ejecutar `make test`, `make sanitize` y `make visual-test`.
2. Confirmar que el CIM produce exactamente las mismas listas que fuerza bruta.
3. Confirmar que los CSV incluyen `N`, `L`, `M`, `rc`, `v`, `dt`, modelo, densidad, `eta` y semilla.
4. No combinar resultados cuyos metadatos físicos difieran.

## 2. Piloto

Los barridos `pilot.json` y `cluster-low-density.json` localizan regiones interesantes. Usan solo dos semillas, por lo que sirven para diseñar el experimento y no para extraer conclusiones finales.

El piloto principal ya indicó una región aproximada de transición de Vicsek entre `eta = 0.5` y `0.75`. El votante requiere resolución más fina cerca de cero. En las densidades `2`, `4` y `8`, `S` suele estar cerca de uno; por eso se agregan los sistemas de baja densidad indicados por la cátedra [N-2026-08-22-densidades-s-tp2].

## 3. Calibración temporal

1. Ejecutar `experiments/configs/calibration.json`.
2. Para cada modelo, densidad y zona de `eta`, graficar `va(t)` y `S(t)`.
3. Dividir cada corrida en bloques completos de igual duración. Un bloque parcial final se descarta.
4. Proponer un inicio estacionario solamente cuando las medias de bloques posteriores fluctúen sin una deriva sistemática comparable con sus fluctuaciones.
5. Repetir la inspección sobre más de una semilla. Una sola trayectoria no justifica el descarte de toda una combinación.
6. Registrar cada valor elegido en un CSV con este encabezado exacto:

```text
model,density,eta,stationary_start
```

Si una corrida todavía deriva al terminar, no se adelanta artificialmente el inicio estacionario: se aumenta `steps` y se vuelve a calibrar.

## 4. Calibración de la malla y de las realizaciones

1. Conservar una malla amplia de `eta` para mostrar los extremos ordenado y desordenado.
2. Refinar la malla donde `va` o `S` cambien con rapidez.
3. Comparar los resúmenes obtenidos con subconjuntos crecientes de semillas.
4. Aceptar la cantidad de realizaciones cuando agregar semillas no cambie materialmente la media ni el desvío en las regiones relevantes.

Las plantillas de producción proponen diez semillas, pero ese número no queda validado hasta realizar esta comprobación.

## 5. Producción

1. Copiar las plantillas `production.example.json` y `cluster-production.example.json` a archivos definitivos.
2. Incorporar la duración, malla y semillas justificadas durante la calibración.
3. Usar directorios de salida nuevos. Cada uno conservará un `manifest.json` y no admitirá otra configuración.
4. Resumir cada semilla sobre su intervalo estacionario y luego calcular media y desvío entre semillas.
5. Generar, para ambos modelos, las series temporales con su línea de descarte, `va` contra `eta`, `S` contra `eta` y `va` contra `S` [TP02, p. 2].

## 6. Casos visuales y CIM

Las animaciones se generan aparte desde archivos de texto. Cada cuadro muestra el estado espacial, `va(t)` y `S(t)`, y la velocidad se informa como `trajectory_every * dt * fps` unidades simuladas por segundo [TP02, p. 1].

El tiempo del CIM se resume por `N`, modelo y configuración geométrica. La comparación con TP1 debe describirse como orientativa: TP2 reconstruye vecindarios en cada paso y además ejecuta dinámica y observables, mientras que las configuraciones físicas del benchmark anterior no son idénticas.

## 7. Cierre

Antes de entregar:

1. regenerar todas las figuras desde los CSV finales;
2. verificar que cada leyenda identifique modelo, densidad real y, donde corresponda, densidad nominal;
3. revisar que ninguna figura use pilotos como resultados finales;
4. ejecutar nuevamente todas las pruebas;
5. crear el ZIP mediante `scripts/package_code.py`, que incluye únicamente el motor C++ y su Makefile.
