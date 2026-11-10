import streamlit as st

from database import init_database
from graphs import make_complete_map, make_radar_graph, make_bar_graph, HOVER_LABELS

def idh_app():
    init_database()

    st.set_page_config(layout='wide')

    main_fragment()
    map_fragment()

@st.cache_data
def get_indicadores() -> dict:
    var = HOVER_LABELS.copy()
    var.pop( 'ano' )
    var.pop( 'CD_MUN' )
    return var

@st.fragment
def main_fragment():
    ano = None
    indicador = None
    uf = None
    with st.sidebar:
        indicadores = {
            "idhm":"IDH Municipal",
            "idhm_e":"IDH Educação",
            "idhm_l":"IDH Longevidade",
            "idhm_r":"IDH Renda"
        }
        ano = st.selectbox('Ano', [2010, 2000, 1991])
        indicador = st.selectbox( 'Indicador',
            options=indicadores.keys(),
            format_func=lambda x: indicadores[x]
        )
        uf = st.selectbox( 'Estado', ['MG', 'AC', 'PA', 'MA', 'BA' ] )

    make_radar_graph( ano )
    make_bar_graph( uf )

@st.fragment
def map_fragment():
    with st.form('map_form'):
        indicadores = get_indicadores()
        ano = st.selectbox('Ano', [2010, 2000, 1991])
        indicador = st.selectbox( 'Indicador',
            options= indicadores.keys(),
            format_func=lambda x: indicadores[x]
        )

        submitted = st.form_submit_button( 'Gerar mapa', width='stretch' )

    if 'map_params' not in st.session_state:
        st.session_state.map_params = { 'ano': 2010, 'indicador': 'idhm' }

    if submitted:
        st.session_state.map_params = { 'ano': ano, 'indicador': indicador }

    params = st.session_state.map_params
    fig = make_complete_map( params['indicador'], params['ano'] )
    st.plotly_chart(fig, width='stretch', key='mapa_idh')

if __name__ == '__main__':idh_app()