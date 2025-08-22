-- anfin_dbt_project/models/marts/fato_caixa.sql

with 

source_data as (
    select * from {{ source('anfin_staging', 'stg_conciliacao_bancaria') }}
),

dim_tempo as (
    select sk_tempo, data from {{ ref('dim_tempo') }}
)

select
    t.sk_tempo,

    case
        when s.tipo = 'ENTRADA' then s.valor
        else 0
    end as valor_entrada,

    -- Padroniza o valor de saída para ser sempre positivo
    case
        when s.tipo = 'SAIDA' then s.valor * -1
        else 0
    end as valor_saida,

    s.historico as origem_dados

from source_data s
left join dim_tempo t on s.data = t.data