-- fx_convert.sql
-- Macro para conversão de moedas usando taxas FX
-- Parâmetros: valor, moeda_origem, moeda_destino, data_referencia

{% macro fx_convert(amount_field, from_currency, to_currency, reference_date, fx_table='stg_fx_rates') %}
    
    case 
        when {{ from_currency }} = {{ to_currency }} then {{ amount_field }}
        when {{ amount_field }} is null then null
        else (
            select {{ amount_field }} * coalesce(fx.rate, 1.0)
            from {{ ref(fx_table) }} fx
            where fx.currency_from = {{ from_currency }}
            and fx.currency_to = {{ to_currency }}
            and fx.rate_date = (
                select max(fx2.rate_date)
                from {{ ref(fx_table) }} fx2
                where fx2.currency_from = {{ from_currency }}
                and fx2.currency_to = {{ to_currency }}
                and fx2.rate_date <= {{ reference_date }}
                and fx2.rate_date >= {{ reference_date }} - interval '7 days'
            )
            limit 1
        )
    end

{% endmacro %}