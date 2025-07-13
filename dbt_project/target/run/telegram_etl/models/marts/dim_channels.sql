
  create view "etl_db"."raw_analytics"."dim_channels__dbt_tmp"
    
    
  as (
    

select distinct
  channel
from "etl_db"."raw_raw"."stg_messages"
  );