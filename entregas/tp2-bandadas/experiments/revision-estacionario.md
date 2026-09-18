# Revisión del régimen estacionario en densidad baja

Fecha: 2026-09-04.

## Pregunta

Se revisó si las barras grandes de la Figura 12 en `eta = 0` se debían a haber
adoptado un único inicio estacionario, `t0 = 4000`, a partir de evidencia que no
cubría todas las densidades y ruidos.

## Evidencia disponible antes de la revisión

El generador del informe aplica `t0 = 4000` a todas las corridas. Los archivos de
bloques conservados sólo cubren tres semillas de Vicsek con `rho = 4, eta = 0.5`
y tres semillas del votante con `rho = 0.32, eta = 0.25`. Por lo tanto, no
justifican por sí solos el descarte de las corridas de baja densidad con ruido
nulo. El protocolo del TP indica que el inicio debe revisarse por combinación de
modelo, densidad y ruido, y que una corrida que todavía deriva al terminar debe
extenderse.

## Experimentos de diagnóstico

Se recompiló el motor C++20 desde las fuentes actuales y se hicieron tres
comprobaciones:

1. Se extendieron hasta `T = 100000` las diez semillas usadas en el informe para
   ambos modelos, las densidades `0.11`, `0.16` y `0.32`, y `eta = 0`.
2. Se midió el primer tiempo a partir del cual `va >= 0.999` se mantiene hasta el
   final en 100 semillas por modelo y densidad. Las corridas se llevaron primero
   hasta `T = 30000`; las tres que no habían convergido se extendieron hasta
   `T = 300000`.
3. Para los 48 casos de ruido positivo en densidad baja se ejecutaron diez
   semillas hasta `T = 30000` y se compararon bloques de 1000 pasos. Los siete
   casos cuyas medias eran más sensibles a la longitud de la ventana se
   extendieron hasta `T = 100000`.

Los 600 tiempos de consenso del segundo punto se conservan en
`results/diagnostico-estacionario-eta0.csv`. El umbral `0.999` se usó para medir
tiempos de llegada; los promedios finales se calcularon directamente con los
observables, sin reemplazarlos por el umbral.

## Resultado para las diez semillas del informe

Vicsek con `rho = 0.32`, semilla 10, alcanza `va >= 0.999` de forma permanente
recién en `t = 15624`. Entre `t = 4000` y `t = 10000` permanece alrededor de
`va = 0.338`. Las otras nueve semillas ya están alineadas. Esto reproduce
`va = 0.933756 +/- 0.209462` del resumen publicado y demuestra que su barra
grande mezcla nueve estados estacionarios con una corrida todavía transitoria.
Además, `T = 10000` termina antes de que esa corrida llegue al estado absorbente.

Al promediar entre `t = 20000` y `t = 30000`, las diez semillas de Vicsek dan
`va = 1` y `S = 1` en las tres densidades, sin dispersión apreciable. La barra
grande de Vicsek en ruido nulo desaparece.

En el votante, `va = 1` después del consenso, pero `S` puede quedar por debajo de
uno porque grupos que ya comparten dirección pueden permanecer espacialmente
separados. Entre `t = 20000` y `t = 30000` se obtiene:

| Densidad | `va` | `S` |
|---:|---:|---:|
| 0.11 | `1.000000 +/- 0.000000` | `0.927273 +/- 0.153323` |
| 0.16 | `1.000000 +/- 0.000000` | `0.981250 +/- 0.059293` |
| 0.32 | `1.000000 +/- 0.000000` | `0.978125 +/- 0.051137` |

Esa dispersión vertical de `S` permanece sin cambios hasta `T = 100000`; es
variabilidad entre estados finales y no un transitorio.

## Cola de los tiempos de consenso

En las 600 corridas de calibración, 24 superaron `t = 4000`, diez superaron
`t = 10000` y tres superaron `t = 30000`. El percentil 99 fue `t = 14592`, pero
dos corridas raras de Vicsek convergieron en `t = 97926` y `t = 101837`. Por eso
ningún tiempo global corto garantiza el consenso para semillas nuevas. El
descarte debe validarse sobre las semillas efectivamente usadas en producción.

## Elección recomendada

Para corregir el informe actual con sus mismas diez semillas y el menor cambio
posible:

- conservar `t0 = 4000` y `T = 10000` para los resultados ya producidos con
  `eta > 0` y para las densidades principales;
- repetir solamente los 60 casos de baja densidad con `eta = 0` hasta
  `T = 30000`;
- resumir esos 60 casos con `t0 = 20000`.

El margen entre el último consenso observado en esas semillas (`t = 15624`) y
`t0 = 20000` es de 4376 pasos. Como `eta = 0` termina en un estado absorbente,
los 10000 pasos restantes no agregan sesgo ni requieren una ventana más larga.

Para semillas distintas se debe repetir la calibración. Si se quisiera cubrir
las 100 semillas ensayadas aquí mediante un único descarte, harían falta al
menos `t0 = 110000` y `T = 120000`, una opción mucho más costosa que no es
necesaria para corregir las diez realizaciones del informe.

## Precisión con ruido positivo

No apareció una deriva sistemática general después de `t = 4000` en los casos
con `eta > 0`. Sí aparecieron fluctuaciones lentas de `S`: al extender los siete
casos más sensibles hasta `T = 100000`, las medias acumuladas entre `T = 75000`
y `T = 100000` cambiaron menos de `0.01`. Esto indica que `T = 10000` limita la
precisión de algunos puntos, pero es un problema distinto del transitorio que
produce la barra anómala en `eta = 0`.

Si se desea mejorar toda la curva de baja densidad en una revisión posterior,
se recomienda `t0 = 4000, T = 100000` para `eta > 0`. Esa mejora requiere
recalcular todas las curvas de baja densidad y no forma parte de la corrección
mínima.

## Cambios mínimos aplicados en el TP

1. Se agregó una configuración de barrido exclusiva para baja densidad y
   `eta = 0`, con las mismas diez semillas y `steps = 30000`.
2. Sus CSV crudos se conservan en un directorio separado para no contradecir el
   `manifest.json` del barrido original.
3. `build_report_assets.sh` usa los archivos extendidos en lugar de
   los archivos originales de `eta = 0`, y una tabla de inicios estacionarios
   con `t0 = 20000` para esos seis parámetros y `t0 = 4000` para los restantes.
4. Se regeneraron `summary-baja-densidad.csv` y las tres figuras que dependen de él:
   `s-vs-eta-baja-densidad.png`, `va-vs-eta-baja-densidad.png` y
   `va-vs-s-baja-densidad.png`.
5. Se actualizaron en el informe la tabla de tiempos y la subsección de determinación
   del estacionario. La explicación debe indicar que el caso de ruido nulo en
   baja densidad usa una corrida más larga por su tiempo de consenso con cola
   larga.
6. Se regeneraron las figuras equivalentes de la presentación para que informe
   y exposición usen los mismos resultados.

No es necesario modificar el motor C++, las definiciones de `va` o `S`, los
resultados de las densidades `2`, `4` y `8`, las figuras del CIM ni el código
entregado.
