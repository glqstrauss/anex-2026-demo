from {{ source("nyc_open_data", "civil_list") }}
select
	lpad(dpt::string, 3, '0') as agency_code,
	agency_name as agency_name,
	_name as employee_name,
	ttl as title_code,
	pc as pay_class,
	regexp_replace(sal_rate, '[$,]','', 'g')::double as pay_rate
