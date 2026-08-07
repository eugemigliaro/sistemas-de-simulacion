# Material y fuentes

Esta carpeta separa originales, archivos pendientes y derivados:

- `entrada/`: bandeja temporal para material todavía no clasificado.
- `catedra/`: originales oficiales; no se editan después de registrarlos.
- `externo/`: bibliografía o recursos complementarios.
- `extraido/`: texto regenerable y buscable, con cortes de página.
- `figuras/`: capturas o diagramas derivados que necesitan inspección visual.

`catalogo.tsv` asigna un ID estable a cada fuente. `checksums.sha256` permite detectar cambios accidentales en originales oficiales. Para registrar una fuente usá `scripts/registrar_fuente.py`; no la copies manualmente a `catedra/`.

IDs sugeridos: `T01` para teoría, `P01` para práctica, `G01` para guías, `B01` para bibliografía y `X01` para material externo. El ID no debe cambiar aunque se renombre el título humano.
