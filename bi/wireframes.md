# Wireframes Power BI - Integrated Financial Analysis
# 3 Páginas: Visão Executiva, Desempenho e Crescimento, Liquidez e Caixa

## PÁGINA 1: VISÃO EXECUTIVA
*Audience: C-Level, Diretoria*
*Objetivo: KPIs de alto nível e trends principais*

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ INTEGRATED FINANCIAL ANALYSIS                                    🔄 Atualizado em: [Data] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ 📊 VISÃO EXECUTIVA                     Filtros: [Empresa ▼] [Setor ▼] [Período ▼] │
│                                                                             │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────────────┤
│             │             │             │             │                     │
│  💰 Receita │  💼 Lucro   │  📈 ROE     │  🚀 Crescim.│    📊 PERFORMANCE   │
│  TTM        │  Líquido    │             │  Receita    │      vs SETOR       │
│             │  TTM        │             │  YoY        │                     │
│  $15.2B     │  $2.8B      │   18.5%     │   +12.3%    │  [Gráfico Scatter] │
│  ↗️ +8.2%   │  ↗️ +15.1%  │  ↗️ +2.1pp  │  ↗️ Acelerou │  ROE vs Revenue TTM │
│             │             │             │             │  Bubbles = Empresas │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────────────┘
│                                                                             │
├─────────────────────────────────────────┬───────────────────────────────────┤
│                                         │                                   │
│         📈 EVOLUÇÃO FINANCEIRA          │      🎯 SCORE DE QUALIDADE        │
│                                         │                                   │
│  [Gráfico de Linha - Dual Axis]        │    [Gauge Chart 0-100]            │
│  Eixo Principal: Receita TTM ($B)       │                                   │
│  Eixo Secundário: Margem Líquida (%)    │         Score: 85/100             │
│  Período: Últimos 5 anos                │         ✅ Excelente              │
│  Linhas: Empresa vs Mediana Setor       │                                   │
│                                         │    Componentes:                   │
│                                         │    ROE: ████████░░ 80%            │
│                                         │    Margem: ██████████ 100%        │
│                                         │    Crescimento: ███████░░░ 70%     │
│                                         │    Liquidez: ████████░░ 80%       │
│                                         │    Alavancagem: ██████████ 100%   │
└─────────────────────────────────────────┴───────────────────────────────────┘
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│              🏆 RANKING SETORIAL                                             │
│                                                                             │
│  [Tabela com formatação condicional]                                        │
│  ┌──────────────────┬──────────┬──────────┬──────────┬──────────┬──────────┐ │
│  │ Empresa          │ Receita  │ ROE      │ Margem   │ Crescim. │ Rank     │ │
│  │                  │ TTM      │          │ Líquida  │ YoY      │ Receita  │ │
│  ├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤ │
│  │ 🟢 EMPRESA ATUAL │ $15.2B   │ 18.5%    │ 18.4%    │ +12.3%   │ #2       │ │
│  │ Microsoft Corp   │ $21.3B   │ 21.2%    │ 22.1%    │ +8.7%    │ #1       │ │
│  │ Oracle Corp      │ $8.9B    │ 15.1%    │ 15.8%    │ +5.2%    │ #3       │ │
│  │ Salesforce       │ $7.1B    │ 12.8%    │ 12.4%    │ +18.9%   │ #4       │ │
│  │ Adobe Inc        │ $5.8B    │ 19.2%    │ 20.3%    │ +9.1%    │ #5       │ │
│  └──────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ 🚨 ALERTAS E INSIGHTS                                                        │
│ • ✅ Liquidez em nível saudável (Current Ratio: 1.8x)                      │
│ • ⚠️  Alavancagem subiu 15% no último trimestre                             │
│ • 🚀 Crescimento acelerando: +12.3% vs +8.1% no trimestre anterior         │
│ • 📊 Performance superior à mediana do setor em ROE e Margem               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PÁGINA 2: DESEMPENHO E CRESCIMENTO  
*Audience: CFO, Analistas Financeiros*
*Objetivo: Análise detalhada de rentabilidade e crescimento*

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📊 DESEMPENHO & CRESCIMENTO              Empresa: [SELECIONADA] | Setor: [TECH] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ 🔍 ANÁLISE DUPONT - DECOMPOSIÇÃO DO ROE                                     │
│                                                                             │
├─────────────────────┬─────────────────────┬───────────────────────────────────┤
│                     │                     │                                 │
│   📈 MARGEM LÍQUIDA │  🔄 GIRO DO ATIVO   │    ⚖️ MULTIPLICADOR CAPITAL    │
│                     │                     │                                 │
│      18.4%          │       0.85x         │           1.18x                 │
│   ↗️ +1.2pp YoY     │    ↘️ -0.05x YoY    │        ↗️ +0.08x YoY           │
│                     │                     │                                 │
│  [Mini Waterfall]   │   [Mini Waterfall]  │      [Mini Waterfall]           │
│  Gross → Op → Net   │  Revenue / Assets   │     Assets / Equity             │
│                     │                     │                                 │
└─────────────────────┴─────────────────────┴───────────────────────────────────┘
│                     =                     ×                   ×             │
│                              ROE = 18.5%                                     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│              📊 EVOLUÇÃO TRIMESTRAL (Últimos 8 Trimestres)                  │
│                                                                             │
│  [Gráfico Combinado - Barras + Linhas]                                     │
│  Barras: Receita Trimestral ($B)                                           │
│  Linha 1: Margem Bruta (%)                                                 │
│  Linha 2: Margem Operacional (%)                                           │
│  Linha 3: Margem Líquida (%)                                               │
│  Eixo X: Q1'22, Q2'22, Q3'22, Q4'22, Q1'23, Q2'23, Q3'23, Q4'23          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
│                                                                             │
├───────────────────────────────┬─────────────────────────────────────────────┤
│                               │                                             │
│    💹 CRESCIMENTO YoY         │         🎯 BENCHMARK SETORIAL               │
│                               │                                             │
│ [Gráfico de Barras Duplas]    │  [Gráfico Radar/Spider]                    │
│ Trimestre atual vs Ano ant.   │  Métricas vs Mediana do Setor:             │
│                               │                                             │
│ Receita:     +12.3% ████████  │  • ROE: 18.5% vs 15.2% (Mediana) ✅        │
│ Op Income:   +18.7% ██████████│  • Op Margin: 22.1% vs 18.8% ✅           │
│ Net Income:  +15.1% █████████ │  • Asset Turn: 0.85x vs 0.92x ⚠️          │
│ EBITDA:      +14.2% █████████ │  • Growth: +12.3% vs +7.1% ✅             │
│ Free CF:     +21.4% ██████████│  • D/E Ratio: 0.18x vs 0.34x ✅           │
│                               │                                             │
│ 🔥 Destaque: FCF crescendo    │  📊 Percentil 75 no setor                  │
│    mais rápido que receita    │                                             │
│                               │                                             │
└───────────────────────────────┴─────────────────────────────────────────────┘
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│              📈 ANÁLISE DE TENDÊNCIAS (5 Anos)                              │
│                                                                             │
│  [Gráfico de Área Empilhada]                                               │
│  Componentes da Receita (se disponível por segmento)                       │
│  + Linha de tendência da Margem EBITDA                                     │
│  + Annotations para eventos importantes (acquisições, etc.)                │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ 🔍 INSIGHTS AUTOMATIZADOS                                                   │
│ • 🚀 Free Cash Flow crescendo 21.4% YoY, superando crescimento da receita  │
│ • 📊 Margem operacional expandiu 120bp nos últimos 4 trimestres            │
│ • ⚡ Giro do ativo ligeiramente abaixo da mediana setorial                  │
│ • 💪 ROE no percentil 75 do setor, driven por margem superior              │
│ • 🎯 Próximo earnings: [DATA] | Consenso receita: $X.XB (+X.X% YoY)        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PÁGINA 3: LIQUIDEZ E CAIXA
*Audience: CFO, Controller, Tesouraria*  
*Objetivo: Análise de liquidez, cash flow e working capital*

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 💧 LIQUIDEZ & GESTÃO DE CAIXA            🔍 Análise Working Capital & Cash Flow │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ 🏦 POSIÇÃO DE LIQUIDEZ                                                      │
│                                                                             │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│                 │                 │                 │                       │
│ 💰 CAIXA &      │ 📊 LIQUIDEZ     │ ⚖️ ALAVANCAGEM  │  📅 CICLO CONVERSÃO   │
│ EQUIVALENTES    │ CORRENTE        │                 │     CAIXA             │
│                 │                 │                 │                       │
│   $8.5B         │     1.8x        │     0.18x       │      32 dias          │
│ ↗️ +$1.2B YoY   │  ↗️ +0.2x YoY   │  ↘️ -0.05x YoY  │    ↘️ -8 dias YoY     │
│                 │                 │                 │                       │
│ [Progress Bar]  │ [Gauge 0-3x]    │ [Gauge 0-1x]    │ [Componentes]:        │
│ vs Debt: 47x    │ Ideal: >1.5x ✅ │ Baixo: <0.3x ✅ │ DSO: 18d ↘️ (-3d)     │
│ coverage        │                 │                 │ DIO: 28d ↘️ (-2d)     │
│                 │                 │                 │ DPO: 14d ↘️ (-3d)     │
│                 │                 │                 │ = CCC: 32d ✅         │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│              💸 ANÁLISE DE CASH FLOW (Últimos 8 Trimestres)                 │
│                                                                             │
│  [Gráfico Waterfall + Área]                                                │
│  Área: Operating Cash Flow (baseline)                                      │
│  Barras: Investing CF (negativo - CapEx, M&A)                             │
│  Barras: Financing CF (dividendos, recompras, debt)                        │
│  Linha: Free Cash Flow resultante                                          │
│  Linha: Cash Balance (escala secundária)                                   │
│                                                                             │
│  Destaques:                                                                 │
│  • Op CF growing consistently ✅                                            │
│  • CapEx as % of Revenue stable at ~8% ✅                                  │
│  • Share buybacks: $2.1B in Q4 📊                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
│                                                                             │
├─────────────────────────────────────┬───────────────────────────────────────┤
│                                     │                                       │
│     🔄 WORKING CAPITAL TRENDS       │       💎 QUALITY OF EARNINGS         │
│                                     │                                       │
│ [Gráfico de Área Empilhada]        │  [Gráfico de Barras Horizontais]     │
│ Componentes:                        │                                       │
│ • Accounts Receivable               │  Cash Earnings Ratio:                │
│ • Inventory                         │  Op CF / Net Income = 1.15x ✅        │
│ • Accounts Payable (negativo)       │                                       │
│ • Net Working Capital               │  [Progressão trimestral]              │
│                                     │  Q4'23: ████████████ 1.15x           │
│ Insights:                           │  Q3'23: ███████████░ 1.08x           │
│ • Working Capital otimizado ✅       │  Q2'23: ██████████░░ 0.98x           │
│ • Inventory turns improving         │  Q1'23: █████████░░░ 0.89x           │
│ • Payment terms stable              │                                       │
│                                     │  🎯 Trend: Improving quality ✅       │
└─────────────────────────────────────┴───────────────────────────────────────┘
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│            📊 LIQUIDEZ vs PEERS (Setor Technology)                          │
│                                                                             │
│  [Scatter Plot]                                                             │
│  Eixo X: Current Ratio                                                      │
│  Eixo Y: Cash-to-Debt Ratio                                                │
│  Bubbles: Empresas do setor (tamanho = Market Cap)                         │
│  Destacar: Empresa atual vs Mediana vs Top/Bottom quartile                 │
│                                                                             │
│  Quadrantes:                                                                │
│  • Superior Direito: "Fortress Balance Sheet" ✅                            │
│  • Superior Esquerdo: "Cash Rich, Low Liquidity"                           │
│  • Inferior Direito: "Liquid but Leveraged"                               │
│  • Inferior Esquerdo: "Risk Zone" ⚠️                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ 🎯 SCORECARD DE LIQUIDEZ                                                    │
│                                                                             │
│ ┌─────────────────────┬──────────┬──────────┬──────────┬──────────────────┐ │
│ │ Métrica             │ Atual    │ Anterior │ Mediana  │ Status           │ │
│ │                     │          │ (4Q ago) │ Setor    │                  │ │
│ ├─────────────────────┼──────────┼──────────┼──────────┼──────────────────┤ │
│ │ Current Ratio       │ 1.8x     │ 1.6x     │ 1.4x     │ ✅ Acima Média  │ │
│ │ Cash Ratio          │ 1.2x     │ 1.0x     │ 0.8x     │ ✅ Forte        │ │
│ │ Days Cash on Hand   │ 180d     │ 165d     │ 120d     │ ✅ Confortável  │ │
│ │ Debt/EBITDA         │ 0.4x     │ 0.5x     │ 1.2x     │ ✅ Conservador  │ │
│ │ Interest Coverage   │ 45.2x    │ 38.1x    │ 12.5x    │ ✅ Excelente    │ │
│ │ Cash Conversion     │ 32d      │ 40d      │ 45d      │ ✅ Eficiente    │ │
│ └─────────────────────┴──────────┴──────────┴──────────┴──────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ 💡 INSIGHTS E RECOMENDAÇÕES                                                 │
│ • 🏆 Posição de caixa robusta permite flexibilidade estratégica             │
│ • 📈 Working capital management melhorando consistentemente                  │
│ • ⚡ Oportunidade: DSO ainda 3 dias acima da mediana do setor               │
│ • 💰 Excess cash: $5.2B above operational needs - consider shareholder returns │
│ • 📊 Quality of earnings excelente: cash consistently > net income          │
│ • 🎯 Debt capacity: Could support $15B+ additional debt if needed           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## CONFIGURAÇÕES RECOMENDADAS

