select
  title_code,
  title_desc,
  union_code,
  standard_hours,
  min_salary_rate,
  max_salary_rate,
from {{ ref("stg_civil_service_titles") }}