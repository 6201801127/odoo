from odoo import models, fields, api


class kw_kt_tag(models.Model):
    _name = "kw_kt_tag"
    _description = "KT Tag"
    _rec_name = 'project_id'

    project_id = fields.Many2one('project.project', string="Project Name", required=True)
    dept_id = fields.Many2one('hr.department', string="Department")
    division = fields.Many2one('hr.department', string="Division")
    section = fields.Many2one('hr.department', string="Practice")
    practise = fields.Many2one('hr.department', string="Section")
    employee_ids = fields.Many2many('hr.employee', 'kw_kt_plan_employee_rel', string="Employee", required=True)
    kt_plan_config_id = fields.Many2one('kw_kt_plan_config', string='KT Plan Config Id', ondelete='cascade')
    company_id = fields.Many2one('res.company', string='Company', index=True, required=True,
                                 default=lambda self: self.env.user.company_id)

    @api.onchange('dept_id')
    def onchange_department(self):
        domain = {}
        for rec in self:
            domain['division'] = [('parent_id', '=', rec.dept_id.id), ('dept_type.code', '=', 'division')]
            domain['employee_ids'] = [('department_id', '=', rec.dept_id.id)]
            return {'domain': domain}

    @api.onchange('division')
    def onchange_division(self):
        domain = {}
        for rec in self:
            if rec.dept_id:
                domain['section'] = [('parent_id', '=', rec.division.id), ('dept_type.code', '=', 'section')]
                domain['employee_ids'] = [('department_id', '=', rec.division.id)]
                return {'domain': domain}

    @api.onchange('section')
    def onchange_section(self):
        domain = {}
        for rec in self:
            if rec.section:
                domain['practise'] = [('parent_id', '=', rec.section.id), ('dept_type.code', '=', 'practice')]
                domain['employee_ids'] = [('department_id', '=', rec.section.id)]
                return {'domain': domain}
