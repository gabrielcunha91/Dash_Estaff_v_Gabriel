from data.dbconnect import get_dataframe_from_query
import pandas as pd
import streamlit as st

# Brindes e Confraternizações lançados no nível 1 Eventos (G2 723) são confraternização interna:
# entram em C3 (Pessoal Interno), não em C5. Os de Marketing (G2 798, nível 1 224) já caem em C8.
BRINDES_CONFRATERNIZACAO_INTERNA_G2 = 723

@st.cache_data
def general_costs_blueme(day1, day2):
    return get_dataframe_from_query(f"""
SELECT 
    DATE_FORMAT(DR.COMPETENCIA, '%m/%Y') AS 'Mês/Ano',
    
    SUM(CASE WHEN G1.ID IN ('216') THEN DR.VALOR_PAGAMENTO ELSE 0 END) AS 'C1 Impostos',
    SUM(CASE WHEN G1.ID IN ('220','221','222','225','232', '218', '226') THEN DR.VALOR_PAGAMENTO ELSE 0 END) AS 'C2 Custos de Ocupação',
    SUM(CASE WHEN G1.ID IN ('223','231','253') OR DR.FK_CLASSIFICACAO_CONTABIL_GRUPO_2 = {BRINDES_CONFRATERNIZACAO_INTERNA_G2} THEN DR.VALOR_PAGAMENTO ELSE 0 END) AS 'C3 Despesas com Pessoal Interno',
    SUM(CASE WHEN G1.ID IN ('230', '210') THEN DR.VALOR_PAGAMENTO ELSE 0 END) AS 'C4 Despesas com Pessoal Terceirizado',
    SUM(CASE WHEN G1.ID IN ('234', '215') AND (DR.FK_CLASSIFICACAO_CONTABIL_GRUPO_2 IS NULL OR DR.FK_CLASSIFICACAO_CONTABIL_GRUPO_2 <> {BRINDES_CONFRATERNIZACAO_INTERNA_G2}) THEN DR.VALOR_PAGAMENTO ELSE 0 END) AS 'C5 Despesas Operacionais com Freelas',
    SUM(CASE WHEN G1.ID IN ('233') THEN DR.VALOR_PAGAMENTO ELSE 0 END) AS 'C6 Despesas com Clientes',
    SUM(CASE WHEN G1.ID IN ('217') THEN DR.VALOR_PAGAMENTO ELSE 0 END) AS 'C7 Despesas com Softwares e Licenças',
    SUM(CASE WHEN G1.ID IN ('211', '224', '227') THEN DR.VALOR_PAGAMENTO ELSE 0 END) AS 'C8 Despesas com Marketing',
    SUM(CASE WHEN G1.ID IN ('213', '229', '228', '212', '214') THEN DR.VALOR_PAGAMENTO ELSE 0 END) AS 'C9 Despesas Financeiras',
    SUM(CASE WHEN G1.ID IN ('219') THEN DR.VALOR_PAGAMENTO ELSE 0 END) AS 'C10 Investimentos',
    SUM(DR.VALOR_PAGAMENTO) AS 'Custos Totais'
FROM T_DESPESA_RAPIDA DR
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 G1 ON DR.FK_CLASSIFICACAO_CONTABIL_GRUPO_1 = G1.ID
WHERE DR.FK_LOJA = '134'
AND DR.COMPETENCIA >= '2025-01-01'
AND (DR.TAG_ESTORNO IS NULL OR DR.TAG_ESTORNO = 0)
AND DR.COMPETENCIA >= '{day1}'
AND DR.COMPETENCIA <= '{day2}'
GROUP BY YEAR(DR.COMPETENCIA), MONTH(DR.COMPETENCIA)
ORDER BY STR_TO_DATE(DATE_FORMAT(DR.COMPETENCIA, '%m/%Y'), '%m/%Y');
""", use_blueme=True)

