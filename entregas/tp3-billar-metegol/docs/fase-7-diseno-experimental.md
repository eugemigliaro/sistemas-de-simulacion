# Fase 7 — Diseño experimental

## Objetivo y alcance

La fase 7 produce los resultados cuantitativos de los puntos 1.1, 1.2 y 1.3
del TP3. Parte del motor C++ y del postproceso `tp3analysis` ya implementados,
y termina con datos crudos, resúmenes estadísticos, figuras reproducibles y
una configuración de obstáculos justificada [TP03, p. 3].

Quedan fuera de esta fase la animación, la preparación del ZIP de entrega y el
cierre de la presentación, que corresponden a la fase 8. Las figuras y las
conclusiones que necesite la presentación sí son productos de esta fase.

El trabajo se divide en cuatro pasos. Después de cada paso se revisan sus
resultados antes de comenzar el siguiente.

## Criterios generales

- El motor de producción es `queue`; `naive` se conserva como control y puede
  aparecer en una comparación complementaria de rendimiento.
- Cada realización usa una semilla distinta. Cuando se comparan
  configuraciones se usan las mismas semillas para reducir ruido ajeno al
  cambio estudiado.
- `t90` se calcula por realización y luego se promedia. No se extrae de una
  curva promedio de `Fu(t)`.
- Los datos crudos se preservan separados de los resúmenes y de las figuras.
- Los scripts registran el comando, la semilla, la configuración y cualquier
  fallo. Una ejecución parcial puede reanudarse sin repetir resultados válidos.
- Las barras se identifican explícitamente como desvío estándar o error
  estándar. Para cumplir el punto 1.1 se grafica el desvío estándar.
- Una configuración que no permita generar las 100 partículas se registra
  como inválida y no se reemplaza silenciosamente.

## Paso 1 — Infraestructura y rendimiento

### Propósito

Construir el ejecutor reproducible común a la fase y resolver el punto 1.1:
tiempo de ejecución del motor final sobre la mesa vacía hasta `tf = 30 s`, con
al menos diez realizaciones por valor de `N` [TP03, p. 3].

### Diseño

1. Preparar el entorno Python declarado en el proyecto y verificar los tests
   de C++, Python y sanitizers.
2. Agregar un ejecutor de lotes que invoque el binario release, capture el
   resumen de `stderr`, valide el código de salida y escriba una fila por
   realización.
3. Ejecutar un piloto con `N = {10, 25, 50, 100, 200, 400}` y semillas 1 a 10.
   Si un punto hace que el tiempo total sea desproporcionado, el rango final se
   ajusta antes de la corrida definitiva y se documenta el criterio.
4. Resumir por `N` la media, el desvío estándar, el error estándar y la cantidad
   de realizaciones.
5. Generar el gráfico requerido de tiempo medio contra `N`, con puntos visibles
   y barras de desvío estándar.

### Productos para revisión

- CSV crudo con una fila por corrida.
- CSV resumido con una fila por `N`.
- Figura de tiempo de ejecución contra `N`.
- Comandos y semillas documentados.
- Informe breve de fallos, advertencias y decisión sobre el rango definitivo.

### Criterio de aceptación

Cada `N` aceptado tiene diez corridas válidas, la simulación alcanza `30 s`, el
resumen se puede regenerar desde el CSV crudo y la figura coincide con ese
resumen.

## Paso 2 — Barrido grueso de obstáculos

### Propósito

Explorar de forma sistemática una familia simple y justificable con `N = 100`:
un obstáculo circular cuyo centro está sobre el eje longitudinal
`y = W/2`. Se varían su radio `R` y su posición `x` [TP03, p. 3].

### Diseño

1. Definir una grilla gruesa de radios y posiciones después de medir que todas
   las configuraciones permiten generar 100 partículas.
2. Aprovechar la simetría entre los dos arcos: basta estudiar una mitad de la
   mesa y el centro; `x` y `L-x` son configuraciones reflejadas equivalentes.
3. Ejecutar diez semillas comunes por configuración, con `tmax = 100 s`, y
   agregar la mesa vacía como referencia.
