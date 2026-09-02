# Rediseño de Implementación - presentación TP2

## Objetivo

Reemplazar las dos diapositivas actuales de Implementación por una explicación fiel y breve de cómo el modelo matemático se traduce al motor C++20. La sección debe mostrar arquitectura y pseudocódigo, sin describir postproceso ni formatos de entrada/salida, conforme a [GPRES, p. 2].

## Diapositiva 7 - Arquitectura del motor

Diagrama de componentes vectorial, definido en Mermaid y renderizado con Mermaid CLI. Se usa un estilo `handDrawn` simple, cercano a Excalidraw, y la paleta de la presentación. Debe mostrar estas responsabilidades reales:

- `run_simulation`: coordina el ciclo;
- `System`: conserva partículas y tiempo;
- búsqueda de vecinos por CIM: produce `NeighborList`;
- dinámica: aplica Vicsek o votante y construye el estado siguiente;
- observables: calcula polarización y componente gigante;
- geometría periódica: servicio compartido por CIM y dinámica.

Las flechas representarán dependencias reales del código. No se mostrarán módulos de Python, archivos CSV ni detalles de postproceso.

El fuente editable queda en `presentacion/figuras/arquitectura-motor.mmd` y su derivado vectorial en `presentacion/figuras/arquitectura-motor.pdf`.

## Diapositiva 8 - Algoritmo del motor

Pseudocódigo de un ciclo completo:

1. inicializar el estado y el generador aleatorio;
2. construir vecinos con CIM;
3. medir `va` y `S` sobre el estado corriente;
4. crear un estado siguiente separado;
5. para cada partícula, elegir la regla, avanzar la posición con el ángulo corriente y calcular el nuevo ángulo con ruido;
6. reemplazar el estado sólo al finalizar el recorrido.

La actualización sincrónica debe quedar explícita. Las validaciones se conservarán en un bloque breve.

## Guion y duración

`SPEECH.md` mantendrá las diapositivas 7 y 8 bajo Eugenio y el bloque total de 4:15. El texto explicará las responsabilidades del UML y recorrerá el pseudocódigo sin leer código fuente línea por línea. El total de la presentación seguirá siendo de 13 minutos.

## Verificación

- Compilar con Tectonic sin cajas desbordadas.
- Confirmar que el PDF conserve 24 páginas y el encabezado con cinco secciones.
- Renderizar e inspeccionar todas las páginas, con atención especial a las diapositivas 7 y 8.
- Ejecutar `./scripts/verificar_repo.sh` y `git diff --check`.
