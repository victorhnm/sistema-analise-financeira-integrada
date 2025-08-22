# etl_project/scripts/ingest_sheets.py

import pandas as pd
from utils.db_connection import get_db_connection

def ingest_sheets_metas(filepath: str):
    """
    Lê um arquivo CSV simulando uma exportação do Google Sheets
    e o insere em uma tabela de staging.
    """
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        
        df = pd.read_csv(filepath)
        print(f"Lidos {len(df)} registros do arquivo de metas (Google Sheets).")

        cursor.execute("TRUNCATE TABLE stg_metas_vendas;")
        print("Tabela stg_metas_vendas limpa.")

        for index, row in df.iterrows():
            cursor.execute(
                """
                INSERT INTO stg_metas_vendas (ano, mes, centro_custo, meta_valor)
                VALUES (%s, %s, %s, %s)
                """,
                (row['ano'], row['mes'], row['centro_custo'], row['meta_valor'])
            )
        
        conn.commit()
        print(f"{len(df)} registros inseridos com sucesso na stg_metas_vendas.")

    except Exception as e:
        print(f"Erro ao ingerir dados do Google Sheets: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("Conexão com o PostgreSQL fechada.")

if __name__ == '__main__':
    csv_file_path = 'sources_data/metas_vendas.csv'
    ingest_sheets_metas(csv_file_path)