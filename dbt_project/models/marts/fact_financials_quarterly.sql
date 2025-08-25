-- fact_financials_quarterly.sql
-- Marts model: Fatos financeiros agregados por empresa-período
-- Grão: Uma linha por empresa por trimestre fiscal

{{ config(
    materialized='incremental',
    unique_key=['company_id', 'period_end_date'],
    on_schema_change='append_new_columns',
    indexes=[
        {'columns': ['company_id', 'period_end_date'], 'unique': True},
        {'columns': ['fiscal_year', 'fiscal_quarter']},
        {'columns': ['ticker', 'period_end_date']}
    ]
) }}

with financial_facts as (
    select * from {{ ref('int_financial_facts_with_fx') }}
    
    {% if is_incremental() %}
    -- Somente novos dados em execução incremental
    where load_ts >= (select max(load_ts) from {{ this }})
    {% endif %}
),

-- Pivotar métricas principais por período
quarterly_metrics as (
    select
        company_id,
        company_name,
        ticker,
        sector,
        period_end,
        fiscal_year,
        fiscal_period,
        form,
        
        -- Demonstração de Resultados (Income Statement)
        sum(case when canonical_metric = 'revenue' then value_usd end) as revenue,
        sum(case when canonical_metric = 'gross_profit' then value_usd end) as gross_profit,
        sum(case when canonical_metric = 'operating_income' then value_usd end) as operating_income,
        sum(case when canonical_metric = 'pretax_income' then value_usd end) as pretax_income,
        sum(case when canonical_metric = 'net_income' then value_usd end) as net_income,
        
        -- Balanço Patrimonial (Balance Sheet) - valores de fim de período
        max(case when canonical_metric = 'total_assets' then value_usd end) as total_assets,
        max(case when canonical_metric = 'current_assets' then value_usd end) as current_assets,
        max(case when canonical_metric = 'cash_and_equivalents' then value_usd end) as cash_and_equivalents,
        max(case when canonical_metric = 'accounts_receivable' then value_usd end) as accounts_receivable,
        max(case when canonical_metric = 'inventory' then value_usd end) as inventory,
        max(case when canonical_metric = 'ppe_net' then value_usd end) as ppe_net,
        max(case when canonical_metric = 'goodwill' then value_usd end) as goodwill,
        max(case when canonical_metric = 'total_liabilities' then value_usd end) as total_liabilities,
        max(case when canonical_metric = 'current_liabilities' then value_usd end) as current_liabilities,
        max(case when canonical_metric = 'accounts_payable' then value_usd end) as accounts_payable,
        max(case when canonical_metric = 'long_term_debt' then value_usd end) as long_term_debt,
        max(case when canonical_metric = 'shareholders_equity' then value_usd end) as shareholders_equity,
        max(case when canonical_metric = 'retained_earnings' then value_usd end) as retained_earnings,
        
        -- Fluxo de Caixa (Cash Flow)
        sum(case when canonical_metric = 'operating_cash_flow' then value_usd end) as operating_cash_flow,
        sum(case when canonical_metric = 'investing_cash_flow' then value_usd end) as investing_cash_flow,
        sum(case when canonical_metric = 'financing_cash_flow' then value_usd end) as financing_cash_flow,
        sum(case when canonical_metric = 'capex' then value_usd end) as capex,
        
        -- Per Share Metrics
        max(case when canonical_metric = 'eps_basic' then value_usd end) as eps_basic,
        max(case when canonical_metric = 'eps_diluted' then value_usd end) as eps_diluted,
        max(case when canonical_metric = 'shares_basic' then value_usd end) as shares_basic,
        max(case when canonical_metric = 'shares_diluted' then value_usd end) as shares_diluted,
        
        max(load_ts) as load_ts
        
    from financial_facts
    group by 1,2,3,4,5,6,7,8
),

-- Adicionar métricas derivadas e limpezas
final as (
    select
        {{ dbt_utils.generate_surrogate_key(['company_id', 'period_end']) }} as financial_id,
        company_id,
        company_name,
        ticker,
        sector,
        period_end as period_end_date,
        fiscal_year,
        case 
            when fiscal_period = 'Q1' then 1
            when fiscal_period = 'Q2' then 2
            when fiscal_period = 'Q3' then 3
            when fiscal_period = 'Q4' then 4
            else null
        end as fiscal_quarter,
        
        -- Income Statement
        revenue,
        gross_profit,
        operating_income,
        pretax_income,
        net_income,
        
        -- Calcular EBITDA aproximado (Operating Income + estimativa D&A)
        operating_income + coalesce(abs(capex) * 0.1, 0) as ebitda,
        
        -- Balance Sheet
        total_assets,
        current_assets,
        cash_and_equivalents,
        accounts_receivable,
        inventory,
        ppe_net,
        goodwill,
        total_liabilities,
        current_liabilities,
        accounts_payable,
        long_term_debt,
        shareholders_equity,
        retained_earnings,
        
        -- Calcular total debt como aproximação
        coalesce(long_term_debt, 0) + coalesce(current_liabilities * 0.3, 0) as total_debt,
        
        -- Cash Flow
        operating_cash_flow,
        investing_cash_flow,
        financing_cash_flow,
        capex,
        
        -- Free Cash Flow = Operating CF - CapEx
        operating_cash_flow - coalesce(abs(capex), 0) as free_cash_flow,
        
        -- Per Share
        eps_basic,
        eps_diluted,
        shares_basic,
        shares_diluted,
        
        'USD' as currency,
        current_timestamp as load_ts
        
    from quarterly_metrics
    
    where revenue is not null  -- Filtrar somente períodos com dados de receita
    or total_assets is not null
)

select * from final