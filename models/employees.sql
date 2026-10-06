select
    -- Employees are not uniquely identifiable in the Civil List dataset,
    -- but this is a reasonable approximation for the purposes of this demo.
    hash(*columns(*)) as employee_id,
    agency_code,
    title_code,
    pay_class,
    salary_rate
from {{ ref("stg_civil_servants") }}