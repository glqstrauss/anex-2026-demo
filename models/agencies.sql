select distinct
	agency_code,
	agency_name
from {{ ref("stg_civil_servants") }}
