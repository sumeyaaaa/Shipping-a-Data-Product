
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select image_id
from "etl_db"."raw_raw"."stg_images"
where image_id is null



  
  
      
    ) dbt_internal_test