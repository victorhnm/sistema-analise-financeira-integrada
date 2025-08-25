-- int_financial_facts_with_fx.sql
-- Intermediate model: Harmonização de fatos financeiros com conversão FX
-- Combina fatos financeiros com taxa de câmbio para normalização em USD

{{ config(
    materialized='table',
    indexes=[
        {'columns': ['company_id', 'period_end']},
        {'columns': ['canonical_metric', 'period_end']}
    ]
) }}

with companies as (
    select * from {{ ref('stg_companies') }}
),

financial_facts as (
    select * from {{ ref('stg_financial_facts') }}
    where canonical_metric is not null  -- Somente métricas mapeadas
),

fx_rates as (
    select * from {{ ref('stg_fx_rates') }}
),

-- Preparar fatos com informações da empresa
facts_with_company as (
    select
        f.*,
        c.company_id,
        c.company_name,
        c.ticker,
        c.currency as company_currency,
        c.sector
        
    from financial_facts f
    inner join companies c
        on f.cik = c.cik
),

-- Calcular taxa FX para conversão (company currency -> USD)
facts_with_fx as (
    select
        f.*,
        coalesce(fx.rate, 1.0) as fx_rate_to_usd,
        fx.rate_date as fx_rate_date
        
    from facts_with_company f
    left join fx_rates fx
        on f.company_currency = fx.currency_from
        and fx.currency_to = 'USD'
        and fx.rate_date = (
            -- Pegar a taxa mais próxima ao fim do período
            select max(fx2.rate_date)
            from fx_rates fx2
            where fx2.currency_from = f.company_currency
            and fx2.currency_to = 'USD'
            and fx2.rate_date <= f.period_end
            and fx2.rate_date >= f.period_end - interval '7 days'
        )
),

-- Aplicar conversões e limpezas finais
final as (
    select
        {{ dbt_utils.generate_surrogate_key(['company_id', 'concept', 'period_end', 'form']) }} as fact_id,
        company_id,
        company_name,
        ticker,
        sector,
        cik,
        concept,
        canonical_metric,
        statement_type,
        metric_category,
        taxonomy,
        unit,
        period_start,
        period_end,
        fiscal_year,
        fiscal_period,
        form,
        value as value_native,
        company_currency as currency_native,
        
        -- Converter para USD se necessário
        case 
            when company_currency = 'USD' then value
            when fx_rate_to_usd > 0 then value * fx_rate_to_usd
            else null  -- Não converter se não há taxa
        end as value_usd,
        
        fx_rate_to_usd,
        fx_rate_date,
        is_restated,
        
        -- Adicionar flags de qualidade
        case 
            when value is null then false
            when abs(value) > 1e12 then false  -- Valores muito grandes
            when company_currency != 'USD' and fx_rate_to_usd is null then false
            else true
        end as is_valid,
        
        load_ts
        
    from facts_with_fx
)

select * from final
where is_valid = true