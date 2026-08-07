# Contribuir

Los cambios deben mantener las invariantes de `docs/arquitectura.md`, funcionar sin servicios alojados y no incorporar material académico con derechos restringidos.

Antes de proponer un cambio:

```bash
make test
```

Un cambio de estructura, `materia.yaml` o comportamiento de los skills debe documentar cómo lo adopta un repositorio existente sin perder contenido. Los scripts base usan Python estándar y herramientas de terminal comunes para conservar portabilidad.
