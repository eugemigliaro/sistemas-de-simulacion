# Auditoría de la presentación TP4 contra consigna, entregas y devoluciones

Fecha: 2026-10-16. Revisión solicitada por el estudiante. Este documento es un análisis de trabajo; no modifica ni aprueba la presentación entregable.

## Cantidad de diapositivas

**No hay un número total obligatorio de diapositivas de resultados.** El TP4 exige una presentación oral de 13 minutos [TP04, p. 1]. Para el sistema 1 sí fija **exactamente una diapositiva, únicamente con la figura ECM contra paso de integración de los cuatro métodos**; excluye introducción, animación u otra información de ese sistema [TP04, p. 2].

Para el sistema 2 deben cubrirse energía y elección del paso, rendimiento comparado, posición de obstáculos, rapidez y densidad. El mapa bidimensional es opcional. La declaración de IA va en una diapositiva extra al finalizar [TP04, pp. 3–4]. La guía limita fundamentos a tres diapositivas y conclusiones a una, pero no fija cantidad para resultados [GPRES, pp. 2–3]. No corresponde trasladar esos límites a resultados.

El borrador inspeccionado tiene 29 páginas: resultados D11–D26, **16 diapositivas de contenido**, incluida la del oscilador y la del mapa opcional. D10 es separadora y no está incluida en esas 16. D28 es la única diapositiva de conclusiones; D29, la declaración de IA. Conservar 16 es una decisión posible, no una exigencia de la cátedra. Quitar únicamente el mapa dejaría 15; resolver la trazabilidad de densidad puede justificar ocupar ese espacio con el resultado obligatorio de 30 s.

## Fuentes y alcance de la revisión

- Consigna TP4 completa, cuatro páginas, incluidas figuras y fórmulas del original; guía de presentaciones completa [TP04] [GPRES].
- Devoluciones catalogadas G7: `material/catedra/practica/Correcciones_TP2.md` [COR02] y `material/catedra/practica/correciones_tp3.txt` [COR03].
- Devolución adicional `entregas/correcciones_tp2.txt`: coincide en lo principal con COR02 y agrega nota «6 + 1», advertencia sobre redacción atribuida a IA y límite orientativo de unas diez páginas para aquel informe. Es un archivo aportado, sin ID catalogado; no reemplaza COR02 ni establece longitud de diapositivas para TP4.
- Presentaciones finales disponibles del G7: TP2, 24 páginas; TP3, 26 páginas. Se contrastaron sus páginas con las observaciones docentes y se inspeccionaron visualmente completas.
- Informe TP2 `informe/SdS_TP2_2026Q2G07CS_Informe.pdf`, 20 páginas: lectura completa de texto y contraste de ubicación/contenido de figuras. No se afirma revisión visual completa de ese informe ni se presupone que sea idéntico a todas las otras versiones disponibles.
- Archivos adicionales `entregas/TP3 - Correcciones.docx` y `entregas/TP3 - Presentación.pptx`: **son una referencia del G10**, no del G7. El DOCX dice G10, nota 9; la portada del PPTX identifica Grupo 10 y 2025 2C. Sus recomendaciones se aprovechan como referencia comparativa, no como errores o calificación del grupo actual. Ambos carecen de ID catalogado.
- TP4: PDF de nombre oficial de 29 páginas, fuente TeX, guion, revisión previa, figuras y su generador, registros y tablas de resultados, partes relevantes del motor y postproceso. Se verificó que el PPTX contiene cinco MP4 y referencias de video en D12, D15, D17, D20 y D23. No se abrió PowerPoint ni se verificó reproducción en el equipo de exposición.

Las conclusiones sobre cumplimiento son de esta auditoría, no una aprobación docente. No se repitieron simulaciones ni una auditoría numérica integral del motor.

## Diagnóstico y prioridades

### 1. Corregir la evidencia presentada para 2.4.a: prioridad alta

La consigna pide **tomar los outputs de 2.1.b**, que corresponden a 30 s [TP04, pp. 3–4]. Se conservaron y analizaron esos outputs, pero las figuras de D24–D25 muestran el complemento refinado, con paso cuatro veces menor, horizontes de hasta 300/600 s y N=50 adicional. D24 lo llama «seguimiento complementario refinado», pero D25 no deja visible el origen ni exhibe el resultado obligatorio original. El guion lo explica; el PDF por sí solo deja incompleta esa trazabilidad.

