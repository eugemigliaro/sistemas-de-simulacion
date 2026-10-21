# Presentación TP4

Presentación de 29 láminas. Conserva el formato 16:9, Beamer Warsaw, miniframes, colores y numeración del TP3. Incluye todos los estudios realizados, cuatro animaciones físicas y declaración de asistencia de IA. El guion suma 12:15, con 45 s de margen; aún requiere ensayo real.

- `../entrega-final/SdS_TP4_2026Q2G07CS_Presentación.pdf`: PDF de entrega con el nombre solicitado; fotogramas estáticos y cuatro enlaces públicos pendientes. Es la única copia: la salida intermedia de tectonic queda en `.build/`.
- `SdS_TP4_2026Q2G07CS_Presentacion.pptx`: versión para exponer, con cuatro MP4 incrustados y guion del orador separado.
- `SdS_TP4_2026Q2G07CS_Presentacion.tex`: fuente editable de texto, fórmulas y disposición.
- `GUION.md`: notas, fuentes y reparto orientativo A/B/C, sin asignar decisiones a los integrantes.
- `revision-guia.md`: correspondencia con la guía y las devoluciones anteriores.

El PPTX sigue el mecanismo del TP3: cada lámina es una imagen y los videos son objetos de medios. Para cambiar texto se edita el TeX y se regenera; los textos y gráficos son imágenes dentro de PowerPoint, salvo los nuevos diagramas UML y de flujo (D5–D6), que contienen texto, nodos y conectores editables. Sus coordenadas para PDF y PPTX se mantienen juntas en `python/presentation_diagrams.py`; `diagramas.tex` es un derivado regenerable. La variante sin notas incrustadas abrió correctamente en Keynote y el estudiante confirmó su funcionamiento. El master de notas previo impedía la importación; por eso el guion se conserva aparte. No se verificó reproducción en PowerPoint. Probarla en el equipo de exposición antes de usarlo.

## Completar antes de entregar

1. Revisar entre todos los integrantes contenido, nombres, comisión y declaración de IA [TP04, p. 4].
2. Publicar las cuatro animaciones en YouTube/Vimeo e incorporar sus URL reales en `enlaces.json` (claves `rendimiento`, `posicion`, `rapidez` y `densidad`). Regenerar para que aparezcan explícitamente debajo de los fotogramas [GPRES, pp. 2–3].
3. Ensayar, acordar quién presenta cada parte y comprobar los videos en el software y equipo de exposición.
4. Después de la última regeneración, `make package` desde `entregas/tp4-billar-circular` agrega el ZIP del motor a `entrega-final/`, junto al PDF. Entregar esos dos archivos, sin animaciones sueltas [GPRES, p. 3] [TP04, p. 1]. El PPTX es el soporte de exposición.

## Regenerar

Desde `entregas/tp4-billar-circular`, con NumPy, Matplotlib, Pillow, Tectonic y Poppler:

```bash
../tp3-billar-metegol/python/.venv/bin/python python/presentation_assets.py
../tp3-billar-metegol/python/.venv/bin/python python/build_presentation.py
```

El segundo comando regenera los diagramas, actualiza los enlaces, compila el PDF y lo escribe con el nombre oficial en `entrega-final/`, renderiza las láminas y reconstruye el PPTX y conserva el guion aparte. No vuelve a ejecutar los estudios. Usa los masters del PPTX anterior sin modificarlo. Busca `tectonic` en el PATH, en Homebrew (macOS) o en `/usr/lib/chatgpt/resources/tectonic/tectonic` (Linux); compila con `--only-cached`, así que la primera vez en una máquina puede hacer falta una compilación sin esa opción para bajar las fuentes. El texto de la diapositiva 16 sale de `rendimiento.tex`, que genera `presentation_assets.py` a partir de `performance-summary.csv`. El runtime Artifact Tool no estaba disponible en este entorno; se utilizó Beamer y ensamblado OOXML local.

Las citas de fuentes se conservan en `notas.json` y `GUION.md`; no se muestran sobre las diapositivas.

