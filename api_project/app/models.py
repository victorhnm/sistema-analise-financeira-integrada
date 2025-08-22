from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from decimal import Decimal

# Modelos para Dimensões
class DimContaResponse(BaseModel):
    sk_conta: str
    id_conta_origem: str
    nome_conta: str
    tipo_conta: str
    grupo_conta: str

class DimCentroCustoResponse(BaseModel):
    sk_centro_custo: str
    id_cc_origem: str
    nome_centro_custo: str
    setor: str
    gerencia: str

class DimTempoResponse(BaseModel):
    sk_tempo: int  # dim_tempo usa integer como PK
    data: date
    ano: int
    mes: int
    trimestre: int
    nome_mes: str
    dia_semana: int
    nome_dia_semana: str

class DimProdutoResponse(BaseModel):
    sk_produto: str
    id_produto_origem: str
    nome_produto: str
    categoria: str
    subcategoria: str

class DimFornecedorResponse(BaseModel):
    sk_fornecedor: str
    id_fornecedor_origem: str
    nome_fornecedor: str
    tipo_fornecedor: str
    categoria_fornecedor: str

# Modelos para Fatos
class FatoLancamentoResponse(BaseModel):
    sk_tempo: int  # dim_tempo usa integer
    sk_conta: str  # outras dimensões usam string (MD5)
    sk_centro_custo: str
    sk_produto: Optional[str] = None  # Pode ser NULL
    sk_fornecedor: Optional[str] = None  # Pode ser NULL
    valor: Decimal
    descricao: Optional[str] = None
    origem_dados: str

class FatoCaixaResponse(BaseModel):
    sk_tempo: int  # dim_tempo usa integer
    sk_conta: str  # outras dimensões usam string (MD5)
    sk_centro_custo: str
    valor_entrada: Optional[Decimal] = Field(default=0)
    valor_saida: Optional[Decimal] = Field(default=0)
    saldo: Decimal
    descricao: Optional[str] = None
    origem_dados: str

# Modelos para Filtros
class DateRangeFilter(BaseModel):
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None

class ContaFilter(BaseModel):
    tipo_conta: Optional[str] = None
    grupo_conta: Optional[str] = None

# Modelos para Análises Agregadas
class ResumoFinanceiroResponse(BaseModel):
    periodo: str
    total_receitas: Decimal
    total_despesas: Decimal
    resultado: Decimal
    margem_percentual: Optional[float] = None

class AnaliseContaResponse(BaseModel):
    conta: DimContaResponse
    valor_periodo: Decimal
    percentual_total: float
    evolucao_periodo_anterior: Optional[float] = None