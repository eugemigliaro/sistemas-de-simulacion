# Diseño de la presentación del TP2

## Objetivo

La presentación debe permitir que docentes y estudiantes comprendan, en una exposición de 10 a 15 minutos, cómo las reglas de Vicsek y del votante producen transiciones de orden diferentes y cómo la conectividad espacial modifica esa lectura. Será autocontenida, pero no reproducirá párrafos del informe.

La fuente académica principal será `entregas/tp2-bandadas/informe/informe.pdf`. La estructura y las decisiones de maquetación seguirán `material/catedra/practica/GuiaPresentaciones.pdf`.

## Estructura narrativa

La versión final tendrá 24 diapositivas:

1. Portada.
2. Separador: Introducción / Sistema real / Fundamentos.
3. Sistema real: bandadas, interacción local y pregunta del trabajo.
4. Dinámica común: posición, orientación y ruido normalizado.
5. Reglas de interacción: promedio de Vicsek frente a copia del votante.
6. Separador: Implementación.
7. Modelo computacional: estado, vecindarios, observables y salida del motor.
8. Paso sincrónico: CIM, actualización y validaciones.
9. Separador: Simulaciones.
10. Caja periódica y parámetros.
11. Observables y promediado estacionario.
12. Separador: Resultados.
13. Fotogramas representativos de Vicsek y del votante.
14. Evolución temporal comparada de la polarización.
15. Polarización media frente al ruido, con barras de error.
16. Evolución temporal al variar la densidad.
17. Componente gigante frente al ruido para las densidades pedidas.
18. Fotograma representativo en baja densidad.
19. Evolución temporal en baja densidad.
20. Componente gigante frente al ruido en baja densidad.
21. Polarización frente a componente gigante.
22. Desempeño del CIM.
23. Separador: Conclusiones.
24. Conclusiones.

No habrá diapositiva de bibliografía ni cierre genérico de agradecimiento.

## Sistema visual

- Se conservará Beamer con el tema Warsaw y navegación por miniframes.
- Los separadores mostrarán únicamente el nombre de la sección, sin número ni la palabra “Sección”.
- Los títulos serán rótulos breves, preferentemente de dos a cinco palabras.
- Cada diapositiva tendrá una única función narrativa y, como regla general, no más de tres ideas visibles.
- Las figuras ocuparán la mayor parte de la superficie; los parámetros se ubicarán en una columna lateral.
- No se usarán captions de informe ni títulos incrustados en los gráficos.
- Las citas, cuando sean necesarias, serán mínimas: “Vicsek, PRL, 1995” y “Loscar et al., PRE, 2021”.
- Se mantendrán números de diapositiva visibles.

## Figuras y datos

- Los fotogramas existentes se reutilizarán sin alterar sus resultados.
- Se generarán variantes específicas para presentación de los gráficos cuantitativos, usando los mismos CSV y cálculos del informe, con tipografía mayor, ejes en palabras, unidades cuando correspondan, leyendas simplificadas y sin título interno.
- Los puntos medidos permanecerán visibles y las barras representarán la desviación estándar entre diez realizaciones.
- Se conservará el criterio de promedio por semilla en el intervalo `[4000, 10000]` y posterior media entre realizaciones.
- Las URL de animaciones permanecerán como campos pendientes si no existe una URL pública comprobable; no se inventarán enlaces.

## Coherencia académica

La presentación conservará exactamente:

- dinámica con `L = 10`, `r_c = 1`, `v = 0,03`, `Delta t = 1`;
- CIM con `M = 9`;
- duración `T = 10000` e inicio estacionario `t0 = 4000`;
- diez realizaciones por punto;
- observables de polarización `v_a` y fracción de componente gigante `S`;
- densidades principales `rho = 2, 4, 8` y densidades bajas equivalentes a `N = 32, 16, 11`;
- conclusiones cuantitativas y cualitativas presentes en el informe final.

Cada conclusión deberá estar respaldada por una figura mostrada en Resultados. La comparación de desempeño del CIM solo aparecerá en conclusiones porque tendrá su propia diapositiva de resultados.

## Verificación

1. Compilar el fuente Beamer con Tectonic.
2. Confirmar 24 páginas, formato 16:9 y numeración correcta.
3. Renderizar las 24 diapositivas a PNG.
4. Inspeccionar cada diapositiva individualmente para detectar texto cortado, títulos partidos, superposiciones o figuras ilegibles.
5. Comparar parámetros, observables y conclusiones contra el informe final.
6. Ejecutar `./scripts/verificar_repo.sh` y revisar el diff antes de entregar.

## Campos externos pendientes

La portada conservará los datos actuales del grupo que figuren en el informe final. Los enlaces de YouTube o plataforma similar no se completarán hasta disponer de URLs públicas verificables.