No es válido presentar los nuevos tiempos como si fueran los del benchmark ni como continuación exacta de aquellas trayectorias. El propio registro explica que se repitió desde el mismo estado inicial con otro paso y cambiaron trayectorias y tiempos. Ejemplo: para N=20, t90 es 21,1±4,2 s en el benchmark y 23,7±4,2 s en el complemento. Esta diferencia tampoco es, por sí sola, una prueba de convergencia o sesgo numérico.

Resultados originales verificados en `experiments/results/density-baseline-summary.csv`:

| N | No alcanzan t90 en 30 s | No alcanzan t100 en 30 s | Media de Fu(30 s) |
|---:|---:|---:|---:|
| 20 | 0/10 | 7/10 | 0,950 |
| 100 | 1/10 | 10/10 | 0,929 |
| 200 | 10/10 | 10/10 | 0,8435 |
| 400 | 10/10 | 10/10 | 0,5413 |
| 650 | 10/10 | 10/10 | 0,02369 |

Solo N=20 tiene media completa de t90. No hay media completa de t100 para ninguno de estos grupos. Mostrar medias donde son observables y cotas donde no lo son; no descartar silenciosamente las corridas incompletas ni reemplazar un tiempo desconocido por 30 s para llamarlo media completa.

**Acción recomendada:** dedicar una figura visible a los outputs originales de 30 s y presentar después las extensiones como estudio complementario. Para conservar la cantidad actual se puede sustituir el mapa opcional D26 por la comparación extendida y reservar D25 para el resultado original. Ajustar D23–D24 para que su contexto y población correspondan al conjunto que introducen. N=50 pertenece al complemento exploratorio, no al benchmark. No es necesario agregar gráficos accesorios para demostrar el punto.

### 2. Completar la discusión de escalamiento, no solo de quién gana: prioridad alta

D16 muestra correctamente medias y desvíos de diez realizaciones y ambos motores en la misma computadora. El resultado visible y el guion se concentran en el cruce entre N=200 y 400. El punto 2.1.b pide también discutir **cómo escala el costo con N** [TP04, p. 3].

Derivación descriptiva de `performance-summary.csv`: al pasar N=100→200→400, el tiempo TP4 se multiplica por aproximadamente 2,42 y 2,62; el TP3, por 9,93 y 17,38. Esto permite explicar que, en ese rango y protocolo, crece más rápidamente el costo de eventos. No demuestra una ley exponencial, un exponente asintótico ni una comparación universal entre métodos. Es justamente el tipo de afirmación no justificada señalado en COR03, D22.

**Acción recomendada:** incluir una comparación breve de esos incrementos o explicarla oralmente apoyándose en los puntos visibles. Identificar que TP3 fue recalculado; no mezclar los tiempos históricos con estos tiempos. Mantener que el cronometraje excluye inicialización y escritura en ambos casos. El protocolo compara los sistemas pedidos por la consigna, con geometrías e implementaciones diferentes; no aísla únicamente el integrador. El paso de TP4 es 5×10⁻⁵ s para esta comparación: no atribuir esos tiempos al paso refinado de los otros estudios.

### 3. Mejorar la evidencia de estacionariedad y ajuste: prioridad alta

D21 muestra distribuciones a 0,1; 0,5; 1 y 60 s, y representa t=0 con una línea vertical en v=1 m/s. Eso permite ver redistribución inicial, pero no comparar visualmente varias distribuciones tardías. Los números de estabilidad citados corresponden a ventanas que no están representadas en esa figura. «Distancia total» no identifica suficientemente la distancia de variación total ni su definición. La ventana [10,60) es un resultado de un criterio local, no un parámetro físico ni el tiempo exacto en que se alcanza el estacionario [COR02] [TP04, pp. 3–4].

**Acción recomendada:** mantener pocos instantes iniciales y usar el espacio para comparar ventanas tardías normalizadas; identificar el criterio de estabilidad y qué poblaciones compara. No hace falta una diapositiva de teoría estadística. No afirmar haber medido un tiempo de relajación frente a N o x0: ese estudio no se realizó. La devolución del G10 también advierte específicamente sobre concluir tiempos de estacionario sin mostrarlos.

D22 presenta correctamente la función Maxwell–Boltzmann 2D y la suma de cuadrados, con kBT como único parámetro. El registro técnico sí documenta grilla logarítmica y sección áurea, pero la figura del mínimo de E(theta) de las figuras de desarrollo no está en la lámina. **Recomendación de esta auditoría:** hacer visible cómo se obtiene el mínimo, mediante una representación pequeña o indicación clara del procedimiento y mínimo. La consigna remite al método de T00 y la guía pide mostrar cómo se halló el mejor ajuste; no hay una regla literal que obligue a una diapositiva adicional separada [TP04, p. 4] [T00, pp. 79–80] [GPRES, p. 2]. Reducir texto de D22 antes de añadir otro panel.

