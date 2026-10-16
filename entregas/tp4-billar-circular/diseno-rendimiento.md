# Rendimiento y densidad — decisiones de implementación

Fecha: 2026-10-16. El estudiante eligió la opción 1: red hexagonal y aleatorización Monte Carlo para N>600.

## Inicialización

Para N≤400 se conserva el rechazo secuencial uniforme en área. Para N>400 se construye una red hexagonal con separación 2r·1,0001, orientación y traslación sorteadas. Se filtran pared y obstáculos, se eligen N sitios con Fisher–Yates y se realizan 500 barridos de movimientos de discos duros sin solapamientos. Cada barrido tiene N propuestas; cada propuesta elige una partícula y un desplazamiento uniforme por coordenada en [−r/4,r/4]. Al finalizar se sortean direcciones uniformes y se asigna módulo v0=1 m/s.

La red tiene margen para N=650 en el billar con obstáculos en contacto. Se valida N exacto, geometría y velocidades al terminar. Este procedimiento produce configuraciones aleatorizadas desde una red, **no garantiza una muestra uniforme del conjunto de configuraciones ni ausencia de orden residual**. Se conservan aceptación y desplazamiento cuadrático respecto de los sitios de partida como diagnósticos de la inicialización, calculados fuera de la simulación. La configuración piloto de semilla 1, con 500 barridos, aceptó el 8,78 % de los movimientos y desplazó cada partícula aproximadamente 0,01089 m en RMS; el orden hexagonal global de seis vecinos resultó aproximadamente 0,572. Estos son diagnósticos de esa configuración, no propiedades universales.

## Medición comparable

Un harness experimental independiente enlaza los motores reales TP3 y TP4 con el mismo compilador y flags C++20 -O3 -DNDEBUG. No modifica el TP3 ni forma parte del motor para entregar. Usa steady_clock alrededor de la llamada al simulador; generación y escritura quedan fuera del cronómetro para ambos. En TP4 se conserva una copia del estado final desde el callback; en TP3 el estado final queda en System. La planificación inicial de eventos y las verificaciones internas pertenecen a cada motor y quedan dentro de su tiempo.

TP4: N={20,100,200,400,650}, obstáculos en contacto x0=r, tf=30 s, h=0,00005 s y 10 semillas por N [TP04, p. 3]. TP3: se recalcula en la misma computadora el rango histórico N={10,25,50,100,200,400}, mesa vacía, tf=30 s y las mismas diez semillas. No se comparan tiempos medidos por métodos distintos ni se reemplazan archivos históricos del TP3. La comparación corresponde a los dos sistemas pedidos, de áreas casi iguales, no a un mismo sistema con dos motores intercambiables.

Las corridas son secuenciales. Los resultados se guardan por realización, con una huella del protocolo, hardware y fuentes. Solo se reutiliza una realización si esa huella coincide y su trayectoria conserva el hash. El hardware se identifica mediante consulta local autorizada; el entorno TP4_CPU_DESCRIPTION permite proporcionar ese dato verificado cuando el sandbox bloquea sysctl.

## Reutilización para densidad

Se guardan estados inicial y final de cada corrida TP4, con first_contact_step por partícula. El primer contacto es estado histórico, no un observable calculado online. Con él Python obtiene exactamente a resolución h los cruces t90 y t100, sin repetir las simulaciones y sin necesitar cuadros intermedios [TP04, p. 4] [COR02].

Los promedios y desvíos muestrales se calculan entre las diez realizaciones de cada N, después de obtener el tiempo por realización [COR03]. Las barras son desvíos estándar (ddof=1). Si alguna corrida no alcanza un umbral en 30 s, la media ordinaria de ese grupo queda sin estimar: se informa cantidad de censuras, Fu final, media condicional de los tiempos observados identificada como tal y cota inferior para la media completa. No se reemplaza el tiempo desconocido por 30 s como si fuera una medición.

Cada corrida verifica también energía inicial y final; ese control no reemplaza el estudio de máximos temporales de 2.1.a. El piloto denso N=650 con obstáculos dio máximo muestreado aproximado 0,00904 % durante 0,5 s; la diferencia de energía final a 30 s fue aproximadamente 0,04089 %. El paso se revisará si alguna realización del estudio supera el criterio energético del 0,1 % al final.
