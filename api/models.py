# api/models.py
# Modelos Pydantic para request/response da API
# Schemas de dados, validação e serialização

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from decimal import Decimal

# =============================================================================
# MODELOS BASE E METADADOS
# =============================================================================

class PaginationMetadata(BaseModel):
    """Metadados de paginação"""
    page: int = Field(..., description="Página atual")
    page_size: int = Field(..., description="Itens por página")
    total_items: int = Field(..., description="Total de itens")
    total_pages: int = Field(..., description="Total de páginas")
    has_next: bool = Field(..., description="Tem próxima página")
    has_previous: bool = Field(..., description="Tem página anterior")

class ErrorResponse(BaseModel):
    """Modelo padrão para respostas de erro"""
    error: str = Field(..., description="Tipo do erro")
    message: str = Field(..., description="Mensagem descritiva")
    path: str = Field(..., description="Path do endpoint")
    timestamp: datetime = Field(..., description="Timestamp do erro")
    details: Optional[Any] = Field(None, description="Detalhes adicionais")

# =============================================================================
# MODELOS DE DADOS DE NEGÓCIO
# =============================================================================

class Company(BaseModel):
    """Modelo de empresa"""
    company_id: str = Field(..., description="ID único da empresa")
    cik: str = Field(..., description="Central Index Key da SEC")
    ticker: Optional[str] = Field(None, description="Símbolo de negociação")
    company_name: str = Field(..., description="Nome da empresa")
    sector: Optional[str] = Field(None, description="Setor econômico")
    country: Optional[str] = Field(None, description="País sede")
    currency: Optional[str] = Field(None, description="Moeda de reporte")
    is_active: bool = Field(..., description="Se empresa está ativa")
    created_ts: datetime = Field(..., description="Data de criação do registro")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FinancialFact(BaseModel):
    """Modelo de fato financeiro"""
    company_id: str = Field(..., description="ID da empresa")
    ticker: Optional[str] = Field(None, description="Ticker da empresa")
    company_name: str = Field(..., description="Nome da empresa")
    concept: str = Field(..., description="Conceito original (US-GAAP/IFRS)")
    canonical_metric: Optional[str] = Field(None, description="Métrica padronizada")
    statement_type: Optional[str] = Field(None, description="Tipo de demonstrativo (IS/BS/CF)")
    period_start: Optional[date] = Field(None, description="Início do período")
    period_end: date = Field(..., description="Fim do período")
    fiscal_year: int = Field(..., description="Ano fiscal")
    fiscal_period: str = Field(..., description="Período fiscal (Q1,Q2,Q3,Q4,FY)")
    form: str = Field(..., description="Tipo de form SEC")
    value_native: Optional[Decimal] = Field(None, description="Valor na moeda original")
    value_usd: Optional[Decimal] = Field(None, description="Valor convertido para USD")
    currency_native: Optional[str] = Field(None, description="Moeda original")
    unit: str = Field(..., description="Unidade de medida")
    is_restated: bool = Field(..., description="Se é um restatement")
    
    @validator('value_native', 'value_usd', pre=True)
    def parse_decimal(cls, v):
        if v is None:
            return v
        return float(v) if isinstance(v, Decimal) else v

class TTMMetric(BaseModel):
    """Modelo de métrica TTM"""
    company_id: str = Field(..., description="ID da empresa")
    ticker: str = Field(..., description="Ticker da empresa")
    company_name: str = Field(..., description="Nome da empresa")
    sector: Optional[str] = Field(None, description="Setor")
    as_of_date: date = Field(..., description="Data de referência")
    
    # TTM Base Metrics
    revenue_ttm: Optional[Decimal] = Field(None, description="Receita TTM (USD)")
    net_income_ttm: Optional[Decimal] = Field(None, description="Lucro líquido TTM (USD)")
    operating_income_ttm: Optional[Decimal] = Field(None, description="Lucro operacional TTM (USD)")
    ebitda_ttm: Optional[Decimal] = Field(None, description="EBITDA TTM (USD)")
    free_cash_flow_ttm: Optional[Decimal] = Field(None, description="Free Cash Flow TTM (USD)")
    
    # Profitability Ratios (como percentuais)
    gross_margin: Optional[float] = Field(None, description="Margem bruta")
    operating_margin: Optional[float] = Field(None, description="Margem operacional")
    net_margin: Optional[float] = Field(None, description="Margem líquida")
    
    # Return Ratios
    roe: Optional[float] = Field(None, description="Return on Equity")
    roa: Optional[float] = Field(None, description="Return on Assets")
    
    # Leverage Ratios
    debt_to_equity: Optional[float] = Field(None, description="Debt to Equity")
    current_ratio: Optional[float] = Field(None, description="Liquidez corrente")
    
    # Growth Rates (como percentuais)
    revenue_growth_yoy: Optional[float] = Field(None, description="Crescimento receita YoY")
    net_income_growth_yoy: Optional[float] = Field(None, description="Crescimento lucro YoY")
    
    # Efficiency Metrics (em dias)
    days_sales_outstanding: Optional[float] = Field(None, description="DSO - dias")
    days_inventory_outstanding: Optional[float] = Field(None, description="DIO - dias")
    days_payable_outstanding: Optional[float] = Field(None, description="DPO - dias")
    
    @validator('revenue_ttm', 'net_income_ttm', 'operating_income_ttm', 'ebitda_ttm', 'free_cash_flow_ttm', pre=True)
    def parse_decimal_fields(cls, v):
        if v is None:
            return v
        return float(v) if isinstance(v, Decimal) else v

