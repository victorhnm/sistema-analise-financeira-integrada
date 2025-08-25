-- Populate Supabase Database - VERSAO CORRIGIDA
-- Execute este script no SQL Editor do Supabase
-- https://supabase.com/dashboard/project/otzqqbcxqfpxzzopcxsk/sql

-- =============================================================================
-- 1. CRIAR TABELAS (VERSAO CORRIGIDA)
-- =============================================================================

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

-- Fato: Financials TTM (ESTRUTURA CORRIGIDA)
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

-- =============================================================================
-- 2. INSERIR DADOS SEED
-- =============================================================================

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

-- =============================================================================
-- 3. INSERIR DADOS FINANCEIROS DE EXEMPLO
-- =============================================================================

-- Dados Q4 2023 (valores em USD)
INSERT INTO marts.fact_financials_quarterly (
    company_id, 
    period_end_date, 
    fiscal_year, 
    fiscal_quarter,
    revenue,
    gross_profit,
    operating_income,
    net_income,
    ebitda,
    total_assets,
    total_liabilities,
    shareholders_equity,
    cash_and_equivalents,
    total_debt,
    operating_cash_flow,
    free_cash_flow
) 
SELECT 
    c.company_id,
    '2023-12-31'::DATE,
    2023,
    4,
    CASE 
        WHEN c.ticker = 'AAPL' THEN 119575000000.0000
        WHEN c.ticker = 'MSFT' THEN 62016000000.0000
        WHEN c.ticker = 'AMZN' THEN 170000000000.0000
        WHEN c.ticker = 'GOOGL' THEN 86254000000.0000
        WHEN c.ticker = 'META' THEN 40111000000.0000
    END as revenue,
    CASE 
        WHEN c.ticker = 'AAPL' THEN 54738000000.0000
        WHEN c.ticker = 'MSFT' THEN 43075000000.0000
        WHEN c.ticker = 'AMZN' THEN 75000000000.0000
        WHEN c.ticker = 'GOOGL' THEN 55722000000.0000
        WHEN c.ticker = 'META' THEN 31915000000.0000
    END as gross_profit,
    CASE 
        WHEN c.ticker = 'AAPL' THEN 40311000000.0000
        WHEN c.ticker = 'MSFT' THEN 27569000000.0000
        WHEN c.ticker = 'AMZN' THEN 13298000000.0000
        WHEN c.ticker = 'GOOGL' THEN 23688000000.0000
        WHEN c.ticker = 'META' THEN 15353000000.0000
    END as operating_income,
    CASE
        WHEN c.ticker = 'AAPL' THEN 33916000000.0000
        WHEN c.ticker = 'MSFT' THEN 22291000000.0000
        WHEN c.ticker = 'AMZN' THEN 10600000000.0000
        WHEN c.ticker = 'GOOGL' THEN 20688000000.0000  
        WHEN c.ticker = 'META' THEN 14017000000.0000
    END as net_income,
    CASE
        WHEN c.ticker = 'AAPL' THEN 43158000000.0000
        WHEN c.ticker = 'MSFT' THEN 30567000000.0000
        WHEN c.ticker = 'AMZN' THEN 25000000000.0000
        WHEN c.ticker = 'GOOGL' THEN 26234000000.0000
        WHEN c.ticker = 'META' THEN 18451000000.0000
    END as ebitda,
    CASE
        WHEN c.ticker = 'AAPL' THEN 365725000000.0000
        WHEN c.ticker = 'MSFT' THEN 411976000000.0000
        WHEN c.ticker = 'AMZN' THEN 527854000000.0000
        WHEN c.ticker = 'GOOGL' THEN 398314000000.0000
        WHEN c.ticker = 'META' THEN 185727000000.0000
    END as total_assets,
    CASE
        WHEN c.ticker = 'AAPL' THEN 290437000000.0000
        WHEN c.ticker = 'MSFT' THEN 205753000000.0000
        WHEN c.ticker = 'AMZN' THEN 302020000000.0000
        WHEN c.ticker = 'GOOGL' THEN 75053000000.0000
        WHEN c.ticker = 'META' THEN 47040000000.0000
    END as total_liabilities,
    CASE
        WHEN c.ticker = 'AAPL' THEN 75288000000.0000
        WHEN c.ticker = 'MSFT' THEN 206223000000.0000
        WHEN c.ticker = 'AMZN' THEN 225834000000.0000
        WHEN c.ticker = 'GOOGL' THEN 323261000000.0000
        WHEN c.ticker = 'META' THEN 138687000000.0000
    END as shareholders_equity,
    CASE
        WHEN c.ticker = 'AAPL' THEN 29943000000.0000
        WHEN c.ticker = 'MSFT' THEN 34704000000.0000
        WHEN c.ticker = 'AMZN' THEN 73387000000.0000
        WHEN c.ticker = 'GOOGL' THEN 111909000000.0000
        WHEN c.ticker = 'META' THEN 65878000000.0000
    END as cash_and_equivalents,
    CASE
        WHEN c.ticker = 'AAPL' THEN 123930000000.0000
        WHEN c.ticker = 'MSFT' THEN 47030000000.0000
        WHEN c.ticker = 'AMZN' THEN 135755000000.0000
        WHEN c.ticker = 'GOOGL' THEN 13253000000.0000
        WHEN c.ticker = 'META' THEN 37230000000.0000
    END as total_debt,
    CASE
        WHEN c.ticker = 'AAPL' THEN 27556000000.0000
        WHEN c.ticker = 'MSFT' THEN 28206000000.0000
        WHEN c.ticker = 'AMZN' THEN 36757000000.0000
        WHEN c.ticker = 'GOOGL' THEN 23683000000.0000
        WHEN c.ticker = 'META' THEN 28090000000.0000
    END as operating_cash_flow,
    CASE
        WHEN c.ticker = 'AAPL' THEN 20563000000.0000
        WHEN c.ticker = 'MSFT' THEN 21563000000.0000
        WHEN c.ticker = 'AMZN' THEN 16936000000.0000
        WHEN c.ticker = 'GOOGL' THEN 17076000000.0000
        WHEN c.ticker = 'META' THEN 19617000000.0000
    END as free_cash_flow
