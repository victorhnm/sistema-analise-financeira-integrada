# ⚖️ Legal Notice & Compliance
# Integrated Financial Analysis - Aviso Legal e Uso de Dados

## 📋 Declaração de Propósito

Este projeto é desenvolvido para fins **educacionais, de pesquisa e análise financeira**, utilizando exclusivamente dados financeiros **públicos e disponibilizados gratuitamente** por agências governamentais e instituições oficiais.

## 📊 Fontes de Dados e Licenças

### 🇺🇸 SEC EDGAR (Securities and Exchange Commission)

**Fonte**: U.S. Securities and Exchange Commission  
**Endpoint**: `https://data.sec.gov/api/xbrl/companyfacts/`  
**Licença**: **Domínio Público** (U.S. Government Work)  
**Regulamentação**: 17 CFR §232.11 (EDGAR Filer Manual)

#### Compliance Requirements:
- ✅ **User-Agent obrigatório** conforme especificação SEC
- ✅ **Rate limiting**: ≤10 requests/second respeitado
- ✅ **Fair use**: Dados usados para análise, não comercialização
- ✅ **Attribution**: Fonte SEC EDGAR devidamente creditada

#### Terms of Use:
> *"Information obtained from the Commission's EDGAR database is public information. There are no restrictions on its use, provided that the information is not misrepresented."* - SEC EDGAR FAQ

