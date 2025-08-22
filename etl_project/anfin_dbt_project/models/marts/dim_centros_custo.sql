-- anfin_dbt_project/models/marts/dim_centros_custo.sql

with 
    
unioned_sources as (
    -- Unifica os centros de custo de todas as fontes de dados
    select distinct 
        centro_custo_id as id_cc_origem 
    from {{ source('anfin_staging', 'stg_erp_lancamentos') }}
    where centro_custo_id is not null
    
    union
    
    select distinct 
        centro_custo as id_cc_origem 
    from {{ source('anfin_staging', 'stg_planilha_mensal') }}
    where centro_custo is not null
)

select
    -- Cria uma chave primária única (surrogate key) para cada id_cc_origem
    {{ dbt_utils.generate_surrogate_key(['id_cc_origem']) }} as sk_centro_custo,

    id_cc_origem,
    
    -- Padroniza e enriquece os dados
    case 
        when id_cc_origem in ('CC_VENDAS', 'VENDAS') then 'Vendas'
        when id_cc_origem in ('CC_MARKETING', 'MARKETING') then 'Marketing'
        when id_cc_origem in ('CC_TI', 'TI') then 'Tecnologia da Informação'
        when id_cc_origem in ('CC_ADM', 'ADM') then 'Administrativo'
        when id_cc_origem in ('CC_RH', 'RH') then 'Recursos Humanos'
        else 'Indefinido'
    end as nome_centro_custo,

    case 
        when id_cc_origem in ('CC_VENDAS', 'VENDAS', 'CC_MARKETING', 'MARKETING') then 'Receita & Custo'
        else 'Despesa'
    end as departamento

from unioned_sources