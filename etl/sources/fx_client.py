# etl/sources/fx_client.py
# Cliente para taxas FX de ECB e FRED
# Suporte alternável entre fontes via configuração

import asyncio
import aiohttp
import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date, timedelta
import json
import backoff
from dataclasses import dataclass

from ..common.config import load_fx_config, FxConfig, DEFAULT_USER_AGENT

# =============================================================================
# ESTRUTURAS DE DADOS
# =============================================================================

@dataclass
class FxRate:
    """Representação de uma taxa de câmbio"""
    rate_date: date
    currency_from: str
    currency_to: str
    rate: float
    source: str

@dataclass
class FxApiResponse:
    """Response padronizada das APIs FX"""
    success: bool
    rates: List[FxRate]
    error: Optional[str]
    source: str
    extract_date: date

# =============================================================================
# CLIENTE BASE FX
# =============================================================================

class FxClientBase:
    """Classe base para clientes FX"""
    
    def __init__(self, config: FxConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
            self._session = None
    
    async def _ensure_session(self):
        """Garantir que session está inicializada"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            headers = {'User-Agent': DEFAULT_USER_AGENT}
            
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers,
                connector=aiohttp.TCPConnector(limit=5, limit_per_host=2)
            )
    
    async def _rate_limit(self):
        """Rate limiting básico"""
        # Implementar delay baseado em RPM
        delay = 60.0 / self.config.rate_limit_rpm
        await asyncio.sleep(delay)

# =============================================================================
# CLIENTE ECB (EUROPEAN CENTRAL BANK)
# =============================================================================

class EcbClient(FxClientBase):
    """Cliente para taxas FX do ECB (EUR base)"""
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        factor=2.0
    )
    async def get_historical_rates(self, days_back: int = 90) -> FxApiResponse:
        """
        Obter taxas históricas do ECB
        
        Args:
            days_back: Números de dias históricos (máx 90 por request)
            
        Returns:
            FxApiResponse com as taxas
        """
        await self._ensure_session()
        await self._rate_limit()
        
        try:
            self.logger.info(f"Fetching ECB rates for last {days_back} days")
            
            async with self._session.get(self.config.ecb_url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    self.logger.error(f"ECB API error {response.status}: {error_text}")
                    return FxApiResponse(
                        success=False,
                        rates=[],
                        error=f"HTTP {response.status}",
                        source="ECB",
                        extract_date=date.today()
                    )
                
                xml_content = await response.text()
                rates = self._parse_ecb_xml(xml_content, days_back)
                
                self.logger.info(f"Successfully fetched {len(rates)} ECB rates")
                return FxApiResponse(
                    success=True,
                    rates=rates,
                    error=None,
                    source="ECB",
                    extract_date=date.today()
                )
                
        except Exception as e:
            self.logger.error(f"Error fetching ECB rates: {e}")
            return FxApiResponse(
                success=False,
                rates=[],
                error=str(e),
                source="ECB",
                extract_date=date.today()
            )
    
    def _parse_ecb_xml(self, xml_content: str, days_back: int) -> List[FxRate]:
        """
        Parse do XML do ECB para extrair taxas
        
        XML Format:
        <gesmes:Envelope>
          <Cube>
            <Cube time="2024-01-02">
              <Cube currency="USD" rate="1.1050"/>
              <Cube currency="GBP" rate="0.8692"/>
            </Cube>
          </Cube>
        </gesmes:Envelope>
        """
        rates = []
        cutoff_date = date.today() - timedelta(days=days_back)
        
        try:
            # Namespace do ECB
            namespaces = {
                'gesmes': 'http://www.gesmes.org/xml/2002-08-01',
                'eurofxref': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'
            }
            
            root = ET.fromstring(xml_content)
            
            # Navegar pela estrutura aninhada
            for time_cube in root.findall('.//eurofxref:Cube[@time]', namespaces):
                rate_date_str = time_cube.get('time')
                if not rate_date_str:
                    continue
                
                rate_date = datetime.strptime(rate_date_str, '%Y-%m-%d').date()
                
                # Filtrar por data
                if rate_date < cutoff_date:
                    continue
                
                # Extrair taxas para cada moeda
                for currency_cube in time_cube.findall('.//eurofxref:Cube[@currency]', namespaces):
                    currency = currency_cube.get('currency')
                    rate_str = currency_cube.get('rate')
                    
                    if currency and rate_str:
                        try:
                            rate_value = float(rate_str)
                            
                            rates.append(FxRate(
                                rate_date=rate_date,
                                currency_from='EUR',
                                currency_to=currency,
                                rate=rate_value,
                                source='ECB'
                            ))
                        except ValueError:
                            self.logger.warning(f"Invalid rate value: {rate_str} for {currency}")
                            continue
        
        except ET.ParseError as e:
            self.logger.error(f"XML parsing error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error parsing ECB XML: {e}")
            return []
        
        return rates

# =============================================================================
# CLIENTE FRED (FEDERAL RESERVE ECONOMIC DATA)
# =============================================================================

class FredClient(FxClientBase):
    """Cliente para taxas FX do FRED (USD base)"""
    
    def __init__(self, config: FxConfig):
        super().__init__(config)
        if not config.fred_api_key:
            raise ValueError("FRED_API_KEY é obrigatório para usar fonte FRED")
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        factor=2.0
    )
    async def get_fx_series(
        self, 
        series_ids: List[str], 
        days_back: int = 90
    ) -> FxApiResponse:
        """
        Obter séries FX do FRED
        
        Args:
            series_ids: IDs das séries (ex: ['DEXUSEU', 'DEXUSGB'])
            days_back: Dias históricos
            
        Returns:
            FxApiResponse com as taxas
        """
        await self._ensure_session()
        
        all_rates = []
        
        for series_id in series_ids:
            await self._rate_limit()
            rates = await self._get_single_series(series_id, days_back)
            all_rates.extend(rates)
        
        self.logger.info(f"Successfully fetched {len(all_rates)} FRED rates")
        return FxApiResponse(
            success=True,
            rates=all_rates,
            error=None,
            source="FRED",
            extract_date=date.today()
        )
    
    async def _get_single_series(self, series_id: str, days_back: int) -> List[FxRate]:
        """Obter uma série individual do FRED"""
        start_date = date.today() - timedelta(days=days_back)
        
        url = f"{self.config.fred_base_url}/series/observations"
        params = {
            'series_id': series_id,
            'api_key': self.config.fred_api_key,
            'file_type': 'json',
            'observation_start': start_date.strftime('%Y-%m-%d'),
            'observation_end': date.today().strftime('%Y-%m-%d')
        }
        
        try:
            async with self._session.get(url, params=params) as response:
                if response.status != 200:
                    self.logger.error(f"FRED API error {response.status} for {series_id}")
                    return []
                
                data = await response.json()
                rates = self._parse_fred_series(data, series_id)
                
                self.logger.debug(f"Fetched {len(rates)} rates for series {series_id}")
                return rates
                
        except Exception as e:
            self.logger.error(f"Error fetching FRED series {series_id}: {e}")
            return []
    
    def _parse_fred_series(self, data: Dict[str, Any], series_id: str) -> List[FxRate]:
        """Parse dos dados JSON do FRED"""
        rates = []
        
        observations = data.get('observations', [])
        currency_to = self._series_to_currency(series_id)
        
        if not currency_to:
            self.logger.warning(f"Unknown currency for series {series_id}")
            return []
        
        for obs in observations:
            try:
                obs_date = datetime.strptime(obs['date'], '%Y-%m-%d').date()
                value_str = obs['value']
                
                # FRED usa '.' para valores missing
                if value_str == '.':
                    continue
                
                rate_value = float(value_str)
                
                rates.append(FxRate(
                    rate_date=obs_date,
                    currency_from='USD',
                    currency_to=currency_to,
                    rate=rate_value,
                    source='FRED'
                ))
                
            except (ValueError, KeyError) as e:
                self.logger.warning(f"Invalid observation in {series_id}: {obs}")
                continue
        
        return rates
    
    def _series_to_currency(self, series_id: str) -> Optional[str]:
        """Mapear ID da série FRED para código de moeda"""
        mapping = {
            'DEXUSEU': 'EUR',  # US Dollar to Euro
            'DEXUSGB': 'GBP',  # US Dollar to British Pound
            'DEXJPUS': 'JPY',  # Japanese Yen to US Dollar
            'DEXCAUS': 'CAD',  # Canadian Dollar to US Dollar
            'DEXCHUS': 'CHF',  # Swiss Franc to US Dollar
            'DEXAUUS': 'AUD',  # Australian Dollar to US Dollar
        }
        return mapping.get(series_id.upper())

# =============================================================================
# CLIENTE PRINCIPAL (FACTORY)
# =============================================================================

class FxClient:
    """Cliente principal que escolhe fonte baseado em configuração"""
    
    def __init__(self, config: Optional[FxConfig] = None):
        self.config = config or load_fx_config()
        self.logger = logging.getLogger(f"{__name__}.FxClient")
        
        # Instanciar cliente baseado na configuração
        if self.config.source == "ECB":
            self._client = EcbClient(self.config)
        elif self.config.source == "FRED":
            self._client = FredClient(self.config)
        else:
            raise ValueError(f"Unsupported FX source: {self.config.source}")
        
        self.logger.info(f"FxClient initialized with source: {self.config.source}")
    
    async def __aenter__(self):
        await self._client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def get_rates(self, days_back: int = 30) -> FxApiResponse:
        """
        Obter taxas FX da fonte configurada
        
        Args:
            days_back: Dias históricos a obter
            
        Returns:
            FxApiResponse com as taxas
        """
        if isinstance(self._client, EcbClient):
            return await self._client.get_historical_rates(days_back)
        elif isinstance(self._client, FredClient):
            # Séries principais USD-based
            series_ids = ['DEXUSEU', 'DEXUSGB', 'DEXJPUS', 'DEXCAUS']
            return await self._client.get_fx_series(series_ids, days_back)
        else:
            raise NotImplementedError(f"get_rates not implemented for {type(self._client)}")

# =============================================================================
# UTILITÁRIOS
# =============================================================================

def normalize_fx_rates(rates: List[FxRate]) -> List[FxRate]:
    """
    Normalizar taxas para incluir conversões inversas
    
    Args:
        rates: Lista de FxRate
        
    Returns:
        Lista expandida com taxas diretas e inversas
    """
    normalized = list(rates)  # Copiar originais
    
    for rate in rates:
        # Adicionar taxa inversa se não for zero
        if rate.rate > 0:
            inverse_rate = FxRate(
                rate_date=rate.rate_date,
                currency_from=rate.currency_to,
                currency_to=rate.currency_from,
                rate=1.0 / rate.rate,
                source=rate.source
            )
            normalized.append(inverse_rate)
    
    return normalized

def get_supported_currencies() -> Dict[str, List[str]]:
    """Retorna moedas suportadas por fonte"""
    return {
        'ECB': ['EUR', 'USD', 'GBP', 'JPY', 'CAD', 'CHF', 'AUD', 'SEK', 'NOK', 'DKK'],
        'FRED': ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'CHF', 'AUD']
    }