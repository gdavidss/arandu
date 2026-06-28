FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md /app/
COPY arandu /app/arandu
COPY config /app/config
COPY tests /app/tests

RUN pip install --no-cache-dir -e ".[dev]"

CMD ["python", "-m", "arandu", "worker"]
