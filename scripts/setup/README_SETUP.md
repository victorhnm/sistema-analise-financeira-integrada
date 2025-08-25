# Setup Manual do Supabase

## Passo 1: Executar SQL no Dashboard

Acesse: https://supabase.com/dashboard/project/otzqqbcxqfpxzzopcxsk

Va em **SQL Editor** e execute o script completo abaixo:

```sql
-- Integrated Financial Analysis - Database Schema
-- Executar no SQL Editor do Supabase

-- Criar schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;  
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS marts;

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

-- Fato: Financials Quarterly
CREATE TABLE IF NOT EXISTS marts.fact_financials_quarterly (
    financial_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES core.dim_company(company_id),
    period_end_date DATE NOT NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_quarter INTEGER NOT NULL,
    currency TEXT DEFAULT 'USD',
    
    -- Income Statement
    revenue DECIMAL(19,4),
    gross_profit DECIMAL(19,4),
    operating_income DECIMAL(19,4),
    net_income DECIMAL(19,4),
    ebitda DECIMAL(19,4),
    
    -- Balance Sheet
    total_assets DECIMAL(19,4),
    total_liabilities DECIMAL(19,4),
    shareholders_equity DECIMAL(19,4),
    cash_and_equivalents DECIMAL(19,4),
    total_debt DECIMAL(19,4),
    
    -- Cash Flow
    operating_cash_flow DECIMAL(19,4),
    investing_cash_flow DECIMAL(19,4),
    financing_cash_flow DECIMAL(19,4),
    free_cash_flow DECIMAL(19,4),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, period_end_date)
);

-- Fato: Financials TTM
CREATE TABLE IF NOT EXISTS marts.fact_financials_ttm (
    ttm_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES core.dim_company(company_id),
    as_of_date DATE NOT NULL,
    
    -- TTM Base Metrics
    revenue_ttm DECIMAL(19,4),
    net_income_ttm DECIMAL(19,4),
    operating_income_ttm DECIMAL(19,4),
    ebitda_ttm DECIMAL(19,4),
    free_cash_flow_ttm DECIMAL(19,4),
    
    -- Calculated Ratios
    gross_margin DECIMAL(8,6),
    operating_margin DECIMAL(8,6),
    net_margin DECIMAL(8,6),
    roe DECIMAL(8,6),
    roa DECIMAL(8,6),
    debt_to_equity DECIMAL(8,6),
    current_ratio DECIMAL(8,6),
    
    -- Growth Metrics
    revenue_growth_yoy DECIMAL(8,6),
    net_income_growth_yoy DECIMAL(8,6),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, as_of_date)
);

-- Inserir dados seed
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

-- Inserir dados de dimensão de data (últimos 5 anos)
INSERT INTO core.dim_date (date_key, year, quarter, month, fiscal_year, fiscal_quarter, is_quarter_end, is_year_end)
SELECT 
    d::DATE as date_key,
    EXTRACT(YEAR FROM d) as year,
    EXTRACT(QUARTER FROM d) as quarter, 
    EXTRACT(MONTH FROM d) as month,
    CASE 
        WHEN EXTRACT(MONTH FROM d) >= 10 THEN EXTRACT(YEAR FROM d) + 1
        ELSE EXTRACT(YEAR FROM d)
    END as fiscal_year,
    CASE 
        WHEN EXTRACT(MONTH FROM d) IN (10,11,12) THEN 1
        WHEN EXTRACT(MONTH FROM d) IN (1,2,3) THEN 2
        WHEN EXTRACT(MONTH FROM d) IN (4,5,6) THEN 3
        ELSE 4
    END as fiscal_quarter,
    EXTRACT(DAY FROM (d + INTERVAL '1 month')::DATE - INTERVAL '1 day') = EXTRACT(DAY FROM d) 
        AND EXTRACT(MONTH FROM d) IN (3,6,9,12) as is_quarter_end,
    EXTRACT(DAY FROM (d + INTERVAL '1 month')::DATE - INTERVAL '1 day') = EXTRACT(DAY FROM d)
        AND EXTRACT(MONTH FROM d) = 12 as is_year_end
FROM generate_series(
    DATE_TRUNC('year', CURRENT_DATE) - INTERVAL '5 years',
    CURRENT_DATE,
    '1 day'::INTERVAL
) AS d
ON CONFLICT (date_key) DO NOTHING;

-- Verificar criação
SELECT schemaname, count(*) as tables
FROM pg_tables 
WHERE schemaname IN ('raw', 'staging', 'core', 'marts')
GROUP BY schemaname
ORDER BY schemaname;

-- Verificar dados seed
SELECT 'dim_company' as table_name, count(*) as records FROM core.dim_company
UNION ALL
SELECT 'dim_currency' as table_name, count(*) as records FROM core.dim_currency  
UNION ALL
SELECT 'dim_date' as table_name, count(*) as records FROM core.dim_date;
```

## Passo 2: Verificar Resultados

Após executar o SQL, você deve ver:

```
Schema raw: 1 tabelas
Schema staging: 1 tabelas  
Schema core: 3 tabelas
Schema marts: 2 tabelas

dim_company: 5 records
dim_currency: 4 records
dim_date: ~1800+ records
```

## Passo 3: Configurar .env

Crie um arquivo `.env` na raiz do projeto:

```bash
# SUPABASE CONFIGURATION  
SUPABASE_HOST=db.otzqqbcxqfpxzzopcxsk.supabase.co
SUPABASE_PASSWORD=SUA_SENHA_AQUI
SUPABASE_PORT=5432
SUPABASE_USER=postgres
SUPABASE_DBNAME=postgres

# SEC EDGAR API
SEC_USER_AGENT="Financial Analysis Bot your.email@example.com"

# CONFIGURACOES GERAIS
LOG_LEVEL=INFO
API_PORT=8000
```

## Passo 4: Testar Conexão

Execute um teste básico:

```sql
-- No SQL Editor do Supabase
SELECT 
    c.company_name,
    c.ticker,
    c.sector
FROM core.dim_company c
WHERE c.is_active = true
ORDER BY c.ticker;
```

## Próximos Passos

1. **ETL**: Executar scripts para carregar dados financeiros reais
2. **API**: Testar endpoints da FastAPI
3. **Power BI**: Conectar e criar dashboards
4. **dbt**: Executar transformações avançadas

## Troubleshooting

### Erro de Permissão
Se houver erro de permissão, execute:
```sql
GRANT USAGE ON SCHEMA raw, staging, core, marts TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA raw, staging, core, marts TO postgres;
```

### Constraint Errors
Se houver erro de foreign key:
```sql
-- Verificar dependências
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint 
WHERE contype = 'f';
```