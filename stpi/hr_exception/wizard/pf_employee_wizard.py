
from odoo import api, fields, models

class PFEmployeeConfirm(models.TransientModel):
    _name = 'pf.employee.confirm'
    _inherit = ['exception.rule.confirm']

    related_model_id = fields.Many2one('pf.employee', 'PF Employee')

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        if self.ignore:
            self.related_model_id.ignore_exception = True
        return super(PFEmployeeConfirm, self).action_confirm()