### 4. Explicitar la comparación energética, sin equiparar magnitudes distintas

Los números visibles de D22 coinciden con el resumen local: theta ajustado = 0,0123986 J; referencia inicial = 0,0125 J; cinética media por partícula = 0,0123234 J; potencial medio por partícula = 0,0001765 J. El ajuste queda aproximadamente 0,81 % por debajo de la referencia inicial. La energía cinética queda aproximadamente 1,41 % por debajo, con esa reducción compensada por el potencial de contacto.

**Acción recomendada:** explicar esa comparación al exponer, en vez de limitarse a leer los cuatro valores. La energía potencial explica la reducción cinética; no explica por sí sola la diferencia entre mínimos cuadrados y segundo momento. No concluir igualdad exacta ni validación formal de Maxwell–Boltzmann: no se hizo una prueba de bondad de ajuste.

Los histogramas promedian 500 cuadros por corrida y luego diez densidades. Los cuadros sucesivos no son realizaciones independientes. Las barras son desvíos entre diez realizaciones, no incertidumbre del parámetro ajustado. El valor 0,01240±0,00008 J disponible corresponde a media y desvío de diez ajustes individuales: **no** debe adjuntarse como error formal del ajuste al histograma medio.

### 5. Completar enlaces y comprobar exposición: bloqueo concreto de entrega

D12, D15, D17, D20 y D23 dicen «YouTube/Vimeo: enlace pendiente de publicación». Por lo tanto, el PDF aún no cumple el requisito de fotograma con enlace explícito real [TP04, p. 1] [GPRES, pp. 2–3]. La presencia estructural de cinco videos en el PPTX no verifica reproducción, autoplay, compatibilidad ni duración efectiva. Completar URL, regenerar y probar en el equipo real.

El guion suma exactamente 13:00, sin margen y sin ensayo medido. Las 16 láminas de resultados tienen asignados 470 s (7:50), unas 29 s por lámina en promedio. D22 dispone de 50 s para fórmula, promediado, minimización y balance energético: es la mayor concentración de explicación. Ensayar con transiciones, videos y cambios de expositor; apuntar a terminar antes del límite. No asumir que «diapositiva extra» de IA autoriza automáticamente exceder los 13 minutos.

## Errores anteriores: cuáles se repiten y cuáles se corrigieron

| Antecedente comprobado | Estado en TP4 | Acción |
|---|---|---|
| TP2 D7/D9 y código: observables en el loop del motor [COR02]. | Corregido en la separación observada: el motor guarda estado y primer contacto; energía, histogramas y tiempos agregados se calculan fuera. | Mantener esta separación. El primer contacto es estado histórico necesario para reconstruir cruces entre cuadros, no una media calculada online. |
| TP2 D8: UML ilegible [COR02]. | No se repite el UML enorme; D5 usa un diagrama mucho más simple. | Mantenerlo simple; añadir claramente el retorno del bucle temporal, ausente en el diagrama actual. |
| TP2 D11: esquema sin etiquetas y confusión de parámetros [COR02]. | D7 sí etiqueta R, r y x0; D9 separa configuración numérica y seguimiento. | Separar visualmente la flecha de velocidad y la cota x0 en el centro del dibujo; aclarar ángulos iniciales uniformes en [0,2π). |
| TP2 D12 y TP3 D14: promediado insuficientemente identificado [COR02] [COR03]. | D8 distingue tiempos por realización y promedio entre corridas; D18 y D21–D22 identifican poblaciones. | Conservarlo. Precisar también las dos condiciones iniciales del ensayo energético y el promedio de la curva mostrada en D13. |
| TP2 D14: leyenda ocupa espacio de animación [COR02]. | No hay ruedas de color; videos físicos grandes y leyendas laterales. | Mantener. |
| TP3 D3: sistema particular ubicado en fundamentos [COR03]. | D3 desarrolla Newton y contacto general; geometría y números aparecen en D7. | Mantener esa división. No volver a introducir toda la configuración en fundamentos. |
| TP3 D16: exceso de plots accesorios [COR03]. | D16 tiene solo la comparación requerida. | Conservar foco, completando discusión de crecimiento sin volver a tres plots. |
| TP3 D17/D18/D20–D21: gráfico temporal animado, heatmap temporal y orden invertido [COR03]. | Corregido: energía 12→13→14; posición 17→18→19; rapidez 20→21→22; densidad 23→24→25. | Mantener evolución estática. El mapa D26 sí usa dos entradas independientes, por lo que su tipo es pertinente aunque sea opcional. |
| TP3 D21: parametrización opaca y semilla aislada [COR03]. | Se ven magnitudes físicas, sin semillas en las láminas. | Completar extremos/rango de x0, h y horizontes donde resulte necesario, sin llenar cada lámina con constantes repetidas. |
| TP3 D22: resultado ajustado encima de curvas y cifras excesivas [COR03]. | Los valores están fuera del gráfico y no tapan curvas. | Mantener. D19/D26 tienen posiciones exactas de grilla con cuatro decimales: son entradas prescritas, no cuatro decimales de precisión del óptimo. Decirlo explícitamente. |
| TP2 D16/D24: cociente interpretativo poco claro [COR02]. | No se repite el reclamo de «veces más ruido». | Los factores de costo propuestos arriba son cocientes directos de tiempos de dos puntos, no una tolerancia física ni ley universal. |
| Informe TP2: 20 páginas; figura temporal fuera de resultados; polarización en sección de conectividad; tabla y gráfico redundantes. | No corresponde trasladar su formato narrativo al TP4. D21/D22 y D28 aún concentran demasiado texto para leer en exposición. | Recortar frases y duplicación de valores; conservar evidencia y explicación oral. La longitud del informe previo no fija cantidad de resultados del TP4. |
| Referencia G10 D25: conclusiones sin estudio mostrado, repetidas o con analogía a gas sin comparación. | D28 no afirma difusión gaseosa ni tiempo exacto de relajación. | Mantener conclusión limitada a lo observado y hablar de mínimos muestrales, sin causalidad no medida. |