@st.cache_data
def costs_blueme_details(day1, day2):
    return get_dataframe_from_query(f"""
SELECT
    CASE
        WHEN G2.ID = {BRINDES_CONFRATERNIZACAO_INTERNA_G2} THEN 'c3_Despesas_com_Pessoal_Interno'
        WHEN G1.ID IN ('216') THEN 'c1_Impostos'
        WHEN G1.ID IN ('220','221','222','225','232', '218', '226') THEN 'c2_Custos_de_Ocupacao'
        WHEN G1.ID IN ('223','231','253', '265') THEN 'c3_Despesas_com_Pessoal_Interno'
        WHEN G1.ID IN ('230', '210') THEN 'c4_Despesas_com_Pessoal_Terceirizado'
        WHEN G1.ID IN ('234', '215') THEN 'c5_Despesas_Operacionais_com_Freelas'
        WHEN G1.ID IN ('233') THEN 'c6_Despesas_com_Clientes'
        WHEN G1.ID IN ('217') THEN 'c7_Despesas_com_Softwares_e_Licencas'
        WHEN G1.ID IN ('211', '224', '227') THEN 'c8_Despesas_com_Marketing'
        WHEN G1.ID IN ('213', '229', '228', '212', '214') THEN 'c9_Despesas_Financeiras'
        WHEN G1.ID IN ('219') THEN 'c10_Investimentos'
    END AS `CATEGORIA DE CUSTO`,
    CASE WHEN G2.ID = {BRINDES_CONFRATERNIZACAO_INTERNA_G2} THEN G2.DESCRICAO ELSE G1.DESCRICAO END AS 'CLASSIFICAÇÃO PRIMÁRIA',
    SUM(DR.VALOR_PAGAMENTO) AS 'VALOR',
    DATE_FORMAT(DR.COMPETENCIA, '%Y/%m') AS 'DATA'
FROM T_DESPESA_RAPIDA DR
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 G2 ON G2.ID = DR.FK_CLASSIFICACAO_CONTABIL_GRUPO_2
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 G1 ON G2.FK_GRUPO_1 = G1.ID
LEFT JOIN T_VERSOES_PLANO_CONTABIL VPC ON VPC.ID = G1.FK_VERSAO_PLANO_CONTABIL
WHERE DR.FK_LOJA = '134'
AND DR.COMPETENCIA >= '2025-01-01'
AND (DR.TAG_ESTORNO IS NULL OR DR.TAG_ESTORNO = 0)
AND DR.COMPETENCIA >= '{day1}'
AND DR.COMPETENCIA <= '{day2}'
GROUP BY YEAR(DR.COMPETENCIA), MONTH(DR.COMPETENCIA), `CATEGORIA DE CUSTO`,
    CASE WHEN G2.ID = {BRINDES_CONFRATERNIZACAO_INTERNA_G2} THEN G2.DESCRICAO ELSE G1.DESCRICAO END
ORDER BY `CATEGORIA DE CUSTO`
""", use_blueme=True)

@st.cache_data
def ratings_rank_blueme(data):
    return get_dataframe_from_query(f"""
SELECT 
    DATE_FORMAT(DR.COMPETENCIA, '%m/%Y') AS 'Mês/Ano',
    G1.DESCRICAO AS 'CLASSIFICAÇÃO PRIMÁRIA',
    SUM(DR.VALOR_PAGAMENTO) AS 'VALOR'
FROM T_DESPESA_RAPIDA DR
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 G2 ON G2.ID = DR.FK_CLASSIFICACAO_CONTABIL_GRUPO_2
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 G1 ON G2.FK_GRUPO_1 = G1.ID
LEFT JOIN T_VERSOES_PLANO_CONTABIL VPC ON VPC.ID = G1.FK_VERSAO_PLANO_CONTABIL
WHERE DR.FK_LOJA = '134'
AND (DR.TAG_ESTORNO IS NULL OR DR.TAG_ESTORNO = 0)
AND DR.COMPETENCIA >= '2025-01-01'
AND DR.COMPETENCIA LIKE '{data}%'
GROUP BY G1.DESCRICAO, YEAR(DR.COMPETENCIA), MONTH(DR.COMPETENCIA)
""", use_blueme=True)

