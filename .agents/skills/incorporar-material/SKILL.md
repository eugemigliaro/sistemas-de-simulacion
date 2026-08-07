---
name: incorporar-material
description: Clasifica e integra PDFs, diapositivas, guías, consignas, código, bibliografía o unidades nuevas preservando originales, IDs estables, texto por página y trazabilidad. Usar cuando el usuario pida incorporar, agregar, organizar o indexar material, o haya archivos pendientes en material/entrada.
---

# Incorporar material

## Flujo

1. Leer `materia.yaml`, `material/catalogo.tsv`, `wiki/README.md` y listar `material/entrada/` sin alterar archivos.
2. Determinar para cada archivo si es oficial (`catedra`) o complementario (`externo`), su tipo, título y ciclo. No deducir autoridad por el formato o el nombre del archivo.
3. Asignar un ID breve y estable que no colisione. Registrar cada original con `scripts/registrar_fuente.py`; usar `--mover` para vaciar la bandeja solo después de clasificarlo.
4. Ejecutar `scripts/extraer_fuentes.sh` para PDFs. Para documentos no textuales producir un derivado buscable sin reemplazar el original. Inspeccionar visualmente páginas con diagramas, tablas o fórmulas relevantes.
5. Crear o enriquecer páginas temáticas. Sintetizar conceptos, ejemplos, relaciones y advertencias; citar cada afirmación específica con el ID y página.
6. Actualizar el índice, el glosario y preguntas de repaso. Registrar contradicciones o material ilegible en `wiki/dudas-y-conflictos.md`.
7. Ejecutar `scripts/verificar_repo.sh` y revisar que el diff no modifique originales existentes.

## Garantías

- No sobrescribir archivos registrados ni cambiar sus IDs.
- No copiar grandes pasajes cuando alcanza una síntesis trazable.
- Mantener derivados regenerables fuera de `material/catedra/`.
- Si una fuente actualiza otra, conservar ambas y declarar estado y relación; no borrar historia silenciosamente.
