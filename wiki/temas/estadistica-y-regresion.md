# Estadística y regresión

## De muestras a distribuciones

Para un histograma, la altura $N_i$ es el conteo del intervalo $i$. La distribución de probabilidad discreta normaliza por el total, $N_i/N$, mientras que una aproximación a la densidad también divide por el ancho del intervalo, $N_i/(Δx_i N)$. Una densidad puede superar uno localmente, pero su integral debe ser uno [T00, p. 68].

En una simulación estocástica se repiten corridas con semillas distintas. El material propone reportar el observable mediante la media y usar el desvío estándar como error asociado cuando corresponde el supuesto gaussiano, con notación $μ±σ$ [T00, p. 69]. Las cifras significativas del valor deben ser coherentes con las del error; por ejemplo, se prefiere $45.4±0.3\,\mathrm{cm}$ a una precisión aparente injustificada [T00, p. 70].

La interpretación exacta de las barras de error debe declararse. En el TP1 se pide explícitamente promedio y **desvío estándar** de los tiempos obtenidos en múltiples búsquedas [TP01, p. 1]. Para otros trabajos, la convención esperada debe verificarse en la consigna y, si no está definida, con la cátedra; la cuestión quedó anotada en [Dudas y conflictos](../dudas-y-conflictos.md).

## Ajuste de modelos

El ajuste debe partir de una relación teórica, no de una función arbitraria elegida solo porque sigue los puntos [T00, p. 75] [T00, p. 82]. Para datos $(x_i,y_i)$ y un modelo $f(x_i,c)$, el material define el error cuadrático:

$$
E(c)=Σ_i[y_i-f(x_i,c)]^2.
$$

El mejor coeficiente $c^*$ es el que minimiza $E(c)$ [T00, p. 79] [T00, p. 80]. Si se muestra un ajuste en una presentación, debe explicarse cómo se obtuvo; no se aceptan interpolaciones arbitrarias mediante polinomios o *splines* sin fundamento en el sistema [GPRES, p. 2].

## Secuencia para presentar resultados

La guía propone esta progresión para cada parámetro estudiado:

1. una animación o imagen representativa que dé contexto a la dinámica;
2. la evolución temporal de un observable para justificar el escalar que la resume;
3. la figura del parámetro de entrada frente al observable, con promedios y barras de error;
4. el ajuste teórico, cuando exista, con su procedimiento;
5. repetición del esquema para los demás parámetros [GPRES, p. 2].

Los puntos medidos deben distinguirse claramente. Las líneas rectas pueden usarse como guía visual, pero no deben ocultar cuáles son los datos. Cuando hay varios órdenes de magnitud se recomienda una escala logarítmica en el eje correspondiente [GPRES, p. 2].

## Aplicación al TP1

El estudio empírico del Cell Index Method varía primero el número de celdas $M$ para dos valores de $N$, repite la búsqueda varias veces y grafica tiempo medio con desvío estándar. Luego fija el $M$ óptimo y estudia el tiempo frente a $N$, comparando densidad libre con densidad fija [TP01, p. 1] [TP01, p. 2]. Esta práctica conecta complejidad algorítmica, protocolo de medición y comunicación de incertidumbre.
