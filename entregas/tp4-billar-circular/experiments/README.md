# Registro técnico — sistema 1 del TP4

Este es un registro de desarrollo y validación, no un informe entregable.

## Protocolo

Se ejecutaron los cuatro métodos para siete pasos, h=5/M con M={1000,2000,5000,10000,20000,50000,100000}; intervalo h=[0,00005;0,005] s. Las constantes, condiciones iniciales y solución de referencia corresponden a [T04, p. 37]; los cuatro métodos y la comparación de ECM son los exigidos por [TP04, p. 1].

El motor genera estados sin observables. Python compara cada posición con la solución analítica en el mismo tiempo y calcula el promedio temporal de los cuadrados de los errores para n=1,...,M. Se excluye t=0, se incluye t=5 s, y el resultado tiene unidades de m². No hay promedios entre partículas, semillas ni realizaciones. No se agregan barras de error estocásticas a un cálculo determinista [COR02] [COR03].

Verlet y Velocity Verlet utilizan el despeje algebraico de la velocidad en la fuerza amortiguada. Beeman usa el predictor-corrector de T04 p. 20, con aceleración recalculada después de corregir la velocidad. Euler PC sigue T04 p. 23. Los estados previos se estiman con Taylor de segundo orden; la solución exacta no se usa para arrancar los integradores. En Verlet se calcula un estado auxiliar fuera del horizonte para recuperar la velocidad centrada del último instante, sin incluir una muestra adicional.

## Resultados verificados

| Método | ECM con h=0,005 s (m²) | ECM con h=0,00005 s (m²) |
|---|---:|---:|
| Beeman | 2,079 × 10⁻⁷ | 2,060 × 10⁻¹⁵ |
| Verlet original | 2,378 × 10⁻⁷ | 2,391 × 10⁻¹⁵ |
| Velocity Verlet | 2,378 × 10⁻⁷ | 2,376 × 10⁻¹⁵ |
| Euler predictor-corrector | 4,683 × 10⁻³ | 8,459 × 10⁻⁷ |

Beeman obtuvo el menor ECM en todos los pasos de este barrido. La afirmación se limita a posición, este oscilador, estos arranques y variantes; no compara costo computacional ni establece qué esquema conviene para otros sistemas.

Verlet y Velocity Verlet se superponen prácticamente en la figura. Con la velocidad centrada y el arranque adoptado, las ecuaciones de Velocity Verlet pueden eliminarse para recuperar la misma recurrencia de posiciones de Verlet: la coincidencia es esperable en aritmética exacta. Las diferencias pequeñas son numéricas; no se cambiaron los métodos para separar artificialmente sus curvas.

Las pendientes del ECM entre los dos pasos más pequeños son aproximadamente 4,00 para Beeman, 3,99 para Verlet, 4,00 para Velocity Verlet y 1,99 para Euler PC. Son pendientes del **error cuadrático medio**, no del error de posición. El barrido no muestra una meseta de ECM, aunque Verlet presenta pequeñas diferencias respecto de su forma en velocidades al reducir el paso.

No se midieron tiempos de ejecución ni se eligió el paso del billar. Para el sistema 2 deberá hacerse su propio estudio de conservación de energía [TP04, p. 3].

## Verificación y reproducción

- C++: movimiento libre; oscilador sin amortiguamiento y amortiguado contra solución analítica; convergencia en tres pasos; estado inicial, índices, horizonte y velocidad final centrada.
- Python/CLI: referencia analítica en regímenes libre, oscilatorio, crítico y sobreamortiguado; ECM con datos de error conocido; contrato CSV; entradas inválidas; detección de estados no finitos; convergencia de los cuatro métodos a través del ejecutable compilado.
- Sanitizadores AddressSanitizer y UndefinedBehaviorSanitizer: sin hallazgos.
- Las 28 trayectorias cumplen esquema, cantidad de muestras, timestamps, estado inicial y finitud. La figura PNG se inspeccionó visualmente.

Ejecutar `make test`, `make sanitize` y `make oscillator-study` desde la raíz del TP4, con las dependencias indicadas en su README. El estudio regenera las corridas; no reutiliza archivos de otras configuraciones. El manifiesto registra constantes, arranques mediante hashes del código, compilador, binario, versiones Python, plataforma y hashes de cada trayectoria y artefacto. Los comandos del manifiesto se interpretan desde la raíz del TP4; el sufijo `.partial` identifica la salida anterior a su validación y renombrado.
