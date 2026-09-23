# Guia de relleno de la presentacion del TP3

La fuente unica de la presentacion es `SdS_TP3_2026Q2G07CS_Presentacion.tex`.
Conserva el mismo preambulo y la misma estetica Beamer de la presentacion final
del TP2: formato 16:9, tema Warsaw, `miniframes`, colores, bloques y numeracion.

## Estado de cierre

Las figuras, los valores experimentales y las conclusiones de las diapositivas
16 a 23 ya están completos. Solo falta publicar `videos/anim-vacia.mp4` y
`videos/anim-mejor.mp4` en YouTube o Vimeo y reemplazar los dos avisos de la
diapositiva 16 por sus URL explícitas [TP03, p. 1]. Después se debe recompilar
el PDF y ejecutar `make package`.

## Compilacion

Desde este directorio:

```bash
tectonic SdS_TP3_2026Q2G07CS_Presentacion.tex
```

El PDF resultante es la fuente visual para generar el PPTX. De ese modo ambos
archivos mantienen exactamente la misma composicion.
