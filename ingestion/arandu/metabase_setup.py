from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)


CHART_COLORS = [
    "#1f77b4",
    "#d62728",
    "#2ca02c",
    "#9467bd",
    "#ff7f0e",
    "#17becf",
    "#8c564b",
    "#e377c2",
]


def line_settings(metric: str, colors: list[str] | None = None) -> dict[str, Any]:
    return {
        # "Série" must be a dimension (breakout), not just series_order_dimension —
        # otherwise Metabase SUMS multiple series into one line.
        "graph.dimensions": ["Data", "Série"],
        "graph.metrics": [metric],
        "graph.colors": colors or CHART_COLORS,
        "graph.x_axis.title_text": "Data",
        "graph.y_axis.title_text": metric,
    }


def bar_settings(metric: str, colors: list[str] | None = None) -> dict[str, Any]:
    return {
        "graph.dimensions": ["Categoria"],
        "graph.metrics": [metric],
        "graph.colors": colors or CHART_COLORS,
        "graph.x_axis.title_text": "Categoria",
        "graph.y_axis.title_text": metric,
    }


def time_bar_settings(metric: str, colors: list[str] | None = None) -> dict[str, Any]:
    return {
        "graph.dimensions": ["Data", "Série"],
        "graph.metrics": [metric],
        "graph.colors": colors or CHART_COLORS,
        "graph.x_axis.title_text": "Data",
        "graph.y_axis.title_text": metric,
    }


SERIES_LABELS = {
    "bcb_sgs_selic_target": "Selic meta",
    "bcb_sgs_ipca_monthly": "IPCA mensal",
    "bcb_sgs_ipca_12m": "IPCA em 12 meses",
    "bcb_focus_ipca_12m_ahead": "Expectativa Focus (12m à frente)",
    "bcb_sgs_usd_brl_sale": "Câmbio BRL/USD",
    "ecb_cny_brl": "Câmbio BRL/CNY",
    "bcb_sgs_reer_ipca": "Câmbio efetivo real (IPCA)",
    "bcb_sgs_pib_monthly_brl": "PIB mensal nominal",
    "bcb_sgs_ibc_br_sa": "IBC-Br dessazonalizado",
    "bcb_sgs_ibc_br_nsa": "IBC-Br (série original)",
    "bcb_sgs_dbgg_pct_gdp": "DBGG",
    "bcb_sgs_dlsp_pct_gdp": "DLSP",
    "bcb_sgs_nfsp_primary_12m_pct_gdp": "Resultado primário NFSP 12m",
    "bcb_sgs_nfsp_nominal_12m_pct_gdp": "Resultado nominal NFSP 12m",
    "bcb_sgs_nfsp_interest_12m_pct_gdp": "Juros nominais 12m",
    "bcb_sgs_nfsp_primary_monthly_brl": "Resultado primário NFSP mensal",
    "bcb_sgs_nfsp_nominal_monthly_brl": "Resultado nominal NFSP mensal",
    "bcb_sgs_nfsp_interest_monthly_brl": "Juros nominais mensais",
    "bcb_sgs_endividamento_familias": "Endividamento das famílias",
    "bcb_sgs_endividamento_familias_ex_hab": "Endividamento exceto habitação",
    "bcb_sgs_comprometimento_renda": "Comprometimento de renda (serviço da dívida)",
    "bcb_sgs_inadimplencia_total": "Inadimplência total",
    "bcb_sgs_inadimplencia_pf": "Inadimplência pessoas físicas",
    "bcb_sgs_ipca_alimentacao": "IPCA alimentação e bebidas",
    "bcb_sgs_ipca_nucleo_ma": "IPCA núcleo (médias aparadas)",
    "bcb_sgs_ipca_servicos": "IPCA serviços",
    "bcb_sgs_salario_minimo": "Salário mínimo",
    "ibge_pnad_unemployment_rate": "Taxa de desocupação",
    "ibge_pnad_real_average_income": "Rendimento real médio",
    "ibge_pnad_real_labor_income_mass": "Massa real de rendimentos",
    "tesouro_rtn_receita_liquida": "Receita líquida",
    "tesouro_rtn_receita_total": "Receita total",
    "tesouro_rtn_transferencias_reparticao": "Transferências por repartição",
    "tesouro_rtn_receita_administrada_rfb": "Receita administrada pela RFB",
    "tesouro_rtn_arrecadacao_rgps": "Arrecadação líquida RGPS",
    "tesouro_rtn_despesa_total": "Despesa total",
    "tesouro_rtn_beneficios_previdenciarios": "Benefícios previdenciários",
    "tesouro_rtn_pessoal_encargos": "Pessoal e encargos",
    "tesouro_rtn_outras_obrigatorias": "Outras obrigatórias",
    "tesouro_rtn_resultado_primario_gc": "Resultado primário Governo Central",
    "tesouro_rtn_resultado_primario_tesouro": "Resultado primário Tesouro",
    "tesouro_rtn_resultado_previdencia": "Resultado Previdência",
    "tesouro_rtn_resultado_primario_bc": "Resultado primário Banco Central",
    "ibge_cnt_volume_sa_agropecuaria": "Agropecuária",
    "ibge_cnt_volume_sa_industria": "Indústria",
    "ibge_cnt_volume_sa_servicos": "Serviços",
    "ibge_cnt_volume_sa_pib": "PIB",
    "ibge_cnt_volume_nsa_agropecuaria": "Agropecuária",
    "ibge_cnt_volume_nsa_industria": "Indústria",
    "ibge_cnt_volume_nsa_servicos": "Serviços",
    "ibge_pim_industria_geral_sa": "Indústria (PIM-PF)",
    "ibge_pmc_varejo_volume_sa": "Varejo (PMC)",
    "ibge_pms_servicos_volume_sa": "Serviços (PMS)",
    "bcb_sgs_exportacoes_fob": "Exportações",
    "bcb_sgs_importacoes_fob": "Importações",
    "bcb_sgs_balanca_comercial_saldo": "Saldo comercial",
    "comexstat_export_china": "China",
    "comexstat_export_eua": "Estados Unidos",
    "comexstat_export_argentina": "Argentina",
    "comexstat_export_paises_baixos": "Países Baixos",
    "comexstat_export_espanha": "Espanha",
    "comexstat_export_singapura": "Singapura",
    "comexstat_export_mexico": "México",
    "comexstat_export_chile": "Chile",
    "comexstat_export_canada": "Canadá",
    "comexstat_export_alemanha": "Alemanha",
    "comexstat_export_japao": "Japão",
    "comexstat_export_coreia_sul": "Coreia do Sul",
    "comexstat_export_demais": "Demais países",
    "comexstat_import_china": "China",
    "comexstat_import_eua": "Estados Unidos",
    "comexstat_import_argentina": "Argentina",
    "comexstat_import_alemanha": "Alemanha",
    "comexstat_import_russia": "Rússia",
    "comexstat_import_india": "Índia",
    "comexstat_import_italia": "Itália",
    "comexstat_import_franca": "França",
    "comexstat_import_mexico": "México",
    "comexstat_import_japao": "Japão",
    "comexstat_import_coreia_sul": "Coreia do Sul",
    "comexstat_import_chile": "Chile",
    "comexstat_import_demais": "Demais países",
    "comexstat_export_mercosul": "Exportações para o Mercosul",
    "comexstat_import_mercosul": "Importações do Mercosul",
    "ibge_va_corrente_agropecuaria": "Agropecuária",
    "ibge_va_corrente_industria": "Indústria",
    "ibge_va_corrente_servicos": "Serviços",
    "ibge_va_corrente_ind_extrativa": "Indústrias extrativas",
    "ibge_va_corrente_ind_transformacao": "Indústrias de transformação",
    "ibge_va_corrente_ind_construcao": "Construção",
    "ibge_va_corrente_ind_eletricidade": "Eletricidade, gás e água",
    "ibge_va_corrente_serv_comercio": "Comércio",
    "ibge_va_corrente_serv_transporte": "Transporte e correio",
    "ibge_va_corrente_serv_informacao": "Informação e comunicação",
    "ibge_va_corrente_serv_financeiras": "Atividades financeiras",
    "ibge_va_corrente_serv_imobiliarias": "Atividades imobiliárias",
    "ibge_va_corrente_serv_admin_publica": "Administração pública",
    "ibge_va_corrente_serv_outros": "Outras atividades de serviços",
    "comexstat_export_prod_comb_oleos_minerais": "Combustíveis e óleos minerais",
    "comexstat_export_prod_graos_oleaginosas": "Grãos e oleaginosas (soja)",
    "comexstat_export_prod_minerios": "Minérios",
    "comexstat_export_prod_carnes": "Carnes",
    "comexstat_export_prod_acucares": "Açúcares",
    "comexstat_export_prod_maquinas_mecanicas": "Máquinas mecânicas",
    "comexstat_export_prod_ferro_aco": "Ferro e aço",
    "comexstat_export_prod_veiculos": "Veículos",
    "comexstat_export_prod_cafe": "Café",
    "comexstat_export_prod_celulose": "Celulose",
    "comexstat_export_prod_demais": "Demais produtos",
    "bcb_spi_pix_count_monthly": "Transações Pix",
    "bcb_spi_pix_value_monthly": "Valor Pix",
    "ibge_tic_domicilios_internet": "Domicílios com internet",
    "ibge_tic_pessoas_internet": "Pessoas que usaram internet",
    "ibge_tic_pessoas_celular": "Pessoas com celular",
    "ibge_tic_domicilios_computador": "Domicílios com computador",
    "ibge_tic_internet_urbana": "Urbano",
    "ibge_tic_internet_rural": "Rural",
    "ibge_tic_conexao_fixa": "Banda larga fixa",
    "ibge_tic_conexao_movel": "Banda larga móvel",
    "ibge_tic_internet_norte": "Norte",
    "ibge_tic_internet_nordeste": "Nordeste",
    "ibge_tic_internet_sudeste": "Sudeste",
    "ibge_tic_internet_sul": "Sul",
    "ibge_tic_internet_centro_oeste": "Centro-Oeste",
    "ibge_tic_ecommerce": "Compraram pela internet",
    "bcb_mpv_pix_value": "Pix",
    "bcb_mpv_pix_count": "Pix",
    "bcb_mpv_ted_value": "TED",
    "bcb_mpv_ted_count": "TED",
    "bcb_mpv_boleto_value": "Boleto",
    "bcb_mpv_boleto_count": "Boleto",
    "bcb_mpv_cheque_value": "Cheque",
    "bcb_mpv_cheque_count": "Cheque",
    "bcb_mpv_cartao_credito_value": "Cartão de crédito",
    "bcb_mpv_cartao_debito_value": "Cartão de débito",
    "bcb_mpv_cartao_credito_count": "Cartão de crédito",
    "bcb_mpv_cartao_debito_count": "Cartão de débito",
    "bcb_pix_usuarios_pf": "Pessoas físicas",
    "bcb_pix_usuarios_pj": "Pessoas jurídicas",
    "bcb_pix_usuarios_total": "Total",
    "rfb_cnae_apostas_arrecadacao": "Arrecadação federal (CNAE 92)",
    "bets_bcb_pix_loterias_ago2024": "Loterias",
    "bets_bcb_pix_cnae92_ago2024": "Apostas — empresas no CNAE 92",
    "bets_bcb_pix_outros_ago2024": "Apostas — empresas fora do CNAE 92",
    "spa_ggr_h1_2025": "GGR — 1º semestre 2025",
    "spa_ggr_ano_2025": "GGR — ano 2025",
    "spa_destinacoes_ano_2025": "Destinações legais (12%) — ano 2025",
    "spa_contas_marcas_2025": "Contas ativas nas marcas/bets",
    "spa_contas_operadores_2025": "Contas ativas em operadores",
    "spa_cpfs_unicos_2025": "CPFs únicos que apostaram",
    "lei14790_dest_esporte": "Esporte",
    "lei14790_dest_turismo": "Turismo",
    "lei14790_dest_seguranca": "Segurança pública",
    "lei14790_dest_educacao": "Educação",
    "lei14790_dest_seguridade": "Seguridade social",
    "lei14790_dest_saude": "Saúde",
    "lei14790_dest_sociedade_civil": "Sociedade civil",
    "lei14790_dest_funapol": "Funapol (Polícia Federal)",
    "lei14790_dest_abdi": "ABDI",
    "bti_status_index_brazil": "Índice de Status",
    "bti_governance_index_brazil": "Índice de Governança",
    "bti_rule_of_law_brazil": "Estado de Direito",
    "bti_stability_democratic_institutions_brazil": "Estabilidade das Instituições Democráticas",
    "bti_stateness_brazil": "Estado (Stateness)",
}


# Presidential-term presets for the dashboard "Período" filter. Each is (label, lower, upper)
# as half-open [lower, upper) SQL date bounds; None means unbounded on that side.
# Terms: FHC 1995-2002, Lula I–II 2003-2010, Dilma 2011 to the 2016-08-31 impeachment
# handover, Temer to 2018, Bolsonaro to 2022, Lula III from 2023. Coverage varies by series:
# BCB reaches ~1996 (some series later by inception), RTN ~1997, IBGE/PNAD only from 2012 —
# so older presets show only the series that existed then (labor/income empty before 2012).
MANDATOS: list[tuple[str, str | None, str | None]] = [
    ("Tudo", None, None),
    ("Últimos 10 anos", "current_date - interval '10 years'", None),
    ("FHC (1995–2002)", "date '1995-01-01'", "date '2003-01-01'"),
    ("Lula I–II (2003–2010)", "date '2003-01-01'", "date '2011-01-01'"),
    ("Dilma (2011–2016)", "date '2011-01-01'", "date '2016-08-31'"),
    ("Temer (2016–2018)", "date '2016-08-31'", "date '2019-01-01'"),
    ("Bolsonaro (2019–2022)", "date '2019-01-01'", "date '2023-01-01'"),
    ("Lula III (2023– )", "date '2023-01-01'", None),
]
PERIODO_VALUES = [label for label, _, _ in MANDATOS]


def _periodo_filter_sql(col: str = "date") -> str:
    """Optional WHERE clause driven by the {{periodo}} text variable (a named preset).

    ``col`` is the date column to bound — pass a qualified name (e.g. 'q."Data"') for
    queries that join/aggregate and where a bare ``date`` would be ambiguous.
    """
    lowers = "\n      ".join(
        f"when '{label}' then {low}" for label, low, _ in MANDATOS if low is not None
    )
    uppers = "\n      ".join(
        f"when '{label}' then {high}" for label, _, high in MANDATOS if high is not None
    )
    # Optional [[ ]] blocks: each is dropped when its variable is unset.
    # {{periodo}} = named presets; {{de}}/{{ate}} = a free custom range (zoom).
    return (
        f"[[ and {col} >= (case {{{{periodo}}}}\n      "
        + lowers
        + "\n      else date '1900-01-01' end)\n"
        + f"    and {col} < (case {{{{periodo}}}}\n      "
        + uppers
        + "\n      else current_date + interval '1 day' end) ]]"
        + f"\n  [[ and {col} >= {{{{de}}}} ]]"
        + f"\n  [[ and {col} <= {{{{ate}}}} ]]"
    )


PERIODO_FILTER = _periodo_filter_sql()


# NFSP below-the-line results are published deficit-positive (necessidade de financiamento).
# We negate the primary and nominal results so the whole dashboard reads surplus-positive
# (+ = superávit), matching the RTN Governo Central tab. Juros (a cost) stays positive.
SURPLUS_POSITIVE_FLIP = {
    "bcb_sgs_nfsp_primary_12m_pct_gdp",
    "bcb_sgs_nfsp_nominal_12m_pct_gdp",
    "bcb_sgs_nfsp_primary_monthly_brl",
    "bcb_sgs_nfsp_nominal_monthly_brl",
}

# Warm gold/amber palette for the Apostas (bets) tab — gives the tab a cohesive identity
# distinct from the fiscal/red charts, and avoids the alarmist all-red look.
BETS_GOLD = "#C4862C"  # headline gold (matches the betting/money theme)
BETS_BROWN = "#A0522D"  # sienna accent
BETS_DEEP = "#8C5A1E"  # deep amber
BETS_GRAY = "#7f7f7f"  # neutral second series
# 9-slice qualitative palette for the Lei 14.790 allocation donut (needs distinct hues).
BETS_PIE = [
    "#C4862C",
    "#2A7F7F",
    "#B5651D",
    "#5E81AC",
    "#8A9A5B",
    "#9C6B9C",
    "#C97B84",
    "#7D7D7D",
    "#5B8C5A",
]


def line_query(
    series_ids: list[str],
    source_view: str = "analytics.observations_enriched",
    metric: str = "Valor",
    negate: set[str] | None = None,
) -> str:
    ids = ",\n    ".join(f"'{series_id}'" for series_id in series_ids)
    labels = "\n    ".join(
        f"when '{series_id}' then '{SERIES_LABELS.get(series_id, series_id)}'"
        for series_id in series_ids
    )
    flip = [s for s in series_ids if negate and s in negate]
    if flip:
        flip_ids = ", ".join(f"'{s}'" for s in flip)
        value_expr = f"(case when series_id in ({flip_ids}) then -value else value end)"
    else:
        value_expr = "value"
    return f"""
select
  date as "Data",
  case series_id
    {labels}
    else name
  end as "Série",
  {value_expr} as "{metric}"
from {source_view}
where series_id in (
    {ids}
  )
  {PERIODO_FILTER}
order by "Data", "Série"
""".strip()


def ipca_target_query() -> str:
    """IPCA 12m plus the time-varying CMN target (center) and its tolerance band.

    Center targets are calendar-year: 4.0 (2003), 5.5 (2004), 4.5 (2005-2018), then the
    declining path 4.25/4.0/3.75/3.5/3.25 to 3.0 from 2024. Tolerance: ±2.5 (2003-2005),
    ±2.0 (2006-2016), ±1.5 (2017+, when the CMN narrowed the band).
    """
    return f"""
with ipca as (
  select date, value as ipca
  from analytics.observations_enriched
  where series_id = 'bcb_sgs_ipca_12m'
),
t as (
  select
    date,
    ipca,
    case extract(year from date)
      when 2003 then 4.0 when 2004 then 5.5
      when 2019 then 4.25 when 2020 then 4.0 when 2021 then 3.75
      when 2022 then 3.5 when 2023 then 3.25
      when 2024 then 3.0 when 2025 then 3.0 when 2026 then 3.0
      else 4.5
    end as meta,
    case
      when extract(year from date) <= 2005 then 2.5
      when extract(year from date) >= 2017 then 1.5
      else 2.0
    end as tol
  from ipca
)
select t.date as "Data", s.label as "Série", s.v as "Variação (%)"
from t
cross join lateral (
  values
    ('IPCA 12m', t.ipca),
    ('Meta', t.meta),
    ('Limite superior', t.meta + t.tol),
    ('Limite inferior', t.meta - t.tol)
) as s(label, v)
where true
  {_periodo_filter_sql("t.date")}
order by "Data", "Série"
""".strip()


IPCA_TARGET_VIZ: dict[str, Any] = {
    "graph.dimensions": ["Data", "Série"],
    "graph.metrics": ["Variação (%)"],
    "graph.x_axis.title_text": "Data",
    "graph.y_axis.title_text": "Variação (%)",
    "graph.series_order": [
        {"key": "IPCA 12m", "enabled": True},
        {"key": "Meta", "enabled": True},
        {"key": "Limite superior", "enabled": True},
        {"key": "Limite inferior", "enabled": True},
    ],
    "series_settings": {
        "IPCA 12m": {"line.marker_enabled": False, "color": "#d62728"},
        "Meta": {"line.marker_enabled": False, "line.style": "solid", "color": "#9aa0a6"},
        "Limite superior": {
            "line.marker_enabled": False,
            "line.style": "dashed",
            "color": "#c7c7c7",
        },
        "Limite inferior": {
            "line.marker_enabled": False,
            "line.style": "dashed",
            "color": "#c7c7c7",
        },
    },
    "column_settings": {'["name","Variação (%)"]': {"suffix": "%", "decimals": 2}},
}


