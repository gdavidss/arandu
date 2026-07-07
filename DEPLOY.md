# Deploying arandu (Supabase + one small host)

The honest split: **Supabase hosts your *data*. One small host runs everything
else.** Supabase is managed Postgres (plus auth/storage/edge functions) — it
cannot run the Metabase JVM app, the Node proxy, or the Python MCP server. Those
are long-running containers and need a host.

| Piece | Where | Cost |
| --- | --- | --- |
| **Warehouse** (your data: `raw` + `analytics`) | **Supabase** managed Postgres | Free |
| Ingestion worker (daily refresh) | the host (keeps Supabase awake) | — |
| Metabase + its own app DB | the host | — |
| Frontend proxy (`server.mjs`) + React | the host | — |
| MCP server | the host | — |
| Daily cron / CI | GitHub Actions | Free |
| **Host** for the 4 containers above | **Oracle Cloud Always Free** VM (or Hetzner ~€4/mo) | Free–€4 |

Data is tiny (a few MB, ~45k rows) — nowhere near Supabase's 500 MB free cap.

---

## 1. Supabase — the warehouse

1. Create a project at [supabase.com](https://supabase.com) (free tier). Pick a
   strong DB password and a region close to your host.
2. Project → **Connect** → copy the **Connection Pooler** credentials
   (*Session mode*, port `5432`). The user looks like `postgres.<project-ref>`.
   Use the pooler (not a direct connection) so Metabase's persistent connections
   don't exhaust the direct-connection limit.
3. On your machine (or the host), create the schema + views on Supabase:
   ```sh
   cp .env.prod.example .env      # fill in the Supabase + Metabase values
   docker compose -f docker-compose.prod.yml run --rm ingestion python -m arandu migrate
   ```
   That applies `warehouse/init/01_schema.sql` and `02_views.sql` to Supabase.

> Free Supabase projects **pause after ~7 days of inactivity**. The ingestion
> worker (below) hits it daily, which keeps it awake. If you ever turn the host
> off for a week, un-pause the project in the dashboard.

## 2. The host

**Recommended: Oracle Cloud Always Free** — an Ampere ARM VM (up to 4 vCPU /
24 GB RAM) that is free *forever*. Metabase alone wants ~1–2 GB, so give it
room. Alternatives: Hetzner CX22 (~€4/mo, simplest), Fly.io, or Railway.

On the host: install Docker + the compose plugin, open ports 80 and 443, and
`git clone` this repo.

## 3. Deploy

```sh
cp .env.prod.example .env         # fill in every value (see comments in the file)
docker compose -f docker-compose.prod.yml up -d --build
# wait ~1–2 min for Metabase to boot, then build the dashboard once:
docker compose -f docker-compose.prod.yml --profile setup run --rm metabase_setup
```

- `up -d` starts: Metabase (+ its local app DB), the ingestion worker, the MCP
  server, the frontend, and Caddy.
- The one-shot `metabase_setup` creates the admin user, registers the Supabase
  warehouse as a Metabase data source (over TLS — `WAREHOUSE_SSL=true`), and
  builds all the cards/tabs. Re-run it only when cards or series change.

## 4. Domain + HTTPS

Point DNS at the host and Caddy handles TLS automatically:

- `A  arandu.cc      -> <host IP>`
- `A  mcp.arandu.cc  -> <host IP>`   (optional, for the MCP endpoint)

Set `ARANDU_DOMAIN=arandu.cc` in `.env`. On first request Caddy fetches a
Let's Encrypt cert. The app is then at `https://arandu.cc`; agents connect at
`https://mcp.arandu.cc/mcp`.

## 5. Keeping data fresh

The `ingestion` worker refreshes the live series every 24 h (BCB, IBGE, Comex,
ECB) and rewrites `frontend/public/dashboard-data.json`. Static snapshots
(Petrobras, VC, energia, Ibovespa, bets, BTI) don't change. Nothing else to
schedule — that daily hit also keeps Supabase from pausing.

*(Optional)* If you'd rather not keep the worker running, run
`docker compose -f docker-compose.prod.yml run --rm ingestion python -m arandu ingest`
from a GitHub Actions cron against `WAREHOUSE_DSN` — but then re-run
`metabase_setup` (or `export-dashboard-data`) to refresh the frontend JSON.

## Costs

Everything is free on Supabase free + Oracle Always Free + GitHub Actions.
If you outgrow Oracle's free tier, Hetzner CX22 (~€4/mo) is the easy next step;
Supabase Pro ($25/mo) removes the pause and raises limits, but you won't need it
at this data size.

## Gotchas

- **Supabase needs TLS.** Metabase's warehouse connection uses `WAREHOUSE_SSL=true`
  (set in the prod compose); the Python DSN needs `?sslmode=require` (already in
  the `.env` template).
- **Use the pooler, not direct.** Direct connections are limited on the free tier.
- **Metabase's app DB stays local** (the `metabase_postgres` service). Don't put
  it on Supabase free — it's separate from your data and churns its own tables.
- **Metabase is not exposed publicly** — only the frontend proxy reaches it
  (`expose`, not `ports`). All public traffic goes through Caddy → frontend.
- **`.env` is gitignored.** Keep it that way; rotate `MB_PASSWORD` and the
  Supabase password if they ever leak.
