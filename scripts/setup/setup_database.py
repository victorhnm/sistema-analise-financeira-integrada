#!/usr/bin/env python3
"""
Criar tabelas e popular dados no Supabase via SQL
"""

import urllib.request
import json

# Configurações
PROJECT_ID = 'otzqqbcxqfpxzzopcxsk'
SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90enFxYmN4cWZweHp6b3BjeHNrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTg5MjgyNSwiZXhwIjoyMDcxNDY4ODI1fQ.63nFJeHtFcjbGvTE_GeB5ZyDJG2U8GwJAfwommwVC4o'

def execute_sql_steps():
    """Executar SQL em etapas via Edge Functions"""
    
    # SQL dividido em steps menores
    sql_steps = [
        # Step 1: Criar tabelas de dimensão
        """
        -- Tabela para dados brutos da SEC
        CREATE TABLE IF NOT EXISTS raw.sec_company_facts (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            cik TEXT NOT NULL,
            company_name TEXT,
            ticker TEXT,
            raw_data JSONB NOT NULL,
            ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            file_date DATE DEFAULT CURRENT_DATE,
            UNIQUE(cik, file_date)
        );

        -- Empresas normalizadas
        CREATE TABLE IF NOT EXISTS staging.stg_companies (
            company_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            cik TEXT UNIQUE NOT NULL,
            ticker TEXT,
            company_name TEXT NOT NULL,
            sector TEXT,
            country TEXT DEFAULT 'US',
            is_active BOOLEAN DEFAULT TRUE
        );
        """,
        
        # Step 2: Criar dimensões core
        """
        -- Dimensão: Empresas
        CREATE TABLE IF NOT EXISTS core.dim_company (
            company_id UUID PRIMARY KEY,
            cik TEXT UNIQUE NOT NULL,
            ticker TEXT,
            company_name TEXT NOT NULL,
            sector TEXT,
            country TEXT DEFAULT 'US',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        -- Dimensão: Data
        CREATE TABLE IF NOT EXISTS core.dim_date (
            date_key DATE PRIMARY KEY,
            year INTEGER NOT NULL,
            quarter INTEGER NOT NULL,
            month INTEGER NOT NULL,
            fiscal_year INTEGER,
            fiscal_quarter INTEGER,
            is_quarter_end BOOLEAN DEFAULT FALSE,
            is_year_end BOOLEAN DEFAULT FALSE
        );

        -- Dimensão: Moedas
        CREATE TABLE IF NOT EXISTS core.dim_currency (
            currency_code TEXT PRIMARY KEY,
            currency_name TEXT NOT NULL,
            currency_symbol TEXT,
            is_active BOOLEAN DEFAULT TRUE
        );
        """,
        
        # Step 3: Inserir dados seed
        """
        -- Inserir empresas seed
        INSERT INTO staging.stg_companies (cik, ticker, company_name, sector) VALUES
            ('0000320193', 'AAPL', 'Apple Inc.', 'Technology'),
            ('0000789019', 'MSFT', 'Microsoft Corporation', 'Technology'), 
            ('0001018724', 'AMZN', 'Amazon.com Inc.', 'Consumer Discretionary'),
            ('0001326801', 'META', 'Meta Platforms Inc.', 'Technology'),
            ('0001652044', 'GOOGL', 'Alphabet Inc.', 'Technology')
        ON CONFLICT (cik) DO NOTHING;

        -- Propagar para core
        INSERT INTO core.dim_company (company_id, cik, ticker, company_name, sector, country)
        SELECT company_id, cik, ticker, company_name, sector, country
        FROM staging.stg_companies
        ON CONFLICT (cik) DO UPDATE SET
            ticker = EXCLUDED.ticker,
            company_name = EXCLUDED.company_name,
            sector = EXCLUDED.sector;

        -- Inserir moedas básicas
        INSERT INTO core.dim_currency (currency_code, currency_name, currency_symbol) VALUES
            ('USD', 'US Dollar', '$'),
            ('EUR', 'Euro', '€'),
            ('GBP', 'British Pound', '£'),
            ('CAD', 'Canadian Dollar', 'C$')
        ON CONFLICT (currency_code) DO NOTHING;
        """
    ]
    
    # Executar cada step
    for i, sql in enumerate(sql_steps, 1):
        print(f"=== EXECUTANDO STEP {i} ===")
        print(f"SQL: {sql[:100]}...")
        
        # Tentar via psql direto (comando bash)
        result = execute_sql_via_bash(sql)
        print(f"Resultado Step {i}: {result}")
        print()

