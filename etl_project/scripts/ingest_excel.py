# etl_project/scripts/ingest_excel.py

import pandas as pd
from utils.db_connection import get_db_connection

def ingest_excel_mensal(filepath: str):
    """
    Lê uma planilha Excel e a insere em uma tabela de staging.
    """
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        
        # Lê a planilha Excel usando Pandas. A biblioteca openpyxl é usada por baixo dos panos.
        df = pd.read_excel(filepath)
        print(f"Lidos {len(df)} registros do arquivo Excel.")

        # Limpa a tabela de staging antes de inserir novos dados
        cursor.execute("TRUNCATE TABLE stg_planilha_mensal;")
        print("Tabela stg_planilha_mensal limpa.")

        # Insere os dados do DataFrame na tabela de staging
        for index, row in df.iterrows():
            cursor.execute(
                """
                INSERT INTO stg_planilha_mensal (data_lancamento, conta_contabil, centro_custo, valor, descricao)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (row['data_lancamento'], row['conta_contabil'], row['centro_custo'], row['valor'], row['descricao'])
            )
        
        conn.commit()
        print(f"{len(df)} registros inseridos com sucesso na stg_planilha_mensal.")

    except Exception as e:
        print(f"Erro ao ingerir dados do Excel: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("Conexão com o PostgreSQL fechada.")

if __name__ == '__main__':
    excel_file_path = 'sources_data/planilha_mensal.xlsx'
    ingest_excel_mensal(excel_file_path)