@st.cache_data
def ratings_rank_details_blueme(data):
    return get_dataframe_from_query(f"""
SELECT 
		DR.ID AS 'ID CUSTO',
    CASE
        WHEN G2.ID = {BRINDES_CONFRATERNIZACAO_INTERNA_G2} THEN 'c3_Despesas_com_Pessoal_Interno'
        WHEN G1.ID IN ('216') THEN 'c1_Impostos'
        WHEN G1.ID IN ('220','221','222','225','232', '218', '226') THEN 'c2_Custos_de_Ocupacao'
        WHEN G1.ID IN ('223','231','253') THEN 'c3_Despesas_com_Pessoal_Interno'
        WHEN G1.ID IN ('230', '210') THEN 'c4_Despesas_com_Pessoal_Terceirizado'
        WHEN G1.ID IN ('234', '215') THEN 'c5_Despesas_Operacionais_com_Freelas'
        WHEN G1.ID IN ('233') THEN 'c6_Despesas_com_Clientes'
        WHEN G1.ID IN ('217') THEN 'c7_Despesas_com_Softwares_e_Licencas'
        WHEN G1.ID IN ('211', '224', '227') THEN 'c8_Despesas_com_Marketing'
        WHEN G1.ID IN ('213', '229', '228', '212', '214') THEN 'c9_Despesas_Financeiras'
        WHEN G1.ID IN ('219') THEN 'c10_Investimentos'
    END AS `GRUPO GERAL`,
    G1.DESCRICAO AS 'NIVEL 1',
    G2.DESCRICAO AS 'NIVEL 2',
    F.FANTASY_NAME AS 'FORNECEDOR',
    DR.VALOR_PAGAMENTO AS 'VALOR',
    SP.DESCRICAO AS 'PAGAMENTO',
    DATE_FORMAT(DR.COMPETENCIA, '%d/%m/%Y') AS 'DATA COMPETÊNCIA',
    DATE_FORMAT(DR.VENCIMENTO, '%d/%m/%Y') AS 'DATA VENCIMENTO',
    DR.OBSERVACAO AS 'DESCRIÇÃO'
FROM T_DESPESA_RAPIDA DR 
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 G2 ON G2.ID = DR.FK_CLASSIFICACAO_CONTABIL_GRUPO_2
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 G1 ON G1.ID = G2.FK_GRUPO_1
LEFT JOIN T_FORNECEDOR F ON F.ID = DR.FK_FORNECEDOR
LEFT JOIN T_STATUS_PAGAMENTO SP ON SP.ID = DR.FK_STATUS_PGTO
LEFT JOIN (
    -- Subquery para calcular o total de valor por CLASSIFICAÇÃO PRIMÁRIA
    SELECT 
        G1.ID AS Grupo1_ID,
        SUM(DR.VALOR_PAGAMENTO) AS Total_Valor
    FROM T_DESPESA_RAPIDA DR 
  	LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 G2 ON G2.ID = DR.FK_CLASSIFICACAO_CONTABIL_GRUPO_2
  	LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 G1 ON G1.ID = G2.FK_GRUPO_1
    
    WHERE DR.FK_LOJA = '134'
    AND (DR.TAG_ESTORNO IS NULL OR DR.TAG_ESTORNO = 0)
    AND DR.COMPETENCIA >= '2025-01-01'
    AND DR.COMPETENCIA LIKE '{data}%'
    GROUP BY G1.ID
) AS Total_Custos ON G1.ID = Total_Custos.Grupo1_ID
WHERE DR.FK_LOJA = '134'
AND (DR.TAG_ESTORNO IS NULL OR DR.TAG_ESTORNO = 0)
AND DR.COMPETENCIA >= '2025-01-01'
AND DR.COMPETENCIA LIKE '{data}%'
ORDER BY Total_Custos.Total_Valor DESC, DR.VALOR_PAGAMENTO DESC;
""", use_blueme=True)

# Receitas lançadas em Receitas Extraordinárias na BlueMe (T_RECEITAS_EXTRAORDINARIAS) que
# entram no faturamento da Estaff. Linha do faturamento -> (FK_EMPRESA, FK_CLASSIFICACAO).
# O mês é o da competência (DATA_OCORRENCIA). Receita nova sem boleto: criar a classificação
# na BlueMe e acrescentar uma linha aqui; o merge do faturamento lê as linhas deste dicionário.
EXTRAORDINARY_REVENUE_MAP = {
    'Desenvolvimentos SaaS': (134, 154),    # classificação "Desenvolvimento SaaS"
    'Rendimentos Financeiros': (134, 150),  # classificação "Juros de Aplicações Financeiras"
}

def _extraordinary_revenue_where(lines):
    return " OR ".join(
        f"(TRE.FK_EMPRESA = {EXTRAORDINARY_REVENUE_MAP[l][0]} AND TRE.FK_CLASSIFICACAO = {EXTRAORDINARY_REVENUE_MAP[l][1]})"
        for l in lines
    )

