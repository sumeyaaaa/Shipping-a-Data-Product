
  create view "etl_db"."raw_analytics"."dim_dates__dbt_tmp"
    
    
  as (
    

select distinct
  date_trunc('day', message_date) as day
from "etl_db"."raw_raw"."stg_messages"
  );