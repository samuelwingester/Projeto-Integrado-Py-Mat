import plotly.express as px
import geopandas as gpd
import streamlit as st
import pandas as pd

import json

from database import connect, MunicipiosRepository, EstadosRepository
from data import ADH_DATA_FIELDS
from dirs_paths import STORAGE_DIR

BASE_PATH = STORAGE_DIR / 'IDH' / 'geo_data'

ESTADOS_DICT = { 
    'MG' : 'MINAS_GERAIS',
    'MA' : 'MARANHAO',
    'BA' : 'BAHIA',
    'AC' : 'ACRE',
    'PA' : 'PARA'
}

HOVER_LABELS = {
    'CD_MUN': 'Código IBGE',
    'ano': 'Ano',
    'idhm': 'IDH Municipal',
    'idhm_e': 'IDH Educação',
    'idhm_l': 'IDH Longevidade',
    'idhm_r': 'IDH Renda',
    'expectativa_vida': 'Expectativa de vida',
    'mortalidade_1': 'Mortalidade infantil',
    'mortalidade_5': 'Mortalidade até 5 anos',
    'expectativa_anos_estudo': 'Expectativa de anos de estudo',
    'taxa_analfabetismo_15_mais': 'Taxa de analfabetismo (15+)',
    'renda_pc': 'Renda per capita',
    'indice_gini': 'Índice de Gini',
    'prop_pobreza': 'Proporção de pobreza'
}

HOVER_DATA = {
    'ano': True,
    'idhm': ':.3f',
    'idhm_e': ':.3f',
    'idhm_l': ':.3f',
    'idhm_r': ':.3f',
    'expectativa_vida': ':.2f',
    'mortalidade_1': ':.2f',
    'mortalidade_5': ':.2f',
    'expectativa_anos_estudo': ':.2f',
    'taxa_analfabetismo_15_mais': ':.2f',
    'renda_pc': ':.2f',
    'indice_gini': ':.3f',
    'prop_pobreza': ':.2f'
}

INDICADORES_RANGES = {
    'idhm': (0, 1),
    'idhm_e': (0, 1),
    'idhm_l': (0, 1),
    'idhm_r': (0, 1),
    'indice_gini': (0, 1),
}

INDICADORES_ESCALA_COR = {
    'idhm': False,
    'idhm_e': False,
    'idhm_l': False,
    'idhm_r': False,

    'expectativa_vida': False,
    'mortalidade_1': True,
    'mortalidade_5': True,
    'expectativa_anos_estudo': False,
    'taxa_analfabetismo_15_mais': True,
    'renda_pc': False,
    'indice_gini': True,
    'prop_pobreza': True
}

filepaths = {}
for sigla, nome in ESTADOS_DICT.items():
    filepaths[sigla] = BASE_PATH / f'MUNICIPIOS_{nome}' / f'{sigla}_Municipios_2025.shp'

@st.cache_data
def get_geo_data( sigla_uf:str ):
    if sigla_uf not in filepaths:
        raise ValueError(f'UF não encontrada: {sigla_uf}')
    gdf = gpd.read_file( filepaths[sigla_uf] ) 
    gdf['CD_MUN'] = gdf['CD_MUN'].astype(str).str.zfill(7)
    return gdf

def merge_dfs( gdf:gpd.GeoDataFrame, df:pd.DataFrame ) -> gpd.GeoDataFrame:
    return gdf.merge( df, left_on='CD_MUN', right_on='id_municipio', how='left', validate='one_to_one' )

@st.cache_data
def get_all_geo_data( ano:int ):
    mun_repo = MunicipiosRepository( connect() )
    gdfs = []
    
    for sigla in ESTADOS_DICT.keys():
        df_idh = mun_repo.get_idh_by_ano_uf(ano, sigla)

        gdf = get_geo_data(sigla)
        gdf = merge_dfs(gdf, df_idh)

        gdfs.append(gdf)

    gdf_completo = gpd.GeoDataFrame( pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs )
    geojson = json.loads( gdf_completo.to_json() )
    return gdf_completo, geojson

def make_complete_map( indicador:str, ano:int ):
    gdf, geojson = get_all_geo_data( ano )

    escala_cor = 'RdYlGn' if not INDICADORES_ESCALA_COR.get( indicador, False ) else 'RdYlGn_r'
    
    fig = px.choropleth_map( 
        gdf,
        geojson=geojson,
        locations='CD_MUN',
        featureidkey='properties.CD_MUN',

        color=indicador,
        hover_name='NM_MUN',

        hover_data={ 'CD_MUN': True, **HOVER_DATA },
        labels=HOVER_LABELS,
        range_color=INDICADORES_RANGES.get(indicador),
        color_continuous_scale=escala_cor, # Escala de Cores

        map_style='carto-positron', # Estilo do Mapa, verificar depois
        center={ 'lat': -14.2350, 'lon': -51.9253 }, #posicao inicial do mapa: Meio do Brasil ~~~
        zoom=3.5,
        opacity=0.7
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=650
    )

    return fig

def make_radar_graph( ano:int ):
    rep = EstadosRepository( connect() ) #muito merda
    df = rep.get_idh_by_ano( ano )

    df = df.melt(
        id_vars='sigla_uf',
        value_vars=['idhm_e', 'idhm_l', 'idhm_r'],
        var_name='indicador',
        value_name='valor'
    )
    
    fig = px.line_polar(
        df, r='valor',
        theta='indicador',
        color='sigla_uf',
        line_close=True,
        markers=True
    )

    fig.update_traces( fill='toself', opacity=0.6 )

    fig.update_layout( 
        polar=dict( radialaxis=dict( visible=True, range=[0, 1] ) ), 
        showlegend=True
    )

    st.plotly_chart(fig, width='stretch')

def make_bar_graph( uf:str ):
    rep = EstadosRepository( connect() ) #muito merda
    df = rep.get_idh_by_uf( uf )

    df = df.melt( 
        id_vars='ano',
        value_vars=['idhm', 'idhm_e', 'idhm_l', 'idhm_r'],
        var_name='indicador', value_name='valor'
    )

    labels = {
        'idhm': 'IDHM',
        'idhm_e': 'Educação',
        'idhm_l': 'Longevidade',
        'idhm_r': 'Renda'
    }

    fig = px.bar(
        df, 
        x='ano', y='valor',
        color='indicador', 
        barmode='group',
        labels={
            'ano': 'Ano',
            'valor': 'Índice',
            'indicador': 'Indicador'
        },
        title=f'Evolução do IDHM por dimensão ( {uf} )',
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig.for_each_trace(
        lambda trace: trace.update(
            name=labels[trace.name]
        )
    )

    fig.update_yaxes(range=[0, 1])

    st.plotly_chart(fig, width='stretch')
