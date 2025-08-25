-- stg_companies.sql
-- Staging model: Limpeza e normalização de dados das empresas
-- Fonte: raw.sec_submissions + seed data

{{ config(
    materialized='table',
    indexes=[
        {'columns': ['cik'], 'unique': True},
        {'columns': ['ticker']}
    ]
) }}

with source_submissions as (
    select * from {{ source('raw', 'sec_submissions') }}
),

source_companies_seed as (
    select * from {{ ref('seed_companies') }}
),

-- Extrair dados das submissions JSON
submissions_parsed as (
    select
        cik,
        raw_data->>'name' as company_name,
        raw_data->>'sic' as sic_code,
        raw_data->>'sicDescription' as sic_description,
        raw_data->>'tickers' as tickers_json,
        raw_data->>'exchanges' as exchanges_json,
        raw_data->'addresses'->0 as business_address,
        load_ts
    from source_submissions
),

-- Normalizar tickers (pegar o primeiro se múltiplo)
submissions_with_ticker as (
    select
        cik,
        company_name,
        sic_code,
        sic_description,
        case 
            when tickers_json is not null 
            then trim(both '"' from split_part(tickers_json, ',', 1))
            else null
        end as ticker,
        business_address,
        load_ts
    from submissions_parsed
),

-- Combinar com seed data (priorizar seed para dados conhecidos)
final as (
    select
        {{ dbt_utils.generate_surrogate_key(['s.cik']) }} as company_id,
        s.cik,
        coalesce(seed.ticker, s.ticker) as ticker,
        coalesce(seed.name, s.company_name) as company_name,
        coalesce(seed.sector, 
                case 
                    when s.sic_code between '1000' and '1999' then 'Energy'
                    when s.sic_code between '2000' and '2999' then 'Materials' 
                    when s.sic_code between '3000' and '3999' then 'Industrials'
                    when s.sic_code between '4000' and '4999' then 'Utilities'
                    when s.sic_code between '5000' and '5999' then 'Consumer Discretionary'
                    when s.sic_code between '6000' and '6999' then 'Financials'
                    when s.sic_code between '7000' and '7999' then 'Technology'
                    when s.sic_code between '8000' and '8999' then 'Healthcare'
                    else 'Other'
                end) as sector,
        coalesce(seed.country, 'US') as country,
        coalesce(seed.currency, 'USD') as currency,
        s.sic_code,
        s.sic_description,
        s.business_address,
        true as is_active,
        current_timestamp as created_ts,
        current_timestamp as updated_ts
    
    from submissions_with_ticker s
    full outer join source_companies_seed seed
        on s.cik = seed.cik
    
    where s.cik is not null or seed.cik is not null
)

select * from final