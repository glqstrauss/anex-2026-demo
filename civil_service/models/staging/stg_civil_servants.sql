from {{ source("nyc_open_data", "civil_list") }}
select
	dpt as agency_code,
	_name as employee_name,
	agency_name,
	ttl as title_code,
	pc as pay_class,
	regexp_replace(sal_rate, '[$,]','', 'g')::double as salary_rate
