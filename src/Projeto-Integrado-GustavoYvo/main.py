import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np


st.set_page_config(
    page_title="Dashboard - Curso Superior - IBGE",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.title("Curso Superior")
st.markdown("---")
st.title("Dashboard de Visualização de Dados")
st.markdown("Análise visual das métricas acadêmicas e operacionais.")
st.markdown("Fonte: **SIDRA - Censo Demográfico 2022 — IBGE **")
st.markdown("---")


@st.cache_data
def carregar_dados():
    df_65 = pd.read_csv("tabela10065.csv", sep=";", skiprows=4)
    df_64 = pd.read_csv("tabela10064.csv", sep=";", skiprows=4)

    sudeste = ['Minas Gerais', 'Espírito Santo', 'Rio de Janeiro', 'São Paulo']
   
    col_total_65 = df_65.columns[2]
    # Conversão rigorosa para numérico (substituindo pontos de milhar e tratando valores inválidos)
    df_65[col_total_65] = pd.to_numeric(
        df_65[col_total_65].astype(str).str.replace('.', '', regex=False).str.strip(), 
        errors='coerce'
    )
    
    col_total_64 = df_64.columns[2]
    df_64[col_total_64] = pd.to_numeric(
        df_64[col_total_64].astype(str).str.replace('.', '', regex=False).str.strip(), 
        errors='coerce'
    )
    
    return df_65[df_65.iloc[:, 0].isin(sudeste)], df_64[df_64.iloc[:, 0].isin(sudeste)]

df_65, df_64 = carregar_dados()

st.sidebar.header("Filtros do Dashboard")
estados = ['Minas Gerais', 'Espírito Santo', 'Rio de Janeiro', 'São Paulo']
uf_sel = st.sidebar.multiselect("Selecione os Estados:", options=estados, default=estados)

col_uf, col_raca, col_total = df_65.columns[0], df_65.columns[1], df_65.columns[2]


df_65_filt = df_65[df_65[col_uf].isin(uf_sel)]
df_totais = df_65_filt[df_65_filt[col_raca] == "Total"]

st.subheader("Panorama Geral do Ensino Superior no Sudeste ")
if not df_totais.empty:
    cols = st.columns(len(df_totais))
    for i, (_, row) in enumerate(df_totais.iterrows()):
        cols[i].metric(label=row[col_uf], value=f"{row[col_total]:,.0f} pessoas".replace(',', '.'))

st.markdown("---")
    
if not df_totais.empty:
    tot, med = df_totais[col_total].sum(), df_totais[col_total].mean()
    maior, menor = df_totais.loc[df_totais[col_total].idxmax()], df_totais.loc[df_totais[col_total].idxmin()]

    st.subheader("Indicadores Dinâmicos Regionais")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Média Regional (Sudeste)", value=f"{med:,.0f} pes.".replace(',', '.'))
    with col2:
        st.metric(label=f"Maior Estado ({maior[col_uf]})", value=f"{maior[col_total]:,.0f}".replace(',', '.'))
    with col3:
        st.metric(label=f"Menor Estado ({menor[col_uf]})", value=f"{menor[col_total]:,.0f}".replace(',', '.'))
    with col4:
        st.metric(label="Total Acumulado Selecionado", value=f"{tot:,.0f}".replace(',', '.'))

st.divider()

st.sidebar.markdown("---")
racas = [r for r in df_65[col_raca].dropna().unique() if r != "Total"]
raca_sel = st.sidebar.selectbox("Filtrar Raça/Cor:", options=["Todas"] + racas)

df_raca = df_65_filt[(df_65_filt[col_raca] != "Total") & (df_65_filt[col_raca] == raca_sel if raca_sel != "Todas" else True)]

st.subheader("Recorte Demográfico por Raça/Cor")
if not df_raca.empty:
    fig_raca = px.bar(df_raca, x=col_uf, y=col_total, color=col_raca, barmode="group", labels={col_total: "População", col_uf: "Estado"})
    st.plotly_chart(fig_raca, use_container_width=True)

if not df_64.empty:
    st.divider()
    st.subheader("Perfil Etário")
    col_uf_64, col_idade, col_tot_64 = df_64.columns[0], df_64.columns[1], df_64.columns[2]
    df_faixas = df_64[(df_64[col_uf_64].isin(uf_sel)) & (df_64[col_idade] != "Total")]
    
    if not df_faixas.empty:
        fig_idade = px.bar(df_faixas, x=col_uf_64, y=col_tot_64, color=col_idade, barmode="group", labels={col_tot_64: "Pessoas", col_uf_64: "Estado"})
        st.plotly_chart(fig_idade, use_container_width=True)


st.subheader("Estatísticas Descritivas e Indicadores Avançados")
df_totais_uf = df_65_filt[df_65_filt[col_raca] == "Total"]

if not df_totais_uf.empty:
    serie_valores = df_totais_uf[col_total]
else:
    serie_valores = pd.Series([0])

media = serie_valores.mean()
mediana = serie_valores.median()
q1 = serie_valores.quantile(0.25)
q3 = serie_valores.quantile(0.75)
iqr = q3 - q1
desvio_padrao = serie_valores.std()
variancia = serie_valores.var()

col4, col5, col6 = st.columns(3)
with col4:
    fig_box = px.box(df_totais_uf, y=col_total, title='Distribuição e Quartis (Boxplot)', labels={col_total: 'População Graduada'})
    st.plotly_chart(fig_box, use_container_width=True, key="estat_box")

with col5:
    fig_hist = px.histogram(df_totais_uf, x=col_total, nbins=len(df_totais_uf) if len(df_totais_uf) > 0 else 1, title='Frequência por Estado', labels={col_total: 'População Graduada'})
    st.plotly_chart(fig_hist, use_container_width=True, key="estat_hist")

with col6:
    fig_horizontal = px.bar(
        df_totais_uf,
        x=col_total,
        y=col_uf,
        orientation='h',
        text=col_total,
        color=col_uf,
        color_discrete_sequence=px.colors.sequential.Blues_r,
        title="Total de Pessoas com Nível Superior Completo por Estado",
        labels={col_total: "Pessoas Graduadas", col_uf: "Unidade da Federação"}
    )
    
    fig_horizontal.update_traces(
        texttemplate='%{text:,.0f}', 
        textposition='outside'
    )
    
    fig_horizontal.update_layout(
        xaxis_title="População com Superior Completo",
        yaxis_title="Estado",
        showlegend=False
    )
    
    st.plotly_chart(fig_horizontal, use_container_width=True)

st.success(f"""
**Análise dos Dados Reais - Medidas de Tendência Central e Dispersão:**
- **Tendência Central:** A **média** de **{media:,.0f}** pessoas e a **mediana** de **{mediana:,.0f}** refletem a realidade demográfica e o impacto concentrador dos estados selecionados.
- **Dispersão:** O **desvio padrão** de **{desvio_padrao:,.0f}** evidencia a heterogeneidade e a disparidade populacional entre as unidades da federação.
- **Quartis e IQR:** O intervalo interquartil (**IQR = {iqr:,.0f}**) delimita a faixa central de variação dos estados analisados.
""")

st.divider()

st.subheader("Mulheres e Atração de Talentos em Áreas STEM")

st.markdown("""
Embora o Censo Demográfico do IBGE demonstre que a população com ensino superior completo apresenta um volume expressivo na Região Sudeste, a atração e retenção de talentos (especialmente em áreas de **STEM — Ciência, Tecnologia, Engenharia e Matemática**) exige análises demográficas regionais detalhadas para fundamentar políticas corporativas de inclusão e diversidade.
""")

df_raca_stem = df_65_filt[df_65_filt[col_raca] != "Total"].copy()

if not df_raca_stem.empty:
    df_stem_real = df_raca_stem.groupby(col_uf, as_index=False)[col_total].sum()
    total_regiao = df_stem_real[col_total].sum()
    
    df_stem_real["Percentual do Polo (%)"] = (df_stem_real[col_total] / total_regiao * 100).round(1)
    df_stem_real = df_stem_real.sort_values(by="Percentual do Polo (%)", ascending=True)

    fig_stem = px.bar(
        df_stem_real,
        x="Percentual do Polo (%)",
        y=col_uf,
        orientation='h',
        text="Percentual do Polo (%)",
        title="Concentração Regional do Pool de Talentos Graduados (Dados Reais IBGE)",
        color="Percentual do Polo (%)",
        color_continuous_scale="Purples"
    )

    fig_stem.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_stem.update_layout(
        xaxis_title="Proporção de Talentos na Região (%)", 
        yaxis_title="Unidade da Federação", 
        showlegend=False
    )

    st.plotly_chart(fig_stem, use_container_width=True, key="grafico_stem_mulheres_real")
else:
    st.warning("Não foi possível carregar os dados reais para o gráfico de STEM.")

st.info("""
** Insights para Gestão e Atração de Talentos:**
- **O Funil de STEM & Distribuição Regional:** A alta concentração de graduados em determinados polos (ex: SP e MG) exige que empresas de tecnologia descentralizem seus programas de atração de talentos e acelerem a inclusão de grupos minoritários.
- **Retenção & Diversidade:** Programas de mentoria corporativa, trabalho flexível e ações afirmativas de recrutamento são pilares fundamentais para mitigar disparidades de gênero e raça nas carreiras tecnológicas.
""")

st.subheader("Tabela Completa de Indicadores")
df_tabela = df_totais[[col_uf, col_total]].rename(columns={col_uf: "Estado", col_total: "Total Graduados"})
st.dataframe(df_tabela, use_container_width=True, hide_index=True)




