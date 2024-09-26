import calendar
import datetime
from datetime import date, datetime, timedelta
from dateutil import relativedelta
from ast import literal_eval
import requests, json
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class kw_deduction_line(models.Model):
    _name = 'kw_advance_deduction_line'
    _description = 'Kw Deduction Line'

    @api.depends('deduction_date')
    # 
    def _compute_emi_start_month(self):
        for rec in self:
            if rec.deduction_date:
                rec.installment_month = datetime.strptime(str(rec.deduction_date), "%Y-%m-%d").strftime('%B-%Y')
                rec.month = datetime.strptime(str(rec.deduction_date), "%Y-%m-%d").strftime('%m')
                rec.year = datetime.strptime(str(rec.deduction_date), "%Y-%m-%d").strftime('%Y')
                newdt = datetime.strptime(str(rec.deduction_date), "%Y-%m-%d").strftime('%Y-%m-15')
                rec.payment_date = datetime.strptime(newdt, "%Y-%m-%d").date()
            else:
                rec.installment_month = ''
                rec.month = 0
                rec.year = 0
                rec.payment_date = False

    deduction_id = fields.Many2one('kw_advance_apply_salary_advance', string='Salary Advance Ref')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    deduction_date = fields.Date(string='EMI Date')
    installment_month = fields.Char(string="Installment Month", compute=_compute_emi_start_month)
    amount = fields.Float(string="Total Payable Amount", digits=(12, 2))
    tax_amount = fields.Float(string="Tax")
    monthly_interest = fields.Float(string="Interest Amount", digits=(12, 2))
    principal_amt = fields.Float(string="Principal Amount")
    balance = fields.Float(string="Ending Balance")
    pay_slip = fields.Char(string='Pay Slip')
    payment_by = fields.Selection(
        string='Payment By',
        selection=[('cheque', 'Cheque'), ('cash', 'Cash'), ('To Account', 'To Account')]
    )
    status = fields.Selection(
        string='Status',
        selection=[('draft', 'Unpaid'), ('paid', 'Paid')], default='draft'
    )
    payment_date = fields.Date(string="Payment Date", compute=_compute_emi_start_month, store=True)
    month = fields.Integer(string="Month", compute=_compute_emi_start_month, store=True)
    year = fields.Integer(string="Year", compute=_compute_emi_start_month, store=True)

    @api.model
    def write(self, vals):
        res = super(kw_deduction_line, self).write(vals)
        if vals.get('status') == 'paid':
            if not self.deduction_id.deduction_line_ids.filtered(lambda r: r.status == 'draft'):
                self.deduction_id.write({'state': 'paid'})
        return res


class kw_temp_advance_deduction_line(models.Model):
    _name = 'kw_temp_advance_deduction_line'
    _description = 'Kw Deduction Line'

    @api.depends('deduction_date')
    # 
    def _compute_emi_start_month(self):
        for rec in self:
            if rec.deduction_date:
                rec.installment_month = datetime.strptime(str(rec.deduction_date), "%Y-%m-%d").strftime('%B-%Y')
                rec.month = datetime.strptime(str(rec.deduction_date), "%Y-%m-%d").strftime('%m')
                rec.year = datetime.strptime(str(rec.deduction_date), "%Y-%m-%d").strftime('%Y')
                newdt = datetime.strptime(str(rec.deduction_date), "%Y-%m-%d").strftime('%Y-%m-15')
                rec.payment_date = datetime.strptime(newdt, "%Y-%m-%d").date()

    deduction_id = fields.Many2one('kw_advance_apply_salary_advance', string='Salary Advance Ref')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    deduction_date = fields.Date(string='EMI Date')
    installment_month = fields.Char(string="Installment Month", compute=_compute_emi_start_month)
    amount = fields.Float(string="Total Payable Amount", digits=(12, 2))
    tax_amount = fields.Float(string="Tax")
    monthly_interest = fields.Float(string="Interest Amount", digits=(12, 2))
    principal_amt = fields.Float(string="Principal Amount")
    balance = fields.Float(string="Ending Balance")
    pay_slip = fields.Char(string='Pay Slip')
    payment_by = fields.Selection(string='Payment By',selection=[('cheque', 'Cheque'), ('cash', 'Cash'), ('To Account', 'To Account')])
    status = fields.Selection(string='Status', selection=[('draft', 'Unpaid'), ('paid', 'Paid')], default='draft')
    payment_date = fields.Date(string="Payment Date", compute=_compute_emi_start_month, store=True)
    month = fields.Integer(string="Month", compute=_compute_emi_start_month, store=True)
    year = fields.Integer(string="Year", compute=_compute_emi_start_month, store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id.id)

class kw_pre_closure_deduction_line(models.Model):
    _name = 'kw_pre_closure_deduction_line'
    _description = 'Pre-closure Deduction Line'

    p_deduction_id = fields.Many2one('kw_advance_apply_salary_advance', string='Salary Advance Ref')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    paid_date = fields.Date(string='Payment Date')
    amount = fields.Float(string="Total Payable Amount")
    closer_type = fields.Selection(string='Closure Type', selection=[('partial', 'Partial'), ('full', 'Full')])
    month_count = fields.Integer(string='No of month(s)')
    payment_by = fields.Selection(
        string='Payment By',
        selection=[('cheque', 'Cheque'), ('cash', 'Cash'), ('To Account', 'To Account')]
    )
