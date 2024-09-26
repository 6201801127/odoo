from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta

class HrItRule(models.Model):
    _name = 'hr.itrule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'IT Rule'
    _rec_name = 'name'

    deduction_id = fields.Selection([
        ('slab_80_declaration', 'Slab - 80 Declaration'),
        ('Medical Insurance Premium paid', 'Medical Insurance Premium paid'),
        ('Deductions on Interest on Savings Account', 'Deductions on Interest on Savings Account'),
        ('Tax Benefits on Home Loan', 'Tax Benefits on Home Loan'),
        ('Tax benefit on Education Loan (80E)', 'Tax benefit on Education Loan (80E)'),
        ('RGESS', 'RGESS'),
        ('Deductions on Medical Expenditure for a Handicapped Relative',
         'Deductions on Medical Expenditure for a Handicapped Relative'),
        ('Deductions on Medical Expenditure on Self or Dependent Relative',
         'Deductions on Medical Expenditure on Self or Dependent Relative'),
        ('Deductions on Donations', 'Deductions on Donations'),
        ('Income from House Property', 'Income from House Property'),
        ('Income from Other Sources', 'Income from Other Sources'),
        ('Deduction - Pension Scheme under section 80CCD(2)', 'Deduction - Pension Scheme under section 80CCD(2)'),
    ], string='Deduction')
    code = fields.Char('Code')
    name = fields.Char('IT Rule Section')
