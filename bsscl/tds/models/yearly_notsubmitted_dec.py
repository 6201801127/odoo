from odoo import api, fields, models, tools
from datetime import datetime, date, timedelta


class YearlyNotSubDec(models.TransientModel):
    _name = "yearly_notsubmitted_declaration"
    _description = "YearlyNot Submitted HR Declaration Details"

    def _default_financial_yr(self):
        fiscal_years = self.env['account.fiscalyear'].search([])
        for rec in fiscal_years:
            current_fiscal = self.env['account.fiscalyear'].search(
                [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
            return current_fiscal

    def _default_comming_yr(self):
        fiscal_years = self.env['account.fiscalyear'].search([])
        for rec in fiscal_years:
            comming_year = self.env['account.fiscalyear'].search([('date_start', '>', datetime.today().date())],
                                                                 limit=1, order='date_start asc')
            return comming_year

    # emp_code = fields.Char(related='employee_id.emp_code', string='Employee Code')
    gender = fields.Selection(related='employee_id.gender', string='Gender')
    date_range = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always',
                                 default=_default_financial_yr)
    employee_id = fields.Many2one('hr.employee', string='Employee', default=lambda self: self.env['hr.employee'].search(
        [('id', '=', self.env.context.get('employee_id'))]))
    pan_number = fields.Char(string='PAN', compute='_compute_pan_num')
    comming_fy = fields.Many2one('account.fiscalyear', 'Previous Year', track_visibility='always',
                                 default=_default_comming_yr)

    basic_salary = fields.Float(string='Basic Salary', default=lambda self: self.env.context.get('basic'))
    hra = fields.Float(string='House Rent Allowance', default=lambda self: self.env.context.get('hra'))
    other_income = fields.Float(string='Other Allowance', default=lambda self: self.env.context.get('oalw'))
    sub_total = fields.Float(string='Sub Total', default=lambda self: self.env.context.get('gross'))
    actual_hra = fields.Float(string='Actual HRA offered by the employer')
    basic_40_percent = fields.Float(string='40% of Basic')
    excess_10_percent = fields.Float(string='(Actual rentpaid)-(10% of the basic salary)')
    hra_by_employee = fields.Float(string='HRA Paid By the Employee	')
    previous_employer_income_final = fields.Float(string="2 . Income from Previous Employer (B)")
    lwop = fields.Float(string='LWOP', default=lambda self: self.env.context.get('lwop'))
    total = fields.Float(string='4 . Total (A+B-C)', default=lambda self: self.env.context.get('afterlwop'))
    hra_exemption = fields.Float(string='5 . HRA U/S (13A)')
    professional_tax = fields.Float(string='6 . Tax on Employment/P.T',
                                    default=lambda self: self.env.context.get('professional_tax'))
    employee_epf = fields.Float(string='Employee EPF Contribution',
                                default=lambda self: self.env.context.get('employee_epf'))
    # insurance_self = fields.Float(string='Health Insurance for Self',
    #                               default=lambda self: self.env.context.get('self_insurance'))
    insurance_dependent = fields.Float(string='Health Insurance for Dependant',
                                       default=lambda self: self.env.context.get('hid_amount'))
    standard_deduction = fields.Float(string="7 . Standard Deduction of 50,000",default=50000)
    income_from_salary = fields.Float(string='8 . Income From Salary (4-5-6-7)',
                                      default=lambda self: self.env.context.get('total_after_pt_sd'))
    housing_loan_interest_payment = fields.Float(string='9 . Income/Loss From House Property')
    gross_total_income = fields.Float(string='10 . Gross Total Income (8+9)',
                                      default=lambda self: self.env.context.get('total_after_pt_sd'))
    tax_regime=fields.Selection([('old_regime', 'Old Regime'), ('new_regime', 'New Regime')], required=True, default='old_regime',
                             string='Tax Regime')
    taxable_income = fields.Float(string='Taxable Income', default=lambda self: self.env.context.get('taxable_income'))
    tax_payable = fields.Float(string='Tax Payable', default=lambda self: self.env.context.get('tax_payable'))
    rebate = fields.Float(string='Rebate', default=lambda self: self.env.context.get('rebate'))
    net_tax_payable = fields.Float(string='Net Tax Payable',
                                   default=lambda self: self.env.context.get('net_tax_payable'))
    additional_sub_chrg = fields.Float(string='Subcharge',
                                       default=lambda self: self.env.context.get('additional_sub_chrg'))
    additional_edu_cess = fields.Float(string='Additional Educational cess',
                                       default=lambda self: self.env.context.get('additional_edu_cess'))
    total_tax_payable = fields.Float(string='Total Tax Payable',
                                     default=lambda self: self.env.context.get('total_tax_payable'))
    tax_recovered = fields.Float(string='Tax Recovered Till Date',
                                 default=lambda self: self.env.context.get('tax_recovered'))
    balance_tax_payable = fields.Float(string='Balance Tax Payable/Refundable',
                                       default=lambda self: self.env.context.get('balance_tax_payable'))

    total_deduction = fields.Float(string='12. Total Deduction',
                                   default=lambda self: self.env.context.get('total_deduction'))

    @api.depends('employee_id')
    def _compute_pan_num(self):
        for rec in self:
            if rec.employee_id.pan_no:

                rec.pan_number = rec.employee_id.pan_no

    # @api.depends('employee_epf','insurance_self','insurance_dependent')
    # def _total_deduction(self):
    #     for rec in self:
    #         rec.total_deduction = rec.employee_epf + rec.insurance_self + rec.insurance_dependent
