{{ config(materialized='table') }}

select
  m.message_id,
  m.channel,
  d.day        as message_day,
  m.sender_id,
  length(m.message_text) as text_length
from {{ ref('stg_messages') }} as m
join {{ ref('dim_dates') }}      as d on date_trunc('day', m.message_date) = d.day