# ======================================================================================
# SYSTEMIC LAYER — content inside the structure.
# CHARTS are the cards: each is a name, a query, a source, and a calm visualization. A new
# card, a new query, a better label, or a correction is a *systemic* change (see
# CONTRIBUTING.md). Adding a card here does not change how the project is organized.
# Re-exported as `arandu.systemic.CHARTS`.
# ======================================================================================
CHARTS: dict[str, dict[str, Any]] = {
    "institutions_bti_brazil": {
        "name": "Qualidade das instituições no Brasil — Índice de Transformação Bertelsmann (BTI)",
        "display": "line",
        "description": (
            "Pontuações do Brasil no Índice de Transformação Bertelsmann (BTI) ao longo das "
            "edições: o Índice de Status, o Índice de Governança e os critérios Estado "
            "(Stateness), Estado de Direito e Estabilidade das Instituições Democráticas. "
            "Fonte: Bertelsmann Stiftung — BTI (https://bti-project.org), planilha BTI "
            "2006–2026 Scores e relatórios de país. Unidade: pontuação de 1 a 10 (10 = melhor). "
            "Frequência: bienal (uma edição a cada dois anos). Conceito: avaliação qualitativa "
            "por especialistas do grau de transformação rumo à democracia sob o Estado de "
            "Direito e à economia de mercado, e da qualidade da governança; valores "
            "transcritos das edições oficiais."
        ),
        "query": line_query(
            [
                "bti_status_index_brazil",
                "bti_governance_index_brazil",
                "bti_rule_of_law_brazil",
                "bti_stability_democratic_institutions_brazil",
                "bti_stateness_brazil",
            ],
            metric="Pontuação (1–10)",
        ),
        "visualization_settings": {
            **line_settings(
                "Pontuação (1–10)",
                ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e"],
            ),
            "graph.x_axis.scale": "ordinal",
            "graph.x_axis.title_text": "Edição (ano)",
            "graph.y_axis.auto_range": False,
            "graph.y_axis.min": 0,
            "graph.y_axis.max": 10,
            "graph.y_axis.title_text": "Pontuação (1–10)",
            "series_settings": {
                "Índice de Status": {"line.marker_enabled": True, "color": "#1f77b4"},
                "Índice de Governança": {"line.marker_enabled": True, "color": "#d62728"},
                "Estado de Direito": {"line.marker_enabled": True, "color": "#2ca02c"},
                "Estabilidade das Instituições Democráticas": {
                    "line.marker_enabled": True,
                    "color": "#9467bd",
                },
                "Estado (Stateness)": {"line.marker_enabled": True, "color": "#ff7f0e"},
            },
        },
    },
    "institutions_bti_status_governance": {
        "name": "Brasil no BTI — Índice de Status e Índice de Governança por edição",
        "display": "line",
        "description": (
            "Os dois índices agregados do BTI para o Brasil, por edição: o Índice de Status "
            "(nível de transformação alcançado) e o Índice de Governança (capacidade de "
            "condução política da transformação). Fonte: Bertelsmann Stiftung — BTI "
            "(https://bti-project.org), planilha BTI 2006–2026 Scores. Unidade: pontuação de "
            "1 a 10 (10 = melhor). Frequência: bienal. Conceito: avaliação qualitativa por "
            "especialistas; valores transcritos das edições oficiais."
        ),
        "query": line_query(
            ["bti_status_index_brazil", "bti_governance_index_brazil"],
            metric="Pontuação (1–10)",
        ),
        "visualization_settings": {
            **line_settings("Pontuação (1–10)", ["#1f77b4", "#d62728"]),
            "graph.x_axis.scale": "ordinal",
            "graph.x_axis.title_text": "Edição (ano)",
            "graph.y_axis.auto_range": False,
            "graph.y_axis.min": 0,
            "graph.y_axis.max": 10,
            "graph.y_axis.title_text": "Pontuação (1–10)",
            "series_settings": {
                "Índice de Status": {"line.marker_enabled": True, "color": "#1f77b4"},
                "Índice de Governança": {"line.marker_enabled": True, "color": "#d62728"},
            },
        },
    },
    "institutions_bti_democracy_criteria": {
        "name": (
            "Brasil no BTI — Estado, Estado de Direito e Estabilidade das Instituições "
            "Democráticas"
        ),
        "display": "line",
        "description": (
            "Três critérios de transformação política do BTI para o Brasil, por edição: Estado "
            "(Stateness), Estado de Direito e Estabilidade das Instituições Democráticas. "
            "Fonte: Bertelsmann Stiftung — BTI (https://bti-project.org), planilha BTI "
            "2006–2026 Scores e relatórios de país. Unidade: pontuação de 1 a 10 (10 = melhor). "
            "Frequência: bienal. Conceito: avaliação qualitativa por especialistas de cada "
            "critério (média dos subindicadores); valores transcritos das edições oficiais."
        ),
        "query": line_query(
            [
                "bti_stateness_brazil",
                "bti_rule_of_law_brazil",
                "bti_stability_democratic_institutions_brazil",
            ],
            metric="Pontuação (1–10)",
        ),
        "visualization_settings": {
            **line_settings("Pontuação (1–10)", ["#ff7f0e", "#2ca02c", "#9467bd"]),
            "graph.x_axis.scale": "ordinal",
            "graph.x_axis.title_text": "Edição (ano)",
            "graph.y_axis.auto_range": False,
            "graph.y_axis.min": 0,
            "graph.y_axis.max": 10,
            "graph.y_axis.title_text": "Pontuação (1–10)",
            "series_settings": {
                "Estado (Stateness)": {"line.marker_enabled": True, "color": "#ff7f0e"},
                "Estado de Direito": {"line.marker_enabled": True, "color": "#2ca02c"},
                "Estabilidade das Instituições Democráticas": {
                    "line.marker_enabled": True,
                    "color": "#9467bd",
                },
            },
        },
    },
    "overview_selic": {
        "name": "Selic meta",
        "display": "line",
        "description": (
            "Selic meta definida pelo Copom. Fonte: BCB SGS 432. "
            "Unidade: % ao ano. Frequência: diária."
        ),
        "query": line_query(["bcb_sgs_selic_target"], metric="Taxa (% a.a.)"),
        "visualization_settings": line_settings("Taxa (% a.a.)", ["#1f77b4"]),
    },
    "overview_ipca": {
        "name": "IPCA em 12 meses vs meta",
        "display": "line",
        "description": (
            "IPCA acumulado em 12 meses contra a meta de inflação do CMN (centro e banda de "
            "tolerância), que variou ao longo do tempo. Fonte: BCB SGS 13522; metas CMN. "
            "Unidade: %. Frequência: mensal."
        ),
        "query": ipca_target_query(),
        "visualization_settings": IPCA_TARGET_VIZ,
    },
    "overview_exchange": {
        "name": "Câmbio BRL/USD",
        "display": "line",
        "description": (
            "Taxa de câmbio livre, dólar venda. Fonte: BCB SGS 1. "
            "Unidade: R$/US$. Frequência: diária."
        ),
        "query": line_query(["bcb_sgs_usd_brl_sale"], metric="R$/US$"),
        "visualization_settings": line_settings("R$/US$", ["#2ca02c"]),
    },
    "cambio_brl_cny": {
        "name": "Câmbio BRL/CNY",
        "display": "line",
        "description": (
            "Reais por iuan chinês (CNY), taxa de câmbio de referência diária. Fonte: BCE "
            "(taxas de referência), via Frankfurter — o BCB não publica BRL/CNY (a PTAX cobre "
            "só ~10 moedas). Unidade: R$/CNY. Frequência: diária (dias úteis). Conceito: "
            "referência de fechamento do BCE, não a PTAX do BCB."
        ),
        "query": line_query(["ecb_cny_brl"], metric="R$/CNY"),
        "visualization_settings": line_settings("R$/CNY", ["#d62728"]),
    },
    "overview_debt": {
        "name": "Dívida pública",
        "display": "line",
        "description": (
            "DBGG (Dívida Bruta do Governo Geral) e DLSP (Dívida Líquida do Setor Público), "
            "em % do PIB. A DBGG soma todos os passivos do governo geral (União, estados e "
            "municípios); a DLSP desconta os ativos do setor público consolidado (como "
            "reservas internacionais e créditos), por isso é menor. Fonte: BCB SGS. "
            "Unidade: % do PIB. Frequência: mensal."
        ),
        "query": line_query(["bcb_sgs_dbgg_pct_gdp", "bcb_sgs_dlsp_pct_gdp"], metric="% do PIB"),
        "visualization_settings": line_settings("% do PIB", ["#9467bd", "#17becf"]),
    },
    "overview_fiscal_balance": {
        "name": "Resultado primário e nominal NFSP 12m",
        "display": "line",
        "description": (
            "NFSP (Necessidade de Financiamento do Setor Público) do Setor Público "
            "Consolidado, acumulada em 12 meses — quanto o setor público precisa captar "
            "para cobrir seus gastos, apurada pelo lado do financiamento (abaixo da linha). "
            "Fonte: BCB SGS. Unidade: % do PIB. Sinal: + superávit, − déficit "
            "(série original do BCB é deficit-positiva; invertida aqui para padronizar)."
        ),
        "query": line_query(
            ["bcb_sgs_nfsp_primary_12m_pct_gdp", "bcb_sgs_nfsp_nominal_12m_pct_gdp"],
            "analytics.fiscal_pulse_series",
            metric="% do PIB",
            negate=SURPLUS_POSITIVE_FLIP,
        ),
        "visualization_settings": line_settings("% do PIB", ["#2ca02c", "#d62728"]),
    },
    "fiscal_12m": {
        "name": "Resultado NFSP 12m e juros",
        "display": "line",
        "description": (
            "Resultado primário, resultado nominal e juros nominais do Setor Público "
            "Consolidado (NFSP — Necessidade de Financiamento do Setor Público, apurada "
            "abaixo da linha), acumulados em 12 meses. Fonte: BCB SGS. Unidade: % do PIB. "
            "Sinal dos resultados: + superávit, − déficit. Identidade: nominal = primário − juros."
        ),
        "query": line_query(
            [
                "bcb_sgs_nfsp_primary_12m_pct_gdp",
                "bcb_sgs_nfsp_nominal_12m_pct_gdp",
                "bcb_sgs_nfsp_interest_12m_pct_gdp",
            ],
            "analytics.fiscal_pulse_series",
            metric="% do PIB",
            negate=SURPLUS_POSITIVE_FLIP,
        ),
        "visualization_settings": line_settings("% do PIB", ["#2ca02c", "#d62728", "#ff7f0e"]),
    },
    "fiscal_primary_deficit_12m": {
        "name": "Resultado primário NFSP 12m",
        "display": "line",
        "description": (
            "NFSP primária (Necessidade de Financiamento do Setor Público) do Setor "
            "Público Consolidado, acumulada em 12 meses — apurada pelo lado do "
            "financiamento (abaixo da linha). "
            "Fonte: BCB SGS 5793. Unidade: % do PIB. Sinal: + superávit, − déficit."
        ),
        "query": line_query(
            ["bcb_sgs_nfsp_primary_12m_pct_gdp"],
            "analytics.fiscal_pulse_series",
            metric="% do PIB",
            negate=SURPLUS_POSITIVE_FLIP,
        ),
        "visualization_settings": line_settings("% do PIB", ["#2ca02c"]),
    },
    "fiscal_nominal_deficit_12m": {
        "name": "Resultado nominal NFSP 12m",
        "display": "line",
        "description": (
            "NFSP nominal (Necessidade de Financiamento do Setor Público) do Setor "
            "Público Consolidado, acumulada em 12 meses — apurada pelo lado do "
            "financiamento (abaixo da linha). "
            "Fonte: BCB SGS 5727. Unidade: % do PIB. Sinal: + superávit, − déficit."
        ),
        "query": line_query(
            ["bcb_sgs_nfsp_nominal_12m_pct_gdp"],
            "analytics.fiscal_pulse_series",
            metric="% do PIB",
            negate=SURPLUS_POSITIVE_FLIP,
        ),
        "visualization_settings": line_settings("% do PIB", ["#d62728"]),
    },
    "fiscal_interest_12m": {
        "name": "Juros nominais NFSP 12m",
        "display": "line",
        "description": (
            "Juros nominais do Setor Público Consolidado (componente da NFSP — "
            "Necessidade de Financiamento do Setor Público, apurada abaixo da linha), "
            "acumulados em 12 meses. Fonte: BCB SGS 5760. Unidade: % do PIB."
        ),
        "query": line_query(
            ["bcb_sgs_nfsp_interest_12m_pct_gdp"],
            "analytics.fiscal_pulse_series",
            metric="% do PIB",
        ),
        "visualization_settings": line_settings("% do PIB", ["#ff7f0e"]),
    },
    "fiscal_monthly_primary": {
        "name": "Resultado primário NFSP mensal",
        "display": "bar",
        "description": (
            "NFSP primária (Necessidade de Financiamento do Setor Público) mensal do "
            "Setor Público Consolidado — apurada pelo lado do financiamento (abaixo da "
            "linha). Fonte: BCB SGS. "
            "Unidade: R$ milhões nominais. Sinal: + superávit, − déficit."
        ),
        "query": line_query(
            ["bcb_sgs_nfsp_primary_monthly_brl"],
            "analytics.fiscal_pulse_series",
            metric="R$ milhões",
            negate=SURPLUS_POSITIVE_FLIP,
        ),
        "visualization_settings": time_bar_settings("R$ milhões", ["#2ca02c"]),
    },
    "fiscal_monthly_nominal": {
        "name": "Resultado nominal NFSP mensal",
        "display": "bar",
        "description": (
            "NFSP nominal (Necessidade de Financiamento do Setor Público) mensal do "
            "Setor Público Consolidado — apurada pelo lado do financiamento (abaixo da "
            "linha). Fonte: BCB SGS. "
            "Unidade: R$ milhões nominais. Sinal: + superávit, − déficit."
        ),
        "query": line_query(
            ["bcb_sgs_nfsp_nominal_monthly_brl"],
            "analytics.fiscal_pulse_series",
            metric="R$ milhões",
            negate=SURPLUS_POSITIVE_FLIP,
        ),
        "visualization_settings": time_bar_settings("R$ milhões", ["#d62728"]),
    },
    "fiscal_monthly_interest": {
        "name": "Juros nominais mensais",
        "display": "bar",
        "description": (
            "Juros nominais mensais do Setor Público Consolidado. "
            "Fonte: BCB SGS. Unidade: R$ milhões nominais."
        ),
        "query": line_query(
            ["bcb_sgs_nfsp_interest_monthly_brl"],
            "analytics.fiscal_pulse_series",
            metric="R$ milhões",
        ),
        "visualization_settings": time_bar_settings("R$ milhões", ["#ff7f0e"]),
    },
    "fiscal_monthly_components": {
        "name": "Resultados e juros NFSP mensais",
        "display": "bar",
        "description": (
            "Resultado primário, resultado nominal e juros nominais mensais do Setor Público "
            "Consolidado (NFSP — Necessidade de Financiamento do Setor Público, apurada "
            "abaixo da linha). Fonte: BCB SGS. Unidade: R$ milhões nominais. "
            "Sinal dos resultados: + superávit, − déficit."
        ),
        "query": line_query(
            [
                "bcb_sgs_nfsp_primary_monthly_brl",
                "bcb_sgs_nfsp_nominal_monthly_brl",
                "bcb_sgs_nfsp_interest_monthly_brl",
            ],
            "analytics.fiscal_pulse_series",
            metric="R$ milhões",
            negate=SURPLUS_POSITIVE_FLIP,
        ),
        "visualization_settings": time_bar_settings(
            "R$ milhões",
            ["#2ca02c", "#d62728", "#ff7f0e"],
        ),
    },
    "fiscal_debt": {
        "name": "Dívida pública",
        "display": "line",
        "description": (
            "DBGG (Dívida Bruta do Governo Geral) e DLSP (Dívida Líquida do Setor Público) "
            "como estoques, em % do PIB. A DBGG soma os passivos do governo geral; a DLSP "
            "desconta os ativos do setor público consolidado (por isso é menor). "
            "Fonte: BCB SGS. Unidade: % do PIB."
        ),
        "query": line_query(
            ["bcb_sgs_dbgg_pct_gdp", "bcb_sgs_dlsp_pct_gdp"],
            "analytics.fiscal_pulse_series",
            metric="% do PIB",
        ),
        "visualization_settings": line_settings("% do PIB", ["#9467bd", "#17becf"]),
    },
    "debt_stock": {
        "name": "DBGG e DLSP",
        "display": "line",
        "description": (
            "DBGG (Dívida Bruta do Governo Geral) e DLSP (Dívida Líquida do Setor Público), "
            "em % do PIB. A DBGG soma os passivos do governo geral; a DLSP desconta os ativos "
            "do setor público consolidado (por isso é menor). Fonte: BCB SGS. Unidade: % do PIB."
        ),
        "query": line_query(
            ["bcb_sgs_dbgg_pct_gdp", "bcb_sgs_dlsp_pct_gdp"],
            "analytics.fiscal_pulse_series",
            metric="% do PIB",
        ),
        "visualization_settings": line_settings("% do PIB", ["#9467bd", "#17becf"]),
    },
    "debt_dbgg": {
        "name": "DBGG",
        "display": "line",
        "description": "Dívida Bruta do Governo Geral. Fonte: BCB SGS 13762. Unidade: % do PIB.",
        "query": line_query(
            ["bcb_sgs_dbgg_pct_gdp"],
            "analytics.fiscal_pulse_series",
            metric="% do PIB",
        ),
        "visualization_settings": line_settings("% do PIB", ["#9467bd"]),
    },
    "debt_dlsp": {
        "name": "DLSP",
        "display": "line",
        "description": "Dívida Líquida do Setor Público. Fonte: BCB SGS 4513. Unidade: % do PIB.",
        "query": line_query(
            ["bcb_sgs_dlsp_pct_gdp"],
            "analytics.fiscal_pulse_series",
            metric="% do PIB",
        ),
        "visualization_settings": line_settings("% do PIB", ["#17becf"]),
    },
    "monetary_selic": {
        "name": "Selic meta",
        "display": "line",
        "description": "Selic meta definida pelo Copom. Fonte: BCB SGS 432. Unidade: % ao ano.",
        "query": line_query(["bcb_sgs_selic_target"], metric="Taxa (% a.a.)"),
        "visualization_settings": line_settings("Taxa (% a.a.)", ["#1f77b4"]),
    },
    "monetary_ipca_12m": {
        "name": "IPCA em 12 meses vs meta",
        "display": "line",
        "description": (
            "IPCA acumulado em 12 meses contra a meta de inflação do CMN (centro e banda "
            "de tolerância), que variou ao longo do tempo. Fonte: BCB SGS 13522; metas CMN. "
            "Unidade: %."
        ),
        "query": ipca_target_query(),
        "visualization_settings": IPCA_TARGET_VIZ,
    },
    "monetary_ipca_monthly": {
        "name": "IPCA mensal",
        "display": "bar",
        "description": "Variação mensal do IPCA. Fonte: BCB SGS 433. Unidade: % ao mês.",
        "query": line_query(["bcb_sgs_ipca_monthly"], metric="Variação (%)"),
        "visualization_settings": time_bar_settings("Variação (%)", ["#ff7f0e"]),
    },
    "monetary_exchange": {
        "name": "Câmbio BRL/USD",
        "display": "line",
        "description": "Taxa de câmbio livre, dólar venda. Fonte: BCB SGS 1. Unidade: R$/US$.",
        "query": line_query(["bcb_sgs_usd_brl_sale"], metric="R$/US$"),
        "visualization_settings": line_settings("R$/US$", ["#2ca02c"]),
    },
    "monetary_ibc": {
        "name": "IBC-Br",
        "display": "line",
        "description": (
            "Índice de Atividade Econômica do Banco Central, com ajuste sazonal. "
            "Fonte: BCB SGS 24364. Unidade: índice."
        ),
        "query": line_query(["bcb_sgs_ibc_br_sa"], metric="Índice"),
        "visualization_settings": line_settings("Índice", ["#9467bd"]),
    },
    "activity_pib_nominal": {
        "name": "PIB mensal nominal",
        "display": "line",
        "description": (
            "PIB mensal em valores correntes estimado pelo Banco Central. "
            "Fonte: BCB SGS 4380. Unidade: R$ milhões nominais. Frequência: mensal."
        ),
        "query": line_query(["bcb_sgs_pib_monthly_brl"], metric="R$ milhões"),
        "visualization_settings": line_settings("R$ milhões", ["#8c564b"]),
    },
    "labor_unemployment": {
        "name": "Taxa de desocupação",
        "display": "line",
        "description": (
            "Taxa de desocupação das pessoas de 14 anos ou mais. "
            "Fonte: IBGE SIDRA/PNAD Contínua, tabela 6381, variável 4099. "
            "Unidade: %. Frequência: trimestre móvel com divulgação mensal."
        ),
        "query": line_query(
            ["ibge_pnad_unemployment_rate"],
            "analytics.labor_income_series",
            metric="Taxa (%)",
        ),
        "visualization_settings": line_settings("Taxa (%)", ["#2ca02c"]),
    },
    "labor_real_average_income": {
        "name": "Rendimento real médio",
        "display": "line",
        "description": (
            "Rendimento médio mensal real habitual de todos os trabalhos. "
            "Fonte: IBGE SIDRA/PNAD Contínua, tabela 6390, variável 5933. "
            "Unidade: R$ reais. Frequência: trimestre móvel com divulgação mensal."
        ),
        "query": line_query(
            ["ibge_pnad_real_average_income"],
            "analytics.labor_income_series",
            metric="R$ reais",
        ),
        "visualization_settings": line_settings("R$ reais", ["#1f77b4"]),
    },
    "labor_real_income_mass": {
        "name": "Massa real de rendimentos",
        "display": "line",
        "description": (
            "Massa de rendimento mensal real habitual de todos os trabalhos. "
            "Fonte: IBGE SIDRA/PNAD Contínua, tabela 6392, variável 6293. "
            "Unidade: R$ milhões reais. Frequência: trimestre móvel com divulgação mensal."
        ),
        "query": line_query(
            ["ibge_pnad_real_labor_income_mass"],
            "analytics.labor_income_series",
            metric="R$ milhões reais",
        ),
        "visualization_settings": line_settings("R$ milhões reais", ["#9467bd"]),
    },
    "central_revenue_spending": {
        "name": "Receita líquida e despesa total (acumulado 12m)",
        "display": "line",
        "description": (
            "Receita líquida e despesa total do Governo Central, acumuladas em 12 meses "
            "para remover a forte sazonalidade mensal — assim o espaço entre as linhas "
            "(o resultado primário) fica legível. Fonte: Tesouro Nacional RTN. "
            "Unidade: R$ milhões nominais, acumulado em 12 meses."
        ),
        "query": f"""
with d as (
  select
    date,
    series_id,
    sum(value) over (
      partition by series_id order by date rows between 11 preceding and current row
    ) as v12,
    count(*) over (
      partition by series_id order by date rows between 11 preceding and current row
    ) as n
  from analytics.observations_enriched
  where series_id in ('tesouro_rtn_receita_liquida', 'tesouro_rtn_despesa_total')
)
select
  date as "Data",
  case series_id
    when 'tesouro_rtn_receita_liquida' then 'Receita líquida'
    when 'tesouro_rtn_despesa_total' then 'Despesa total'
  end as "Série",
  v12 as "R$ milhões (12m)"
from d
where n = 12
  {_periodo_filter_sql("date")}
order by "Data", "Série"
""".strip(),
        "visualization_settings": {
            **line_settings("R$ milhões (12m)", ["#d62728", "#2ca02c"]),
            "series_settings": {
                "Receita líquida": {"line.marker_enabled": False},
                "Despesa total": {"line.marker_enabled": False},
            },
        },
    },
    "central_primary_components": {
        "name": "Resultado primário do Governo Central e componentes",
        "display": "line",
        "description": (
            "Resultado primário do Governo Central e seus componentes Tesouro Nacional e "
            "Previdência Social. Fonte: Tesouro Nacional RTN. Unidade: R$ milhões nominais. "
            "Sinal: + superávit, − déficit. (O resultado do Banco Central, ~mil vezes menor, "
            "foi omitido por ser ilegível nesta escala.)"
        ),
        "query": line_query(
            [
                "tesouro_rtn_resultado_primario_gc",
                "tesouro_rtn_resultado_primario_tesouro",
                "tesouro_rtn_resultado_previdencia",
            ],
            "analytics.governo_central_series",
            metric="R$ milhões",
        ),
        "visualization_settings": line_settings(
            "R$ milhões",
            ["#1f77b4", "#2ca02c", "#d62728"],
        ),
    },
    "central_primary_pct_gdp": {
        "name": "Resultado primário do Governo Central (% do PIB, 12m)",
        "display": "line",
        "description": (
            "Resultado primário do Governo Central acumulado em 12 meses dividido pelo PIB "
            "nominal acumulado em 12 meses. Fonte: Tesouro Nacional (RTN) e Banco Central "
            "(PIB mensal, SGS 4380). Unidade: % do PIB. Frequência: mensal, acumulado 12m. "
            "Conceito: resultado primário acima da linha do Governo Central — não confundir "
            "com a NFSP (Necessidade de Financiamento do Setor Público) abaixo da linha do "
            "Setor Público Consolidado. "
            "Sinal: + superávit, - déficit. Última informação disponível conforme RTN."
        ),
        "query": f"""
with p as (
  select
    date,
    sum(value) over (order by date rows between 11 preceding and current row) as acc12,
    count(*) over (order by date rows between 11 preceding and current row) as n
  from analytics.observations_enriched
  where series_id = 'tesouro_rtn_resultado_primario_gc'
),
g as (
  select
    date,
    sum(value) over (order by date rows between 11 preceding and current row) as gdp12,
    count(*) over (order by date rows between 11 preceding and current row) as n
  from analytics.observations_enriched
  where series_id = 'bcb_sgs_pib_monthly_brl'
)
select
  p.date as "Data",
  'Resultado primário GC (% PIB, 12m)' as "Série",
  round(100.0 * p.acc12 / nullif(g.gdp12, 0), 2) as "% do PIB"
from p
join g on g.date = p.date
where p.n = 12 and g.n = 12
  {_periodo_filter_sql("p.date")}
order by "Data"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data"],
            "graph.metrics": ["% do PIB"],
            "graph.colors": ["#1f77b4"],
            "graph.x_axis.title_text": "Data",
            "graph.y_axis.title_text": "% do PIB",
            "graph.show_legend": False,
            "graph.show_goal": True,
            "graph.goal_value": 0,
            "graph.goal_label": "Equilíbrio (0% do PIB)",
            "series_settings": {
                "Resultado primário GC (% PIB, 12m)": {"line.marker_enabled": False}
            },
            "column_settings": {'["name","% do PIB"]': {"suffix": "%", "decimals": 1}},
        },
    },
    "central_spending_composition": {
        "name": "Composição da despesa primária (participação no total, 12m)",
        "display": "area",
        "description": (
            "Participação de cada categoria na despesa primária total do Governo Central, "
            "acumulada em 12 meses. Fonte: Tesouro Nacional (RTN). Unidade: % da despesa "
            "primária total (área 100% empilhada). Frequência: mensal, acumulado 12m. "
            "Conceito: despesa acima da linha do Governo Central; Demais = despesa total "
            "menos previdência, pessoal e outras obrigatórias."
        ),
        "query": f"""
with d as (
  select
    date,
    series_id,
    sum(value) over (
      partition by series_id order by date rows between 11 preceding and current row
    ) as v12,
    count(*) over (
      partition by series_id order by date rows between 11 preceding and current row
    ) as n
  from analytics.observations_enriched
  where series_id in (
    'tesouro_rtn_beneficios_previdenciarios',
    'tesouro_rtn_pessoal_encargos',
    'tesouro_rtn_outras_obrigatorias',
    'tesouro_rtn_despesa_total'
  )
),
w as (
  select
    date,
    min(n) as n,
    max(v12) filter (where series_id = 'tesouro_rtn_beneficios_previdenciarios') as prev,
    max(v12) filter (where series_id = 'tesouro_rtn_pessoal_encargos') as pess,
    max(v12) filter (where series_id = 'tesouro_rtn_outras_obrigatorias') as outras,
    max(v12) filter (where series_id = 'tesouro_rtn_despesa_total') as total
  from d
  group by date
)
select s."Data", s."Série", s."R$ milhões (12m)"
from (
  select date as "Data", n, total, 'Previdência' as "Série", prev as "R$ milhões (12m)" from w
  union all select date, n, total, 'Pessoal e encargos', pess from w
  union all select date, n, total, 'Outras obrigatórias', outras from w
  union all select date, n, total, 'Demais',
    greatest(total - coalesce(prev, 0) - coalesce(pess, 0) - coalesce(outras, 0), 0) from w
) s
where s.n = 12 and s.total is not null
  {_periodo_filter_sql('s."Data"')}
order by s."Data", s."Série"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data", "Série"],
            "graph.metrics": ["R$ milhões (12m)"],
            "graph.x_axis.title_text": "Data",
            "graph.y_axis.title_text": "% da despesa total",
            "stackable.stack_type": "normalized",
            # Color by meaning: the catch-all "Demais" is the muted gray, real categories saturated.
            "series_settings": {
                "Previdência": {"color": "#1f77b4"},
                "Pessoal e encargos": {"color": "#9467bd"},
                "Outras obrigatórias": {"color": "#ff7f0e"},
                "Demais": {"color": "#c7c7c7"},
            },
        },
    },
    "central_revenues": {
        "name": "Fontes de receita do Governo Central (acumulado 12m)",
        "display": "line",
        "description": (
            "Principais fluxos de receita do Governo Central, acumulados em 12 meses para "
            "remover a sazonalidade: receita administrada pela RFB, arrecadação líquida do "
            "RGPS e transferências por repartição (estados/municípios). Fonte: Tesouro "
            "Nacional RTN. Unidade: R$ milhões nominais, acumulado 12m. Não inclui os "
            "agregados Receita total/líquida (vistos em outro painel)."
        ),
        "query": f"""
with d as (
  select
    date,
    series_id,
    sum(value) over (
      partition by series_id order by date rows between 11 preceding and current row
    ) as v12,
    count(*) over (
      partition by series_id order by date rows between 11 preceding and current row
    ) as n
  from analytics.observations_enriched
  where series_id in (
    'tesouro_rtn_receita_administrada_rfb',
    'tesouro_rtn_arrecadacao_rgps',
    'tesouro_rtn_transferencias_reparticao'
  )
)
select
  date as "Data",
  case series_id
    when 'tesouro_rtn_receita_administrada_rfb' then 'Receita administrada RFB'
    when 'tesouro_rtn_arrecadacao_rgps' then 'Arrecadação RGPS'
    when 'tesouro_rtn_transferencias_reparticao' then 'Transferências'
  end as "Série",
  v12 as "R$ milhões (12m)"
from d
where n = 12
  {_periodo_filter_sql("date")}
order by "Data", "Série"
""".strip(),
        "visualization_settings": {
            **line_settings("R$ milhões (12m)", ["#1f77b4", "#2ca02c", "#ff7f0e"]),
            "series_settings": {
                "Receita administrada RFB": {"line.marker_enabled": False},
                "Arrecadação RGPS": {"line.marker_enabled": False},
                "Transferências": {"line.marker_enabled": False},
            },
        },
    },
    "central_social_security": {
        "name": "Previdência: arrecadação e benefícios",
        "display": "line",
        "description": (
            "Arrecadação líquida do RGPS e benefícios previdenciários no Governo Central. "
            "Fonte: Tesouro Nacional RTN. Unidade: R$ milhões nominais."
        ),
        "query": line_query(
            ["tesouro_rtn_arrecadacao_rgps", "tesouro_rtn_beneficios_previdenciarios"],
            "analytics.governo_central_series",
            metric="R$ milhões",
        ),
        "visualization_settings": line_settings("R$ milhões", ["#2ca02c", "#d62728"]),
    },
    "budget_latest": {
        "name": "Despesa por categoria",
        "display": "bar",
        "description": (
            "Categorias selecionadas de despesa do RTN. Fonte: Tesouro Nacional. "
            "Unidade: R$ milhões nominais. Frequência: mensal."
        ),
        "query": """
select
  case series_id
    when 'tesouro_rtn_beneficios_previdenciarios' then 'Benefícios previdenciários'
    when 'tesouro_rtn_pessoal_encargos' then 'Pessoal e encargos'
    when 'tesouro_rtn_outras_obrigatorias' then 'Outras obrigatórias'
    else name
  end as "Categoria",
  round(latest_value, 2) as "R$ milhões"
from analytics.series_latest
where series_id in (
  'tesouro_rtn_beneficios_previdenciarios',
  'tesouro_rtn_pessoal_encargos',
  'tesouro_rtn_outras_obrigatorias'
)
order by "R$ milhões" desc
""".strip(),
        "visualization_settings": bar_settings(
            "R$ milhões",
            ["#1f77b4", "#ff7f0e", "#2ca02c"],
        ),
    },
    "budget_trend": {
        "name": "Tendência de despesas",
        "display": "line",
        "description": (
            "Tendência mensal de categorias selecionadas de despesa. "
            "Fonte: Tesouro Nacional RTN. Unidade: R$ milhões nominais."
        ),
        "query": line_query(
            [
                "tesouro_rtn_beneficios_previdenciarios",
                "tesouro_rtn_pessoal_encargos",
                "tesouro_rtn_outras_obrigatorias",
            ],
            "analytics.federal_budget_series",
            metric="R$ milhões",
        ),
        "visualization_settings": line_settings("R$ milhões"),
    },
    "social_household_debt": {
        "name": "Endividamento das famílias",
        "display": "line",
        "description": (
            "Endividamento das famílias com o SFN sobre a renda acumulada em 12 meses, "
            "com e sem crédito habitacional. Fonte: BCB SGS 29037 e 29038. "
            "Unidade: % da renda. Frequência: mensal."
        ),
        "query": line_query(
            [
                "bcb_sgs_endividamento_familias",
                "bcb_sgs_endividamento_familias_ex_hab",
            ],
            metric="% da renda (12m)",
        ),
        "visualization_settings": line_settings("% da renda (12m)", ["#1f77b4", "#9467bd"]),
    },
    "social_default_rate": {
        "name": "Inadimplência do crédito",
        "display": "line",
        "description": (
            "Inadimplência da carteira de crédito do SFN (atrasos > 90 dias), total e "
            "pessoas físicas. Fonte: BCB SGS 21082 e 21084. "
            "Unidade: % da carteira. Frequência: mensal."
        ),
        "query": line_query(
            ["bcb_sgs_inadimplencia_total", "bcb_sgs_inadimplencia_pf"],
            metric="% da carteira",
        ),
        "visualization_settings": line_settings("% da carteira", ["#7f7f7f", "#d62728"]),
    },
    "social_food_inflation": {
        "name": "Inflação de alimentos (IPCA)",
        "display": "bar",
        "description": (
            "IPCA do grupo Alimentação e bebidas, variação mensal. Proxy de pressão de "
            "preços de alimentos sobre as famílias — não mede insegurança alimentar. "
            "Fonte: BCB SGS 1635. Unidade: % no mês. Frequência: mensal."
        ),
        "query": line_query(["bcb_sgs_ipca_alimentacao"], metric="Variação (% no mês)"),
        "visualization_settings": time_bar_settings("Variação (% no mês)", ["#bcbd22"]),
    },
    # --- Apostas (bets) ---
    "bets_market_growth": {
        "name": "Crescimento do mercado de apostas no Brasil (GGR)",
        "display": "bar",
        "description": (
            "Receita bruta de jogo (GGR) do mercado de apostas no Brasil em dois retratos: "
            "2022, antes da regulamentação (estimativa da Entain de US$ 1,5 bi, ~R$ 7,7 bi ao "
            "câmbio médio de 2022), e 2025, primeiro ano do mercado regulado (R$ 36,96 bi, GGR "
            "oficial da SPA/MF). As duas pontas têm origens distintas — 2022 é estimativa de "
            "operadora para o mercado não regulado e 2025 é dado oficial da SPA — então a "
            "comparação indica a ordem de grandeza do crescimento, não um número exato. Fontes: "
            "Entain (2022, via Infomoney) e SPA/MF, 2º Panorama jan/2026 (2025). Unidade: R$ "
            "bilhões (GGR). Frequência: dois retratos anuais (não é série temporal). Conceito: "
            "GGR = receita bruta de jogo (valor apostado menos prêmios pagos)."
        ),
        "query": """
select
  case series_id
    when 'bets_market_2022_est' then '2022 (estimativa, não regulado)'
    when 'spa_ggr_ano_2025' then '2025 (oficial, regulado)'
  end as "Ano",
  value as "R$ bilhões"
from analytics.observations_enriched
where series_id in ('bets_market_2022_est', 'spa_ggr_ano_2025')
order by "Ano"
""".strip(),
        "visualization_settings": {
            **bar_settings("R$ bilhões", [BETS_GOLD]),
            "graph.dimensions": ["Ano"],
            "graph.x_axis.scale": "ordinal",
            "graph.x_axis.title_text": "",
            "graph.show_legend": False,
            "column_settings": {'["name","R$ bilhões"]': {"decimals": 1}},
        },
    },
    "bets_tax_revenue": {
        "name": "Arrecadação federal do setor de jogos e apostas (CNAE 92), por ano",
        "display": "line",
        "description": (
            "Tributo federal arrecadado pela Receita Federal junto à divisão econômica 92 da "
            "CNAE (“Atividades de exploração de jogos de azar e apostas”), por ano, de 2016 a "
            "2025. De 2016 a 2024 a arrecadação ficou entre R$ 2 milhões e R$ 106 milhões por "
            "ano; em 2025, primeiro ano de tributação do mercado regulado de apostas de quota "
            "fixa, chegou a cerca de R$ 10,0 bilhões. O eixo Y está em escala logarítmica para "
            "mostrar todos os anos apesar da diferença de ordem de grandeza. Fonte: Receita "
            "Federal — Arrecadação por Divisão Econômica da CNAE (dados abertos, planilha XLSX), "
            "divisão 92. Unidade: R$ milhões nominais (escala log). Frequência: anual (a RFB "
            "não publica série mensal por divisão da CNAE em formato aberto e estável). "
            "Conceito: tributo federal pago pelas empresas do setor — não é o GGR (receita "
            "bruta de jogo) nem o volume apostado."
        ),
        "query": line_query(["rfb_cnae_apostas_arrecadacao"], metric="R$ milhões"),
        "visualization_settings": {
            **line_settings("R$ milhões", [BETS_BROWN]),
            "graph.dimensions": ["Data"],
            "graph.x_axis.scale": "ordinal",
            "graph.y_axis.scale": "log",
            "graph.show_legend": False,
            "series_settings": {
                "Arrecadação federal (CNAE 92)": {
                    "color": BETS_BROWN,
                    "line.marker_enabled": True,
                },
            },
            "column_settings": {'["name","R$ milhões"]': {"decimals": 0}},
        },
    },
    "bets_pix_estimate": {
        "name": "Estimativa BCB: movimentação via Pix, apostas vs loterias (ago/2024)",
        "display": "bar",
        "description": (
            "Estimativa pontual do Banco Central (Estudo Especial 119, 2024) para a média "
            "mensal de 2024 dos valores movimentados, em R$ bilhões: loterias da Caixa "
            "(R$ 1,9 bi), empresas de apostas registradas no CNAE 92 (R$ 0,3 bi) e empresas "
            "de apostas que não se classificam no CNAE 92 (R$ 20,8 bi) — estas últimas "
            "concentram a maior parte das transferências Pix recebidas pelo setor. O BCB "
            "estima que cerca de 15% do valor apostado é retido pelas casas (o restante "
            "retorna como prêmio). Fonte: BCB, Estudo Especial 119 — “Análise técnica sobre o "
            "mercado de apostas online no Brasil e o perfil dos apostadores”, tabela "
            "comparativa, dados de agosto de 2024. Unidade: R$ bilhões (média mensal de 2024). "
            "Frequência: estimativa pontual — NÃO é série temporal e não é atualizada pela "
            "rotina diária. Conceito: recebimentos brutos estimados via Pix (proxy do volume "
            "apostado), distinto do GGR e do tributo arrecadado."
        ),
        "query": """
select
  case series_id
    when 'bets_bcb_pix_loterias_ago2024' then 'Loterias'
    when 'bets_bcb_pix_cnae92_ago2024' then 'Apostas — empresas no CNAE 92'
    when 'bets_bcb_pix_outros_ago2024' then 'Apostas — empresas fora do CNAE 92'
  end as "Categoria",
  value as "R$ bilhões"
from analytics.observations_enriched
where series_id in (
    'bets_bcb_pix_loterias_ago2024',
    'bets_bcb_pix_cnae92_ago2024',
    'bets_bcb_pix_outros_ago2024'
  )
order by value desc
""".strip(),
        "visualization_settings": {
            **bar_settings("R$ bilhões", [BETS_BROWN]),
            "graph.show_legend": False,
            "column_settings": {'["name","R$ bilhões"]': {"decimals": 1}},
        },
    },
    "bets_spa_market": {
        "name": "Mercado regulado de apostas de quota fixa (2025)",
        "display": "bar",
        "description": (
            "Tamanho do mercado regulado de apostas de quota fixa em 2025, em R$ bilhões: GGR "
            "(receita bruta de jogo) do 1º semestre (R$ 17,4 bi) e do ano (R$ 36,96 bi; exato "
            "R$ 36.959.783.379,70), e as destinações legais de 12% no ano (R$ 4,53 bi; exato "
            "R$ 4.532.797.794,92). No 1º semestre 17,7 milhões de CPFs únicos apostaram, "
            "chegando a 25,2 milhões no ano. Fonte: SPA/MF — 1º Panorama Semestral (ago/2025) "
            "e 2º Panorama (jan/2026), "
            "https://www.gov.br/fazenda/pt-br/composicao/orgaos/secretaria-de-premios-e-apostas. "
            "Unidade: R$ bilhões. Frequência: retratos acumulados de período (não série "
            "temporal; a SPA publica apenas apresentações em PDF). Conceito: GGR é a receita "
            "bruta de jogo (apostas menos prêmios pagos); destinações são a parcela legal de "
            "12%."
        ),
        "query": """
select
  case series_id
    when 'spa_ggr_h1_2025' then 'GGR — 1º semestre 2025'
    when 'spa_ggr_ano_2025' then 'GGR — ano 2025'
    when 'spa_destinacoes_ano_2025' then 'Destinações legais (12%) — ano 2025'
  end as "Categoria",
  value as "R$ bilhões"
from analytics.observations_enriched
where series_id in (
    'spa_ggr_h1_2025',
    'spa_ggr_ano_2025',
    'spa_destinacoes_ano_2025'
  )
order by value desc
""".strip(),
        "visualization_settings": {
            **bar_settings("R$ bilhões", [BETS_GOLD]),
            "graph.show_legend": False,
            "column_settings": {'["name","R$ bilhões"]': {"decimals": 1}},
        },
    },
    "bets_spa_accounts_funnel": {
        "name": "Apostadores únicos vs. contas ativas (2025)",
        "display": "bar",
        "description": (
            "Comparação entre contas ativas e pessoas físicas distintas no mercado regulado de "
            "apostas em 2025: 100.775.427 contas ativas nas marcas/bets, 87.671.439 contas "
            "ativas em operadores/empresas e 25.245.319 CPFs únicos que apostaram. Há, "
            "portanto, muito mais contas do que apostadores — em média várias contas por "
            "pessoa. Fonte: SPA/MF — 2º Panorama (jan/2026), "
            "https://www.gov.br/fazenda/pt-br/composicao/orgaos/secretaria-de-premios-e-apostas. "
            "Unidade: contagem. Frequência: retrato acumulado do ano (não série temporal). "
            "Conceito: contas ativas (por marca e por operador) vs. CPFs únicos (pessoas "
            "físicas distintas)."
        ),
        "query": """
select
  case series_id
    when 'spa_contas_marcas_2025' then 'Contas ativas nas marcas/bets'
    when 'spa_contas_operadores_2025' then 'Contas ativas em operadores'
    when 'spa_cpfs_unicos_2025' then 'CPFs únicos que apostaram'
  end as "Categoria",
  value as "Contagem"
from analytics.observations_enriched
where series_id in (
    'spa_contas_marcas_2025',
    'spa_contas_operadores_2025',
    'spa_cpfs_unicos_2025'
  )
order by value desc
""".strip(),
        "visualization_settings": {
            **bar_settings("Contagem", [BETS_DEEP]),
            "graph.show_legend": False,
            "column_settings": {'["name","Contagem"]': {"decimals": 0}},
        },
    },
    "bets_pbf": {
        "name": "Beneficiários do Bolsa Família e apostas (estimativa BCB, ago/2024)",
        "display": "bar",
        "description": (
            "Estimativa pontual do Banco Central (Estudo Especial 119, 2024) para agosto de "
            "2024: 5 milhões de beneficiários do Bolsa Família enviaram R$ 3 bilhões via Pix a "
            "empresas de apostas (mediana de R$ 100 por pessoa); destes, 4 milhões (70%) são "
            "chefes de família — quem de fato recebe o benefício — e enviaram R$ 2 bilhões "
            "(67% do total). Cerca de 17% dos cadastrados no PBF (base dez/2023) apostaram no "
            "período. O gráfico mostra, lado a lado, as pessoas (em milhões) e o valor enviado "
            "(em R$ bilhões), para o total e para os chefes de família. Fonte: BCB, Estudo "
            "Especial 119 — “Análise técnica sobre o mercado de apostas online no Brasil e o "
            "perfil dos apostadores” (bcb.gov.br), dados de agosto de 2024. "
            "Unidade: milhões de pessoas e R$ bilhões. Frequência: estimativa pontual de "
            "ago/2024 (não atualizada pela rotina diária). Conceito: estimativa via Pix do "
            "BCB; descreve o perfil dos apostadores, sem afirmar relação de causa e efeito."
        ),
        "query": """
select
  case
    when series_id like '%total%' then 'Beneficiários do PBF (total)'
    else 'Chefes de família (recebem o benefício)'
  end as "Categoria",
  case
    when series_id like 'bets_pbf_pessoas%' then 'Pessoas (milhões)'
    else 'Valor via Pix (R$ bilhões)'
  end as "Série",
  value as "Valor"
from analytics.observations_enriched
where series_id in (
    'bets_pbf_pessoas_total_ago2024',
    'bets_pbf_pessoas_chefes_ago2024',
    'bets_pbf_valor_total_ago2024',
    'bets_pbf_valor_chefes_ago2024'
  )
order by "Categoria" desc, "Série"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Categoria", "Série"],
            "graph.metrics": ["Valor"],
            "graph.colors": [BETS_GOLD, BETS_GRAY],
            "graph.x_axis.title_text": "Categoria",
            "graph.y_axis.title_text": "Pessoas (mi) / Valor (R$ bi)",
            "graph.show_legend": True,
            "column_settings": {'["name","Valor"]': {"decimals": 0}},
        },
    },
    "bets_lei_allocation": {
        "name": "Destinação legal da arrecadação das apostas (Lei 14.790/2023)",
        "display": "pie",
        "description": (
            "Como a lei reparte a parcela da arrecadação das apostas de quota fixa destinada a "
            "políticas públicas, por área (% da fatia destinada): esporte 36%, turismo 28%, "
            "segurança pública 13,6%, educação 10%, seguridade social 10%, saúde 1%, sociedade "
            "civil 0,5%, Funapol/Polícia Federal 0,5% e ABDI 0,4% (soma 100%). Fonte: Lei nº "
            "14.790/2023, Art. 30, "
            "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14790.htm. "
            "Unidade: % da arrecadação destinada. Frequência: estrutura legal (não série "
            "temporal, não execução efetiva). Conceito: alocação estatutária prevista em lei."
        ),
        "query": """
select
  case series_id
    when 'lei14790_dest_esporte' then 'Esporte'
    when 'lei14790_dest_turismo' then 'Turismo'
    when 'lei14790_dest_seguranca' then 'Segurança pública'
    when 'lei14790_dest_educacao' then 'Educação'
    when 'lei14790_dest_seguridade' then 'Seguridade social'
    when 'lei14790_dest_saude' then 'Saúde'
    when 'lei14790_dest_sociedade_civil' then 'Sociedade civil'
    when 'lei14790_dest_funapol' then 'Funapol (Polícia Federal)'
    when 'lei14790_dest_abdi' then 'ABDI'
  end as "Categoria",
  value as "% da destinação"
from analytics.observations_enriched
where series_id in (
    'lei14790_dest_esporte',
    'lei14790_dest_turismo',
    'lei14790_dest_seguranca',
    'lei14790_dest_educacao',
    'lei14790_dest_seguridade',
    'lei14790_dest_saude',
    'lei14790_dest_sociedade_civil',
    'lei14790_dest_funapol',
    'lei14790_dest_abdi'
  )
order by value desc
""".strip(),
        "visualization_settings": {
            "pie.dimension": "Categoria",
            "pie.metric": "% da destinação",
            "pie.show_legend": True,
            "pie.show_total": True,
            "pie.percent_visibility": "legend",
            "pie.slice_threshold": 0,
            "pie.colors": {
                "Esporte": BETS_PIE[0],
                "Turismo": BETS_PIE[1],
                "Segurança pública": BETS_PIE[2],
                "Educação": BETS_PIE[3],
                "Seguridade social": BETS_PIE[4],
                "Saúde": BETS_PIE[5],
                "Sociedade civil": BETS_PIE[6],
                "Funapol (Polícia Federal)": BETS_PIE[7],
                "ABDI": BETS_PIE[8],
            },
            "column_settings": {'["name","% da destinação"]': {"suffix": "%", "decimals": 1}},
        },
    },
    # --- Added from the per-tab discovery workflow (verified, existing/new data) ---
    "monetary_real_rate": {
        "name": "Juro real ex-post (Selic − IPCA 12m)",
        "display": "line",
        "description": (
            "Juro real ex-post: Selic meta (média mensal) menos IPCA acumulado em 12 meses. "
            "Fonte: BCB SGS 432 e 13522. Unidade: pontos percentuais ao ano. Frequência: "
            "mensal. Conceito: ambos anuais; aproximação ex-post (spread), não estoque."
        ),
        "query": f"""
with selic as (
  select date_trunc('month', date)::date as m, avg(value) as selic
  from analytics.observations_enriched
  where series_id = 'bcb_sgs_selic_target'
  group by 1
),
ipca as (
  select date, value as ipca12
  from analytics.observations_enriched
  where series_id = 'bcb_sgs_ipca_12m'
)
select
  ipca.date as "Data",
  'Juro real ex-post' as "Série",
  round((selic.selic - ipca.ipca12)::numeric, 2) as "% ao ano"
from ipca
join selic on selic.m = date_trunc('month', ipca.date)::date
where true
  {_periodo_filter_sql("ipca.date")}
order by "Data"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data"],
            "graph.metrics": ["% ao ano"],
            "graph.colors": ["#1f77b4"],
            "graph.x_axis.title_text": "Data",
            "graph.y_axis.title_text": "% ao ano",
            "graph.show_legend": False,
            "graph.show_goal": True,
            "graph.goal_value": 0,
            "graph.goal_label": "Juro real zero",
            "series_settings": {"Juro real ex-post": {"line.marker_enabled": False}},
            "column_settings": {'["name","% ao ano"]': {"suffix": "%", "decimals": 1}},
        },
    },
    "monetary_focus_ipca": {
        "name": "Expectativa de inflação (Focus, 12m à frente) vs IPCA realizado (12m)",
        "display": "line",
        "description": (
            "Expectativa de mercado para o IPCA dos próximos 12 meses (mediana suavizada do "
            "boletim Focus, último boletim de cada mês) ao lado do IPCA efetivamente realizado "
            "acumulado nos últimos 12 meses. Fonte: BCB Olinda/Expectativas "
            "(ExpectativasMercadoInflacao12Meses) e BCB SGS 13522. Unidade: %. Frequência: "
            "mensal. Conceito: a expectativa é prospectiva (próximos 12m) e o realizado é "
            "retrospectivo (últimos 12m) — horizontes alinhados de 12 meses, mas em sentidos "
            "opostos; não é o erro de previsão ponto a ponto."
        ),
        "query": line_query(
            ["bcb_focus_ipca_12m_ahead", "bcb_sgs_ipca_12m"],
            metric="% em 12 meses",
        ),
        "visualization_settings": {
            **line_settings("% em 12 meses", ["#9467bd", "#d62728"]),
            "series_settings": {
                "Expectativa Focus (12m à frente)": {
                    "line.marker_enabled": False,
                    "color": "#9467bd",
                },
                "IPCA em 12 meses": {"line.marker_enabled": False, "color": "#d62728"},
            },
            "column_settings": {'["name","% em 12 meses"]': {"suffix": "%", "decimals": 2}},
        },
    },
    "monetary_reer": {
        "name": "Câmbio efetivo real (índice, IPCA)",
        "display": "line",
        "description": (
            "Índice da taxa de câmbio efetiva real do real — cesta de moedas dos principais "
            "parceiros comerciais, deflacionada pelo IPCA. Fonte: BCB SGS 11752. "
            "Unidade: índice (junho/1994 = 100). Frequência: mensal. Conceito: efetivo "
            "(multilateral), não bilateral; valores mais altos = real mais apreciado em termos "
            "reais. Não confundir com a cotação nominal BRL/USD."
        ),
        "query": line_query(["bcb_sgs_reer_ipca"], metric="Índice (jun/1994=100)"),
        "visualization_settings": {
            "graph.dimensions": ["Data"],
            "graph.metrics": ["Índice (jun/1994=100)"],
            "graph.colors": ["#2ca02c"],
            "graph.x_axis.title_text": "Data",
            "graph.y_axis.title_text": "Índice (jun/1994=100)",
            "graph.show_legend": False,
            "series_settings": {
                "Câmbio efetivo real (IPCA)": {"line.marker_enabled": False}
            },
        },
    },
    "social_debt_service": {
        "name": "Comprometimento de renda das famílias com o serviço da dívida",
        "display": "line",
        "description": (
            "Comprometimento de renda das famílias com o serviço da dívida (juros + "
            "amortização) com o Sistema Financeiro Nacional, sem ajuste sazonal. Fonte: BCB "
            "SGS 29265. Unidade: % da renda mensal. Frequência: mensal (média móvel "
            "trimestral). Conceito: fluxo de pagamentos sobre a renda — distinto do "
            "endividamento, que é o estoque da dívida sobre a renda de 12 meses."
        ),
        "query": line_query(["bcb_sgs_comprometimento_renda"], metric="% da renda mensal"),
        "visualization_settings": {
            "graph.dimensions": ["Data"],
            "graph.metrics": ["% da renda mensal"],
            "graph.colors": ["#ff7f0e"],
            "graph.x_axis.title_text": "Data",
            "graph.y_axis.title_text": "% da renda mensal",
            "graph.show_legend": False,
            "series_settings": {
                "Comprometimento de renda (serviço da dívida)": {
                    "line.marker_enabled": False
                }
            },
            "column_settings": {'["name","% da renda mensal"]': {"suffix": "%", "decimals": 1}},
        },
    },
    "monetary_ipca_decomposition": {
        "name": "IPCA: cheio, alimentos e serviços (variação mensal)",
        "display": "line",
        "description": (
            "IPCA cheio, grupo Alimentação e bebidas e grupo Serviços, variação mensal. "
            "Fonte: BCB SGS 433, 1635, 10844. Unidade: % no mês. Frequência: mensal. "
            "Conceito: variações mensais comparáveis; não somam ao cheio (são recortes)."
        ),
        "query": line_query(
            ["bcb_sgs_ipca_monthly", "bcb_sgs_ipca_alimentacao", "bcb_sgs_ipca_servicos"],
            metric="Variação (% no mês)",
        ),
        "visualization_settings": {
            **line_settings("Variação (% no mês)", ["#111111", "#ff7f0e", "#1f77b4"]),
            "graph.dimensions": ["Data", "Série"],
            "series_settings": {
                "IPCA mensal": {"line.marker_enabled": False, "color": "#111111"},
                "IPCA alimentação e bebidas": {"line.marker_enabled": False, "color": "#ff7f0e"},
                "IPCA serviços": {"line.marker_enabled": False, "color": "#1f77b4"},
            },
            "column_settings": {'["name","Variação (% no mês)"]': {"suffix": "%", "decimals": 2}},
        },
    },
    "monetary_ipca_core": {
        "name": "IPCA cheio vs núcleo de médias aparadas",
        "display": "line",
        "description": (
            "IPCA cheio e núcleo por médias aparadas com suavização, variação mensal. "
            "Fonte: BCB SGS 433 e 4466. Unidade: % no mês. Frequência: mensal. "
            "Conceito: o núcleo remove itens voláteis; acompanhado pelo Copom."
        ),
        "query": line_query(
            ["bcb_sgs_ipca_monthly", "bcb_sgs_ipca_nucleo_ma"],
            metric="Variação (% no mês)",
        ),
        "visualization_settings": {
            **line_settings("Variação (% no mês)", ["#c7c7c7", "#d62728"]),
            "graph.dimensions": ["Data", "Série"],
            "series_settings": {
                "IPCA mensal": {"line.marker_enabled": False, "line.style": "solid"},
                "IPCA núcleo (médias aparadas)": {
                    "line.marker_enabled": False,
                    "line.style": "solid",
                },
            },
            "column_settings": {'["name","Variação (% no mês)"]': {"suffix": "%", "decimals": 2}},
        },
    },
    "activity_ibc_yoy": {
        "name": "IBC-Br: variação em 12 meses",
        "display": "line",
        "description": (
            "Variação interanual do IBC-Br (proxy mensal do PIB), calculada sobre a série "
            "ORIGINAL (sem ajuste sazonal) — a base correta para variação em 12 meses. "
            "Fonte: BCB SGS 24363. Unidade: % (12 meses). Frequência: mensal."
        ),
        "query": f"""
with s as (
  select date, value, lag(value, 12) over (order by date) as prev
  from analytics.observations_enriched
  where series_id = 'bcb_sgs_ibc_br_nsa'
)
select
  date as "Data",
  'IBC-Br (variação 12m)' as "Série",
  round((((value / nullif(prev, 0)) - 1) * 100)::numeric, 2) as "Variação (%)"
from s
where prev is not null
  {_periodo_filter_sql("date")}
order by "Data"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data"],
            "graph.metrics": ["Variação (%)"],
            "graph.colors": ["#9467bd"],
            "graph.x_axis.title_text": "Data",
            "graph.y_axis.title_text": "Variação (%)",
            "graph.show_legend": False,
            "graph.show_goal": True,
            "graph.goal_value": 0,
            "graph.goal_label": "Estagnação (0%)",
            "series_settings": {"IBC-Br (variação 12m)": {"line.marker_enabled": False}},
            "column_settings": {'["name","Variação (%)"]': {"suffix": "%", "decimals": 1}},
        },
    },
    "labor_income_yoy": {
        "name": "Rendimento real médio: variação interanual",
        "display": "line",
        "description": (
            "Variação em 12 meses do rendimento médio real habitual (PNAD Contínua). "
            "Fonte: IBGE/PNAD Contínua (tabela 6390). Unidade: % (12 meses). "
            "Frequência: trimestre móvel, divulgação mensal. Conceito: rendimento real."
        ),
        "query": f"""
with s as (
  select date, value, lag(value, 12) over (order by date) as prev
  from analytics.observations_enriched
  where series_id = 'ibge_pnad_real_average_income'
)
select
  date as "Data",
  'Rendimento real médio (variação 12m)' as "Série",
  round((((value / nullif(prev, 0)) - 1) * 100)::numeric, 2) as "Variação (%)"
from s
where prev is not null
  {_periodo_filter_sql("date")}
order by "Data"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data"],
            "graph.metrics": ["Variação (%)"],
            "graph.colors": ["#2ca02c"],
            "graph.x_axis.title_text": "Data",
            "graph.y_axis.title_text": "Variação (%)",
            "graph.show_legend": False,
            "graph.show_goal": True,
            "graph.goal_value": 0,
            "graph.goal_label": "Sem ganho real (0%)",
            "series_settings": {
                "Rendimento real médio (variação 12m)": {"line.marker_enabled": False}
            },
            "column_settings": {'["name","Variação (%)"]': {"suffix": "%", "decimals": 1}},
        },
    },
    "social_default_spread": {
        "name": "Inadimplência: spread pessoas físicas − total",
        "display": "line",
        "description": (
            "Diferença entre a inadimplência de pessoas físicas e a inadimplência total "
            "da carteira de crédito do SFN. Fonte: BCB SGS 21084 e 21082. Unidade: pontos "
            "percentuais. Frequência: mensal. Conceito: spread (PF − total)."
        ),
        "query": f"""
with pf as (
  select date, value from analytics.observations_enriched
  where series_id = 'bcb_sgs_inadimplencia_pf'
),
t as (
  select date, value from analytics.observations_enriched
  where series_id = 'bcb_sgs_inadimplencia_total'
)
select
  pf.date as "Data",
  'Spread PF − total' as "Série",
  round((pf.value - t.value)::numeric, 2) as "p.p."
from pf
join t on t.date = pf.date
where true
  {_periodo_filter_sql("pf.date")}
order by "Data"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data"],
            "graph.metrics": ["p.p."],
            "graph.colors": ["#d62728"],
            "graph.x_axis.title_text": "Data",
            "graph.y_axis.title_text": "p.p.",
            "graph.show_legend": False,
            "series_settings": {"Spread PF − total": {"line.marker_enabled": False}},
        },
    },
    "social_minimum_wage": {
        "name": "Salário mínimo: nominal vs real (em R$ de hoje)",
        "display": "line",
        "description": (
            "Salário mínimo nominal e seu valor real, deflacionado pelo IPCA para os preços "
            "do mês mais recente (poder de compra). Fonte: BCB SGS 1619 (salário mínimo) e "
            "433 (IPCA mensal). Unidade: R$. Frequência: mensal. Conceito: nominal corrente "
            "vs real a preços de hoje; no mês mais recente as duas linhas coincidem."
        ),
        "query": f"""
with ipca as (
  select date, value as m
  from analytics.observations_enriched
  where series_id = 'bcb_sgs_ipca_monthly'
),
idx as (
  select date, exp(sum(ln(1 + m / 100.0)) over (order by date)) as cpi
  from ipca
),
base as (select max(cpi) as cpi_now from idx),
sm as (
  select date, value as nominal
  from analytics.observations_enriched
  where series_id = 'bcb_sgs_salario_minimo'
)
select sm.date as "Data", t.label as "Série", t.valor as "R$"
from sm
join idx i on i.date = sm.date
cross join base b
cross join lateral (
  values
    ('Nominal', round(sm.nominal::numeric, 0)),
    ('Real (R$ de hoje)', round((sm.nominal * b.cpi_now / i.cpi)::numeric, 0))
) as t(label, valor)
where true
  {_periodo_filter_sql("sm.date")}
order by "Data", "Série"
""".strip(),
        "visualization_settings": {
            **line_settings("R$", ["#1f77b4", "#9aa0a6"]),
            "series_settings": {
                "Real (R$ de hoje)": {
                    "line.marker_enabled": False,
                    "line.style": "solid",
                    "color": "#1f77b4",
                },
                "Nominal": {
                    "line.marker_enabled": False,
                    "line.style": "dashed",
                    "color": "#9aa0a6",
                },
            },
            "column_settings": {'["name","R$"]': {"prefix": "R$ ", "decimals": 0}},
        },
    },
    # --- Setores produtivos ---
    "sectors_gdp_volume_index": {
        "name": "PIB e valor adicionado por setor (índice de volume, com ajuste sazonal)",
        "display": "line",
        "description": (
            "Série encadeada do índice de volume trimestral com ajuste sazonal do PIB e do "
            "valor adicionado por setor (agropecuária, indústria, serviços). Fonte: IBGE "
            "SIDRA, tabela 1621, variável 584, classificação 11255. Unidade: número-índice "
            "(média 1995 = 100). Frequência: trimestral. Conceito: volume real (quantum), "
            "com ajuste sazonal; níveis entre setores não são comparáveis (cada um tem sua "
            "própria base), apenas suas trajetórias."
        ),
        "query": line_query(
            [
                "ibge_cnt_volume_sa_pib",
                "ibge_cnt_volume_sa_agropecuaria",
                "ibge_cnt_volume_sa_industria",
                "ibge_cnt_volume_sa_servicos",
            ],
            metric="Índice (1995=100)",
        ),
        "visualization_settings": {
            **line_settings(
                "Índice (1995=100)", ["#111111", "#2ca02c", "#9467bd", "#1f77b4"]
            ),
            "series_settings": {
                "PIB": {"line.marker_enabled": False, "line.style": "solid", "color": "#111111"},
                "Agropecuária": {"line.marker_enabled": False, "color": "#2ca02c"},
                "Indústria": {"line.marker_enabled": False, "color": "#9467bd"},
                "Serviços": {"line.marker_enabled": False, "color": "#1f77b4"},
            },
        },
    },
    "sectors_gdp_yoy": {
        "name": "Valor adicionado por setor: variação em 4 trimestres",
        "display": "line",
        "description": (
            "Variação do índice de volume contra o mesmo trimestre do ano anterior, por "
            "setor, calculada sobre a série SEM ajuste sazonal (base correta para variação "
            "interanual). Fonte: IBGE SIDRA, tabela 1620, variável 583, classificação 11255. "
            "Unidade: % (4 trimestres). Frequência: trimestral. Conceito: volume real."
        ),
        "query": f"""
with s as (
  select
    series_id,
    date,
    value,
    lag(value, 4) over (partition by series_id order by date) as prev
  from analytics.observations_enriched
  where series_id in (
    'ibge_cnt_volume_nsa_agropecuaria',
    'ibge_cnt_volume_nsa_industria',
    'ibge_cnt_volume_nsa_servicos'
  )
)
select
  date as "Data",
  case series_id
    when 'ibge_cnt_volume_nsa_agropecuaria' then 'Agropecuária'
    when 'ibge_cnt_volume_nsa_industria' then 'Indústria'
    when 'ibge_cnt_volume_nsa_servicos' then 'Serviços'
  end as "Série",
  round((((value / nullif(prev, 0)) - 1) * 100)::numeric, 2) as "Variação (%)"
from s
where prev is not null
  {_periodo_filter_sql("date")}
order by "Data", "Série"
""".strip(),
        "visualization_settings": {
            **line_settings("Variação (%)", ["#2ca02c", "#9467bd", "#1f77b4"]),
            "graph.show_goal": True,
            "graph.goal_value": 0,
            "graph.goal_label": "Estagnação (0%)",
            "series_settings": {
                "Agropecuária": {"line.marker_enabled": False, "color": "#2ca02c"},
                "Indústria": {"line.marker_enabled": False, "color": "#9467bd"},
                "Serviços": {"line.marker_enabled": False, "color": "#1f77b4"},
            },
            "column_settings": {'["name","Variação (%)"]': {"suffix": "%", "decimals": 1}},
        },
    },
    "sectors_va_composition": {
        "name": "Participação dos setores no valor adicionado (área 100%)",
        "display": "area",
        "description": (
            "Participação de cada setor produtivo (agropecuária, indústria, serviços) no "
            "valor adicionado bruto a preços correntes, por trimestre. Fonte: IBGE SIDRA, "
            "tabela 1846, variável 585, classificação 11255 (códigos 90687, 90691, 90696). "
            "Unidade: % do valor adicionado a preços básicos (área 100% empilhada). "
            "Frequência: trimestral. Conceito: composição da produção a preços correntes; "
            "os três setores somam o valor adicionado total. O padrão sazonal (pico da "
            "agropecuária no início do ano) reflete a safra agrícola."
        ),
        "query": f"""
select
  date as "Data",
  case series_id
    when 'ibge_va_corrente_agropecuaria' then 'Agropecuária'
    when 'ibge_va_corrente_industria' then 'Indústria'
    when 'ibge_va_corrente_servicos' then 'Serviços'
  end as "Série",
  value as "R$ milhões (correntes)"
from analytics.observations_enriched
where series_id in (
    'ibge_va_corrente_agropecuaria',
    'ibge_va_corrente_industria',
    'ibge_va_corrente_servicos'
  )
  {_periodo_filter_sql("date")}
order by "Data", "Série"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data", "Série"],
            "graph.metrics": ["R$ milhões (correntes)"],
            "graph.x_axis.title_text": "Data",
            "graph.y_axis.title_text": "% do valor adicionado",
            "stackable.stack_type": "normalized",
            "series_settings": {
                "Serviços": {"color": "#1f77b4", "line.marker_enabled": False},
                "Indústria": {"color": "#9467bd", "line.marker_enabled": False},
                "Agropecuária": {"color": "#2ca02c", "line.marker_enabled": False},
            },
        },
    },
    "sectors_industria_composition": {
        "name": "Composição da indústria por subsetor (área 100%)",
        "display": "area",
        "description": (
            "Participação de cada subsetor da indústria (extrativa, transformação, "
            "construção, eletricidade/gás/água/resíduos) no valor adicionado da indústria, "
            "por trimestre. Fonte: IBGE SIDRA, tabela 1846, variável 585, classificação "
            "11255 (códigos 90692, 90693, 90694, 90695). Unidade: % do valor adicionado da "
            "indústria (área 100% empilhada). Frequência: trimestral. Conceito: composição "
            "a preços correntes; os subsetores somam o total da indústria."
        ),
        "query": f"""
select
  date as "Data",
  case series_id
    when 'ibge_va_corrente_ind_transformacao' then 'Indústrias de transformação'
    when 'ibge_va_corrente_ind_construcao' then 'Construção'
    when 'ibge_va_corrente_ind_extrativa' then 'Indústrias extrativas'
    when 'ibge_va_corrente_ind_eletricidade' then 'Eletricidade, gás e água'
  end as "Série",
  value as "R$ milhões (correntes)"
from analytics.observations_enriched
where series_id in (
    'ibge_va_corrente_ind_transformacao',
    'ibge_va_corrente_ind_construcao',
    'ibge_va_corrente_ind_extrativa',
    'ibge_va_corrente_ind_eletricidade'
  )
  {_periodo_filter_sql("date")}
order by "Data", "Série"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data", "Série"],
            "graph.metrics": ["R$ milhões (correntes)"],
            "graph.x_axis.title_text": "Data",
            "graph.y_axis.title_text": "% da indústria",
            "stackable.stack_type": "normalized",
            "series_settings": {
                "Indústrias de transformação": {"color": "#9467bd"},
                "Construção": {"color": "#ff7f0e"},
                "Indústrias extrativas": {"color": "#8c564b"},
                "Eletricidade, gás e água": {"color": "#17becf"},
            },
        },
    },
    "sectors_servicos_composition": {
        "name": "Composição dos serviços por subsetor (área 100%)",
        "display": "area",
        "description": (
            "Participação de cada subsetor de serviços no valor adicionado dos serviços, "
            "por trimestre: comércio, transporte/correio, informação e comunicação, "
            "atividades financeiras, atividades imobiliárias, administração pública e outras "
            "atividades de serviços. Fonte: IBGE SIDRA, tabela 1846, variável 585, "
            "classificação 11255 (códigos 90697-90703). Unidade: % do valor adicionado dos "
            "serviços (área 100% empilhada). Frequência: trimestral. Conceito: composição a "
            "preços correntes; os subsetores somam o total dos serviços."
        ),
        "query": f"""
select
  date as "Data",
  case series_id
    when 'ibge_va_corrente_serv_outros' then 'Outras atividades de serviços'
    when 'ibge_va_corrente_serv_admin_publica' then 'Administração pública'
    when 'ibge_va_corrente_serv_comercio' then 'Comércio'
    when 'ibge_va_corrente_serv_financeiras' then 'Atividades financeiras'
    when 'ibge_va_corrente_serv_imobiliarias' then 'Atividades imobiliárias'
    when 'ibge_va_corrente_serv_transporte' then 'Transporte e correio'
    when 'ibge_va_corrente_serv_informacao' then 'Informação e comunicação'
  end as "Série",
  value as "R$ milhões (correntes)"
from analytics.observations_enriched
where series_id in (
    'ibge_va_corrente_serv_outros',
    'ibge_va_corrente_serv_admin_publica',
    'ibge_va_corrente_serv_comercio',
    'ibge_va_corrente_serv_financeiras',
    'ibge_va_corrente_serv_imobiliarias',
    'ibge_va_corrente_serv_transporte',
    'ibge_va_corrente_serv_informacao'
  )
  {_periodo_filter_sql("date")}
order by "Data", "Série"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data", "Série"],
            "graph.metrics": ["R$ milhões (correntes)"],
            "graph.x_axis.title_text": "Data",
            "graph.y_axis.title_text": "% dos serviços",
            "stackable.stack_type": "normalized",
            "series_settings": {
                "Comércio": {"color": "#1f77b4"},
                "Administração pública": {"color": "#d62728"},
                "Outras atividades de serviços": {"color": "#2ca02c"},
                "Atividades financeiras": {"color": "#9467bd"},
                "Atividades imobiliárias": {"color": "#ff7f0e"},
                "Transporte e correio": {"color": "#8c564b"},
                "Informação e comunicação": {"color": "#17becf"},
            },
        },
    },
    "sectors_monthly_volume": {
        "name": "Volume mensal: indústria, varejo e serviços (com ajuste sazonal)",
        "display": "line",
        "description": (
            "Índices mensais de volume com ajuste sazonal da produção industrial (PIM-PF), "
            "do comércio varejista restrito (PMC) e dos serviços (PMS). Fonte: IBGE SIDRA, "
            "tabelas 8888 (var 12607), 8880 (var 7170) e 8163 (var 7168). Unidade: "
            "número-índice (2022 = 100). Frequência: mensal. Conceito: volume real, com "
            "ajuste sazonal; mesma base (2022 = 100), portanto comparáveis."
        ),
        "query": line_query(
            [
                "ibge_pim_industria_geral_sa",
                "ibge_pmc_varejo_volume_sa",
                "ibge_pms_servicos_volume_sa",
            ],
            metric="Índice (2022=100)",
        ),
        "visualization_settings": {
            **line_settings("Índice (2022=100)", ["#9467bd", "#ff7f0e", "#1f77b4"]),
            "series_settings": {
                "Indústria (PIM-PF)": {"line.marker_enabled": False, "color": "#9467bd"},
                "Varejo (PMC)": {"line.marker_enabled": False, "color": "#ff7f0e"},
                "Serviços (PMS)": {"line.marker_enabled": False, "color": "#1f77b4"},
            },
        },
    },
    "sectors_industrial_production": {
        "name": "Produção industrial (PIM-PF, com ajuste sazonal)",
        "display": "line",
        "description": (
            "Produção física industrial, indústria geral, índice de volume com ajuste "
            "sazonal. Fonte: IBGE SIDRA, tabela 8888, variável 12607, categoria 129314. "
            "Unidade: número-índice (2022 = 100). Frequência: mensal. Conceito: volume real."
        ),
        "query": line_query(
            ["ibge_pim_industria_geral_sa"], metric="Índice (2022=100)"
        ),
        "visualization_settings": {
            "graph.dimensions": ["Data"],
            "graph.metrics": ["Índice (2022=100)"],
            "graph.colors": ["#9467bd"],
            "graph.x_axis.title_text": "Data",
            "graph.y_axis.title_text": "Índice (2022=100)",
            "graph.show_legend": False,
            "series_settings": {"Indústria (PIM-PF)": {"line.marker_enabled": False}},
        },
    },
    "sectors_retail": {
        "name": "Comércio varejista (PMC, volume com ajuste sazonal)",
        "display": "line",
        "description": (
            "Volume de vendas no comércio varejista restrito, índice com ajuste sazonal. "
            "Fonte: IBGE SIDRA, tabela 8880, variável 7170, categoria 56734. Unidade: "
            "número-índice (2022 = 100). Frequência: mensal. Conceito: volume real."
        ),
        "query": line_query(
            ["ibge_pmc_varejo_volume_sa"], metric="Índice (2022=100)"
        ),
        "visualization_settings": {
            "graph.dimensions": ["Data"],
            "graph.metrics": ["Índice (2022=100)"],
            "graph.colors": ["#ff7f0e"],
            "graph.x_axis.title_text": "Data",
            "graph.y_axis.title_text": "Índice (2022=100)",
            "graph.show_legend": False,
            "series_settings": {"Varejo (PMC)": {"line.marker_enabled": False}},
        },
    },
    "sectors_services": {
        "name": "Serviços (PMS, volume com ajuste sazonal)",
        "display": "line",
        "description": (
            "Volume de serviços (total), índice com ajuste sazonal. Fonte: IBGE SIDRA, "
            "tabela 8163, variável 7168, categorias 56726 e 56703. Unidade: número-índice "
            "(2022 = 100). Frequência: mensal. Conceito: volume real."
        ),
        "query": line_query(
            ["ibge_pms_servicos_volume_sa"], metric="Índice (2022=100)"
        ),
        "visualization_settings": {
            "graph.dimensions": ["Data"],
            "graph.metrics": ["Índice (2022=100)"],
            "graph.colors": ["#1f77b4"],
            "graph.x_axis.title_text": "Data",
            "graph.y_axis.title_text": "Índice (2022=100)",
            "graph.show_legend": False,
            "series_settings": {"Serviços (PMS)": {"line.marker_enabled": False}},
        },
    },
    # --- Comércio exterior ---
    "trade_exports_imports": {
        "name": "Exportações e importações de bens (mensal)",
        "display": "line",
        "description": (
            "Exportações e importações de bens, base Balanço de Pagamentos, fluxo mensal. "
            "Fonte: BCB SGS 22708 (exportações) e 22709 (importações). Unidade: US$ milhões. "
            "Frequência: mensal. Conceito: fluxo nominal em dólares, base Balanço de "
            "Pagamentos (BPM6)."
        ),
        "query": line_query(
            ["bcb_sgs_exportacoes_fob", "bcb_sgs_importacoes_fob"],
            metric="US$ milhões",
        ),
        "visualization_settings": {
            **line_settings("US$ milhões", ["#2ca02c", "#d62728"]),
            "series_settings": {
                "Exportações": {"line.marker_enabled": False, "color": "#2ca02c"},
                "Importações": {"line.marker_enabled": False, "color": "#d62728"},
            },
        },
    },
    "trade_flows_12m": {
        "name": "Exportações, importações e saldo de bens (acumulado em 12 meses)",
        "display": "line",
        "description": (
            "Exportações, importações e saldo da balança comercial de bens, acumulados em "
            "12 meses para remover a sazonalidade mensal. Fonte: BCB SGS 22708, 22709 e "
            "22707 (base Balanço de Pagamentos). Unidade: US$ milhões (acumulado 12m). "
            "Frequência: mensal. Conceito: fluxo nominal; saldo = exportações − importações."
        ),
        "query": f"""
with d as (
  select
    date,
    series_id,
    sum(value) over (
      partition by series_id order by date rows between 11 preceding and current row
    ) as v12,
    count(*) over (
      partition by series_id order by date rows between 11 preceding and current row
    ) as n
  from analytics.observations_enriched
  where series_id in (
    'bcb_sgs_exportacoes_fob',
    'bcb_sgs_importacoes_fob',
    'bcb_sgs_balanca_comercial_saldo'
  )
)
select
  date as "Data",
  case series_id
    when 'bcb_sgs_exportacoes_fob' then 'Exportações'
    when 'bcb_sgs_importacoes_fob' then 'Importações'
    when 'bcb_sgs_balanca_comercial_saldo' then 'Saldo comercial'
  end as "Série",
  v12 as "US$ milhões (12m)"
from d
where n = 12
  {_periodo_filter_sql("date")}
order by "Data", "Série"
""".strip(),
        "visualization_settings": {
            **line_settings("US$ milhões (12m)", ["#2ca02c", "#d62728", "#1f77b4"]),
            "series_settings": {
                "Exportações": {"line.marker_enabled": False, "color": "#2ca02c"},
                "Importações": {"line.marker_enabled": False, "color": "#d62728"},
                "Saldo comercial": {"line.marker_enabled": False, "color": "#1f77b4"},
            },
        },
    },
    "trade_balance_monthly": {
        "name": "Saldo da balança comercial de bens (mensal)",
        "display": "bar",
        "description": (
            "Saldo mensal da balança comercial de bens (exportações menos importações), "
            "base Balanço de Pagamentos. Fonte: BCB SGS 22707. Unidade: US$ milhões. "
            "Frequência: mensal. Sinal: + superávit, − déficit."
        ),
        "query": line_query(
            ["bcb_sgs_balanca_comercial_saldo"], metric="US$ milhões"
        ),
        "visualization_settings": {
            "graph.dimensions": ["Data"],
            "graph.metrics": ["US$ milhões"],
            "graph.colors": ["#1f77b4"],
            "graph.x_axis.title_text": "Data",
            "graph.y_axis.title_text": "US$ milhões",
            "graph.show_legend": False,
            "graph.show_goal": True,
            "graph.goal_value": 0,
            "graph.goal_label": "Equilíbrio (0)",
        },
    },
    "trade_partners_exports": {
        "name": "Exportações de bens por parceiro (anual, FOB)",
        "display": "bar",
        "description": (
            "Exportações brasileiras de bens (FOB) por país de destino, total anual, para "
            "os doze maiores parceiros (China, Estados Unidos, Argentina, Países Baixos, "
            "Espanha, Singapura, México, Chile, Canadá, Alemanha, Japão, Coreia do Sul) e "
            "demais países. Fonte: MDIC/SECEX Comex Stat. Unidade: US$ milhões. "
            "Frequência: anual (apenas anos completos). Conceito: fluxo nominal, base SECEX "
            "por país — distinto da base Balanço de Pagamentos do BCB. Barras empilhadas "
            "somam o total exportado (maior parceiro na base, demais países no topo)."
        ),
        "query": f"""
select
  date as "Data",
  case series_id
    when 'comexstat_export_china' then 'China'
    when 'comexstat_export_eua' then 'Estados Unidos'
    when 'comexstat_export_argentina' then 'Argentina'
    when 'comexstat_export_paises_baixos' then 'Países Baixos'
    when 'comexstat_export_espanha' then 'Espanha'
    when 'comexstat_export_singapura' then 'Singapura'
    when 'comexstat_export_mexico' then 'México'
    when 'comexstat_export_chile' then 'Chile'
    when 'comexstat_export_canada' then 'Canadá'
    when 'comexstat_export_alemanha' then 'Alemanha'
    when 'comexstat_export_japao' then 'Japão'
    when 'comexstat_export_coreia_sul' then 'Coreia do Sul'
    when 'comexstat_export_demais' then 'Demais países'
  end as "Série",
  value as "US$ milhões"
from analytics.observations_enriched
where series_id in (
    'comexstat_export_china',
    'comexstat_export_eua',
    'comexstat_export_argentina',
    'comexstat_export_paises_baixos',
    'comexstat_export_espanha',
    'comexstat_export_singapura',
    'comexstat_export_mexico',
    'comexstat_export_chile',
    'comexstat_export_canada',
    'comexstat_export_alemanha',
    'comexstat_export_japao',
    'comexstat_export_coreia_sul',
    'comexstat_export_demais'
  )
  and date < date_trunc('year', current_date)
  {_periodo_filter_sql("date")}
-- Metabase stacks by the order series first appear in the result set (first = top of
-- stack). Emit the residual "Demais países" first and China last, so China sits at the
-- base, partners descend upward and "Demais países" is the top band.
order by "Data", case series_id
    when 'comexstat_export_demais' then 0
    when 'comexstat_export_coreia_sul' then 1
    when 'comexstat_export_japao' then 2
    when 'comexstat_export_alemanha' then 3
    when 'comexstat_export_canada' then 4
    when 'comexstat_export_chile' then 5
    when 'comexstat_export_mexico' then 6
    when 'comexstat_export_singapura' then 7
    when 'comexstat_export_espanha' then 8
    when 'comexstat_export_paises_baixos' then 9
    when 'comexstat_export_argentina' then 10
    when 'comexstat_export_eua' then 11
    when 'comexstat_export_china' then 12
  end
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data", "Série"],
            "graph.metrics": ["US$ milhões"],
            "graph.x_axis.title_text": "Ano",
            "graph.x_axis.scale": "ordinal",
            "graph.y_axis.title_text": "US$ milhões",
            "stackable.stack_type": "stacked",
            # Largest partner (China) at the bottom, descending upward, with the
            # "Demais países" residual as the top band — a stable big base, tail on top.
            # Metabase renders the FIRST series_order entry at the TOP of the stack, so
            # the array is listed top→bottom: Demais first, China last (at the base).
            "graph.series_order": [
                {"key": "Demais países", "enabled": True, "name": "Demais países"},
                {"key": "Coreia do Sul", "enabled": True, "name": "Coreia do Sul"},
                {"key": "Japão", "enabled": True, "name": "Japão"},
                {"key": "Alemanha", "enabled": True, "name": "Alemanha"},
                {"key": "Canadá", "enabled": True, "name": "Canadá"},
                {"key": "Chile", "enabled": True, "name": "Chile"},
                {"key": "México", "enabled": True, "name": "México"},
                {"key": "Singapura", "enabled": True, "name": "Singapura"},
                {"key": "Espanha", "enabled": True, "name": "Espanha"},
                {"key": "Países Baixos", "enabled": True, "name": "Países Baixos"},
                {"key": "Argentina", "enabled": True, "name": "Argentina"},
                {"key": "Estados Unidos", "enabled": True, "name": "Estados Unidos"},
                {"key": "China", "enabled": True, "name": "China"},
            ],
            "series_settings": {
                "China": {"color": "#d62728"},
                "Estados Unidos": {"color": "#1f77b4"},
                "Argentina": {"color": "#2ca02c"},
                "Países Baixos": {"color": "#ff7f0e"},
                "Espanha": {"color": "#9467bd"},
                "Singapura": {"color": "#17becf"},
                "México": {"color": "#8c564b"},
                "Chile": {"color": "#e377c2"},
                "Canadá": {"color": "#bcbd22"},
                "Alemanha": {"color": "#393b79"},
                "Japão": {"color": "#7f7f7f"},
                "Coreia do Sul": {"color": "#9edae5"},
                "Demais países": {"color": "#c7c7c7"},
            },
        },
    },
    "trade_partners_imports": {
        "name": "Importações de bens por parceiro (anual, FOB)",
        "display": "bar",
        "description": (
            "Importações brasileiras de bens (FOB) por país de origem, total anual, para os "
            "doze maiores parceiros (China, Estados Unidos, Alemanha, Argentina, Rússia, "
            "Índia, Itália, França, México, Japão, Coreia do Sul, Chile) e demais países. "
            "Fonte: MDIC/SECEX Comex Stat. Unidade: US$ milhões. Frequência: anual (apenas "
            "anos completos). Conceito: fluxo nominal, base SECEX por país — distinto da base "
            "Balanço de Pagamentos do BCB. Barras empilhadas somam o total importado (maior "
            "parceiro na base, demais países no topo)."
        ),
        "query": f"""
select
  date as "Data",
  case series_id
    when 'comexstat_import_china' then 'China'
    when 'comexstat_import_eua' then 'Estados Unidos'
    when 'comexstat_import_alemanha' then 'Alemanha'
    when 'comexstat_import_argentina' then 'Argentina'
    when 'comexstat_import_russia' then 'Rússia'
    when 'comexstat_import_india' then 'Índia'
    when 'comexstat_import_italia' then 'Itália'
    when 'comexstat_import_franca' then 'França'
    when 'comexstat_import_mexico' then 'México'
    when 'comexstat_import_japao' then 'Japão'
    when 'comexstat_import_coreia_sul' then 'Coreia do Sul'
    when 'comexstat_import_chile' then 'Chile'
    when 'comexstat_import_demais' then 'Demais países'
  end as "Série",
  value as "US$ milhões"
from analytics.observations_enriched
where series_id in (
    'comexstat_import_china',
    'comexstat_import_eua',
    'comexstat_import_alemanha',
    'comexstat_import_argentina',
    'comexstat_import_russia',
    'comexstat_import_india',
    'comexstat_import_italia',
    'comexstat_import_franca',
    'comexstat_import_mexico',
    'comexstat_import_japao',
    'comexstat_import_coreia_sul',
    'comexstat_import_chile',
    'comexstat_import_demais'
  )
  and date < date_trunc('year', current_date)
  {_periodo_filter_sql("date")}
-- Metabase stacks by the order series first appear in the result set (first = top of
-- stack). Emit the residual "Demais países" first and China last, so China sits at the
-- base, partners descend upward and "Demais países" is the top band.
order by "Data", case series_id
    when 'comexstat_import_demais' then 0
    when 'comexstat_import_chile' then 1
    when 'comexstat_import_coreia_sul' then 2
    when 'comexstat_import_japao' then 3
    when 'comexstat_import_mexico' then 4
    when 'comexstat_import_franca' then 5
    when 'comexstat_import_italia' then 6
    when 'comexstat_import_india' then 7
    when 'comexstat_import_russia' then 8
    when 'comexstat_import_argentina' then 9
    when 'comexstat_import_alemanha' then 10
    when 'comexstat_import_eua' then 11
    when 'comexstat_import_china' then 12
  end
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data", "Série"],
            "graph.metrics": ["US$ milhões"],
            "graph.x_axis.title_text": "Ano",
            "graph.x_axis.scale": "ordinal",
            "graph.y_axis.title_text": "US$ milhões",
            "stackable.stack_type": "stacked",
            # Largest partner (China) at the bottom, descending upward, with the
            # "Demais países" residual as the top band. Metabase renders the FIRST
            # series_order entry at the TOP, so the array is listed top→bottom.
            "graph.series_order": [
                {"key": "Demais países", "enabled": True, "name": "Demais países"},
                {"key": "Chile", "enabled": True, "name": "Chile"},
                {"key": "Coreia do Sul", "enabled": True, "name": "Coreia do Sul"},
                {"key": "Japão", "enabled": True, "name": "Japão"},
                {"key": "México", "enabled": True, "name": "México"},
                {"key": "França", "enabled": True, "name": "França"},
                {"key": "Itália", "enabled": True, "name": "Itália"},
                {"key": "Índia", "enabled": True, "name": "Índia"},
                {"key": "Rússia", "enabled": True, "name": "Rússia"},
                {"key": "Argentina", "enabled": True, "name": "Argentina"},
                {"key": "Alemanha", "enabled": True, "name": "Alemanha"},
                {"key": "Estados Unidos", "enabled": True, "name": "Estados Unidos"},
                {"key": "China", "enabled": True, "name": "China"},
            ],
            "series_settings": {
                "China": {"color": "#d62728"},
                "Estados Unidos": {"color": "#1f77b4"},
                "Alemanha": {"color": "#2ca02c"},
                "Argentina": {"color": "#ff7f0e"},
                "Rússia": {"color": "#9467bd"},
                "Índia": {"color": "#8c564b"},
                "Itália": {"color": "#17becf"},
                "França": {"color": "#393b79"},
                "México": {"color": "#e377c2"},
                "Japão": {"color": "#7f7f7f"},
                "Coreia do Sul": {"color": "#9edae5"},
                "Chile": {"color": "#bcbd22"},
                "Demais países": {"color": "#c7c7c7"},
            },
        },
    },
    "trade_china_usa_trend": {
        "name": "Comércio com China e Estados Unidos (anual, FOB)",
        # Grouped (clustered) bars: China and EUA side by side per year — multi-series
        # bar without a stack type renders clustered, matching the tab's annual-bar style
        # and making the China-overtaking-EUA comparison clearer.
        "display": "bar",
        "description": (
            "Corrente de comércio (exportações + importações de bens, FOB) do Brasil com os "
            "dois maiores parceiros, China e Estados Unidos, por ano. Fonte: MDIC/SECEX "
            "Comex Stat. Unidade: US$ milhões. Frequência: anual (apenas anos completos). "
            "Conceito: fluxo nominal, base SECEX por país (corrente = exportações + "
            "importações) — distinto da base Balanço de Pagamentos do BCB. Barras agrupadas "
            "por ano, com linha de tendência habilitada."
        ),
        "query": f"""
select
  date as "Data",
  case
    when series_id in ('comexstat_export_china', 'comexstat_import_china') then 'China'
    when series_id in ('comexstat_export_eua', 'comexstat_import_eua')
      then 'Estados Unidos'
  end as "Série",
  sum(value) as "US$ milhões"
from analytics.observations_enriched
where series_id in (
    'comexstat_export_china',
    'comexstat_import_china',
    'comexstat_export_eua',
    'comexstat_import_eua'
  )
  and date < date_trunc('year', current_date)
  {_periodo_filter_sql("date")}
group by date, "Série"
order by "Data", "Série"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data", "Série"],
            "graph.metrics": ["US$ milhões"],
            "graph.x_axis.title_text": "Ano",
            "graph.x_axis.scale": "ordinal",
            "graph.y_axis.title_text": "US$ milhões",
            "graph.show_trendline": True,
            "graph.series_order": [
                {"key": "China", "enabled": True, "name": "China"},
                {"key": "Estados Unidos", "enabled": True, "name": "Estados Unidos"},
            ],
            "series_settings": {
                "China": {"line.marker_enabled": True, "color": "#d62728"},
                "Estados Unidos": {"line.marker_enabled": True, "color": "#1f77b4"},
            },
        },
    },
    "trade_mercosul": {
        "name": "Comércio com o Mercosul (anual, FOB)",
        "display": "line",
        "description": (
            "Exportações e importações brasileiras de bens (FOB) com o bloco Mercosul, e o "
            "saldo (exportações − importações), por ano. Fonte: MDIC/SECEX Comex Stat, "
            "agrupamento por bloco econômico (Mercado Comum do Sul - Mercosul). Unidade: "
            "US$ milhões. Frequência: anual (apenas anos completos). Conceito: fluxo "
            "nominal, base SECEX por bloco — distinto da base Balanço de Pagamentos do BCB. "
            "O agrupamento da SECEX reflete a composição do bloco ao longo do tempo "
            "(Venezuela suspensa desde 2016; Bolívia membro pleno a partir de 2024)."
        ),
        "query": f"""
with m as (
  select
    date,
    sum(value) filter (where series_id = 'comexstat_export_mercosul') as exp,
    sum(value) filter (where series_id = 'comexstat_import_mercosul') as imp
  from analytics.observations_enriched
  where series_id in ('comexstat_export_mercosul', 'comexstat_import_mercosul')
    and date < date_trunc('year', current_date)
  group by date
)
select m.date as "Data", s.label as "Série", s.v as "US$ milhões"
from m
cross join lateral (
  values
    ('Exportações', m.exp),
    ('Importações', m.imp),
    ('Saldo comercial', m.exp - m.imp)
) as s(label, v)
where s.v is not null
  {_periodo_filter_sql("m.date")}
order by "Data", "Série"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data", "Série"],
            "graph.metrics": ["US$ milhões"],
            "graph.x_axis.title_text": "Ano",
            "graph.x_axis.scale": "ordinal",
            "graph.y_axis.title_text": "US$ milhões",
            "graph.show_trendline": True,
            "graph.series_order": [
                {"key": "Exportações", "enabled": True, "name": "Exportações"},
                {"key": "Importações", "enabled": True, "name": "Importações"},
                {"key": "Saldo comercial", "enabled": True, "name": "Saldo comercial"},
            ],
            "series_settings": {
                "Exportações": {"line.marker_enabled": True, "color": "#2ca02c"},
                "Importações": {"line.marker_enabled": True, "color": "#d62728"},
                "Saldo comercial": {"line.marker_enabled": True, "color": "#1f77b4"},
            },
        },
    },
    "trade_brics_flows": {
        "name": "Comércio do Brasil com os BRICS: exportações, importações e saldo (anual, FOB)",
        "display": "line",
        "description": (
            "Exportações e importações brasileiras de bens (FOB) com os países do BRICS, e o "
            "saldo (exportações − importações), por ano. Fonte: MDIC/SECEX Comex Stat "
            "(https://comexstat.mdic.gov.br/), soma dos parceiros nomeados (o Comex Stat não "
            "possui bloco BRICS). Unidade: US$ milhões. Frequência: anual (apenas anos "
            "completos). Conceito: fluxo nominal FOB, base SECEX por país — distinto da base "
            "Balanço de Pagamentos do BCB. BRICS = China, Índia, Rússia e África do Sul "
            "(definição central; o Brasil é membro e não entra no agregado por ser o país "
            "declarante); membros do BRICS ampliado (2024/2025) não estão incluídos."
        ),
        "query": f"""
with m as (
  select
    date,
    sum(value) filter (where series_id like 'comexstat_export_%') as exp,
    sum(value) filter (where series_id like 'comexstat_import_%') as imp
  from analytics.observations_enriched
  where series_id in (
      'comexstat_export_china','comexstat_export_india',
      'comexstat_export_russia','comexstat_export_africa_sul',
      'comexstat_import_china','comexstat_import_india',
      'comexstat_import_russia','comexstat_import_africa_sul'
    )
    and date < date_trunc('year', current_date)
  group by date
)
select m.date as "Data", s.label as "Série", s.v as "US$ milhões"
from m
cross join lateral (
  values
    ('Exportações', m.exp),
    ('Importações', m.imp),
    ('Saldo comercial', m.exp - m.imp)
) as s(label, v)
where s.v is not null
  {_periodo_filter_sql("m.date")}
order by "Data", "Série"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data", "Série"],
            "graph.metrics": ["US$ milhões"],
            "graph.x_axis.title_text": "Ano",
            "graph.x_axis.scale": "ordinal",
            "graph.y_axis.title_text": "US$ milhões",
            "graph.show_trendline": True,
            "graph.series_order": [
                {"key": "Exportações", "enabled": True, "name": "Exportações"},
                {"key": "Importações", "enabled": True, "name": "Importações"},
                {"key": "Saldo comercial", "enabled": True, "name": "Saldo comercial"},
            ],
            "series_settings": {
                "Exportações": {"line.marker_enabled": True, "color": "#2ca02c"},
                "Importações": {"line.marker_enabled": True, "color": "#d62728"},
                "Saldo comercial": {"line.marker_enabled": True, "color": "#1f77b4"},
            },
        },
    },
    "trade_brics_share": {
        "name": "Participação dos BRICS no comércio exterior do Brasil (anual)",
        "display": "line",
        "description": (
            "Participação dos países do BRICS nas exportações e nas importações brasileiras "
            "de bens, por ano. Numerador: soma do comércio com os BRICS; denominador: total "
            "do comércio do Brasil no mesmo fluxo (mesma base SECEX por país). Fonte: "
            "MDIC/SECEX Comex Stat (https://comexstat.mdic.gov.br/). Unidade: % do total. "
            "Frequência: anual (apenas anos completos). Conceito: razão de fluxos nominais "
            "FOB, base SECEX por país — distinto da base Balanço de Pagamentos do BCB. "
            "BRICS = China, Índia, Rússia e África do Sul (definição central; o Brasil é "
            "membro e não entra no agregado); membros do BRICS ampliado (2024/2025) não "
            "estão incluídos."
        ),
        "query": """
with e as (
  -- denominator = the per-flow country universe (the 12 named export partners +
  -- comexstat_export_demais), which sums cleanly to Brazil's total exports. The new
  -- BRICS legs (india/russia/africa_sul) are NOT added here: they already sit inside
  -- comexstat_export_demais, so adding them would double-count the numerator's members.
  select date,
    sum(value) filter (where series_id in (
      'comexstat_export_china','comexstat_export_india',
      'comexstat_export_russia','comexstat_export_africa_sul')) as brics,
    sum(value) filter (where series_id in (
      'comexstat_export_china','comexstat_export_eua','comexstat_export_argentina',
      'comexstat_export_paises_baixos','comexstat_export_espanha','comexstat_export_singapura',
      'comexstat_export_mexico','comexstat_export_chile','comexstat_export_canada',
      'comexstat_export_alemanha','comexstat_export_japao','comexstat_export_coreia_sul',
      'comexstat_export_demais')) as total
  from analytics.observations_enriched
  where series_id in (
      'comexstat_export_china','comexstat_export_eua','comexstat_export_argentina',
      'comexstat_export_paises_baixos','comexstat_export_espanha','comexstat_export_singapura',
      'comexstat_export_mexico','comexstat_export_chile','comexstat_export_canada',
      'comexstat_export_alemanha','comexstat_export_japao','comexstat_export_coreia_sul',
      'comexstat_export_demais',
      'comexstat_export_india','comexstat_export_russia','comexstat_export_africa_sul')
    and date < date_trunc('year', current_date)
  group by date
),
i as (
  -- denominator = the 12 named import partners + comexstat_import_demais (= total
  -- imports). Among the BRICS members only África do Sul is folded into demais, so we
  -- add just that leg to the numerator-source set while keeping the denominator clean.
  select date,
    sum(value) filter (where series_id in (
      'comexstat_import_china','comexstat_import_india',
      'comexstat_import_russia','comexstat_import_africa_sul')) as brics,
    sum(value) filter (where series_id in (
      'comexstat_import_china','comexstat_import_eua','comexstat_import_alemanha',
      'comexstat_import_argentina','comexstat_import_russia','comexstat_import_india',
      'comexstat_import_italia','comexstat_import_franca','comexstat_import_mexico',
      'comexstat_import_japao','comexstat_import_coreia_sul','comexstat_import_chile',
      'comexstat_import_demais')) as total
  from analytics.observations_enriched
  where series_id in (
      'comexstat_import_china','comexstat_import_eua','comexstat_import_alemanha',
      'comexstat_import_argentina','comexstat_import_russia','comexstat_import_india',
      'comexstat_import_italia','comexstat_import_franca','comexstat_import_mexico',
      'comexstat_import_japao','comexstat_import_coreia_sul','comexstat_import_chile',
      'comexstat_import_demais','comexstat_import_africa_sul')
    and date < date_trunc('year', current_date)
  group by date
)
select e.date as "Data", 'Exportações' as "Série",
       round(100.0 * e.brics / nullif(e.total,0), 1) as "% do total"
from e
union all
select i.date, 'Importações',
       round(100.0 * i.brics / nullif(i.total,0), 1)
from i
order by "Data", "Série"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data", "Série"],
            "graph.metrics": ["% do total"],
            "graph.x_axis.title_text": "Ano",
            "graph.x_axis.scale": "ordinal",
            "graph.y_axis.title_text": "% do total",
            "graph.y_axis.suffix": "%",
            "graph.show_trendline": True,
            "graph.series_order": [
                {"key": "Exportações", "enabled": True, "name": "Exportações"},
                {"key": "Importações", "enabled": True, "name": "Importações"},
            ],
            "series_settings": {
                "Exportações": {"line.marker_enabled": True, "color": "#2ca02c"},
                "Importações": {"line.marker_enabled": True, "color": "#d62728"},
            },
        },
    },
    "trade_brics_by_member": {
        "name": "Comércio do Brasil com os BRICS por país-membro (anual, FOB)",
        "display": "bar",
        "description": (
            "Corrente de comércio (exportações + importações de bens, FOB) do Brasil com cada "
            "país-membro do BRICS, por ano, empilhada. Fonte: MDIC/SECEX Comex Stat "
            "(https://comexstat.mdic.gov.br/), por país. Unidade: US$ milhões. Frequência: "
            "anual (apenas anos completos). Conceito: fluxo nominal FOB (corrente = "
            "exportações + importações), base SECEX por país — distinto da base Balanço de "
            "Pagamentos do BCB. BRICS = China, Índia, Rússia e África do Sul (definição "
            "central; o Brasil é membro e não entra no agregado); membros do BRICS ampliado "
            "(2024/2025) não estão incluídos."
        ),
        "query": f"""
select
  date as "Data",
  case
    when series_id like '%_china' then 'China'
    when series_id like '%_india' then 'Índia'
    when series_id like '%_russia' then 'Rússia'
    when series_id like '%_africa_sul' then 'África do Sul'
  end as "Série",
  sum(value) as "US$ milhões"
from analytics.observations_enriched
where series_id in (
    'comexstat_export_china','comexstat_import_china',
    'comexstat_export_india','comexstat_import_india',
    'comexstat_export_russia','comexstat_import_russia',
    'comexstat_export_africa_sul','comexstat_import_africa_sul'
  )
  and date < date_trunc('year', current_date)
  {_periodo_filter_sql("date")}
group by date, "Série"
order by "Data", "Série"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data", "Série"],
            "graph.metrics": ["US$ milhões"],
            "graph.x_axis.title_text": "Ano",
            "graph.x_axis.scale": "ordinal",
            "graph.y_axis.title_text": "US$ milhões",
            "stackable.stack_type": "stacked",
            "graph.series_order": [
                {"key": "África do Sul", "enabled": True, "name": "África do Sul"},
                {"key": "Rússia", "enabled": True, "name": "Rússia"},
                {"key": "Índia", "enabled": True, "name": "Índia"},
                {"key": "China", "enabled": True, "name": "China"},
            ],
            "series_settings": {
                "China": {"color": "#d62728"},
                "Índia": {"color": "#8c564b"},
                "Rússia": {"color": "#9467bd"},
                "África do Sul": {"color": "#2ca02c"},
            },
        },
    },
    "trade_brics_vs_blocs": {
        "name": (
            "Corrente de comércio do Brasil com BRICS, Mercosul, União Europeia e "
            "Estados Unidos (anual, FOB)"
        ),
        "display": "line",
        "description": (
            "Corrente de comércio (exportações + importações de bens, FOB) do Brasil com "
            "quatro agrupamentos de parceiros — BRICS, Mercosul, União Europeia e Estados "
            "Unidos — por ano. Fonte: MDIC/SECEX Comex Stat (https://comexstat.mdic.gov.br/); "
            "BRICS é soma de países nomeados, Mercosul e União Europeia são blocos do Comex "
            "Stat, Estados Unidos é país. Unidade: US$ milhões. Frequência: anual (apenas "
            "anos completos). Conceito: fluxo nominal FOB, base SECEX — distinto da base "
            "Balanço de Pagamentos do BCB. Os grupos não são mutuamente exclusivos e não "
            "somam ao total: comparação de magnitude, não de composição. BRICS = China, "
            "Índia, Rússia e África do Sul (definição central; membros do BRICS ampliado de "
            "2024/2025 não incluídos)."
        ),
        "query": f"""
select date as "Data", "Série", sum(value) as "US$ milhões"
from (
  select date,
    case
      when series_id in (
        'comexstat_export_china','comexstat_import_china',
        'comexstat_export_india','comexstat_import_india',
        'comexstat_export_russia','comexstat_import_russia',
        'comexstat_export_africa_sul','comexstat_import_africa_sul') then 'BRICS'
      when series_id in ('comexstat_export_mercosul','comexstat_import_mercosul')
        then 'Mercosul'
      when series_id in ('comexstat_export_uniao_europeia','comexstat_import_uniao_europeia')
        then 'União Europeia'
      when series_id in ('comexstat_export_eua','comexstat_import_eua')
        then 'Estados Unidos'
    end as "Série",
    value
  from analytics.observations_enriched
  where series_id in (
      'comexstat_export_china','comexstat_import_china',
      'comexstat_export_india','comexstat_import_india',
      'comexstat_export_russia','comexstat_import_russia',
      'comexstat_export_africa_sul','comexstat_import_africa_sul',
      'comexstat_export_mercosul','comexstat_import_mercosul',
      'comexstat_export_uniao_europeia','comexstat_import_uniao_europeia',
      'comexstat_export_eua','comexstat_import_eua'
    )
    and date < date_trunc('year', current_date)
    {_periodo_filter_sql("date")}
) t
where "Série" is not null
group by date, "Série"
order by "Data", "Série"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data", "Série"],
            "graph.metrics": ["US$ milhões"],
            "graph.x_axis.title_text": "Ano",
            "graph.x_axis.scale": "ordinal",
            "graph.y_axis.title_text": "US$ milhões",
            "graph.show_trendline": False,
            "graph.series_order": [
                {"key": "BRICS", "enabled": True, "name": "BRICS"},
                {"key": "União Europeia", "enabled": True, "name": "União Europeia"},
                {"key": "Estados Unidos", "enabled": True, "name": "Estados Unidos"},
                {"key": "Mercosul", "enabled": True, "name": "Mercosul"},
            ],
            "series_settings": {
                "BRICS": {"line.marker_enabled": True, "color": "#d62728"},
                "União Europeia": {"line.marker_enabled": True, "color": "#1f77b4"},
                "Estados Unidos": {"line.marker_enabled": True, "color": "#ff7f0e"},
                "Mercosul": {"line.marker_enabled": True, "color": "#2ca02c"},
            },
        },
    },
    "trade_commodities_exports": {
        "name": "Maiores commodities exportadas por capítulo (anual, FOB)",
        "display": "bar",
        "description": (
            "Exportações brasileiras de bens (FOB) por capítulo de produto (SH2), total "
            "anual, para os dez maiores capítulos (combustíveis e óleos minerais, grãos e "
            "oleaginosas, minérios, carnes, açúcares, máquinas mecânicas, ferro e aço, "
            "veículos, café, celulose) e demais produtos. Fonte: MDIC/SECEX Comex Stat, "
            "agrupamento por capítulo SH2 (details=chapter). Unidade: US$ milhões. "
            "Frequência: anual (apenas anos completos). Conceito: fluxo nominal, base SECEX "
            "por produto. Barras empilhadas somam o total exportado."
        ),
        "query": f"""
select
  date as "Data",
  case series_id
    when 'comexstat_export_prod_comb_oleos_minerais' then 'Combustíveis e óleos minerais'
    when 'comexstat_export_prod_graos_oleaginosas' then 'Grãos e oleaginosas (soja)'
    when 'comexstat_export_prod_minerios' then 'Minérios'
    when 'comexstat_export_prod_carnes' then 'Carnes'
    when 'comexstat_export_prod_acucares' then 'Açúcares'
    when 'comexstat_export_prod_maquinas_mecanicas' then 'Máquinas mecânicas'
    when 'comexstat_export_prod_ferro_aco' then 'Ferro e aço'
    when 'comexstat_export_prod_veiculos' then 'Veículos'
    when 'comexstat_export_prod_cafe' then 'Café'
    when 'comexstat_export_prod_celulose' then 'Celulose'
    when 'comexstat_export_prod_demais' then 'Demais produtos'
  end as "Série",
  value as "US$ milhões"
from analytics.observations_enriched
where series_id in (
    'comexstat_export_prod_comb_oleos_minerais',
    'comexstat_export_prod_graos_oleaginosas',
    'comexstat_export_prod_minerios',
    'comexstat_export_prod_carnes',
    'comexstat_export_prod_acucares',
    'comexstat_export_prod_maquinas_mecanicas',
    'comexstat_export_prod_ferro_aco',
    'comexstat_export_prod_veiculos',
    'comexstat_export_prod_cafe',
    'comexstat_export_prod_celulose',
    'comexstat_export_prod_demais'
  )
  and date < date_trunc('year', current_date)
  {_periodo_filter_sql("date")}
-- Metabase stacks by the order series first appear in the result set (first = top of
-- stack). Emit "Demais produtos" first and the largest chapter last, so the biggest
-- commodity sits at the base, chapters descend upward and "Demais produtos" is on top.
order by "Data", case series_id
    when 'comexstat_export_prod_demais' then 0
    when 'comexstat_export_prod_celulose' then 1
    when 'comexstat_export_prod_cafe' then 2
    when 'comexstat_export_prod_veiculos' then 3
    when 'comexstat_export_prod_ferro_aco' then 4
    when 'comexstat_export_prod_maquinas_mecanicas' then 5
    when 'comexstat_export_prod_acucares' then 6
    when 'comexstat_export_prod_carnes' then 7
    when 'comexstat_export_prod_minerios' then 8
    when 'comexstat_export_prod_graos_oleaginosas' then 9
    when 'comexstat_export_prod_comb_oleos_minerais' then 10
  end
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data", "Série"],
            "graph.metrics": ["US$ milhões"],
            "graph.x_axis.title_text": "Ano",
            "graph.x_axis.scale": "ordinal",
            "graph.y_axis.title_text": "US$ milhões",
            "stackable.stack_type": "stacked",
            # Largest commodity chapter at the bottom, descending upward, with the
            # "Demais produtos" residual as the top band. Metabase renders the FIRST
            # series_order entry at the TOP, so the array is listed top→bottom.
            "graph.series_order": [
                {"key": "Demais produtos", "enabled": True, "name": "Demais produtos"},
                {"key": "Celulose", "enabled": True, "name": "Celulose"},
                {"key": "Café", "enabled": True, "name": "Café"},
                {"key": "Veículos", "enabled": True, "name": "Veículos"},
                {"key": "Ferro e aço", "enabled": True, "name": "Ferro e aço"},
                {"key": "Máquinas mecânicas", "enabled": True, "name": "Máquinas mecânicas"},
                {"key": "Açúcares", "enabled": True, "name": "Açúcares"},
                {"key": "Carnes", "enabled": True, "name": "Carnes"},
                {"key": "Minérios", "enabled": True, "name": "Minérios"},
                {
                    "key": "Grãos e oleaginosas (soja)",
                    "enabled": True,
                    "name": "Grãos e oleaginosas (soja)",
                },
                {
                    "key": "Combustíveis e óleos minerais",
                    "enabled": True,
                    "name": "Combustíveis e óleos minerais",
                },
            ],
            "series_settings": {
                "Combustíveis e óleos minerais": {"color": "#8c564b"},
                "Grãos e oleaginosas (soja)": {"color": "#2ca02c"},
                "Minérios": {"color": "#7f7f7f"},
                "Carnes": {"color": "#d62728"},
                "Açúcares": {"color": "#e377c2"},
                "Máquinas mecânicas": {"color": "#1f77b4"},
                "Ferro e aço": {"color": "#393b79"},
                "Veículos": {"color": "#9467bd"},
                "Café": {"color": "#bcbd22"},
                "Celulose": {"color": "#17becf"},
                "Demais produtos": {"color": "#c7c7c7"},
            },
        },
    },
    # --- Consumo digital ---
    "digital_pix_value": {
        "name": "Valor das transações Pix (liquidado no SPI)",
        "display": "line",
        "description": (
            "Valor mensal das transações Pix liquidadas no SPI. "
            "Fonte: BCB, Estatísticas do SPI (PixLiquidadosAtual). "
            "Unidade: R$ bilhões nominais. Frequência: mensal. "
            "Conceito: soma diária do valor liquidado no mês, em R$ bilhões "
            "(a fonte publica em R$ mil); apenas meses completos."
        ),
        "query": line_query(["bcb_spi_pix_value_monthly"], metric="R$ bilhões"),
        "visualization_settings": {
            **line_settings("R$ bilhões", ["#2ca02c"]),
            "graph.show_legend": False,
            "series_settings": {"Valor Pix": {"line.marker_enabled": False}},
        },
    },
    "digital_pix_count": {
        "name": "Quantidade de transações Pix (liquidado no SPI)",
        "display": "line",
        "description": (
            "Quantidade mensal de transações Pix liquidadas no SPI. "
            "Fonte: BCB, Estatísticas do SPI (PixLiquidadosAtual). "
            "Unidade: milhões de transações. Frequência: mensal. "
            "Conceito: soma diária da quantidade liquidada no mês, em milhões; "
            "apenas meses completos. Contagem e valor são unidades distintas "
            "(gráficos separados)."
        ),
        "query": line_query(["bcb_spi_pix_count_monthly"], metric="Milhões de transações"),
        "visualization_settings": {
            **line_settings("Milhões de transações", ["#1f77b4"]),
            "graph.show_legend": False,
            "series_settings": {"Transações Pix": {"line.marker_enabled": False}},
        },
    },
    "digital_households_internet": {
        "name": "Domicílios com internet",
        "display": "line",
        "description": (
            "Percentual de domicílios particulares permanentes em que havia utilização "
            "da internet. Fonte: IBGE, PNAD Contínua TIC (tabela 7307). "
            "Unidade: % dos domicílios. Frequência: anual. "
            "Conceito: penetração da internet nos domicílios (TIC não coletada em 2020)."
        ),
        "query": line_query(["ibge_tic_domicilios_internet"], metric="% dos domicílios"),
        "visualization_settings": {
            **line_settings("% dos domicílios", ["#9467bd"]),
            "graph.x_axis.scale": "ordinal",
            "graph.x_axis.title_text": "Ano",
            "graph.show_legend": False,
            "series_settings": {"Domicílios com internet": {"line.marker_enabled": True}},
            "column_settings": {'["name","% dos domicílios"]': {"suffix": "%", "decimals": 1}},
        },
    },
    "digital_people_access": {
        "name": "Pessoas com internet e celular",
        "display": "line",
        "description": (
            "Percentual de pessoas de 10 anos ou mais que usaram a internet nos últimos "
            "três meses (ODS 17.8.1) e que tinham telefone móvel celular para uso pessoal "
            "(ODS 5.b.1). Fonte: IBGE, PNAD Contínua TIC (tabelas 4752 e 6863). "
            "Unidade: % das pessoas de 10+ anos. Frequência: anual. "
            "Conceito: penetração digital individual (TIC não coletada em 2020)."
        ),
        "query": line_query(
            ["ibge_tic_pessoas_internet", "ibge_tic_pessoas_celular"],
            metric="% das pessoas (10+)",
        ),
        "visualization_settings": {
            **line_settings("% das pessoas (10+)", ["#1f77b4", "#ff7f0e"]),
            "graph.x_axis.scale": "ordinal",
            "graph.x_axis.title_text": "Ano",
            "series_settings": {
                "Pessoas que usaram internet": {"line.marker_enabled": True},
                "Pessoas com celular": {"line.marker_enabled": True},
            },
            "column_settings": {'["name","% das pessoas (10+)"]': {"suffix": "%", "decimals": 1}},
        },
    },
    # --- Consumo digital: acesso / penetração (PNAD-C TIC, anual) ---
    "digital_access_devices": {
        "name": "Penetração digital nos domicílios",
        "display": "line",
        "description": (
            "Percentual de domicílios com utilização da internet e com computador. "
            "Fonte: IBGE, PNAD Contínua TIC (tabelas 7307 e 7302). "
            "Unidade: % dos domicílios. Frequência: anual. "
            "Conceito: penetração de acesso e de equipamento nos domicílios "
            "(TIC não coletada em 2020)."
        ),
        "query": line_query(
            ["ibge_tic_domicilios_internet", "ibge_tic_domicilios_computador"],
            metric="% dos domicílios",
        ),
        "visualization_settings": {
            **line_settings("% dos domicílios", ["#9467bd", "#8c564b"]),
            "graph.x_axis.scale": "ordinal",
            "graph.x_axis.title_text": "Ano",
            "series_settings": {
                "Domicílios com internet": {"line.marker_enabled": True},
                "Domicílios com computador": {"line.marker_enabled": True},
            },
            "column_settings": {'["name","% dos domicílios"]': {"suffix": "%", "decimals": 1}},
        },
    },
    "digital_access_urban_rural": {
        "name": "Acesso à internet por situação do domicílio",
        "display": "line",
        "description": (
            "Percentual de domicílios com utilização da internet, urbanos e rurais. "
            "Fonte: IBGE, PNAD Contínua TIC (tabela 7307, situação do domicílio). "
            "Unidade: % dos domicílios. Frequência: anual. "
            "Conceito: penetração da internet por situação do domicílio "
            "(TIC não coletada em 2020)."
        ),
        "query": line_query(
            ["ibge_tic_internet_urbana", "ibge_tic_internet_rural"],
            metric="% dos domicílios",
        ),
        "visualization_settings": {
            **line_settings("% dos domicílios", ["#1f77b4", "#ff7f0e"]),
            "graph.x_axis.scale": "ordinal",
            "graph.x_axis.title_text": "Ano",
            "series_settings": {
                "Urbano": {"line.marker_enabled": True},
                "Rural": {"line.marker_enabled": True},
            },
            "column_settings": {'["name","% dos domicílios"]': {"suffix": "%", "decimals": 1}},
        },
    },
    "digital_access_regions": {
        "name": "Acesso à internet por região",
        "display": "line",
        "description": (
            "Percentual de domicílios com utilização da internet, por Grande Região. "
            "Fonte: IBGE, PNAD Contínua TIC (tabela 7307, nível Grandes Regiões). "
            "Unidade: % dos domicílios. Frequência: anual. "
            "Conceito: penetração da internet por região (TIC não coletada em 2020)."
        ),
        "query": line_query(
            [
                "ibge_tic_internet_norte",
                "ibge_tic_internet_nordeste",
                "ibge_tic_internet_sudeste",
                "ibge_tic_internet_sul",
                "ibge_tic_internet_centro_oeste",
            ],
            metric="% dos domicílios",
        ),
        "visualization_settings": {
            **line_settings(
                "% dos domicílios",
                ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e"],
            ),
            "graph.x_axis.scale": "ordinal",
            "graph.x_axis.title_text": "Ano",
            "series_settings": {
                "Norte": {"line.marker_enabled": True},
                "Nordeste": {"line.marker_enabled": True},
                "Sudeste": {"line.marker_enabled": True},
                "Sul": {"line.marker_enabled": True},
                "Centro-Oeste": {"line.marker_enabled": True},
            },
            "column_settings": {'["name","% dos domicílios"]': {"suffix": "%", "decimals": 1}},
        },
    },
    "digital_connection_type": {
        "name": "Tipo de conexão dos domicílios com internet",
        "display": "line",
        "description": (
            "Percentual dos domicílios com internet que usavam banda larga fixa e banda larga "
            "móvel. Fonte: IBGE, PNAD Contínua TIC (tabela 7313). Unidade: % dos domicílios "
            "com internet. Frequência: anual. Conceito: as categorias se sobrepõem (um "
            "domicílio pode ter as duas conexões), portanto somam mais de 100% e não formam "
            "uma composição (TIC não coletada em 2020)."
        ),
        "query": line_query(
            ["ibge_tic_conexao_fixa", "ibge_tic_conexao_movel"],
            metric="% dos domicílios com internet",
        ),
        "visualization_settings": {
            **line_settings("% dos domicílios com internet", ["#17becf", "#e377c2"]),
            "graph.x_axis.scale": "ordinal",
            "graph.x_axis.title_text": "Ano",
            "series_settings": {
                "Banda larga fixa": {"line.marker_enabled": True},
                "Banda larga móvel": {"line.marker_enabled": True},
            },
            "column_settings": {
                '["name","% dos domicílios com internet"]': {"suffix": "%", "decimals": 1}
            },
        },
    },
    # --- Consumo digital: pagamentos digitais (BCB Olinda MPV/Pix, mensal e trimestral) ---
    "digital_payments_value": {
        "name": "Valor por instrumento de pagamento (mensal)",
        "display": "line",
        "description": (
            "Valor mensal das transações por instrumento de pagamento de varejo: Pix, TED, "
            "boleto e cheque. Fonte: BCB, Estatísticas de Meios de Pagamentos "
            "(MeiosdePagamentosMensalDA). Unidade: R$ bilhões nominais. Frequência: mensal. "
            "Conceito: o Pix aqui inclui liquidação dentro e fora do SPI (medida mais ampla "
            "que a série específica do SPI); valor e quantidade são gráficos separados."
        ),
        "query": line_query(
            [
                "bcb_mpv_pix_value",
                "bcb_mpv_ted_value",
                "bcb_mpv_boleto_value",
                "bcb_mpv_cheque_value",
            ],
            metric="R$ bilhões",
        ),
        "visualization_settings": {
            **line_settings("R$ bilhões", ["#2ca02c", "#1f77b4", "#ff7f0e", "#9aa0a6"]),
            "series_settings": {
                "Pix": {"line.marker_enabled": False},
                "TED": {"line.marker_enabled": False},
                "Boleto": {"line.marker_enabled": False},
                "Cheque": {"line.marker_enabled": False, "color": "#9aa0a6"},
            },
        },
    },
    "digital_payments_count": {
        "name": "Quantidade por instrumento de pagamento (mensal)",
        "display": "line",
        "description": (
            "Quantidade mensal de transações por instrumento de pagamento de varejo: Pix, "
            "TED, boleto e cheque. Fonte: BCB, Estatísticas de Meios de Pagamentos "
            "(MeiosdePagamentosMensalDA). Unidade: milhões de transações. Frequência: mensal. "
            "Conceito: contagem de transações; o Pix inclui liquidação dentro e fora do SPI. "
            "Quantidade e valor são unidades distintas (gráficos separados)."
        ),
        "query": line_query(
            [
                "bcb_mpv_pix_count",
                "bcb_mpv_ted_count",
                "bcb_mpv_boleto_count",
                "bcb_mpv_cheque_count",
            ],
            metric="Milhões de transações",
        ),
        "visualization_settings": {
            **line_settings(
                "Milhões de transações", ["#2ca02c", "#1f77b4", "#ff7f0e", "#9aa0a6"]
            ),
            "series_settings": {
                "Pix": {"line.marker_enabled": False},
                "TED": {"line.marker_enabled": False},
                "Boleto": {"line.marker_enabled": False},
                "Cheque": {"line.marker_enabled": False, "color": "#9aa0a6"},
            },
        },
    },
    "digital_payments_share": {
        "name": "Participação dos instrumentos no valor pago (área 100%)",
        "display": "area",
        "description": (
            "Participação de cada instrumento (Pix, TED, boleto, cheque) no valor mensal "
            "total pago por esses quatro instrumentos. Fonte: BCB, Estatísticas de Meios de "
            "Pagamentos (MeiosdePagamentosMensalDA). Unidade: % do valor total dos quatro "
            "instrumentos (área 100% empilhada). Frequência: mensal. Conceito: composição "
            "por valor; o Pix inclui liquidação dentro e fora do SPI."
        ),
        "query": f"""
with v as (
  select date, series_id, value
  from analytics.observations_enriched
  where series_id in (
    'bcb_mpv_pix_value',
    'bcb_mpv_ted_value',
    'bcb_mpv_boleto_value',
    'bcb_mpv_cheque_value'
  )
)
select
  date as "Data",
  case series_id
    when 'bcb_mpv_pix_value' then 'Pix'
    when 'bcb_mpv_ted_value' then 'TED'
    when 'bcb_mpv_boleto_value' then 'Boleto'
    when 'bcb_mpv_cheque_value' then 'Cheque'
  end as "Série",
  value as "R$ bilhões"
from v
where true
  {_periodo_filter_sql("date")}
order by "Data", "Série"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data", "Série"],
            "graph.metrics": ["R$ bilhões"],
            "graph.x_axis.title_text": "Data",
            "graph.y_axis.title_text": "% do valor total",
            "stackable.stack_type": "normalized",
            "series_settings": {
                "Pix": {"color": "#2ca02c"},
                "TED": {"color": "#1f77b4"},
                "Boleto": {"color": "#ff7f0e"},
                "Cheque": {"color": "#9aa0a6"},
            },
        },
    },
    "digital_payments_share_count": {
        "name": "Participação dos instrumentos na quantidade de transações (área 100%)",
        "display": "area",
        "description": (
            "Participação de cada instrumento (Pix, TED, boleto, cheque) na quantidade "
            "mensal de transações desses quatro instrumentos. Fonte: BCB, Estatísticas de "
            "Meios de Pagamentos (MeiosdePagamentosMensalDA). Unidade: % do número total de "
            "transações (área 100% empilhada). Frequência: mensal. Conceito: composição por "
            "quantidade — diferente da composição por valor, pois o Pix domina o número de "
            "transações enquanto a TED concentra grandes valores."
        ),
        "query": f"""
with v as (
  select date, series_id, value
  from analytics.observations_enriched
  where series_id in (
    'bcb_mpv_pix_count',
    'bcb_mpv_ted_count',
    'bcb_mpv_boleto_count',
    'bcb_mpv_cheque_count'
  )
)
select
  date as "Data",
  case series_id
    when 'bcb_mpv_pix_count' then 'Pix'
    when 'bcb_mpv_ted_count' then 'TED'
    when 'bcb_mpv_boleto_count' then 'Boleto'
    when 'bcb_mpv_cheque_count' then 'Cheque'
  end as "Série",
  value as "Transações (milhões)"
from v
where true
  {_periodo_filter_sql("date")}
order by "Data", "Série"
""".strip(),
        "visualization_settings": {
            "graph.dimensions": ["Data", "Série"],
            "graph.metrics": ["Transações (milhões)"],
            "graph.x_axis.title_text": "Data",
            "graph.y_axis.title_text": "% das transações",
            "stackable.stack_type": "normalized",
            "series_settings": {
                "Pix": {"color": "#2ca02c"},
                "TED": {"color": "#1f77b4"},
                "Boleto": {"color": "#ff7f0e"},
                "Cheque": {"color": "#9aa0a6"},
            },
        },
    },
    "digital_cards_value": {
        "name": "Valor das transações com cartão (trimestral)",
        "display": "line",
        "description": (
            "Valor trimestral das transações nacionais com cartão de crédito e de débito. "
            "Fonte: BCB, Estatísticas de Meios de Pagamentos (Quantidadeetransacoesdecartoes). "
            "Unidade: R$ bilhões nominais. Frequência: trimestral. Conceito: transações "
            "nacionais somadas entre bandeiras; trimestral, não comparável no mesmo gráfico "
            "com os instrumentos mensais."
        ),
        "query": line_query(
            ["bcb_mpv_cartao_credito_value", "bcb_mpv_cartao_debito_value"],
            metric="R$ bilhões",
        ),
        "visualization_settings": {
            **line_settings("R$ bilhões", ["#d62728", "#1f77b4"]),
            "series_settings": {
                "Cartão de crédito": {"line.marker_enabled": False},
                "Cartão de débito": {"line.marker_enabled": False},
            },
        },
    },
    "digital_cards_count": {
        "name": "Quantidade de transações com cartão (trimestral)",
        "display": "line",
        "description": (
            "Quantidade trimestral de transações nacionais com cartão de crédito e de débito. "
            "Fonte: BCB, Estatísticas de Meios de Pagamentos (Quantidadeetransacoesdecartoes). "
            "Unidade: milhões de transações. Frequência: trimestral. Conceito: transações "
            "nacionais somadas entre bandeiras; quantidade e valor são gráficos separados."
        ),
        "query": line_query(
            ["bcb_mpv_cartao_credito_count", "bcb_mpv_cartao_debito_count"],
            metric="Milhões de transações",
        ),
        "visualization_settings": {
            **line_settings("Milhões de transações", ["#d62728", "#1f77b4"]),
            "series_settings": {
                "Cartão de crédito": {"line.marker_enabled": False},
                "Cartão de débito": {"line.marker_enabled": False},
            },
        },
    },
    "digital_pix_users": {
        "name": "Usuários cadastrados no Pix (DICT)",
        "display": "line",
        "description": (
            "Estoque mensal de usuários cadastrados no DICT (diretório de chaves Pix), "
            "pessoas físicas e jurídicas. Fonte: BCB, Estatísticas do Pix "
            "(PixUsuariosCadastradosDICT). Unidade: milhões de usuários. Frequência: mensal. "
            "Conceito: estoque de usuários cadastrados (não é volume de transações)."
        ),
        "query": line_query(
            ["bcb_pix_usuarios_pf", "bcb_pix_usuarios_pj"],
            metric="Milhões de usuários",
        ),
        "visualization_settings": {
            **line_settings("Milhões de usuários", ["#1f77b4", "#ff7f0e"]),
            "series_settings": {
                "Pessoas físicas": {"line.marker_enabled": False},
                "Pessoas jurídicas": {"line.marker_enabled": False},
            },
        },
    },
    # --- Consumo digital: uso / consumo (PNAD-C TIC, anual) ---
    # digital_ecommerce removed: IBGE only collects this category from 2022 (3 data points),
    # too sparse to be a useful chart. Revisit when the series has more history.
}


