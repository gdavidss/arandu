"""Per-card plain-language descriptions for the arandu.ai Metabase cards.

Each entry has the same shape, rendered as Markdown in the card's info popover:
a plain lead line saying what the chart shows (jargon expanded inline), a
**Por que importa** section on why it matters, and a compact source line
(Fonte / Unidade / Frequência). Applied over CHARTS in arandu.metabase_setup
after the card specs are defined; unknown keys are ignored.
"""

from __future__ import annotations

CHART_DESCRIPTIONS: dict[str, str] = {
    "institutions_bti_status_governance": (
        "Mostra dois índices do BTI (Bertelsmann Transformation Index) para o Brasil, por "
        "edição: o Índice de Status (quanto de transformação já foi alcançado) e o Índice "
        "de Governança (a capacidade de conduzir politicamente essa "
        "transformação).\n\n**Por que importa:** É uma leitura comparável ao longo do tempo "
        "da qualidade das instituições. Notas mais altas indicam avanço na transformação "
        "e na condução política; notas mais baixas, o contrário.\n\nFonte: Bertelsmann "
        "Stiftung — BTI (https://bti-project.org), planilha BTI 2006–2026 Scores · "
        "Unidade: pontuação de 1 a 10 (10 = melhor) · Frequência: bienal"
    ),
    "institutions_bti_democracy_criteria": (
        "Mostra três critérios políticos do BTI (Bertelsmann Transformation Index) para o "
        "Brasil, por edição: Estado (Stateness), Estado de Direito e Estabilidade das "
        "Instituições Democráticas.\n\n**Por que importa:** Ajuda a acompanhar a solidez "
        "das instituições democráticas ao longo do tempo. Notas mais altas indicam "
        "instituições mais estáveis e mais Estado de Direito; notas mais baixas, o "
        "contrário.\n\nFonte: Bertelsmann Stiftung — BTI (https://bti-project.org), "
        "planilha BTI 2006–2026 Scores e relatórios de país · Unidade: pontuação de 1 a "
        "10 (10 = melhor) · Frequência: bienal"
    ),
    "overview_selic": (
        "Mostra a meta da taxa Selic, a taxa básica de juros da economia, definida pelo "
        "Copom (Comitê de Política Monetária do Banco Central).\n\n**Por que importa:** É a "
        "principal ferramenta de política monetária. Alta da Selic tende a conter a "
        "inflação e encarecer o crédito; queda tende a estimular a economia e baratear o "
        "crédito.\n\nFonte: BCB SGS 432 · Unidade: % ao ano · Frequência: diária"
    ),
    "overview_ipca": (
        "Mostra a inflação medida pelo IPCA acumulada em 12 meses, comparada à meta de "
        "inflação do CMN (Conselho Monetário Nacional), com o centro e a banda de "
        "tolerância, que variaram ao longo do tempo.\n\n**Por que importa:** É a referência "
        "oficial de inflação no Brasil. Quando o IPCA fica acima da banda, os preços "
        "sobem mais rápido que o previsto; abaixo do centro, mais devagar.\n\nFonte: BCB "
        "SGS 13522; metas CMN · Unidade: % · Frequência: mensal"
    ),
    "overview_exchange": (
        "Mostra a taxa de câmbio livre entre real e dólar, na cotação de venda (quantos "
        "reais custa um dólar).\n\n**Por que importa:** Afeta preços de importados, "
        "combustíveis e viagens. Alta do dólar significa real mais desvalorizado; queda, "
        "real mais valorizado.\n\nFonte: BCB SGS 1 · Unidade: R$/US$ · Frequência: diária"
    ),
    "cambio_brl_cny": (
        "Mostra a taxa de câmbio entre real e iuan chinês (CNY), na referência diária de "
        "fechamento do BCE (Banco Central Europeu), via Frankfurter — o Banco Central do "
        "Brasil não publica BRL/CNY (a PTAX cobre só cerca de 10 moedas).\n\n**Por que "
        "importa:** A China é o maior parceiro comercial do Brasil. Alta do iuan "
        "significa real mais desvalorizado frente à moeda chinesa; queda, o "
        "contrário.\n\nFonte: BCE (taxas de referência), via Frankfurter · Unidade: R$/CNY "
        "· Frequência: diária (dias úteis)"
    ),
    "overview_debt": (
        "Mostra o tamanho da dívida pública em relação ao PIB, em duas medidas: DBGG "
        "(Dívida Bruta do Governo Geral, soma dos passivos de União, estados e "
        "municípios) e DLSP (Dívida Líquida do Setor Público, que desconta os ativos do "
        "setor público consolidado, como reservas internacionais e créditos, por isso é "
        "menor).\n\n**Por que importa:** A relação entre dívida e PIB indica a capacidade "
        "do país de arcar com seus compromissos. Uma alta tende a sinalizar mais gastos "
        "financiados por dívida ou economia mais fraca; uma queda, o contrário.\n\nFonte: "
        "BCB SGS · Unidade: % do PIB · Frequência: mensal"
    ),
    "overview_fiscal_balance": (
        "Mostra a NFSP (Necessidade de Financiamento do Setor Público) do Setor Público "
        "Consolidado, acumulada em 12 meses — quanto o setor público precisa captar para "
        "cobrir seus gastos, medido pelo lado do financiamento (abaixo da linha). Sinal: "
        "+ superávit, − déficit (a série original do BCB é deficit-positiva; foi "
        "invertida aqui para padronizar).\n\n**Por que importa:** Indica se o setor público "
        "gastou mais do que arrecadou no período. Um déficit maior tende a sinalizar "
        "necessidade de captar mais recursos; um superávit, o contrário.\n\nFonte: BCB SGS "
        "· Unidade: % do PIB"
    ),
    "fiscal_12m": (
        "Mostra três medidas do Setor Público Consolidado acumuladas em 12 meses: "
        "resultado primário, resultado nominal e juros nominais — tudo pela NFSP "
        "(Necessidade de Financiamento do Setor Público, apurada abaixo da linha, isto é, "
        "pelo lado do financiamento). Sinal dos resultados: + superávit, − déficit. "
        "Identidade: nominal = primário − juros.\n\n**Por que importa:** Separa o resultado "
        "das contas antes dos juros (primário) do peso dos juros da dívida. Um primário "
        "melhor sem melhora no nominal tende a indicar juros pesando sobre as "
        "contas.\n\nFonte: BCB SGS · Unidade: % do PIB"
    ),
    "fiscal_primary_deficit_12m": (
        "Mostra o resultado primário do Setor Público Consolidado (arrecadação menos "
        "gastos, antes dos juros da dívida) acumulado em 12 meses, pela NFSP (Necessidade "
        "de Financiamento do Setor Público, apurada abaixo da linha, ou seja, pelo lado "
        "do financiamento). Sinal: + superávit, − déficit.\n\n**Por que importa:** É o "
        "principal termômetro do esforço fiscal antes dos juros. Um superávit maior tende "
        "a indicar contas mais equilibradas; um déficit, gastos acima da "
        "arrecadação.\n\nFonte: BCB SGS 5793 · Unidade: % do PIB"
    ),
    "fiscal_monthly_primary": (
        "Mostra o resultado primário mensal do Setor Público Consolidado (arrecadação "
        "menos gastos, antes dos juros da dívida), pela NFSP (Necessidade de "
        "Financiamento do Setor Público, apurada abaixo da linha, isto é, pelo lado do "
        "financiamento). Sinal: + superávit, − déficit.\n\n**Por que importa:** Mostra mês "
        "a mês se as contas fecharam acima ou abaixo do equilíbrio antes dos juros. Ajuda "
        "a acompanhar a trajetória fiscal ao longo do ano, sujeita a "
        "sazonalidade.\n\nFonte: BCB SGS · Unidade: R$ milhões nominais"
    ),
    "fiscal_monthly_nominal": (
        "Mostra o resultado nominal mensal do Setor Público Consolidado (que já inclui os "
        "juros da dívida), pela NFSP (Necessidade de Financiamento do Setor Público, "
        "apurada abaixo da linha, ou seja, pelo lado do financiamento). Sinal: + "
        "superávit, − déficit.\n\n**Por que importa:** É o resultado das contas depois de "
        "contar os juros — a medida mais próxima do que de fato pressiona a dívida. "
        "Déficits mensais tendem a indicar mais necessidade de captação.\n\nFonte: BCB SGS "
        "· Unidade: R$ milhões nominais"
    ),
    "fiscal_monthly_interest": (
        "Quanto o setor público consolidado (União, estados, municípios e estatais) "
        "gastou, em cada mês, pagando juros sobre sua dívida.\n\n**Por que importa:** É o "
        "custo de carregar a dívida pública. Quando sobe, tende a refletir juros mais "
        "altos, mais dívida ou câmbio pressionando os papéis indexados; esse gasto "
        "disputa espaço com outras despesas do Estado.\n\nFonte: BCB SGS · Unidade: R$ "
        "milhões nominais · Frequência: mensal"
    ),
    "fiscal_debt": (
        "Estoque da dívida pública em relação ao tamanho da economia, por duas medidas: a "
        "DBGG (Dívida Bruta do Governo Geral, soma dos passivos de União, estados e "
        "municípios) e a DLSP (Dívida Líquida do Setor Público, que desconta os ativos do "
        "setor público consolidado, como reservas e créditos, por isso é menor).\n\n**Por "
        "que importa:** Indica o peso da dívida sobre a economia. Alta sustentada tende a "
        "sinalizar dificuldade de pagar mais do que se arrecada; queda, o "
        "contrário.\n\nFonte: BCB SGS · Unidade: % do PIB"
    ),
    "debt_stock": (
        "Estoque da dívida pública em relação ao tamanho da economia, por duas medidas: a "
        "DBGG (Dívida Bruta do Governo Geral, soma dos passivos do governo geral) e a "
        "DLSP (Dívida Líquida do Setor Público, que desconta os ativos do setor público "
        "consolidado, por isso é menor).\n\n**Por que importa:** Mostra o peso da dívida "
        "sobre a economia. Uma alta sustentada tende a sinalizar que o setor público "
        "gasta mais do que arrecada; uma queda, o contrário.\n\nFonte: BCB SGS · Unidade: % "
        "do PIB"
    ),
    "debt_dbgg": (
        "Dívida Bruta do Governo Geral (soma dos passivos de União, estados e municípios) "
        "em relação ao tamanho da economia.\n\n**Por que importa:** É a medida mais ampla "
        "do endividamento público, sem descontar os ativos do governo. Alta sustentada "
        "tende a sinalizar que se gasta mais do que se arrecada; queda, o "
        "contrário.\n\nFonte: BCB SGS 13762 · Unidade: % do PIB"
    ),
    "debt_dlsp": (
        "Dívida Líquida do Setor Público (o que o setor público deve depois de descontar "
        "seus ativos, como reservas e créditos) em relação ao tamanho da economia.\n\n**Por "
        "que importa:** Mostra o endividamento público já líquido dos ativos do Estado. "
        "Uma alta sustentada tende a sinalizar mais dívida do que caixa; uma queda, o "
        "contrário.\n\nFonte: BCB SGS 4513 · Unidade: % do PIB"
    ),
    "monetary_selic": (
        "Taxa básica de juros da economia (Selic meta), definida pelo Copom, o comitê de "
        "política monetária do Banco Central.\n\n**Por que importa:** É a principal "
        "ferramenta contra a inflação e baliza o custo do crédito. Alta encarece "
        "empréstimos e tende a frear preços e atividade; queda barateia o crédito e tende "
        "a estimular a economia.\n\nFonte: BCB SGS 432 · Unidade: % ao ano"
    ),
    "monetary_ipca_12m": (
        "A inflação medida pelo IPCA, acumulada nos últimos 12 meses, comparada à meta de "
        "inflação do CMN (Conselho Monetário Nacional): o centro da meta e a banda de "
        "tolerância, que mudaram ao longo do tempo.\n\n**Por que importa:** Mostra o quanto "
        "os preços subiram no ano e se a inflação está dentro do alvo oficial. Valores "
        "acima da banda tendem a indicar pressão de preços; valores abaixo, o "
        "contrário.\n\nFonte: BCB SGS 13522; metas CMN · Unidade: %"
    ),
    "monetary_exchange": (
        "Quantos reais custa um dólar americano, pela taxa de câmbio livre (cotação de "
        "venda).\n\n**Por que importa:** O câmbio afeta preços de importados, combustíveis "
        "e viagens. Uma alta (mais reais por dólar) tende a encarecer produtos vindos de "
        "fora; uma queda, o contrário.\n\nFonte: BCB SGS 1 · Unidade: R$/US$"
    ),
    "monetary_ibc": (
        "Índice de Atividade Econômica do Banco Central (IBC-Br), uma medida mensal que "
        "acompanha o ritmo da economia, com ajuste sazonal (correção de efeitos do "
        "calendário e da estação do ano).\n\n**Por que importa:** Funciona como uma prévia "
        "mensal do PIB. Uma alta tende a indicar aquecimento da economia; uma queda, "
        "desaceleração.\n\nFonte: BCB SGS 24364 · Unidade: índice"
    ),
    "activity_pib_nominal": (
        "PIB (soma de tudo o que a economia produz) mensal em valores correntes, ou seja, "
        "a preços do próprio mês, sem descontar a inflação. Estimativa do Banco "
        "Central.\n\n**Por que importa:** Dá o tamanho da economia mês a mês em reais. Por "
        "ser nominal, parte da variação vem do aumento de preços, não só de mais "
        "produção.\n\nFonte: BCB SGS 4380 · Unidade: R$ milhões nominais · Frequência: "
        "mensal"
    ),
    "labor_unemployment": (
        "Taxa de desemprego (o IBGE chama de \"taxa de desocupação\") das pessoas de 14 "
        "anos ou mais, isto é, a parcela de quem procura trabalho e não encontra.\n\n**Por "
        "que importa:** É um dos principais termômetros do mercado de trabalho. Uma alta "
        "tende a indicar mais dificuldade para encontrar emprego; uma queda, o "
        "contrário.\n\nFonte: IBGE SIDRA/PNAD Contínua, tabela 6381, variável 4099 · "
        "Unidade: % · Frequência: trimestre móvel com divulgação mensal"
    ),
    "labor_real_average_income": (
        "Rendimento médio mensal do trabalho já descontada a inflação (rendimento real), "
        "considerando o valor habitual de todos os trabalhos.\n\n**Por que importa:** "
        "Mostra o poder de compra médio de quem trabalha. Uma alta tende a indicar ganho "
        "real de renda; uma queda, perda de poder de compra.\n\nFonte: IBGE SIDRA/PNAD "
        "Contínua, tabela 6390, variável 5933 · Unidade: R$ reais · Frequência: trimestre "
        "móvel com divulgação mensal"
    ),
    "labor_real_income_mass": (
        "Soma de todos os rendimentos do trabalho no país em um mês, já descontada a "
        "inflação (rendimento real).\n\n**Por que importa:** Combina quanto as pessoas "
        "ganham e quantas estão trabalhando. Uma alta tende a indicar mais gente ocupada "
        "e/ou salários maiores em poder de compra; uma queda, o contrário.\n\nFonte: IBGE "
        "SIDRA/PNAD Contínua, tabela 6392, variável 6293 · Unidade: R$ milhões reais · "
        "Frequência: trimestre móvel com divulgação mensal"
    ),
    "central_revenue_spending": (
        "Receita líquida e despesa total do Governo Central lado a lado, somadas nos "
        "últimos 12 meses para remover a forte variação de mês a mês "
        "(sazonalidade).\n\n**Por que importa:** O espaço entre as duas linhas é o "
        "resultado primário. Receita acima da despesa aponta superávit; despesa acima da "
        "receita, déficit.\n\nFonte: Tesouro Nacional RTN · Unidade: R$ milhões nominais, "
        "acumulado em 12 meses"
    ),
    "central_primary_components": (
        "Resultado primário do Governo Central e suas partes (Tesouro Nacional e "
        "Previdência Social), somados nos últimos 12 meses para remover a variação de mês "
        "a mês (sazonalidade). O sinal + é superávit e − é déficit.\n\n**Por que importa:** "
        "Mostra de onde vem o resultado das contas. Ajuda a distinguir o peso do Tesouro "
        "e o da Previdência na melhora ou piora do primário.\n\nFonte: Tesouro Nacional RTN "
        "· Unidade: R$ milhões nominais, acumulado em 12 meses. (O resultado do Banco "
        "Central, ~mil vezes menor, foi omitido por ser ilegível nesta escala.)"
    ),
    "central_primary_pct_gdp": (
        "Resultado primário do Governo Central (receitas menos despesas, antes dos juros "
        "da dívida) acumulado em 12 meses, medido como fatia do PIB. O sinal + é "
        "superávit e − é déficit.\n\n**Por que importa:** Como PIB, permite comparar o "
        "resultado fiscal ao longo do tempo em escala relativa. Um número mais negativo "
        "indica maior déficit em relação ao tamanho da economia.\n\nFonte: Tesouro Nacional "
        "(RTN) e Banco Central (PIB mensal, SGS 4380) · Unidade: % do PIB · Frequência: "
        "mensal, acumulado 12m. Conceito: primário acima da linha do Governo Central, não "
        "a NFSP (Necessidade de Financiamento do Setor Público) do Setor Público "
        "Consolidado."
    ),
    "central_spending_composition": (
        "Quanto cada categoria pesa dentro da despesa primária total do Governo Central "
        "(gastos exceto juros da dívida), somada nos últimos 12 meses.\n\n**Por que "
        "importa:** Mostra para onde vai o gasto público e como essa divisão muda com o "
        "tempo. Uma categoria que ganha espaço deixa proporcionalmente menos para as "
        "demais.\n\nFonte: Tesouro Nacional (RTN) · Unidade: % da despesa primária total "
        "(área 100% empilhada) · Frequência: mensal, acumulado 12m. Conceito: Demais = "
        "despesa total menos previdência, pessoal e outras obrigatórias."
    ),
    "central_revenues": (
        "Principais fontes de receita do Governo Central, somadas nos últimos 12 meses "
        "para remover a variação de mês a mês (sazonalidade): receita administrada pela "
        "Receita Federal, arrecadação líquida da previdência (RGPS) e transferências "
        "repartidas com estados e municípios.\n\n**Por que importa:** Mostra de onde o "
        "governo tira dinheiro e como cada fonte evolui. Movimentos na arrecadação tendem "
        "a acompanhar a atividade econômica e mudanças de tributação.\n\nFonte: Tesouro "
        "Nacional RTN · Unidade: R$ milhões nominais, acumulado 12m. Não inclui os "
        "agregados Receita total/líquida (vistos em outro painel)."
    ),
    "central_social_security": (
        "Mostra, mês a mês, o que a Previdência arrecada e o que paga em benefícios no "
        "Governo Central: a arrecadação líquida do RGPS (Regime Geral de Previdência "
        "Social, a previdência dos trabalhadores da iniciativa privada) e o total pago em "
        "benefícios previdenciários.\n\n**Por que importa:** A distância entre as duas "
        "linhas mostra o resultado da Previdência. Benefícios crescendo mais rápido que a "
        "arrecadação tende a sinalizar maior pressão sobre as contas públicas.\n\nFonte: "
        "Tesouro Nacional RTN · Unidade: R$ milhões nominais"
    ),
    "budget_latest": (
        "Mostra quanto o governo federal gastou em cada categoria de despesa selecionada "
        "no mês mais recente.\n\n**Por que importa:** Ajuda a ver onde o dinheiro público "
        "foi aplicado no período. Comparar categorias mostra o peso relativo de cada tipo "
        "de gasto no orçamento federal.\n\nFonte: Tesouro Nacional · Unidade: R$ milhões "
        "nominais · Frequência: mensal"
    ),
    "budget_trend": (
        "Mostra a evolução da despesa federal por categoria selecionada, somada nos "
        "últimos 12 meses para remover a forte variação de mês para mês "
        "(sazonalidade).\n\n**Por que importa:** Acompanhar 12 meses acumulados revela a "
        "tendência de cada tipo de gasto sem o ruído mensal. Uma categoria em alta "
        "sustentada indica peso crescente no orçamento federal.\n\nFonte: Tesouro Nacional "
        "RTN · Unidade: R$ milhões nominais, acumulado em 12 meses"
    ),
    "social_household_debt": (
        "Mostra quanto as famílias devem ao SFN (Sistema Financeiro Nacional, o conjunto "
        "de bancos e instituições financeiras) em relação à renda acumulada em 12 meses, "
        "com e sem o crédito para compra de imóveis (habitacional).\n\n**Por que importa:** "
        "É o estoque de dívida das famílias frente à renda. Uma alta indica que as "
        "famílias devem uma parcela maior do que ganham; uma queda, o contrário.\n\nFonte: "
        "BCB SGS 29037 e 29038 · Unidade: % da renda · Frequência: mensal"
    ),
    "social_default_rate": (
        "Mostra a inadimplência da carteira de crédito do SFN (Sistema Financeiro "
        "Nacional, o conjunto de bancos e instituições financeiras): a parcela dos "
        "empréstimos com atraso superior a 90 dias, no total e só entre pessoas "
        "físicas.\n\n**Por que importa:** Indica a dificuldade de quem tomou crédito em "
        "pagar em dia. Uma alta costuma acompanhar renda mais apertada ou juros mais "
        "altos; uma queda, o contrário.\n\nFonte: BCB SGS 21082 e 21084 · Unidade: % da "
        "carteira · Frequência: mensal"
    ),
    "social_food_inflation": (
        "Mostra a inflação de alimentos: a variação de preços do grupo Alimentação e "
        "bebidas do IPCA, acumulada em 12 meses.\n\n**Por que importa:** É uma medida da "
        "pressão dos preços de alimentos sobre o orçamento das famílias (não mede "
        "insegurança alimentar). Uma alta indica comida mais cara; uma queda, alívio no "
        "custo dos alimentos.\n\nFonte: BCB SGS 1635 · Unidade: % em 12 meses · Frequência: "
        "mensal"
    ),
    "bets_market_growth": (
        "Tamanho do mercado de apostas no Brasil pela receita bruta de jogo (GGR = valor "
        "apostado menos prêmios pagos), em dois retratos: 2022 (antes da regulamentação) "
        "e 2025 (primeiro ano regulado).\n\n**Por que importa:** Dá a ordem de grandeza do "
        "crescimento do setor. As pontas têm origens distintas: 2022 é estimativa de "
        "operadora (Entain, US$ 1,5 bi, ~R$ 7,7 bi ao câmbio médio de 2022) para o "
        "mercado não regulado; 2025 é dado oficial (R$ 36,96 bi). A comparação indica "
        "escala, não um número exato.\n\nFontes: Entain (2022, via Infomoney) e SPA/MF, 2º "
        "Panorama jan/2026 (2025) · Unidade: R$ bilhões (GGR) · Frequência: dois retratos "
        "anuais (não é série temporal)."
    ),
    "bets_tax_revenue": (
        "Tributo federal arrecadado pela Receita Federal junto à divisão 92 da CNAE "
        "(\"Atividades de exploração de jogos de azar e apostas\"), por ano, de 2016 a "
        "2025. O eixo Y usa escala logarítmica para mostrar todos os anos apesar da "
        "diferença de grandeza.\n\n**Por que importa:** Mede quanto o setor paga em tributo "
        "federal — não o GGR (receita bruta de jogo) nem o volume apostado. De 2016 a "
        "2024 ficou entre R$ 2 mi e R$ 106 mi por ano; em 2025, primeiro ano de "
        "tributação do mercado regulado de quota fixa, chegou a cerca de R$ 10,0 "
        "bi.\n\nFonte: Receita Federal — Arrecadação por Divisão Econômica da CNAE (dados "
        "abertos, planilha XLSX), divisão 92 · Unidade: R$ milhões nominais (escala log) "
        "· Frequência: anual."
    ),
    "bets_pix_estimate": (
        "Estimativa pontual do Banco Central para a média mensal de 2024 dos valores "
        "movimentados via Pix, em R$ bilhões: loterias da Caixa (R$ 1,9 bi), empresas de "
        "apostas registradas no CNAE 92 (R$ 0,3 bi) e empresas de apostas fora do CNAE 92 "
        "(R$ 20,8 bi) — estas últimas concentram a maior parte.\n\n**Por que importa:** É "
        "uma proxy do volume apostado (recebimentos brutos via Pix), distinta do GGR e do "
        "tributo. O BCB estima que ~15% do valor apostado fica com as casas; o restante "
        "retorna como prêmio.\n\nFonte: BCB, Estudo Especial 119 — \"Análise técnica sobre o "
        "mercado de apostas online no Brasil e o perfil dos apostadores\", tabela "
        "comparativa, dados de agosto de 2024 · Unidade: R$ bilhões (média mensal de "
        "2024) · Frequência: estimativa pontual (não é série temporal)."
    ),
    "bets_spa_market": (
        "Tamanho do mercado regulado de apostas de quota fixa em 2025, em R$ bilhões: GGR "
        "(receita bruta de jogo = apostas menos prêmios pagos) do 1º semestre (R$ 17,4 "
        "bi) e do ano (R$ 36,96 bi), e as destinações legais de 12% no ano (R$ 4,53 "
        "bi).\n\n**Por que importa:** Mostra a escala do setor e quanto vai para as "
        "destinações legais. No 1º semestre, 17,7 milhões de CPFs únicos apostaram, "
        "chegando a 25,2 milhões no ano.\n\nFonte: SPA/MF — 1º Panorama Semestral "
        "(ago/2025) e 2º Panorama (jan/2026), "
        "https://www.gov.br/fazenda/pt-br/composicao/orgaos/secretaria-de-premios-e-apost"
        "as · Unidade: R$ bilhões · Frequência: retratos acumulados de período (não série "
        "temporal)."
    ),
    "bets_spa_accounts_funnel": (
        "Comparação, no mercado regulado de apostas em 2025, entre contas ativas e "
        "pessoas físicas distintas: 100.775.427 contas ativas nas marcas/bets, 87.671.439 "
        "contas ativas em operadores/empresas e 25.245.319 CPFs únicos que "
        "apostaram.\n\n**Por que importa:** Há muito mais contas do que apostadores — em "
        "média, várias contas por pessoa. A diferença ajuda a interpretar números de "
        "\"contas\" como medida do tamanho do público.\n\nFonte: SPA/MF — 2º Panorama "
        "(jan/2026), "
        "https://www.gov.br/fazenda/pt-br/composicao/orgaos/secretaria-de-premios-e-apost"
        "as · Unidade: contagem · Frequência: retrato acumulado do ano (não série "
        "temporal)."
    ),
    "bets_pbf": (
        "Estimativa pontual do Banco Central para agosto de 2024: 5 milhões de "
        "beneficiários do Bolsa Família enviaram R$ 3 bilhões via Pix a empresas de "
        "apostas (mediana de R$ 100 por pessoa); destes, 4 milhões (70%) são chefes de "
        "família — quem de fato recebe o benefício — e enviaram R$ 2 bilhões (67% do "
        "total). O gráfico mostra, lado a lado, pessoas (em milhões) e valor enviado (em "
        "R$ bilhões), para o total e para os chefes de família.\n\n**Por que importa:** "
        "Descreve o perfil dos apostadores, sem afirmar relação de causa e efeito. Cerca "
        "de 17% dos cadastrados no PBF (base dez/2023) apostaram no período.\n\nFonte: BCB, "
        "Estudo Especial 119 — \"Análise técnica sobre o mercado de apostas online no "
        "Brasil e o perfil dos apostadores\" (bcb.gov.br), dados de agosto de 2024 · "
        "Unidade: milhões de pessoas e R$ bilhões · Frequência: estimativa pontual de "
        "ago/2024 (não atualizada pela rotina diária)."
    ),
    "bets_lei_allocation": (
        "Mostra como a lei reparte, por área, a parcela da arrecadação das apostas de "
        "quota fixa destinada a políticas públicas (% da fatia destinada): esporte 36%, "
        "turismo 28%, segurança pública 13,6%, educação 10%, seguridade social 10%, saúde "
        "1%, sociedade civil 0,5%, Funapol/Polícia Federal 0,5% e ABDI 0,4% (soma "
        "100%).\n\n**Por que importa:** Indica quais áreas a lei prioriza ao dividir esses "
        "recursos. É a alocação prevista em lei, não a execução efetiva do que foi de "
        "fato repassado a cada área.\n\nFonte: Lei nº 14.790/2023, Art. 30, "
        "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14790.htm · "
        "Unidade: % da arrecadação destinada · Frequência: estrutura legal (não série "
        "temporal, não execução efetiva)"
    ),
    "monetary_real_rate": (
        "Mostra o juro real: a Selic meta (taxa básica de juros, média mensal) menos o "
        "IPCA (inflação oficial) acumulado em 12 meses.\n\n**Por que importa:** O juro real "
        "indica quanto rende o dinheiro acima da inflação. Um valor mais alto tende a "
        "encarecer o crédito e atrair poupança; mais baixo, o contrário. É uma "
        "aproximação ex-post (o resultado já observado, um spread), não um "
        "estoque.\n\nFonte: BCB SGS 432 e 13522 · Unidade: pontos percentuais ao ano · "
        "Frequência: mensal"
    ),
    "monetary_focus_ipca": (
        "Compara a inflação que o mercado espera para os próximos 12 meses (mediana "
        "suavizada do boletim Focus do Banco Central, último boletim de cada mês) com o "
        "IPCA (inflação oficial) já observado nos últimos 12 meses.\n\n**Por que importa:** "
        "A expectativa é prospectiva (olha à frente) e o realizado é retrospectivo (olha "
        "para trás) — mesmos 12 meses, sentidos opostos, então não é o erro de previsão "
        "ponto a ponto. A distância entre as linhas ajuda a ler quanto o mercado projeta "
        "de mudança no ritmo de preços.\n\nFonte: BCB Olinda/Expectativas "
        "(ExpectativasMercadoInflacao12Meses) e BCB SGS 13522 · Unidade: % · Frequência: "
        "mensal"
    ),
    "monetary_reer": (
        "Mostra o câmbio efetivo real do real: um índice que compara o real com uma cesta "
        "de moedas dos principais parceiros comerciais, descontando a inflação "
        "(deflacionada pelo IPCA).\n\n**Por que importa:** É efetivo (multilateral, várias "
        "moedas), não bilateral, e não se confunde com a cotação nominal do dólar "
        "(BRL/USD). Valores mais altos indicam o real mais valorizado em termos reais "
        "frente aos parceiros, o que tende a baratear importações e encarecer "
        "exportações.\n\nFonte: BCB SGS 11752 · Unidade: índice (junho/1994 = 100) · "
        "Frequência: mensal"
    ),
    "social_debt_service": (
        "Mostra quanto da renda das famílias é comprometido com o serviço da dívida — os "
        "pagamentos de juros mais amortização — junto ao Sistema Financeiro Nacional, sem "
        "ajuste sazonal.\n\n**Por que importa:** Mede o fluxo de pagamentos sobre a renda, "
        "distinto do endividamento, que é o estoque da dívida sobre a renda de 12 meses. "
        "Uma parcela maior deixa menos renda livre para consumo; menor, o "
        "contrário.\n\nFonte: BCB SGS 29265 · Unidade: % da renda mensal · Frequência: "
        "mensal (média móvel trimestral)"
    ),
    "monetary_ipca_decomposition": (
        "Mostra o IPCA (inflação oficial) cheio ao lado de dois grupos que o compõem — "
        "Alimentação e bebidas e Serviços — na variação acumulada em 12 meses (composição "
        "multiplicativa das variações mensais).\n\n**Por que importa:** Separar os grupos "
        "ajuda a ver de onde vem a pressão de preços. Os recortes são comparáveis entre "
        "si, mas não somam ao índice cheio, pois cobrem apenas parte da cesta.\n\nFonte: "
        "BCB SGS 433, 1635, 10844 · Unidade: % em 12 meses · Frequência: mensal"
    ),
    "monetary_ipca_core": (
        "Compara a inflação cheia (IPCA) com seu núcleo por médias aparadas com "
        "suavização — medida que retira do mês os itens que mais subiram e mais caíram "
        "para revelar a tendência de fundo dos preços. Variação mensal.\n\n**Por que "
        "importa:** O cheio oscila com choques pontuais (alimentos, combustíveis); o "
        "núcleo mostra a inflação mais persistente. Quando o núcleo sobe, tende a "
        "sinalizar pressão disseminada de preços, acompanhada pelo Copom.\n\nFonte: BCB SGS "
        "433 e 4466 · Unidade: % no mês · Frequência: mensal"
    ),
    "activity_ibc_yoy": (
        "Variação do IBC-Br (índice mensal do Banco Central usado como prévia do PIB) "
        "frente ao mesmo mês do ano anterior, calculada sobre a série original, sem "
        "ajuste sazonal.\n\n**Por que importa:** É um termômetro rápido da atividade "
        "econômica antes do PIB oficial. Valores positivos indicam economia maior que um "
        "ano antes; negativos, menor.\n\nFonte: BCB SGS 24363 · Unidade: % (12 meses) · "
        "Frequência: mensal"
    ),
    "labor_income_yoy": (
        "Variação do rendimento médio real habitual do trabalho (já descontada a "
        "inflação) frente ao mesmo período do ano anterior, pela PNAD Contínua do "
        "IBGE.\n\n**Por que importa:** Mostra se o salário médio ganhou ou perdeu poder de "
        "compra ao longo de um ano. Alta indica rendimento crescendo acima da inflação; "
        "queda, o contrário.\n\nFonte: IBGE/PNAD Contínua (tabela 6390) · Unidade: % (12 "
        "meses) · Frequência: trimestre móvel, divulgação mensal"
    ),
    "social_default_spread": (
        "Diferença, em pontos percentuais, entre a inadimplência das pessoas físicas e a "
        "inadimplência total da carteira de crédito do SFN (Sistema Financeiro "
        "Nacional).\n\n**Por que importa:** Mostra o quanto as famílias atrasam mais (ou "
        "menos) que o crédito em geral. Um spread maior tende a indicar que as pessoas "
        "físicas enfrentam mais dificuldade de pagamento que empresas.\n\nFonte: BCB SGS "
        "21084 e 21082 · Unidade: pontos percentuais · Frequência: mensal"
    ),
    "social_minimum_wage": (
        "Salário mínimo em valor nominal (o pago no mês) e em valor real, deflacionado "
        "pelo IPCA para os preços do mês mais recente — ou seja, o poder de compra. No "
        "mês mais recente as duas linhas coincidem.\n\n**Por que importa:** Separa o "
        "reajuste em reais do ganho ou perda de poder de compra. Quando o real sobe, o "
        "mínimo compra mais que antes; quando cai, a inflação corrói o reajuste.\n\nFonte: "
        "BCB SGS 1619 (salário mínimo) e 433 (IPCA mensal) · Unidade: R$ · Frequência: "
        "mensal"
    ),
    "sectors_gdp_volume_index": (
        "Índice de volume trimestral do PIB e do valor adicionado por setor "
        "(agropecuária, indústria, serviços), em série encadeada com ajuste sazonal "
        "(limpa efeitos de safra e calendário). Mede o quantum produzido, sem efeito de "
        "preços.\n\n**Por que importa:** Acompanha a trajetória real de cada setor da "
        "economia ao longo do tempo. Como cada setor tem base própria, comparam-se as "
        "trajetórias, não os níveis entre setores.\n\nFonte: IBGE SIDRA, tabela 1621, "
        "variável 584, classificação 11255 · Unidade: número-índice (média 1995 = 100) · "
        "Frequência: trimestral"
    ),
    "sectors_gdp_yoy": (
        "Quanto o valor adicionado (a produção líquida) de cada setor cresceu ou caiu no "
        "acumulado de 4 trimestres frente aos 4 trimestres anteriores.\n\n**Por que "
        "importa:** Mostra o ritmo do crescimento por setor (agropecuária, indústria, "
        "serviços) sem o ruído sazonal. Números positivos indicam expansão da produção "
        "real; negativos, retração.\n\nFonte: IBGE SIDRA, tabela 1620, variável 583, "
        "classificação 11255 · Unidade: % (acumulado em 4 trimestres) · Frequência: "
        "trimestral"
    ),
    "sectors_va_composition": (
        "Fatia de cada setor produtivo (agropecuária, indústria, serviços) no valor "
        "adicionado bruto do país, a preços do momento, trimestre a trimestre.\n\n**Por que "
        "importa:** Revela o peso de cada setor na economia e como isso muda ao longo do "
        "tempo. O pico da agropecuária no início do ano reflete a safra agrícola, não uma "
        "mudança estrutural.\n\nFonte: IBGE SIDRA, tabela 1846, variável 585, classificação "
        "11255 (códigos 90687, 90691, 90696) · Unidade: % do valor adicionado a preços "
        "básicos (área 100% empilhada) · Frequência: trimestral"
    ),
    "sectors_industria_composition": (
        "Fatia de cada subsetor da indústria (extrativa, transformação, construção e "
        "eletricidade/gás/água/resíduos) na produção líquida da indústria, a preços do "
        "momento, trimestre a trimestre.\n\n**Por que importa:** Mostra como a indústria se "
        "divide internamente e como esse desenho muda com o tempo. Um subsetor que ganha "
        "ou perde participação sinaliza deslocamento da atividade industrial.\n\nFonte: "
        "IBGE SIDRA, tabela 1846, variável 585, classificação 11255 (códigos 90692, "
        "90693, 90694, 90695) · Unidade: % do valor adicionado da indústria (área 100% "
        "empilhada) · Frequência: trimestral"
    ),
    "sectors_servicos_composition": (
        "Fatia de cada subsetor de serviços na produção líquida do setor de serviços, a "
        "preços do momento, trimestre a trimestre: comércio; transporte (transporte, "
        "armazenagem e correio); informação e comunicação; financeiro e seguros; "
        "imobiliárias; administração pública (administração, defesa, saúde e educação "
        "públicas e seguridade social); e outros serviços.\n\n**Por que importa:** Serviços "
        "são a maior parte da economia; ver seu recorte interno mostra quais atividades "
        "ganham ou perdem peso ao longo do tempo.\n\nFonte: IBGE SIDRA, tabela 1846, "
        "variável 585, classificação 11255 (códigos 90697-90703) · Unidade: % do valor "
        "adicionado dos serviços (área 100% empilhada) · Frequência: trimestral"
    ),
    "sectors_monthly_volume": (
        "Índices mensais de quanto se produziu de fato (volume, já ajustado para o padrão "
        "do calendário) na indústria (PIM-PF), no comércio varejista restrito (PMC) e nos "
        "serviços (PMS).\n\n**Por que importa:** É a leitura mais rápida do ritmo da "
        "atividade em três grandes frentes. Como usam a mesma base (2022 = 100), dá para "
        "comparar suas trajetórias lado a lado. Alta indica mais produção/vendas; queda, "
        "menos.\n\nFonte: IBGE SIDRA, tabelas 8888 (var 12607), 8880 (var 7170) e 8163 (var "
        "7168) · Unidade: número-índice (2022 = 100) · Frequência: mensal"
    ),
    "sectors_retail": (
        "Índice de quanto foi vendido de fato no comércio varejista restrito (volume, já "
        "ajustado para o padrão do calendário), mês a mês.\n\n**Por que importa:** É um "
        "termômetro do consumo das famílias. Alta indica mais vendas em volume real; "
        "queda, menos — sem confundir com variação de preços.\n\nFonte: IBGE SIDRA, tabela "
        "8880, variável 7170, categoria 56734 · Unidade: número-índice (2022 = 100) · "
        "Frequência: mensal"
    ),
    "sectors_services": (
        "Mostra o volume de serviços prestados no Brasil, em número-índice com ajuste "
        "sazonal (corrigido para efeitos de calendário e de estação do ano). Reflete "
        "quantidade real, não faturamento.\n\n**Por que importa:** Os serviços são a maior "
        "parte da economia brasileira. Uma alta do índice tende a indicar mais atividade "
        "no setor; uma queda, menos.\n\nFonte: IBGE SIDRA, tabela 8163, variável 7168, "
        "categorias 56726 e 56703 · Unidade: número-índice (2022 = 100) · Frequência: "
        "mensal."
    ),
    "trade_flows_12m": (
        "Mostra exportações, importações e o saldo da balança comercial de bens "
        "(exportações menos importações), somados nos últimos 12 meses para tirar o "
        "efeito da estação do ano.\n\n**Por que importa:** Acompanha a relação comercial do "
        "Brasil com o mundo. Saldo positivo (superávit) significa que o país vendeu mais "
        "bens do que comprou; saldo negativo (déficit), o contrário.\n\nFonte: BCB SGS "
        "22708, 22709 e 22707 (base Balanço de Pagamentos) · Unidade: US$ milhões "
        "(acumulado 12m) · Frequência: mensal."
    ),
    "trade_balance_monthly": (
        "Mostra o saldo mensal da balança comercial de bens, ou seja, exportações menos "
        "importações a cada mês.\n\n**Por que importa:** Indica se o país vendeu mais bens "
        "ao exterior do que comprou. Sinal +: superávit (vendeu mais); sinal −: déficit "
        "(comprou mais).\n\nFonte: BCB SGS 22707 (base Balanço de Pagamentos) · Unidade: "
        "US$ milhões · Frequência: mensal."
    ),
    "trade_partners_exports": (
        "Mostra quanto o Brasil exportou em bens (valor FOB, sem frete e seguro) por país "
        "de destino a cada ano, para os cinco maiores parceiros (China, Estados Unidos, "
        "Argentina, Países Baixos e Espanha); os demais destinos entram em \"Demais "
        "países\".\n\n**Por que importa:** Revela para quem o Brasil vende e o peso de cada "
        "mercado. Mudanças na fatia de um parceiro indicam maior ou menor dependência "
        "daquele destino.\n\nFonte: MDIC/SECEX Comex Stat · Unidade: US$ milhões · "
        "Frequência: anual (apenas anos completos)."
    ),
    "trade_partners_imports": (
        "Mostra quanto o Brasil importou em bens (valor FOB, sem frete e seguro) por país "
        "de origem a cada ano, para os cinco maiores parceiros (China, Estados Unidos, "
        "Alemanha, Argentina e Rússia); os demais entram em \"Demais países\".\n\n**Por que "
        "importa:** Revela de quem o Brasil compra e o peso de cada fornecedor. Mudanças "
        "na fatia de um parceiro indicam maior ou menor dependência daquela "
        "origem.\n\nFonte: MDIC/SECEX Comex Stat · Unidade: US$ milhões · Frequência: anual "
        "(apenas anos completos)."
    ),
    "trade_china_usa_trend": (
        "Mostra a corrente de comércio (exportações mais importações de bens, valor FOB, "
        "sem frete e seguro) do Brasil com seus dois maiores parceiros, China e Estados "
        "Unidos, ano a ano.\n\n**Por que importa:** Mede o tamanho total do vínculo "
        "comercial com cada país. Uma corrente crescente indica troca de bens mais "
        "intensa; uma queda, menos.\n\nFonte: MDIC/SECEX Comex Stat · Unidade: US$ milhões "
        "· Frequência: anual (apenas anos completos)."
    ),
    "trade_mercosul": (
        "Exportações e importações de bens do Brasil com o bloco Mercosul (Mercado Comum "
        "do Sul), além do saldo (exportações − importações), por ano.\n\n**Por que "
        "importa:** Mostra o peso dos vizinhos sul-americanos no comércio brasileiro. Um "
        "saldo positivo indica que o Brasil vende mais do que compra do bloco; a "
        "composição do Mercosul muda com o tempo (Venezuela suspensa desde 2016; Bolívia "
        "membro pleno a partir de 2024).\n\nFonte: MDIC/SECEX Comex Stat, agrupamento por "
        "bloco econômico (Mercosul) · Unidade: US$ milhões · Frequência: anual (apenas "
        "anos completos)"
    ),
    "trade_brics_flows": (
        "Exportações e importações de bens do Brasil com os países do BRICS, além do "
        "saldo (exportações − importações), por ano.\n\n**Por que importa:** Mostra o peso "
        "do grupo no comércio brasileiro. Um saldo positivo indica que o Brasil vende "
        "mais do que compra desses países. Aqui BRICS = China, Índia, Rússia e África do "
        "Sul (definição central; o Brasil não entra por ser o país declarante, e os "
        "membros do BRICS ampliado de 2024/2025 não estão incluídos).\n\nFonte: MDIC/SECEX "
        "Comex Stat (https://comexstat.mdic.gov.br/), soma dos parceiros nomeados · "
        "Unidade: US$ milhões · Frequência: anual (apenas anos completos)"
    ),
    "trade_brics_share": (
        "Fatia dos países do BRICS nas exportações e nas importações brasileiras de bens, "
        "por ano.\n\n**Por que importa:** Indica o quanto do comércio do Brasil está "
        "concentrado nesse grupo. Uma fatia crescente sinaliza maior dependência desses "
        "parceiros. Aqui BRICS = China, Índia, Rússia e África do Sul (definição central; "
        "o Brasil não entra no agregado; membros do BRICS ampliado de 2024/2025 não "
        "incluídos).\n\nFonte: MDIC/SECEX Comex Stat (https://comexstat.mdic.gov.br/) · "
        "Unidade: % do total · Frequência: anual (apenas anos completos)"
    ),
    "trade_brics_by_member": (
        "Corrente de comércio (exportações + importações de bens) do Brasil com cada "
        "país-membro do BRICS, por ano, empilhada.\n\n**Por que importa:** Separa o quanto "
        "cada parceiro pesa no comércio com o grupo, revelando quem puxa o total. Aqui "
        "BRICS = China, Índia, Rússia e África do Sul (definição central; o Brasil não "
        "entra no agregado; membros do BRICS ampliado de 2024/2025 não "
        "incluídos).\n\nFonte: MDIC/SECEX Comex Stat (https://comexstat.mdic.gov.br/), por "
        "país · Unidade: US$ milhões · Frequência: anual (apenas anos completos)"
    ),
    "trade_brics_vs_blocs": (
        "Corrente de comércio (exportações + importações de bens) do Brasil com quatro "
        "agrupamentos de parceiros — BRICS, Mercosul, União Europeia e Estados Unidos — "
        "por ano.\n\n**Por que importa:** Compara o tamanho relativo de cada mercado para o "
        "Brasil. Os grupos se sobrepõem e não somam ao total, então serve para comparar "
        "magnitude, não composição. Aqui BRICS = China, Índia, Rússia e África do Sul "
        "(definição central; membros do BRICS ampliado de 2024/2025 não "
        "incluídos).\n\nFonte: MDIC/SECEX Comex Stat (https://comexstat.mdic.gov.br/) · "
        "Unidade: US$ milhões · Frequência: anual (apenas anos completos)"
    ),
    "trade_commodities_exports": (
        "Exportações brasileiras de bens por capítulo de produto (SH2, o agrupamento de "
        "dois dígitos da classificação de mercadorias), total anual, para os dez maiores "
        "capítulos e os demais produtos.\n\n**Por que importa:** Mostra de quais produtos o "
        "Brasil mais depende para exportar (combustíveis, grãos, minérios, carnes, "
        "açúcares, máquinas, ferro e aço, veículos, café, celulose). Concentração alta "
        "sinaliza maior exposição a oscilações de preço desses itens.\n\nFonte: MDIC/SECEX "
        "Comex Stat, agrupamento por capítulo SH2 (details=chapter) · Unidade: US$ "
        "milhões · Frequência: anual (apenas anos completos)"
    ),
    "digital_pix_value": (
        "Mostra o valor mensal das transações Pix liquidadas no SPI (Sistema de "
        "Pagamentos Instantâneos, a infraestrutura do Banco Central que processa o "
        "Pix).\n\n**Por que importa:** O valor movimentado indica quanto dinheiro circula "
        "por esse meio de pagamento. Uma alta sugere maior uso do Pix na economia; uma "
        "queda, o contrário.\n\nFonte: BCB, Estatísticas do SPI (PixLiquidadosAtual) · "
        "Unidade: R$ bilhões nominais · Frequência: mensal"
    ),
    "digital_pix_count": (
        "Mostra a quantidade mensal de transações Pix liquidadas no SPI (Sistema de "
        "Pagamentos Instantâneos, a infraestrutura do Banco Central que processa o "
        "Pix).\n\n**Por que importa:** O número de transações indica com que frequência as "
        "pessoas usam o Pix no dia a dia. Uma alta sugere maior adoção; uma queda, o "
        "contrário. Contagem e valor são unidades distintas (gráficos separados).\n\nFonte: "
        "BCB, Estatísticas do SPI (PixLiquidadosAtual) · Unidade: milhões de transações · "
        "Frequência: mensal"
    ),
    "digital_households_internet": (
        "Mostra a parcela dos domicílios particulares permanentes em que havia uso da "
        "internet.\n\n**Por que importa:** Indica quão disseminado é o acesso à internet "
        "nos lares. Uma alta aponta maior inclusão digital; uma queda, o contrário. O "
        "dado de TIC não foi coletado em 2020.\n\nFonte: IBGE, PNAD Contínua TIC (tabela "
        "7307) · Unidade: % dos domicílios · Frequência: anual"
    ),
    "digital_people_access": (
        "Mostra a parcela das pessoas de 10 anos ou mais que usaram a internet nos "
        "últimos três meses (indicador ODS 17.8.1) e que tinham celular para uso pessoal "
        "(indicador ODS 5.b.1).\n\n**Por que importa:** Mede o acesso digital individual, "
        "não só por domicílio. Uma alta indica maior inclusão das pessoas; uma queda, o "
        "contrário. O dado de TIC não foi coletado em 2020.\n\nFonte: IBGE, PNAD Contínua "
        "TIC (tabelas 4752 e 6863) · Unidade: % das pessoas de 10+ anos · Frequência: "
        "anual"
    ),
    "digital_access_devices": (
        "Mostra a parcela dos domicílios com uso da internet e a parcela com "
        "computador.\n\n**Por que importa:** Compara o acesso à rede com a posse de "
        "equipamento. Uma diferença entre as duas indica lares que se conectam por outros "
        "meios, como o celular. Uma alta aponta maior inclusão digital; uma queda, o "
        "contrário. O dado de TIC não foi coletado em 2020.\n\nFonte: IBGE, PNAD Contínua "
        "TIC (tabelas 7307 e 7302) · Unidade: % dos domicílios · Frequência: anual"
    ),
    "digital_access_urban_rural": (
        "Mostra a parcela dos domicílios com uso da internet, separando os urbanos dos "
        "rurais.\n\n**Por que importa:** A diferença entre campo e cidade revela a "
        "desigualdade de acesso à internet no território. Uma distância que diminui "
        "indica avanço da inclusão nas áreas rurais. O dado de TIC não foi coletado em "
        "2020.\n\nFonte: IBGE, PNAD Contínua TIC (tabela 7307, situação do domicílio) · "
        "Unidade: % dos domicílios · Frequência: anual"
    ),
    "digital_access_regions": (
        "Percentual de domicílios com acesso à internet, separado por Grande Região do "
        "país.\n\n**Por que importa:** Mostra o quanto o acesso à internet chega de forma "
        "desigual pelo território. Diferenças persistentes entre regiões costumam "
        "sinalizar lacunas de infraestrutura e de renda.\n\nFonte: IBGE, PNAD Contínua TIC "
        "(tabela 7307, nível Grandes Regiões) · Unidade: % dos domicílios · Frequência: "
        "anual (TIC não coletada em 2020)."
    ),
    "digital_connection_type": (
        "Entre os domicílios que já têm internet, a fatia que usa banda larga fixa (por "
        "cabo/fibra) e a que usa banda larga móvel (via rede de celular).\n\n**Por que "
        "importa:** Indica que tipo de conexão sustenta o acesso das famílias. As "
        "categorias se sobrepõem (um domicílio pode ter as duas), por isso somam mais de "
        "100% e não formam uma composição.\n\nFonte: IBGE, PNAD Contínua TIC (tabela 7313) "
        "· Unidade: % dos domicílios com internet · Frequência: anual (TIC não coletada "
        "em 2020)."
    ),
    "digital_payments_value": (
        "Valor movimentado a cada mês por instrumento de pagamento do varejo: Pix, TED, "
        "boleto e cheque.\n\n**Por que importa:** Mostra por onde passa o dinheiro nos "
        "pagamentos do dia a dia e como esse peso migra entre os meios. Mudanças indicam "
        "como pessoas e empresas escolhem pagar.\n\nFonte: BCB, Estatísticas de Meios de "
        "Pagamentos (MeiosdePagamentosMensalDA) · Unidade: R$ bilhões nominais · "
        "Frequência: mensal. O Pix aqui inclui liquidação dentro e fora do SPI (medida "
        "mais ampla que a série específica do SPI); valor e quantidade são gráficos "
        "separados."
    ),
    "digital_payments_count": (
        "Número de transações feitas a cada mês por instrumento de pagamento do varejo: "
        "Pix, TED, boleto e cheque.\n\n**Por que importa:** Conta quantas vezes cada meio é "
        "usado, e não quanto vale — um retrato do hábito de pagar. Mudanças mostram como "
        "pessoas e empresas escolhem transacionar.\n\nFonte: BCB, Estatísticas de Meios de "
        "Pagamentos (MeiosdePagamentosMensalDA) · Unidade: milhões de transações · "
        "Frequência: mensal. O Pix inclui liquidação dentro e fora do SPI; quantidade e "
        "valor são unidades distintas (gráficos separados)."
    ),
    "digital_payments_share": (
        "Fatia de cada instrumento (Pix, TED, boleto, cheque) no valor total pago por "
        "esses quatro meios a cada mês.\n\n**Por que importa:** Revela quem domina o "
        "dinheiro que circula nos pagamentos e como essa divisão muda. Uma fatia que "
        "cresce sinaliza a substituição de um meio por outro.\n\nFonte: BCB, Estatísticas "
        "de Meios de Pagamentos (MeiosdePagamentosMensalDA) · Unidade: % do valor total "
        "dos quatro instrumentos (área 100% empilhada) · Frequência: mensal. O Pix inclui "
        "liquidação dentro e fora do SPI."
    ),
    "digital_payments_share_count": (
        "Fatia de cada instrumento (Pix, TED, boleto, cheque) no número total de "
        "transações desses quatro meios a cada mês.\n\n**Por que importa:** Mostra qual "
        "meio é mais usado no dia a dia — diferente da divisão por valor. O Pix domina a "
        "quantidade de transações, enquanto a TED concentra grandes valores.\n\nFonte: BCB, "
        "Estatísticas de Meios de Pagamentos (MeiosdePagamentosMensalDA) · Unidade: % do "
        "número total de transações (área 100% empilhada) · Frequência: mensal."
    ),
    "digital_cards_value": (
        "Valor total, a cada trimestre, das compras feitas no Brasil com cartão de "
        "crédito e de débito.\n\n**Por que importa:** Acompanha quanto as pessoas "
        "movimentam com cartões, uma das principais formas de pagamento no varejo. Uma "
        "alta costuma acompanhar mais consumo; uma queda, o contrário.\n\nFonte: BCB, "
        "Estatísticas de Meios de Pagamentos (Quantidadeetransacoesdecartoes) · Unidade: "
        "R$ bilhões nominais · Frequência: trimestral"
    ),
    "digital_cards_count": (
        "Número total, a cada trimestre, de compras feitas no Brasil com cartão de "
        "crédito e de débito.\n\n**Por que importa:** Mostra com que frequência os cartões "
        "são usados no dia a dia, independentemente do valor gasto. Uma alta indica mais "
        "transações; uma queda, menos uso.\n\nFonte: BCB, Estatísticas de Meios de "
        "Pagamentos (Quantidadeetransacoesdecartoes) · Unidade: milhões de transações · "
        "Frequência: trimestral"
    ),
    "digital_pix_users": (
        "Quantos usuários, pessoas físicas e empresas, têm chaves Pix cadastradas no DICT "
        "(o diretório que liga cada chave a uma conta), mês a mês.\n\n**Por que importa:** "
        "Mede o alcance do Pix na população e nos negócios. Este é o estoque de "
        "cadastrados, não o volume de transações; uma alta indica que mais gente entrou "
        "no sistema de pagamentos instantâneos.\n\nFonte: BCB, Estatísticas do Pix "
        "(PixUsuariosCadastradosDICT) · Unidade: milhões de usuários · Frequência: mensal"
    ),
    "petrobras_financeiro": (
        "Resultados anuais da Petrobras: a receita de vendas consolidada e o lucro "
        "líquido, em R$ bilhões, de 2022 a 2024.\n\n**Por que importa:** A Petrobras é a "
        "maior empresa do Brasil e uma das maiores pagadoras de tributos e dividendos ao "
        "país; sua receita e seu lucro afetam a arrecadação pública, o investimento e o "
        "setor de energia.\n\nFonte: Petrobras — Relações com Investidores / Agência "
        "Petrobras (divulgação de resultados) · Unidade: R$ bilhões · Frequência: anual"
    ),
    "matriz_eletrica_fontes": (
        "Participação de cada fonte na matriz elétrica brasileira em 2024, pela Oferta "
        "Interna de Energia Elétrica (OIEE = toda a geração nacional mais a importação "
        "líquida): hidráulica, eólica, solar, biomassa e gás natural.\n\n**Por que "
        "importa:** Mostra o quanto a eletricidade do país vem de fontes renováveis (a "
        "matriz é cerca de 88% renovável) e como eólica e solar vêm ganhando espaço — o "
        "que afeta preço, emissões e segurança do abastecimento.\n\nFonte: EPE — Balanço "
        "Energético Nacional (BEN) 2025, ano base 2024 · Unidade: % da Oferta Interna de "
        "Energia Elétrica · Frequência: anual"
    ),
    "industria_transformacao_pib": (
        "Mostra quanto a indústria de transformação (as fábricas que transformam "
        "matérias-primas em produtos) representa do PIB brasileiro a cada ano, em % — o "
        "valor adicionado da manufatura sobre o total da economia.\n\n**Por que importa:** "
        "A queda dessa fatia ao longo do tempo é o indicador mais usado para acompanhar a "
        "desindustrialização do país, tema que afeta empregos qualificados, tecnologia e "
        "a estrutura da economia.\n\nFonte: IBGE — Sistema de Contas Nacionais / Indicador "
        "ODS 9.2.1 (SIDRA, Tabela 6587) · Unidade: % do PIB · Frequência: anual"
    ),
    "vc_deployed_brasil": (
        "Volume total de venture capital (aportes de fundos em startups em estágio "
        "inicial e de crescimento) captado por startups brasileiras a cada ano, em "
        "bilhões de dólares.\n\n**Por que importa:** O venture capital financia a criação e "
        "a expansão de empresas de tecnologia; o volume anual mostra o apetite dos "
        "investidores pelo ecossistema de inovação — do pico de 2021 (US$ 9,4 bi) à forte "
        "retração dos anos seguintes (o \"inverno\" global do VC).\n\nFonte: Distrito — "
        "relatório Inside Venture Capital (fonte privada; não há estatística oficial de "
        "VC no Brasil). Série de equity em US$; 2025 ainda não foi fechado pela Distrito "
        "· Unidade: US$ bilhões · Frequência: anual"
    ),
    "mensageria_uso_internet": (
        "Percentual de usuários de Internet no Brasil (pessoas de 10 anos ou mais que "
        "usaram a Internet nos últimos três meses) que enviaram mensagens instantâneas — "
        "atividade que engloba aplicativos como WhatsApp e Telegram.\n\n**Por que "
        "importa:** A mensageria instantânea é a atividade mais difundida da Internet "
        "brasileira e o principal canal de conversa, informação e serviços; o indicador "
        "mostra seu alcance quase universal sem depender de números não oficiais de "
        "audiência das empresas.\n\nFonte: Cetic.br/NIC.br — TIC Domicílios, indicador C5 "
        "(não existe DAU/MAU oficial do WhatsApp) · Unidade: % dos usuários de Internet · "
        "Frequência: anual"
    ),
}
