#!/usr/bin/env python3
"""
Script para reorganizar completamente o projeto
Remove duplicatas, organiza estrutura, prepara para GitHub
"""

import os
import shutil
import glob

def criar_estrutura_final():
    """Criar estrutura de diretórios limpa e organizada"""
    
    estrutura = {
        'scripts/': 'Scripts de setup e utilitários',
        'scripts/setup/': 'Scripts de inicialização',
        'scripts/migration/': 'Scripts de migração (deprecated)',
        'sql/': 'Scripts SQL para database',
        'sql/init/': 'Scripts de inicialização do banco',
        'sql/migrations/': 'Migrações de schema',
        'sql/seed/': 'Dados iniciais',
        'tests/': 'Testes automatizados',
        'temp/': 'Arquivos temporários (será ignorado pelo Git)',
        '.github/': 'Configurações do GitHub',
        '.github/workflows/': 'GitHub Actions'
    }
    
    print("=== CRIANDO ESTRUTURA LIMPA ===")
    for pasta, desc in estrutura.items():
        os.makedirs(pasta, exist_ok=True)
        print(f"✓ {pasta} - {desc}")

def identificar_arquivos_para_remover():
    """Identificar arquivos duplicados e desnecessários"""
    
    # Arquivos para remover (duplicatas e temporários)
    arquivos_remover = [
        # Migrações duplicadas
        'migrar_*.py',
        'completar_migracao.py',
        'migrar_todos_dados_supabase.py',
        
        # Scripts de teste duplicados  
        'check_*.py',
        'test_*.py',
        'verificar_*.py',
        'localizar_*.py',
        'mostrar_*.py',
        'analyze_*.py',
        
        # Setup duplicados
        'setup_*.py',
        'configurar_*.py',
        'create_*.py',
        'run_*.py',
        
        # Arquivos temporários
        'get-pip.py',
        'nul',
        '*.png',
        'venv/',
        
        # SQL duplicados
        'populate_supabase.sql',  # Manter apenas o _fixed
        'verificar_*.sql',
        
        # Outros
        'add_more_companies.py',
        'fix_table_constraints.py',
        'guia_schemas.py',
        'execute_sql.py',
        
        # Diretórios mal formados
        'dbt_projectmacros/',
        'dbt_projectmodelsmarts/',  
        'dbt_projectmodelsstaging/',
        'etlcommon/',
        'etljobs/',
        'etlparsers/',
        'etlsources/'
    ]
    
    return arquivos_remover

def mover_arquivos_importantes():
    """Mover arquivos importantes para locais corretos"""
    
    movimentos = {
        # SQL Scripts
        'populate_supabase_fixed.sql': 'sql/init/01_create_tables_and_seed.sql',
        'infra/init.sql': 'sql/init/00_create_schemas.sql',
        
        # Scripts de setup
        'setup_supabase_manual.md': 'scripts/setup/README_SETUP.md',
        'test_supabase_simple.py': 'scripts/setup/test_connection.py',
        'create_tables_supabase.py': 'scripts/setup/setup_database.py',
        
        # Documentação
        'ORGANIZACAO_PROJETO.md': 'docs/PROJECT_ORGANIZATION.md',
        'INSTRUCOES_POPULACAO.md': 'docs/DATABASE_SETUP.md',
        'prompt.txt': 'docs/PROJECT_REQUIREMENTS.md',
        
        # Arquivos de configuração para raiz
        'infra/seed_companies.csv': 'sql/seed/companies.csv'
    }
    
    print("=== MOVENDO ARQUIVOS IMPORTANTES ===")
    for origem, destino in movimentos.items():
        if os.path.exists(origem):
            # Criar diretório de destino se não existir
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            shutil.move(origem, destino)
            print(f"✓ {origem} → {destino}")

