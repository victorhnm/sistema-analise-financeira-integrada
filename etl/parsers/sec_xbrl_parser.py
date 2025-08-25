"""
Parser para dados XBRL da SEC
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SECXBRLParser:
    """Parser para dados XBRL/JSON da SEC"""
    
    def __init__(self):
        # Mapeamento de conceitos US-GAAP
        self.concept_mapping = {
            'Revenues': 'revenue',
            'GrossProfit': 'gross_profit', 
            'OperatingIncomeLoss': 'operating_income',
            'NetIncomeLoss': 'net_income',
            'Assets': 'total_assets',
            'StockholdersEquity': 'shareholders_equity',
        }
        
    def parse_company_facts(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse company facts JSON para formato tabular"""
        if not raw_data or 'facts' not in raw_data:
            return []
            
        company_info = {
            'cik': raw_data.get('cik'),
            'company_name': raw_data.get('entityName'),
            'ticker': raw_data.get('tradingSymbol', '').upper()
        }
        
        facts = []
        us_gaap_facts = raw_data.get('facts', {}).get('us-gaap', {})
        
        for concept, concept_data in us_gaap_facts.items():
            if concept not in self.concept_mapping:
                continue
                
            canonical_metric = self.concept_mapping[concept]
            units = concept_data.get('units', {})
            
            for unit, values in units.items():
                for value_entry in values:
                    fact = self._parse_fact_entry(
                        company_info, concept, canonical_metric, unit, value_entry
                    )
                    if fact:
                        facts.append(fact)
        
        logger.info(f"Parsed {len(facts)} facts for {company_info.get('company_name')}")
        return facts
    
    def _parse_fact_entry(self, company_info, concept, canonical_metric, unit, value_entry):
        """Parse uma entrada individual"""
        try:
            end_date = value_entry.get('end')
            start_date = value_entry.get('start') 
            value = value_entry.get('val')
            form = value_entry.get('form', '')
            fiscal_year = value_entry.get('fy')
            fiscal_period = value_entry.get('fp', '')
            
            if not end_date or value is None:
                return None
            
            # Parse dates
            period_end = datetime.strptime(end_date, '%Y-%m-%d').date()
            period_start = None
            if start_date:
                period_start = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            # Extract fiscal year from end date if not provided
            if not fiscal_year:
                fiscal_year = period_end.year
                
            return {
                'cik': company_info['cik'],
                'company_name': company_info['company_name'],
                'ticker': company_info['ticker'],
                'concept': concept,
                'canonical_metric': canonical_metric,
                'statement': 'BalanceSheet' if concept in ['Assets', 'StockholdersEquity'] else 'IncomeStatement',
                'period_start': period_start,
                'period_end': period_end,
                'fiscal_year': int(fiscal_year),
                'fiscal_period': fiscal_period,
                'form': form,
                'value': float(value),
                'currency': 'USD' if 'USD' in unit else unit.split('-')[0] if '-' in unit else 'USD',
                'unit': unit
            }
        except Exception as e:
            logger.error(f"Erro ao parse fact: {e}")
            return None
