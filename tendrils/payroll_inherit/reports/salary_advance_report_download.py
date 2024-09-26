from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, time
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from odoo.addons import decimal_precision as dp


class SalaryAdvWizard(models.TransientModel):
    _name = 'salary_advance_report_download'
    _description = 'Salary Advance Details'

    def _get_salary_advance_data(self):
        salary_adv_ids = self.env.context.get('selected_active_ids')
        res = self.env['payroll_salary_advance_report'].sudo().search(
            [('id', 'in', salary_adv_ids)])
        return res

    salary_adv_ids = fields.Many2many('payroll_salary_advance_report','salary_advance_report_download_rel', default=_get_salary_advance_data,
                                     string="Salary Advance")
    total_amount = fields.Float(compute='calculate_total_amount_of_salary_adv',digits=dp.get_precision('Payroll'))
    total_interest = fields.Float(compute='calculate_total_amount_of_salary_adv',digits=dp.get_precision('Payroll'))
    
    def compute_month(self):
        month_dict = {'1': 'January', '2': 'February', '3': 'March', '4': 'April', '5': 'May', '6': 'June', '7': 'July', '8': 'August',
                      '9': 'September', '10': 'October', '11': 'November', '12': 'December'}
        for rec in self.salary_adv_ids:
            if rec.month:
                return month_dict.get(str(rec.month))
                
    def calculate_total_amount_of_salary_adv(self):
        total = 0
        interest = 0
        for rec in self.salary_adv_ids:
            total += rec.principal_amount
            interest += rec.interest
        self.total_amount = total
        self.total_interest = interest