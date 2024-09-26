from odoo import models, fields, api
from datetime import date
import odoo.addons.decimal_precision as dp

state_selection = [('draft', 'Draft'), ('applied', 'Applied'),
                   ('approve', 'Approved'), ('hold', 'Hold'),
                   ('grant', 'Grant'),('release', 'Release'), ('cancel', 'Cancelled'), ('reject', 'Rejected')]


class kw_adv_emi_ledger_log(models.Model):
    _name = 'kw_advance_emi_ledger_log'
    _description = 'EMI ledger log'

    # deduction_id = fields.Many2one('kw_advance_apply_salary_advance',string='Deduction Line')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    deduction_date = fields.Date(string='Deduction Date')
    amount = fields.Float(string="Total Payable Amount")
    tax_amount = fields.Float(string="Tax")
    monthly_interest = fields.Float(string="Monthly Interest")
    principal_amt = fields.Float(string="Principal Amount")
    balance = fields.Float(string="Ending Balance")
    pay_slip = fields.Char(string='Pay Slip')
    payment_by = fields.Selection(
        string='Payment By',
        selection=[('cheque', 'Cheque'), ('cash', 'Cash'), ('To Account', 'To Account')], default='cheque'
    )
    status = fields.Selection(
        string='Status',
        selection=[('draft', 'Draft'), ('approved', 'Approved')], default='draft'
    )


class kw_sal_adv_log(models.Model):
    _name = 'kw_sal_adv_log'
    _description = 'Salary advance log'

    sal_adv_id = fields.Many2one('kw_advance_apply_salary_advance', string='Salary Advance ID')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    currency_id = fields.Many2one('res.currency', string="Currency", required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    adv_amnt = fields.Float(string="Advance Amount", required=True, track_visibility='onchange',
                            digits=dp.get_precision('Advance'))
    adv_purpose = fields.Many2one('kw_advance_purpose', string="Advance Purpose", required=True)
    total_install = fields.Integer(string="No. of Installment", default=0, required=True)
    req_date = fields.Date(string="Required Date")
    applied_date = fields.Date(string="Applied Date")
    description = fields.Text(string="Description", required=True)
    payment_date = fields.Date(string="Disburse Date", track_visibility='onchange')
    eligibility_amt = fields.Integer(string="Eligible Amount", readonly=True)
    interest = fields.Integer(string='Interest(% pa)', readonly=True)
    state = fields.Selection(string='Status', selection=state_selection, default='draft', track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id',
                                    store=True)
    division = fields.Many2one('hr.department', string="Division", related='employee_id.division', store=True)
    section = fields.Many2one('hr.department', string="Practice", related='employee_id.section', store=True)
    practise = fields.Many2one('hr.department', string="Section", related='employee_id.practise', store=True)
    job_id = fields.Many2one('hr.job', string="Designation", related='employee_id.job_id', store=True)
    buffer_period = fields.Many2one('kw_advance_buffer_period_master', string='Relaxation Period')
