# Guia de relleno de la presentacion del TP3

La fuente unica de la presentacion es `SdS_TP3_2026Q2G07CS_Presentacion.tex`.
Conserva el mismo preambulo y la misma estetica Beamer de la presentacion final
del TP2: formato 16:9, tema Warsaw, `miniframes`, colores, bloques y numeracion.

## Campos pendientes

1. Diapositiva 16: insertar dos fotogramas y las URL explicitas de YouTube o
   Vimeo.
2. Diapositiva 17: insertar tiempo de ejecucion medio frente a `N`, con desvio
   estandar y al menos 10 realizaciones por punto.
3. Diapositiva 18: insertar dos evoluciones tipicas de `Fu(t)` y marcar
   `Fu = 0,9` y cada `t90`.
4. Diapositiva 19: insertar el barrido de configuraciones, la referencia de
   mesa vacia y los parametros de la configuracion elegida.
5. Diapositiva 20: insertar DCM, recta ajustada, `E(c)`, ventana de ajuste y
   valor de `D`.
6. Diapositiva 21: insertar la comparacion entre `D` y `<t90>` y escribir solo
   la relacion respaldada por los datos.
7. Diapositiva 23: completar tres conclusiones, cada una respaldada por una
   figura ya presentada.

Antes de entregar deben desaparecer todos los textos `REEMPLAZAR`, las
expresiones entre corchetes y el sufijo `Borrador` de los archivos.

## Compilacion

Desde este directorio:

```bash
tectonic SdS_TP3_2026Q2G07CS_Presentacion.tex
```

El PDF resultante es la fuente visual para generar el PPTX. De ese modo ambos
archivos mantienen exactamente la misma composicion.
