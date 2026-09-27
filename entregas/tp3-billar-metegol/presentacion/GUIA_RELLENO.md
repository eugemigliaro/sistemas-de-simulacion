# Guia de relleno de la presentacion del TP3

La fuente unica de la presentacion es `SdS_TP3_2026Q2G07CS_Presentacion.tex`.
Conserva el mismo preambulo y la misma estetica Beamer de la presentacion final
del TP2: formato 16:9, tema Warsaw, `miniframes`, colores, bloques y numeracion.

## Estructura (indicaciones de la catedra, 2026-09-26)

- Introduccion: dinamica molecular dirigida por eventos en general, ecuacion del
  tiempo de choque entre dos particulas [T03, p. 14] y operador de choque.
- Implementacion: arquitectura, estructuras, algoritmo y diagrama UML.
- Simulaciones: sistema particular, parametros fijos y variables, observables.
- Resultados:
  1. tiempo de ejecucion hasta la saturacion;
  2. animacion de la mesa vacia con `Fu(t)`;
  3. mapa `Fu(t)` segun el radio del disco central;
  4. resumen de la busqueda;
  5. animacion de la elegida con `Fu(t)`;
  6. `t90` segun la profundidad de la sala;
  7. DCM en funcion del tiempo y `E(c)`;
  8. `D` en funcion de `t90`.

## Estado

Completa. Si cambia algo: recompilar, ejecutar `make package` y
`scripts/build_pptx.py`.

Videos publicados (diapositivas 17 y 20): mesa vacia
<https://youtu.be/D2RamY4L4Lk>, elegida <https://youtu.be/vTp_REslNT8>.

El PPTX de la exposicion lo arma `scripts/build_pptx.py`: cada diapositiva es
la pagina del PDF y los MP4 van embebidos sobre sus fotogramas.

## Compilacion

Desde este directorio:

```bash
tectonic SdS_TP3_2026Q2G07CS_Presentacion.tex
```

Las figuras se regeneran con `make assets` desde la raiz de la entrega.
