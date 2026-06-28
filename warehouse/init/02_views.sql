create or replace view analytics.observations_enriched as
select
  o.series_id,
  s.name,
  s.source_series_code,
  src.name as source_name,
  src.institution,
  src.url as source_home_url,
  s.source_url,
  s.unit,
  s.frequency,
  s.concept,
  s.geography,
  s.seasonal_adjustment,
  s.transformation,
  s.scope,
  s.method,
  o.date,
  o.value,
  o.original_value,
  o.inserted_at,
  o.revised_at,
  s.last_checked_at,
  s.last_successful_update_at
from raw.observations o
join raw.series s on s.series_id = o.series_id
join raw.sources src on src.source_id = s.source_id;

create or replace view analytics.series_latest as
select distinct on (s.series_id)
  s.series_id,
  s.name,
  s.source_series_code,
  src.name as source_name,
  src.institution,
  s.unit,
  s.frequency,
  s.concept,
  s.geography,
  s.seasonal_adjustment,
  s.transformation,
  s.scope,
  s.method,
  s.start_date,
  s.end_date,
  o.date as latest_date,
  o.value as latest_value,
  s.last_checked_at,
  s.last_successful_update_at,
  s.source_url,
  s.notes
from raw.series s
join raw.sources src on src.source_id = s.source_id
left join raw.observations o on o.series_id = s.series_id
order by s.series_id, o.date desc nulls last;

create or replace view analytics.data_catalog as
select
  series_id,
  name,
  source_series_code,
  source_name,
  institution,
  unit,
  frequency,
  concept,
  geography,
  seasonal_adjustment,
  transformation,
  scope,
  method,
  start_date,
  end_date,
  latest_date,
  last_successful_update_at,
  source_url,
  notes
from analytics.series_latest
order by source_name, name;

create or replace view analytics.overview_latest as
select *
from (
  select 10 as display_order, 'Selic target' as kpi_group, * from analytics.series_latest where series_id = 'bcb_sgs_selic_target'
  union all
  select 20, 'IPCA 12m', * from analytics.series_latest where series_id = 'bcb_sgs_ipca_12m'
  union all
  select 30, 'BRL/USD', * from analytics.series_latest where series_id = 'bcb_sgs_usd_brl_sale'
  union all
  select 40, 'IBC-Br SA', * from analytics.series_latest where series_id = 'bcb_sgs_ibc_br_sa'
  union all
  select 50, 'Primary result 12m', * from analytics.series_latest where series_id = 'bcb_sgs_nfsp_primary_12m_pct_gdp'
  union all
  select 60, 'DBGG', * from analytics.series_latest where series_id = 'bcb_sgs_dbgg_pct_gdp'
  union all
  select 70, 'DLSP', * from analytics.series_latest where series_id = 'bcb_sgs_dlsp_pct_gdp'
) kpis
order by display_order;

create or replace view analytics.fiscal_pulse_series as
select *
from analytics.observations_enriched
where series_id in (
  'bcb_sgs_nfsp_primary_12m_pct_gdp',
  'bcb_sgs_nfsp_nominal_12m_pct_gdp',
  'bcb_sgs_nfsp_interest_12m_pct_gdp',
  'bcb_sgs_dbgg_pct_gdp',
  'bcb_sgs_dlsp_pct_gdp',
  'bcb_sgs_nfsp_primary_monthly_brl',
  'bcb_sgs_nfsp_nominal_monthly_brl',
  'bcb_sgs_nfsp_interest_monthly_brl'
);

create or replace view analytics.inflation_monetary_series as
select *
from analytics.observations_enriched
where series_id in (
  'bcb_sgs_ipca_monthly',
  'bcb_sgs_ipca_12m',
  'bcb_sgs_selic_target',
  'bcb_sgs_usd_brl_sale'
);

create or replace view analytics.labor_income_series as
select *
from analytics.observations_enriched
where series_id in (
  'ibge_pnad_unemployment_rate',
  'ibge_pnad_real_average_income',
  'ibge_pnad_real_labor_income_mass'
);

create or replace view analytics.governo_central_series as
select *
from analytics.observations_enriched
where series_id in (
  'tesouro_rtn_receita_liquida',
  'tesouro_rtn_receita_total',
  'tesouro_rtn_transferencias_reparticao',
  'tesouro_rtn_receita_administrada_rfb',
  'tesouro_rtn_arrecadacao_rgps',
  'tesouro_rtn_despesa_total',
  'tesouro_rtn_beneficios_previdenciarios',
  'tesouro_rtn_pessoal_encargos',
  'tesouro_rtn_outras_obrigatorias',
  'tesouro_rtn_resultado_primario_gc',
  'tesouro_rtn_resultado_primario_tesouro',
  'tesouro_rtn_resultado_previdencia',
  'tesouro_rtn_resultado_primario_bc'
);

create or replace view analytics.federal_budget_series as
select *
from analytics.observations_enriched
where series_id in (
  'tesouro_rtn_beneficios_previdenciarios',
  'tesouro_rtn_pessoal_encargos',
  'tesouro_rtn_outras_obrigatorias'
);

create or replace view analytics.global_last_updated as
select
  max(last_successful_update_at) as last_successful_update_at,
  max(last_checked_at) as last_checked_at,
  count(*) filter (where latest_date is not null) as populated_series,
  count(*) as configured_series
from analytics.series_latest;
