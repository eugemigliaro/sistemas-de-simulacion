---
name: procesar-notas
description: Contrasta notas personales pendientes con el material oficial, enriquece los apuntes canónicos y archiva intactos los originales con un registro idempotente. Usar cuando el usuario pida procesar o integrar notas, enriquecer apuntes, o haya Markdown pendiente en notas/bandeja.
---

# Procesar notas

## Flujo automático

1. Leer `materia.yaml`, `notas/registro.tsv`, los archivos de `notas/bandeja/` y las páginas temáticas relacionadas.
2. Calcular SHA-256 de cada nota y omitir cualquier hash ya registrado.
3. Asignar el ID `N-AAAA-MM-DD-slug` a partir de la nota. Buscar respaldo o conflicto en fuentes oficiales y externas.
4. Integrar en la wiki solo los aportes útiles: aclaraciones, ejemplos de clase, conexiones, énfasis docente o dudas. Citar la nota y conservar la jerarquía de autoridad.
5. Si una afirmación contradice la cátedra o no puede verificarse, no normalizarla como hecho; registrarla en `wiki/dudas-y-conflictos.md`.
6. Verificar que el hash no cambió, mover el original a `notas/procesadas/` y anexar una fila a `notas/registro.tsv` con páginas modificadas y observaciones.
7. Actualizar glosario o repaso cuando corresponda y ejecutar `scripts/verificar_repo.sh`.

No resumir una nota por obligación: si no aporta conocimiento nuevo, archivarla y registrar ese resultado sin alterar la wiki.