# --- Legibility tweaks from the per-card visualization audit (38 of 40 cards) ---
# Deep-merged into each card's visualization_settings; display overrides applied after.
DISPLAY_OVERRIDES: dict[str, str] = {
    # fiscal_monthly_interest stays a bar: it sits in a small-multiple row with the
    # monthly primary/nominal bars, and Tufte parallelism wants the triad uniform.
    "fiscal_monthly_components": "line",
    "social_food_inflation": "line",
}

VIZ_PATCHES: dict[str, dict[str, Any]] = {
    "overview_selic": {
        "graph.show_legend": False,
        "series_settings": {
            "Selic meta": {"line.interpolate": "step-after", "line.marker_enabled": False}
        },
        "column_settings": {'["name","Taxa (% a.a.)"]': {"suffix": "%", "decimals": 2}},
    },
    # overview_ipca now uses IPCA_TARGET_VIZ (time-varying target); no flat 3% goal.
    "overview_exchange": {
        "graph.show_legend": False,
        "series_settings": {"Câmbio BRL/USD": {"line.marker_enabled": False}},
    },
    "overview_debt": {
        "series_settings": {
            "DBGG": {"line.marker_enabled": False, "line.style": "solid"},
            "DLSP": {"line.marker_enabled": False, "line.style": "dashed", "color": "#9aa0a6"},
        },
        "column_settings": {'["name","% do PIB"]': {"suffix": "%", "decimals": 1}},
    },
    "overview_fiscal_balance": {
        "graph.show_goal": True,
        "graph.goal_value": 0,
        "graph.goal_label": "Equilíbrio (0)",
        "column_settings": {'["name","% do PIB"]': {"suffix": "%", "decimals": 1}},
        "series_settings": {
            "Resultado primário NFSP 12m": {"line.marker_enabled": False, "line.style": "solid"},
            "Resultado nominal NFSP 12m": {
                "line.marker_enabled": False,
                "line.style": "dashed",
                "color": "#9aa0a6",
            },
        },
    },
    "fiscal_12m": {
        "graph.show_goal": True,
        "graph.goal_value": 0,
        "graph.goal_label": "Equilíbrio (0% do PIB)",
    },
    "fiscal_primary_deficit_12m": {
        "graph.show_goal": True,
        "graph.goal_value": 0,
        "graph.goal_label": "Equilíbrio (0)",
        "graph.show_legend": False,
    },
    "fiscal_nominal_deficit_12m": {
        "graph.show_legend": False,
        "series_settings": {
            "Resultado nominal NFSP 12m": {
                "line.marker_enabled": False,
                "line.interpolate": "linear",
                "line.style": "solid",
            }
        },
    },
    "fiscal_interest_12m": {
        "graph.show_legend": False,
        "column_settings": {'["name","% do PIB"]': {"suffix": "%", "decimals": 1}},
    },
    "fiscal_monthly_primary": {
        "graph.show_goal": True,
        "graph.goal_value": 0,
        "graph.goal_label": "Equilíbrio (0)",
        "graph.show_legend": False,
    },
    "fiscal_monthly_nominal": {
        "graph.show_goal": True,
        "graph.goal_value": 0,
        "graph.show_legend": False,
    },
    "fiscal_monthly_interest": {
        "graph.show_legend": False,
        "graph.show_goal": True,
        "graph.goal_value": 0,
        "series_settings": {
            "Juros nominais mensais": {
                "line.marker_enabled": False,
                "line.interpolate": "linear",
                "line.style": "solid",
            }
        },
    },
    "fiscal_monthly_components": {
        "graph.show_goal": True,
        "graph.goal_value": 0,
        "graph.goal_label": "Equilíbrio (0)",
        "series_settings": {
            "Resultado primário NFSP mensal": {"line.marker_enabled": False},
            "Resultado nominal NFSP mensal": {"line.marker_enabled": False},
            "Juros nominais mensais": {"line.marker_enabled": False},
        },
    },
    "fiscal_debt": {
        "series_settings": {
            "DBGG": {
                "line.interpolate": "linear",
                "line.marker_enabled": False,
                "line.style": "solid",
            },
            "DLSP": {
                "line.interpolate": "linear",
                "line.marker_enabled": False,
                "line.style": "dashed",
                "color": "#9aa0a6",
            },
        }
    },
    "debt_stock": {
        "series_settings": {
            "DLSP": {"line.style": "dashed", "line.marker_enabled": False, "color": "#9aa0a6"},
            "DBGG": {"line.style": "solid", "line.marker_enabled": False},
        }
    },
    "debt_dbgg": {
        "graph.show_legend": False,
        "series_settings": {
            "DBGG": {
                "line.marker_enabled": False,
                "line.interpolate": "linear",
                "line.style": "solid",
            }
        },
    },
    "debt_dlsp": {"graph.show_legend": False},
    "monetary_selic": {
        "graph.show_legend": False,
        "series_settings": {
            "Selic meta": {
                "line.interpolate": "step-after",
                "line.marker_enabled": False,
                "line.style": "solid",
            }
        },
        "column_settings": {'["name","Taxa (% a.a.)"]': {"suffix": "%", "decimals": 2}},
    },
    # monetary_ipca_12m now uses IPCA_TARGET_VIZ (time-varying target); no flat 3% goal.
    "monetary_ipca_monthly": {
        "graph.show_legend": False,
        "column_settings": {'["name","Variação (%)"]': {"suffix": "%", "decimals": 2}},
    },
    "monetary_exchange": {
        "graph.show_legend": False,
        "series_settings": {
            "Câmbio BRL/USD": {
                "line.marker_enabled": False,
                "line.interpolate": "linear",
                "line.style": "solid",
            }
        },
    },
    "monetary_ibc": {
        "graph.show_legend": False,
        "series_settings": {
            "IBC-Br dessazonalizado": {
                "line.marker_enabled": False,
                "line.interpolate": "linear",
                "line.style": "solid",
            }
        },
    },
    "activity_pib_nominal": {
        "graph.show_legend": False,
        "column_settings": {'["name","R$ milhões"]': {"number_style": "decimal", "decimals": 0}},
    },
    "labor_real_average_income": {
        "graph.show_legend": False,
        "column_settings": {'["name","R$ reais"]': {"prefix": "R$ ", "decimals": 0}},
    },
    "labor_real_income_mass": {"graph.show_legend": False},
    "central_revenue_spending": {
        "series_settings": {
            "Receita líquida": {
                "line.marker_enabled": False,
                "line.interpolate": "linear",
                "line.style": "solid",
            },
            "Despesa total": {
                "line.marker_enabled": False,
                "line.interpolate": "linear",
                "line.style": "solid",
            },
        }
    },
    "central_primary_components": {
        "graph.show_goal": True,
        "graph.goal_value": 0,
        "graph.goal_label": "Zero (equilíbrio)",
    },
    "central_revenues": {
        "series_settings": {
            "Arrecadação líquida RGPS": {"line.marker_enabled": False},
            "Receita administrada pela RFB": {"line.marker_enabled": False},
            "Receita líquida": {"line.marker_enabled": False},
            "Receita total": {"line.marker_enabled": False},
            "Transferências por repartição": {"line.marker_enabled": False},
        }
    },
    "budget_latest": {
        "graph.show_values": True,
        "graph.label_value_formatting": "compact",
        "graph.show_legend": False,
    },
    "budget_trend": {
        "series_settings": {
            "Benefícios previdenciários": {"line.marker_enabled": False},
            "Pessoal e encargos": {"line.marker_enabled": False},
            "Outras obrigatórias": {"line.marker_enabled": False},
        },
        "column_settings": {
            '["name","R$ milhões"]': {"number_style": "decimal", "decimals": 0, "prefix": "R$ "}
        },
    },
    "social_household_debt": {
        "series_settings": {
            "Endividamento exceto habitação": {
                "line.style": "dashed",
                "line.marker_enabled": False,
                "color": "#9aa0a6",
            },
            "Endividamento das famílias": {"line.style": "solid", "line.marker_enabled": False},
        }
    },
    "social_default_rate": {
        "series_settings": {
            "Inadimplência total": {"line.style": "solid", "line.marker_enabled": False},
            "Inadimplência pessoas físicas": {
                "line.style": "dashed",
                "line.marker_enabled": False,
                "color": "#9aa0a6",
            },
        },
        "column_settings": {'["name","% da carteira"]': {"suffix": "%", "decimals": 2}},
    },
    "social_food_inflation": {
        "graph.show_legend": False,
        "graph.show_goal": True,
        "graph.goal_value": 0,
        "series_settings": {
            "IPCA alimentação e bebidas": {
                "line.interpolate": "linear",
                "line.marker_enabled": False,
                "line.style": "solid",
            }
        },
        "column_settings": {'["name","Variação (% no mês)"]': {"suffix": "%", "decimals": 2}},
    },
}


