from {{ source("nyc_open_data", "civil_service_titles") }}
select
	title as title_code,
	descr as title_desc,
	std_hrs as standard_hours,
	asg_lvl as assignment_level,
	union_cd as union_code,
	union_descr as union_description,
	barg_unit as bargaining_unit,
	barg_descr as bargaining_description,
	min_rate,
	max_rate,
	investigation_before_appointment as requires_investigation
