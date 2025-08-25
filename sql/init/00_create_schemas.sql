-- Integrated Financial Analysis - Database Schema
-- Arquivo: infra/init.sql

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

-- Inserir empresas seed
INSERT INTO staging.stg_companies (cik, ticker, company_name, sector) VALUES
    ('0000320193', 'AAPL', 'Apple Inc.', 'Technology'),
    ('0000789019', 'MSFT', 'Microsoft Corporation', 'Technology'), 
    ('0001018724', 'AMZN', 'Amazon.com Inc.', 'Consumer Discretionary')
ON CONFLICT (cik) DO NOTHING;

-- Propagar para core
INSERT INTO core.dim_company (company_id, cik, ticker, company_name, sector, country)
SELECT company_id, cik, ticker, company_name, sector, country
FROM staging.stg_companies
ON CONFLICT (cik) DO UPDATE SET
    ticker = EXCLUDED.ticker,
    company_name = EXCLUDED.company_name,
    sector = EXCLUDED.sector;

-- Verificar criação
SELECT schemaname, count(*) as tables
FROM pg_tables 
WHERE schemaname IN ('raw', 'staging', 'core', 'marts')
GROUP BY schemaname;