def _deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


for _patch_key, _patch in VIZ_PATCHES.items():
    _card = CHARTS.get(_patch_key)
    if _card is not None:
        _deep_merge(_card.setdefault("visualization_settings", {}), _patch)

for _disp_key, _disp in DISPLAY_OVERRIDES.items():
    if _disp_key in CHARTS:
        CHARTS[_disp_key]["display"] = _disp

# line_settings adds "Série" as a breakout dimension so multi-series charts don't get
# summed into one line. For single-series line_query charts that breakout just yields a
# redundant 1-item legend, so drop it back to a plain ["Data"] dimension and hide the legend.
for _chart in CHARTS.values():
    _vs = _chart.get("visualization_settings", {})
    _query = _chart.get("query", "")
    if _vs.get("graph.dimensions") == ["Data", "Série"] and "case series_id" in _query:
        _series_count = len(re.findall(r"when '\w+' then '", _query))
        if _series_count <= 1:
            _vs["graph.dimensions"] = ["Data"]
            _vs.setdefault("graph.show_legend", False)


def _grid(rows: list[list[tuple[str, int]]], size_y: int = 6) -> list[dict[str, Any]]:
    """Lay every card out uniformly: a third of the width (size_x=8), three per row.

    The per-row groupings and widths passed in are intentionally ignored — cards are
    flattened in reading order and placed three-up so every tab is an even grid of
    same-size cards. (Widths in the tab definitions are kept only for readability.)
    """
    keys = [key for row in rows for key, _width in row]
    width = 8  # a third of the 24-column grid -> three cards per row
    per_row = 3
    out: list[dict[str, Any]] = []
    for i, key in enumerate(keys):
        r, c = divmod(i, per_row)
        out.append(
            {"key": key, "row": r * size_y, "col": c * width, "size_x": width, "size_y": size_y}
        )
    return out


