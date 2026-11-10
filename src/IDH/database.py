import pandas as pd
import sqlite3

from dirs_paths import STORAGE_DIR
from data import *

DATABASE_DIR = STORAGE_DIR / 'IDH' / 'database'
DATABASE_PATH = DATABASE_DIR / 'idh.db'

TABLE_NAME_ESTADOS = 'estados_brasil'
TABLE_NAME_MUNICIPIOS = 'municipios_brasil'
TABLE_NAME_ESTADOS_IDH = 'estados_idh_brasil'
TABLE_NAME_MUNICIPIOS_IDH = 'municipios_idh_brasil'

def init_database():
    if DATABASE_PATH.exists(): return connect()

    DATABASE_DIR.mkdir(exist_ok=True)
    connection = connect()

    with connection: 
        df_estados = get_estados_data()
        df_municipios = get_municipios_data( df_estados )
    
        save_data( df_estados, TABLE_NAME_ESTADOS, connection )
        save_data( df_municipios, TABLE_NAME_MUNICIPIOS, connection )
        save_data( get_estados_idh_data( df_estados ), TABLE_NAME_ESTADOS_IDH, connection )
        save_data( get_municipios_idh_data( df_municipios ), TABLE_NAME_MUNICIPIOS_IDH, connection )

    return connection

def save_data( df:DataFrame, name:str, connection ):
    df.to_sql( name, connection, if_exists='replace', index=False )

def connect():
    return sqlite3.connect( DATABASE_PATH )

class MunicipiosRepository():
    def __init__( self, connection ):
        self.connection = connection
        self.table = TABLE_NAME_MUNICIPIOS_IDH

    def get_idh_by_ano_uf( self, ano:int, sigla:str ) -> pd.DataFrame:
        query = f"""
            SELECT * FROM { self.table }
            WHERE ano = ? AND sigla_uf = ?;
        """
        return pd.read_sql( query, self.connection, params=(ano, sigla))

    def get_idh_by_ano( self, ano:int ) -> pd.DataFrame:
            query = f"""
                SELECT * FROM { self.table }
                WHERE ano = ?;
            """
            return pd.read_sql( query, self.connection, params=(ano,))

    def get_idh_by_uf( self, sigla:str ) -> pd.DataFrame:
            query = f"""
                SELECT * FROM { self.table }
                WHERE sigla_uf = ?;
            """
            return pd.read_sql( query, self.connection, params=(sigla,))

    def get_all_idh( self ) -> pd.DataFrame:
        query = f"SELECT * FROM { self.table }"
        return pd.read_sql( query, self.connection )

class EstadosRepository():
    def __init__( self, connection ):
        self.connection = connection
        self.table = TABLE_NAME_ESTADOS_IDH

    def get_idh_by_ano_uf( self, ano:int, sigla:str ) -> pd.DataFrame:
        query = f"""
            SELECT * FROM { self.table }
            WHERE ano = ? AND sigla_uf = ?;
        """
        return pd.read_sql( query, self.connection, params=(ano, sigla))

    def get_idh_by_ano( self, ano:int ) -> pd.DataFrame:
            query = f"""
                SELECT * FROM { self.table }
                WHERE ano = ?;
            """
            return pd.read_sql( query, self.connection, params=(ano,))

    def get_idh_by_uf( self, sigla:str ) -> pd.DataFrame:
            query = f"""
                SELECT * FROM { self.table }
                WHERE sigla_uf = ?;
            """
            return pd.read_sql( query, self.connection, params=(sigla,))

    def get_all_idh( self ) -> pd.DataFrame:
        query = f"SELECT * FROM { self.table }"
        return pd.read_sql( query, self.connection )