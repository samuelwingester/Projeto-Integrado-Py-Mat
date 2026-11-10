from pandas import DataFrame, read_csv
from dirs_paths import STORAGE_DIR

ESTADOS_DATA_FIELDS = [ 'id_uf', 'sigla', 'nome' ] 
MUNICIPIOS_DATA_FIELDS = [ 'id_municipio', 'id_uf', 'nome', 'sigla_uf' ]
ADH_DATA_FIELDS = [ 'ano', 'idhm', 'idhm_e', 'idhm_l', 'idhm_r', 
                    'expectativa_vida', 'mortalidade_1', 'mortalidade_5',
                    'expectativa_anos_estudo', 'taxa_analfabetismo_15_mais',
                    'renda_pc', 'indice_gini','prop_pobreza' ]

def get_csv_data( filename:str, fields:list[str] ) -> DataFrame:
    return read_csv( STORAGE_DIR / 'IDH' / 'raw' / f'{ filename }.csv', usecols=fields )
   
def get_estados_data() -> DataFrame:
    filename = 'unidades_federais_brasil' 
    return get_csv_data( filename, ESTADOS_DATA_FIELDS ).reset_index(drop=True)

def get_municipios_data( df_uf:DataFrame ) -> DataFrame:
    filename = 'municipios_brasil'
    df = get_csv_data( filename, MUNICIPIOS_DATA_FIELDS )
    df = df[ df[ 'sigla_uf' ].isin( df_uf[ 'sigla' ] ) ].reset_index(drop=True) 
    df['id_municipio'] = ( df['id_municipio'].astype(str).str.zfill(7) )
    return df

def get_estados_idh_data( df_uf:DataFrame ) -> DataFrame:
    filename = 'unidades_federais_brasil_adh'
    df = get_csv_data( filename, ADH_DATA_FIELDS + ['sigla_uf'] )
    return df[ df[ 'sigla_uf' ].isin( df_uf[ 'sigla' ] ) ].reset_index(drop=True)

def get_municipios_idh_data( df_mun:DataFrame ) -> DataFrame:
    filename = 'municipios_brasil_adh'
    df = get_csv_data( filename, ADH_DATA_FIELDS + ['id_municipio'] )
    df['id_municipio'] = ( df['id_municipio'].astype(str).str.zfill(7) )
    return df.merge(
        df_mun[['id_municipio', 'sigla_uf']], on='id_municipio',
        how='inner', validate='many_to_one'
    ).reset_index(drop=True)

