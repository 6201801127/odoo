from odoo import models, fields, api
from odoo import tools


class WorkForceAnalyticReport(models.Model):
    _name = "work_force_analytics_report"
    _description = "Work Force Analytic Report"
    _auto = False

    emp_id = fields.Many2one('hr.employee', string="Employee")
    emp_name = fields.Char('Employee Name')
    emp_code = fields.Char('Employee Code')
    department_id = fields.Many2one('hr.department', string="Department")
    designation_id = fields.Many2one('hr.job', string="Designation")
    job_branch_id = fields.Many2one('kw_res_branch', string="Location")
    emp_role = fields.Many2one('kwmaster_role_name', string="Emp Role")
    emp_category = fields.Many2one('kwmaster_category_name', string="Emp Category")
    employement_type = fields.Many2one('kwemp_employment_type', string="Employement Type")
    sbu_type = fields.Selection(string='Resource Type',selection=[('sbu', 'SBU'), ('horizontal', 'Horizontal')])
    sbu_master_id = fields.Many2one('kw_sbu_master', string="SBU")
    primary_skill_id = fields.Many2one('kw_skill_master', string="Skill")
    emp_company_id = fields.Many2one('res.company')
    club_role = fields.Char("Club Role")
    db_role = fields.Char("Database Role")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW {table} AS (
                SELECT row_number() over() AS id, 
            hr.id as emp_id,
            hr.name as emp_name,
            hr.emp_code as emp_code,
            hr.department_id as department_id,
            hr.job_id as designation_id,
            hr.job_branch_id as job_branch_id,
            hr.emp_role as emp_role,
            hr.emp_category as emp_category,
            hr.employement_type as employement_type,
            hr.sbu_type as sbu_type,
            hr.sbu_master_id as sbu_master_id,
            hr.company_id as emp_company_id,
            CASE 
                WHEN hr.job_id IN (select id from hr_job where name in ('Data Engineer', 'Programmer', 'Programmer Analyst','Research Analyst','Software Engineer','Sr. Data Analyst','Sr. Data Engineer','Sr. Database Analyst','Sr. Programmer Analyst','Sr. Software Engineer')) THEN 'Coder/Programmer'
                WHEN hr.job_id IN (select id from hr_job where name in('Data Scientist', 'Module Lead', 'Project Leader','Sr. Project leader','Sr. Tech Lead','Tech Lead','Technical Architect')) THEN 'Leader/Manager'
                WHEN hr.job_id IN (select id from hr_job where name in('Associate Project Manager', 'Associate VP (Projects)', 'Chief Digital Officer','Chief Service Delivery Officer','Chief Technology Officer','Program Manager','Project Manager','Sr. Project Manager','VP-Project Management')) THEN 'Project Manager'
                WHEN hr.job_id IN (select id from hr_job where name in('Business Analyst (Projects)', 'Associate Business Analyst', 'Business Analyst','Lead Business Analyst','Sr. Business Analyst'))THEN 'Business Analyst'
                ELSE (select name from hr_job where id=hr.job_id)
            END AS club_role,
            CASE 
				WHEN kcn.code = 'DBA' THEN 'DBA'
				WHEN rsd.primary_skill_id IN (SELECT id FROM kw_skill_master WHERE name ILIKE '%sql%') THEN 'DB Developer'
			END AS db_role,
            rsd.primary_skill_id as primary_skill_id
            
            from hr_employee hr 
            left join resource_skill_data rsd on rsd.employee_id = hr.id
            LEFT JOIN kwmaster_category_name kcn ON kcn.id = hr.emp_category
            where hr.active=true
            )
        """.format(table=self._table))