**Referências Legais**:
- [SEC EDGAR Public Dissemination Service](https://www.sec.gov/edgar/filer-information/public-dissemination-service)
- [EDGAR API Documentation](https://www.sec.gov/edgar/sec-api-documentation)

### 🇪🇺 European Central Bank (ECB) - Euro Reference Rates

**Fonte**: European Central Bank  
**Endpoint**: `https://www.ecb.europa.eu/stats/eurofxref/`  
**Licença**: **Livre uso com atribuição**  
**Regulamentação**: EU Regulation (EU) No 1024/2013

#### Terms of Use:
> *"ECB statistical data may be used for any purpose provided that the source is acknowledged."* - ECB Copyright Notice

#### Attribution Required:
```
Source: European Central Bank (ECB)
Euro foreign exchange reference rates
https://www.ecb.europa.eu/stats/eurofxref/
```

### 🇺🇸 FRED (Federal Reserve Economic Data)

**Fonte**: Federal Reserve Bank of St. Louis  
**Endpoint**: `https://api.stlouisfed.org/fred/`  
**Licença**: **Domínio Público** (U.S. Government Work)  
**API Key**: Gratuita com registro

#### Terms of Use:
> *"FRED data is in the public domain and may be used without permission for any purpose."* - FRED Terms of Use

**Referências**:
- [FRED Terms of Use](https://fred.stlouisfed.org/legal/)
- [FRED API Documentation](https://fred.stlouisfed.org/docs/api/fred/)

## 🛡️ Data Processing & Privacy

### Data Collection
- **Escopo**: Somente dados **financeiros públicos** de empresas listadas
- **Período**: Dados históricos a partir de 2010 (limite técnico)
- **Frequência**: Dados trimestrais e anuais conforme reportado pelas empresas
- **Volume**: Limitado por rate limiting das APIs (não bulk download)

### Data Storage
- **Local**: Supabase (PostgreSQL) - servidor na nuvem
- **Retenção**: Dados mantidos para análise histórica e trending
- **Backup**: Conforme políticas do Supabase
- **Acesso**: Read-only para API pública, full access para pipeline ETL

### Data Processing
- **Transformação**: Normalização, conversão de moedas, cálculo de ratios
- **Agregação**: Métricas TTM (Trailing Twelve Months)
- **Quality**: Testes de integridade e consistency checks
- **Lineage**: Dados originais preservados em schema `raw`

### No Personal Data
- ❌ **Nenhum dado pessoal** é coletado ou processado
- ❌ **Não há cookies** ou tracking de usuários
- ❌ **Não há autenticação** ou registration required
- ✅ **Somente dados corporativos públicos** (receita, lucro, ativos, etc.)

## 🔒 Security & Access Control

### API Security
```yaml
Authentication: None (public read-only data)
Rate Limiting: 1000 requests/hour per IP
HTTPS: Required for all connections
CORS: Restricted to PowerBI and approved origins
SQL Injection: Parameterized queries only
```

### Data Access
- **Public API**: Read-only access to aggregated financial metrics
- **Raw Data**: Not exposed via public API
- **Admin Access**: Limited to database schema management
- **Audit Trail**: All API requests logged (no PII)

## 📜 Intellectual Property

### This Project
**License**: MIT License  
**Copyright**: © 2024 Data Engineering Team  
**Repository**: Public GitHub repository  

#### MIT License Summary:
```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies, subject to the following conditions:

- The above copyright notice shall be included in all copies
- The software is provided "as is", without warranty of any kind
```

### Third-Party Dependencies
Todas as dependências Python/JavaScript são de código aberto:
- **FastAPI**: MIT License
- **dbt**: Apache 2.0 License  
- **Pandas**: BSD 3-Clause License
- **PostgreSQL**: PostgreSQL License
- **Power BI Desktop**: Microsoft License (uso gratuito permitido)

## ⚠️ Disclaimers & Limitations

### Financial Data Accuracy
> **⚠️ IMPORTANT DISCLAIMER**: Os dados financeiros são fornecidos "AS-IS" baseados em filings públicos da SEC. Este projeto:
> 
> - ❌ **NÃO é aconselhamento financeiro ou de investimento**
> - ❌ **NÃO garante accuracy ou completude dos dados**
> - ❌ **NÃO substitui due diligence profissional**
> - ✅ **É ferramenta educacional para aprender data engineering**

### Data Timeliness
- **Delay**: Dados SEC podem ter delay de até 90 dias após period end
- **Restated**: Earnings restatements podem não ser capturados imediatamente
- **Market Hours**: FX rates são end-of-day, não intraday
- **Holidays**: Gaps nos dados durante feriados e weekends

### Technical Limitations
- **Beta Software**: Este é um projeto de demonstração, não production-ready
- **Uptime**: Não há SLA ou garantia de availability
- **Support**: Community support only, não há suporte comercial
- **Scalability**: Limitado pelo tier gratuito do Supabase

## 🌍 International Compliance

### GDPR Compliance (EU)
- **No Personal Data**: Projeto não processa dados pessoais → GDPR não aplicável
- **Corporate Data**: Dados de empresas públicas não são considerados personal data
- **Analytics**: Não há tracking de usuários individuais

### CCPA Compliance (California)
- **No Consumer Data**: Não há coleta de dados de consumidores
- **Business Purpose**: Uso exclusivamente para análise financeira educacional

### SOX Compliance (Sarbanes-Oxley)
- **Public Data Only**: Uso de dados já auditados e públicos
- **No Material Information**: Não há acesso a material non-public information

## 🚨 Prohibited Uses

### ❌ Não Permitido:
- **Insider Trading**: Usar para decisões baseadas em material non-public information
- **Market Manipulation**: Disseminar informações falsas ou enganosas
- **Scraping Abusivo**: Exceder rate limits ou sobrecarregar APIs
- **Commercial Resale**: Vender acesso aos dados sem transformação significativa
- **Reverse Engineering**: Tentar identificar estratégias proprietárias
- **Regulatory Violation**: Qualquer uso que viole securities laws

### ✅ Usos Permitidos:
- **Educational**: Aprender data engineering e análise financeira
- **Research**: Pesquisa acadêmica e estudos de mercado
- **Personal Portfolio**: Análise de investimentos pessoais
- **Professional Development**: Building skills em data stack moderno
- **Open Source**: Contribuir com melhorias para a comunidade

## 📞 Contact & Reporting

### Legal Inquiries
Para questões legais ou de compliance:
- **Email**: legal@[your-domain].com
- **GitHub Issues**: Para questões técnicas/license
- **Response Time**: 5-7 business days para legal matters

### Reporting Violations
Para reportar uso inadequado:
- **Security Issues**: security@[your-domain].com  
- **DMCA Claims**: dmca@[your-domain].com
- **Abuse**: abuse@[your-domain].com

### Data Subject Rights
Como este projeto não coleta dados pessoais, não há data subject rights aplicáveis. No entanto, se você acredita que seus dados estão sendo processados incorretamente, entre em contato.

## 📚 Additional Resources

### Regulatory References
- [SEC EDGAR Terms of Use](https://www.sec.gov/edgar)
- [ECB Statistical Data Policy](https://www.ecb.europa.eu/stats/html/index.en.html)
- [FRED Terms and Conditions](https://fred.stlouisfed.org/legal/)

### Financial Regulations
- [Securities Act of 1933](https://www.sec.gov/answers/about-lawsshtml.html#secact1933)
- [Securities Exchange Act of 1934](https://www.sec.gov/answers/about-lawsshtml.html#secexact1934)  
- [Sarbanes-Oxley Act of 2002](https://www.sec.gov/answers/about-lawsshtml.html#sox2002)

### Data Protection
- [GDPR Full Text](https://gdpr-info.eu/)
- [CCPA Overview](https://oag.ca.gov/privacy/ccpa)

## 🔄 Updates & Changes

This legal notice may be updated periodically. Major changes will be:
- **Announced**: Via GitHub releases and README updates  
- **Effective Date**: 30 days after publication for material changes
- **Backwards Compatible**: No retroactive changes to data processing

**Version History**:
- v1.0 (2024-08-23): Initial legal notice
- Last Updated: 2024-08-23

---

## 📝 Acknowledgment

By using this project, you acknowledge that you have read, understood, and agree to comply with this Legal Notice and all applicable laws and regulations.

**This project is provided for educational purposes only and does not constitute financial advice.**

---

*For the most current version of this notice, please visit: [GitHub Repository](https://github.com/seu-usuario/integrated-financial-analysis)*

*Legal Notice Version: 1.0 | Effective Date: August 23, 2024*