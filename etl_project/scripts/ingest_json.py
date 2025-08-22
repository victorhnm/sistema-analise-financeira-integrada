# etl_project/scripts/ingest_json.py

import pandas as pd
from utils.db_connection import get_db_connection

def ingest_json_erp(filepath: str):
    """
    Lê um arquivo JSON de lançamentos do ERP e o insere em uma tabela de staging.
    """
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        
        # Lê o arquivo JSON usando Pandas
        df = pd.read_json(filepath)
        print(f"Lidos {len(df)} registros do arquivo JSON.")

        # Limpa a tabela de staging
        cursor.execute("TRUNCATE TABLE stg_erp_lancamentos;")
        print("Tabela stg_erp_lancamentos limpa.")

        # Insere os dados
        for index, row in df.iterrows():
            cursor.execute(
                """
                INSERT INTO stg_erp_lancamentos (id_transacao, data, conta, centro_custo_id, valor, detalhes)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (row['id_transacao'], row['data'], row['conta'], row['centro_custo_id'], row['valor'], row['detalhes'])
            )
        
        conn.commit()
        print(f"{len(df)} registros inseridos com sucesso na stg_erp_lancamentos.")

    except Exception as e:
        print(f"Erro ao ingerir dados do JSON: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("Conexão com o PostgreSQL fechada.")

if __name__ == '__main__':
    json_file_path = 'sources_data/erp_lancamentos.json'
    ingest_json_erp(json_file_path)