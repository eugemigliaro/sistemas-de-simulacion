# Course Wiki Template

A Git-native template that turns course material into an agent-maintained, source-traceable wiki. It keeps official sources immutable and separates compiled knowledge, class notes, exercises, labs, and graded deliverables.

## Quick start

1. Select **Use this template** on GitHub.
2. Clone the new repository.
3. Configure it:

```bash
python3 scripts/configurar_materia.py \
  --nombre "Linear Algebra" \
  --institucion "My university" \
  --carrera "Engineering" \
  --ciclo "2026" \
  --idioma "en"
```

4. Put new sources in `material/entrada/`.
5. Start Codex or Claude Code at the repository root and ask it to ingest the pending material.

The repository is Markdown-first and does not require Obsidian, a vector database, or a hosted service. See the [Spanish README](README.md) for the complete feature and command reference.