### Temas e Formatação
```yaml
Paleta de Cores:
  Primária: "#1f4e79" (Azul corporativo)
  Secundária: "#70ad47" (Verde crescimento)  
  Alertas: "#e74c3c" (Vermelho)
  Neutro: "#7f7f7f" (Cinza)
  
Fontes:
  Títulos: Segoe UI Bold, 14pt
  Texto: Segoe UI, 10pt
  Números: Segoe UI Semibold, 12pt
```

### Interações
```yaml
Filtros Globais (todas as páginas):
  - Empresa (multi-select)
  - Setor (multi-select) 
  - Período de referência (date range)

Cross-filtering:
  - Clique em empresa → filtra toda a página
  - Drill-through: Empresa → Página detalhada
  - Tooltips customizados com contexto adicional
```

### Atualizações de Dados
```yaml
Refresh Schedule:
  - Diário: 06:00 UTC (após ETL pipeline)
  - Alertas: Email se falha no refresh
  - Incremental: Apenas últimos 90 dias para performance
  
Data Source:
  - Conexão direta ao Supabase via DirectQuery (tempo real)
  - Ou Import mode com refresh agendado (melhor performance)
```

### Instruções de Conexão

#### Opção A: Conexão Direta (DirectQuery)
1. Power BI Desktop → Get Data → PostgreSQL
2. Server: `your-project.supabase.co`
3. Database: `postgres`
4. Port: `5432`
5. Advanced → SSL Mode: `require`
6. Credentials: Username: `postgres`, Password: `[sua senha]`
7. Navigator → Selecionar tabelas dos schemas `core` e `marts`