def limpar_arquivos_desnecessarios():
    """Remover arquivos duplicados e temporários"""
    
    arquivos_remover = identificar_arquivos_para_remover()
    
    print("=== REMOVENDO ARQUIVOS DESNECESSARIOS ===")
    
    for pattern in arquivos_remover:
        # Usar glob para patterns com wildcards
        if '*' in pattern:
            matches = glob.glob(pattern)
            for arquivo in matches:
                if os.path.isfile(arquivo):
                    os.remove(arquivo)
                    print(f"✗ Removido: {arquivo}")
                elif os.path.isdir(arquivo):
                    shutil.rmtree(arquivo)
                    print(f"✗ Removido diretório: {arquivo}")
        else:
            # Arquivo específico
            if os.path.exists(pattern):
                if os.path.isfile(pattern):
                    os.remove(pattern)
                    print(f"✗ Removido: {pattern}")
                elif os.path.isdir(pattern):
                    shutil.rmtree(pattern)
                    print(f"✗ Removido diretório: {pattern}")

def atualizar_documentacao():
    """Consolidar documentação dispersa"""
    
    # Mover docs importantes
    docs_moves = {
        'PROJETO_CONCLUIDO.md': 'docs/PROJECT_STATUS.md'
    }
    
    print("=== ORGANIZANDO DOCUMENTACAO ===")
    for origem, destino in docs_moves.items():
        if os.path.exists(origem):
            shutil.move(origem, destino)
            print(f"✓ Doc movido: {origem} → {destino}")

def criar_arquivo_estrutura():
    """Criar arquivo explicando a nova estrutura"""
    
    estrutura_md = """# Estrutura do Projeto

## Diretórios Principais

```
integrated-financial-analysis/
├── api/                    # FastAPI REST API
├── bi/                     # Power BI assets
│   └── pbip/              # Power BI Project files (.pbip)
├── dbt_project/           # dbt transformações
├── etl/                   # Pipeline de extração de dados
├── docs/                  # Documentação técnica  
├── scripts/               # Scripts de utilidade
│   ├── setup/            # Scripts de inicialização
│   └── migration/        # Scripts de migração (deprecated)
├── sql/                   # Scripts SQL
│   ├── init/             # Inicialização do banco
│   ├── migrations/       # Migrações de schema
│   └── seed/             # Dados iniciais
├── tests/                 # Testes automatizados
└── .github/              # Configurações GitHub Actions
```

## Arquivos de Configuração

- `.env.example` - Template de variáveis de ambiente
- `.env` - Variáveis locais (não commitado)
- `.gitignore` - Arquivos ignorados pelo Git
- `requirements.txt` - Dependências Python globais
- `LICENSE` - Licença MIT
- `README.md` - Documentação principal

## Scripts de Setup

- `scripts/setup/setup_database.py` - Inicializar Supabase
- `scripts/setup/test_connection.py` - Testar conectividade
- `sql/init/00_create_schemas.sql` - Criar schemas
- `sql/init/01_create_tables_and_seed.sql` - Criar tabelas e dados

## Como Usar

1. Configure `.env` baseado no `.env.example`
2. Execute setup: `python scripts/setup/setup_database.py`
3. Teste conexão: `python scripts/setup/test_connection.py`  
4. Inicie API: `python api/main.py`
5. Abra Power BI: `bi/pbip/definition.pbir`

## Documentação

Veja `/docs/` para documentação técnica detalhada.
"""
    
    with open('PROJECT_STRUCTURE.md', 'w') as f:
        f.write(estrutura_md)
    
    print("✓ Criado PROJECT_STRUCTURE.md")

def main():
    print("=== REORGANIZACAO COMPLETA DO PROJETO ===")
    print("Executando limpeza e reorganizacao...")
    
    # 1. Criar nova estrutura
    criar_estrutura_final()
    
    # 2. Mover arquivos importantes  
    mover_arquivos_importantes()
    
    # 3. Atualizar documentação
    atualizar_documentacao()
    
    # 4. Limpar arquivos desnecessários
    limpar_arquivos_desnecessarios()
    
    # 5. Criar documentação da estrutura
    criar_arquivo_estrutura()
    
    print("\\n=== REORGANIZACAO COMPLETA ===")
    print("✓ Estrutura limpa e organizada")
    print("✓ Arquivos duplicados removidos") 
    print("✓ Documentação consolidada")
    print("\\nPróximo passo: Executar script de configuração Git")

if __name__ == "__main__":
    main()