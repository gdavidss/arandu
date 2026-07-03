"""Per-card plain-language descriptions for the arandu.ai Metabase cards.

Each entry is short enough to fit the card's info tooltip without truncation:
a plain lead line (what the chart shows) and a **Por que importa** line (why it
matters). Kept under ~255 characters — the tooltip clips longer text with an
ellipsis. Provenance is shown separately via the card's source logo. Applied
over CHARTS in arandu.metabase_setup after the specs are defined.
"""

from __future__ import annotations

CHART_DESCRIPTIONS: dict[str, str] = {
    "institutions_bti_status_governance": (
        "Índices de Status e de Governança do BTI para o Brasil, por edição.\n\n**Por que "
        "importa:** Leitura comparável da qualidade das instituições: notas mais altas "
        "indicam mais transformação alcançada e melhor condução política; mais baixas, o "
        "contrário."
    ),
    "institutions_bti_democracy_criteria": (
        "Três critérios políticos do BTI para o Brasil, por edição: Estado, Estado de "
        "Direito e Estabilidade das Instituições Democráticas.\n\n**Por que importa:** "
        "Notas mais altas indicam instituições mais estáveis e mais Estado de Direito; "
        "mais baixas, o oposto."
    ),
    "overview_selic": (
        "Meta da taxa Selic, os juros básicos da economia, definida pelo Copom.\n\n**Por "
        "que importa:** Principal ferramenta de política monetária: alta tende a conter a "
        "inflação e encarecer o crédito; queda estimula a economia e barateia o crédito."
    ),
    "overview_ipca": (
        "Inflação pelo IPCA acumulada em 12 meses, com o centro e a banda da meta do "
        "CMN.\n\n**Por que importa:** Referência oficial de inflação: acima da banda, os "
        "preços sobem mais rápido que o previsto; abaixo do centro, mais devagar."
    ),
    "overview_exchange": (
        "Taxa de câmbio livre real/dólar, cotação de venda (quantos reais custa um "
        "dólar).\n\n**Por que importa:** Afeta preços de importados, combustíveis e "
        "viagens: alta do dólar é real mais desvalorizado; queda, real mais valorizado."
    ),
    "cambio_brl_cny": (
        "Câmbio real/iuan (CNY), pela referência diária do BCE — o BCB não publica "
        "BRL/CNY.\n\n**Por que importa:** A China é o maior parceiro comercial do Brasil: "
        "alta do iuan é real mais desvalorizado frente à moeda chinesa; queda, o "
        "contrário."
    ),
    "overview_debt": (
        "Dívida pública em % do PIB por duas medidas: DBGG (bruta do governo geral) e "
        "DLSP (líquida, desconta ativos, por isso menor).\n\n**Por que importa:** Indica a "
        "capacidade de pagar: alta sinaliza mais gasto por dívida ou economia mais fraca."
    ),
    "overview_fiscal_balance": (
        "NFSP do Setor Público Consolidado em 12 meses, o quanto o setor público precisa "
        "captar para cobrir gastos. Sinal: + superávit, − déficit.\n\n**Por que importa:** "
        "Mostra se gastou mais do que arrecadou: déficit maior sinaliza necessidade de "
        "captar mais."
    ),
    "fiscal_12m": (
        "Resultado primário, nominal e juros do Setor Público Consolidado, acumulados em "
        "12 meses. Sinal: + superávit, − déficit.\n\n**Por que importa:** Separa as contas "
        "antes dos juros (primário) do peso dos juros da dívida (nominal = primário − "
        "juros)."
    ),
    "fiscal_primary_deficit_12m": (
        "Resultado primário do Setor Público Consolidado (arrecadação menos gastos, antes "
        "dos juros) acumulado em 12 meses. Sinal: + superávit, − déficit.\n\n**Por que "
        "importa:** Termômetro do esforço fiscal antes dos juros; superávit indica contas "
        "equilibradas."
    ),
    "fiscal_monthly_primary": (
        "Resultado primário mensal do Setor Público Consolidado (arrecadação menos "
        "gastos, antes dos juros). Sinal: + superávit, − déficit.\n\n**Por que importa:** "
        "Mostra mês a mês se as contas fecharam acima ou abaixo do equilíbrio antes dos "
        "juros."
    ),
    "fiscal_monthly_nominal": (
        "Resultado nominal mensal do Setor Público Consolidado, já incluídos os juros da "
        "dívida. Sinal: + superávit, − déficit.\n\n**Por que importa:** É o resultado após "
        "os juros, o mais próximo do que pressiona a dívida. Déficits indicam mais "
        "captação."
    ),
    "fiscal_monthly_interest": (
        "Quanto o setor público consolidado gastou, em cada mês, pagando juros sobre a "
        "dívida.\n\n**Por que importa:** É o custo de carregar a dívida pública. Sobe com "
        "juros mais altos, mais dívida ou câmbio; disputa espaço com outras despesas."
    ),
    "fiscal_debt": (
        "Estoque da dívida pública sobre o PIB em duas medidas: DBGG (dívida bruta do "
        "governo geral) e DLSP (líquida, que desconta ativos).\n\n**Por que importa:** Peso "
        "da dívida sobre a economia. Alta sustentada sinaliza gastar mais do que se "
        "arrecada."
    ),
    "debt_stock": (
        "Estoque da dívida pública sobre o PIB em duas medidas: DBGG (dívida bruta do "
        "governo geral) e DLSP (líquida, que desconta ativos).\n\n**Por que importa:** Peso "
        "da dívida sobre a economia. Alta sustentada sinaliza gastar mais do que se "
        "arrecada."
    ),
    "debt_dbgg": (
        "Dívida Bruta do Governo Geral (passivos de União, estados e municípios) sobre o "
        "PIB.\n\n**Por que importa:** É a medida mais ampla do endividamento público, sem "
        "descontar ativos. Alta sustentada sinaliza gastar mais do que se arrecada; "
        "queda, o contrário."
    ),
    "debt_dlsp": (
        "Dívida Líquida do Setor Público — o que o setor público deve já descontados seus "
        "ativos (reservas, créditos) — em % do PIB.\n\n**Por que importa:** Alta sustentada "
        "tende a indicar mais dívida do que caixa; queda, o contrário."
    ),
    "monetary_selic": (
        "Taxa básica de juros da economia (Selic meta), definida pelo Copom.\n\n**Por que "
        "importa:** Alta encarece o crédito e tende a frear a inflação e a atividade; "
        "queda barateia o crédito e estimula a economia."
    ),
    "monetary_ipca_12m": (
        "Inflação pelo IPCA acumulada em 12 meses, ante a meta do CMN (centro e banda de "
        "tolerância, que mudaram no tempo).\n\n**Por que importa:** Acima da banda indica "
        "pressão de preços; abaixo do centro, o contrário."
    ),
    "monetary_exchange": (
        "Quantos reais custa um dólar, pela taxa de câmbio livre (cotação de "
        "venda).\n\n**Por que importa:** Afeta preços de importados, combustíveis e "
        "viagens. Alta encarece o que vem de fora; queda, o contrário."
    ),
    "monetary_ibc": (
        "IBC-Br, índice mensal do Banco Central que acompanha o ritmo da economia, com "
        "ajuste sazonal.\n\n**Por que importa:** Funciona como prévia do PIB. Alta indica "
        "economia mais aquecida; queda, desaceleração."
    ),
    "activity_pib_nominal": (
        "PIB mensal a preços correntes (do próprio mês, sem descontar a inflação), "
        "estimado pelo Banco Central.\n\n**Por que importa:** Dá o tamanho da economia em "
        "reais. Por ser nominal, parte da variação vem de preços, não só de produção."
    ),
    "labor_unemployment": (
        "Taxa de desemprego (desocupação, IBGE) das pessoas de 14 anos ou mais: quem "
        "procura trabalho e não encontra.\n\n**Por que importa:** Alta indica mais "
        "dificuldade para conseguir emprego; queda, o contrário."
    ),
    "labor_real_average_income": (
        "Rendimento médio mensal do trabalho já descontada a inflação (rendimento real), "
        "pelo valor habitual de todos os trabalhos.\n\n**Por que importa:** Mostra o poder "
        "de compra de quem trabalha. Alta indica ganho real; queda, perda."
    ),
    "labor_real_income_mass": (
        "Soma de todos os rendimentos do trabalho no país em um mês, já descontada a "
        "inflação (rendimento real).\n\n**Por que importa:** Combina salários e número de "
        "ocupados; alta indica mais gente trabalhando e/ou maior poder de compra, queda o "
        "contrário."
    ),
    "central_revenue_spending": (
        "Receita líquida e despesa total do Governo Central, acumuladas em 12 meses (sem "
        "sazonalidade).\n\n**Por que importa:** O espaço entre as linhas é o resultado "
        "primário: receita acima da despesa aponta superávit, despesa acima da receita, "
        "déficit."
    ),
    "central_primary_components": (
        "Resultado primário do Governo Central e suas partes (Tesouro e Previdência), "
        "acumulado em 12 meses. Sinal +: superávit, −: déficit.\n\n**Por que importa:** "
        "Mostra de onde vem o resultado, separando o peso do Tesouro e o da Previdência "
        "na melhora ou piora."
    ),
    "central_primary_pct_gdp": (
        "Resultado primário do Governo Central (receitas menos despesas, antes dos "
        "juros), acumulado em 12 meses, como % do PIB. Sinal +: superávit, −: "
        "déficit.\n\n**Por que importa:** Permite comparar o resultado fiscal no tempo; "
        "mais negativo, maior déficit."
    ),
    "central_spending_composition": (
        "Peso de cada categoria na despesa primária total do Governo Central (gastos "
        "exceto juros), acumulada em 12 meses.\n\n**Por que importa:** Mostra para onde vai "
        "o gasto público e como muda; uma categoria que cresce deixa menos espaço para as "
        "demais."
    ),
    "central_revenues": (
        "Principais fontes de receita do Governo Central, acumuladas em 12 meses: receita "
        "administrada, previdência (RGPS) e transferências a estados e municípios.\n\n**Por "
        "que importa:** Mostra de onde vem o dinheiro; a arrecadação segue a atividade e "
        "a tributação."
    ),
    "central_social_security": (
        "Arrecadação líquida do RGPS (previdência dos trabalhadores privados) e total "
        "pago em benefícios, mês a mês.\n\n**Por que importa:** A distância entre as linhas "
        "é o resultado da Previdência; benefícios acima da arrecadação pressionam as "
        "contas."
    ),
    "budget_latest": (
        "Quanto o governo federal gastou em cada categoria de despesa selecionada no mês "
        "mais recente.\n\n**Por que importa:** Mostra onde o dinheiro público foi aplicado; "
        "comparar categorias revela o peso relativo de cada gasto no orçamento."
    ),
    "budget_trend": (
        "Despesa federal por categoria, somada em 12 meses para tirar a "
        "sazonalidade.\n\n**Por que importa:** Revela a tendência de cada tipo de gasto sem "
        "o ruído mensal. Alta sustentada indica peso crescente no orçamento federal."
    ),
    "social_household_debt": (
        "Dívida das famílias com o SFN (bancos e instituições) frente à renda de 12 "
        "meses, com e sem o crédito habitacional.\n\n**Por que importa:** É o estoque de "
        "dívida ante a renda. Alta: devem parcela maior do que ganham; queda, o "
        "contrário."
    ),
    "social_default_rate": (
        "Inadimplência do crédito do SFN (bancos): parcela dos empréstimos em atraso "
        "acima de 90 dias, no total e só entre pessoas físicas.\n\n**Por que importa:** "
        "Mede a dificuldade de pagar em dia. Alta acompanha renda apertada ou juros "
        "altos; queda, o contrário."
    ),
    "social_food_inflation": (
        "Inflação de alimentos: variação do grupo Alimentação e bebidas do IPCA, "
        "acumulada em 12 meses.\n\n**Por que importa:** Mede a pressão dos preços de "
        "alimentos sobre o orçamento (não a insegurança alimentar). Alta: comida mais "
        "cara; queda, alívio."
    ),
    "bets_market_growth": (
        "Mercado de apostas pela receita bruta de jogo (GGR = apostado menos prêmios): "
        "2022 (antes da regulamentação) e 2025 (1º ano regulado).\n\n**Por que importa:** "
        "Ordem de grandeza do crescimento. Origens distintas: mede escala, não valor "
        "exato."
    ),
    "bets_tax_revenue": (
        "Tributo federal arrecadado na divisão 92 da CNAE (jogos de azar e apostas), por "
        "ano, de 2016 a 2025. Eixo Y em escala logarítmica.\n\n**Por que importa:** Mede o "
        "que o setor paga em tributo federal, não o GGR nem o volume apostado."
    ),
    "bets_pix_estimate": (
        "Estimativa do BCB para a média mensal de 2024 via Pix: loterias da Caixa, "
        "apostas dentro e fora do CNAE 92 (estas concentram a maior parte).\n\n**Por que "
        "importa:** É uma proxy do volume apostado, distinta do GGR e do tributo. ~15% "
        "fica com as casas."
    ),
    "bets_spa_market": (
        "Mercado regulado de apostas de quota fixa em 2025: GGR (apostas menos prêmios) "
        "do 1º semestre e do ano, e as destinações legais de 12%.\n\n**Por que importa:** "
        "Mostra a escala do setor e quanto vai para as destinações legais previstas em "
        "lei."
    ),
    "bets_spa_accounts_funnel": (
        "Contas ativas e apostadores no mercado regulado de 2025: contas nas marcas/bets, "
        "contas em operadores e CPFs únicos que apostaram.\n\n**Por que importa:** Há muito "
        "mais contas que apostadores. A diferença ajuda a ler \"contas\" como medida do "
        "público."
    ),
    "bets_pbf": (
        "Estimativa do BC (ago/2024): beneficiários do Bolsa Família que enviaram "
        "dinheiro via Pix a casas de apostas — total e chefes de família, pessoas e "
        "valor.\n\n**Por que importa:** Descreve o perfil dos apostadores, sem afirmar "
        "causa e efeito."
    ),
    "bets_lei_allocation": (
        "Como a lei reparte, por área, a parcela da arrecadação das apostas de quota fixa "
        "destinada a políticas públicas.\n\n**Por que importa:** Indica quais áreas a lei "
        "prioriza. É a alocação prevista em lei, não a execução efetiva."
    ),
    "monetary_real_rate": (
        "Juro real: a Selic meta (média mensal) menos o IPCA em 12 meses.\n\n**Por que "
        "importa:** Mostra quanto o dinheiro rende acima da inflação. Mais alto tende a "
        "encarecer o crédito; mais baixo, o contrário."
    ),
    "monetary_focus_ipca": (
        "Inflação esperada para os próximos 12 meses (mediana do Focus) frente ao IPCA já "
        "observado em 12 meses.\n\n**Por que importa:** Uma olha à frente, a outra para "
        "trás. A distância entre as linhas indica mudança esperada no ritmo de preços."
    ),
    "monetary_reer": (
        "Câmbio efetivo real: índice que compara o real a uma cesta de moedas de "
        "parceiros comerciais, descontada a inflação.\n\n**Por que importa:** É "
        "multilateral, não a cotação do dólar. Mais alto = real mais valorizado em termos "
        "reais."
    ),
    "social_debt_service": (
        "Quanto da renda das famílias vai para o serviço da dívida (juros mais "
        "amortização) no Sistema Financeiro Nacional.\n\n**Por que importa:** É o fluxo de "
        "pagamentos sobre a renda, não o estoque. Parcela maior deixa menos renda livre; "
        "menor, o contrário."
    ),
    "monetary_ipca_decomposition": (
        "IPCA cheio ao lado de dois grupos que o compõem — Alimentação e bebidas e "
        "Serviços — na variação em 12 meses.\n\n**Por que importa:** Ajuda a ver de onde "
        "vem a pressão de preços. Os recortes não somam ao índice cheio, pois cobrem só "
        "parte da cesta."
    ),
    "monetary_ipca_core": (
        "Inflação cheia (IPCA) e seu núcleo por médias aparadas, que retira os itens de "
        "maior alta e queda para revelar a tendência de fundo.\n\n**Por que importa:** O "
        "cheio oscila com choques pontuais; alta do núcleo indica pressão mais "
        "persistente."
    ),
    "activity_ibc_yoy": (
        "Variação do IBC-Br (prévia mensal do PIB do Banco Central) frente ao mesmo mês "
        "do ano anterior.\n\n**Por que importa:** Termômetro rápido da atividade antes do "
        "PIB oficial. Positivo indica economia maior que um ano antes; negativo, menor."
    ),
    "labor_income_yoy": (
        "Variação do rendimento médio real do trabalho (descontada a inflação) frente ao "
        "mesmo período do ano anterior.\n\n**Por que importa:** Mostra se o salário médio "
        "ganhou ou perdeu poder de compra. Alta é renda acima da inflação; queda, o "
        "oposto."
    ),
    "social_default_spread": (
        "Diferença, em pontos percentuais, entre a inadimplência das pessoas físicas e a "
        "do total da carteira de crédito do SFN.\n\n**Por que importa:** Mostra o quanto as "
        "famílias atrasam mais que o crédito em geral. Spread maior indica mais "
        "dificuldade delas."
    ),
    "social_minimum_wage": (
        "Salário mínimo em valor nominal (o pago no mês) e em valor real, deflacionado "
        "pelo IPCA a preços atuais.\n\n**Por que importa:** Separa o reajuste em reais do "
        "poder de compra. Real em alta compra mais; em queda, a inflação corrói o "
        "reajuste."
    ),
    "sectors_gdp_volume_index": (
        "Índice de volume trimestral do PIB e do valor adicionado por setor "
        "(agropecuária, indústria, serviços), com ajuste sazonal.\n\n**Por que importa:** "
        "Acompanha a trajetória real de cada setor. Cada base é própria: comparam-se "
        "trajetórias, não níveis."
    ),
    "sectors_gdp_yoy": (
        "Quanto o valor adicionado de cada setor cresceu ou caiu no acumulado de 4 "
        "trimestres frente aos 4 anteriores.\n\n**Por que importa:** Mostra o ritmo por "
        "setor (agropecuária, indústria, serviços) sem ruído sazonal. Positivo é "
        "expansão; negativo, retração."
    ),
    "sectors_va_composition": (
        "Fatia de cada setor (agropecuária, indústria, serviços) no valor adicionado "
        "bruto do país, a preços do momento.\n\n**Por que importa:** Revela o peso de cada "
        "setor e como muda. O pico da agropecuária no início do ano reflete a safra, não "
        "mudança estrutural."
    ),
    "sectors_industria_composition": (
        "Fatia de cada subsetor (extrativa, transformação, construção, "
        "eletricidade/gás/água) na produção da indústria, a preços correntes, por "
        "trimestre.\n\n**Por que importa:** Um subsetor que ganha ou perde peso sinaliza "
        "deslocamento da atividade industrial."
    ),
    "sectors_servicos_composition": (
        "Fatia de cada subsetor (comércio, transporte, informação, financeiro, "
        "imobiliárias, administração pública, outros) na produção de serviços, por "
        "trimestre.\n\n**Por que importa:** Serviços são a maior parte da economia; mostra "
        "o que ganha ou perde peso."
    ),
    "sectors_monthly_volume": (
        "Índices mensais de volume produzido (ajustado pelo calendário) na indústria "
        "(PIM-PF), no varejo restrito (PMC) e nos serviços (PMS), base comum 2022 = "
        "100.\n\n**Por que importa:** Leitura rápida do ritmo da atividade; a base comum "
        "permite comparar."
    ),
    "sectors_retail": (
        "Índice de volume vendido no comércio varejista restrito (ajustado pelo "
        "calendário), mês a mês, base 2022 = 100.\n\n**Por que importa:** Termômetro do "
        "consumo das famílias. Alta indica mais vendas em volume real; queda, menos — sem "
        "confundir com preços."
    ),
    "sectors_services": (
        "Volume de serviços prestados no Brasil, em número-índice com ajuste sazonal "
        "(base 2022 = 100). Reflete quantidade real, não faturamento.\n\n**Por que "
        "importa:** Serviços são a maior parte da economia; alta indica mais atividade no "
        "setor; queda, menos."
    ),
    "trade_flows_12m": (
        "Exportações, importações e saldo da balança comercial de bens (exportações menos "
        "importações), somados em 12 meses para tirar a sazonalidade.\n\n**Por que "
        "importa:** Saldo positivo (superávit) é vender mais bens do que comprar; "
        "negativo, o contrário."
    ),
    "trade_balance_monthly": (
        "Saldo mensal da balança comercial de bens: exportações menos importações a cada "
        "mês.\n\n**Por que importa:** Indica se o país vendeu mais bens ao exterior do que "
        "comprou. Sinal +: superávit (vendeu mais); sinal −: déficit (comprou mais)."
    ),
    "trade_partners_exports": (
        "Exportações de bens (valor FOB) por país de destino a cada ano, para os cinco "
        "maiores parceiros (China, EUA, Argentina, Países Baixos, Espanha); os demais "
        "somados.\n\n**Por que importa:** A fatia de um parceiro indica maior ou menor "
        "dependência dele."
    ),
    "trade_partners_imports": (
        "Quanto o Brasil importou em bens (valor FOB) por país de origem a cada ano, para "
        "os cinco maiores parceiros e os demais.\n\n**Por que importa:** Revela de quem o "
        "Brasil compra. Mudança na fatia de um parceiro indica mais ou menos dependência "
        "daquela origem."
    ),
    "trade_china_usa_trend": (
        "Corrente de comércio (exportações + importações de bens, FOB) do Brasil com seus "
        "dois maiores parceiros, China e EUA, ano a ano.\n\n**Por que importa:** Mede o "
        "tamanho do vínculo com cada país. Corrente crescente indica troca mais intensa; "
        "queda, menos."
    ),
    "trade_mercosul": (
        "Exportações e importações de bens do Brasil com o Mercosul, além do saldo "
        "(exportações − importações), por ano.\n\n**Por que importa:** Mostra o peso dos "
        "vizinhos no comércio. Saldo positivo indica que o Brasil vende mais do que "
        "compra do bloco."
    ),
    "trade_brics_flows": (
        "Exportações e importações de bens do Brasil com o BRICS (China, Índia, Rússia e "
        "África do Sul), além do saldo, por ano.\n\n**Por que importa:** Mostra o peso do "
        "grupo no comércio. Saldo positivo indica que o Brasil vende mais do que compra "
        "desses países."
    ),
    "trade_brics_share": (
        "Fatia do BRICS (China, Índia, Rússia e África do Sul) nas exportações e "
        "importações brasileiras de bens, por ano.\n\n**Por que importa:** Indica o quanto "
        "do comércio se concentra nesse grupo. Fatia crescente sinaliza maior dependência "
        "desses parceiros."
    ),
    "trade_brics_by_member": (
        "Corrente de comércio (exportações + importações de bens) do Brasil com cada "
        "membro do BRICS (China, Índia, Rússia e África do Sul), por ano, "
        "empilhada.\n\n**Por que importa:** Separa o quanto cada parceiro pesa no grupo, "
        "revelando quem puxa o total."
    ),
    "trade_brics_vs_blocs": (
        "Corrente de comércio (exportações + importações de bens) do Brasil com quatro "
        "grupos — BRICS, Mercosul, UE e EUA — por ano.\n\n**Por que importa:** Compara o "
        "tamanho de cada mercado. Os grupos se sobrepõem: serve para comparar magnitude, "
        "não composição."
    ),
    "trade_commodities_exports": (
        "Exportações brasileiras de bens por capítulo de produto (SH2), por ano, para os "
        "dez maiores capítulos e os demais.\n\n**Por que importa:** Mostra de quais "
        "produtos o Brasil mais depende para exportar. Concentração alta sinaliza maior "
        "exposição a preços."
    ),
    "digital_pix_value": (
        "Valor mensal das transações Pix liquidadas no SPI (Sistema de Pagamentos "
        "Instantâneos do Banco Central).\n\n**Por que importa:** Indica quanto dinheiro "
        "circula pelo Pix. Alta sugere maior uso; queda, o contrário."
    ),
    "digital_pix_count": (
        "Quantidade mensal de transações Pix liquidadas no SPI (Sistema de Pagamentos "
        "Instantâneos do Banco Central).\n\n**Por que importa:** Indica com que frequência "
        "se usa o Pix. Alta sugere maior adoção; queda, o contrário."
    ),
    "digital_households_internet": (
        "Parcela dos domicílios em que havia uso da internet.\n\n**Por que importa:** "
        "Indica quão disseminado é o acesso nos lares. Alta aponta maior inclusão "
        "digital; queda, o contrário. TIC não coletada em 2020."
    ),
    "digital_people_access": (
        "Parcela das pessoas de 10+ anos que usaram a internet nos últimos três meses e "
        "que tinham celular pessoal.\n\n**Por que importa:** Mede o acesso digital "
        "individual, não só por domicílio. Alta indica maior inclusão. TIC não coletada "
        "em 2020."
    ),
    "digital_access_devices": (
        "Parcela dos domicílios com uso da internet e a parcela com computador.\n\n**Por "
        "que importa:** Compara acesso à rede com posse de equipamento; a diferença "
        "revela lares que se conectam por outros meios, como o celular. TIC não coletada "
        "em 2020."
    ),
    "digital_access_urban_rural": (
        "Parcela dos domicílios com uso da internet, separando urbanos de rurais.\n\n**Por "
        "que importa:** A diferença entre campo e cidade revela a desigualdade de acesso. "
        "Uma distância que diminui indica avanço nas áreas rurais."
    ),
    "digital_access_regions": (
        "Percentual de domicílios com acesso à internet, por Grande Região do "
        "país.\n\n**Por que importa:** Mostra o acesso desigual pelo território. Diferenças "
        "persistentes costumam sinalizar lacunas de infraestrutura e de renda."
    ),
    "digital_connection_type": (
        "Entre os domicílios com internet, a fatia com banda larga fixa (cabo/fibra) e a "
        "com banda larga móvel (rede de celular).\n\n**Por que importa:** Indica que "
        "conexão sustenta o acesso. As categorias se sobrepõem e somam mais de 100%."
    ),
    "digital_payments_value": (
        "Valor movimentado a cada mês por instrumento de pagamento do varejo: Pix, TED, "
        "boleto e cheque.\n\n**Por que importa:** Mostra por onde passa o dinheiro no dia a "
        "dia e como o peso migra entre os meios."
    ),
    "digital_payments_count": (
        "Número de transações por mês em cada instrumento de pagamento do varejo: Pix, "
        "TED, boleto e cheque.\n\n**Por que importa:** Conta quantas vezes cada meio é "
        "usado (não quanto vale): um retrato do hábito de pagar."
    ),
    "digital_payments_share": (
        "Fatia de cada instrumento (Pix, TED, boleto, cheque) no valor total pago por "
        "esses quatro meios, a cada mês.\n\n**Por que importa:** Uma fatia que cresce "
        "sinaliza a substituição de um meio de pagamento por outro."
    ),
    "digital_payments_share_count": (
        "Fatia de cada instrumento (Pix, TED, boleto, cheque) no número total de "
        "transações desses quatro meios, a cada mês.\n\n**Por que importa:** Mostra o meio "
        "mais usado no dia a dia: o Pix domina em quantidade; a TED, em valor."
    ),
    "digital_cards_value": (
        "Valor total, a cada trimestre, das compras no Brasil com cartão de crédito e de "
        "débito.\n\n**Por que importa:** Uma alta costuma acompanhar mais consumo; uma "
        "queda, o contrário."
    ),
    "digital_cards_count": (
        "Número total, a cada trimestre, de compras no Brasil com cartão de crédito e de "
        "débito.\n\n**Por que importa:** Mostra com que frequência os cartões são usados, à "
        "parte do valor gasto. Alta: mais transações; queda, menos."
    ),
    "digital_pix_users": (
        "Usuários (pessoas e empresas) com chaves Pix cadastradas no DICT, mês a "
        "mês.\n\n**Por que importa:** Mede o alcance do Pix. É o estoque de cadastrados, "
        "não o volume de transações; uma alta indica mais gente no sistema."
    ),
    "petrobras_financeiro": (
        "Resultados anuais da Petrobras: receita de vendas consolidada e lucro líquido, "
        "em R$ bilhões.\n\n**Por que importa:** Maior empresa do país e grande pagadora de "
        "tributos e dividendos; receita e lucro afetam a arrecadação pública."
    ),
    "matriz_eletrica_fontes": (
        "Participação de cada fonte (hidráulica, eólica, solar, biomassa, gás) na matriz "
        "elétrica brasileira em 2024, pela Oferta Interna de Energia Elétrica "
        "(OIEE).\n\n**Por que importa:** Mostra quanto da eletricidade é renovável; eólica "
        "e solar ganham espaço."
    ),
    "industria_transformacao_pib": (
        "Quanto a indústria de transformação (fábricas que convertem matérias-primas em "
        "produtos) representa do PIB a cada ano, em %.\n\n**Por que importa:** A queda "
        "dessa fatia é o principal indicador da desindustrialização do país."
    ),
    "vc_deployed_brasil": (
        "Volume anual de venture capital (aportes de fundos em startups) captado por "
        "startups brasileiras, em US$ bilhões.\n\n**Por que importa:** Reflete o apetite "
        "dos investidores pela inovação; alta indica mais aportes, queda o contrário."
    ),
    "mensageria_uso_internet": (
        "Percentual de usuários de Internet (10+ anos, uso nos últimos 3 meses) que "
        "enviaram mensagens instantâneas, como WhatsApp e Telegram.\n\n**Por que importa:** "
        "Mede o alcance da mensageria, o principal canal de conversa e informação no "
        "país."
    ),
}
