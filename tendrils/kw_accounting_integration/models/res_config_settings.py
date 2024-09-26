from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    salary_journal_id = fields.Many2one('account.journal', 'Salary Journal')


    @api.multi
    def set_values(self):
        super().set_values()
        param = self.env['ir.config_parameter'].sudo()
        field1 = self.salary_journal_id.id or False
        param.set_param('hr_payroll.default_salary_journal', field1)


    @api.model
    def get_values(self):
        res = super().get_values()
        salary_journal = self.env['ir.config_parameter'].sudo().get_param('hr_payroll.default_salary_journal')
        res.update(salary_journal_id = int(salary_journal) if salary_journal else False)
        return res