{{ config(materialized='view') }}

select distinct
  date_trunc('day', message_date) as day
from {{ ref('stg_messages') }}
