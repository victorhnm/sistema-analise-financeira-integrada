# Integrated Financial Analysis

> **End-to-end financial data pipeline** with SEC EDGAR integration, automated ETL, and interactive Power BI dashboards.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Supabase](https://img.shields.io/badge/database-Supabase-green.svg)](https://supabase.com)
[![Power BI](https://img.shields.io/badge/visualization-Power%20BI-yellow.svg)](https://powerbi.microsoft.com)

**Integrated Financial Analysis** is a comprehensive data platform that extracts, transforms, and analyzes financial data from SEC EDGAR filings. Built with modern data stack: Python ETL, PostgreSQL/Supabase, dbt transformations, FastAPI, and Power BI dashboards.

## Overview

### Key Features

- **🏢 Multi-Company Analysis** - Automated data extraction for Fortune 500 companies
- **📊 Real-Time Dashboards** - Interactive Power BI reports with 15+ financial KPIs  
- **🔄 TTM Calculations** - Trailing Twelve Months metrics with automatic updates
- **📈 Peer Benchmarking** - Cross-industry financial ratio comparisons
- **🚀 Cloud-Native** - Fully hosted on Supabase with GitHub Actions CI/CD
- **📋 Compliance Ready** - SEC-compliant data extraction with proper attribution

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SEC EDGAR     │───▶│   Python ETL     │───▶│   Supabase      │
│   (Raw Data)    │    │   (Extract &     │    │   (PostgreSQL)  │
└─────────────────┘    │    Transform)    │    └─────────────────┘
                       └──────────────────┘             │
                                ▲                       │
┌─────────────────┐             │                       ▼
│   Power BI      │◀────────────┼──────────────┐ ┌──────────────────┐
│   (Dashboard)   │             │              │ │       dbt        │
└─────────────────┘             │              │ │ (Transformations)│
                                │              │ └──────────────────┘
┌─────────────────┐             │              │
│   FastAPI       │◀────────────┘              │
│   (REST API)    │◀───────────────────────────┘
└─────────────────┘
```

### Data Flow

1. **Extract** - Python scripts pull quarterly financials from SEC EDGAR API
2. **Load** - Raw JSON data stored in `raw.sec_company_facts` table
3. **Transform** - dbt models create star schema with fact/dimension tables
4. **Serve** - FastAPI provides RESTful access to transformed data
5. **Visualize** - Power BI connects directly to Supabase for real-time dashboards

## 🚀 Quick Start

### 1. Configuração Inicial
```bash
git clone https://github.com/victorhnm/integrated-financial-analysis.git
cd integrated-financial-analysis
pip install -r requirements.txt
cp .env.example .env  # Configure suas credenciais
```

### 2. PostgreSQL Setup
```bash
# Docker PostgreSQL
docker run --name postgres-financial \
  -e POSTGRES_USER=victorhnm \
  -e POSTGRES_PASSWORD=@urora12 \
  -e POSTGRES_DB=aurora_db \
  -p 5432:5432 -d postgres:15

# Inicializar schema
python execute_sql.py
```

### 3. Executar Pipeline
```bash
# Testar conectividade
python -m etl.main health

# Ingerir dados
python -m etl.main companies
```

### 4. API
```bash
python api/app.py
# Docs: http://localhost:8000/docs
```

## 📊 Dados Disponíveis

### Empresas Incluídas
- **AAPL**: Apple Inc.
- **MSFT**: Microsoft Corporation  
- **AMZN**: Amazon.com Inc.

### Métricas Financeiras
- Income Statement: Revenue, Net Income, Operating Income
- Balance Sheet: Assets, Liabilities, Equity
- Cash Flow: Operating, Investing, Financing

## 🌐 API Endpoints

- `GET /health` - Health check
- `GET /companies` - Lista empresas
- `GET /raw-data/{cik}` - Dados brutos SEC

## 🔧 Configuração

### Variáveis de Ambiente (.env)
```env
DATABASE_URL=postgresql://victorhnm:@urora12@localhost:5432/aurora_db
SEC_USER_AGENT="Victor Nascimento victorhnm@gmail.com"
```

## 📋 Status do Projeto

### ✅ Implementado
- [x] ETL Pipeline Python com SEC EDGAR
- [x] Modelo PostgreSQL (4 camadas)
- [x] FastAPI com endpoints principais  
- [x] dbt project básico
- [x] Parser XBRL básico

### 🔄 Em Desenvolvimento
- [ ] GitHub Actions CI/CD
- [ ] Power BI templates
- [ ] Métricas TTM completas

## 🤝 Contributing

Contribuições são bem-vindas! Veja [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

## 📄 License

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/victorhnm/integrated-financial-analysis/issues)
- **Docs**: [Documentation](docs/)

---

**Desenvolvido com ❤️ por [@victorhnm](https://github.com/victorhnm)**  
*Projeto completo de Análise Financeira Integrada*
