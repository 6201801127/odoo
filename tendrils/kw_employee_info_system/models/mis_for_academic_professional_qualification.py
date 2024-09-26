from string import digits
from odoo import models, fields, api
from odoo import tools


class MisreportEmployee(models.Model):
    _name = "hr.mis.academic.and.professional.qualification"
    _description = "MIS Report for Academic and Professional Qualification"
    _auto = False

    emp_id = fields.Many2one('hr.employee', string="Employee ID")
    name = fields.Char(string="Employee Name", related='emp_id.name')
    emp_code = fields.Char(string="Employee Code", related='emp_id.emp_code')
    department_id = fields.Many2one('hr.department', string="Department")
    job_id = fields.Many2one('hr.job', string="Designation")
    job_branch_id = fields.Many2one('kw_res_branch', string="Work Location")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],
                              string="Gender", groups="base.group_user")
    previous_company_experience = fields.Char(string="Previous Company Experience")
    csm_experience = fields.Char(string="CSM Experience")
    total_experience = fields.Char(string="Total Experience")

    gr_stream = fields.Many2one('kwmaster_stream_name', string="Graduation Stream")
    gr_specialization = fields.Char(string='Graduation Specialization')
    gr_year = fields.Char(string='Graduation Year')

    pg_stream = fields.Many2one('kwmaster_stream_name', string="PG Stream")
    pg_specialization = fields.Char(string='PG Specialization')
    pg_year = fields.Char(string='PG Year')
    
    prof_stream_1 = fields.Many2one('kwmaster_stream_name', string="Prof 1 Stream")
    prof_specialization_1 = fields.Many2one('kwmaster_institute_name',string='Prof 1 Vendor')
    prof_year_1 = fields.Char(string='Prof 1 Year')
    
    prof_stream_2 = fields.Many2one('kwmaster_stream_name', string="Prof 2 Stream")
    prof_specialization_2 = fields.Many2one('kwmaster_institute_name',string='Prof 2 Vendor')
    prof_year_2 = fields.Char(string='Prof 2 Year')
    
    prof_stream_3 = fields.Many2one('kwmaster_stream_name', string="Prof 3 Stream")
    prof_specialization_3 = fields.Many2one('kwmaster_institute_name',string='Prof 3 Vendor')
    prof_year_3 = fields.Char(string='Prof 3 Year')
    
    prof_stream_4 = fields.Many2one('kwmaster_stream_name', string="Prof 4 Stream")
    prof_specialization_4 = fields.Many2one('kwmaster_institute_name',string='Prof 4 Vendor')
    prof_year_4 = fields.Char(string='Prof 4 Year')

    cert_1_stream = fields.Many2one('kwmaster_stream_name', string="Certification 1 Name")
    cert_1_vendor_id = fields.Many2one('kwmaster_institute_name', string="Certificate 1 Vendor")
    cert_1_year = fields.Char(string='Certificate 1 Year')

    cert_2_stream = fields.Many2one('kwmaster_stream_name', string="Certification 2 Name")
    cert_2_vendor_id = fields.Many2one('kwmaster_institute_name', string="Certificate 2 Vendor")
    cert_2_year = fields.Char(string='Certificate 2 Year')

    cert_3_stream = fields.Many2one('kwmaster_stream_name', string="Certification 3 Name")
    cert_3_vendor_id = fields.Many2one('kwmaster_institute_name', string="Certificate 3 Vendor")
    cert_3_year = fields.Char(string='Certificate 3 Year')

    cert_4_stream = fields.Many2one('kwmaster_stream_name', string="Certification 4 Name")
    cert_4_vendor_id = fields.Many2one('kwmaster_institute_name', string="Certificate 4 Vendor")
    cert_4_year = fields.Char(string='Certificate 4 Year')

    cert_5_stream = fields.Many2one('kwmaster_stream_name', string="Certification 5 Name")
    cert_5_vendor_id = fields.Many2one('kwmaster_institute_name', string="Certificate 5 Vendor")
    cert_5_year = fields.Char(string='Certificate 5 Year')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
with gr_edu as (
    SELECT emp_id,stream_id, passing_year,
    (SELECT string_agg(name::text,', ') FROM kwmaster_specializations 
     WHERE id in (SELECT kwmaster_specializations_id 
			  FROM kwemp_educational_qualification_kwmaster_specializations_rel 
			  WHERE kwemp_educational_qualification_id = k.id)) as specializations
FROM kwemp_educational_qualification AS k 
WHERE k.course_id=3),

pg_edu as (
    SELECT emp_id,stream_id, passing_year,
    (SELECT string_agg(name::text,', ') FROM kwmaster_specializations 
     WHERE id in (SELECT kwmaster_specializations_id 
			  FROM kwemp_educational_qualification_kwmaster_specializations_rel 
			  WHERE kwemp_educational_qualification_id = k.id)) as specializations
    FROM kwemp_educational_qualification AS k 
    WHERE k.course_id=4),
prof_edu as (SELECT emp_id, row_num, stream_id, university_name, passing_year FROM
	(SELECT ROW_NUMBER() OVER(PARTITION BY emp_id) AS row_num, stream_id, emp_id, course_id, university_name, passing_year 
	FROM kwemp_educational_qualification 
	WHERE course_id=5) Y),

