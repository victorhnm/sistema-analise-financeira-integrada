-- stg_financial_facts.sql
-- Staging model: Normalização de fatos financeiros SEC XBRL
-- Fonte: raw.sec_company_facts

{{ config(
    materialized='table',
    indexes=[
        {'columns': ['cik', 'period_end', 'concept']},
        {'columns': ['fiscal_year', 'fiscal_period']},
        {'columns': ['canonical_metric']}
    ]
) }}

with source_facts as (
    select * from {{ source('raw', 'sec_company_facts') }}
),

taxonomy_map as (
    select * from {{ ref('taxonomy_map') }}
    where is_active = true
),

-- Expandir os fatos do JSON aninhado
facts_expanded as (
    select
        cik,
        jsonb_each(raw_data->'facts'->'us-gaap') as gaap_fact,
        load_ts
    from source_facts
    where raw_data->'facts'->'us-gaap' is not null
    
    union all
    
    select
        cik,
        jsonb_each(raw_data->'facts'->'ifrs-full') as gaap_fact,
        load_ts
    from source_facts
    where raw_data->'facts'->'ifrs-full' is not null
),

-- Normalizar cada fato individual
facts_normalized as (
    select
        cik,
        (gaap_fact).key as concept,
        case 
            when raw_data->'facts'->'us-gaap' is not null then 'US-GAAP'
            else 'IFRS'
        end as taxonomy,
        jsonb_array_elements((gaap_fact).value->'units') as unit_data,
        load_ts
    from source_facts,
    lateral jsonb_each(
        coalesce(raw_data->'facts'->'us-gaap', raw_data->'facts'->'ifrs-full')
    ) as gaap_fact
),

-- Extrair valores por período
facts_detailed as (
    select
        cik,
        concept,
        taxonomy,
        (unit_data).key as unit,
        jsonb_array_elements((unit_data).value) as period_value,
        load_ts
    from facts_normalized
),

-- Parse final dos valores e datas
facts_parsed as (
    select
        cik,
        concept,
        taxonomy,
        unit,
        (period_value->>'start')::date as period_start,
        (period_value->>'end')::date as period_end,
        extract(year from (period_value->>'end')::date) as fiscal_year,
        case 
            when extract(month from (period_value->>'end')::date) in (1,2,3) then 'Q1'
            when extract(month from (period_value->>'end')::date) in (4,5,6) then 'Q2'
            when extract(month from (period_value->>'end')::date) in (7,8,9) then 'Q3'
            else 'Q4'
        end as fiscal_period,
        coalesce(period_value->>'form', '10-K') as form,
        {{ safe_cast_decimal('period_value->>\'val\'', 20, 2) }} as value,
        load_ts
    from facts_detailed
    where period_value->>'val' is not null
    and (period_value->>'end')::date >= '{{ var("start_date") }}'
),

-- Adicionar mapeamento canônico
final as (
    select
        {{ dbt_utils.generate_surrogate_key(['f.cik', 'f.concept', 'f.period_end', 'f.form', 'f.unit']) }} as fact_id,
        f.cik,
        f.concept,
        f.taxonomy,
        f.unit,
        f.period_start,
        f.period_end,
        f.fiscal_year,
        f.fiscal_period,
        f.form,
        f.value,
        tm.canonical_metric,
        tm.statement_type,
        tm.metric_category,
        -- Detectar restatements (simplificado)
        case when f.load_ts > f.period_end + interval '6 months' 
             then true else false 
        end as is_restated,
        f.load_ts
        
    from facts_parsed f
    left join taxonomy_map tm
        on f.concept = tm.original_concept 
        and f.taxonomy = tm.original_taxonomy
    
    where f.value is not null
    and abs(f.value) < 1e15  -- Filtro de sanidade para valores
)

select * from final