import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Painel de Emprego", layout="wide")

st.title("Painel de Emprego: Ministério, SEBRAE e Indústria")
st.write("Fonte dos dados: Pesquisa Nacional por Amostra de Domicílios Contínua - PNAD Contínua (IBGE)")

# dados limpos
try:
    df = pd.read_csv("dados_pnad_limpos.csv")
except FileNotFoundError:
    st.error("Erro: O arquivo 'dados_pnad_limpos.csv' não foi encontrado. Execute o script 'tratar_dados.py' primeiro!")
    st.stop()

st.subheader("Resultados Consolidados da Análise")

# Calcúlos
media_valor = df['Valor'].mean()
mediana_valor = df['Valor'].median()

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
    df_pizza = df[df['Valor'] > 0]
    fig_pizza = px.pie(df_pizza, values='Valor', names='Categoria', title="Proporção por Recorte Cadastrado")
    st.plotly_chart(fig_pizza, use_container_width=True)
    
with g_col2:
    # Gráfico de Boxplot
    fig_box = px.box(df, x='Ano', y='Valor', color='Categoria', title="Distribuição Estatística (Visão Ministério)")
    st.plotly_chart(fig_box, use_container_width=True)

# Gráfico de Barras
fig_barra = px.bar(df, x='Ano', y='Valor', color='Categoria', barmode='group', title="Evolução por Ano (Visão Indústria/SEBRAE)")
st.plotly_chart(fig_barra, use_container_width=True)

st.write("Dados de 2012 a 2016")
st.write("Conclusão")
st.write("Os dados exibidos foram pré-processados a partir da estrutura original da PNAD Contínua (IBGE), unificando os blocos informativos em um repositório tabular limpo, livre de registros duplicados e dados nulos.")
