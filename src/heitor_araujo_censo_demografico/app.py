import pandas as pd #type: ignore
import numpy as np #type: ignore
import streamlit as st #type: ignore
import plotly.express as px #type: ignore
import asyncio #type: ignore
import os #type: ignore

class EstiamtivaCapitaisDOU():

    def get_capitais(self):
        df = pd.read_csv("./src/heitor_araujo_censo_demografico/estimativa_capitais_2026.csv")
        return df

    async def first_rodeo(self):
        df = pd.read_excel("./src/heitor_araujo_censo_demografico/estimativa_dou_2026.xlsx")
        df = df.drop(columns=['Unnamed: 4'])

        df.columns = ['uf', 'cod_uf', 'cod_munic', 'nome_munic', 'populacao_estimada']

        df = df.astype({'cod_munic': 'str'})

        df_limpo = df[df['uf'] != "UF"]

        cap_cod = [
            ("MG","6200"),
            ("SP","50308"),
            ("SE","308"),
            ("AC","401"),
            ("AP","303"),
            ("AM","2603"),
            ("PA","1402"),
            ("RO","205"),
            ("RR","100"),
            ("TO","21000"),
            ("AL","4302"),
            ("BA","27408"),
            ("CE","4400"),
            ("MA","11300"),
            ("PB","7507"),
            ("PE","11606"),
            ("PI","11001"),
            ("RN","8102"),
            ("DF","108"),
            ("GO","8707"),
            ("MT","3403"),
            ("MS","2704"),
            ("ES","5309"),
            ("RJ","4557"),
            ("PR","6902"),
            ("SC","5407"),
            ("RS","14902")
        ]

        df_cap = df_limpo[df_limpo[['uf','cod_munic']].apply(tuple,axis=1).isin(cap_cod)]

        norte = ["RO", "AC", "AM", "RR", "TO", "AP", "PA"]
        nordeste = ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"]
        sudeste = ["ES", "SP", "MG", "RJ"]
        centro = ["GO", "MT", "MS", "DF"]
        sul =  ["PR", "RS", "SC"]

        con = [
            df_cap["uf"].isin(norte),
            df_cap["uf"].isin(nordeste),
            df_cap["uf"].isin(centro),
            df_cap["uf"].isin(sudeste),
            df_cap["uf"].isin(sul)
        ]

        result = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]

        df_cap["regiao"] = np.select(con, result, default="Falhou.")

        df_cap["populacao_estimada"] = pd.to_numeric(
            df_cap["populacao_estimada"].astype(str).str.replace('.', '', regex=False),
            errors='coerce')

        df_cap.to_csv('estimativa_capitais_2026.csv', index=False)

        print("Gerar o gráfico agora? (S/N)")
        answer = input()
        if answer.lower() == "s":
            await self.graph()
            return
        
        print("Tabela filtrada criada com sucesso! Desligando. . .")
        return

    async def graph(self):
        st.set_page_config(
        page_title="Gráfico DOU",
        page_icon="🔎",
        layout="wide"
        )

        df = self.get_capitais()

        st.sidebar.divider()
        st.sidebar.header("Filtros Censo Demográfico")
        select = st.sidebar.multiselect(
            "Selecione a Região:",
            options=df["regiao"].unique(),
            default=df["regiao"].unique()
        )

        filtro = df[df["regiao"].isin(select)]
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
            st.plotly_chart(fig_linha, width=1100, height=300)

        with col3:
            st.subheader("Quantidade de População Estimada por Região (Linha)")
            fig_linha = px.line(filtro, x="populacao_estimada", y="regiao", labels={"populacao_estimada": "População Estimada", "regiao": "Região"}, hover_name="nome_munic", color="regiao", markers=True)
            st.plotly_chart(fig_linha, width=1100, height=300)

        
        with st.expander("Ver base de dados completa"):
            st.dataframe(filtro, width=1100, height=300)

if not os.path.exists("./src/heitor_araujo_censo_demografico/estimativa_capitais_2026.csv"):
    estimativa = EstiamtivaCapitaisDOU()
    asyncio.run(estimativa.first_rodeo())
else:
    grafico = EstiamtivaCapitaisDOU()
    asyncio.run(grafico.graph())