## Revisión de principio a fin del borrador TP4

| D | Evaluación y ajuste recomendado |
|---:|---|
| 1 | Portada identificada como borrador. Confirmar autores/comisión; retirar esa indicación solo tras la revisión real del grupo. |
| 2 | Separadora válida; la guía pide separar secciones. No eliminarla solo para bajar artificialmente el conteo. |
| 3 | Fundamentos generales bien ubicados. Modelo repulsivo y dirección de la normal coherentes con la consigna. Definir fuerza nula sin contacto al exponer. |
| 4 | Separadora válida. |
| 5 | Mucho más legible que el UML del TP2. El flujo dibujado parece lineal: hacer visible la repetición hasta tf y la salida cada n pasos. La imagen de pared está formulada, pero un esquema pequeño de contacto ayudaría si sustituye texto. |
| 6 | Separadora válida. |
| 7 | Geometría y parámetros correctos. Las etiquetas vi y x0 quedan muy próximas. Explicitar obstáculos fijos y ángulos en [0,2π); no confundir r de partícula con radio de interacción. |
| 8 | Buena definición de Fu, cruces y promediado. Añadir que la media completa requiere observar todos los tiempos; censura y cotas se distinguen en resultados. |
| 9 | Buena tabla de protocolos, sin llamar parámetros físicos a duraciones o repeticiones. Definir «2 iniciales» como dos condiciones iniciales. h y ventana estacionaria no son parámetros físicos del sistema. |
| 10 | Separadora válida. |
| 11 | Cumple excepción de una sola figura del oscilador con ejes logarítmicos y cuatro métodos. Explicar oralmente cuál obtuvo menor ECM. La superposición de curvas exige señalarlas; no agregar otra diapositiva del sistema 1. |
| 12 | Animación de energía con N=300 sin obstáculos pertinente a 2.1.a. La crítica del TP3 a animar mesa vacía no es una prohibición general: aquí esa configuración es el estudio requerido. Falta URL. |
| 13 | Incluye energía total cinética más resortes y máximo relativo muestreado. Precisar si se muestra una condición inicial o promedio; el protocolo menciona dos. Asegurar que los contactos de pares se cuentan una sola vez. |
| 14 | Criterio 0,1 % correctamente marcado como local. Separar con claridad elección de h para benchmark y refinamiento para estudios largos. Un máximo muestreado no garantiza el máximo entre cuadros. |
| 15 | Contexto físico antes del costo, adecuado. Falta URL. No confundir tiempo de video con tiempo de ejecución. |
| 16 | Datos y barras coinciden con tabla; falta reforzar discusión de escalamiento y dejar claro que TP3 fue recalculado. h del benchmark debe ser inequívoco. |
| 17 | Tres posiciones representativas, antes del análisis. Falta URL. El número de paneles no obliga a incluir todas las posiciones del barrido. |
| 18 | Evolución estática y promedio de cinco fracciones bien explicados. No obtener t90 de la curva media. |
| 19 | Medias y desvíos de cinco tiempos, comparación N=100/N=20, mínimos muestrales bien identificados. Agregar que todas las corridas alcanzaron t90 antes de 100 s. Discutir mezcla por colisiones como interpretación, sin afirmar frecuencia medida. |
| 20 | Animación física adecuada para rapidez sin obstáculos. Falta URL. |
| 21 | Normalización y población claras. Reemplazar parte del detalle textual por evidencia comparativa de ventanas tardías; definir la métrica citada. No presentar t=10 s como relajación física exacta. |
| 22 | Fórmula y función objetivo correctas; alta densidad de información. Mostrar mejor cómo se localizó el mínimo y discutir el balance de energía. Diferenciar variabilidad entre realizaciones e incertidumbre del ajuste. |
| 23 | N=50 corresponde al complemento, no a 2.1.b. Ajustar contexto si introduce la reutilización original. Falta URL. |
| 24 | Identifica complemento refinado, censura y media de Fu. Debe quedar claro que se repitió desde estados iniciales, no se continuaron bit a bit los outputs de 30 s. |
| 25 | Medias, desvíos y cotas del complemento están bien distinguidos, pero falta el resultado original exigido de 30 s. Es el principal problema de cobertura del borrador. |
| 26 | Mapa pertinente para dos parámetros y rotulado como mínimo muestral. Es opcional; primera candidata a ceder espacio a la trazabilidad obligatoria de densidad. No interpretar desplazamientos entre mínimos vecinos como diferencias significativas probadas. |
| 27 | Separadora válida. |
| 28 | Resultados ya mostrados, sin introducir causas nuevas. Condensar las cuatro frases. La segunda conclusión debe conservar «menor media observada en la grilla»; evitar convertirla en una ley del óptimo. No añadir otra mención del oscilador que contradiga su restricción específica. |
| 29 | Declaración extra presente y fiel al tipo de asistencia registrado. Debe reflejar el proceso final real: la consigna no permite producción independiente de presentaciones por agentes. La elaboración, revisión y defensa del contenido corresponden al grupo. |

