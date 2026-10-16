# Diseño — cierre de TP4 2.4.a y 2.4.b

Pedido explícito del estudiante: cerrar ambos puntos. Se conserva el motor y se amplía el análisis reproducible; no se prepara la presentación entregable.

## Densidad (2.4.a)

La fuente primaria exigida son las 50 corridas de 30 s del benchmark (N={20,100,200,400,650}, diez realizaciones, x0=r). Se reutilizan sin sobrescribir ni cambiar sus tiempos de ejecución [TP04, pp. 3–4]. Se obtienen primeros cruces desde `first_contact_step` del estado final. Las medias ordinarias solo se publican si el grupo completo alcanzó el umbral; las demás se acompañan de número de censuras, Fu final y cotas inferiores.

Como complemento, se siguen las mismas condiciones iniciales hasta 300 s con h inicial=0,0000125 s. Se reutilizan las corridas existentes de 100 s que ya observaron t100 y cuya condición inicial coincide exactamente: un primer cruce ya observado no necesita seguimiento posterior. Para los demás casos se importa el estado inicial del benchmark con 17 dígitos significativos. No se presenta esta simulación refinada como una continuación bit a bit del benchmark: cambia h. Se informa el cambio de resolución y se conserva el conjunto obligatorio de 30 s por separado.

Se controla energía total desde estados cada 1 s, incluyendo pares, pared y obstáculos. Se permite hasta dos reducciones adicionales de h si el error máximo muestreado supera el criterio local de 0,1 %. Cada intento queda registrado. Los casos reutilizados conservan sus controles energéticos originales de extremos; no se inventa un máximo temporal para ellos.

300 s es un límite explícito de observación, no una garantía de conversión. Si persiste censura, se informa la imposibilidad de conocer la media ordinaria sin extrapolar. También se calcula la media **restringida** de min(T,tau), con tau=30 s y tau=300 s: es un observable diferente, identificable con los seguimientos disponibles, y nunca se etiqueta como media completa de T. No se ajustan colas exponenciales ni se reemplazan tiempos desconocidos por tiempos medidos ficticios.

Decisión adaptativa durante la ejecución: dos primeras realizaciones N=400 terminaron con 399/400 convertidas a 300 s. Se agrega seguimiento selectivo a 600 s para los casos N≤400 que sigan censurados, conservando los conjuntos originales de 30 y 300 s. Se usa la misma condición inicial y el mismo h refinado; se verifica igualdad exacta del estado de 300 s con el ensayo anterior. Si persiste censura, se mantiene. N=650 no se extrapola: las diez realizaciones convirtieron apenas el 4,32 % en promedio a 300 s. El seguimiento selectivo tiene contrato y manifiesto propios.

Segunda ampliación exploratoria: los cinco casos N=50 del mapa en x0=r sugirieron menor t90 que N=20. Se completan diez realizaciones N=50 con cinco simulaciones nuevas hasta 300 s, h=0,0000125 s. Se añaden al complemento de densidad con contrato propio, sin modificar el benchmark original ni los cinco casos por celda del mapa. Se distingue mínimo de t90 y de t100, y no se presenta la elección adaptativa como una prueba confirmatoria.

## Mapa (2.4.b)

Se estudia t90 en N={20,50,100,200}, once posiciones uniformes x0 entre r y R−r, cinco realizaciones y corte 100 s: 220 casos. Se reutilizan 110 de 2.2 y se agregan N=50 y N=200. Los seguimientos más largos de N=200 en x0=r se truncan explícitamente al corte 100 s usando los primeros contactos; no se usa información futura para rellenar una celda censurada [TP04, p. 4].

Cada celda contiene la media de cinco t90 por realización, con su desvío en CSV. Celdas censuradas se enmascaran o rotulan como tales, sin interpolarlas. El mínimo por fila solo se certifica sobre la grilla si su media completa no puede ser superada por la cota inferior de una celda censurada. Es un mínimo **muestral** y no prueba significancia estadística ni determina el óptimo continuo. Para apoyar la lectura se muestran además cortes de t90(x0) con desvíos y evolución Fu(t) reconstruida a partir de contactos [COR03].

## Ejecución y validación

El motor C++ únicamente produce estados. Python calcula energía, conversiones, estadísticas y gráficos. El ejecutor principal y el seguimiento usan hasta cuatro simulaciones independientes cada uno; el complemento N=50 usa dos. Pueden solaparse, con un máximo de diez procesos frente a 15 CPU lógicas identificadas por el intérprete. No se están cronometrando para comparar rendimiento. La CPU y las fuentes del benchmark permanecen intactas. Se guardan contratos, comandos, hashes de archivos y checkpoints por caso. El ejecutor rechaza fuentes incompatibles y permite reanudar. Los gráficos se generan con un programa independiente para no alterar fuentes durante corridas largas.

Pruebas: censuras sin medias inventadas; media restringida diferenciada de media completa; seguimiento insuficiente rechazado; semilla duplicada rechazada; mínimo no certificado frente a una celda censurada que todavía podría mejorarlo. Verificación final de grilla, número de semillas, hashes, tiempos, energía y figuras. Se interpretan densidad, mezcla y acceso a obstáculos sin afirmar que se midió directamente la frecuencia de colisiones.
