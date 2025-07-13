

select
  m.message_id,
  m.channel,
  d.day        as message_day,
  m.sender_id,
  length(m.message_text) as text_length
from "etl_db"."raw_raw"."stg_messages" as m
join "etl_db"."raw_analytics"."dim_dates"      as d on date_trunc('day', m.message_date) = d.day