def execute_sql_via_bash(sql):
    """Executar SQL via comando bash psql"""
    import subprocess
    import tempfile
    import os
    
    try:
        # Criar arquivo temporário com SQL
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(sql)
            sql_file = f.name
        
        # Comando psql
        cmd = [
            'psql',
            '-h', 'db.otzqqbcxqfpxzzopcxsk.supabase.co',
            '-p', '5432',
            '-U', 'postgres',
            '-d', 'postgres',
            '-f', sql_file,
            '--single-transaction'
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = '996744957Vh@'
        
        result = subprocess.run(
            cmd, 
            env=env, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        # Limpar arquivo temporário
        os.unlink(sql_file)
        
        if result.returncode == 0:
            return {'success': True, 'output': result.stdout}
        else:
            return {'success': False, 'error': result.stderr}
            
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Timeout'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def create_basic_tables_only():
    """Criar apenas tabelas básicas via SQL simples"""
    
    sql = """
    -- Dimensão: Empresas (versão simplificada)
    CREATE TABLE IF NOT EXISTS core.dim_company (
        company_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        cik TEXT UNIQUE NOT NULL,
        ticker TEXT,
        company_name TEXT NOT NULL,
        sector TEXT,
        country TEXT DEFAULT 'US',
        is_active BOOLEAN DEFAULT TRUE
    );

    -- Inserir dados básicos
    INSERT INTO core.dim_company (cik, ticker, company_name, sector) VALUES
        ('0000320193', 'AAPL', 'Apple Inc.', 'Technology'),
        ('0000789019', 'MSFT', 'Microsoft Corporation', 'Technology'), 
        ('0001018724', 'AMZN', 'Amazon.com Inc.', 'Consumer Discretionary'),
        ('0001326801', 'META', 'Meta Platforms Inc.', 'Technology'),
        ('0001652044', 'GOOGL', 'Alphabet Inc.', 'Technology')
    ON CONFLICT (cik) DO NOTHING;

    -- Verificar resultado
    SELECT ticker, company_name FROM core.dim_company ORDER BY ticker;
    """
    
    return execute_sql_via_bash(sql)

def main():
    print("=== CRIANDO TABELAS NO SUPABASE ===")
    print(f"Project: {PROJECT_ID}")
    print()
    
    # Verificar se psql está disponível
    import subprocess
    try:
        result = subprocess.run(['which', 'psql'], capture_output=True)
        if result.returncode == 0:
            print("✅ psql encontrado, tentando execução direta")
            
            # Teste básico primeiro
            basic_result = create_basic_tables_only()
            print(f"Resultado básico: {basic_result}")
            
            if basic_result.get('success'):
                print("\n✅ SUCESSO! Tabela básica criada")
                print("Executando script completo...")
                execute_sql_steps()
            else:
                print("\n❌ Falha na execução básica")
                print("Execute manualmente no SQL Editor:")
                print("https://supabase.com/dashboard/project/otzqqbcxqfpxzzopcxsk/sql")
        else:
            print("❌ psql não encontrado")
            print("\nExecute manualmente:")
            print("1. Acesse: https://supabase.com/dashboard/project/otzqqbcxqfpxzzopcxsk/sql")
            print("2. Cole e execute o arquivo 'populate_supabase_fixed.sql'")
            
    except Exception as e:
        print(f"Erro: {e}")
        print("\nUse método manual no SQL Editor")

if __name__ == "__main__":
    main()