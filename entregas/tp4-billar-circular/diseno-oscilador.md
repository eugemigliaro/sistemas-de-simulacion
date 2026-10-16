# Primera etapa del TP4: oscilador amortiguado

Estado: diseño aprobado e implementado. Se acordó despejar algebraicamente el amortiguamiento en Verlet y Velocity Verlet; el estudio de 28 corridas y sus pruebas están disponibles. Ver comandos y resultados en README.md.

## Objetivo y alcance

Resolver los puntos 1.1 y 1.2: comparar Beeman, Verlet original, Velocity Verlet y Euler predictor-corrector con la solución analítica del oscilador, calculando ECM para distintos pasos menores a 0,01 s [TP04, p. 1]. El resultado será una figura log–log con cuatro curvas, los datos que la sustentan y comandos reproducibles. La presentación final del sistema 1 solo admite esa figura en una diapositiva [TP04, p. 2].

## Alternativas consideradas

1. **C++20 para trayectorias y Python para análisis (recomendada).** Respeta la tecnología configurada y la separación motor/post-proceso; permite continuar después con el billar.
2. **Prototipo íntegro en Python.** Acorta la exploración inicial, pero requiere trasladar después los integradores al motor configurado.
3. **Implementar oscilador y billar juntos.** Permite compartir infraestructura desde el comienzo, pero amplía la primera etapa y dificulta aislar errores numéricos.

Se propone la primera alternativa, con un alcance limitado al oscilador. No se necesita decidir todavía la arquitectura del billar.

## Modelo y convenciones

Usar m=70 kg, k=10000 N/m, gamma=100 kg/s, posición inicial 1 m, velocidad inicial −5/7 m/s y duración 5 s. La solución de referencia es la de T04 p. 37; la remisión a la 36 en la consigna es una errata documentada [T04, p. 37] [TP04, p. 1].

Las ecuaciones verificadas están en [la wiki de integradores](../../wiki/temas/paso-temporal-e-integradores.md). Las siguientes adaptaciones son decisiones propuestas, no instrucciones textuales adicionales de la cátedra:

- **Verlet original:** conservar la recurrencia de posiciones y usar velocidad centrada en la fuerza amortiguada. Al sustituirla en la ecuación, despejar la posición futura:
  `r_next = [(2 − k*h*h/m)*r − (1 − gamma*h/(2*m))*r_prev] / [1 + gamma*h/(2*m)]`.
- **Velocity Verlet:** despejar algebraicamente la velocidad futura que aparece en la aceleración amortiguada, como se desarrolla en la wiki.
- **Beeman:** variante predictor-corrector de T04 p. 20. Evaluar la aceleración para corregir la velocidad con la velocidad predicha; después recalcular la aceleración con el estado corregido para conservarla en el siguiente paso.
- **Euler predictor-corrector:** seguir exactamente las etapas de T04 p. 23, sin cambiarlo por otro método con el mismo nombre.

Para Verlet, iniciar `r_prev = r0 − h*v0 + h*h*a0/2`. Para Beeman, estimar el estado previo con Taylor de segundo orden, incluyendo `v_prev = v0 − h*a0 + h*h*j0/2`, donde `j0 = −(k*v0 + gamma*a0)/m`; evaluar desde ese estado la aceleración previa. No usar la solución exacta para inicializar el motor: reservarla para la validación independiente.

## Componentes y archivos

- `cpp/`: modelo del oscilador, cuatro integradores, ejecutable de consola y pruebas numéricas; compilación con Make y C++20.
- `python/`: post-proceso que lee trayectorias, evalúa solución analítica, calcula ECM y genera la figura con NumPy/Matplotlib.
- `experiments/`: configuración del barrido, manifiesto, resumen CSV y figura; trayectorias regenerables en una carpeta ignorada por Git.
- `Makefile` y `README.md`: comandos para compilar, verificar y ejecutar el estudio.

Cada trayectoria tendrá columnas `step,time,position,velocity`, escritas con precisión suficiente para conservar el error numérico; la configuración identificará método, paso y constantes. El motor no calculará ECM. En Verlet se escribirá la velocidad centrada correspondiente al tiempo de la posición; se calculará un estado auxiliar posterior al final para cerrar la última velocidad sin agregar muestras al análisis.

## Experimento y análisis

Pasos implementados: `h=5/M`, con M en {1000, 2000, 5000, 10000, 20000, 50000, 100000}. Todos son menores a 0,01 s y llegan exactamente al mismo horizonte físico mediante contador entero. La interfaz recibe duración y cantidad de pasos, y deriva h para evitar incompatibilidad entre horizonte y paso. Rechaza entradas no finitas, cantidades de pasos no positivas y métodos desconocidos.

Calcular `ECM = sum((r_n − r_exact(t_n))²)/M` para n=1,...,M: se excluye t=0 y se incluye t=5 s. Este promedio es temporal, no entre partículas ni realizaciones. No lleva barras de dispersión entre realizaciones porque el problema es determinista [TP04, p. 1] [COR03]. Conservar también el error máximo de posición como diagnóstico técnico.

Comparar ECM en el intervalo de pasos estudiado; comprobar finitud y convergencia al refinar, e identificar un eventual piso de redondeo. No declarar de antemano qué método gana ni atribuir un orden global a partir de una fórmula local de Taylor.

## Validación y criterio de cierre

Comprobar movimiento libre y oscilación sin amortiguamiento para detectar errores de arranque e índices; verificar posición y velocidad iniciales, timestamps y duración exacta; contrastar el oscilador amortiguado con la solución analítica en varios pasos. Incluir un control independiente del ECM con un archivo pequeño cuyo error sea conocido. No se agregó fuerza externa constante al modelo únicamente para probarlo.

La etapa queda terminada cuando los cuatro métodos generan trayectorias válidas, el estudio se reproduce con un comando, la figura contiene las cuatro curvas con ejes y unidades, y las limitaciones observadas quedan documentadas. Las corridas del billar y sus decisiones experimentales pertenecen a la etapa siguiente.

## Revisión

Se revisaron alcance, arranques, sincronización temporal, separación de responsabilidades y normalización del error. Las alternativas numéricas están identificadas como propuestas. No se hace commit: las instrucciones del repositorio lo reservan a un pedido explícito.
