# Adopción en un repositorio existente

No es necesario migrar un repositorio que ya funciona. La adopción recomendada es incremental.

## Nivel 0 — referencia

Usar el repositorio existente como caso de comparación sin modificarlo. Es el estado recomendado mientras el template evoluciona.

## Nivel 1 — enrolamiento mínimo

Agregar solamente:

- `materia.yaml` con la configuración real;
- `.course-wiki-version` con la versión compatible;
- referencias a las instrucciones existentes si ya cumplen las invariantes.

El comando de configuración admite `--adoptar --sin-readme` para generar únicamente esos archivos. Debe ejecutarse desde una copia del template indicando `--root` hacia el repositorio a adoptar.

```bash
python3 scripts/configurar_materia.py \
  --root /ruta/al/repo-existente \
  --nombre "Nombre de la materia" \
  --adoptar
```

## Nivel 2 — sincronización selectiva

Copiar o actualizar skills y validadores genéricos solo después de revisar el diff. Nunca regenerar fuentes, wiki o soluciones existentes. Un repositorio puede conservar nombres y rutas propios si `AGENTS.md` los documenta.

## Bases de Datos II

`bd2` fue el caso que originó este template y ya satisface las invariantes principales. No necesita reorganización. Su incorporación futura debería limitarse al nivel 1 y, opcionalmente, a actualizaciones selectivas de skills.