## Qué no está demostrado y no debe aparecer como conclusión

1. Que exista una densidad óptima global única. N=50 minimiza la media muestral de t90 en el complemento; N=20 minimiza la de t100. Este último está en el borde inferior de la grilla, y 41±14 s frente a 42,5±8,1 s no establece por sí solo diferencia poblacional.
2. Que N=650 convierta lentamente exclusivamente por densidad, frecuencia de choques o inmovilidad. Cambia también la familia de inicialización y queda orden residual; la frecuencia no se midió. Sus tiempos están censurados, no estimados en 300 s.
3. Que la posición óptima siga una ley monótona con N. Los mínimos de cuatro filas no la muestran y hay vecinos próximos dentro de la dispersión.
4. Que la concordancia visual con Maxwell–Boltzmann sea una prueba formal o que kBT ajustado sea exactamente la cinética media medida.
5. Que el cruce de costos observado sea un N exacto o una comparación universal entre algoritmos.
6. Que la ventana estacionaria elegida determine un tiempo exacto de relajación.

## Cierre verificable antes de entregar

- Mostrar el resultado de las salidas originales de 30 s y diferenciar el complemento refinado.
- Completar discusión de crecimiento del costo y explicación del ajuste y balance energético.
- Mantener definiciones de promedios y barras, sin medias ficticias por censura.
- Revisar D21–D22 y D28 para reducir lectura de texto y mejorar evidencia visible.
- Completar cinco enlaces públicos reales; regenerar PDF/PPTX y comprobarlos.
- Ensayar dentro de 13 minutos y verificar reproducción en el equipo de exposición.
- Revisar todo el contenido entre los integrantes; conservar una declaración de IA fiel.
- Preparar y verificar por separado el ZIP final del motor menor de 100 KB, sin postproceso, datos, figuras ni documentación [TP04, p. 1]. No se encontró ese ZIP de TP4 en el listado de archivos de esta revisión; no se da por listo.

La presentación tiene mejoras reales respecto de TP2/TP3, pero la revisión previa `revision-guia.md` no basta como certificado de cumplimiento: persisten los pendientes anteriores. No se modificaron el mazo, los originales oficiales ni las entregas históricas.
