-- Modelo staging para fatos financeiros extraídos da SEC
{{ config(materialized='view') }}

WITH raw_facts AS (
    SELECT
        cik,
        company_name,
        ticker,
        raw_data,
        ingested_at,
        file_date
    FROM {{ source('raw', 'sec_company_facts') }}
),

parsed_facts AS (
    SELECT
        cik,
        company_name,
        UPPER(COALESCE(ticker, '')) AS ticker,
        raw_data ->> 'entityName' AS entity_name,
        raw_data ->> 'tradingSymbol' AS trading_symbol,
        raw_data -> 'facts' -> 'us-gaap' AS us_gaap_facts,
        COALESCE(
            (raw_data -> 'facts' -> 'us-gaap') IS NOT NULL AND 
            (raw_data -> 'facts' -> 'us-gaap') != 'null'::jsonb, 
            FALSE
        ) AS has_us_gaap_data,
        ingested_at,
        file_date
    FROM raw_facts
)

SELECT
    cik,
    COALESCE(entity_name, company_name) AS company_name,
    COALESCE(NULLIF(UPPER(trading_symbol), ''), UPPER(ticker)) AS ticker,
    has_us_gaap_data,
    CASE 
        WHEN has_us_gaap_data THEN jsonb_object_keys(us_gaap_facts)
        ELSE NULL
    END AS available_concepts,
    ingested_at,
    file_date,
    -- Metadados de qualidade
    CASE 
        WHEN has_us_gaap_data THEN 'complete'
        ELSE 'limited'
    END AS data_quality
FROM parsed_facts
WHERE company_name IS NOT NULL