# =============================================================================
# MODELOS DE RESPOSTA
# =============================================================================

class HealthResponse(BaseModel):
    """Resposta do health check"""
    status: str = Field(..., description="Status da API (healthy/degraded/unhealthy)")
    message: str = Field(..., description="Mensagem descritiva")
    timestamp: datetime = Field(..., description="Timestamp da verificação")
    database_connected: bool = Field(..., description="Se banco está conectado")
    data_summary: Optional[Dict[str, int]] = Field(None, description="Resumo dos dados")

class CompanyResponse(BaseModel):
    """Resposta do endpoint de empresas"""
    data: List[Company] = Field(..., description="Lista de empresas")
    metadata: PaginationMetadata = Field(..., description="Metadados de paginação")
    filters_applied: Dict[str, Any] = Field(..., description="Filtros aplicados")

class FactsResponse(BaseModel):
    """Resposta do endpoint de fatos financeiros"""
    data: List[FinancialFact] = Field(..., description="Lista de fatos financeiros")
    metadata: PaginationMetadata = Field(..., description="Metadados de paginação")
    filters_applied: Dict[str, Any] = Field(..., description="Filtros aplicados")
    aggregations: Dict[str, Any] = Field(default_factory=dict, description="Agregações dos dados")

class TTMResponse(BaseModel):
    """Resposta do endpoint de métricas TTM"""
    data: List[TTMMetric] = Field(..., description="Lista de métricas TTM")
    metadata: PaginationMetadata = Field(..., description="Metadados de paginação")
    filters_applied: Dict[str, Any] = Field(..., description="Filtros aplicados")
    summary_stats: Dict[str, Any] = Field(default_factory=dict, description="Estatísticas resumo")

# =============================================================================
# MODELOS DE REQUEST (para POST endpoints futuros)
# =============================================================================

class CompanyFilterRequest(BaseModel):
    """Request para filtros avançados de empresas"""
    tickers: Optional[List[str]] = Field(None, description="Lista de tickers")
    sectors: Optional[List[str]] = Field(None, description="Lista de setores")
    countries: Optional[List[str]] = Field(None, description="Lista de países")
    market_cap_min: Optional[float] = Field(None, description="Market cap mínimo")
    market_cap_max: Optional[float] = Field(None, description="Market cap máximo")
    
    @validator('tickers', 'sectors', 'countries', pre=True)
    def convert_to_upper(cls, v):
        if v is None:
            return v
        return [item.upper() for item in v]

class MetricsFilterRequest(BaseModel):
    """Request para filtros de métricas financeiras"""
    companies: Optional[List[str]] = Field(None, description="Lista de company_ids ou tickers")
    metrics: Optional[List[str]] = Field(None, description="Lista de canonical_metrics")
    date_range: Optional[Dict[str, date]] = Field(None, description="Range de datas")
    statements: Optional[List[str]] = Field(None, description="Tipos de demonstrativo")
    
    @validator('statements', pre=True)
    def validate_statements(cls, v):
        if v is None:
            return v
        valid_statements = ['IS', 'BS', 'CF']
        return [s.upper() for s in v if s.upper() in valid_statements]

# =============================================================================
# UTILITÁRIOS E VALIDADORES
# =============================================================================

class APIConfig(BaseModel):
    """Configurações da API"""
    max_page_size: int = 1000
    default_page_size: int = 100
    cache_ttl_seconds: int = 300
    rate_limit_requests: int = 1000
    rate_limit_window_seconds: int = 3600

def format_currency(value: Optional[Union[float, Decimal]], currency: str = "USD") -> Optional[str]:
    """Formatar valores monetários"""
    if value is None:
        return None
    
    if isinstance(value, Decimal):
        value = float(value)
    
    if abs(value) >= 1e12:
        return f"{value/1e12:.1f}T {currency}"
    elif abs(value) >= 1e9:
        return f"{value/1e9:.1f}B {currency}"
    elif abs(value) >= 1e6:
        return f"{value/1e6:.1f}M {currency}"
    elif abs(value) >= 1e3:
        return f"{value/1e3:.1f}K {currency}"
    else:
        return f"{value:.2f} {currency}"

def format_percentage(value: Optional[float], decimal_places: int = 1) -> Optional[str]:
    """Formatar percentuais"""
    if value is None:
        return None
    
    percentage = value * 100  # Converter decimal para percentual
    return f"{percentage:.{decimal_places}f}%"

def format_ratio(value: Optional[float], decimal_places: int = 2) -> Optional[str]:
    """Formatar ratios"""
    if value is None:
        return None
    
    return f"{value:.{decimal_places}f}x"