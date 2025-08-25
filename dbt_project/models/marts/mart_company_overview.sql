-- Visão consolidada de empresas para análise
{{ config(materialized='table') }}

WITH company_base AS (
    SELECT
        company_id,
        cik,
        ticker,
        company_name,
        sector,
        country,
        is_active,
        created_at
    FROM {{ source('core', 'dim_company') }}
    WHERE is_active = TRUE
),

company_data_status AS (
    SELECT
        c.cik,
        c.ticker,
        COUNT(*) AS data_files_count,
        MAX(sf.ingested_at) AS last_data_update,
        BOOL_OR(sf.has_us_gaap_data) AS has_financial_data,
        STRING_AGG(DISTINCT sf.data_quality, ', ') AS data_quality_summary
    FROM company_base c
    LEFT JOIN {{ ref('stg_company_facts') }} sf ON c.cik = sf.cik
    GROUP BY c.cik, c.ticker
)

SELECT
    c.company_id,
    c.cik,
    c.ticker,
    c.company_name,
    c.sector,
    c.country,
    c.is_active,
    c.created_at,
    
    -- Status dos dados
    COALESCE(ds.data_files_count, 0) AS data_files_available,
    ds.last_data_update,
    COALESCE(ds.has_financial_data, FALSE) AS has_financial_data,
    COALESCE(ds.data_quality_summary, 'no_data') AS data_quality,
    
    -- Classificação para BI
    CASE
        WHEN COALESCE(ds.has_financial_data, FALSE) THEN 'Ready for Analysis'
        WHEN COALESCE(ds.data_files_count, 0) > 0 THEN 'Data Available'
        ELSE 'No Data'
    END AS analysis_readiness,
    
    -- Timestamp da última atualização desta tabela
    CURRENT_TIMESTAMP AS mart_updated_at

FROM company_base c
LEFT JOIN company_data_status ds ON c.cik = ds.cik
ORDER BY 
    ds.has_financial_data DESC,
    c.company_name