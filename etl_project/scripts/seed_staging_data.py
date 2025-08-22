# etl_project/scripts/seed_staging_data.py

import pandas as pd
from faker import Faker
import random
from datetime import date

# Importa a função de conexão do nosso módulo utilitário
from utils.db_connection import get_db_connection

# Inicializa o Faker para gerar dados em português brasileiro
fake = Faker('pt_BR')

def seed_data():
    """
    Função principal para gerar e inserir dados sintéticos em todas as tabelas de staging.
    """
    conn = get_db_connection()
    if conn is None:
        print("Não foi possível conectar ao banco. Abortando o seeding.")
        return

    try:
        cursor = conn.cursor()

        # --- 1. DEFINIR NOSSAS ENTIDADES DE NEGÓCIO ---
        print("Definindo entidades de negócio...")
        centros_custo = {"CC_VENDAS": "VENDAS", "CC_MARKETING": "MARKETING", "CC_TI": "TI", "CC_ADM": "ADM", "CC_RH": "RH"}
        contas_contabeis = {"4.1.1.01": "Receita de Vendas", "5.1.1.01": "Salários e Encargos", "5.1.1.02": "Marketing e Publicidade", "5.2.1.01": "Aluguel e Condomínio", "5.3.1.04": "Software e Licenças", "5.3.1.09": "Serviços de Terceiros"}
        produtos = {"PROD-A": "Produto Alpha", "PROD-B": "Produto Beta", "PROD-C": "Produto Gamma"}
        start_date = date(2023, 1, 1)
        end_date = date(2024, 12, 31)
        print("Entidades definidas.")

        # --- 2. GERAR DADOS PARA CADA TABELA DE STAGING ---
        print("Gerando dados sintéticos...")

        # a) stg_erp_lancamentos (2000 lançamentos)
        erp_data = []
        for i in range(2000):
            conta_id = random.choice(list(contas_contabeis.keys()))
            valor = random.uniform(100, 5000) * -1 if conta_id.startswith('5') else random.uniform(500, 15000)
            erp_data.append({"id_transacao": f"TXN-{i+1:05d}", "data": fake.date_between(start_date=start_date, end_date=end_date), "conta": conta_id, "centro_custo_id": random.choice(list(centros_custo.keys())), "valor": round(valor, 2), "detalhes": fake.sentence(nb_words=4)})
        df_erp = pd.DataFrame(erp_data)
        print(f"- {len(df_erp)} registros gerados para stg_erp_lancamentos.")

        # b) stg_conciliacao_bancaria (3000 transações)
        conciliacao_data = []
        for _ in range(3000):
            tipo = random.choice(["ENTRADA", "SAIDA"])
            valor = random.uniform(50, 8000) * (-1 if tipo == "SAIDA" else 1)
            conciliacao_data.append({"data": fake.date_between(start_date=start_date, end_date=end_date), "historico": fake.sentence(nb_words=6), "valor": round(valor, 2), "tipo": tipo})
        df_conciliacao = pd.DataFrame(conciliacao_data)
        print(f"- {len(df_conciliacao)} registros gerados para stg_conciliacao_bancaria.")

        # c) stg_planilha_mensal (500 lançamentos manuais)
        planilha_data = []
        for _ in range(500):
            conta_id = random.choice(list(contas_contabeis.keys()))
            valor = random.uniform(50, 1000) * -1 if conta_id.startswith('5') else random.uniform(100, 2000)
            planilha_data.append({"data_lancamento": fake.date_between(start_date=start_date, end_date=end_date), "conta_contabil": conta_id, "centro_custo": random.choice(list(centros_custo.values())), "valor": round(valor, 2), "descricao": "Ajuste manual" })
        df_planilha = pd.DataFrame(planilha_data)
        print(f"- {len(df_planilha)} registros gerados para stg_planilha_mensal.")

        # d) stg_banco_transacional (1500 vendas)
        banco_data = []
        for _ in range(1500):
            qtd = random.randint(1, 10)
            vlr_unit = random.uniform(10, 850)
            banco_data.append({"id_venda": fake.uuid4(), "data_venda": fake.date_time_between(start_date=start_date, end_date=end_date), "id_produto": random.choice(list(produtos.keys())), "quantidade": qtd, "valor_unitario": round(vlr_unit, 2), "cliente_id": f"CLI-{random.randint(100, 500)}"})
        df_banco = pd.DataFrame(banco_data)
        print(f"- {len(df_banco)} registros gerados para stg_banco_transacional.")

        # e) stg_metas_vendas
        metas_data = []
        for ano in [2023, 2024]:
            for mes in range(1, 13):
                metas_data.append({"ano": ano, "mes": mes, "centro_custo": "VENDAS", "meta_valor": random.uniform(20000, 50000)})
        df_metas = pd.DataFrame(metas_data)
        print(f"- {len(df_metas)} registros gerados para stg_metas_vendas.")


        # --- 3. INSERIR OS DADOS NO BANCO ---
        print("\nLimpando todas as tabelas de staging...")
        cursor.execute("TRUNCATE TABLE stg_erp_lancamentos, stg_conciliacao_bancaria, stg_planilha_mensal, stg_banco_transacional, stg_metas_vendas CASCADE;")
        
        print("Iniciando inserção dos dados...")

        # Inserir dados do ERP
        for _, row in df_erp.iterrows():
            cursor.execute("INSERT INTO stg_erp_lancamentos (id_transacao, data, conta, centro_custo_id, valor, detalhes) VALUES (%s, %s, %s, %s, %s, %s)", tuple(row))
        print(f"- {len(df_erp)} registros inseridos em stg_erp_lancamentos.")

        # Inserir dados da Conciliação
        for _, row in df_conciliacao.iterrows():
            cursor.execute("INSERT INTO stg_conciliacao_bancaria (data, historico, valor, tipo) VALUES (%s, %s, %s, %s)", tuple(row))
        print(f"- {len(df_conciliacao)} registros inseridos em stg_conciliacao_bancaria.")

        # Inserir dados da Planilha
        for _, row in df_planilha.iterrows():
            cursor.execute("INSERT INTO stg_planilha_mensal (data_lancamento, conta_contabil, centro_custo, valor, descricao) VALUES (%s, %s, %s, %s, %s)", tuple(row))
        print(f"- {len(df_planilha)} registros inseridos em stg_planilha_mensal.")
        
        # Inserir dados do Banco Transacional
        for _, row in df_banco.iterrows():
            cursor.execute("INSERT INTO stg_banco_transacional (id_venda, data_venda, id_produto, quantidade, valor_unitario, cliente_id) VALUES (%s, %s, %s, %s, %s, %s)", tuple(row))
        print(f"- {len(df_banco)} registros inseridos em stg_banco_transacional.")

        # Inserir dados das Metas
        for _, row in df_metas.iterrows():
            cursor.execute("INSERT INTO stg_metas_vendas (ano, mes, centro_custo, meta_valor) VALUES (%s, %s, %s, %s)", tuple(row))
        print(f"- {len(df_metas)} registros inseridos em stg_metas_vendas.")
        
        conn.commit()
        print("\nTodos os dados sintéticos foram inseridos com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro durante o seeding: {e}")
        conn.rollback()
    finally:
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        if conn and not conn.closed:
            conn.close()
            print("Conexão com o PostgreSQL fechada.")

if __name__ == '__main__':
    seed_data()