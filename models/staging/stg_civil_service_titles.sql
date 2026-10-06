from {{ source("nyc_open_data", "civil_service_titles") }}
select
	title as title_code,
	descr as title_desc,
	std_hrs as standard_hours,
	asg_lvl as assignment_level,
	union_cd as union_code,
	union_descr as union_desc,
	barg_unit as bargaining_unit_code,
	barg_descr as bargaining_unit_desc,
	min_rate as min_salary_rate,
	max_rate as max_salary_rate,
	investigation_before_appointment as investigation_before_appointment
