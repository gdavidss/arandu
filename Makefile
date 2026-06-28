COMPOSE=docker compose

.PHONY: up down logs ingest refresh export-dashboard-data migrate seed-metabase test lint fmt ps clean

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=200

ps:
	$(COMPOSE) ps

migrate:
	$(COMPOSE) run --rm ingestion python -m arandu migrate

ingest:
	$(COMPOSE) run --rm ingestion python -m arandu ingest
	$(MAKE) export-dashboard-data

# Manual one-shot refresh; the `ingestion` service also does this daily on its own.
refresh: ingest

export-dashboard-data:
	$(COMPOSE) run --rm -v "$(CURDIR)/frontend/public:/frontend-public" ingestion python -m arandu export-dashboard-data --output /frontend-public/dashboard-data.json

seed-metabase:
	$(COMPOSE) run --rm metabase_setup python -m arandu.metabase_setup

test:
	$(COMPOSE) run --rm ingestion pytest

lint:
	$(COMPOSE) run --rm ingestion ruff check .

fmt:
	$(COMPOSE) run --rm ingestion ruff format .

clean:
	$(COMPOSE) down -v --remove-orphans
