# arandu.ai ingestion

Python ingestion service for official Brazilian public macro and fiscal series.

Run inside Docker:

```sh
make ingest
make test
```

Run locally:

```sh
cd ingestion
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
WAREHOUSE_DSN=postgresql://fiscallens:fiscallens@localhost:5433/fiscallens python -m arandu ingest
```
