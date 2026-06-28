create schema if not exists raw;
create schema if not exists analytics;

create table if not exists raw.sources (
  source_id text primary key,
  name text not null,
  institution text not null,
  url text not null,
  license_or_terms text,
  notes text
);

create table if not exists raw.series (
  series_id text primary key,
  source_id text not null references raw.sources(source_id),
  source_series_code text not null,
  name text not null,
  description text,
  unit text not null,
  frequency text not null,
  concept text not null,
  geography text not null default 'Brazil',
  seasonal_adjustment text not null default 'not seasonally adjusted',
  transformation text not null,
  scope text,
  method text,
  start_date date,
  end_date date,
  last_checked_at timestamptz,
  last_successful_update_at timestamptz,
  source_url text,
  notes text,
  unique (source_id, source_series_code)
);

create table if not exists raw.observations (
  series_id text not null references raw.series(series_id) on delete cascade,
  date date not null,
  value numeric not null,
  original_value numeric,
  inserted_at timestamptz not null default now(),
  revised_at timestamptz,
  raw_payload jsonb,
  primary key (series_id, date)
);

create table if not exists raw.ingestion_runs (
  run_id bigserial primary key,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  status text not null default 'running',
  series_attempted int not null default 0,
  series_succeeded int not null default 0,
  observations_upserted int not null default 0
);

create table if not exists raw.ingestion_errors (
  error_id bigserial primary key,
  run_id bigint references raw.ingestion_runs(run_id) on delete cascade,
  source_id text,
  series_id text,
  message text not null,
  details jsonb,
  created_at timestamptz not null default now()
);

create table if not exists raw.dashboard_annotations (
  annotation_id bigserial primary key,
  date date not null,
  title text not null,
  body text,
  source_url text
);

create index if not exists observations_series_date_idx
  on raw.observations(series_id, date desc);

create index if not exists series_source_idx
  on raw.series(source_id);

insert into raw.sources (source_id, name, institution, url, license_or_terms, notes)
values
  (
    'bcb_sgs',
    'Sistema Gerenciador de Séries Temporais (SGS/BCData)',
    'Banco Central do Brasil',
    'https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados?formato=json',
    'Open Data Commons Open Database License (ODbL), as listed in the BCB open-data portal',
    'Official BCB time-series API. Some fiscal indicators are below-the-line NFSP concepts and must not be mixed with Tesouro RTN above-the-line concepts.'
  ),
  (
    'tesouro_series',
    'Séries Temporais do Tesouro Nacional',
    'Secretaria do Tesouro Nacional',
    'https://series-temporais.tesouro.gov.br/backend-series-temporais/rest/Public/SerieGrafico',
    'Tesouro Transparente public data terms / ODbL in CKAN metadata where listed',
    'Official Tesouro Transparente public API used for RTN Governo Central monthly series.'
  ),
  (
    'ibge_sidra',
    'SIDRA / Serviço de Dados IBGE',
    'Instituto Brasileiro de Geografia e Estatística',
    'https://servicodados.ibge.gov.br/api/v3/agregados',
    'IBGE public API terms',
    'Used for macro context series where configured.'
  )
on conflict (source_id) do update set
  name = excluded.name,
  institution = excluded.institution,
  url = excluded.url,
  license_or_terms = excluded.license_or_terms,
  notes = excluded.notes;
