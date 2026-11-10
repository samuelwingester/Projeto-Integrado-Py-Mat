import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Dashboard - Compilação de Dados Gerais",
    layout="wide",
    initial_sidebar_state="expanded")

st.title("Dashboard de Visualização de Dados Gerais")
st.markdown("Conjunto de Dados presentes: Curso Superior, Trabalho e Emprego, Crescimento Demográfico e IDH Municipal.")
st.markdown("Fonte do IBGE")
st.markdown("---")
st.title("Curso Superior - Gustavo Yvo")

from src.gustavo_yvo_curso_superior.main import dados_curso
from src.hebert_velloso_trabalho_emprego.trabalho import dados_emprego
from src.heitor_araujo_censo_demografico.app import EstiamtivaCapitaisDOU

dados_curso_superior, perfil_etario = dados_curso()

estados = ['Minas Gerais', 'Espírito Santo', 'Rio de Janeiro', 'São Paulo']
uf_sel = st.sidebar.multiselect("Selecione os Estados:", options=estados, default=estados, key="uf_selection")

col_uf, col_raca, col_total = dados_curso_superior.columns[0], dados_curso_superior.columns[1], dados_curso_superior.columns[2]


dados_filtro = dados_curso_superior[dados_curso_superior[col_uf].isin(uf_sel)]
df_totais = dados_filtro[dados_filtro[col_raca] == "Total"]

st.subheader("Panorama Geral do Ensino Superior no Sudeste ")
if not df_totais.empty:
    cols = st.columns(len(df_totais))
    for i, (_, row) in enumerate(df_totais.iterrows()):
        cols[i].metric(label=row[col_uf], value=f"{row[col_total]:,.0f} pessoas".replace(',', '.'))
    
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

racas = [r for r in dados_curso_superior[col_raca].dropna().unique() if r != "Total"]
raca_sel = st.sidebar.selectbox("Filtrar Raça/Cor:", options=["Todas"] + racas, key="raca_selection")
df_raca = dados_filtro[(dados_filtro[col_raca] != "Total") & (dados_filtro[col_raca] == raca_sel if raca_sel != "Todas" else True)]

st.divider()

st.subheader("Recorte Demográficos")

if not df_raca.empty and not perfil_etario.empty:
    col5, col6 = st.columns(2)
    with col5:
        fig_raca = px.bar(df_raca, x=col_uf, y=col_total, color=col_raca, barmode="group", labels={col_total: "População", col_uf: "Estado"}, title="Distribuição por Raça/Cor")
        st.plotly_chart(fig_raca, use_container_width=True)

    with col6:
        col_uf_64, col_idade, col_tot_64 = perfil_etario.columns[0], perfil_etario.columns[1], perfil_etario.columns[2]
        df_faixas = perfil_etario[(perfil_etario[col_uf_64].isin(uf_sel)) & (perfil_etario[col_idade] != "Total")]
        
        if not df_faixas.empty:
            fig_idade = px.bar(df_faixas, x=col_uf_64, y=col_tot_64, color=col_idade, barmode="group", labels={col_tot_64: "Pessoas", col_uf_64: "Estado"}, title="Distribuição por Faixa Etária")
            st.plotly_chart(fig_idade, use_container_width=True)

if not perfil_etario.empty and df_raca.empty:
    st.divider()
    st.subheader("Perfil Etário")
    col_uf_64, col_idade, col_tot_64 = perfil_etario.columns[0], perfil_etario.columns[1], perfil_etario.columns[2]
    df_faixas = perfil_etario[(perfil_etario[col_uf_64].isin(uf_sel)) & (perfil_etario[col_idade] != "Total")]
    
    if not df_faixas.empty:
        fig_idade = px.bar(df_faixas, x=col_uf_64, y=col_tot_64, color=col_idade, barmode="group", labels={col_tot_64: "Pessoas", col_uf_64: "Estado"}, title="Distribuição por Faixa Etária")
        st.plotly_chart(fig_idade, use_container_width=True)

if not df_raca.empty and perfil_etario.empty:
    st.divider()
    st.subheader("Recorte Demográfico por Raça/Cor")
    fig_raca = px.bar(df_raca, x=col_uf, y=col_total, color=col_raca, barmode="group", labels={col_total: "População", col_uf: "Estado"}, title="Distribuição por Raça/Cor")
    st.plotly_chart(fig_raca, use_container_width=True)

st.subheader("Estatísticas Descritivas e Indicadores Avançados")
df_totais_uf = dados_filtro[dados_filtro[col_raca] == "Total"]

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

