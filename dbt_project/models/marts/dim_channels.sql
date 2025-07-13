{{ config(materialized='view') }}

select distinct
  channel
from {{ ref('stg_messages') }}
