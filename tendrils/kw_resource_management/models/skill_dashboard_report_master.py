from odoo import models, fields, api
from odoo import tools


class WEorkForceAnalyticReport(models.Model):
    _name = "skill_dashboard_analytics_report"
    _description = "Skill Dashboard analytic Report"
    _auto = False

    emp_id = fields.Many2one('hr.employee', string="Employee")
    emp_name = fields.Char('Employee Name')
    designation = fields.Many2one('hr.job', string="Designation")
    emp_location = fields.Many2one('kw_res_branch', string="Location")
    emp_role = fields.Many2one('kwmaster_role_name', string="Emp Role")
    emp_category = fields.Many2one('kwmaster_category_name', string="Emp Category")
    employement_type = fields.Many2one('kwemp_employment_type', string="Employement Type")
    sbu_type = fields.Selection(string='Resource Type',selection=[('sbu', 'SBU'), ('horizontal', 'Horizontal')])
    sbu_master_id = fields.Many2one('kw_sbu_master', string="SBU")
    primary_skill = fields.Many2one('kw_skill_master', string="Primary Skill")
    secondary_skill = fields.Many2one('kw_skill_master', string="Secondary Skill")
    tertiarry_skill = fields.Many2one('kw_skill_master', string="Tertiarry Skill")
    primary_skill_type = fields.Char("Skill Type")
    secondary_skill_type = fields.Char("Skill Type")
    tertiary_skill_type = fields.Char("Skill Type")   
    certification_course_1 = fields.Many2one('kwmaster_stream_name',"Certification 1")
    certification_course_2 = fields.Many2one('kwmaster_stream_name',"Certification 2")
    certification_course_3 = fields.Many2one('kwmaster_stream_name',"Certification 3")
    certification_course_4 = fields.Many2one('kwmaster_stream_name',"Certification 4")
    certification_course_5 = fields.Many2one('kwmaster_stream_name',"Certification 5")
    club_role = fields.Char("Club Role")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            WITH crt AS (
                    SELECT 
                        emp_id,
                        stream_id,
                        ROW_NUMBER() OVER (PARTITION BY emp_id) AS certification_number
                    FROM kwemp_educational_qualification
                    WHERE  course_id=6
                )

                SELECT
                    row_number() OVER() AS id,
                    hr.id AS emp_id,
                    hr.name AS emp_name,
                    hr.job_id AS designation,
                    hr.emp_role AS emp_role,
                    hr.emp_category AS emp_category,
                    hr.employement_type AS employement_type,
                    hr.sbu_type AS sbu_type,
                    hr.sbu_master_id AS sbu_master_id,
                    hr.job_branch_id AS emp_location,
                    skl.primary_skill_id AS primary_skill,
                    CASE WHEN skl.primary_skill_id IS NOT NULL THEN 'Primary' ELSE NULL END AS primary_skill_type,
                    skl.secondary_skill_id AS secondary_skill,
                    CASE WHEN skl.secondary_skill_id IS NOT NULL THEN 'Secondary' ELSE NULL END AS secondary_skill_type,
                    skl.tertial_skill_id AS tertiarry_skill,
                    CASE WHEN skl.tertial_skill_id IS NOT NULL THEN 'Tertiary' ELSE NULL END AS tertiary_skill_type,
					CASE 
						WHEN hr.job_id IN (select id from hr_job where name in ('Data Engineer', 'Programmer', 'Programmer Analyst','Research Analyst','Software Engineer','Sr. Data Analyst','Sr. Data Engineer','Sr. Database Analyst','Sr. Programmer Analyst','Sr. Software Engineer')) THEN 'Coder/Programmer'
						WHEN hr.job_id IN (select id from hr_job where name in('Data Scientist', 'Module Lead', 'Project Leader','Sr. Project leader','Sr. Tech Lead','Tech Lead','Technical Architect')) THEN 'Leader/Manager'
						WHEN hr.job_id IN (select id from hr_job where name in('Associate Project Manager', 'Associate VP (Projects)', 'Chief Digital Officer','Chief Service Delivery Officer','Chief Technology Officer','Program Manager','Project Manager','Sr. Project Manager','VP-Project Management')) THEN 'Project Manager'
						WHEN hr.job_id IN (select id from hr_job where name in('Business Analyst (Projects)', 'Associate Business Analyst', 'Business Analyst','Lead Business Analyst','Sr. Business Analyst'))THEN 'Business Analyst'
						ELSE (select name from hr_job where id=hr.job_id)
					END AS club_role,
                    cr.stream_id AS certification_course_1,
                    cr1.stream_id AS certification_course_2,
                    cr2.stream_id AS certification_course_3,
                    cr3.stream_id AS certification_course_4,
                    cr4.stream_id AS certification_course_5

                FROM hr_employee hr
                LEFT JOIN resource_skill_data skl ON hr.id = skl.employee_id
                LEFT JOIN crt cr ON cr.emp_id = hr.id AND cr.certification_number = 1
                LEFT JOIN crt cr1 ON cr1.emp_id = hr.id AND cr1.certification_number = 2
                LEFT JOIN crt cr2 ON cr2.emp_id = hr.id AND cr2.certification_number = 3
                LEFT JOIN crt cr3 ON cr3.emp_id = hr.id AND cr3.certification_number = 4
                LEFT JOIN crt cr4 ON cr4.emp_id = hr.id AND cr4.certification_number = 5

                WHERE hr.active = true 
                    AND hr.department_id in (SELECT id FROM hr_department where code='BSS')
                    AND hr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')
            )""" % (self._table))
   