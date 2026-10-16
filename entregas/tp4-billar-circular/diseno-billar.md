# Billar circular y estudio 2.1.a

Diseño para la implementación solicitada: motor del sistema 2 y selección inicial del paso por conservación de energía. Los estudios 2.1.b–2.4 quedan para las etapas siguientes.

## Decisiones

- C++20 genera estados en texto con Verlet original: posiciones mediante dos pasos y velocidades centradas sincronizadas. Se conserva la interfaz `oscillator` y se agrega `billiard` al ejecutable.
- Contactos repulsivos de resorte lineal entre pares, obstáculos y pared, con parámetros y geometría de [TP04, p. 2] y [TP04, p. 3]. Para pares se usa una grilla de lado 2r, reconstruida en cada paso; se valida contra todos los pares. Esta alternativa evita el costo cuadrático de un motor ingenuo, sin introducir una lista de vecinos con vigencia temporal que deba ajustarse.
- Inicialización por rechazo uniforme en área, con generador mt19937_64 y cota de intentos. Si no se pueden ubicar todas las partículas, falla explícitamente: nunca cambia N ni acepta superposiciones. La inicialización de densidades mayores que las alcanzables por rechazo requerirá una etapa específica antes del benchmark N>600.
- Salida CSV por partícula: paso, tiempo, ID, posición, velocidad, estado usada y paso del primer contacto con obstáculo (−1 si no ocurrió). Guardar este último dato como estado histórico permite recuperar tiempos de conversión con resolución h aunque los cuadros estén separados por n pasos. No calcular Fu, energía ni promedios dentro del motor [COR02].
- Posiciones iniciales opcionales desde CSV para repetir exactamente una configuración entre pasos y permitir pruebas de colisiones. Las configuraciones físicas y controles numéricos quedan registrados junto a cada trayectoria.

## Experimento de energía

N=300 sin obstáculos; misma condición inicial por semilla y duración 2 s; pasos iniciales {0,001;0,0005;0,00025;0,0001;0,00005;0,000025} s. Guardado cada max(h,0,0005 s), siempre múltiplo entero de h. Python procesa las trayectorias por cuadros y suma energía cinética y potencial de pares/pared/obstáculos, contando cada par una sola vez [T04, p. 42].

Observable propuesto: máximo muestreado de |E(t)−E(0)|/E(0), sin promediarlo entre realizaciones. Criterio de trabajo: elegir el mayor paso con error ≤0,001, siempre que todos los pasos menores también cumplan. Si ninguno pasa, ampliar el barrido hacia pasos menores; si aparece inestabilidad, registrarla y no convertirla en una medición válida.

Antes de dar la selección por válida, comprobar una segunda condición inicial, repetir el candidato durante 30 s y ejecutar una corrida densa del candidato (cada paso) durante 0,5 s. Comparar su máximo con el de la misma trayectoria submuestreada a la cadencia ordinaria; exigir una diferencia menor al 10 % de la tolerancia energética y que ambas cumplan. Si falla, aumentar la cadencia y repetir la selección. La tolerancia y los horizontes son decisiones locales, no umbrales fijados por la cátedra.

Entregar dos figuras estáticas: E(t) para los pasos ensayados y error energético contra h con tolerancia indicada. Conservar series, resumen, trayectorias comprimidas y manifiesto con hashes, versiones y comandos. No generar presentación o informe entregable.

## Pruebas y cierre

Contrastar fuerzas con un cálculo independiente de todos los pares; verificar repulsión, acción/reacción, pared radial y oblicua, ausencia de fuerza sin contacto, conversión irreversible y conservación de N. Comparar colisiones binarias con solución analítica del resorte y reflexión contra obstáculo/pared al disminuir h. Validar inicialización, determinismo por semilla, salida completa y sincronizada, primer contacto y rechazo de entradas inválidas. Python verifica potenciales conocidos y pérdida de información al submuestrear.

La etapa se considera completa con motor probado, barrido ejecutado, figuras inspeccionadas y selección documentada con sus límites. No se reutilizará automáticamente el paso del oscilador.
