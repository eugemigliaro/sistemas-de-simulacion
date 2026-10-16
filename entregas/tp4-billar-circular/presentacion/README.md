# Presentación TP4

Borrador de 29 láminas para revisión del grupo. Conserva el formato 16:9, Beamer Warsaw, miniframes, colores y numeración del TP3. Incluye todos los estudios realizados, cinco animaciones físicas y declaración de asistencia de IA. El guion propone 13 minutos; aún requiere ensayo real.

- `SdS_TP4_2026Q2G07CS_Presentación.pdf`: nombre solicitado para la entrega; fotogramas estáticos y cinco enlaces públicos pendientes.
- `SdS_TP4_2026Q2G07CS_Presentacion.pptx`: versión para exponer, con cinco MP4 incrustados y guion del orador separado.
- `SdS_TP4_2026Q2G07CS_Presentacion.tex`: fuente editable de texto, fórmulas y disposición.
- `GUION.md`: notas, fuentes y reparto orientativo A/B/C, sin asignar decisiones a los integrantes.
- `revision-guia.md`: correspondencia con la guía y las devoluciones anteriores.

El PPTX sigue el mecanismo del TP3: cada lámina es una imagen y los videos son objetos de medios. Para cambiar texto se edita el TeX y se regenera; los textos y gráficos no son objetos editables dentro de PowerPoint. La variante sin notas incrustadas abrió correctamente en Keynote y el estudiante confirmó su funcionamiento. El master de notas previo impedía la importación; por eso el guion se conserva aparte. No se verificó reproducción en PowerPoint. Probarla en el equipo de exposición antes de usarlo.

## Completar antes de entregar

1. Revisar entre todos los integrantes contenido, nombres, comisión y declaración de IA. La consigna reserva a los estudiantes la elaboración final y no permite producción independiente de presentaciones por agentes [TP04, p. 4]. La revisión del grupo todavía no se da por realizada.
2. Publicar las cinco animaciones en YouTube/Vimeo por decisión del grupo e incorporar sus URL reales en `enlaces.json`. No se publicó ningún archivo ni se inventaron enlaces. Regenerar para que aparezcan explícitamente debajo de los fotogramas [GPRES, pp. 2–3].
3. Ensayar, acordar quién presenta cada parte y comprobar los videos en el software y equipo de exposición. Quitar la indicación de borrador de la portada solamente al finalizar la revisión.
4. Entregar el PDF, sin adjuntar archivos sueltos de animaciones [GPRES, p. 3]. El PPTX es el soporte de exposición. El ZIP del motor es otro componente de la entrega [TP04, p. 4].

## Regenerar

Desde `entregas/tp4-billar-circular`, con NumPy, Matplotlib, Pillow, Tectonic y Poppler:

```bash
../tp3-billar-metegol/python/.venv/bin/python python/presentation_assets.py
../tp3-billar-metegol/python/.venv/bin/python python/build_presentation.py
```

El segundo comando actualiza los enlaces, compila el PDF, copia su nombre oficial, renderiza las láminas y reconstruye el PPTX y conserva el guion aparte. No vuelve a ejecutar los estudios. Usa los masters del PPTX anterior sin modificarlo. El runtime Artifact Tool no estaba disponible en este entorno; se utilizó Beamer y ensamblado OOXML local.

Las citas de fuentes se conservan en `notas.json` y `GUION.md`; no se muestran sobre las diapositivas.

Las animaciones ya están generadas. `python/presentation_media.py` permite regenerarlas desde trayectorias de demostración; `--position-only` reutiliza las tres trayectorias verificadas de posición. Si cambian los GIF, reconvertir a MP4 antes de reconstruir el PPTX. En macOS se utilizó `gif_to_mp4.swift` con AVFoundation. Los clips `*-live.mp4` son los que se incrustan. `.build/` contiene derivados de revisión, manifiestos y hashes, no archivos para entregar.
