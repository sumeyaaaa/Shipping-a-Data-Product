{{ config(
    materialized='table',
    schema='raw'
) }}

select
  image_id,
  channel,
  message_id::bigint,
  file_path,
  download_date
from {{ source('raw', 'images') }}