FROM core.dim_company c
WHERE c.ticker IN ('AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META')
ON CONFLICT (company_id, period_end_date) DO UPDATE SET
    revenue = EXCLUDED.revenue,
    gross_profit = EXCLUDED.gross_profit,
    operating_income = EXCLUDED.operating_income,
    net_income = EXCLUDED.net_income,
    ebitda = EXCLUDED.ebitda,
    total_assets = EXCLUDED.total_assets,
    total_liabilities = EXCLUDED.total_liabilities,
    shareholders_equity = EXCLUDED.shareholders_equity,
    cash_and_equivalents = EXCLUDED.cash_and_equivalents,
    total_debt = EXCLUDED.total_debt,
    operating_cash_flow = EXCLUDED.operating_cash_flow,
    free_cash_flow = EXCLUDED.free_cash_flow;

-- =============================================================================
-- 4. CALCULAR TTM (ESTRUTURA CORRIGIDA)
-- =============================================================================

-- Para exemplo, usar dados Q4 2023 como TTM
INSERT INTO marts.fact_financials_ttm (
    company_id,
    as_of_date,
    revenue_ttm,
    net_income_ttm,
    operating_income_ttm,
    ebitda_ttm,
    free_cash_flow_ttm,
    gross_margin,
    operating_margin,
    net_margin,
    roe,
    roa,
    debt_to_equity,
    current_ratio,
    revenue_growth_yoy,
    net_income_growth_yoy
)
SELECT 
    fq.company_id,
    fq.period_end_date as as_of_date,
    fq.revenue as revenue_ttm,
    fq.net_income as net_income_ttm,
    fq.operating_income as operating_income_ttm,
    fq.ebitda as ebitda_ttm,
    fq.free_cash_flow as free_cash_flow_ttm,
    
    -- Ratios calculados
    CASE WHEN fq.revenue > 0 THEN fq.gross_profit / fq.revenue ELSE NULL END as gross_margin,
    CASE WHEN fq.revenue > 0 THEN fq.operating_income / fq.revenue ELSE NULL END as operating_margin,
    CASE WHEN fq.revenue > 0 THEN fq.net_income / fq.revenue ELSE NULL END as net_margin,
    CASE WHEN fq.shareholders_equity > 0 THEN fq.net_income / fq.shareholders_equity ELSE NULL END as roe,
    CASE WHEN fq.total_assets > 0 THEN fq.net_income / fq.total_assets ELSE NULL END as roa,
    CASE WHEN fq.shareholders_equity > 0 THEN fq.total_debt / fq.shareholders_equity ELSE NULL END as debt_to_equity,
    
    -- Current ratio estimado (simplificado)
    CASE WHEN fq.total_liabilities > 0 THEN (fq.cash_and_equivalents * 1.5) / (fq.total_liabilities * 0.3) ELSE NULL END as current_ratio,
    
    -- Growth YoY (assumindo valores para exemplo)
    0.10 as revenue_growth_yoy,
    0.15 as net_income_growth_yoy
    
