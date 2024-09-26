

from odoo import api, fields, models

class PFWidthdrawlConfirm(models.TransientModel):
    _name = 'employee.pf.widthdrawl.confirm'
    _inherit = ['exception.rule.confirm']

    related_model_id = fields.Many2one('pf.widthdrawl', 'PF Widthdrawl')

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        string = ''
        for exep in self.exception_ids:
            for line in exep.group_approval_ids:
                string += str(line.group.name) + ' >> '
        self.related_model_id.approval_workflow = string
        if self.ignore:
            self.related_model_id.ignore_exception = True
        return super(PFWidthdrawlConfirm, self).action_confirm()
