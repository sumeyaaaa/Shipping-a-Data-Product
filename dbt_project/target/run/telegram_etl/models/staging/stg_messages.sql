
  
    

  create  table "etl_db"."raw_raw"."stg_messages__dbt_tmp"
  
  
    as
  
  (
    

with base as (
  select
    raw->>'message_id'     as message_id,
    raw->>'channel'        as channel,
    raw->>'sender_id'      as sender_id,
    (raw->>'message_date')::timestamptz as message_date,
    raw->>'message_text'   as message_text
  from "etl_db"."raw"."messages"
)

select
  message_id::bigint,
  channel,
  sender_id::bigint,
  message_date,
  message_text
from base
  );
  