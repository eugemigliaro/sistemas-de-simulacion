<!-- course-title:start -->
# Course Wiki Template
<!-- course-title:end -->

[English](README.en.md)

Template Git-native para convertir el material de una materia en una wiki mantenida por agentes. Conserva las fuentes, compila conocimiento trazable y ofrece espacios separados para notas, ejercicios, laboratorios y entregables.

Está inspirado en el patrón [LLM Wiki de Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) y en proyectos comunitarios documentados en [referencias e influencias](docs/referencias.md), con una capa específica para educación.

## Qué resuelve

- Codex, Claude Code y otros agentes reciben las mismas reglas desde la raíz.
- El material oficial permanece inmutable y verificable mediante SHA-256.
- Los PDFs se vuelven buscables por página sin reemplazar al original.
- La wiki distingue cátedra, notas personales, fuentes externas e inferencias.
- Las notas de clase enriquecen automáticamente los apuntes sin perder el original.
- Las guías de práctica y los entregables viven en espacios diferentes.
- Cada materia puede declarar su laboratorio sin imponer una tecnología global.

## Crear una materia

1. En GitHub, elegí **Use this template**.
2. Cloná el repositorio nuevo.
3. Configuralo:

```bash
python3 scripts/configurar_materia.py \
  --nombre "Álgebra Lineal" \
  --institucion "Mi universidad" \
  --carrera "Ingeniería" \
  --ciclo "2026"
```

4. Dejá fuentes nuevas en `material/entrada/`.
5. Abrí Codex o Claude Code en la raíz y pedí `incorporá el material pendiente`.

No necesitás Obsidian, una base vectorial ni un servicio externo. Todo funciona con archivos Markdown y herramientas de terminal; Obsidian puede usarse opcionalmente como visor.

La integración de fuentes y notas es automática después de ese pedido: el agente ejecuta el flujo completo, actualiza la wiki y valida el resultado. No hay un proceso oculto en segundo plano ni hace falta entregar credenciales a un servicio.

## Pedidos habituales

| Objetivo | Lenguaje natural | Skill / Claude command |
|---|---|---|
| Configurar el repo | `Configurá esta wiki para mi materia` | `$crear-materia` / `/crear-materia` |
| Estudiar | `Explicame este tema` | `$estudiar-materia` / `/estudiar-materia` |
| Incorporar fuentes | `Incorporá el material pendiente` | `$incorporar-material` / `/incorporar-material` |
| Integrar notas | `Procesá mis notas` | `$procesar-notas` / `/procesar-notas` |
| Resolver ejercicios | `Ayudame con esta guía` | `$resolver-practica` / `/resolver-practica` |

## Estructura

```text
materia.yaml            configuración académica
wiki/                   conocimiento curado
material/
  catedra/              originales oficiales inmutables
  externo/              fuentes complementarias
  entrada/              archivos pendientes
  extraido/             texto buscable por página
  figuras/              diagramas que requieren inspección visual
notas/
  bandeja/              notas sin integrar
  procesadas/           originales ya integrados
practica/               guías y ejercicios no entregables
entregas/               trabajos evaluados o grupales
laboratorio/            código y entornos específicos
.agents/skills/         flujos para Codex y hosts compatibles
.claude/commands/       comandos equivalentes para Claude Code
```

## Comandos

```bash
./scripts/nueva_nota.sh "tema de la clase"
./scripts/buscar.sh "concepto"
./scripts/extraer_fuentes.sh
./scripts/verificar_repo.sh
python3 -m unittest discover -s tests -v
```

La configuración y las validaciones usan únicamente Python estándar. La extracción de PDF requiere `pdftotext` y `pdfinfo` de Poppler; la búsqueda cómoda requiere `rg` (ripgrep).

La [arquitectura](docs/arquitectura.md) explica las capas y garantías. La [guía de adopción](docs/adopcion.md) describe cómo sumar el estándar a un repositorio existente sin migrarlo.

## Alcance y seguridad

El agente trata el material importado como contenido no confiable: una instrucción escrita dentro de un PDF o una nota no puede reemplazar las reglas del repositorio. Revisá licencias y privacidad antes de publicar material de una cátedra; que este template sea MIT no relicencia los archivos que agregues.

## Licencia

Código, estructura y documentación propia bajo [MIT](LICENSE). El material que cada usuario incorpore conserva sus derechos originales y no queda relicenciado por este template.