# ======================================================================================
# METASYSTEMIC LAYER — the structure that organizes the content.
# DASHBOARD_TABS defines the public rooms of arandu.ai, and the grammar above (_grid,
# the *_settings helpers, the period presets, the calm palette) defines how every card
# looks. Adding, removing, renaming, or reordering a tab — or changing the visual grammar
# — is a *metasystemic* change: it changes the lens, not only the picture, and per the
# constitution it needs a proposal and (for public structure) a vote. See GOVERNANCE.md.
# Re-exported as `arandu.metasystemic.DASHBOARD_TABS`.
#
# A single dashboard with Metabase tabs. Tab order tells a story: the macro snapshot,
# then prices and the policy response, then real activity and jobs, then how that lands
# on households, then the government's accounts and the debt they build, then the
# above-the-line detail, and finally the data provenance.
# ======================================================================================
DASHBOARD_TABS: list[dict[str, Any]] = [
    {
        "name": "Visão geral",
        # One read of each story: prices/rates/FX, the fiscal+debt headline, then
        # activity/jobs, then the household squeeze.
        "cards": _grid(
            [
                [("overview_selic", 8), ("overview_ipca", 8), ("overview_exchange", 8)],
                [("cambio_brl_cny", 8)],
                [("fiscal_primary_deficit_12m", 12), ("debt_stock", 12)],
                [("activity_pib_nominal", 8), ("monetary_ibc", 8), ("labor_unemployment", 8)],
                [
                    ("labor_real_average_income", 8),
                    ("social_household_debt", 8),
                    ("social_default_rate", 8),
                ],
            ]
        ),
    },
    {
        "name": "Inflação e juros",
        # Headline IPCA vs target full-width, then the policy rate and real rate,
        # expectations and monthly detail, the decomposition and core, FX, and food.
        "cards": _grid(
            [
                [("monetary_ipca_12m", 24)],
                [("monetary_selic", 12), ("monetary_real_rate", 12)],
                [("monetary_focus_ipca", 12), ("monetary_ipca_monthly", 12)],
                [("monetary_ipca_decomposition", 12), ("monetary_ipca_core", 12)],
                [("monetary_exchange", 12), ("cambio_brl_cny", 12), ("monetary_reer", 12)],
                [("social_food_inflation", 24)],
            ]
        ),
    },
    {
        "name": "Atividade e emprego",
        # Headline: monthly GDP-proxy growth. Then output levels, unemployment and income.
        "cards": _grid(
            [
                [("activity_ibc_yoy", 24)],
                [("activity_pib_nominal", 12), ("monetary_ibc", 12)],
                [("labor_unemployment", 12), ("labor_income_yoy", 12)],
                [("labor_real_average_income", 12), ("labor_real_income_mass", 12)],
            ]
        ),
    },
    {
        "name": "Bem-estar das famílias",
        # Headline: the wage floor's purchasing power. Then debt burden, default,
        # income and food prices.
        "cards": _grid(
            [
                [("social_minimum_wage", 24)],
                [("social_household_debt", 12), ("social_debt_service", 12)],
                [("social_default_rate", 12), ("social_default_spread", 12)],
                [("labor_real_average_income", 12), ("labor_real_income_mass", 12)],
                [("social_food_inflation", 24)],
            ]
        ),
    },
    {
        "name": "Instituições",
        # Headline: BTI status/governance indices + 3 democracy criteria, by edition (biennial).
        "cards": _grid(
            [
                [("institutions_bti_brazil", 24)],
                [
                    ("institutions_bti_status_governance", 12),
                    ("institutions_bti_democracy_criteria", 12),
                ],
            ]
        ),
    },
    {
        "name": "Pulso fiscal",
        # Headline: combined 12m result + interest. Then the % of GDP small multiples,
        # the combined monthly flows, and the monthly small multiples.
        "cards": _grid(
            [
                [("fiscal_12m", 24)],
                [
                    ("fiscal_primary_deficit_12m", 8),
                    ("fiscal_nominal_deficit_12m", 8),
                    ("fiscal_interest_12m", 8),
                ],
                [("fiscal_monthly_components", 24)],
                [
                    ("fiscal_monthly_primary", 8),
                    ("fiscal_monthly_nominal", 8),
                    ("fiscal_monthly_interest", 8),
                ],
            ]
        ),
    },
    {
        "name": "Dívida",
        # Headline: the debt stock. Then gross/net measures, then the two drivers.
        "cards": _grid(
            [
                [("debt_stock", 24)],
                [("debt_dbgg", 12), ("debt_dlsp", 12)],
                [("fiscal_nominal_deficit_12m", 12), ("monetary_selic", 12)],
            ]
        ),
    },
    {
        "name": "Governo Central",
        # Headline: primary result as % of GDP. Then revenue vs spending, spending
        # composition, the primary components, revenue breakdowns and spending trend.
        "cards": _grid(
            [
                [("central_primary_pct_gdp", 24)],
                [("central_revenue_spending", 24)],
                [("central_spending_composition", 24)],
                [("central_primary_components", 12), ("central_social_security", 12)],
                [("central_revenues", 12), ("budget_latest", 12)],
                [("budget_trend", 24)],
            ]
        ),
    },
    {
        "name": "Setores produtivos",
        # Headline: sector shares of GDP. Then industry/services breakdown, growth by
        # sector, the volume indices and the monthly gauges.
        "cards": _grid(
            [
                [("sectors_va_composition", 24)],
                [
                    ("sectors_industria_composition", 12),
                    ("sectors_servicos_composition", 12),
                ],
                [("sectors_gdp_yoy", 24)],
                [("sectors_gdp_volume_index", 24)],
                [("sectors_monthly_volume", 24)],
                [
                    ("sectors_industrial_production", 8),
                    ("sectors_retail", 8),
                    ("sectors_services", 8),
                ],
            ]
        ),
    },
    {
        "name": "Comércio exterior",
        # Headline: 12m-accumulated trade flows and balance. Then monthly flows/balance,
        # commodity composition, partners, and the real effective FX.
        "cards": _grid(
            [
                [("trade_flows_12m", 24)],
                [("trade_exports_imports", 12), ("trade_balance_monthly", 12)],
                [("trade_commodities_exports", 24)],
                [("trade_partners_exports", 12), ("trade_partners_imports", 12)],
                [("trade_china_usa_trend", 12), ("trade_mercosul", 12)],
                [("trade_brics_flows", 12), ("trade_brics_share", 12)],
                [("trade_brics_by_member", 12), ("trade_brics_vs_blocs", 12)],
                [("monetary_reer", 24)],
            ]
        ),
    },
    {
        "name": "Consumo digital",
        # Three themes, each led by its strongest chart. ACESSO/PENETRAÇÃO (annual PNAD-C
        # TIC): household devices headline, then people, urban/rural, regions, connection
        # type. PAGAMENTOS DIGITAIS (monthly/quarterly BCB): the instrument-mix share
        # headline, then value/count by instrument, the SPI-only Pix detail, cards
        # (quarterly), and registered Pix users. USO/CONSUMO: e-commerce. Annual, monthly
        # and quarterly series are never mixed in the same chart (different frequencies).
        "cards": _grid(
            [
                # Acesso / penetração
                [("digital_access_devices", 24)],
                [("digital_people_access", 12), ("digital_access_urban_rural", 12)],
                [("digital_access_regions", 12), ("digital_connection_type", 12)],
                # Pagamentos digitais
                [("digital_payments_share", 12), ("digital_payments_share_count", 12)],
                [("digital_payments_value", 12), ("digital_payments_count", 12)],
                [("digital_pix_value", 12), ("digital_pix_count", 12)],
                [("digital_cards_value", 12), ("digital_cards_count", 12)],
                [("digital_pix_users", 24)],
            ]
        ),
    },
]


