# Correcciones del informe del TP2

Última actualización: 2026-08-31.

Este archivo registra las observaciones de revisión del informe, su estado y los
cambios acordados. Una corrección se considera cerrada solo después de revisar el
PDF recompilado cuando afecte la composición visual.

## Pendientes

- [ ] Revisar el bloque asociado a la ecuación 7, incluida la conversión entre la
  escala de ruido normalizada y la del trabajo original. Se decidió postergar
  esta corrección.
- [ ] Revisar el fundamento teórico y la interpretación de la componente gigante,
  incluida la forma de calcular `S` y las afirmaciones sobre conectividad y
  percolación. Se decidió postergar esta corrección.
- [ ] Revisar visualmente todas las páginas del PDF recompilado, en particular la
  página 8 y cualquier página modificada por las barreras de flotantes.

## Corregidas

### Determinación del estado estacionario

- **Antes:** se presentaba un procedimiento formal extenso basado en bloques,
  promedios de ensamble y bandas de dos desviaciones estándar.
- **Después:** se indica que se inspeccionaron las diez realizaciones de cada caso
  y que se adoptó de forma conservadora `t_0 = 4000` para todas las corridas.

### Tiempo de relajación en las conclusiones

- **Antes:** las conclusiones repetían valores y comparaciones de tiempos de
  relajación que ya aparecían en Resultados.
- **Después:** el análisis detallado quedó únicamente en Resultados y se eliminó
  su repetición del cierre.

### Ubicación de figuras

- **Antes:** las figuras 2, 3--4, 9 y 12 podían aparecer después del comienzo de
  la subsección siguiente.
- **Después:** se agregaron barreras antes de 5.2, 5.3, 5.5 y 5.6 para mantener
  cada figura dentro de la subsección a la que pertenece.

### Relación entre las figuras 10 y 12

- **Antes:** el texto pasaba al caso de densidades bajas sin explicar con claridad
  qué limitación mostraba la figura 10.
- **Después:** se explicita que, en las densidades pedidas, `S` varía poco y los
  puntos se concentran; esto justifica repetir el análisis en densidades bajas.

### Ejes de la figura 12

- **Antes:** la componente gigante estaba en el eje horizontal y la polarización
  en el vertical.
- **Después:** la polarización quedó en el eje horizontal y la componente gigante
  en el vertical. También se actualizaron el texto, el pie, el generador y la
  prueba visual.

### Desborde de la página 5

- **Antes:** las mallas de valores de ruido se escribían en línea y excedían el
  margen derecho.
- **Después:** cada conjunto se presenta como una expresión matemática dividida
  explícitamente en dos líneas.

### Subsección 3.4, "Validación"

- **Antes:** detallaba toda la batería de pruebas, configuraciones inválidas,
  formatos, interfaz de línea de comandos y uso de sanitizers.
- **Después:** conserva en un único párrafo las dos comprobaciones relevantes para
  el informe: coincidencia exacta entre CIM y fuerza bruta, y el control físico
  `v_a = 1` cuando `eta = 0`.

### Barras de error de la figura 5

- [x] Se verificó que el gráfico usa la desviación estándar muestral entre las diez
  medias temporales independientes. Las 66 filas tienen un desvío calculado;
  algunas barras no se distinguen porque son muy pequeñas. No fue necesario
  modificar la figura.

### Piso de polarización y distribución de Rayleigh

- [x] Se redujo el desarrollo a una mención de la distribución de Rayleigh y a la
  estimación no numerada `sqrt(pi)/(2 sqrt(N))`, usada únicamente para explicar
  que la polarización residual en `eta = 1` es un efecto de tamaño finito.

## Pendientes de verificación visual

- [ ] Confirmar en el PDF recompilado que las figuras 2, 3--4, 9 y 12 permanecen
  dentro de sus subsecciones y que la paginación resultante es legible.
- [ ] Confirmar que las listas de valores de ruido ya no exceden el margen de la
  página 5.
- [ ] Confirmar que la figura 12 recompilada muestra `v_a` en el eje horizontal y
  `S` en el vertical.
