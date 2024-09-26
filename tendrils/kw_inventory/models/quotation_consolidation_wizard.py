# from datetime import date
# from odoo.exceptions import UserError, ValidationError
# from odoo import exceptions, _
from odoo import api, models, fields


class kw_quotation_consolidation_wizard(models.TransientModel):
    _name = 'kw_quotation_consolidation_wizard'
    _description = 'Inventory quotation consolidation wizard'

    remark = fields.Text(string='Remark')
    ref_id = fields.Many2one('kw_quotation_consolidation', string='Quote ID')

    def submit(self):
        self.ref_id.write({'state': 'invalid', 'remark': self.remark})
        self.ref_id.quotation.write({'state': 'draft'})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
