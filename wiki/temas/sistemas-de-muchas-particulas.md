# Sistemas de muchas partículas y materia activa

## Muchas partículas

Los problemas de uno y dos cuerpos pueden ser integrables, mientras que desde tres cuerpos aparecen sistemas que en general requieren integración numérica; para $N$ cuerpos se recurre a dinámica molecular y, cuando $N$ es muy grande, a descripciones estadísticas o cinéticas [T01, p. 2]. Ejemplos del curso incluyen sistemas gravitatorios, flujos granulares, peatones, bacterias, cardúmenes y bandadas [T01, p. 3] [T01, p. 4] [T01, p. 7] [T01, p. 8].

En los sistemas tratados inicialmente, las partículas interactúan de a pares y las interacciones dependen de la distancia. Las fuerzas de largo alcance pueden requerir considerar todos los pares; para corto alcance bastan las vecinas cercanas [T01, p. 18]. Esta distinción motiva las listas de vecinos y el [Cell Index Method](cell-index-method.md).

## Materia activa y emergencia

La materia activa está formada por unidades autopropulsadas que convierten energía almacenada o ambiental en movimiento sistemático. El aporte energético ocurre localmente, a escala de partícula o agente, y puede producir estructuras colectivas y transiciones orden-desorden lejos del equilibrio [T01, p. 6]. El comportamiento emergente aparece cuando muchos agentes simples con interacciones sencillas generan espontáneamente patrones cuya escala supera la de un agente individual [T01, p. 15].

La bibliografía externa amplía la definición: las interacciones entre partículas activas y con el medio pueden generar movimiento colectivo correlacionado, esfuerzos mecánicos y orden orientacional. También distingue sistemas “secos”, donde el sustrato impide conservar el momento, y suspensiones “húmedas”, donde importa el fluido circundante [B05, p. 1] [B05, p. 2].

## Dos familias de modelos

El modelo de fuerzas sociales para peatones combina términos granulares, sociales, de impulso propio y, según el caso, fluctuaciones. Las ecuaciones individuales quedan acopladas y se integran con métodos de dinámica molecular [T01, p. 9] [T01, p. 10]. En estos sistemas pueden surgir formación espontánea de carriles, bloqueo por fluctuaciones intensas (*freezing by heating*) y el efecto *faster is slower* en cuellos de botella [B01, p. 7] [B01, p. 8] [B01, p. 9].

El modelo de Reynolds representa cada “boid” como actor independiente con percepción local. La bandada no sigue un guion central: el patrón agregado emerge de tres reglas priorizadas —evitar colisiones, igualar velocidad y acercarse al centro local de la bandada— [B04, p. 1] [B04, p. 4]. Es un ejemplo directo de cómo reglas microscópicas locales producen organización macroscópica.

## Escalas de descripción

Las fuentes muestran una progresión útil:

- **microscópica:** posición, velocidad, orientación e interacción de cada agente;
- **mesoscópica:** vecindarios, densidades locales y estructuras colectivas;
- **macroscópica:** campos de densidad, polarización, flujo y tensiones.

La revisión de materia activa conecta modelos de partículas con teorías continuas hidrodinámicas, pero esa conexión requiere decidir qué variables lentas y leyes de conservación son pertinentes [B05, p. 1] [B05, p. 7].
