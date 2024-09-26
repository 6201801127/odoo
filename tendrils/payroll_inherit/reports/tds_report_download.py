from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, time
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from odoo.addons import decimal_precision as dp


class TdsReportWizard(models.TransientModel):
    _name = 'tds_report_download'
    _description = 'TDS Report Details'

    def _get_tds_data(self):
        tds_balance_ids = self.env.context.get('selected_active_ids')
        res = self.env['payroll_tds_report'].sudo().search(
            [('id', 'in', tds_balance_ids)])
        return res

    tds_balance_ids = fields.Many2many('payroll_tds_report', default=_get_tds_data,
                                     string="TDS Data")
    total_amount = fields.Float(compute='calculate_tds_amount',digits=dp.get_precision('Payroll'))
    final_gross = fields.Float(compute='calculate_tds_amount',digits=dp.get_precision('Payroll'))

    
    def calculate_tds_amount(self):
        total = 0
        final_gross = 0
        for rec in self.tds_balance_ids:
            total += rec.tds_amount
            final_gross += rec.final_gross
            
        self.total_amount = total
        self.final_gross = final_gross
        