col5, col6, col7 = st.columns(3)
with col5:
    fig_box = px.box(df_totais_uf, y=col_total, title='Distribuição e Quartis (Boxplot)', labels={col_total: 'População Graduada'})
    st.plotly_chart(fig_box, use_container_width=True, key="estat_box")

with col6:
    fig_hist = px.histogram(df_totais_uf, x=col_total, nbins=len(df_totais_uf) if len(df_totais_uf) > 0 else 1, title='Frequência por Estado', labels={col_total: 'População Graduada'})
    st.plotly_chart(fig_hist, use_container_width=True, key="estat_hist")

with col7:
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
    
    st.plotly_chart(fig_horizontal, use_container_width=True, key="odd_one_out")

st.success(f"""
**Análise dos Dados Reais - Medidas de Tendência Central e Dispersão:**
- **Tendência Central:** A **média** de **{media:,.0f}** pessoas e a **mediana** de **{mediana:,.0f}** refletem a realidade demográfica e o impacto concentrador dos estados selecionados.
- **Dispersão:** O **desvio padrão** de **{desvio_padrao:,.0f}** evidencia a heterogeneidade e a disparidade populacional entre as unidades da federação.
- **Quartis e IQR:** O intervalo interquartil (**IQR = {iqr:,.0f}**) delimita a faixa central de variação dos estados analisados.
""")

st.divider()
st.title("Trabalho e Emprego - Hebert Velloso")

df_emprego = dados_emprego()

media_valor = df_emprego['Valor'].mean()
mediana_valor = df_emprego['Valor'].median()

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Média Geral dos Indicadores", value=f"{media_valor:.1f}")
with col2:
    st.metric(label="Mediana Geral dos Indicadores", value=f"{mediana_valor:.1f}")


st.write("### Gráficos de Análise")

# Um do lado do outro
g_col1, g_col2 = st.columns(2)

with g_col1:
    # Gráfico de Pizza
    df_pizza = df_emprego[df_emprego['Valor'] > 0]
    fig_pizza = px.pie(df_pizza, values='Valor', names='Categoria', title="Proporção por Recorte Cadastrado")
    st.plotly_chart(fig_pizza, use_container_width=True, key="graf_pizza")
    
with g_col2:
    # Gráfico de Boxplot
    fig_box = px.box(df_emprego, x='Ano', y='Valor', color='Categoria', title="Distribuição Estatística (Visão Ministério)")
    st.plotly_chart(fig_box, use_container_width=True, key="graf_box")

# Gráfico de Barras
fig_barra = px.bar(df_emprego, x='Ano', y='Valor', color='Categoria', barmode='group', title="Evolução por Ano (Visão Indústria/SEBRAE)")
st.plotly_chart(fig_barra, use_container_width=True, key="graf_barra")

st.success("""Dados de 2012 a 2016
Conclusão
Os dados exibidos foram pré-processados a partir da estrutura original da PNAD Contínua (IBGE), unificando os blocos informativos em um repositório tabular limpo, livre de registros duplicados e dados nulos.
""")

st.divider()
st.title("Censo Demográfico - Heitor Araújo")

dados_censo = EstiamtivaCapitaisDOU()

df_censo = dados_censo.get_capitais()

select = st.sidebar.multiselect(
            "Selecione a Região:",
            options=df_censo["regiao"].unique(),
            default=df_censo["regiao"].unique(),
            key="regiao_selection"
        )

filtro = df_censo[df_censo["regiao"].isin(select)]

st.title("Gráfico de Projeção Demográfica")
st.markdown("Projeção da Expansão Demográfica das Capitais")

media = filtro["populacao_estimada"].mean()

col1, = st.columns(1)
col1.metric(label="População Média Estimada das Capitais", value=f"{media:,.0f}")

st.divider()

col2, col3 = st.columns(2)

with col2:
    st.subheader("Quantidade de População Estimada por Região (Barras)")
    fig_linha = px.bar(filtro, x="populacao_estimada", y="regiao", labels={"populacao_estimada": "População Estimada", "regiao": "Região"}, color="regiao", barmode="group")
    st.plotly_chart(fig_linha, width=1100, height=300, key="censo_barras")  

with col3:
    st.subheader("Quantidade de População Estimada por Região (Linha)")
    fig_linha = px.line(filtro, x="populacao_estimada", y="regiao", labels={"populacao_estimada": "População Estimada", "regiao": "Região"}, hover_name="nome_munic", color="regiao", markers=True)
    st.plotly_chart(fig_linha, width=1100, height=300, key="censo_linha") 

with st.expander("Ver base de dados completa"):
    st.dataframe(filtro, width=1100, height=300)