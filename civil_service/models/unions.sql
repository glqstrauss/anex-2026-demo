select distinct
  union_code,
  union_desc,
  bargaining_unit_code,
  bargaining_unit_desc
from {{ ref("stg_civil_service_titles") }}
