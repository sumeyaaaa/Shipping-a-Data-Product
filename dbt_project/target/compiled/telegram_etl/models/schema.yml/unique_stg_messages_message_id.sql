
    
    

select
    message_id as unique_field,
    count(*) as n_records

from "etl_db"."raw_raw"."stg_messages"
where message_id is not null
group by message_id
having count(*) > 1


