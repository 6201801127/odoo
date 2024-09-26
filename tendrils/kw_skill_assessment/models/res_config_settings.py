from ast import literal_eval
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    skill_manager_emp = fields.Many2many('hr.employee', "skill_empl_rel", "skill_id", "emp_id", string="Employee")
    induction_assessment = fields.Boolean(string="Induction Assessment")

    @api.multi
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('kw_skill_assessment.skill_manager_emp_name',
                                                  self.skill_manager_emp.ids)
        self.env['ir.config_parameter'].set_param('kw_skill_assessment.induction_assessment', self.induction_assessment or False)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        skill_manager_emp = self.env['ir.config_parameter'].sudo().get_param(
            'kw_skill_assessment.skill_manager_emp_name')
        lines = False
        if skill_manager_emp:
            lines = [(6, 0, literal_eval(skill_manager_emp))]

        res.update(skill_manager_emp=lines,
                induction_assessment=params.get_param('kw_skill_assessment.induction_assessment'))
        return res
