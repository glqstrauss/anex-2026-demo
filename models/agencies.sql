select distinct
    hash(agency_code) as agency_id,
	agency_code,
	agency_name
from {{ ref("stg_civil_servants") }}