def env(name: str, default: str) -> str:
    return os.environ.get(name, default)


class MetabaseClient:
    def __init__(self) -> None:
        self.internal_url = env("MB_URL", "http://localhost:3000").rstrip("/")
        self.public_url = env("PUBLIC_METABASE_URL", self.internal_url).rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def wait(self, timeout_seconds: int = 240) -> None:
        deadline = time.time() + timeout_seconds
        last_error: Exception | None = None
        while time.time() < deadline:
            try:
                response = self.session.get(f"{self.internal_url}/api/health", timeout=5)
                if response.ok:
                    return
            except Exception as exc:  # noqa: BLE001
                last_error = exc
            time.sleep(3)
        raise TimeoutError(f"Metabase did not become ready: {last_error}")

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        response = self.session.request(method, f"{self.internal_url}{path}", timeout=60, **kwargs)
        if not response.ok:
            raise RuntimeError(
                f"{method} {path} failed: {response.status_code} {response.text[:500]}"
            )
        return response

    def setup_or_login(self) -> None:
        properties = self.request("GET", "/api/session/properties").json()
        token = properties.get("setup-token")
        if token:
            logger.info("running first Metabase setup")
            payload = {
                "token": token,
                "user": {
                    "email": env("MB_EMAIL", "admin@fiscallens.local"),
                    "first_name": env("MB_FIRST_NAME", "arandu.ai"),
                    "last_name": env("MB_LAST_NAME", "Admin"),
                    "password": env("MB_PASSWORD", "FiscalLensBrasil2026!"),
                },
                "prefs": {
                    "site_name": "arandu.ai",
                    "site_locale": "pt-BR",
                    "allow_tracking": False,
                },
                "database": warehouse_database_payload(),
            }
            try:
                response = self.request("POST", "/api/setup", json=payload).json()
                session_id = response.get("id") or response.get("session_id")
                if session_id:
                    self.session.headers.update({"X-Metabase-Session": session_id})
                    return
            except RuntimeError:
                logger.info("Metabase setup token was not usable; falling back to login")

        logger.info("logging into Metabase")
        response = self.request(
            "POST",
            "/api/session",
            json={
                "username": env("MB_EMAIL", "admin@fiscallens.local"),
                "password": env("MB_PASSWORD", "FiscalLensBrasil2026!"),
            },
        ).json()
        self.session.headers.update({"X-Metabase-Session": response["id"]})

    def enable_public_sharing(self) -> None:
        # enable-query-caching is read-only in recent Metabase; only public sharing matters here.
        for key, value in {
            "enable-public-sharing": True,
        }.items():
            try:
                self.request("PUT", f"/api/setting/{key}", json={"value": value})
            except Exception:
                logger.warning("could not set Metabase setting %s", key, exc_info=True)

    def ensure_database(self) -> int:
        databases = self.request("GET", "/api/database").json()
        data = databases.get("data", databases if isinstance(databases, list) else [])
        for database in data:
            if database.get("name") == "arandu.ai warehouse":
                return int(database["id"])

        response = self.request("POST", "/api/database", json=warehouse_database_payload()).json()
        return int(response["id"])

    def ensure_collection(self) -> int | None:
        try:
            collections = self.request("GET", "/api/collection").json()
            data = collections if isinstance(collections, list) else collections.get("data", [])
            for collection in data:
                if collection.get("name") == "arandu.ai":
                    return int(collection["id"])
            created = self.request(
                "POST",
                "/api/collection",
                json={
                    "name": "arandu.ai",
                    "description": "Seeded questions for the arandu.ai public dashboard.",
                    "color": "#6b665d",
                },
            ).json()
            return int(created["id"])
        except Exception:
            logger.warning(
                "could not create/find collection; cards will be in the root collection",
                exc_info=True,
            )
            return None

    def create_card(
        self,
        key: str,
        spec: dict[str, Any],
        database_id: int,
        collection_id: int | None,
    ) -> int:
        template_tags: dict[str, Any] = {}
        if "{{periodo}}" in spec["query"]:
            template_tags["periodo"] = {
                "id": "periodo",
                "name": "periodo",
                "display-name": "Período",
                "type": "text",
                "default": "Últimos 10 anos",
            }
        # Free custom date range (zoom), driven by two optional date variables.
        if "{{de}}" in spec["query"]:
            template_tags["de"] = {
                "id": "de",
                "name": "de",
                "display-name": "De",
                "type": "date",
            }
        if "{{ate}}" in spec["query"]:
            template_tags["ate"] = {
                "id": "ate",
                "name": "ate",
                "display-name": "Até",
                "type": "date",
            }
        payload: dict[str, Any] = {
            "name": spec["name"],
            "description": spec["description"],
            "display": spec["display"],
            "dataset_query": {
                "type": "native",
                "database": database_id,
                "native": {"query": spec["query"], "template-tags": template_tags},
            },
            "visualization_settings": spec.get("visualization_settings", {}),
        }
        if collection_id is not None:
            payload["collection_id"] = collection_id

        logger.info("creating Metabase card %s", key)
        response = self.request("POST", "/api/card", json=payload).json()
        return int(response["id"])

    def public_question_url(self, card_id: int) -> str:
        try:
            card = self.request("GET", f"/api/card/{card_id}").json()
            public_uuid = card.get("public_uuid")
            if not public_uuid:
                public_uuid = (
                    self.request("POST", f"/api/card/{card_id}/public_link").json().get("uuid")
                )
            if not public_uuid:
                raise RuntimeError("Metabase did not return public question uuid")
            return f"{self.public_url}/public/question/{public_uuid}"
        except Exception:
            logger.warning("could not create public link for card %s", card_id, exc_info=True)
            return ""

    def create_tabbed_dashboard(
        self,
        tabs: list[dict[str, Any]],
        card_ids: dict[str, int],
        dated_keys: set[str],
        collection_id: int | None,
    ) -> int:
        payload: dict[str, Any] = {
            "name": dashboard_name("all"),
            "description": dashboard_description("all"),
            "parameters": [
                {
                    "id": "periodo",
                    "name": "Período",
                    "slug": "periodo",
                    "type": "string/=",
                    "default": "Últimos 10 anos",
                    "values_query_type": "list",
                    "values_source_type": "static-list",
                    "values_source_config": {"values": PERIODO_VALUES},
                },
                # Free custom range for zooming into any window (overrides the preset bounds
                # by intersection). Leave empty to use just the preset.
                {"id": "de", "name": "De", "slug": "de", "type": "date/single"},
                {"id": "ate", "name": "Até", "slug": "ate", "type": "date/single"},
            ],
            "width": "full",
        }
        if collection_id is not None:
            payload["collection_id"] = collection_id

        logger.info("creating tabbed Metabase dashboard")
        dashboard = self.request("POST", "/api/dashboard", json=payload).json()
        dashboard_id = int(dashboard["id"])

        tabs_payload = [{"id": -(i + 1), "name": tab["name"]} for i, tab in enumerate(tabs)]
        cards_payload = []
        counter = 0
        for i, tab in enumerate(tabs):
            tab_id = -(i + 1)
            for dashcard in tab["cards"]:
                counter += 1
                card_id = card_ids[dashcard["key"]]
                mappings = []
                if dashcard["key"] in dated_keys:
                    mappings = [
                        {
                            "parameter_id": "periodo",
                            "card_id": card_id,
                            "target": ["variable", ["template-tag", "periodo"]],
                        },
                        {
                            "parameter_id": "de",
                            "card_id": card_id,
                            "target": ["variable", ["template-tag", "de"]],
                        },
                        {
                            "parameter_id": "ate",
                            "card_id": card_id,
                            "target": ["variable", ["template-tag", "ate"]],
                        },
                    ]
                cards_payload.append(
                    {
                        "id": -counter,
                        "card_id": card_id,
                        "dashboard_tab_id": tab_id,
                        "row": dashcard["row"],
                        "col": dashcard["col"],
                        "size_x": dashcard["size_x"],
                        "size_y": dashcard["size_y"],
                        "parameter_mappings": mappings,
                    }
                )
        self.request(
            "PUT",
            f"/api/dashboard/{dashboard_id}/cards",
            json={"cards": cards_payload, "tabs": tabs_payload},
        )
        return dashboard_id

    def public_dashboard_url(self, dashboard_id: int) -> str:
        try:
            dashboard = self.request("GET", f"/api/dashboard/{dashboard_id}").json()
            public_uuid = dashboard.get("public_uuid")
            if not public_uuid:
                public_uuid = (
                    self.request("POST", f"/api/dashboard/{dashboard_id}/public_link")
                    .json()
                    .get("uuid")
                )
            if not public_uuid:
                raise RuntimeError("Metabase did not return public dashboard uuid")
            return f"{self.public_url}/public/dashboard/{public_uuid}"
        except Exception:
            logger.warning(
                "could not create public link for dashboard %s",
                dashboard_id,
                exc_info=True,
            )
            return ""


