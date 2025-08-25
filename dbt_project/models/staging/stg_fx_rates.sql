-- stg_fx_rates.sql
-- Staging model: Normalização de taxas de câmbio ECB/FRED
-- Fonte: raw.fx_rates_raw

{{ config(
    materialized='table',
    indexes=[
        {'columns': ['rate_date', 'currency_from', 'currency_to']},
        {'columns': ['source']}
    ]
) }}

with source_fx as (
    select * from {{ source('raw', 'fx_rates_raw') }}
),

-- Parse ECB XML data (EUR base)
ecb_rates as (
    select
        extract_date as rate_date,
        'EUR' as currency_from,
        jsonb_object_keys(raw_data->'rates') as currency_to,
        (raw_data->'rates'->>jsonb_object_keys(raw_data->'rates'))::decimal(10,6) as rate,
        'ECB' as source,
        load_ts
    from source_fx
    where source = 'ECB'
    and raw_data->'rates' is not null
),

-- Parse FRED JSON data (USD base) 
fred_rates as (
    select
        (observation->>'date')::date as rate_date,
        'USD' as currency_from,
        case 
            when raw_data->>'series_id' like 'DEXUS%' 
            then right(raw_data->>'series_id', 2)
            else 'EUR'  -- Default para DEXUSEU
        end as currency_to,
        (observation->>'value')::decimal(10,6) as rate,
        'FRED' as source,
        load_ts
    from source_fx,
    lateral jsonb_array_elements(raw_data->'observations') as observation
    where source = 'FRED'
    and raw_data->'observations' is not null
    and observation->>'value' != '.'  -- FRED usa '.' para missing values
),

-- Combinar ambas as fontes
all_rates as (
    select * from ecb_rates
    union all
    select * from fred_rates
),

-- Adicionar taxas inversas para flexibilidade
rates_with_inverse as (
    select 
        rate_date,
        currency_from,
        currency_to,
        rate,
        source,
        load_ts
    from all_rates
    
    union all
    
    -- Adicionar taxas inversas
    select
        rate_date,
        currency_to as currency_from,
        currency_from as currency_to,
        1.0 / nullif(rate, 0) as rate,
        source,
        load_ts
    from all_rates
    where rate > 0
),

-- Adicionar USD/USD = 1.0 como referência
rates_with_base as (
    select * from rates_with_inverse
    
    union all
    
    select distinct
        rate_date,
        'USD' as currency_from,
        'USD' as currency_to,
        1.0 as rate,
        'SYSTEM' as source,
        current_timestamp as load_ts
    from rates_with_inverse
),

-- Filtrar duplicatas e dados de qualidade
final as (
    select
        {{ dbt_utils.generate_surrogate_key(['rate_date', 'currency_from', 'currency_to', 'source']) }} as fx_id,
        rate_date,
        currency_from,
        currency_to,
        rate,
        source,
        load_ts
    
    from rates_with_base
    
    where rate_date >= '{{ var("start_date") }}'
    and rate > 0
    and rate < 1000  -- Filtro de sanidade
    
    qualify row_number() over (
        partition by rate_date, currency_from, currency_to 
        order by 
            case when source = 'ECB' then 1 
                 when source = 'FRED' then 2 
                 else 3 end,
            load_ts desc
    ) = 1
)

select * from final