.PHONY: configurar extraer nota buscar verificar test

configurar:
	@echo 'Usá: python3 scripts/configurar_materia.py --nombre "Mi materia" [opciones]'

extraer:
	./scripts/extraer_fuentes.sh

nota:
	@echo 'Usá: ./scripts/nueva_nota.sh "tema"'

buscar:
	@echo 'Usá: ./scripts/buscar.sh "concepto"'

verificar:
	./scripts/verificar_repo.sh

test:
	python3 -m unittest discover -s tests -v
	./scripts/verificar_repo.sh
