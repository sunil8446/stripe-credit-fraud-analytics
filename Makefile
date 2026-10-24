.PHONY: setup seed build train ml-build phase2 phase2-5 test export standalone demo dashboard serve clean

PYTHON ?= python3
DBT := .venv/bin/dbt
UV_CACHE_DIR ?= .uv-cache

setup:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv sync --extra dbt --extra ml --extra dev --locked

seed:
	$(DBT) seed --project-dir dbt_project --profiles-dir dbt_project --target local

build:
	$(DBT) build --project-dir dbt_project --profiles-dir dbt_project --target local --exclude tag:ml

train:
	PYTHONPATH=src .venv/bin/python scripts/train_model.py

ml-build:
	$(DBT) build --project-dir dbt_project --profiles-dir dbt_project --target local --select tag:ml

phase2: phase2-5

phase2-5: seed build train ml-build export

test: seed build train ml-build
	.venv/bin/pytest
	$(DBT) test --project-dir dbt_project --profiles-dir dbt_project --target local

export:
	.venv/bin/python scripts/export_dashboard.py
	$(PYTHON) scripts/build_standalone_dashboard.py

standalone:
	$(PYTHON) scripts/build_standalone_dashboard.py

demo: phase2-5

dashboard: build train ml-build export

serve: dashboard
	$(PYTHON) -m http.server 8000 --directory dashboard

clean:
	$(DBT) clean --project-dir dbt_project --profiles-dir dbt_project

