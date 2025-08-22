# 📊 Conectando Power BI à API e DWH

## 🎯 Opções de Conexão

Você tem **duas opções principais** para conectar o Power BI aos dados:

### **Opção 1: Conexão Direta ao PostgreSQL (RECOMENDADO)**
✅ **Melhor performance**  
✅ **Queries nativas**  
✅ **Refresh automático**  
✅ **Relacionamentos no Power BI**  

### **Opção 2: Conexão via API REST**  
✅ **Dados pré-processados**  
✅ **Lógicas de negócio aplicadas**  
✅ **Análises prontas**  

---

## 🔗 Opção 1: Conexão Direta ao PostgreSQL

### 1. Configurar Conexão no Power BI

1. **Abrir Power BI Desktop**
2. **Obter Dados** → **Base de Dados** → **PostgreSQL**
3. **Configurar conexão:**
   ```
   Servidor: localhost:5432
   Base de Dados: aurora_db
   ```

4. **Credenciais:**
   ```
   Utilizador: postgres
   Palavra-passe: 123456
   ```

### 2. Selecionar Tabelas

Selecione as tabelas do DWH:
- ✅ `dim_contas`
- ✅ `dim_centros_custo`
- ✅ `dim_tempo`
- ✅ `dim_produtos`
- ✅ `dim_fornecedores`
- ✅ `fato_lancamentos`
- ✅ `fato_caixa`

### 3. Criar Relacionamentos

No **Modelo** do Power BI:
```
fato_lancamentos → dim_contas (sk_conta)
fato_lancamentos → dim_centros_custo (sk_centro_custo)
fato_lancamentos → dim_tempo (sk_tempo)

fato_caixa → dim_contas (sk_conta)
fato_caixa → dim_centros_custo (sk_centro_custo)
fato_caixa → dim_tempo (sk_tempo)
```

### 4. Medidas DAX Sugeridas

```dax
Total Receitas = 
SUMX(
    FILTER(fato_lancamentos, RELATED(dim_contas[tipo_conta]) = "Receita"),
    fato_lancamentos[valor]
)

Total Despesas = 
SUMX(
    FILTER(fato_lancamentos, RELATED(dim_contas[tipo_conta]) = "Despesa"),
    ABS(fato_lancamentos[valor])
)

Resultado = [Total Receitas] - [Total Despesas]

Margem % = 
IF([Total Receitas] > 0, [Resultado] / [Total Receitas], BLANK())
```

---

## 🌐 Opção 2: Conexão via API REST

### 1. Configurar Web Source

1. **Obter Dados** → **Web**
2. **URL da API:** `http://localhost:8000/v1/fatos/resumo-financeiro?agrupamento=mensal`

### 2. Endpoints Úteis para Power BI

#### KPIs Principais
```
GET http://localhost:8000/v1/fatos/kpis
```

#### Resumo por Período
```
GET http://localhost:8000/v1/fatos/resumo-financeiro?agrupamento=mensal&data_inicio=2024-01-01
```

#### Top Contas
```
GET http://localhost:8000/v1/fatos/analise-contas?top_n=10&tipo_conta=Despesa
```

#### Lançamentos Detalhados
```
GET http://localhost:8000/v1/fatos/lancamentos?data_inicio=2024-01-01&limit=1000
```

### 3. Power Query - Expandir JSON

Após importar da API, use **Power Query** para:
1. **Converter em Tabela**
2. **Expandir colunas JSON**
3. **Definir tipos de dados**

---

## 🎨 Dashboards Sugeridos

### Dashboard 1: Visão Executiva
- 📊 **KPIs:** Receita, Despesa, Resultado, Margem
- 📈 **Gráfico:** Evolução mensal
- 🥧 **Pizza:** Receitas por grupo de conta
- 📋 **Tabela:** Top 10 contas

### Dashboard 2: Análise Operacional
- 📊 **Gráfico de Barras:** Despesas por centro de custo
- 📈 **Linha:** Evolução por trimestre
- 🗓️ **Slicer:** Filtro de período
- 📋 **Matriz:** Contas vs Centros de Custo

### Dashboard 3: Fluxo de Caixa
- 💰 **Waterfall:** Entradas vs Saídas
- 📈 **Área:** Saldo acumulado
- 📊 **Barras:** Maiores movimentações

---

## ⚡ Configurações de Performance

### Para Conexão PostgreSQL:
1. **DirectQuery** para dados em tempo real
2. **Import Mode** para melhor performance
3. **Scheduled Refresh** para dados atualizados

### Para API REST:
1. **Refresh incremental** configurado
2. **Cache de dados** habilitado
3. **Queries parametrizadas**

---

## 🔧 Troubleshooting

### Erro de Conexão PostgreSQL:
```sql
-- Testar conexão diretamente:
psql -h localhost -p 5432 -U postgres -d aurora_db
```

### API não responde:
```bash
# Verificar se API está rodando:
curl http://localhost:8000/health
```

### Firewall/Rede:
- Verificar portas 5432 (PostgreSQL) e 8000 (API)
- Configurar exceções no Windows Defender

---

## 🚀 Próximos Passos

1. **Teste ambas as opções** para escolher a ideal
2. **Crie os dashboards** baseados nos dados
3. **Configure refresh automático**
4. **Publique no Power BI Service** (opcional)
5. **Configure row-level security** se necessário