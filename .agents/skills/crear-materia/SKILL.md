---
name: crear-materia
description: Configura Course Wiki Template para una materia nueva o agrega su contrato mínimo a un repositorio académico existente. Usar cuando el usuario pida crear, inicializar, configurar o adaptar una wiki de materia, incluidos motor, lenguaje, modalidad de estudio y política de entregas.
---

# Crear materia

## Flujo

1. Inspeccionar el repositorio y leer `README.md`, `materia.yaml` y `AGENTS.md` si existen.
2. Obtener del pedido o preguntar únicamente los datos que cambien materialmente el resultado: nombre, institución, carrera, ciclo, modalidad de estudio, tecnología de laboratorio y si las guías son entregables.
3. Para un repo creado desde el template ejecutar `python3 scripts/configurar_materia.py` con esos valores. No usar `--force` sin mostrar antes qué configuración se reemplazará.
4. Para un repo académico existente usar `--adoptar`: esto agrega solo `materia.yaml` y `.course-wiki-version`. No mover, renombrar ni reescribir contenido previo.
5. Adaptar el laboratorio únicamente cuando el usuario o el material requieran una tecnología concreta.
6. Ejecutar `./scripts/verificar_repo.sh` y revisar el diff.

## Criterios

- Preferir valores explícitos del usuario y conservar vacíos los datos desconocidos.
- No inventar reglas de evaluación ni herramientas.
- Mantener `estudio.modo: adaptativo` cuando el usuario no elija otro modo.
- Explicar cualquier adopción opcional como incremental y reversible.
- No crear un remoto, commit ni push salvo pedido explícito.