#### Opção B: Via API (recomendado para publicação)
1. Usar endpoints da FastAPI: `/companies`, `/facts`, `/ttm`
2. Power BI → Get Data → Web → URL da API
3. Benefícios: Rate limiting, cache, paginação automática

#### Opção C: Export CSV/Parquet
Script Python para export periódico:
```python
# Executar via cron/scheduler
python -m etl.export_powerbi --format parquet --output ./bi/exports/
```

**Commit sugerido:**

```bash
# Comandos git (copiar/colar)
git checkout -b feat/bi/power-bi-wireframes-medidas
git add bi/modelo_estrela.md bi/medidas_dax.txt bi/wireframes.md
git commit -m "feat(bi): adicionar modelo estrela, medidas DAX e wireframes Power BI

- Modelo dimensional com fact tables quarterly/ttm
- 15+ medidas DAX incluindo DuPont, ratios e KPIs
- 3 wireframes detalhados: Executivo, Performance, Liquidez
- Instruções de conexão Supabase e configurações recomendadas"
git push -u origin feat/bi/power-bi-wireframes-medidas
```

**Título PR:** feat(bi): modelo Power BI completo com wireframes e medidas DAX

**Descrição PR:** Adiciona modelo dimensional estrela, 15+ medidas DAX (incluindo análise DuPont e ratios financeiros) e wireframes detalhados de 3 páginas para dashboard executivo. Inclui instruções de conexão ao Supabase e configurações de formatação recomendadas.

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Criar vis\u00e3o geral e diagrama ASCII da arquitetura", "status": "completed", "activeForm": "Criando vis\u00e3o geral e diagrama ASCII"}, {"content": "Definir estrutura de pastas e .gitignore", "status": "completed", "activeForm": "Definindo estrutura de pastas"}, {"content": "Criar cat\u00e1logo de fontes de dados e licen\u00e7as", "status": "completed", "activeForm": "Criando cat\u00e1logo de fontes"}, {"content": "Desenvolver esquema do banco (DDL completo)", "status": "completed", "activeForm": "Desenvolvendo esquema do banco"}, {"content": "Configurar projeto dbt completo", "status": "completed", "activeForm": "Configurando projeto dbt"}, {"content": "Implementar ingest\u00e3o Python (ETL)", "status": "completed", "activeForm": "Implementando ingest\u00e3o Python"}, {"content": "Criar workflows GitHub Actions", "status": "completed", "activeForm": "Criando workflows GitHub Actions"}, {"content": "Desenvolver API FastAPI", "status": "completed", "activeForm": "Desenvolvendo API FastAPI"}, {"content": "Configurar modelo Power BI e medidas DAX", "status": "completed", "activeForm": "Configurando modelo Power BI"}, {"content": "Criar documenta\u00e7\u00e3o completa (README, troubleshooting, legal)", "status": "in_progress", "activeForm": "Criando documenta\u00e7\u00e3o completa"}]