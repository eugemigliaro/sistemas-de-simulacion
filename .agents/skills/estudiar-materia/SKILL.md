---
name: estudiar-materia
description: Responde preguntas, explica temas, prepara repasos o simulacros y corrige razonamientos usando primero la wiki y las fuentes de la materia. Usar ante pedidos académicos como explicame, resumí, compará, tomame, preparame, corregí o ayudame a entender.
---

# Estudiar materia

## Recuperar evidencia

1. Leer `materia.yaml`, `wiki/README.md` y el apunte temático relevante.
2. Buscar términos y sinónimos en `wiki/`, `material/extraido/`, notas y práctica con `rg -n -i` o `scripts/buscar.sh`.
3. Verificar afirmaciones importantes contra la fuente catalogada. Inspeccionar el original cuando haya fórmulas, diagramas o maquetación significativa.
4. Aplicar la prioridad de fuentes y el formato de citas definidos en `AGENTS.md`.

## Enseñar de forma adaptativa

- Respetar `estudio.modo`. En modo adaptativo inferir por el pedido si convienen una pista, resolución acompañada o respuesta directa; ante ambigüedad ofrecer las opciones brevemente.
- Conectar intuición, definición formal y ejemplo concreto.
- Separar con claridad lo dicho por la cátedra, lo aportado por notas y el conocimiento general.
- Para un simulacro, preguntar de a una consigna, esperar la respuesta y dar devolución basada en evidencia.
- Para corregir, identificar primero el paso exacto donde cambia la validez; no reemplazar toda la solución si una corrección localizada alcanza.

Una consulta de estudio no autoriza a reescribir la wiki. Si revela un error o vacío, informarlo y proponer la actualización por separado.