cert as (SELECT emp_id, row_num, stream_id, university_name, passing_year FROM
	(SELECT ROW_NUMBER() OVER(PARTITION BY emp_id) AS row_num, stream_id, emp_id, course_id, university_name, passing_year 
	FROM kwemp_educational_qualification 
	WHERE course_id=6) X)


SELECT *,
-- previous_company_experience
case when emp.previous_company_exp is not null then
concat(div(emp.previous_company_exp, 12)::varchar, 
'.', 
CAST(mod(COALESCE(emp.previous_company_exp,0), 12)::varchar as varchar)) else '0' end AS previous_company_experience,

-- csm_experience
case when emp.date_of_joining is not null then 		
concat(div(emp.csm_exp, 12)::varchar, 
'.', 
CAST(mod(COALESCE(emp.csm_exp,0), 12)::varchar as varchar)) else '0' end AS csm_experience,

-- total_experience
concat(div((COALESCE(emp.csm_exp,0) + COALESCE(emp.previous_company_exp,0)), 12)::varchar, 
'.', 
CAST(mod((COALESCE(emp.csm_exp,0) + COALESCE(emp.previous_company_exp,0)), 12)::varchar as varchar)) AS total_experience

FROM (SELECT  row_number() over(order by name asc) AS id,

hr.id AS emp_id,  
hr.department_id, 
hr.job_id, 
hr.emp_project_id AS project_id, 
hr.job_branch_id, 
hr.gender,
hr.date_of_joining,

(select 
sum(date_part('year', AGE(x.effective_to, x.effective_from)) * 12 + date_part('month', AGE(x.effective_to, x.effective_from)))::numeric from kwemp_work_experience AS x where x.emp_id = hr.id group by x.emp_id )  AS previous_company_exp,

case when hr.date_of_joining is not null then
(date_part('year', AGE(CURRENT_DATE, hr.date_of_joining)) * 12 + date_part('month', AGE(CURRENT_DATE, hr.date_of_joining)))::numeric else 0 end  AS csm_exp, 

-- Graduation data
gr_edu.stream_id AS gr_stream, gr_edu.passing_year AS gr_year, gr_edu.specializations AS gr_specialization,

-- PG data
pg_edu.stream_id AS pg_stream, pg_edu.passing_year AS pg_year, pg_edu.specializations AS pg_specialization,

-- Prof 1 data
prof_edu_1.stream_id AS prof_stream_1, prof_edu_1.passing_year AS prof_year_1, prof_edu_1.university_name AS prof_specialization_1,

-- Prof 2 data
prof_edu_2.stream_id AS prof_stream_2, prof_edu_2.passing_year AS prof_year_2, prof_edu_2.university_name AS prof_specialization_2,

-- Prof 3 data
prof_edu_3.stream_id AS prof_stream_3, prof_edu_3.passing_year AS prof_year_3, prof_edu_3.university_name AS prof_specialization_3,

-- Prof 4 data
prof_edu_4.stream_id AS prof_stream_4, prof_edu_4.passing_year AS prof_year_4, prof_edu_4.university_name AS prof_specialization_4,


-- Certification 1 data
cert1.stream_id cert_1_stream, cert1.university_name cert_1_vendor_id, cert1.passing_year cert_1_year,

-- Certification 2 data
cert2.stream_id cert_2_stream, cert2.university_name cert_2_vendor_id, cert2.passing_year cert_2_year, 

-- Certification 3 data
cert3.stream_id cert_3_stream, cert3.university_name cert_3_vendor_id, cert3.passing_year cert_3_year, 

-- Certification 4 data
cert4.stream_id cert_4_stream, cert4.university_name cert_4_vendor_id, cert4.passing_year cert_4_year, 

-- Certification 5 data
cert5.stream_id cert_5_stream, cert5.university_name cert_5_vendor_id, cert5.passing_year cert_5_year

FROM hr_employee hr
LEFT JOIN gr_edu on gr_edu.emp_id=hr.id
LEFT JOIN pg_edu on pg_edu.emp_id=hr.id 

LEFT JOIN prof_edu AS prof_edu_1 on prof_edu_1.emp_id=hr.id AND prof_edu_1.row_num=1
LEFT JOIN prof_edu AS prof_edu_2 on prof_edu_2.emp_id=hr.id AND prof_edu_2.row_num=2
LEFT JOIN prof_edu AS prof_edu_3 on prof_edu_3.emp_id=hr.id AND prof_edu_3.row_num=3
LEFT JOIN prof_edu AS prof_edu_4 on prof_edu_4.emp_id=hr.id AND prof_edu_4.row_num=4


LEFT JOIN cert AS cert1 on cert1.emp_id=hr.id AND cert1.row_num=1
LEFT JOIN cert AS cert2 on cert2.emp_id=hr.id AND cert2.row_num=2
LEFT JOIN cert AS cert3 on cert3.emp_id=hr.id AND cert3.row_num=3
LEFT JOIN cert AS cert4 on cert4.emp_id=hr.id AND cert4.row_num=4
LEFT JOIN cert AS cert5 on cert5.emp_id=hr.id AND cert5.row_num=5

WHERE hr.active is true AND hr.employement_type != 5
ORDER BY name ASC) AS emp

        )"""
        # print("tracker quey",query)
        self.env.cr.execute(query)
