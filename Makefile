# Makefile for vc-pattern-notebooks.
#
# Targets are intentionally thin wrappers so a reader can reproduce
# everything in this repo without memorizing flags.

PYTHON ?= python3
NOTEBOOKS := $(wildcard notebooks/*.ipynb)

.PHONY: help setup fetch-data validate run-notebooks lint clean refresh

help:
	@echo "Targets:"
	@echo "  setup          install pinned deps into the current env"
	@echo "  fetch-data     pull public unicorn + founder data into data/raw/"
	@echo "  validate       run scripts/validate_data.py (sanity checks)"
	@echo "  run-notebooks  execute all notebooks in place (timeout 180s/cell)"
	@echo "  lint           ruff on scripts/, nbqa ruff on notebooks/"
	@echo "  refresh        timestamped re-pull + diff vs prior snapshot"
	@echo "  clean          drop ipynb checkpoints and __pycache__"

setup:
	$(PYTHON) -m pip install -r requirements.lock || $(PYTHON) -m pip install -r requirements.txt

fetch-data:
	$(PYTHON) scripts/fetch_data.py

validate:
	$(PYTHON) scripts/validate_data.py

run-notebooks:
	$(PYTHON) -m jupyter nbconvert --to notebook --execute \
		--ExecutePreprocessor.timeout=180 --inplace $(NOTEBOOKS)

lint:
	$(PYTHON) -m ruff check scripts/
	$(PYTHON) -m nbqa ruff notebooks/

refresh:
	$(PYTHON) scripts/refresh_data.py

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .ipynb_checkpoints -prune -exec rm -rf {} +
	find . -type d -name .ruff_cache -prune -exec rm -rf {} +
	find notebooks -maxdepth 1 -type f -name '*_nbqa_ipynb.py' -delete
	rm -f notebooks/_tmp.ipynb
