.PHONY: setup seed build test export demo dashboard serve clean

PYTHON ?= python3
DBT := .venv/bin/dbt
UV_CACHE_DIR ?= .uv-cache

setup:
	UV_CACHE_DIR=$(UV_CACHE_DIR) uv sync --extra dbt --extra dev --locked

seed:
	$(DBT) seed --project-dir dbt_project --profiles-dir dbt_project --target local

build:
	$(DBT) build --project-dir dbt_project --profiles-dir dbt_project --target local

test:
	.venv/bin/pytest
	$(DBT) test --project-dir dbt_project --profiles-dir dbt_project --target local

export:
	.venv/bin/python scripts/export_dashboard.py

demo: seed build export

dashboard: build export

serve: dashboard
	$(PYTHON) -m http.server 8000 --directory dashboard

clean:
	$(DBT) clean --project-dir dbt_project --profiles-dir dbt_project

