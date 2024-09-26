from odoo import models, fields, api, tools


class kw_skill_employee_expertise(models.Model):
    _name = 'kw_employee_skill_expertise'
    _description = "A model to view employee skill"
    _rec_name = 'employee_name'

    emp_id = fields.Many2one('hr.employee', string="Employee Name", required=True)
    employee_name = fields.Char(string="Employee Name", related="emp_id.name", store=True)
    employee_code = fields.Char(string="Code", related="emp_id.emp_code", store=True)
    deg_id = fields.Many2one('hr.job', string='Designation', related="emp_id.job_id", store=True)
    department_id = fields.Many2one('hr.department', string="Department", related='emp_id.department_id',
                                    store=True)
    emp_work_email = fields.Char(string="Work mail", related="emp_id.work_email", store=True)

    primary_skill_id = fields.Many2one('kw_skill_master', string="Primary Skill")
    primary_skill = fields.Text(string="Other Primary Skill")
    secondary_skill_id = fields.Many2one('kw_skill_master', string="Secondary Skill")
    secondary_skill = fields.Text(string="Other Secondary Skill")
    tertiary_skill_id = fields.Many2one('kw_skill_master', string="Tertiary Skill")
    tertiary_skill = fields.Text(string="Other Tertiary Skill")

    is_submitted = fields.Boolean(string="submitted")
    emp_location = fields.Many2one("kw_res_branch", string="Location", related="emp_id.job_branch_id")
    reopen_survey = fields.Boolean(string="Reopen Survey")

    @api.model
    def _get_employee_skill_url(self, user_id):
        emp_skill_url = f"/employee-skill-expertise"
        return emp_skill_url
    
    
    
class ReopenSurveyskill(models.TransientModel):
    _name = "survey_reopened_wizard"
    _description = "survey_reopened_wizard"

    @api.model
    def default_get(self, fields):
        res = super(ReopenSurveyskill, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])

        res.update({
            'employee_ids': active_ids,
        })
        return res

    employee_ids = fields.Many2many(string='Employee',
        comodel_name='kw_employee_skill_expertise',
        relation='reopen_skill_rel',
        column1='reopen_wizard_id',
        column2='survey_reopen_id',)  
    
    reopend_bool = fields.Boolean(string="Reopen Survey")  
    
    def get_reopen_survey(self):
        for rec in self.employee_ids:
            skill_reopen = self.env['kw_employee_skill_expertise'].search([('emp_id','=',rec.emp_id.id)])
            if skill_reopen:
                skill_reopen.reopen_survey = True
    