def warehouse_database_payload() -> dict[str, Any]:
    return {
        "name": "arandu.ai warehouse",
        "engine": "postgres",
        "details": {
            "host": env("WAREHOUSE_HOST", "localhost"),
            "port": int(env("WAREHOUSE_PORT", "5433")),
            "dbname": env("WAREHOUSE_DB", "fiscallens"),
            "user": env("WAREHOUSE_USER", "fiscallens"),
            "password": env("WAREHOUSE_PASSWORD", "fiscallens"),
            "ssl": False,
            "tunnel-enabled": False,
        },
        "is_full_sync": True,
        "is_on_demand": False,
        "schedules": {},
    }


def dashboard_name(key: str) -> str:
    labels = {
        "all": "Indicadores macrofiscais do Brasil",
        "overview": "Visão geral",
        "fiscal_pulse": "Pulso fiscal",
        "debt": "Dívida",
        "inflation_monetary": "Inflação e monetário",
        "governo_central": "Governo Central",
        "federal_budget": "Orçamento federal",
        "data_catalog": "Catálogo de dados",
    }
    return labels.get(key, key)


def dashboard_description(key: str) -> str:
    descriptions = {
        "all": "Gráficos de indicadores macroeconômicos, fiscais, monetários e orçamentários.",
        "overview": "Painel Metabase com gráficos dos principais indicadores oficiais disponíveis.",
        "fiscal_pulse": "Painel Metabase com gráficos de resultado fiscal, juros e dívida.",
        "debt": "Painel Metabase com gráficos de DBGG e DLSP.",
        "inflation_monetary": "Painel Metabase com gráficos de Selic, IPCA, câmbio e atividade.",
        "governo_central": (
            "Painel Metabase com gráficos do Resultado do Tesouro Nacional para o Governo Central."
        ),
        "federal_budget": (
            "Painel Metabase com gráficos de categorias selecionadas de despesa federal."
        ),
        "data_catalog": "Painel Metabase com gráficos de cobertura do catálogo de dados.",
    }
    return descriptions.get(key, "Painel Metabase do arandu.ai.")


