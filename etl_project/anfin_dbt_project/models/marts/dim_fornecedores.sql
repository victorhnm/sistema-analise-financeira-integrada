-- anfin_dbt_project/models/marts/dim_fornecedores.sql

with source_data as (
    -- Dados fictícios de fornecedores para demonstração
    -- Em produção, estes dados viriam de um sistema de cadastro
    select 'FORN-ACME-01' as id_fornecedor_origem, 'Fornecedor ACME Corp' as nome_fornecedor, 'Serviços' as tipo, 'TI e Software' as categoria
    union all
    select 'FORN-XYZ-02' as id_fornecedor_origem, 'Papelaria XYZ' as nome_fornecedor, 'Material' as tipo, 'Escritório' as categoria
    union all
    select 'FORN-ABC-03' as id_fornecedor_origem, 'ABC Consultoria' as nome_fornecedor, 'Serviços' as tipo, 'Consultoria' as categoria
    union all
    select 'FORN-DEF-04' as id_fornecedor_origem, 'DEF Materiais' as nome_fornecedor, 'Material' as tipo, 'Construção' as categoria
    union all
    select 'FORN-GHI-05' as id_fornecedor_origem, 'GHI Equipamentos' as nome_fornecedor, 'Equipamentos' as tipo, 'Tecnologia' as categoria
)

select
    -- Cria chave surrogate única para cada fornecedor
    {{ dbt_utils.generate_surrogate_key(['id_fornecedor_origem']) }} as sk_fornecedor,
    
    id_fornecedor_origem,
    nome_fornecedor,
    
    -- Padroniza o tipo de fornecedor
    tipo as tipo_fornecedor,
    
    -- Adiciona categorização para análises
    categoria as categoria_fornecedor

from source_data