FROM marts.fact_financials_quarterly fq
WHERE fq.period_end_date = '2023-12-31'
ON CONFLICT (company_id, as_of_date) DO UPDATE SET
    revenue_ttm = EXCLUDED.revenue_ttm,
    net_income_ttm = EXCLUDED.net_income_ttm,
    operating_income_ttm = EXCLUDED.operating_income_ttm,
    ebitda_ttm = EXCLUDED.ebitda_ttm,
    free_cash_flow_ttm = EXCLUDED.free_cash_flow_ttm,
    gross_margin = EXCLUDED.gross_margin,
    operating_margin = EXCLUDED.operating_margin,
    net_margin = EXCLUDED.net_margin,
    roe = EXCLUDED.roe,
    roa = EXCLUDED.roa,
    debt_to_equity = EXCLUDED.debt_to_equity,
    current_ratio = EXCLUDED.current_ratio,
    revenue_growth_yoy = EXCLUDED.revenue_growth_yoy,
    net_income_growth_yoy = EXCLUDED.net_income_growth_yoy;

-- =============================================================================
-- 5. VERIFICACAO FINAL (QUERIES CORRIGIDAS)
-- =============================================================================

-- Verificar tabelas criadas
SELECT schemaname, count(*) as tables
FROM pg_tables 
WHERE schemaname IN ('raw', 'staging', 'core', 'marts')
GROUP BY schemaname
ORDER BY schemaname;

-- Verificar dados inseridos
SELECT 
    'dim_company' as table_name, 
    count(*) as records 
FROM core.dim_company

UNION ALL

SELECT 
    'dim_currency' as table_name, 
    count(*) as records 
FROM core.dim_currency  

UNION ALL

SELECT 
    'fact_financials_quarterly' as table_name, 
    count(*) as records 
FROM marts.fact_financials_quarterly

UNION ALL

SELECT 
    'fact_financials_ttm' as table_name, 
    count(*) as records 
FROM marts.fact_financials_ttm;

-- Verificar dados financeiros (QUERY CORRIGIDA)
SELECT 
    c.ticker,
    c.company_name,
    ROUND(f.revenue / 1000000000.0, 2) as revenue_billions,
    ROUND(f.net_income / 1000000000.0, 2) as net_income_billions,
    ROUND(ttm.gross_margin * 100, 2) as gross_margin_pct,
    ROUND(ttm.roe * 100, 2) as roe_pct
FROM marts.fact_financials_quarterly f
JOIN core.dim_company c ON f.company_id = c.company_id
JOIN marts.fact_financials_ttm ttm ON f.company_id = ttm.company_id AND f.period_end_date = ttm.as_of_date
ORDER BY f.revenue DESC;

-- Success message
SELECT 'DATABASE SETUP COMPLETO! Dados inseridos com sucesso - VERSAO CORRIGIDA.' as status;