@st.cache_data
def extraordinary_revenue_monthly(day1, day2):
    columns = ",\n".join(
        f"SUM(CASE WHEN TRE.FK_EMPRESA = {empresa} AND TRE.FK_CLASSIFICACAO = {classif} THEN TRE.VALOR ELSE 0 END) AS '{line}'"
        for line, (empresa, classif) in EXTRAORDINARY_REVENUE_MAP.items()
    )
    return get_dataframe_from_query(f"""
SELECT
DATE_FORMAT(TRE.DATA_OCORRENCIA, '%m/%Y') AS 'Mês/Ano',
{columns}
FROM T_RECEITAS_EXTRAORDINARIAS TRE
WHERE ({_extraordinary_revenue_where(EXTRAORDINARY_REVENUE_MAP)})
AND DATE(TRE.DATA_OCORRENCIA) >= '{day1}'
AND DATE(TRE.DATA_OCORRENCIA) <= '{day2}'
GROUP BY DATE_FORMAT(TRE.DATA_OCORRENCIA, '%m/%Y')
ORDER BY STR_TO_DATE(CONCAT('01/', DATE_FORMAT(TRE.DATA_OCORRENCIA, '%m/%Y')), '%d/%m/%Y') ASC
""", use_blueme=True)

@st.cache_data
def extraordinary_revenue_details(day1, day2, line):
    return get_dataframe_from_query(f"""
SELECT
TRE.ID AS 'ID_Receita',
DATE(TRE.DATA_OCORRENCIA) AS 'Data_Competencia',
DATE(TRE.DATA_RECEBIMENTO) AS 'Data_Recebimento',
TREC.NOME AS 'Cliente',
TRE.OBSERVACOES AS 'Descricao',
TFP.DESCRICAO AS 'Forma_Pagamento',
TRE.NUM_DOCUMENTACAO AS 'Documento',
TRE.VALOR AS 'Valor'
FROM T_RECEITAS_EXTRAORDINARIAS TRE
LEFT JOIN T_RECEITAS_EXTRAORDINARIAS_CLIENTE TREC ON (TRE.FK_CLIENTE = TREC.ID)
LEFT JOIN T_FORMAS_DE_PAGAMENTO TFP ON (TRE.FK_FORMA_PAGAMENTO = TFP.ID)
WHERE ({_extraordinary_revenue_where([line])})
AND DATE(TRE.DATA_OCORRENCIA) >= '{day1}'
AND DATE(TRE.DATA_OCORRENCIA) <= '{day2}'
ORDER BY TRE.DATA_OCORRENCIA DESC
""", use_blueme=True)

PEOPLE_COST_G2_IDS = (769, 770, 771, 772, 773, 783, 785, 786, 793, 794, 863, 864)

@st.cache_data
def people_cost_g2_classifications():
    ids_str = ",".join(str(i) for i in PEOPLE_COST_G2_IDS)
    return get_dataframe_from_query(f"""
SELECT ID, DESCRICAO
FROM T_CLASSIFICACAO_CONTABIL_GRUPO_2
WHERE ID IN ({ids_str})
ORDER BY DESCRICAO
""", use_blueme=True)

@st.cache_data
def people_cost_by_center(month, g2_ids):
    if not g2_ids:
        return pd.DataFrame(columns=["CENTRO DE CUSTO PESSOAS", "VALOR"])
    ids_str = ",".join(str(int(i)) for i in g2_ids)
    return get_dataframe_from_query(f"""
SELECT
    tcdc.NAME AS 'CENTRO DE CUSTO PESSOAS',
    SUM(tdr.VALOR_PAGAMENTO * tafcdc.PERCENTUAL_CENTRO_DE_CUSTO / 100) AS 'VALOR'
FROM T_DESPESA_RAPIDA tdr
LEFT JOIN T_FORNECEDOR tf ON (tdr.FK_FORNECEDOR = tf.ID)
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 tccg ON (tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_1 = tccg.ID)
LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 tccg2 ON (tdr.FK_CLASSIFICACAO_CONTABIL_GRUPO_2 = tccg2.ID)
LEFT JOIN T_ASSOCIACIATIVA_FORNECEDOR_CENTROS_DE_CUSTOS tafcdc ON (tf.ID = tafcdc.FK_FORNECEDOR)
LEFT JOIN T_CENTROS_DE_CUSTOS tcdc ON (tafcdc.FK_CENTRO_DE_CUSTO = tcdc.ID)
WHERE tccg2.ID IN ({ids_str})
AND DATE_FORMAT(tdr.COMPETENCIA, '%Y-%m') = '{month}'
AND tccg.ID = 223
AND tdr.FK_LOJA = 134
AND tdr.BIT_CANCELADA = 0
AND tcdc.ID IS NOT NULL
GROUP BY tcdc.ID, tcdc.NAME
ORDER BY SUM(tdr.VALOR_PAGAMENTO * tafcdc.PERCENTUAL_CENTRO_DE_CUSTO / 100) DESC
""", use_blueme=True)