

select distinct
  date_trunc('day', message_date) as day
from "etl_db"."raw_raw"."stg_messages"