Las animaciones ya están generadas. `python/presentation_media.py` permite regenerarlas desde trayectorias de demostración; `--position-only` reutiliza las tres trayectorias verificadas de posición. Si cambian los GIF, reconvertir a MP4 antes de reconstruir el PPTX. En macOS se utilizó `gif_to_mp4.swift` con AVFoundation. Los clips `*-live.mp4` son los que se incrustan. `.build/` contiene derivados de revisión, manifiestos y hashes, no archivos para entregar.

## Correcciones del 20/10/2026

- Portada sin la indicación de borrador.
- D8: rótulos de r y de la velocidad dentro del círculo.
- D10: tabla con N, x0, paso, corridas y tiempo simulado de cada estudio, como pide GPRES p. 2; se quitó la referencia interna a otra diapositiva.
- D12: una sola figura de ECM frente al paso, con la leyenda fuera de los datos y una franja inferior con el ECM relativo a Verlet original; más grande y legible.
- D16: texto de escalado generado desde los datos; el protocolo v2, ejecutado el 21/10 en la Apple M5 Pro, agrega el TP3 hasta N=650.
- D21: bins centrados en múltiplos de 0,1 m/s; la delta inicial ya no se reparte entre dos bins.
- D22: ajuste y error del ajuste S(k_BT) lado a lado, como en el TP3; comparación con m⟨v²⟩/2 y mv0²/2.
- D24 y D25: explicación de la extensión a 300 s y del triángulo de N=650 sin jerga.
- D26: rótulo de la barra de color completo.
- D25: rótulos del eje logarítmico fijados; al regenerar en otra máquina habían desaparecido.
- D28: las conclusiones responden las preguntas de la consigna; el guion las desarrolla.
- D29: Codex con GPT-6.1 Sol y Claude Code con Claude Opus 5.5.
- Guion: 12:15 en total, con margen, y notas nuevas de D10, D12, D16, D19, D21, D22, D24, D25, D28 y D29.

## Correcciones del 19/10/2026

- D5: UML con nombres de estructuras únicamente. D6: flujo completo con decisión final y retorno del paso temporal.
- Antigua D9 → D10: parámetros fijos y variables con rangos; duraciones y repeticiones junto a cada estudio.
- Se retiró la antigua D12 (animación de energía) según la devolución recibida. TP04, p. 3 exige el análisis energético; GPRES, p. 2 recomienda animación como estructura general. Se conservan las cuatro animaciones restantes y las separadoras.
- D13: variación porcentual con signo respecto de E(0), una condición inicial común entre pasos y ecuaciones separadas para evitar desbordes. D14 define su máximo absoluto muestreado en porcentaje.
- D16: crecimiento del costo cuantificado entre N=100, 200 y 400, sin inferir una ley asintótica.

Se mantienen 29 láminas. El guion fue renumerado y conserva 13 minutos como objetivo de ensayo. Los originales previos están preservados en `.build/antes-correcciones-2026-10-19/`. El registro `auditoria-tp2-tp3-tp4.md` describe el borrador previo y mantiene recomendaciones de contenido todavía pendientes; esta corrección no certifica toda la entrega ni sustituye la revisión del grupo.

### Segunda versión del UML

D5 incorpora las funciones libres `generate()`, `simulate()` y `forces()`, las estructuras Config, Particle, ForceResult y Vec, títulos en castellano y relaciones rotuladas. Las dependencias principales se distinguen de la composición. Se retiró el recuadro del namespace `tp4::billiard`, que no describía una responsabilidad. No se agregaron atributos ni métodos a las estructuras. La versión anterior del generador y PPTX se conserva en `.build/uml-simple/`.

### Continuidad entre D8 y D10

D8 presenta geometría, estado inicial y conversión irreversible, sin valores numéricos de constantes. D9 define los observables de esa conversión. D10 concentra la única tabla general de parámetros fijos y rangos variables. Se conservan los símbolos en el esquema y las condiciones necesarias junto a las figuras de resultados.
