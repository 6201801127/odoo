from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, time
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from odoo.addons import decimal_precision as dp


class OtherAdvWizard(models.TransientModel):
    _name = 'other_advance_report_download'
    _description = 'Other Advance Details'

    def _get_insurance_data(self):
        other_adv_ids = self.env.context.get('selected_active_ids')
        res = self.env['payroll_other_advance_report'].sudo().search(
            [('id', 'in', other_adv_ids)])
        return res

    other_adv_ids = fields.Many2many('payroll_other_advance_report', default=_get_insurance_data,
                                     string="Other Advance")
    total_amount = fields.Float(compute='calculate_total_amount',digits=dp.get_precision('Payroll'))
    
    def calculate_total_amount(self):
        total = 0
        for rec in self.other_adv_ids:
            total += rec.other_adv
        self.total_amount = total
 