4. Calcular `t90`, goles finales, media, desvío, error estándar y cantidad de
   corridas que no alcanzaron el umbral.
5. Producir un mapa o gráfico del barrido y seleccionar un conjunto pequeño de
   finalistas, sin declarar aún una configuración ganadora.

### Productos para revisión

- Archivos de configuración de la grilla.
- CSV crudo y resumen del barrido.
- Visualización de `t90` en función de `x` y `R`.
- Comparación explícita con la mesa vacía.
- Lista argumentada de finalistas.

### Criterio de aceptación

Todas las configuraciones incluidas son geométricamente válidas, cada punto
tiene diez realizaciones comparables y los finalistas surgen de los datos, no
de una selección visual previa.

## Paso 3 — Refinamiento y selección

### Propósito

Refinar la región más prometedora del paso 2 y elegir la configuración que se
presentará en la competencia.

### Diseño

1. Construir una grilla fina alrededor de los mejores puntos del barrido
   grueso.
2. Usar diez realizaciones para esa exploración local.
3. Confirmar las finalistas y la mesa vacía con 30 semillas comunes.
4. Comparar no solo la media de `t90`, sino también su dispersión, las corridas
   que no alcanzan el umbral y los goles finales.
5. Generar curvas representativas de `Fu(t)` y el archivo definitivo con líneas
   `xk yk Rk`.

### Productos para revisión

- Comparación de las finalistas con 30 realizaciones.
- Curvas representativas de `Fu(t)`.
- Recomendación argumentada.
- Archivo de configuración candidato para la competencia.

### Criterio de aceptación

La configuración elegida mejora de forma defendible la referencia y satisface
las restricciones geométricas y de generación. La elección queda sujeta a
revisión antes de declararla definitiva.

## Paso 4 — Difusión y cierre

### Propósito

Estimar el coeficiente de difusión para la mesa vacía y configuraciones
representativas, y evaluar su relación con `t90` [TP03, p. 3].

### Diseño

1. Generar trayectorias con `--save-every 10` para la mesa vacía, la ganadora y
   configuraciones representativas del barrido.
2. Usar la mesa vacía para identificar una ventana aproximadamente difusiva,
   separada del régimen balístico inicial y del confinamiento tardío.
3. Fijar esa ventana antes de comparar configuraciones y usarla sin cambios en
   todas ellas.
4. Ajustar `DCM(t) = 4Dt` por el origen mediante el barrido de `E(c)` ya
   implementado [T03, p. 25] [T00, pp. 79-82].
5. Presentar como estimación principal la media de `D` por realización y su
   dispersión entre semillas. Las otras estimaciones del postproceso quedan
   como control.
6. Graficar DCM y ajuste, `E(c)`, comparación de `D` y relación entre `D` y
   `<t90>`.
7. Registrar si los datos respaldan, contradicen o no permiten afirmar una
   correlación.

### Productos para revisión

- CSV de DCM y de estimaciones de `D`.
- Justificación de la ventana común.
- Figuras de DCM, ajuste y `E(c)`.
- Comparación de `D` con `<t90>`.
- Conclusiones de la fase 7 respaldadas por las figuras.

### Criterio de aceptación

La ventana se elige antes de comparar configuraciones, el mismo procedimiento
se aplica a todas, las figuras se regeneran desde datos preservados y cada
conclusión se puede rastrear hasta esos datos.

## Manejo de errores y verificación

- Un proceso que termina con código distinto de cero no produce una medición
  válida; se conserva su diagnóstico.
- Una salida sin el resumen esperado o que no llega al tiempo solicitado se
  rechaza.
- No se mezclan realizaciones con parámetros físicos u obstáculos distintos.
- No se reutilizan semillas dentro de un mismo promedio.
- Los scripts de resumen y gráficos tienen pruebas sobre datos pequeños y
  deterministas.
- Al cerrar cada paso se ejecutan las pruebas pertinentes y
  `./scripts/verificar_repo.sh`, y se revisa el diff antes de presentarlo.

## Secuencia de aprobación

El orden es estricto: paso 1, revisión; paso 2, revisión; paso 3, revisión;
paso 4, revisión final. No se avanza automáticamente entre pasos.
