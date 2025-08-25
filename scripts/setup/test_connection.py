#!/usr/bin/env python3
"""
Teste simples de conexão com Supabase
Usar apenas bibliotecas padrão do Python
"""

import os
import urllib.request
import urllib.parse
import json
import sys

def get_env_var(key, default=None):
    """Le variavel de ambiente ou do arquivo .env"""
    value = os.getenv(key, default)
    if value:
        return value
    
    # Tentar ler do .env
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.strip().startswith(key + '='):
                    return line.strip().split('=', 1)[1]
    except FileNotFoundError:
        pass
    
    return default

def test_supabase_connection():
    """Teste básico de conectividade com Supabase"""
    print("=== TESTE DE CONEXAO SUPABASE ===")
    
    # Obter credenciais
    host = get_env_var('SUPABASE_HOST', 'db.otzqqbcxqfpxzzopcxsk.supabase.co')
    password = get_env_var('SUPABASE_PASSWORD')
    
    if not password:
        print("[ERRO] SUPABASE_PASSWORD nao encontrada no .env")
        return False
    
    print(f"Host: {host}")
    print(f"Password: {'*' * len(password)}")
    
    # Usar REST API do Supabase para teste básico
    project_id = host.replace('db.', '').replace('.supabase.co', '')
    api_url = f"https://{project_id}.supabase.co/rest/v1/"
    
    print(f"API URL: {api_url}")
    
    # Preparar headers para autenticação (usando service_role key se disponível)
    headers = {
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # Teste simples: tentar acessar endpoint de health
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.getcode() == 200:
                print("[OK] Supabase acessível via REST API")
                return True
            else:
                print(f"[WARN] Resposta inesperada: {response.getcode()}")
                return False
                
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("[INFO] Supabase requer autenticação (normal)")
            print("[OK] Supabase está online e respondendo")
            return True
        else:
            print(f"[ERRO] HTTP Error: {e.code}")
            return False
    except Exception as e:
        print(f"[ERRO] Conexão falhou: {e}")
        return False

def create_sample_data():
    """Cria dados de exemplo diretos via SQL"""
    print("\n=== INSTRUCOES PARA POPULAR DADOS ===")
    
    print("Execute no SQL Editor do Supabase:")
    print("https://supabase.com/dashboard/project/otzqqbcxqfpxzzopcxsk")
    
    sql_sample = """
-- Dados de exemplo para testes
INSERT INTO marts.fact_financials_quarterly (
    company_id, 
    period_end_date, 
    fiscal_year, 
    fiscal_quarter,
    revenue,
    net_income,
    total_assets
) 
SELECT 
    c.company_id,
    '2023-12-31'::DATE,
    2023,
    4,
    CASE 
        WHEN c.ticker = 'AAPL' THEN 119575000000
        WHEN c.ticker = 'MSFT' THEN 86230000000  
        WHEN c.ticker = 'AMZN' THEN 170000000000
        ELSE 50000000000
    END as revenue,
    CASE
        WHEN c.ticker = 'AAPL' THEN 33916000000
        WHEN c.ticker = 'MSFT' THEN 22291000000
        WHEN c.ticker = 'AMZN' THEN 10600000000  
        ELSE 5000000000
    END as net_income,
    CASE
        WHEN c.ticker = 'AAPL' THEN 365725000000
        WHEN c.ticker = 'MSFT' THEN 411976000000
        WHEN c.ticker = 'AMZN' THEN 527854000000
        ELSE 100000000000
    END as total_assets
FROM core.dim_company c
WHERE c.ticker IN ('AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META')
ON CONFLICT (company_id, period_end_date) DO UPDATE SET
    revenue = EXCLUDED.revenue,
    net_income = EXCLUDED.net_income,
    total_assets = EXCLUDED.total_assets;

-- Verificar dados inseridos
SELECT 
    c.ticker,
    c.company_name,
    f.revenue / 1000000000.0 as revenue_billions,
    f.net_income / 1000000000.0 as net_income_billions
FROM marts.fact_financials_quarterly f
JOIN core.dim_company c ON f.company_id = c.company_id
ORDER BY f.revenue DESC;
"""
    
    print(sql_sample)
    return True

def main():
    print("TESTE DE SETUP SUPABASE")
    print("=" * 40)
    
    # Teste 1: Conectividade
    if test_supabase_connection():
        print("\n[OK] Conectividade verificada")
    else:
        print("\n[ERRO] Falha na conectividade")
        return
    
    # Teste 2: Instruções para dados
    create_sample_data()
    
    print("\n=== PROXIMOS PASSOS ===")
    print("1. Execute o SQL acima no dashboard Supabase")
    print("2. Execute: python test_api_db_connection.py")
    print("3. Abra Power BI e teste a conexão")
    print("4. Dashboard: https://supabase.com/dashboard/project/otzqqbcxqfpxzzopcxsk")

if __name__ == "__main__":
    main()