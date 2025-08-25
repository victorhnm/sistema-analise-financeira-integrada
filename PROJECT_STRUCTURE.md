# Estrutura do Projeto

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
