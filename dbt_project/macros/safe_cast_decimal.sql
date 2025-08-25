-- safe_cast_decimal.sql
-- Macro para conversão segura de strings para decimal
-- Trata valores null, vazios e não-numéricos

{% macro safe_cast_decimal(field, precision=20, scale=2) %}
    case 
        when {{ field }} is null then null
        when trim({{ field }}) = '' then null
        when {{ field }} ~ '^-?[0-9]+\.?[0-9]*$' then
            {{ field }}::decimal({{ precision }}, {{ scale }})
        else null
    end
{% endmacro %}