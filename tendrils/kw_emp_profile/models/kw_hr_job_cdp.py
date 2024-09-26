from odoo import models, fields, api
from odoo.exceptions import ValidationError


class hr_job_cdp(models.Model):
    _name = "hr_job_cdp_model"
    _description = "hr job cdp model"
    _rec_name = "department"
    _order = "sequence"

    sequence = fields.Integer(string="sequence")
    category_id = fields.Many2one('hr_job_cdp_category_master', string="Category", store=True)
    name = fields.Char(string="Name")
    department = fields.Char(string='Department')
    level = fields.Char(string='Level')
    grade = fields.Char(string="Grade")
    designation = fields.Char(string='Designation')
    years = fields.Char(string='Years')


class my_cdp_view(models.Model):
    _name = 'cdp_query_views_'
    _description = 'CDP Query View'
    _auto = False
    _order = 'cdp_model_name ASC, sequence ASC'

    employee_profile_id = fields.Many2one('kw_emp_profile', string='Employee Profile')
    cdp_model_name = fields.Char(string='CDP Model Name', readonly=True)
    department = fields.Char(string='Department', readonly=True)
    level = fields.Char(string='Level', readonly=True)
    grade = fields.Char(string='Grade', readonly=True)
    designation_id = fields.Integer(string='Designation ID', readonly=True)
    designation = fields.Char(string='Designation', readonly=True)
    years = fields.Char(string='Years', readonly=True)
    sequence = fields.Integer(string="Sequence", readonly=True)

    def init(self):
        # self_user = self.env.user.employee_ids.id
        self._cr.execute("""
            CREATE OR REPLACE VIEW cdp_query_views_ AS (
             SELECT 
                ROW_NUMBER() OVER () AS id, 
                cdp_model.sequence, 
                emp_profile.id AS employee_profile_id,
                cdp_model.name AS cdp_model_name,
                cdp_model.department,
                cdp_model.level,
                cdp_model.grade, 
                designations.id AS designation_id,
                cdp_model.designation,  
                cdp_model.years
            FROM hr_job_cdp_model AS cdp_model
            JOIN hr_job_cdp_category_master AS category_master ON cdp_model.category_id = category_master.id
            JOIN job_cdp_category_master_rel AS rel ON category_master.id = rel.hr_job_cdp_category_master_id
            JOIN hr_job AS designations ON rel.hr_job_id = designations.id
            JOIN kw_emp_profile AS emp_profile ON TRUE
            GROUP BY emp_profile.id, cdp_model.name, cdp_model.department, cdp_model.level, cdp_model.grade, 
                cdp_model.sequence, designation_id, cdp_model.years,cdp_model.designation, category_master.id
            ORDER BY emp_profile.id, category_master.id	
            )
        """)
