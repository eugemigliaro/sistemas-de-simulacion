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

La versión final reemplaza este primer diagrama por el flujo ya empleado entre el motor y los resultados. La diapositiva independiente de flujo se elimina para evitar repetición. El diagrama UML se conserva como descripción interna del motor.

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

Además del PDF de entrega, se genera un PPTX de alta fidelidad visual para importar en Google Slides. Cada página del PDF ocupa una diapositiva completa; los videos se agregan luego como objetos nativos de Google Slides sobre los fotogramas correspondientes.

## Enlaces de las animaciones

El PDF muestra un vínculo visible y clicable debajo de cada fotograma, como exige [GPRES, p. 3]. Se usa la forma corta `youtu.be` para evitar desbordes, conservando como destino la URL original de YouTube. La correspondencia verificada mediante los metadatos públicos es:

- Vicsek, $\rho=4$, $\eta=0{,}25$: `rdCnXcYPSuY`;
- votante, $\rho=4$, $\eta=0{,}25$: `M_k5zIgXsTU`;
- Vicsek, $\rho=0{,}32$, $\eta=0{,}25$: `VN1cVtJb4IU`.
