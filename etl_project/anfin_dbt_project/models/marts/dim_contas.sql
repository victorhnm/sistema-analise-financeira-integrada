-- anfin_dbt_project/models/marts/dim_contas.sql

with 
    
source_data as (
    -- Unifica as contas contábeis de todas as fontes de dados
    select distinct 
        conta as id_conta_origem 
    from {{ source('anfin_staging', 'stg_erp_lancamentos') }} 
    where conta is not null
    
    union
    
    select distinct 
        conta_contabil as id_conta_origem 
    from {{ source('anfin_staging', 'stg_planilha_mensal') }} 
    where conta_contabil is not null
)

select
    -- Cria uma chave primária única (surrogate key) para cada id_conta_origem
    {{ dbt_utils.generate_surrogate_key(['id_conta_origem']) }} as sk_conta,
    
    id_conta_origem,
    
    -- Aplica regras de negócio para enriquecer os dados
    case
        when id_conta_origem = '4.1.1.01' then 'Receita de Vendas'
        when id_conta_origem = '5.1.1.01' then 'Salários e Encargos'
        when id_conta_origem = '5.1.1.02' then 'Marketing e Publicidade'
        when id_conta_origem = '5.2.1.01' then 'Aluguel e Condomínio'
        when id_conta_origem = '5.3.1.04' then 'Software e Licenças'
        when id_conta_origem = '5.3.1.09' then 'Serviços de Terceiros'
        else 'Conta Desconhecida'
    end as nome_conta,

    case
        when left(id_conta_origem, 1) = '4' then 'Receita'
        when left(id_conta_origem, 1) = '5' then 'Despesa'
        else 'Outro'
    end as tipo_conta,

    case
        when left(id_conta_origem, 3) = '4.1' then 'Receitas Operacionais'
        when left(id_conta_origem, 3) = '5.1' then 'Despesas com Pessoal'
        when left(id_conta_origem, 3) = '5.2' then 'Despesas Administrativas'
        when left(id_conta_origem, 3) = '5.3' then 'Despesas com Serviços'
        else 'Outros'
    end as grupo_conta

from source_data