# Official data sources, for the per-card source logo (links to where the data lives).
CHART_SOURCES: dict[str, dict[str, str]] = {
    "MDIC": {
        "label": "MDIC / ComexStat",
        "url": "https://comexstat.mdic.gov.br",
        "domain": "mdic.gov.br",
    },
    "TESOURO": {
        "label": "Tesouro Nacional",
        "url": "https://www.tesourotransparente.gov.br",
        "domain": "tesourotransparente.gov.br",
    },
    "IBGE": {"label": "IBGE / SIDRA", "url": "https://sidra.ibge.gov.br", "domain": "ibge.gov.br"},
    "RFB": {
        "label": "Receita Federal",
        "url": "https://www.gov.br/receitafederal",
        "domain": "gov.br",
    },
    "SPA": {
        "label": "SPA / Ministério da Fazenda",
        "url": "https://www.gov.br/fazenda/pt-br/composicao/orgaos/secretaria-de-premios-e-apostas",
        "domain": "gov.br",
    },
    "PLANALTO": {
        "label": "Planalto — Legislação",
        "url": "https://www.planalto.gov.br",
        "domain": "planalto.gov.br",
    },
    "BCB": {
        "label": "Banco Central do Brasil",
        "url": "https://dadosabertos.bcb.gov.br",
        "domain": "bcb.gov.br",
    },
    "ECB": {
        "label": "Banco Central Europeu (taxas de referência)",
        "url": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html",
        "domain": "ecb.europa.eu",
    },
    "BTI": {
        "label": "BTI — Bertelsmann Stiftung",
        "url": "https://bti-project.org",
        "domain": "bti-project.org",
    },
}


def _chart_source(query: str) -> dict[str, str]:
    """Pick the primary official source for a chart from the series in its SQL."""
    if "comexstat" in query:
        return CHART_SOURCES["MDIC"]
    if "tesouro_" in query:
        return CHART_SOURCES["TESOURO"]
    if "ibge_" in query:
        return CHART_SOURCES["IBGE"]
    # RFB CNAE arrecadação (e.g. the betting tax line) is a Receita Federal source, not BCB.
    # The BCB Pix-estimate series (bets_bcb_pix_*) stays on the BCB default branch below.
    if "rfb_cnae" in query:
        return CHART_SOURCES["RFB"]
    if "ecb_" in query:
        return CHART_SOURCES["ECB"]
    if "bti_" in query:
        return CHART_SOURCES["BTI"]
    if "spa_" in query:
        return CHART_SOURCES["SPA"]
    if "lei14790_" in query:
        return CHART_SOURCES["PLANALTO"]
    return CHART_SOURCES["BCB"]


def write_links(
    path: str,
    links: dict[str, str],
    status: str,
    question_links: dict[str, str] | None = None,
    edit_links: dict[str, str] | None = None,
) -> None:
    # Map each chart's visible title -> its public question URL, so the frontend can open
    # the card full-screen (with native zoom) when a user clicks it on the dashboard.
    question_by_name = {
        CHARTS[key]["name"]: url
        for key, url in (question_links or {}).items()
        if url and key in CHARTS
    }
    # Title -> interactive (logged-in) question URL, for the "edit visualization" fullscreen.
    question_edit_by_name = {
        CHARTS[key]["name"]: url
        for key, url in (edit_links or {}).items()
        if url and key in CHARTS
    }
    # Map each chart's visible title -> its primary source (logo + link).
    card_sources = {spec["name"]: _chart_source(spec.get("query", "")) for spec in CHARTS.values()}
    # Title -> default visualization type, so the client-side viewer can start from the
    # card's intended chart before the user edits and persists their own choice locally.
    display_by_name = {spec["name"]: spec.get("display", "line") for spec in CHARTS.values()}
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": status,
        "metabase_base_url": env("PUBLIC_METABASE_URL", "http://localhost:3000"),
        "links": links,
        "question_links": question_links or {},
        "question_by_name": question_by_name,
        "question_edit_by_name": question_edit_by_name,
        "card_sources": card_sources,
        "display_by_name": display_by_name,
        "notes": (
            "Generated by arandu.metabase_setup. Primary links are public Metabase "
            "dashboards. Empty links mean Metabase setup "
            "or public sharing failed; the frontend will show setup instructions."
        ),
    }
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    links = {"all": ""}
    question_links = {key: "" for key in CHARTS}
    edit_links: dict[str, str] = {}
    output_path = env("METABASE_LINKS_PATH", "/frontend-public/metabase-dashboards.json")
    try:
        client = MetabaseClient()
        client.wait()
        client.setup_or_login()
        client.enable_public_sharing()
        database_id = client.ensure_database()
        collection_id = client.ensure_collection()
        card_ids: dict[str, int] = {}
        for key, spec in CHARTS.items():
            card_id = client.create_card(key, spec, database_id, collection_id)
            card_ids[key] = card_id
            question_links[key] = client.public_question_url(card_id)
            # Interactive (logged-in) question URL: full Metabase question view where the
            # user can change the visualization and use native chart interactions.
            edit_links[key] = f"{client.public_url}/question/{card_id}"
        dated_keys = {key for key, spec in CHARTS.items() if "{{periodo}}" in spec["query"]}
        dashboard_id = client.create_tabbed_dashboard(
            DASHBOARD_TABS, card_ids, dated_keys, collection_id
        )
        links["all"] = client.public_dashboard_url(dashboard_id)
        write_links(output_path, links, "ok", question_links, edit_links)
        logger.info("wrote Metabase public links to %s", output_path)
        return 0
    except Exception:
        logger.exception("Metabase setup failed")
        write_links(output_path, links, "failed", question_links, edit_links)
        return 1


if __name__ == "__main__":
    sys.exit(main())
