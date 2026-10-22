{% macro timestamp_from_seconds(column_name) -%}
  {{ return(adapter.dispatch('timestamp_from_seconds', 'fraud_analytics')(column_name)) }}
{%- endmacro %}

{% macro duckdb__timestamp_from_seconds(column_name) -%}
  timestamp '2013-09-01 00:00:00' + ({{ column_name }} * interval '1 second')
{%- endmacro %}

{% macro bigquery__timestamp_from_seconds(column_name) -%}
  timestamp_add(timestamp('2013-09-01 00:00:00'), interval cast({{ column_name }} as int64) second)
{%- endmacro %}

{% macro default__timestamp_from_seconds(column_name) -%}
  timestamp '2013-09-01 00:00:00' + ({{ column_name }} * interval '1 second')
{%- endmacro %}

