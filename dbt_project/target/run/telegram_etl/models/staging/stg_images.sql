
  
    

  create  table "etl_db"."raw_raw"."stg_images__dbt_tmp"
  
  
    as
  
  (
    

select
  image_id,
  channel,
  message_id::bigint,
  file_path,
  download_date
from "etl_db"."raw"."images"
  );
  