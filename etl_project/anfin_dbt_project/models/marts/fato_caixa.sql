-- anfin_dbt_project/models/marts/fato_caixa.sql

with 

source_data as (
    select * from {{ source('anfin_staging', 'stg_conciliacao_bancaria') }}
),

dim_tempo as (
    select sk_tempo, data from {{ ref('dim_tempo') }}
),

dim_contas as (
    select sk_conta, id_conta_origem from {{ ref('dim_contas') }}
),

dim_centros_custo as (
    select sk_centro_custo, id_cc_origem from {{ ref('dim_centros_custo') }}
)

select
    t.sk_tempo,
    dc.sk_conta,
    dcc.sk_centro_custo,

    case
        when s.tipo = 'ENTRADA' then s.valor
        else 0
    end as valor_entrada,

    -- Padroniza o valor de saída para ser sempre positivo
    case
        when s.tipo = 'SAIDA' then abs(s.valor)
        else 0
    end as valor_saida,
    
    -- Calcula saldo (entrada - saída)
    case
        when s.tipo = 'ENTRADA' then s.valor
        when s.tipo = 'SAIDA' then -abs(s.valor)
        else 0
    end as saldo,

    s.historico as descricao,
    'Conciliação Bancária' as origem_dados

from source_data s
left join dim_tempo t on s.data = t.data
-- Mapear para uma conta padrão de caixa/bancos se não tiver conta específica
left join dim_contas dc on dc.id_conta_origem = coalesce(s.conta, '4.1.1.01') 
-- Mapear para centro de custo padrão se não especificado
left join dim_centros_custo dcc on dcc.id_cc_origem = coalesce(s.centro_custo, 'CC-ADM-01')