from odoo import api, fields, models


class HrJobExceptionConfirm(models.TransientModel):
    _name = 'hr.job.exception.confirm'
    _inherit = ['exception.rule.confirm']

    related_model_id = fields.Many2one('hr.job', 'Hr Job')

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        if self.ignore:
            self.related_model_id.ignore_exception = True
        return super(HrJobExceptionConfirm, self).action_confirm()
