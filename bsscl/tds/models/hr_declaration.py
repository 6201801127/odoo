from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
from odoo.addons import decimal_precision as dp
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
import json, requests
import re
import pytz
import math
from math import floor,ceil
from odoo.tools.mimetypes import guess_mimetype
import base64


class HrDeclaration(models.Model):
    _name = 'hr.declaration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'IT Declaration'
    _rec_name = 'employee_id'

    def calculate_round_amount(self, amount):
        if amount - int(amount) >= 0.5:
            return ceil(amount)
        else:
            return round(amount)


    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('deduct_report'):
            ids = []
            if self.env.user.has_group('tds.group_report_manager_declaration'):
                query = "select id from hr_declaration"
                self._cr.execute(query)
                ids = self._cr.fetchall()
                args += [('id', 'in', ids)]

            else:
                user_id = self.env.uid
                query = f"select id from hr_declaration where create_uid = {user_id}"
                self._cr.execute(query)
                ids = self._cr.fetchall()
                args = [('id', 'in', ids)]

        return super(HrDeclaration, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                  access_rights_uid=access_rights_uid)


    def _default_comming_yr(self):
        comming_year = self.env['account.fiscalyear'].search([('date_start', '>', datetime.today().date())],
                                                             limit=1, order='date_start asc')
        return comming_year


    @api.onchange('date_range')
    def comming_fy_formatted(self):
        if self.date_range:
            current_date_range = self.date_range.name
            current_year = int(current_date_range.split('-')[0])
            coming_year = current_year + 1
            self.comming_date_range = f"{coming_year}-{coming_year + 1}"
        else:
            self.comming_date_range = False

    @api.depends('date_range')
    def _chk_payslip_exist(self):
        for rec in self:
            payslip = self.env['hr.payslip'].sudo().search(
                [('employee_id', '=', rec.employee_id.id), ('date_from', '>=', rec.date_range.date_start),
                 ('date_to', '<=', rec.date_range.date_stop)])
            if len(payslip) > 0:
                rec.tax_freeze_bool = True
            else:
                rec.tax_freeze_bool = False

# deepak
    def _default_financial_yr(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        return current_fiscal

    def _default_comming_yr(self):
        comming_year = self.env['account.fiscalyear'].search([('date_start', '>', datetime.today().date())],
                                                                limit=1, order='date_start asc')
        return comming_year

    def calculateAge(self):
        fy_start_date =  self.env['account.fiscalyear'].search([('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())]).date_start
        birthday = self.env.user.employee_ids.birthday
        if birthday:
            age = fy_start_date.year - birthday.year -((fy_start_date.month, fy_start_date.day) < (birthday.month, birthday.day))
            return age

    def _default_employee(self):
        return self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)

    def default_joining_date(self):
        emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
        if emp:
            date = emp.transfer_date
            return date

    def _default_gender(self):
        emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
        if emp:
            gender = emp.gende
            return gender

    emp_age = fields.Integer(track_visibility='always',default=calculateAge,readonly=True,string='Age')
    bank_account = fields.Char(string='Bank A/c#', compute='_compute_pan_num',)
    bank_name = fields.Char(compute='_compute_pan_num',)
    employee_id = fields.Many2one('hr.employee', string='Employee Name', default=_default_employee,)
    emp_name = fields.Char(related='employee_id.name', string='Name')
    # image = fields.Binary(related='employee_id.image',string='Image')
    birthday = fields.Date(related='employee_id.birthday', string='Date of Birth')
    job_name = fields.Char(related='employee_id.job_id.name', string='Designation')
    department_name = fields.Char(related='employee_id.department_id.name', string='Department')
    tax_freeze_bool = fields.Boolean(compute='_chk_payslip_exist')
    # job_id = fields.Many2one('hr.job', string="Functional Designation", store=True)
    gender = fields.Selection([('male', 'Male'),
                              ('female', 'Female'),
                              ('transgender', 'All')
                              ], string="Gender" , default= _default_gender)
    # emp_code = fields.Char(related='employee_id.emp_code', string='Employee Code')
    pan_number = fields.Char(string='PAN', compute='_compute_pan_num', track_visibility="always")
    date_range = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always',
                                 default=_default_financial_yr)
    # comming_fy = fields.Many2one('account.fiscalyear', 'Previous Year', track_visibility='always',
    #                              default=_default_comming_yr)
    comming_date_range = fields.Char(compute='comming_fy_formatted')
    mobile_phone = fields.Char(related='employee_id.mobile_phone', string='Contact no')
    date_of_joining = fields.Date(string='Date of Joining', default = default_joining_date)
    # last_working_day = fields.Date(related='employee_id.last_working_day', string='Date of Leaving Service from Current Employer')

    previous_employer_income = fields.Float(string='Amount', digits=dp.get_precision('tds'), track_visibility="always")
    # previous_employer_actual_income = fields.Float(string='Actual Amount',digits=dp.get_precision('tds'))
    house_rent_paid = fields.Float(string='Declaration Amount', digits=dp.get_precision('tds'), track_visibility="always")
    actual_house_rent_paid = fields.Float(string='Actual Amount', digits=dp.get_precision('tds'), track_visibility="always")
    pan_landlord = fields.Binary(string='Rent Receipt')

    tax_regime=fields.Selection([('new_regime', 'New Regime'),('old_regime', 'Old Regime')], required=True, default='new_regime',
                             string='Tax Regime', track_visibility="alaways", store=True)

    slab_ids = fields.One2many('declaration.slab', 'slab_id', string='80C', track_visibility="onchange")
    housing_loan_ids = fields.One2many('housing_loan', 'housing_loan_id', string='Housing Loan Details')
    temp_interest_payment = fields.Float(string='', digits=dp.get_precision('tds'), track_visibility="always")
    actual_interest_payment = fields.Float(string='', digits=dp.get_precision('tds'), track_visibility="always")

    calculate_interest_payment = fields.Float(string='9 . Income/Loss From House Property', track_visibility="always",digits=dp.get_precision('tds'))
    allowed_rebate_under_80c = fields.Float(string='Allowed Rebate under Section 80C', track_visibility="always",digits=dp.get_precision('tds'))
    allowed_rebate_under_80b = fields.Float(string='Allowed Rebate under Section 80CCD1(B)', track_visibility="always",digits=dp.get_precision('tds'))
    allowed_rebate_under_80d = fields.Float(string='Allowed Rebate under Section 80D', track_visibility="always",digits=dp.get_precision('tds'))
    total_deductions = fields.Float(string='Total Deductions', track_visibility="always",digits=dp.get_precision('tds'))
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id, track_visibility="always")
    state = fields.Selection([('draft', 'Submitted'), ('approved', 'Approved')], default='draft',
                             string='Status', track_visibility='always')
    gross_salary = fields.Float(string='1 . Final Gross Salary', track_visibility="always",digits=dp.get_precision('tds'))
    basic_salary = fields.Float(string='Basic Salary', track_visibility="always",digits=dp.get_precision('tds'))
    actual_basic_salary = fields.Float(string='Basic Salary', track_visibility="always",digits=dp.get_precision('tds'))
    projection_basic_salary = fields.Float(string='Basic Salary', track_visibility="always",digits=dp.get_precision('tds'))

    hra = fields.Float(string='House Rent Allowance', track_visibility="always",digits=dp.get_precision('tds'))
    actual_hra = fields.Float(string='Actual HRA offered by the employer', track_visibility="always",digits=dp.get_precision('tds'))
    actual_payroll_hra = fields.Float(digits=dp.get_precision('tds'))
    projection_payroll_hra = fields.Float(digits=dp.get_precision('tds'))

    basic_40_percent = fields.Float(string='40% of Basic', track_visibility="always",digits=dp.get_precision('tds'))
    excess_10_percent = fields.Float(string='(Actual rent paid)-(10% of the basic salary)', tracking=True,digits=dp.get_precision('tds'))
    hra_by_employee = fields.Float(string='HRA Paid By the Employee', track_visibility="always",digits=dp.get_precision('tds'))
    sub_total = fields.Float(string='1 . Sub Total', track_visibility="always",digits=dp.get_precision('tds'))
    lwop = fields.Float(string='LWOP', track_visibility="always",digits=dp.get_precision('tds'))
    actual_lwop = fields.Float(string='LWOP', track_visibility="always",digits=dp.get_precision('tds'))
    projection_lwop = fields.Float(string='LWOP', track_visibility="always",digits=dp.get_precision('tds'))

    total = fields.Float(string='4 . Total (A+B-C)', track_visibility="always",digits=dp.get_precision('tds'))
    hra_exemption = fields.Float(string='5 . HRA U/S (13A)', track_visibility="always",digits=dp.get_precision('tds'))
    professional_tax = fields.Float(string='6 . Tax on Employment/P.T', track_visibility="always",digits=dp.get_precision('tds'))
    actual_professional_tax = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    projection_professional_tax = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))

    income_from_salary = fields.Float(string='8 . Income From Salary (4-5-6)', track_visibility="always",digits=dp.get_precision('tds'))
    gross_total_income = fields.Float(string='10 . Gross Total Income (8+9)', track_visibility="always",digits=dp.get_precision('tds'))
    housing_loan_interest_payment = fields.Float(string='10 . Housing Loan Interest Payment', track_visibility="always",digits=dp.get_precision('tds'))
    # principal_amt_of_housing_loan = fields.Float(string='11. Principal amount of Housing Loan')
    employees_epf = fields.Float(string="Employee's Contribution to P.F", track_visibility="always",digits=dp.get_precision('tds'))
    taxable_income = fields.Float(string='Taxable Income', track_visibility="always",digits=dp.get_precision('tds'))
    tax_payable = fields.Float(string='Tax Payable', track_visibility="always",digits=dp.get_precision('tds'))
    rebate = fields.Float(string='Rebate', track_visibility="always",digits=dp.get_precision('tds'))
    net_tax_payable = fields.Float(string='Net Tax Payable', track_visibility="always",digits=dp.get_precision('tds'))
    additional_sub_chrg = fields.Float(string='Subcharge', track_visibility="always",digits=dp.get_precision('tds'))
    additional_edu_cess = fields.Float(string='Additional Educational cess', track_visibility="always",digits=dp.get_precision('tds'))
    total_tax_payable = fields.Float(string='Total Tax Payable', track_visibility="always",digits=dp.get_precision('tds'))
    slab_80d_ids = fields.One2many('slab_declaration_80d', 'slab_80d_id', string='80D', track_visibility="always")
    check_month = fields.Boolean(string='Month', compute='_cheak_month')
    income_from_pre_employer_doc = fields.Binary(string='Document', track_visibility="always")
    doc_file_name_pre_emp = fields.Char(string='File Name')
    slab_80g_ids = fields.One2many('declaration_slab_80g', 'slab_80g_id', string='80G', track_visibility="always")
    slab_80e_ids = fields.One2many('declaration_slab_80e', 'slab_80e_id', string='80E', track_visibility="always")
    slab_ccd_ids = fields.One2many('declaration_slab_ccd', 'slab_ccd_id', string='80CCD', track_visibility="always")
    slab_80dd_ids = fields.One2many('declaration_slab_80dd', 'slab_80dd_id', string='80DD', track_visibility="always")
    pan_of_landlord = fields.Char(string='PAN of House Owner', track_visibility="always")
    previous_employer_income_final = fields.Float(string="2 . Income from Previous Employer (B)", track_visibility="always",digits=dp.get_precision('tds'))
    standard_deduction = fields.Float(string="Standard Deduction of 50,000", default=50000, track_visibility="always",digits=dp.get_precision('tds'))
    final_amount = fields.Float(string="Total Deductions", track_visibility="always",digits=dp.get_precision('tds'))
    prl_hlth_self = fields.Float(string="Health Insurance for Self", track_visibility="always",digits=dp.get_precision('tds'))
    prl_hlth_dependant = fields.Float(string="Health Insurance for Spouse,Children", track_visibility="always",digits=dp.get_precision('tds'))
    health_insurance_parent = fields.Float(string="Health Insurance for Parents", track_visibility="always",digits=dp.get_precision('tds'))
    tax_recovered = fields.Float(string='Tax Recovered Till Date', track_visibility="always",digits=dp.get_precision('tds'))
    balance_tax_payable = fields.Float(string='Balance Tax Payable/Refundable', track_visibility="always",digits=dp.get_precision('tds'))
    other_income = fields.Float(string='Other Allowance', track_visibility="always",digits=dp.get_precision('tds'))
    pan_landlord_file_name = fields.Char(string='File Name', track_visibility="always",attachment=True)
    tot_80c_epf = fields.Float(string='Total Amount of 80C', track_visibility="always",digits=dp.get_precision('tds'))
    tot_80ccd = fields.Float(string='Total Amount of 80CCD', track_visibility="always",digits=dp.get_precision('tds'))
    allowed_rebate_under_80ccd = fields.Float(string='Allowed Rebate under Section 80CCD', track_visibility="always",digits=dp.get_precision('tds'))
    tot_80d = fields.Float(string='Total Amount of 80D', track_visibility="always",digits=dp.get_precision('tds'))
    tot_80dd = fields.Float(string='Total Amount of 80DD', track_visibility="always",digits=dp.get_precision('tds'))
    allowed_rebate_under_80dd = fields.Float(string='Allowed Rebate under Section 80DD', track_visibility="always",digits=dp.get_precision('tds'))
    tot_80e = fields.Float(string='Total Amount of 80E', tracking=True,digits=dp.get_precision('tds'))
    allowed_rebate_under_80e = fields.Float(string='Allowed Rebate under Section 80E', track_visibility="always",digits=dp.get_precision('tds'))
    tot_80g = fields.Float(string='Total Amount of 80G', tracking=True,digits=dp.get_precision('tds'))
    allowed_rebate_under_80g = fields.Float(string='Allowed Rebate under Section 80G', track_visibility="always")
    check_previous_emp_income = fields.Boolean(string='Check Income', compute='_cheak_month', track_visibility="always")
    hra_percent = fields.Char(string='', track_visibility="always")
    tds_previous_employer = fields.Float(string='TDS Paid', digits=dp.get_precision('tds'), track_visibility="always")
    tds_doc = fields.Binary(string='TDS Document', track_visibility="always")
    gross_annual_value = fields.Float(string='Gross Annual Value', digits=dp.get_precision('tds'), track_visibility="always")
    municipal_taxes = fields.Float(string='Less: Municipal Taxes', digits=dp.get_precision('tds'), track_visibility="always")
    net_annual_value = fields.Float(string='Net annual Value', track_visibility="always",digits=dp.get_precision('tds'))
    standard_30_deduction = fields.Float(string='Less: Standard Deduction at 30%', track_visibility="always",digits=dp.get_precision('tds'))
    lowest_hra = fields.Float(string='Lowest', track_visibility="always",digits=dp.get_precision('tds'))
    total_income_interest = fields.Float(string='Income/Loss From House Property', track_visibility="always",digits=dp.get_precision('tds'))
    slab_80c_limit = fields.Float(string='Maximum amount allowed', compute='_compute_limit', digits=dp.get_precision('tds'), track_visibility="always")
    slab_80ccd_limit = fields.Float(string='Maximum amount allowed', compute='_compute_limit', digits=dp.get_precision('tds'), track_visibility="always")
    slab_80d_limit = fields.Char(string='Maximum amount allowed',
                                 default='Parent above 60 years : 50,000,Parent below 60 years : 25000,Self and Spouse,Children above 60 years : 50,000,Self and Spouse, Children below 60 years : 25,000',
                                 readonly=True, track_visibility="always")
    slab_80dd_limit = fields.Float(string='Threshold Limit', compute='_compute_limit', digits=dp.get_precision('tds'), track_visibility="always")
    slab_80e_limit = fields.Char(string='Threshold Limit', default='No Limit', readonly=True, track_visibility="always")
    slab_80g_limit = fields.Char(string='Threshold Limit',
                                 default='Donations Eligible for 100% & 50% Deduction Without Qualifying Limit as per IT LIST',
                                 readonly=True, track_visibility="always")
    professional_tax_pad = fields.Float(string='Professional Tax Paid', track_visibility="always",digits=dp.get_precision('tds'))
    total_80c_payable = fields.Float(string='Total Contribution to 80C', track_visibility="always",digits=dp.get_precision('tds'))
    tds_by_company = fields.Char(compute='_cheak_month',)
    invisible = fields.Boolean(string='Month', compute='_cheak_month')
    house_loan_doc = fields.Binary(string='Document', attachment=True)
    house_loan_doc_file_name =  fields.Char(string='Document Name')
    test_css = fields.Html(string='CSS', sanitize=False, compute='_compute_css', store=False)
    housing_loan_institute_pan = fields.Char(string='PAN of Houseing Loan Institution', track_visibility="always")
    housing_loan_institute = fields.Char(string='Name of Houseing Loan Institution', track_visibility="always")
    name_of_landlord = fields.Char(string='Name of Landlord', track_visibility="always")
    tds_doc_name = fields.Char(track_visibility="always",attachment=True)
    allowable_housing_intrest = fields.Float(string='Less: Allowable of Interest on House Loan', track_visibility="always",digits=dp.get_precision('tds'))
    slab_80ddb_ids = fields.One2many('declaration_slab_80ddb', 'slab_80ddb_id', string='Section 80DDB (Payments made towards Medical treatment specified diseases)', track_visibility="onchange")
    slab_80ddb_limit = fields.Char(string='Threshold Limit', default='Deduction limit of ₹ 40,000 (₹ 1,00,000 if Senior Citizen)', readonly=True, track_visibility="always")
    allowed_rebate_under_80ddb = fields.Float(string='Allowed Rebate under Section 80DDB', track_visibility="always",digits=dp.get_precision('tds'))

    income_from_other_sources = fields.Float(string='Declaration Amount', track_visibility="always",digits=dp.get_precision('tds'))
    actual_income_from_other_sources = fields.Float(string='Actual Amount', track_visibility="always",digits=dp.get_precision('tds'))
    income_from_other_sources_doc = fields.Binary(string='Document', attachment=True)
    other_source_income_file_name =  fields.Char(string='Document Name')
    final_amount_other_income = fields.Float(string='Income from Other Sources', track_visibility="always",digits=dp.get_precision('tds'))
    conveyance =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_conveyance =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    projection_conveyance =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    productivity =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_productivity =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    projection_productivity =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    commitment =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_commitment =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    projection_commitment =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))

    interest_received_from_bank = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_interest_received = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    interest_received_doc = fields.Binary(attachment=True)
    interest_received_file_name =  fields.Char()
    final_amount_bank_interest = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))

    lta =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_lta =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    projection_lta =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    prof_persuit =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_prof_persuit =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    projection_prof_persuit =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))

    arrear =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_arrear =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    projection_arrear =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))

    incentive =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_incentive =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    projection_incentive =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))

    variable =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_variable =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    projection_variable =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))

    splalw =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_splalw =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    projection_splalw  =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))

    equalw =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_equalw =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    projection_equalw =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))

    leave_encahment =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_leave_encahment =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    projection_leave_encahment =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))

    city_alw =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_city_alw =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    projection_city_alw =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))

    trng_inc =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_trng_inc =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    projection_trng_inc =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))

    erbonus =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_erbonus =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    projection_erbonus =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))

    total_salary = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_total_salary =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    projection_total_salary =  fields.Float(track_visibility="always",digits=dp.get_precision('tds'))

    income_from_bank_other = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_income_from_bank_other = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    final_income_from_bank_other = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))

    lta_spent_by_employee = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_lta_spent_by_employee = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    final_lta_spent_by_employee = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    lta_document = fields.Binary(attachment=True)
    lta_document_file_name = fields.Char(string='Document Name')

    prof_persuit_spent_by_employee = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_prof_persuit_spent_by_employee = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    final_prof_persuit_spent_by_employee = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    prof_persuit_document = fields.Binary(attachment=True)
    prof_persuit_document_file_name = fields.Char(string='Document Name')

    taxable_salary_from_csm = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    total_taxable_salary = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))

    monthly_tax_to_recover = fields.Integer(track_visibility="always")
    is_manager = fields.Boolean(compute='_compute_check_user')
    is_computed = fields.Boolean(string='Is Computed')

    # Hide edit button code written by Deepak Yadav
    edit_hide_css = fields.Html(string='CSS', sanitize=False, store=True, compute='_compute_edit_hide_css')

    @api.depends('state')
    def _compute_edit_hide_css(self):
        for rec in self:
            if rec.state == 'approved' or rec.state != 'draft':
                rec.edit_hide_css = '<style>.o_form_button_edit {display: none !important;}</style>'
                print('Deepak Yadavaaa')
            else:
                rec.edit_hide_css = False
                print('*********DDD')

    @api.depends('employee_id')
    def _compute_check_user(self):
        if self.env.user.has_group('tds.group_manager_hr_declaration'):
            self.is_manager = True
        else:
            self.is_manager = False

    def button_approve(self):
        for rec in self:
            if rec.is_computed != True:
                raise ValidationError("Please compute the tax before approving")
        self.state = 'approved'

    def button_compute_tax(self):
        self.is_computed = True

    @api.constrains('gross_annual_value')
    def check_gross_annual_value(self):
        for rec in self:
            if rec.gross_annual_value < 0:
                raise ValidationError("Gross Annual Value must be greater than 0")
            if rec.gross_annual_value < rec.municipal_taxes or rec.gross_annual_value < rec.temp_interest_payment:
                raise ValidationError("Gross Annual Value must be greater than Municipal Taxes paid and Interest on House Loan")

    

    # def button_compute_tax(self, **kwargs):
    #     bs = 0.00
    #     gross = 0.00
    #     lwop = 0.00
    #     ptd = 0.00
    #     epf = 0.00
    #     tds = 0.00
    #     conveyance = productivity = commitment = lta = prof_persuit = arrear = incentive = variable = splalw = equalw = leave_encahment = city_alw = trng_inc = erbonus = sum_prl = actual_hra = 0
    #     for rec in self:
    #         birthday = rec.employee_id.birthday
    #         if birthday:
    #             age = rec.date_range.date_start.year - birthday.year - (
    #                         (rec.date_range.date_start.month, rec.date_range.date_start.day) < (
    #                 birthday.month, birthday.day))
    #             rec.emp_age = age
    #         if kwargs.get('date_to'):
    #             check_value = 1 if kwargs.get('date_to') <= rec.date_range.date_stop else 0
    #         else:
    #             check_value = 1 if date.today() < rec.date_range.date_stop else 0

    #         contrct = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id),
    #                                                          ], limit=1)
    #         payslip = self.env['hr.payslip'].sudo().search([('employee_id', '=', rec.employee_id.id),
    #                                                         ('state', '=', 'done'),
    #                                                         ('date_from', '>=', rec.date_range.date_start),
    #                                                         ('date_to', '<=', rec.date_range.date_stop),
    #                                                         ])

    #         prl_id = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),
    #                                                             ('slip_id.state', '=', 'done'),
    #                                                             ('slip_id.date_from', '>=', rec.date_range.date_start),
    #                                                             ('slip_id.date_to', '<=', rec.date_range.date_stop),
    #                                                             ])
    #         j_date = rec.date_of_joining
    #         if j_date >= rec.date_range.date_start and j_date <= rec.date_range.date_stop:
    #             remain_months = (rec.date_range.date_stop.year - j_date.year) * 12 + (
    #                     rec.date_range.date_stop.month - j_date.month)
    #             month_limit = int(remain_months) + 1
    #         else:
    #             month_limit = 12

    #         blk_date_lst = []
    #         counter = 0
    #         last_counter = 0
    #         # block_payslips = self.env['hr_block_salary'].sudo().search([('employee_id', '=', rec.employee_id.id)])
    #         # for blk_payslp in block_payslips:
    #         #     blk_year = int(blk_payslp.year)
    #         #     blk_month = int(blk_payslp.month)
    #         #     blk_date = date(blk_year, blk_month, 1)
    #         #     blk_date_lst.append(blk_date)
    #         # for dates in blk_date_lst:
    #         #     if rec.date_range.date_start <= dates <= rec.date_range.date_stop:
    #         #         chk_payslip = payslip.filtered(lambda x: x.date_from <= dates <= x.date_to)
    #         #         if not chk_payslip:
    #         #             counter += 1
    #         # if rec.employee_id.last_working_day:
    #         #     if rec.date_range.date_start <= rec.employee_id.last_working_day <= rec.date_range.date_stop and rec.employee_id.active == False:
    #         #         last_counter = (
    #         #                                    rec.date_range.date_stop.year - rec.employee_id.last_working_day.year) * 12 + rec.date_range.date_stop.month - rec.employee_id.last_working_day.month
    #         #         print('last_counter================', last_counter)
    #         remaining_month = month_limit - len(payslip) - counter - last_counter if check_value == 1 else 0
    #         if check_value == 1 and kwargs.get('date_to'):
    #             remaining_month -= 1

    #         for pr in prl_id:
    #             if pr.code == 'BASIC':
    #                 bs += pr.amount
    #             if pr.code == 'GROSS':
    #                 gross += pr.amount
    #             if pr.code == 'LWOP':
    #                 lwop += pr.amount
    #             if pr.code == 'PTD':
    #                 ptd += pr.amount
    #             if pr.code == 'EEPF':
    #                 epf += pr.amount
    #             if pr.code == 'TDS':
    #                 tds += pr.amount
    #             if pr.code == 'TCA':
    #                 conveyance += pr.amount
    #             if pr.code == 'PBONUS':
    #                 productivity += pr.amount
    #             if pr.code == 'CBONUS':
    #                 commitment += pr.amount
    #             if pr.code == 'LTC':
    #                 lta += pr.amount
    #             if pr.code == 'PP':
    #                 prof_persuit += pr.amount
    #             if pr.code == 'ARRE':
    #                 arrear += pr.amount
    #             if pr.code == 'INC':
    #                 incentive += pr.amount
    #             if pr.code == 'VAR':
    #                 variable += pr.amount
    #             if pr.code == 'SALW':
    #                 splalw += pr.amount
    #             if pr.code == 'EALW':
    #                 equalw += pr.amount
    #             if pr.code == 'LE':
    #                 leave_encahment += pr.amount
    #             if pr.code == 'CBDA':
    #                 city_alw += pr.amount
    #             if pr.code == 'TINC':
    #                 trng_inc += pr.amount
    #             if pr.code == 'ERBONUS':
    #                 erbonus += pr.amount
    #         # hra_percentage_rec = self.env['city_wise_hra_config_master'].sudo().search(
    #         #     [('city', '=', rec.employee_id.base_branch_id.city)], limit=1)
    #         # hra_percentage = hra_percentage_rec.hra_percentage if hra_percentage_rec else contrct.house_rent_allowance_metro_nonmetro
    #         hra_percentage = contrct.hra


    #         gross_basic = contrct.wage
    #         gross_hra = contrct.wage * 40 / 100
    #         gross_conveyance = contrct.wage * contrct.travel_allowance / 100
    #         # gross_pb = contrct.productivity
    #         gross_pb = 0.0
    #         gross_cb = 0.0 #contrct.commitment
    #         gross_bonus = 0.0 #contrct.bonus
    #         gross_pp = 0.0 #contrct.prof_persuit
    #         gross_ltc = 0.0 #contrct.ltc

    #         current_month_basic = kwargs.get('basic') if kwargs.get('basic') else 0
    #         current_month_gross = kwargs.get('gross') if kwargs.get('gross') else 0
    #         current_month_lwop = kwargs.get('LWOP') if kwargs.get('LWOP') else 0
    #         rec.actual_lwop = lwop
    #         rec.projection_lwop = current_month_lwop
    #         rec.lwop = lwop + current_month_lwop
    #         rec.actual_basic_salary = bs
    #         rec.projection_basic_salary = current_month_basic + (contrct.wage * remaining_month)
    #         rec.basic_salary = bs + current_month_basic + (contrct.wage * remaining_month)
    #         for record in prl_id:
    #             if record.code == 'HRA':
    #                 sum_prl += record.amount
    #         # actual_hra = (sum_prl + (
    #         #             contrct.current_basic * contrct.house_rent_allowance_metro_nonmetro / 100) * remaining_month) + (current_month_basic * contrct.house_rent_allowance_metro_nonmetro / 100)
    #         rec.actual_payroll_hra = sum_prl
    #         rec.projection_payroll_hra = ((
    #                                           rec.calculate_round_amount(
    #                                               contrct.wage * contrct.hra / 100)) * remaining_month) + rec.calculate_round_amount(
    #             current_month_basic * contrct.hra / 100)
    #         rec.actual_hra = rec.actual_payroll_hra + rec.projection_payroll_hra

    #         rec.hra = rec.actual_hra
    #         rec.actual_conveyance = conveyance
    #         rec.projection_conveyance = ((
    #                                          rec.calculate_round_amount(
    #                                              contrct.wage * contrct.travel_allowance / 100)) * remaining_month) + (
    #                                                 current_month_basic * contrct.travel_allowance / 100)
    #         rec.conveyance = (rec.actual_conveyance + rec.projection_conveyance)
    #         current_month_productivity = kwargs.get('pb') if kwargs.get('pb') else 0
    #         current_month_commitment = kwargs.get('cb') if kwargs.get('cb') else 0
    #         current_month_lta = kwargs.get('lta') if kwargs.get('lta') else 0
    #         current_month_prof_persuit = kwargs.get('prof_persuit') if kwargs.get('prof_persuit') else 0
    #         rec.actual_productivity = productivity
    #         rec.projection_productivity = current_month_productivity + rec.calculate_round_amount(remaining_month)
    #         rec.productivity = rec.projection_productivity + rec.actual_productivity
    #         rec.actual_commitment = commitment
    #         rec.projection_commitment = current_month_commitment + rec.calculate_round_amount(remaining_month)
    #         rec.commitment = rec.actual_commitment + rec.projection_commitment
    #         rec.actual_lta = lta
    #         rec.projection_lta = current_month_lta + 0.0
    #         rec.lta = rec.actual_lta + rec.projection_lta
    #         rec.actual_prof_persuit = prof_persuit
    #         rec.projection_prof_persuit = current_month_prof_persuit + 0
    #         rec.prof_persuit = rec.actual_prof_persuit + rec.projection_prof_persuit
    #         current_month_arrear = kwargs.get('arrear') if kwargs.get('arrear') else 0
    #         current_month_incentive = kwargs.get('INC') if kwargs.get('INC') else 0
    #         current_month_variable = kwargs.get('VAR') if kwargs.get('VAR') else 0
    #         current_month_splalw = kwargs.get('SALW') if kwargs.get('SALW') else 0
    #         current_month_equalw = kwargs.get('EALW') if kwargs.get('EALW') else 0
    #         current_month_le = kwargs.get('LE') if kwargs.get('LE') else 0
    #         current_month_city = kwargs.get('CBDA') if kwargs.get('CBDA') else 0
    #         current_month_tinc = kwargs.get('TINC') if kwargs.get('TINC') else 0
    #         current_month_erbonus = kwargs.get('ERBONUS') if kwargs.get('ERBONUS') else 0
    #         rec.actual_arrear = arrear
    #         rec.projection_arrear = current_month_arrear
    #         rec.arrear = rec.actual_arrear + rec.projection_arrear
    #         rec.actual_incentive = incentive
    #         rec.projection_incentive = current_month_incentive
    #         rec.incentive = rec.actual_incentive + rec.projection_incentive
    #         rec.actual_variable = variable
    #         rec.projection_variable = current_month_variable
    #         rec.variable = rec.actual_variable + rec.projection_variable
    #         rec.actual_splalw = splalw
    #         rec.projection_splalw = current_month_splalw
    #         rec.splalw = rec.actual_splalw + rec.projection_splalw
    #         rec.actual_equalw = equalw
    #         rec.projection_equalw = current_month_equalw
    #         rec.equalw = rec.actual_equalw + rec.projection_equalw
    #         rec.actual_leave_encahment = leave_encahment
    #         rec.projection_leave_encahment = current_month_le
    #         rec.leave_encahment = rec.actual_leave_encahment + rec.projection_leave_encahment
    #         rec.actual_city_alw = city_alw
    #         rec.projection_city_alw = current_month_city
    #         rec.city_alw = rec.actual_city_alw + rec.projection_city_alw
    #         rec.actual_trng_inc = trng_inc
    #         rec.projection_trng_inc = current_month_tinc
    #         rec.trng_inc = rec.actual_trng_inc + rec.projection_trng_inc
    #         rec.actual_erbonus = erbonus
    #         rec.projection_erbonus = current_month_erbonus
    #         rec.erbonus = rec.actual_erbonus + rec.projection_erbonus

    #         rec.actual_total_salary = rec.actual_basic_salary - rec.actual_lwop + rec.actual_payroll_hra + rec.actual_conveyance + rec.actual_productivity + rec.actual_commitment + rec.actual_lta + rec.actual_prof_persuit + rec.actual_arrear + rec.actual_incentive + rec.actual_variable + rec.actual_splalw + rec.actual_equalw + rec.actual_leave_encahment + rec.actual_city_alw + rec.actual_trng_inc + rec.actual_erbonus

    #         rec.projection_total_salary = rec.projection_basic_salary - rec.projection_lwop + rec.projection_payroll_hra + rec.projection_conveyance + rec.projection_productivity + rec.projection_commitment + rec.projection_lta + rec.projection_prof_persuit + rec.projection_arrear + rec.projection_incentive + rec.projection_variable + rec.projection_splalw + rec.projection_equalw + rec.projection_leave_encahment + rec.projection_city_alw + rec.projection_trng_inc + rec.projection_erbonus

    #         rec.total_salary = rec.basic_salary - rec.lwop + rec.hra + rec.conveyance + rec.productivity + rec.commitment + rec.lta + rec.prof_persuit + rec.arrear + rec.incentive + rec.variable + rec.equalw + rec.leave_encahment + rec.city_alw + rec.trng_inc + rec.erbonus + rec.splalw

    #         if rec.tax_regime == 'old_regime':
    #             rec.standard_deduction = 50000
    #             rec.net_annual_value = rec.gross_annual_value - rec.municipal_taxes
    #             rec.standard_30_deduction = rec.net_annual_value * 30 / 100
    #             enable_epf = 'No'
    #             if enable_epf == 'yes':
    #                 if contrct.pf_deduction == 'other':
    #                     if contrct.epf_percent:
    #                         rec.employees_epf = epf + (current_month_basic * contrct.epf_percent / 100) + (
    #                                     contrct.wage * contrct.epf_percent / 100) * remaining_month
    #                     else:
    #                         rec.employees_epf = epf + 0
    #                 elif contrct.pf_deduction == 'avail1800' and contrct.wage >= 15000:
    #                     rec.employees_epf = epf + 1800 + (1800 * remaining_month)
    #                 else:
    #                     rec.employees_epf = epf + (current_month_basic * 12 / 100) + (
    #                                 contrct.wage * 12 / 100) * remaining_month
    #             else:
    #                 rec.employees_epf = 0

    #             pt_gross = gross_basic + gross_hra + gross_conveyance + gross_pb + gross_cb + gross_bonus + gross_pp + gross_ltc
    #             if pt_gross * 12 >= 300000:
    #                 extra_amount = 0 if remaining_month == 0 else 100
    #                 current_pt = 200 if current_month_gross != 0 else 0
    #                 pt = ptd + current_pt + (200 * remaining_month) + extra_amount
    #             elif pt_gross * 12 >= 160000 and pt_gross * 12 < 300000:
    #                 current_pt = 125 if current_month_gross != 0 else 0
    #                 pt = ptd + current_pt + (125 * remaining_month)
    #             else:
    #                 pt = 0
    #             rec.actual_professional_tax = ptd
    #             rec.projection_professional_tax = pt - ptd
    #             rec.professional_tax = pt
    #             basic_40_percent = 0.00
    #             excess_10_percent = 0.00
    #             fid_amount = 0
    #             emi_amount = 0
    #             # health_dependant = self.env['health_insurance_dependant'].sudo().search(
    #             #     [('employee_id', '=', rec.employee_id.id),
    #             #      ('date_range.date_start', '<=', rec.date_range.date_start),
    #             #      ('date_range.date_stop', '>=', rec.date_range.date_stop), ('state', '=', 'approved')], limit=1)
    #             # if health_dependant:
    #             #     check_parent = health_dependant.family_details_ids.filtered(
    #             #         lambda x: x.relationship_id.kw_id in (3, 4))
    #             #     if check_parent:
    #             #         fid_amount += sum(health_dependant.emi_details_ids.mapped('installment'))
    #             #     else:
    #             #         emi_amount += sum(health_dependant.emi_details_ids.mapped('installment'))
    #             # rec.prl_hlth_dependant = rec.calculate_round_amount(emi_amount)
    #             # rec.health_insurance_parent = rec.calculate_round_amount(fid_amount)

    #             # hra based on 40 percent of basic
    #             basic_40_percent = rec.calculate_round_amount(rec.basic_salary * hra_percentage / 100)
    #             rec.basic_40_percent = basic_40_percent if basic_40_percent > 0 else 0
    #             basic_10_percent = (contrct.wage * remaining_month + current_month_basic + bs) * 10 / 100
    #             # excess_10_percent = (rec.actual_house_rent_paid - basic_10_percent) if remaining_month < 1 else (rec.house_rent_paid - basic_10_percent)
    #             excess_10_percent = (
    #                         rec.actual_house_rent_paid - basic_10_percent) if rec.actual_house_rent_paid > 0 else (
    #                         rec.house_rent_paid - basic_10_percent)
    #             rec.excess_10_percent = excess_10_percent if excess_10_percent > 0 else 0
    #             rec.hra_by_employee = rec.actual_house_rent_paid if rec.actual_house_rent_paid > 0 else rec.house_rent_paid
    #             rec.previous_employer_income_final = rec.previous_employer_income
    #             rec.lowest_hra = min(rec.actual_hra, rec.excess_10_percent, rec.basic_40_percent)
    #             rec.hra_exemption = rec.lowest_hra

    #             rec.final_amount_bank_interest = rec.actual_interest_received if rec.actual_interest_received > 1 else rec.interest_received_from_bank
    #             rec.final_amount_other_income = rec.actual_income_from_other_sources if rec.actual_income_from_other_sources > 1 else rec.income_from_other_sources

    #             rec.income_from_bank_other = rec.interest_received_from_bank + rec.income_from_other_sources

    #             rec.actual_income_from_bank_other = rec.actual_interest_received + rec.actual_income_from_other_sources

    #             rec.final_income_from_bank_other = rec.final_amount_bank_interest + rec.final_amount_other_income

    #             rec.final_lta_spent_by_employee = rec.actual_lta_spent_by_employee if rec.actual_lta_spent_by_employee > 1 and rec.actual_lta_spent_by_employee <= rec.lta else rec.lta if rec.actual_lta_spent_by_employee > rec.lta else rec.lta if rec.lta_spent_by_employee > rec.lta and rec.actual_lta_spent_by_employee == 0 else rec.lta_spent_by_employee

    #             rec.final_prof_persuit_spent_by_employee = rec.actual_prof_persuit_spent_by_employee if rec.actual_prof_persuit_spent_by_employee > 1 and rec.actual_prof_persuit_spent_by_employee <= rec.prof_persuit else rec.prof_persuit if rec.actual_prof_persuit_spent_by_employee > rec.prof_persuit else rec.prof_persuit if rec.prof_persuit_spent_by_employee > rec.prof_persuit and rec.actual_prof_persuit_spent_by_employee == 0 else rec.prof_persuit_spent_by_employee

    #             rec.taxable_salary_from_csm = rec.total_salary - rec.lowest_hra - rec.final_lta_spent_by_employee - rec.final_prof_persuit_spent_by_employee
    #             rec.total_taxable_salary = rec.taxable_salary_from_csm + rec.previous_employer_income - rec.standard_deduction - rec.professional_tax
    #             amnt_80c = 0
    #             tot_80c_invst = 0
    #             tot_80ccd = 0
    #             tot_80ccd_invst = 0
    #             amnt_80dd = 0
    #             total_80dd = 0
    #             amnt_80e = 0
    #             total_80e = 0
    #             amnt_80ddb = 0
    #             amnt_80g = 0
    #             actual_80c = declared_80c = actual_80ccd = declared_80ccd = 0

    #             # Slab 80c calculation max limit 150000
    #             for lines in rec.slab_ids:
    #                 actual_80c += lines.actual_amt
    #                 declared_80c += lines.investment
    #                 tot_80c_invst = lines.it_rule.rebate
    #                 if remaining_month < 1:
    #                     amnt_80c = actual_80c + rec.employees_epf if (
    #                                                                              actual_80c + rec.employees_epf) <= tot_80c_invst else tot_80c_invst
    #                 else:
    #                     if (declared_80c + rec.employees_epf) >= (actual_80c + rec.employees_epf):
    #                         amnt_80c = tot_80c_invst if (declared_80c + rec.employees_epf) >= tot_80c_invst else (
    #                                     declared_80c + rec.employees_epf)
    #                     else:
    #                         if (actual_80c + rec.employees_epf) >= tot_80c_invst:
    #                             amnt_80c = tot_80c_invst
    #                         else:
    #                             amnt_80c = actual_80c + rec.employees_epf
    #             rec.allowed_rebate_under_80c = amnt_80c

    #             for lines in rec.slab_ccd_ids:
    #                 actual_80ccd += lines.actual_amt
    #                 declared_80ccd += lines.investment
    #                 tot_80ccd_invst += lines.it_rule.rebate
    #                 if remaining_month < 1:
    #                     tot_80ccd = actual_80ccd if actual_80ccd <= tot_80ccd_invst else tot_80ccd_invst
    #                 else:
    #                     if declared_80ccd >= actual_80ccd:
    #                         tot_80ccd = tot_80ccd_invst if declared_80ccd >= tot_80ccd_invst else declared_80ccd
    #                     else:
    #                         tot_80ccd = tot_80ccd_invst if actual_80ccd >= tot_80ccd_invst else actual_80ccd
    #             rec.allowed_rebate_under_80ccd = tot_80ccd

    #             slab80_deduction = rec.allowed_rebate_under_80c + rec.allowed_rebate_under_80ccd
    #             actual_80ddb = declared_80ddb = 0
    #             amnt_self_below_60 = 0
    #             amnt_self_below_60_rebate = 0
    #             amnt_self_above_60 = 0
    #             amnt_self_above_60_rebate = 0
    #             amnt_parent_below_60 = 0
    #             amnt_parent_below_60_rebate = 0
    #             amnt_parent_above_60 = 0
    #             amnt_parent_above_60_rebate = 0
    #             actual_80e_amount = 0
    #             declared_80e_amount = 0
    #             actual_80dd = 0
    #             declared_80dd = 0
    #             actual_80d = declared_80d = actual_80d_parent_below_60 = declared_80d_parent_below_60 = actual_80d_spouse_below_60 = declared_80d_spouse_below_60 = actual_80d_parent_above_60 = declared_80d_parent_above_60 = 0

    #             saving_master_rec = self.env['saving.master'].sudo().search([])
    #             for lines in rec.slab_80d_ids:
    #                 amnt_self_below_60_rebate = saving_master_rec.filtered(lambda x: x.code == 'MIPB').rebate
    #                 amnt_self_above_60_rebate = saving_master_rec.filtered(lambda x: x.code == 'MIPS').rebate
    #                 amnt_parent_below_60_rebate = saving_master_rec.filtered(lambda x: x.code == 'MIPSPB').rebate
    #                 amnt_parent_above_60_rebate = saving_master_rec.filtered(lambda x: x.code == 'MIPSP').rebate

    #                 if lines.saving_master.code == 'MIPB':  ###25000 ###Health Insurance Premium Paid for Self, Spouse and Children below 60 years
    #                     actual_80d += lines.actual_amt
    #                     declared_80d += lines.investment
    #                     if remaining_month < 1:
    #                         amnt_self_below_60 = actual_80d if actual_80d <= amnt_self_below_60_rebate else amnt_self_below_60_rebate
    #                     else:
    #                         if declared_80d >= actual_80d:
    #                             amnt_self_below_60 = amnt_self_below_60_rebate if declared_80d >= amnt_self_below_60_rebate else declared_80d
    #                         else:
    #                             amnt_self_below_60 = amnt_self_below_60_rebate if actual_80d >= amnt_self_below_60_rebate else actual_80d

    #                     # amnt_self_below_60 += lines.actual_amt if remaining_month < 1 else lines.investment

    #                 if lines.saving_master.code == 'MIPS':  ###50000 Health Insurance Premium Paid for Self,Spouse and Children above 60 years
    #                     actual_80d_spouse_below_60 += lines.actual_amt
    #                     declared_80d_spouse_below_60 += lines.investment
    #                     if remaining_month < 1:
    #                         amnt_self_above_60 = actual_80d_spouse_below_60 if actual_80d_spouse_below_60 <= amnt_self_above_60_rebate else amnt_self_above_60_rebate
    #                     else:
    #                         if declared_80d_spouse_below_60 >= actual_80d_spouse_below_60:
    #                             amnt_self_above_60 = amnt_self_above_60_rebate if declared_80d_spouse_below_60 >= amnt_self_above_60_rebate else declared_80d_spouse_below_60
    #                         else:
    #                             amnt_self_above_60 = amnt_self_above_60_rebate if actual_80d_spouse_below_60 >= amnt_self_above_60_rebate else actual_80d_spouse_below_60
    #                     # amnt_self_above_60 += lines.actual_amt if remaining_month < 1 else lines.investment
    #                 if lines.saving_master.code == 'MIPSPB':  ###25000 ###Health Insurance Premium Paid for Parent below 60 years
    #                     actual_80d_parent_below_60 += lines.actual_amt
    #                     declared_80d_parent_below_60 += lines.investment
    #                     if remaining_month < 1:
    #                         amnt_parent_below_60 = actual_80d_parent_below_60 if actual_80d_parent_below_60 <= amnt_parent_below_60_rebate else amnt_parent_below_60_rebate
    #                     else:
    #                         if declared_80d_parent_below_60 >= actual_80d_parent_below_60:
    #                             amnt_parent_below_60 = amnt_parent_below_60_rebate if declared_80d_parent_below_60 >= amnt_parent_below_60_rebate else declared_80d_parent_below_60
    #                         else:
    #                             amnt_parent_below_60 = amnt_parent_below_60_rebate if actual_80d_parent_below_60 >= amnt_parent_below_60_rebate else actual_80d_parent_below_60

    #                     # amnt_parent_below_60 += lines.actual_amt if remaining_month < 1 else lines.investment
    #                 if lines.saving_master.code == 'MIPSP':  ###50000 ###Health Insurance Premium Paid for Parent above 60 years
    #                     actual_80d_parent_above_60 += lines.actual_amt
    #                     declared_80d_parent_above_60 += lines.investment
    #                     if remaining_month < 1:
    #                         amnt_parent_above_60 = actual_80d_parent_above_60 if actual_80d_parent_above_60 <= amnt_parent_above_60_rebate else amnt_parent_above_60_rebate
    #                     else:
    #                         if declared_80d_parent_above_60 >= actual_80d_parent_above_60:
    #                             amnt_parent_above_60 = amnt_parent_above_60_rebate if declared_80d_parent_above_60 >= amnt_parent_above_60_rebate else declared_80d_parent_above_60
    #                         else:
    #                             amnt_parent_above_60 = amnt_parent_above_60_rebate if actual_80d_parent_above_60 >= amnt_parent_above_60_rebate else actual_80d_parent_above_60
    #                     # amnt_parent_above_60 += lines.actual_amt if remaining_month < 1 else lines.investment
    #             if amnt_self_above_60 > 0:
    #                 tot_self = amnt_self_above_60 + rec.prl_hlth_dependant + amnt_self_below_60
    #                 deduction_self = tot_self if tot_self < amnt_self_above_60_rebate else amnt_self_above_60_rebate
    #             else:
    #                 tot_self = amnt_self_below_60 + rec.prl_hlth_dependant
    #                 deduction_self = tot_self if tot_self < amnt_self_below_60_rebate else amnt_self_below_60_rebate

    #             if amnt_parent_above_60 > 0:
    #                 tot_dependent = amnt_parent_above_60 + rec.health_insurance_parent + amnt_parent_below_60
    #                 deduction_dependent = tot_dependent if tot_dependent < amnt_parent_above_60_rebate else amnt_parent_above_60_rebate
    #             else:
    #                 tot_dependent = amnt_parent_below_60 + rec.health_insurance_parent
    #                 deduction_dependent = tot_dependent if tot_dependent < amnt_parent_below_60_rebate else amnt_parent_below_60_rebate
    #             rec.allowed_rebate_under_80d = deduction_self + deduction_dependent
    #             tot_80dd_invst = 0
    #             for lines in rec.slab_80dd_ids:
    #                 amnt_80dd += lines.investment if lines.actual_amt == 0 else lines.actual_amt
    #                 tot_80dd_invst += lines.saving_master.rebate

    #             total_80dd += amnt_80dd
    #             rec.tot_80dd = amnt_80dd
    #             rec.allowed_rebate_under_80dd = total_80dd

    #             for lines in rec.slab_80e_ids:
    #                 # amnt_80e += lines.actual_amt if remaining_month < 1 else lines.investment
    #                 if remaining_month < 1:
    #                     amnt_80e += lines.actual_amt
    #                 else:
    #                     actual_80e_amount += lines.actual_amt
    #                     declared_80e_amount += lines.investment
    #                     amnt_80e = max(actual_80e_amount, declared_80e_amount)

    #             total_80e += amnt_80e
    #             rec.tot_80e = total_80e
    #             rec.allowed_rebate_under_80e = amnt_80e

    #             for lines in rec.slab_80g_ids:
    #                 if lines.saving_master.code == '80GN':
    #                     actual_80g = declared_80g = 0
    #                     actual_80g += lines.actual_amt
    #                     declared_80g += lines.investment
    #                     if remaining_month < 1:
    #                         amnt_80g += lines.actual_amt / 2
    #                     else:
    #                         amnt_80g += max(actual_80g, declared_80g) / 2

    #                 if lines.saving_master.code != '80GN':
    #                     actual_80g = declared_80g = 0
    #                     actual_80g += lines.actual_amt
    #                     declared_80g += lines.investment
    #                     if remaining_month < 1:
    #                         amnt_80g += lines.actual_amt
    #                     else:
    #                         amnt_80g += max(actual_80g, declared_80g)

    #             tot_80ddb_invst = 0
    #             for lines in rec.slab_80ddb_ids:
    #                 # amnt_80ddb += lines.actual_amt if remaining_month < 1 else lines.investment
    #                 actual_80ddb += lines.actual_amt
    #                 declared_80ddb += lines.investment
    #                 tot_80ddb_invst = lines.it_rule.rebate
    #                 if remaining_month < 1:
    #                     amnt_80ddb = actual_80ddb if actual_80ddb <= tot_80ddb_invst else tot_80ddb_invst
    #                 else:
    #                     if declared_80ddb >= actual_80ddb:
    #                         amnt_80ddb = tot_80ccd_invst if declared_80ddb >= tot_80ccd_invst else declared_80ddb
    #                     else:
    #                         amnt_80ddb = tot_80ccd_invst if actual_80ddb >= tot_80ccd_invst else actual_80ddb
    #                 if rec.emp_age >= 60:
    #                     rec.allowed_rebate_under_80ddb = tot_80ddb_invst if amnt_80ddb >= tot_80ddb_invst else amnt_80ddb
    #                 else:
    #                     rec.allowed_rebate_under_80ddb = 40000 if amnt_80ddb >= 40000 else amnt_80ddb

    #             rec.tot_80g = amnt_80g
    #             rec.allowed_rebate_under_80g = amnt_80g
    #             saving_rec = self.env['saving.master'].sudo().search([('code', '=', 'IP')])
    #             cal_income_deduction = 0
    #             # if remaining_month < 1:
    #             #     cal_income_deduction = (rec.net_annual_value - rec.standard_30_deduction) - 200000 if rec.actual_interest_payment >= 200000 else -rec.actual_interest_payment
    #             #     rec.allowable_housing_intrest = 200000 if rec.actual_interest_payment >= 200000 else rec.actual_interest_payment
    #             # else:
    #             #     rec.allowable_housing_intrest = 200000 if rec.temp_interest_payment >= 200000 else rec.temp_interest_payment
    #             #     cal_income_deduction = (rec.net_annual_value - rec.standard_30_deduction) - 200000 if rec.temp_interest_payment >= 200000 else -rec.temp_interest_payment
    #             # rec.total_income_interest = cal_income_deduction
    #             rec.total_income_interest = rec.net_annual_value - rec.standard_30_deduction - rec.temp_interest_payment
    #             if rec.total_income_interest < 0:
    #                 temp_income_interest = rec.total_income_interest if -(
    #                     rec.total_income_interest) < saving_rec.rebate else -(saving_rec.rebate)
    #             else:
    #                 temp_income_interest = rec.total_income_interest

    #             rec.calculate_interest_payment = temp_income_interest
    #             rec.final_amount_other_income = rec.actual_income_from_other_sources if remaining_month < 1 else rec.income_from_other_sources
    #             temp_gross_total_income = (
    #                         rec.total_taxable_salary + rec.calculate_interest_payment + rec.final_income_from_bank_other)
    #             rec.gross_total_income = temp_gross_total_income if temp_gross_total_income > 0 else 0

    #             rec.final_amount = slab80_deduction + deduction_self + deduction_dependent + total_80dd + total_80e + amnt_80g + rec.allowed_rebate_under_80ddb
    #             temp_taxable_income = rec.gross_total_income - rec.final_amount
    #             if (temp_taxable_income % 10) >= 5:
    #                 z = 10 - (temp_taxable_income % 10)
    #                 tax_amount = temp_taxable_income + z
    #             else:
    #                 tax_amount = temp_taxable_income - (temp_taxable_income % 10)
    #             rec.taxable_income = tax_amount if tax_amount > 0 else 0

    #             temp_tax_payable = 0

    #             if rec.emp_age < 60:
    #                 if rec.taxable_income > 250000 and rec.taxable_income <= 500000:
    #                     tds_amount = rec.taxable_income - 250000
    #                     tax_slab = self.env['tax_slab'].sudo().search(
    #                         [('date_range', '=', rec.date_range.id), ('salary_from', '<=', rec.taxable_income),
    #                          ('salary_to', '>=', rec.taxable_income), ('tax_regime', '=', 'old_regime'),
    #                          ('age_from', '<=', rec.emp_age), ('age_to', '>=', rec.emp_age)], limit=1)
    #                     temp_tax_payable = tds_amount * tax_slab.tax_rate / 100
    #                 elif rec.taxable_income > 500000 and rec.taxable_income <= 1000000:
    #                     tds_above5 = rec.taxable_income - 500000
    #                     tax_slab = self.env['tax_slab'].sudo().search(
    #                         [('date_range', '=', rec.date_range.id), ('salary_from', '<=', rec.taxable_income),
    #                          ('salary_to', '>=', rec.taxable_income), ('tax_regime', '=', 'old_regime'),
    #                          ('age_from', '<=', rec.emp_age), ('age_to', '>=', rec.emp_age)], limit=1)
    #                     tds_above5percentage = tds_above5 * tax_slab.tax_rate / 100
    #                     tax_slab_1 = self.env['tax_slab'].sudo().search(
    #                         [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 250001),
    #                          ('salary_to', '<=', 500000), ('tax_regime', '=', 'old_regime'),
    #                          ('age_from', '<=', rec.emp_age), ('age_to', '>=', rec.emp_age)], limit=1)
    #                     tds_below5percentage = 250000 * tax_slab_1.tax_rate / 100
    #                     temp_tax_payable = tds_above5percentage + tds_below5percentage
    #                 elif rec.taxable_income > 1000000:
    #                     tds_above10 = rec.taxable_income - 1000000
    #                     tax_slab = self.env['tax_slab'].sudo().search(
    #                         [('date_range', '=', rec.date_range.id), ('salary_from', '<=', rec.taxable_income),
    #                          ('salary_to', '>=', rec.taxable_income), ('tax_regime', '=', 'old_regime'),
    #                          ('age_from', '<=', rec.emp_age), ('age_to', '>=', rec.emp_age)], limit=1)
    #                     tds_above10percentage = tds_above10 * tax_slab.tax_rate / 100
    #                     tax_slab_1 = self.env['tax_slab'].sudo().search(
    #                         [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 500001),
    #                          ('salary_to', '<=', 1000000), ('tax_regime', '=', 'old_regime'),
    #                          ('age_from', '<=', rec.emp_age), ('age_to', '>=', rec.emp_age)], limit=1)
    #                     tds_above5percentage = 500000 * tax_slab_1.tax_rate / 100
    #                     tax_slab_2 = self.env['tax_slab'].sudo().search(
    #                         [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 250001),
    #                          ('salary_to', '<=', 500000), ('tax_regime', '=', 'old_regime'),
    #                          ('age_from', '<=', rec.emp_age), ('age_to', '>=', rec.emp_age)], limit=1)
    #                     tds_below5percentage = 250000 * tax_slab_2.tax_rate / 100
    #                     temp_tax_payable = tds_above10percentage + tds_above5percentage + tds_below5percentage

    #             if 60 <= rec.emp_age <= 80:
    #                 if rec.taxable_income > 300000 and rec.taxable_income <= 500000:
    #                     tds_amount = rec.taxable_income - 300000
    #                     tax_slab = self.env['tax_slab'].sudo().search(
    #                         [('date_range', '=', rec.date_range.id), ('salary_from', '<=', rec.taxable_income),
    #                          ('salary_to', '>=', rec.taxable_income), ('tax_regime', '=', 'old_regime'),
    #                          ('age_from', '<=', rec.emp_age), ('age_to', '>=', rec.emp_age)], limit=1)
    #                     temp_tax_payable = tds_amount * tax_slab.tax_rate / 100
    #                 elif rec.taxable_income > 500000 and rec.taxable_income <= 1000000:
    #                     tds_above5 = rec.taxable_income - 500000
    #                     tax_slab = self.env['tax_slab'].sudo().search(
    #                         [('date_range', '=', rec.date_range.id), ('salary_from', '<=', rec.taxable_income),
    #                          ('salary_to', '>=', rec.taxable_income), ('tax_regime', '=', 'old_regime'),
    #                          ('age_from', '<=', rec.emp_age), ('age_to', '>=', rec.emp_age)], limit=1)

    #                     tds_above5percentage = tds_above5 * tax_slab.tax_rate / 100
    #                     tax_slab_1 = self.env['tax_slab'].sudo().search(
    #                         [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 300001),
    #                          ('salary_to', '<=', 500000), ('tax_regime', '=', 'old_regime'),
    #                          ('age_from', '<=', rec.emp_age), ('age_to', '>=', rec.emp_age)], limit=1)

    #                     tds_below5percentage = 200000 * tax_slab_1.tax_rate / 100
    #                     temp_tax_payable = tds_above5percentage + tds_below5percentage
    #                 elif rec.taxable_income > 1000000:
    #                     tds_above10 = rec.taxable_income - 1000000
    #                     tax_slab = self.env['tax_slab'].sudo().search(
    #                         [('date_range', '=', rec.date_range.id), ('salary_from', '<=', rec.taxable_income),
    #                          ('salary_to', '>=', rec.taxable_income), ('tax_regime', '=', 'old_regime'),
    #                          ('age_from', '<=', rec.emp_age), ('age_to', '>=', rec.emp_age)], limit=1)

    #                     tds_above10percentage = tds_above10 * tax_slab.tax_rate / 100
    #                     tax_slab_1 = self.env['tax_slab'].sudo().search(
    #                         [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 500001),
    #                          ('salary_to', '<=', 1000000), ('tax_regime', '=', 'old_regime'),
    #                          ('age_from', '<=', rec.emp_age), ('age_to', '>=', rec.emp_age)], limit=1)
    #                     tds_above5percentage = 500000 * tax_slab_1.tax_rate / 100
    #                     tax_slab_2 = self.env['tax_slab'].sudo().search(
    #                         [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 300001),
    #                          ('salary_to', '<=', 500000), ('tax_regime', '=', 'old_regime'),
    #                          ('age_from', '<=', rec.emp_age), ('age_to', '>=', rec.emp_age)], limit=1)
    #                     tds_below5percentage = 200000 * tax_slab_2.tax_rate / 100
    #                     temp_tax_payable = tds_above10percentage + tds_above5percentage + tds_below5percentage
    #             if rec.emp_age > 80:
    #                 if rec.taxable_income > 500001 and rec.taxable_income <= 1000000:
    #                     tds_amount = rec.taxable_income - 500000
    #                     tax_slab = self.env['tax_slab'].sudo().search(
    #                         [('date_range', '=', rec.date_range.id), ('salary_from', '<=', rec.taxable_income),
    #                          ('salary_to', '>=', rec.taxable_income), ('tax_regime', '=', 'old_regime'),
    #                          ('age_from', '<=', rec.emp_age), ('age_to', '>=', rec.emp_age)], limit=1)
    #                     temp_tax_payable = tds_amount * tax_slab.tax_rate / 100
    #                 elif rec.taxable_income > 1000000:
    #                     tds_above5 = rec.taxable_income - 1000000
    #                     tax_slab = self.env['tax_slab'].sudo().search(
    #                         [('date_range', '=', rec.date_range.id), ('salary_from', '<=', rec.taxable_income),
    #                          ('salary_to', '>=', rec.taxable_income), ('tax_regime', '=', 'old_regime'),
    #                          ('age_from', '<=', rec.emp_age), ('age_to', '>=', rec.emp_age)], limit=1)
    #                     tds_above5percentage = tds_above5 * tax_slab.tax_rate / 100
    #                     tax_slab_1 = self.env['tax_slab'].sudo().search(
    #                         [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 500001),
    #                          ('salary_to', '<=', 1000000), ('tax_regime', '=', 'old_regime'),
    #                          ('age_from', '<=', rec.emp_age), ('age_to', '>=', rec.emp_age)], limit=1)
    #                     tds_below5percentage = 500000 * tax_slab_1.tax_rate / 100
    #                     temp_tax_payable = tds_above5percentage + tds_below5percentage

    #             rec.tax_payable = temp_tax_payable if temp_tax_payable > 0 else 0

    #             rec.rebate = rec.tax_payable if rec.taxable_income < 500000 and rec.tax_payable > 0 else 0
    #             temp_net_tax_payable = rec.tax_payable - rec.rebate
    #             rec.net_tax_payable = temp_net_tax_payable if temp_net_tax_payable > 0 else 0
    #             tax_slab_rec = self.env['tax_slab'].sudo().search(
    #                 [('date_range', '=', rec.date_range.id), ('salary_from', '<=', rec.taxable_income),
    #                  ('salary_to', '>=', rec.taxable_income), ('tax_regime', '=', 'old_regime'),
    #                  ('age_from', '<=', rec.emp_age), ('age_to', '>=', rec.emp_age)], limit=1)
    #             rec.additional_sub_chrg = rec.net_tax_payable * tax_slab_rec.surcharge / 100
    #             rec.additional_edu_cess = rec.net_tax_payable * tax_slab_rec.cess / 100

    #             total_tax_payable = rec.net_tax_payable + rec.additional_sub_chrg + rec.additional_edu_cess
    #             if (total_tax_payable % 10) >= 5:
    #                 z = 10 - (total_tax_payable % 10)
    #                 var_tax_payable = total_tax_payable + z
    #             else:
    #                 var_tax_payable = total_tax_payable - (total_tax_payable % 10)
    #             rec.total_tax_payable = var_tax_payable
    #             rec.tax_recovered = tds + rec.tds_previous_employer
    #             temp_balance_tax_payable = rec.total_tax_payable - rec.tax_recovered

    #             rec.balance_tax_payable = temp_balance_tax_payable
    #             rec.monthly_tax_to_recover = rec.balance_tax_payable / remaining_month if rec.balance_tax_payable > 0 else 0
    #         else:
    #             rec.allowed_rebate_under_80c = 0
    #             rec.allowed_rebate_under_80ccd = 0
    #             rec.allowed_rebate_under_80d = 0
    #             rec.allowed_rebate_under_80ddb = 0
    #             rec.allowed_rebate_under_80dd = 0
    #             rec.allowed_rebate_under_80e = 0
    #             rec.allowed_rebate_under_80g = 0
    #             rec.final_lta_spent_by_employee = 0
    #             rec.final_prof_persuit_spent_by_employee = 0
    #             rec.previous_employer_income_final = rec.previous_employer_income
    #             rec.hra_by_employee = 0
    #             rec.excess_10_percent = 0
    #             rec.actual_hra = 0
    #             rec.basic_40_percent = 0
    #             rec.lowest_hra = 0
    #             rec.standard_30_deduction = 0
    #             rec.net_annual_value = rec.gross_annual_value - rec.municipal_taxes
    #             rec.total_income_interest = rec.net_annual_value
    #             rec.hra_exemption = 0
    #             rec.professional_tax = 0
    #             rec.actual_professional_tax = 0
    #             rec.projection_professional_tax = 0
    #             rec.employees_epf = 0
    #             rec.total_80c_payable = 0
    #             rec.allowed_rebate_under_80c = 0
    #             rec.final_amount_bank_interest = 0
    #             rec.final_amount_other_income = 0
    #             rec.final_income_from_bank_other = 0
    #             rec.actual_house_rent_paid = 0
    #             rec.house_loan_doc = False
    #             for slab in rec.slab_ids:
    #                 slab.investment = 0.0
    #                 slab.actual_amt = False
    #                 slab.document = False
    #             for ccd in rec.slab_ccd_ids:
    #                 ccd.investment = False
    #                 ccd.actual_amt = False
    #                 ccd.document = False
    #             for d in rec.slab_80d_ids:
    #                 d.investment = False
    #                 d.actual_amt = False
    #                 d.document = False
    #             for dd in rec.slab_80dd_ids:
    #                 dd.investment = False
    #                 dd.actual_amt = False
    #                 dd.document = False
    #                 dd.handicapped_percent = False
    #                 dd.actual_handicapped_percent = False
    #             for e in rec.slab_80e_ids:
    #                 e.investment = False
    #                 e.actual_amt = False
    #                 e.document = False
    #             for g in rec.slab_80g_ids:
    #                 g.investment = False
    #                 g.actual_amt = False
    #                 g.document = False
    #             for ddb in self.slab_80ddb_ids:
    #                 ddb.investment = False
    #                 ddb.actual_amt = False
    #                 ddb.document = False

    #             rec.taxable_salary_from_csm = rec.total_salary

    #             saving_rec = self.env['saving.master'].sudo().search([('code', '=', 'IP')])
    #             if rec.total_income_interest < 0:
    #                 temp_income_interest = rec.total_income_interest if -(
    #                     rec.total_income_interest) < saving_rec.rebate else -(saving_rec.rebate)
    #             else:
    #                 temp_income_interest = rec.total_income_interest

    #             rec.calculate_interest_payment = temp_income_interest
    #             rec.final_amount_other_income = rec.actual_income_from_other_sources if rec.actual_income_from_other_sources > 1 else rec.income_from_other_sources
    #             rec.final_amount_bank_interest = rec.actual_interest_received if rec.actual_interest_received > 1 else rec.interest_received_from_bank

    #             rec.income_from_bank_other = rec.interest_received_from_bank + rec.income_from_other_sources

    #             rec.actual_income_from_bank_other = rec.actual_interest_received + rec.actual_income_from_other_sources

    #             rec.final_income_from_bank_other = rec.final_amount_bank_interest + rec.final_amount_other_income
    #             # rec.standard_deduction = 52500 if (rec.taxable_salary_from_csm + rec.previous_employer_income) > 1550000 else 0
    #             rec.standard_deduction = 50000
    #             rec.final_amount = 0
    #             rec.total_taxable_salary = rec.taxable_salary_from_csm + rec.previous_employer_income - rec.standard_deduction
    #             temp_gross_total_income = (
    #                         rec.total_taxable_salary + rec.calculate_interest_payment + rec.final_income_from_bank_other)
    #             rec.gross_total_income = temp_gross_total_income if temp_gross_total_income > 0 else 0
    #             temp_taxable_income = rec.gross_total_income - rec.final_amount
    #             if (temp_taxable_income % 10) >= 5:
    #                 z = 10 - (temp_taxable_income % 10)
    #                 tax_amount = temp_taxable_income + z
    #             else:
    #                 tax_amount = temp_taxable_income - (temp_taxable_income % 10)
    #             rec.taxable_income = tax_amount if tax_amount > 0 else 0

    #             temp_tax_payable = 0

    #             if rec.taxable_income > 300000 and rec.taxable_income <= 600000:
    #                 tds_amount = rec.taxable_income - 300000
    #                 tax_slab = self.env['tax_slab'].sudo().search(
    #                     [('date_range', '=', rec.date_range.id), ('salary_from', '<=', rec.taxable_income),
    #                      ('salary_to', '>=', rec.taxable_income), ('tax_regime', '=', 'new_regime')], limit=1)
    #                 temp_tax_payable = tds_amount * tax_slab.tax_rate / 100
    #             elif rec.taxable_income > 600000 and rec.taxable_income <= 900000:

    #                 tds_above5 = rec.taxable_income - 600000
    #                 tax_slab = self.env['tax_slab'].sudo().search(
    #                     [('date_range', '=', rec.date_range.id), ('salary_from', '<=', rec.taxable_income),
    #                      ('salary_to', '>=', rec.taxable_income), ('tax_regime', '=', 'new_regime')], limit=1)
    #                 tds_above5percentage = tds_above5 * tax_slab.tax_rate / 100
    #                 tax_slab_1 = self.env['tax_slab'].sudo().search(
    #                     [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 300001),
    #                      ('salary_to', '<=', 600000), ('tax_regime', '=', 'new_regime')], limit=1)
    #                 tds_below5percentage = 300000 * tax_slab_1.tax_rate / 100
    #                 temp_tax_payable = tds_above5percentage + tds_below5percentage
    #             elif rec.taxable_income > 900000 and rec.taxable_income <= 1200000:
    #                 tds_above75 = rec.taxable_income - 900000
    #                 tax_slab = self.env['tax_slab'].sudo().search(
    #                     [('date_range', '=', rec.date_range.id), ('salary_from', '<=', rec.taxable_income),
    #                      ('salary_to', '>=', rec.taxable_income), ('tax_regime', '=', 'new_regime')], limit=1)
    #                 tds_above75percentage = tds_above75 * tax_slab.tax_rate / 100
    #                 tax_slab_1 = self.env['tax_slab'].sudo().search(
    #                     [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 600001),
    #                      ('salary_to', '<=', 900000), ('tax_regime', '=', 'new_regime')], limit=1)
    #                 tds_above5percentage = 300000 * tax_slab_1.tax_rate / 100
    #                 tax_slab_2 = self.env['tax_slab'].sudo().search(
    #                     [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 300001),
    #                      ('salary_to', '<=', 600000), ('tax_regime', '=', 'new_regime')], limit=1)
    #                 tds_below5percentage = 300000 * tax_slab_2.tax_rate / 100
    #                 temp_tax_payable = tds_above75percentage + tds_above5percentage + tds_below5percentage

    #             elif rec.taxable_income > 1200000 and rec.taxable_income <= 1500000:
    #                 tds_above10 = rec.taxable_income - 1200000
    #                 tax_slab = self.env['tax_slab'].sudo().search(
    #                     [('date_range', '=', rec.date_range.id), ('salary_from', '<=', rec.taxable_income),
    #                      ('salary_to', '>=', rec.taxable_income), ('tax_regime', '=', 'new_regime')], limit=1)
    #                 tds_above10percentage = tds_above10 * tax_slab.tax_rate / 100

    #                 tax_slab_1 = self.env['tax_slab'].sudo().search(
    #                     [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 900001),
    #                      ('salary_to', '<=', 1200000), ('tax_regime', '=', 'new_regime')], limit=1)
    #                 tds_above75percentage = 300000 * tax_slab_1.tax_rate / 100

    #                 tax_slab_2 = self.env['tax_slab'].sudo().search(
    #                     [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 600001),
    #                      ('salary_to', '<=', 900000), ('tax_regime', '=', 'new_regime')], limit=1)
    #                 tds_above5percentage = 300000 * tax_slab_2.tax_rate / 100

    #                 tax_slab_3 = self.env['tax_slab'].sudo().search(
    #                     [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 300001),
    #                      ('salary_to', '<=', 600000), ('tax_regime', '=', 'new_regime')], limit=1)
    #                 tds_below5percentage = 300000 * tax_slab_3.tax_rate / 100

    #                 temp_tax_payable = tds_above10percentage + tds_above75percentage + tds_above5percentage + tds_below5percentage

    #             elif rec.taxable_income > 1500000:
    #                 tds_above15 = rec.taxable_income - 1500000
    #                 tax_slab_15 = self.env['tax_slab'].sudo().search(
    #                     [('date_range', '=', rec.date_range.id), ('salary_from', '<=', rec.taxable_income),
    #                      ('salary_to', '>=', rec.taxable_income), ('tax_regime', '=', 'new_regime')], limit=1)
    #                 tds_above15percentage = tds_above15 * tax_slab_15.tax_rate / 100

    #                 tax_slab_12 = self.env['tax_slab'].sudo().search(
    #                     [('date_range', '=', rec.date_range.id), ('salary_from', '<=', 1200001),
    #                      ('salary_to', '>=', 1500000), ('tax_regime', '=', 'new_regime')], limit=1)
    #                 tds_above12percentage = 300000 * tax_slab_12.tax_rate / 100

    #                 tax_slab = self.env['tax_slab'].sudo().search(
    #                     [('date_range', '=', rec.date_range.id), ('salary_from', '<=', 900001),
    #                      ('salary_to', '>=', 1200000), ('tax_regime', '=', 'new_regime')], limit=1)
    #                 tds_above10percentage = 300000 * tax_slab.tax_rate / 100

    #                 tax_slab_1 = self.env['tax_slab'].sudo().search(
    #                     [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 600001),
    #                      ('salary_to', '<=', 900000), ('tax_regime', '=', 'new_regime')], limit=1)
    #                 tds_above75percentage = 300000 * tax_slab_1.tax_rate / 100

    #                 tax_slab_2 = self.env['tax_slab'].sudo().search(
    #                     [('date_range', '=', rec.date_range.id), ('salary_from', '>=', 300001),
    #                      ('salary_to', '<=', 600000), ('tax_regime', '=', 'new_regime')], limit=1)
    #                 tds_above5percentage = 300000 * tax_slab_2.tax_rate / 100

    #                 temp_tax_payable = tds_above15percentage + tds_above12percentage + tds_above10percentage + tds_above75percentage + tds_above5percentage

    #             rec.tax_payable = temp_tax_payable if temp_tax_payable > 0 else 0
    #             rec.rebate = rec.tax_payable if rec.taxable_income <= 700000 and rec.tax_payable > 0 else 0
    #             temp_net_tax_payable = rec.tax_payable - rec.rebate
    #             rec.net_tax_payable = temp_net_tax_payable if temp_net_tax_payable > 0 else 0
    #             tax_slab_rec = self.env['tax_slab'].sudo().search(
    #                 [('date_range', '=', rec.date_range.id), ('salary_from', '<=', rec.taxable_income),
    #                  ('salary_to', '>=', rec.taxable_income), ('tax_regime', '=', 'new_regime')], limit=1)
    #             rec.additional_sub_chrg = rec.calculate_round_amount(rec.net_tax_payable * tax_slab_rec.surcharge / 100)
    #             rec.additional_edu_cess = rec.calculate_round_amount(rec.net_tax_payable * tax_slab_rec.cess / 100)
    #             total_tax_payable = rec.net_tax_payable + rec.additional_sub_chrg + rec.additional_edu_cess
    #             if (total_tax_payable % 10) >= 5:
    #                 z = 10 - (total_tax_payable % 10)
    #                 var_tax_payable = total_tax_payable + z
    #             else:
    #                 var_tax_payable = total_tax_payable - (total_tax_payable % 10)
    #             rec.total_tax_payable = var_tax_payable
    #             rec.tax_recovered = tds + rec.tds_previous_employer
    #             temp_balance_tax_payable = rec.total_tax_payable - rec.tax_recovered
    #             rec.balance_tax_payable = temp_balance_tax_payable
    #             rec.monthly_tax_to_recover = rec.balance_tax_payable / remaining_month if rec.balance_tax_payable > 0 else 0
    #     print("------------------------------------------------------------------------------------------")

    @api.depends('state')
    def _compute_css(self):
        ir_config_params = self.env['ir.config_parameter'].sudo()
        actual_end_month = ir_config_params.get_param('tds.end_month') or False
        actual_end_day = ir_config_params.get_param('tds.end_day') or False
        if actual_end_month != False and actual_end_day != False:
            for record in self:
                actual_end_date = date(record.date_range.date_stop.year, int(actual_end_month), int(actual_end_day))
                if (record.state == 'approved' and not self.env.user.has_group(
                        'tds.group_report_manager_declaration')) or (
                        actual_end_date < datetime.today().date() and not self.env.user.has_group(
                    'tds.group_report_manager_declaration')):
                    record.test_css = '<style>.o_form_button_edit {display: none !important;}</style>'
                else:
                    record.test_css = False
        else:
            self.test_css = False

    def current_dt(self):
        return (datetime.now().strftime("%d-%m-%Y"))

    def recent_time(self):
        return str(datetime.now().strftime("%H:%M:%S")) + "+5'30'"

    def current_date(self):
        today_date = date.today()
        return today_date

    def digital_signature(self):
        digital_sign = self.env['digital_sign'].sudo().search([], limit=1)
        return digital_sign.digital_signat

    def employer_pan(self):
        ir_config_parameter = self.env['ir.config_parameter'].sudo()
        company_pan = ir_config_parameter.get_param('tds.company_pan') or ''
        return company_pan

    def employer_tan(self):
        ir_config_parameter = self.env['ir.config_parameter'].sudo()
        company_tan = ir_config_parameter.get_param('tds.company_tan') or ''
        return company_tan


    @api.constrains('temp_interest_payment')
    def check_house_loan_interest(self):
        for rec in self:
            if rec.temp_interest_payment > 200000:
                raise ValidationError("Interest on house loan can not be more than 2LK.")

    @api.constrains('temp_interest_payment')
    def check_house_loan_interest(self):
        if self.house_rent_paid:
            if self.house_rent_paid > 100000:
                if not self.pan_of_landlord:
                    raise ValidationError("Please enter Landlord Pancard Number!!!")
                
    # @api.constrains('income_from_pre_employer_doc', 'tds_doc', 'pan_landlord', 'house_loan_doc')
    # def _check_doc_size_and_type(self):
    #     allowed_file_list = ['application/pdf','image/jpeg','image/png','image/jpg']
    #     for record in self:
    #         if record.income_from_pre_employer_doc:
    #             acp_size = ((len(record.income_from_pre_employer_doc) * 3 / 4) / 1024) / 1024
    #             mimetype = guess_mimetype(base64.b64decode(record.income_from_pre_employer_doc))
    #             if str(mimetype) not in allowed_file_list:
    #                 raise ValidationError("Only PDF/jpg/jpeg/png format is allowed")
    #             if acp_size > 5:
    #                 raise ValidationError("Document allowed size less than 5MB")

    #             if record.tds_doc:
    #                 acp_size = ((len(record.tds_doc) * 3 / 4) / 1024) / 1024
    #                 mimetype = guess_mimetype(base64.b64decode(record.tds_doc))
    #                 if str(mimetype) not in allowed_file_list:
    #                     raise ValidationError("Only PDF/jpg/jpeg/png format is allowed")
    #                 if acp_size > 5:
    #                     raise ValidationError("Document allowed size less than 5MB")

    #             if record.pan_landlord:
    #                 acp_size = ((len(record.pan_landlord) * 3 / 4) / 1024) / 1024
    #                 mimetype = guess_mimetype(base64.b64decode(record.pan_landlord))
    #                 if str(mimetype) not in allowed_file_list:
    #                     raise ValidationError("Only PDF/jpg/jpeg/png format is allowed")
    #                 if acp_size > 5:
    #                     raise ValidationError("Document allowed size less than 5MB")

    #                 if record.house_loan_doc:
    #                     acp_size = ((len(record.house_loan_doc) * 3 / 4) / 1024) / 1024
    #                     mimetype = guess_mimetype(base64.b64decode(record.house_loan_doc))
    #                     if str(mimetype) not in allowed_file_list:
    #                         raise ValidationError("Only PDF/jpg/jpeg/png format is allowed")
    #                     if acp_size > 5:
    #                         raise ValidationError("Document allowed size less than 5MB")

    @api.constrains('income_from_pre_employer_doc')
    def _check_doc_size_and_type1(self):
        allowed_file_list = ['application/pdf','image/jpeg','image/png','image/jpg']
        for record in self:
            if record.income_from_pre_employer_doc:
                acp_size = ((len(record.income_from_pre_employer_doc) * 3 / 4) / 1024) / 1024
                mimetype = guess_mimetype(base64.b64decode(record.income_from_pre_employer_doc))
                if str(mimetype) not in allowed_file_list:
                    raise ValidationError("Only PDF/jpg/jpeg/png format is allowed")
                if acp_size > 5:
                    raise ValidationError("Document allowed size less than 5MB")
    
    @api.constrains('tds_doc')
    def _check_doc_size_and_type2(self):
        allowed_file_list = ['application/pdf','image/jpeg','image/png','image/jpg']
        for record in self:
            if record.tds_doc:
                acp_size = ((len(record.tds_doc) * 3 / 4) / 1024) / 1024
                mimetype = guess_mimetype(base64.b64decode(record.tds_doc))
                if str(mimetype) not in allowed_file_list:
                    raise ValidationError("Only PDF/jpg/jpeg/png format is allowed")
                if acp_size > 5:
                    raise ValidationError("Document allowed size less than 5MB")
        
    @api.constrains('pan_landlord')
    def _check_doc_size_and_type3(self):
        allowed_file_list = ['application/pdf','image/jpeg','image/png','image/jpg']
        for record in self:
            if record.pan_landlord:
                acp_size = ((len(record.pan_landlord) * 3 / 4) / 1024) / 1024
                mimetype = guess_mimetype(base64.b64decode(record.pan_landlord))
                if str(mimetype) not in allowed_file_list:
                    raise ValidationError("Only PDF/jpg/jpeg/png format is allowed")
                if acp_size > 5:
                    raise ValidationError("Document allowed size less than 5MB")
                
    @api.constrains('house_loan_doc')
    def _check_doc_size_and_type4(self):
        allowed_file_list = ['application/pdf','image/jpeg','image/png','image/jpg']
        for record in self:
             if record.house_loan_doc:
                    acp_size = ((len(record.house_loan_doc) * 3 / 4) / 1024) / 1024
                    mimetype = guess_mimetype(base64.b64decode(record.house_loan_doc))
                    if str(mimetype) not in allowed_file_list:
                        raise ValidationError("Only PDF/jpg/jpeg/png format is allowed")
                    if acp_size > 5:
                        raise ValidationError("Document allowed size less than 5MB")

    @api.constrains('interest_received_doc')
    def _check_doc_size_and_type5(self):
        allowed_file_list = ['application/pdf','image/jpeg','image/png','image/jpg']
        for record in self:
             if record.interest_received_doc:
                    acp_size = ((len(record.interest_received_doc) * 3 / 4) / 1024) / 1024
                    mimetype = guess_mimetype(base64.b64decode(record.interest_received_doc))
                    if str(mimetype) not in allowed_file_list:
                        raise ValidationError("Only PDF/jpg/jpeg/png format is allowed")
                    if acp_size > 5:
                        raise ValidationError("Document allowed size less than 5MB")
                    
    @api.constrains('income_from_other_sources_doc')
    def _check_doc_size_and_type6(self):
        allowed_file_list = ['application/pdf','image/jpeg','image/png','image/jpg']
        for record in self:
             if record.income_from_other_sources_doc:
                    acp_size = ((len(record.income_from_other_sources_doc) * 3 / 4) / 1024) / 1024
                    mimetype = guess_mimetype(base64.b64decode(record.income_from_other_sources_doc))
                    if str(mimetype) not in allowed_file_list:
                        raise ValidationError("Only PDF/jpg/jpeg/png format is allowed")
                    if acp_size > 5:
                        raise ValidationError("Document allowed size less than 5MB")
                    
    @api.constrains('pan_landlord')
    def _check_doc_size_and_type7(self):
        allowed_file_list = ['application/pdf','image/jpeg','image/png','image/jpg']
        for record in self:
             if record.pan_landlord:
                    acp_size = ((len(record.pan_landlord) * 3 / 4) / 1024) / 1024
                    mimetype = guess_mimetype(base64.b64decode(record.pan_landlord))
                    if str(mimetype) not in allowed_file_list:
                        raise ValidationError("Only PDF/jpg/jpeg/png format is allowed")
                    if acp_size > 5:
                        raise ValidationError("Document allowed size less than 5MB")
                    
    @api.onchange('tax_regime')
    def onchange_tax_regime(self):
        if self.tax_regime == 'old_regime':
            prvs_tds = self.env['hr.declaration'].sudo().search(
                [('employee_id', '=', self.employee_id.id), ('tax_regime', '=', 'old_regime'),
                 ('state', '=', 'approved')])
            if prvs_tds:
                previous_tds = prvs_tds.filtered(
                    lambda x: (self.date_range.date_start - x.date_range.date_stop).days == 1)
                if previous_tds:
                    self.house_rent_paid = previous_tds.actual_house_rent_paid
                    self.gross_annual_value = previous_tds.gross_annual_value
                    self.municipal_taxes = previous_tds.municipal_taxes
                    self.temp_interest_payment = previous_tds.actual_interest_payment
                    self.income_from_other_sources = previous_tds.actual_income_from_other_sources
                    for slab in self.slab_ids:
                        slab.investment = previous_tds.slab_ids.filtered(
                            lambda x: slab.saving_master.code == x.saving_master.code).actual_amt
                    for ccd in self.slab_ccd_ids:
                        ccd.investment = previous_tds.slab_ccd_ids.filtered(
                            lambda x: ccd.saving_master.code == x.saving_master.code).actual_amt
                    for d in self.slab_80d_ids:
                        d.investment = previous_tds.slab_80d_ids.filtered(
                            lambda x: d.saving_master.code == x.saving_master.code).actual_amt
                    for dd in self.slab_80dd_ids:
                        dd.handicapped_percent = previous_tds.slab_80dd_ids.filtered(
                            lambda x: dd.saving_master.code == x.saving_master.code).handicapped_percent
                    for e in self.slab_80e_ids:
                        e.investment = previous_tds.slab_80e_ids.filtered(
                            lambda x: e.saving_master.code == x.saving_master.code).actual_amt
                    for g in self.slab_80g_ids:
                        g.investment = previous_tds.slab_80g_ids.filtered(
                            lambda x: g.saving_master.code == x.saving_master.code).actual_amt
                    for ddb in self.slab_80ddb_ids:
                        ddb.investment = previous_tds.slab_80ddb_ids.filtered(
                            lambda x: ddb.saving_master.code == x.saving_master.code).actual_amt
        elif self.tax_regime == 'new_regime':
            self.pan_landlord = False
            self.pan_of_landlord = False
            self.house_rent_paid = False
            self.actual_house_rent_paid = False
            self.gross_annual_value = False
            self.municipal_taxes = False
            self.temp_interest_payment = False
            self.actual_interest_payment = False
            self.hra_by_employee = False
            self.excess_10_percent = False
            self.lta_spent_by_employee = False
            self.actual_lta_spent_by_employee = False
            self.final_lta_spent_by_employee = False
            self.lta_document = False
            self.prof_persuit_spent_by_employee = False
            self.actual_prof_persuit_spent_by_employee = False
            self.final_prof_persuit_spent_by_employee = False
            self.prof_persuit_document = False
            self.allowed_rebate_under_80c = False
            self.allowed_rebate_under_80ccd = False
            self.allowed_rebate_under_80d = False
            self.allowed_rebate_under_80ddb = False
            self.allowed_rebate_under_80dd = False
            self.allowed_rebate_under_80e = False
            self.allowed_rebate_under_80g = False
            self.final_amount_bank_interest = 0
            self.final_amount_other_income = 0
            self.final_income_from_bank_other = 0
            for slab in self.slab_ids:
                slab.investment = 0.0
                slab.actual_amt = False
                slab.document = False
            for ccd in self.slab_ccd_ids:
                ccd.investment = False
                ccd.actual_amt = False
                ccd.document = False
            for d in self.slab_80d_ids:
                d.investment = False
                d.actual_amt = False
                d.document = False
            for dd in self.slab_80dd_ids:
                dd.investment = False
                dd.actual_amt = False
                dd.document = False
                dd.handicapped_percent = False
                dd.actual_handicapped_percent = False
            for e in self.slab_80e_ids:
                e.investment = False
                e.actual_amt = False
                e.document = False
            for g in self.slab_80g_ids:
                g.investment = False
                g.actual_amt = False
                g.document = False
            for ddb in self.slab_80ddb_ids:
                ddb.investment = False
                ddb.actual_amt = False
                ddb.document = False

    @api.constrains('pan_of_landlord')
    def check_pan_of_landlord(self):
        for record in self:
            if record.pan_of_landlord:
                if re.match("[A-Z]{5}[0-9]{4}[A-Z]{1}",
                            str(record.pan_of_landlord)) == None:  # modified to allow + and space 24 april
                    raise ValidationError("Please Enter Valid PAN of House Owner")

    @api.depends('slab_80dd_ids', 'slab_ids', 'slab_ccd_ids')
    def _compute_limit(self):
        for rec in self:
            saving_80c = self.env['saving.master'].sudo().search([('it_rule.code', '=', '80_c')])
            for res in saving_80c:
                rec.slab_80c_limit += res.rebate
            saving_8080ccd = self.env['saving.master'].sudo().search([('it_rule.code', '=', '80ccd')])
            for ccd in saving_8080ccd:
                rec.slab_80ccd_limit += ccd.rebate
            saving_80dd = self.env['saving.master'].sudo().search([('it_rule.code', '=', '80dd')])
            for dd in saving_80dd:
                rec.slab_80dd_limit += dd.rebate

    @api.onchange('gross_annual_value')
    def validate_gross_annual_value(self):
        for rec in self:
            if rec.gross_annual_value <= 0:
                rec.municipal_taxes = 0

    @api.onchange('previous_employer_income')
    def onchange_income(self):
        for rec in self:
            if rec.previous_employer_income == 0:
                rec.tds_previous_employer = 0
                rec.tds_doc = 0

    @api.constrains('slab_80dd_ids', 'slab_ids', 'slab_80d_ids', 'slab_80g_ids', 'slab_80e_ids', 'slab_ccd_ids',
                    'slab_80ddb_ids')
    def validate_document(self):
        for rec in self.slab_80dd_ids:
            if rec.actual_handicapped_percent > 40 and rec.document == False:
                raise ValidationError(f"Kindly Upload the Document for {rec.saving_master.saving_type} under 80DD.")
            if rec.actual_handicapped_percent > 100 or rec.actual_handicapped_percent < 0 or rec.handicapped_percent > 100 or rec.handicapped_percent < 0:
                raise ValidationError("Disability Percentage Should be in Between 1-100.")
        for rec in self.slab_ids:
            if rec.actual_amt > 0 and rec.document == False:
                raise ValidationError(f"Kindly Upload the Document for  {rec.saving_master.saving_type} under 80C.")
        for rec in self.slab_80d_ids:
            if rec.actual_amt > 0 and rec.document == False:
                raise ValidationError(f"Kindly Upload the Document for {rec.saving_master.saving_type} under 80D.")
        for rec in self.slab_80g_ids:
            if rec.actual_amt > 0 and rec.document == False:
                raise ValidationError(f"Kindly Upload the Document for {rec.saving_master.saving_type} under 80G.")
        for rec in self.slab_80e_ids:
            if rec.actual_amt > 0 and rec.document == False:
                raise ValidationError(f"Kindly Upload the Document for {rec.saving_master.saving_type} under 80E.")
        for rec in self.slab_ccd_ids:
            if rec.actual_amt > 0 and rec.document == False:
                raise ValidationError(f"Kindly Upload the Document for {rec.saving_master.saving_type} under 80CCD.")
        for rec in self.slab_80ddb_ids:
            if rec.actual_amt > 0 and rec.document == False:
                raise ValidationError(f"Kindly Upload the Document for {rec.saving_master.saving_type} under 80DDB.")

    @api.constrains('previous_employer_income', 'tds_previous_employer')
    def check_tds_amount(self):
        for rec in self:
            if rec.tds_previous_employer and rec.previous_employer_income:
                if rec.tds_previous_employer >= rec.previous_employer_income:
                    raise ValidationError("TDS amount should be less than previous employer income.")

    @api.depends('date_range')
    def _cheak_month(self):
        for rec in self:
            # current_month = datetime.now().month
            ir_config_params = self.env['ir.config_parameter'].sudo()
            start_date = ir_config_params.get_param('tds.actual_start_date') or False
            end_date = ir_config_params.get_param('tds.actual_end_date') or False
            actual_start_month = ir_config_params.get_param('tds.start_month') or False
            actual_start_day = ir_config_params.get_param('tds.start_day') or False
            actual_end_month = ir_config_params.get_param('tds.end_month') or False
            actual_end_day = ir_config_params.get_param('tds.end_day') or False
            if actual_start_month != False and actual_start_day != False and actual_end_month != False and actual_end_day != False:
                actual_start_date = date(rec.date_range.date_stop.year, int(actual_start_month), int(actual_start_day))
                actual_end_date = date(rec.date_range.date_stop.year, int(actual_end_month), int(actual_end_day))
                rec.check_month = True if actual_start_date <= datetime.today().date() <= actual_end_date else False
                rec.invisible = True if datetime.today().date() >= actual_start_date else False
            else:
                actual_start_date = False
                actual_end_date = False
                rec.check_month = False
                rec.invisible = False

            # if start_date != False and end_date != False:
            #     rec.check_month = True  if datetime.today().date() >= datetime.strptime(start_date, "%Y-%m-%d").date() and datetime.today().date() <= datetime.strptime(end_date, "%Y-%m-%d").date() else False
            if rec.date_of_joining >= rec.date_range.date_start:
                rec.check_previous_emp_income = True
            else:
                rec.check_previous_emp_income = False
            rec.tds_by_company = rec.tax_recovered - rec.tds_previous_employer if rec.tax_recovered - rec.tds_previous_employer > 0 else 0

    _sql_constraints = [
        ('date_range_unique', 'unique(date_range,employee_id)', 'This Financial Year is already exist.'),
    ]

    def hr_declaration_actual_doc_add(self):
        ir_config_params = self.env['ir.config_parameter'].sudo()
        start_date = ir_config_params.get_param('tds.actual_start_date') or False
        end_date = ir_config_params.get_param('tds.actual_end_date') or False
        if start_date != False and end_date != False:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            start = datetime.strptime(start_date, "%Y-%m-%d")
            if start < datetime.now() < end:
                current_fiscal = self.env['account.fiscalyear'].search(
                    [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
                declaration = self.env['hr.declaration'].search(
                    [('date_range', '=', current_fiscal.id), ('state', '!=', 'approved')])
                for rec in declaration:
                    slab_80c = rec.slab_ids.filtered(lambda x: x.investment > 0 and x.document != False)
                    slab_80dd_ids = rec.slab_80dd_ids.filtered(lambda x: x.investment > 0 and x.document != False)
                    slab_80d_ids = rec.slab_80d_ids.filtered(lambda x: x.investment > 0 and x.document != False)
                    slab_80g_ids = rec.slab_80g_ids.filtered(lambda x: x.investment > 0 and x.document != False)
                    slab_80e_ids = rec.slab_80e_ids.filtered(lambda x: x.investment > 0 and x.document != False)
                    slab_ccd_ids = rec.slab_ccd_ids.filtered(lambda x: x.investment > 0 and x.document != False)
                    slab_80ddb_limit = rec.slab_80ddb_limit.filtered(lambda x: x.investment > 0 and x.document != False)
                    if slab_80c or slab_80dd_ids or slab_80d_ids or slab_80g_ids or slab_80e_ids or slab_ccd_ids or slab_80ddb_limit or (
                            rec.actual_house_rent_paid > 0 and rec.pan_landlord != False) or (
                            rec.house_loan_doc != False and rec.temp_interest_payment > 0):
                        pass
                    else:
                        inform_template = self.env.ref('tds.actual_doc_verification_template')
                        inform_template.with_context(end_date=end.strftime("%d-%b-%Y"),
                                                     current_fiscal=current_fiscal.name).send_mail(rec.id,
                                                                                                   notif_layout="kwantify_theme.csm_mail_notification_light")
    @api.model
    def create(self, vals):
        print(vals, 'DDDDDDD')
        fy_month = self.env['ir.config_parameter'].sudo().get_param('tds.month')
        fy_day = self.env['ir.config_parameter'].sudo().get_param('tds.day')
        current_date = date.today()
        if fy_day and fy_month:
            fy_date = date(date.today().year, int(fy_month), int(fy_day))
            if fy_date and fy_date >= current_date:
                raise ValidationError(f"IT Declaration can be filled after {fy_date.strftime('%d-%b-%Y')}.")
        new_record = super(HrDeclaration, self).create(vals)
        # new_record.button_compute_tax()
        return new_record

    def calculate_round_amount(self, amount):
        if amount - int(amount) >= 0.5:
            return ceil(amount)
        else:
            return round(amount)

    def btn_take_action_from_tree(self):
        rc = {
            'name': 'IT Declaration',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(self.env.ref('tds.hr_declaration_bifurcation_view_form').id, 'form')],
            'view_id': self.env.ref('tds.hr_declaration_bifurcation_view_form').id,
            'res_model': 'hr.declaration',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'self',
            'context': {'edit': 1, 'create': 0, 'delete': 0},
            # 'flags'     : { 'mode': 'edit',},

        }
        return rc

    def button_take_action(self):
        rc = {
            'name': 'IT Declaration',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(self.env.ref('tds.hr_declaration_bifurcation_view_form').id, 'form')],
            'view_id': self.env.ref('tds.hr_declaration_bifurcation_view_form').id,
            'res_model': 'hr.declaration',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'self',
            'context': {'hide_button': 1}
        }
        return rc

    def button_view_declarations(self):
        rc = {
            'name': 'View Declarations',
            'view_type': 'form',
            # 'view_mode': 'form',
            'views': [(self.env.ref('tds.hr_declaration_bifurcation_view_form').id, 'form')],
            'view_id': self.env.ref('tds.hr_declaration_bifurcation_view_form').id,
            'res_model': 'hr.declaration',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'self',
        }
        return rc

    @api.depends('employee_id')
    def _compute_pan_num(self):
        for rec in self:
            # if rec.employee_id.pan_no:
            print(rec.employee_id.pan_no, 'DEEPAK')
            rec.pan_number = rec.employee_id.pan_no.upper() if rec.employee_id.pan_no else ''

            # contract = self.env['hr.contract'].sudo().search(
            #     [('state', '=', 'open'), ('employee_id', '=', rec.employee_id.id)])
            # print("contract----------------------------------------------------",contract)
            # if contract:
            #     rec.bank_account = contract.bank_account if contract.bank_account else ''
            #     rec.bank_name = contract.personal_bank_name if contract.personal_bank_name else ''
            # else:
            rec.bank_account = rec.employee_id.bank_account_id.acc_number if rec.employee_id.bank_account_id else ''
            rec.bank_name = rec.employee_id.bank_account_id.bank_id.name if rec.employee_id.bank_account_id.bank_id else ''

    def default_get(self, fields_list):
        val = super(HrDeclaration, self).default_get(fields_list)
        for rec in fields_list:

            slab_ids_lst = []
            saving_rec = self.env['saving.master'].sudo().search([('it_rule.code', '=', '80_c')])
            for res in saving_rec:
                slab_ids_lst.append((0, 0, {
                    'deduction_id': 'slab_80_declaration',
                    'it_rule': res.it_rule.id,
                    'saving_master': res.id,
                    'investment': 0,
                    'actual_amt': 0,
                }))
                val['slab_ids'] = slab_ids_lst
            slab_lst = []
            housing_loan_ids = []
            saving_rec = self.env['saving.master'].sudo().search([('it_rule.code', '=', '80ee')])
            for res in saving_rec:
                housing_loan_ids.append((0, 0, {
                    'deduction_id': 'Tax Benefits on Home Loan',
                    'it_rule': res.it_rule.id,
                    'saving_master': res.id,
                    'investment': 0,
                    'actual_amt': 0,
                }))
                val['housing_loan_ids'] = housing_loan_ids
            slab_80d_ids = []
            saving_rec = self.env['saving.master'].sudo().search([('it_rule.code', '=', '80d')])
            for res in saving_rec:
                slab_80d_ids.append((0, 0, {
                    'deduction_id': 'Medical Insurance Premium paid',
                    'it_rule': res.it_rule.id,
                    'saving_master': res.id,
                    'investment': 0,
                    'actual_amt': 0,
                }))
                val['slab_80d_ids'] = slab_80d_ids
            slab_80g_ids = []
            saving_rec = self.env['saving.master'].sudo().search([('it_rule.code', '=', '80G')])
            for res in saving_rec:
                slab_80g_ids.append((0, 0, {
                    'deduction_id': 'Deductions on Donations',
                    'it_rule': res.it_rule.id,
                    'saving_master': res.id,
                    'investment': 0,
                    'actual_amt': 0,
                }))
                val['slab_80g_ids'] = slab_80g_ids
            slab_80e_ids = []
            saving_rec = self.env['saving.master'].sudo().search([('it_rule.code', '=', '80e')])
            for res in saving_rec:
                slab_80e_ids.append((0, 0, {
                    'deduction_id': 'Tax benefit on Education Loan (80E)',
                    'it_rule': res.it_rule.id,
                    'saving_master': res.id,
                    'investment': 0,
                    'actual_amt': 0,
                }))
                val['slab_80e_ids'] = slab_80e_ids
            slab_ccd_ids = []
            saving_rec = self.env['saving.master'].sudo().search([('it_rule.code', '=', '80ccd')])
            for res in saving_rec:
                slab_ccd_ids.append((0, 0, {
                    'deduction_id': 'Contribution to National Pension Scheme(NPS)',
                    'it_rule': res.it_rule.id,
                    'saving_master': res.id,
                    'investment': 0,
                    'actual_amt': 0,
                }))
                val['slab_ccd_ids'] = slab_ccd_ids
            slab_80dd_ids = []
            saving_rec = self.env['saving.master'].sudo().search([('it_rule.code', '=', '80dd')])
            for res in saving_rec:
                slab_80dd_ids.append((0, 0, {
                    'deduction_id': 'Deductions on Medical Expenditure for a Handicapped Relative',
                    'it_rule': res.it_rule.id,
                    'saving_master': res.id,
                    'investment': 0,
                }))
                val['slab_80dd_ids'] = slab_80dd_ids
            slab_80ddb_ids = []
            saving_rec = self.env['saving.master'].sudo().search([('it_rule.code', '=', '80ddb')])
            for res in saving_rec:
                slab_80ddb_ids.append((0, 0, {
                    'deduction_id': 'slab_80ddb_declaration',
                    'it_rule': res.it_rule.id,
                    'saving_master': res.id,
                    'investment': 0,
                }))
                val['slab_80ddb_ids'] = slab_80ddb_ids
        return val

    def button_approved(self):
        for rec in self:
            # rec.button_compute_tax()
            inform_template = self.env.ref('tds.compute_tax_approve_mail')
            inform_template.send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            rec.write({'state': 'approved'})
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    def button_reset_to_draft(self):
        ir_config_params = self.env['ir.config_parameter'].sudo()
        actual_end_month = ir_config_params.get_param('tds.end_month') or False
        actual_end_day = ir_config_params.get_param('tds.end_day') or False
        if actual_end_month != False and actual_end_day != False:
            for record in self:
                actual_end_date = date(record.date_range.date_stop.year, int(actual_end_month), int(actual_end_day))
                if record.state == 'approved' and actual_end_date >= datetime.today().date():
                    record.state = 'draft'
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    }
                else:
                    raise ValidationError("Cann't revert the approved TDS")

    def fillup_it_declaration(self):
        contrct = self.env['hr.contract'].sudo().search(
            [('state', '=', 'open'), ('employee_id.active', '=', True), ('employee_id.enable_payroll', '=', 'yes')])
        if contrct:
            for cnt in contrct:
                # current_ctc = cnt.wage * 12
                # if current_ctc >= 500000:
                search_id = self.env['hr.declaration'].search(
                    [('employee_id', '=', cnt.employee_id.id),
                     ('date_range.date_start', '<=', datetime.today().date()),
                     ('date_range.date_stop', '>=', datetime.today().date())])
                if not search_id:
                    ir_config_params = self.env['ir.config_parameter'].sudo()
                    send_mail_config = ir_config_params.get_param('tds.run_esi_schedule_start_date') or False
                    dt_from = datetime.strptime(str(send_mail_config), DEFAULT_SERVER_DATE_FORMAT).date()
                    from_day = int(ir_config_params.get_param('tds.from_day'))
                    to_day = int(ir_config_params.get_param('tds.to_day'))
                    current_day = datetime.now().day
                    if from_day <= current_day <= to_day:
                        current_fiscal = self.env['account.fiscalyear'].search(
                            [('date_start', '<=', datetime.today().date()),
                             ('date_stop', '>=', datetime.today().date())], limit=1)
                        current_date = datetime.today().date()
                        end_date = current_date.replace(day=to_day)
                        formatted_end_date = end_date.strftime("%d-%b-%Y")
                        email = cnt.employee_id.work_email
                        name = cnt.employee_id.name
                        fy = current_fiscal.name
                        extra_params = {'email': email, 'name': name, 'date': formatted_end_date, 'fy': fy}
                        self.env['hr.contract'].contact_send_custom_mail(res_id=cnt.id,
                                                                         notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                         template_layout='tds.user_tds_fillup_mail_template',
                                                                         ctx_params=extra_params,
                                                                         description="IT Declaration Reminder")

    def calculate_80d(self):
        for rec in self:
            return rec.prl_hlth_dependant + rec.health_insurance_parent


class SlabDeclarations(models.Model):
    _name = 'declaration.slab'
    _description = 'declaration.slab'

    def set_80_c_rules(self):
        current_rule = self.env['hr.itrule'].search([('code', '=', '80_c')])
        return current_rule

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
        ('Contribution to National Pension Scheme(NPS)', 'Contribution to National Pension Scheme(NPS)'),
    ], string='Deduction', default='slab_80_declaration')

    slab_id = fields.Many2one('hr.declaration', string='Slab', track_visibility='onchange')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section', domain=[('code', '=', '80_c')],
                              default=set_80_c_rules)
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Declaration Amount', digits=dp.get_precision('tds'))
    actual_amt = fields.Float(string='Actual Amount', digits=dp.get_precision('tds'))
    document = fields.Binary(string='Document', attachment=True)
    file_name = fields.Char(string='Document Name')

    @api.onchange('investment', 'actual_amt')
    def onchange_number_valid(self):
        print(self.investment,self.actual_amt, 'XXXXXXXX')
        if not self.investment:
            self.investment = 0.0
        if self.investment:
            val = self.investment
            print(val)
            print(isinstance(val, (int, float)), 'DDPPPPPPPP')
            if isinstance(val, (int, float)):
                pass
            if not isinstance(val, (int, float)):
                raise ValidationError("Please Enter Integer/Float Value only !!.")

    def unlink(self):
        return super(SlabDeclarations, self).unlink()

    @api.constrains('document')
    def _check_doc_size_and_type(self):
        allowed_file_list = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
        for record in self:
            if record.document:
                acp_size = ((len(record.document) * 3 / 4) / 1024) / 1024
                mimetype = guess_mimetype(base64.b64decode(record.document))
                if str(mimetype) not in allowed_file_list:
                    raise ValidationError("Only PDF/jpg/jpeg/png format is allowed under section 80C")
                if acp_size > 5:
                    raise ValidationError("Document allowed size less than 5MB under section 80C")

    # @api.model
    # def create(self, values):
    #     if self.investment:
    #         val = self.investment
    #         if not isinstance(val, (int, float)):
    #             raise ValidationError("Please Enter Integer/Float Value only !!.")
    #     res = super(SlabDeclarations, self).create(values)
    #     # self.env.user.notify_success("Record added successfully.")
    #     return res
    #
    # def write(self, values):
    #     if self.investment:
    #         val = self.investment
    #         if not isinstance(val, (int, float)):
    #             raise ValidationError("Please Enter Integer/Float Value only !!.")
    #     res = super(SlabDeclarations, self).write(values)
    #     # self.env.user.notify_success("Record updated successfully.")
    #     return res


class MedicalDeclarations(models.Model):
    _name = 'housing_loan'
    _description = 'housing_loan'

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
        ('Contribution to National Pension Scheme(NPS)', 'Contribution to National Pension Scheme(NPS)'),
    ], string='Deduction', default='Medical Insurance Premium paid')

    housing_loan_id = fields.Many2one('hr.declaration', string='Medical')
    saving_master = fields.Many2one('saving.master', string='Saving Type', domain=['|', ('saving_type', '=', 'LIC'), (
        'name', '=', 'Contribution to any statuotory/Public Provident Fund')])
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')
    investment = fields.Float(string='Declaration Amount', digits=dp.get_precision('tds'))
    actual_amt = fields.Float(string='Actual Amount', digits=dp.get_precision('tds'))
    document = fields.Binary(string='Document', attachment=True)
    file_name = fields.Char(string='Document Name')
    # status = fields.Selection(related='housing_loan_id.state')
    # check_month = fields.Boolean(string='Month', compute='_cheak_month')

    # @api.depends('saving_master')
    # def _cheak_month(self):
    #     for rec in self:
    #         current_month = datetime.now().month
    #         rec.check_month = True if current_month == 3 else False

    def unlink(self):
        return super(MedicalDeclarations, self).unlink()


class SavingsMaster(models.Model):
    _name = 'saving.master'
    _description = 'Saving Master'
    _order = 'saving_type'

    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')
    saving_type = fields.Char('Saving Type')
    description = fields.Text('Description')
    rebate = fields.Float('Max. Allowed Limit', store=True)
    code = fields.Char('Code')

    @api.depends('saving_type')
    def name_get(self):
        res = []
        name = ''
        for record in self:
            if record.saving_type:
                name = str(record.saving_type)
            else:
                name = 'Savings'
            res.append((record.id, name))
        return res

    @api.model
    def create(self, vals):
        new_record = super(SavingsMaster, self).create(vals)
        for rec in new_record:
            slab_ids_lst = []
            if rec.it_rule.code == '80_c':
                slab_rec = self.env['declaration.slab'].sudo().search([])
                slab_rec.create({'deduction_id': 'slab_80_declaration',
                                 'it_rule': rec.it_rule.id,
                                 'saving_master': rec.id, })
        return new_record

    @api.constrains('saving_type', 'code', 'it_rule')
    def validate_name_code(self):
        for rec in self:
            # record = self.env['saving.master'].sudo().search([('saving_type', '=', rec.saving_type)]) - self
            # if record:
            #     raise ValidationError(f"{record.saving_type} Already Exist.")
            code_rec = self.env['saving.master'].sudo().search([('code', '=', rec.code)]) - self
            if code_rec:
                raise ValidationError(f"{code_rec.code} Already Exist.")
            saving_rec = self.env['saving.master'].sudo().search(
                [('saving_type', '=', rec.saving_type), ('it_rule', '=', rec.it_rule.id),
                 ('code', '=', rec.code)]) - self
            if saving_rec:
                raise ValidationError(f"This record is Already Exist.")


class SlabDeclarations80_d(models.Model):
    _name = 'slab_declaration_80d'
    _description = 'slab 80 declaration'

    def set_80d_rules(self):
        current_rule = self.env['hr.itrule'].search([('code', '=', '80d')])
        return current_rule

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
        ('Contribution to National Pension Scheme(NPS)', 'Contribution to National Pension Scheme(NPS)'),
    ], string='Deduction', default='slab_80_declaration')

    slab_80d_id = fields.Many2one('hr.declaration', string='Slab')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section', domain=[('code', '=', '80d')],
                              default=set_80d_rules)
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Declaration Amount', digits=dp.get_precision('tds'))
    actual_amt = fields.Float(string='Actual Amount', digits=dp.get_precision('tds'))
    document = fields.Binary(string='Document', attachment=True)
    file_name = fields.Char(string='Document Name')

    @api.constrains('document')
    def _check_doc_size_and_type(self):
        allowed_file_list = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
        for record in self:
            if record.document:
                acp_size = ((len(record.document) * 3 / 4) / 1024) / 1024
                mimetype = guess_mimetype(base64.b64decode(record.document))
                if str(mimetype) not in allowed_file_list:
                    raise ValidationError("Only PDF/jpg/jpeg/png format is allowed under section 80D(Health Insurance)")
                if acp_size > 5:
                    raise ValidationError("Document allowed size less than 5MB under section 80D(Health Insurance)")


class SlabDeclarations_80g(models.Model):
    _name = 'declaration_slab_80g'
    _description = 'declaration.slab80g'

    def set_80G_rules(self):
        current_rule = self.env['hr.itrule'].search([('code', '=', '80G')])
        return current_rule

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
        ('Contribution to National Pension Scheme(NPS)', 'Contribution to National Pension Scheme(NPS)'),
    ], string='Deduction', default='slab_80_declaration')

    slab_80g_id = fields.Many2one('hr.declaration', string='Slab')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section', domain=[('code', '=', '80G')],
                              default=set_80G_rules)
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Declared Amount', digits=dp.get_precision('tds'))
    actual_amt = fields.Float(string='Actual Amount', digits=dp.get_precision('tds'))
    document = fields.Binary(string='Document', attachment=True)
    file_name = fields.Char(string='Document Name')

    @api.constrains('document')
    def _check_doc_size_and_type(self):
        allowed_file_list = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
        for record in self:
            if record.document:
                acp_size = ((len(record.document) * 3 / 4) / 1024) / 1024
                mimetype = guess_mimetype(base64.b64decode(record.document))
                if str(mimetype) not in allowed_file_list:
                    raise ValidationError("Only PDF/jpg/jpeg/png format is allowed under section 80G")
                if acp_size > 5:
                    raise ValidationError("Document allowed size less than 5MB under section 80G")


class SlabDeclarations_80e(models.Model):
    _name = 'declaration_slab_80e'
    _description = 'declaration_slab_80e'

    def set_80e_rules(self):
        current_rule = self.env['hr.itrule'].search([('code', '=', '80e')])
        return current_rule

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
        ('Contribution to National Pension Scheme(NPS)', 'Contribution to National Pension Scheme(NPS)'),
    ], string='Deduction', default='slab_80_declaration')

    slab_80e_id = fields.Many2one('hr.declaration', string='Slab')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section', domain=[('code', '=', '80e')],
                              default=set_80e_rules)
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Declaration Amount', digits=dp.get_precision('tds'))
    actual_amt = fields.Float(string='Actual Amount', digits=dp.get_precision('tds'))
    document = fields.Binary(string='Document', attachment=True)
    file_name = fields.Char(string='Document Name')

    @api.constrains('document')
    def _check_doc_size_and_type(self):
        allowed_file_list = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
        for record in self:
            if record.document:
                acp_size = ((len(record.document) * 3 / 4) / 1024) / 1024
                mimetype = guess_mimetype(base64.b64decode(record.document))
                if str(mimetype) not in allowed_file_list:
                    raise ValidationError("Only PDF/jpg/jpeg/png format is allowed under section 80E")
                if acp_size > 5:
                    raise ValidationError("Document allowed size less than 5MB under section 80E")


class SlabDeclarations_80ccd(models.Model):
    _name = 'declaration_slab_ccd'
    _description = 'declaration_slab_ccd'

    def set_80ccd_rules(self):
        current_rule = self.env['hr.itrule'].search([('code', '=', '80ccd')])
        return current_rule

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
        ('Contribution to National Pension Scheme(NPS)', 'Contribution to National Pension Scheme(NPS)'),
    ], string='Deduction', default='slab_80_declaration')

    slab_ccd_id = fields.Many2one('hr.declaration', string='Slab')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section', domain=[('code', '=', '80ccd')],
                              default=set_80ccd_rules)
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Declaration Amount', digits=dp.get_precision('tds'))
    actual_amt = fields.Float(string='Actual Amount', digits=dp.get_precision('tds'))
    document = fields.Binary(string='Document', attachment=True)
    file_name = fields.Char(string='Document Name')

    @api.constrains('document')
    def _check_doc_size_and_type(self):
        allowed_file_list = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
        for record in self:
            if record.document:
                acp_size = ((len(record.document) * 3 / 4) / 1024) / 1024
                mimetype = guess_mimetype(base64.b64decode(record.document))
                if str(mimetype) not in allowed_file_list:
                    raise ValidationError("Only PDF/jpg/jpeg/png format is allowed under section 80CCD(NPS)")
                if acp_size > 5:
                    raise ValidationError("Document allowed size less than 5MB under section 80CCD(NPS)")


class SlabDeclarations_80dd(models.Model):
    _name = 'declaration_slab_80dd'
    _description = 'declaration.slab80dd'
    _order = 'saving_master'

    def set_80dd_rules(self):
        current_rule = self.env['hr.itrule'].search([('code', '=','80dd')])
        return current_rule

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
        ('Contribution to National Pension Scheme(NPS)', 'Contribution to National Pension Scheme(NPS)'),
    ], string='Deduction', default='slab_80_declaration', track_visibility="always")

    slab_80dd_id = fields.Many2one('hr.declaration', string='Slab', track_visibility="onchange")
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section',domain=[('code','=','80dd')],default=set_80dd_rules)
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Declaration', compute='compute_investment', digits=dp.get_precision('tds'))
    actual_amt = fields.Float(string='Actual Amount', digits=dp.get_precision('tds'),compute='compute_investment',)
    document = fields.Binary(string='Document', attachment=True)
    file_name = fields.Char(string='Document Name')
    handicapped_percent = fields.Integer(string='Disability Percentage', )
    actual_handicapped_percent = fields.Integer(string='Actual Disability Percentage', )

    @api.constrains('document')
    def _check_doc_size_and_type(self):
        allowed_file_list = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
        for record in self:
            if record.document:
                acp_size = ((len(record.document) * 3 / 4) / 1024) / 1024
                mimetype = guess_mimetype(base64.b64decode(record.document))
                if str(mimetype) not in allowed_file_list:
                    raise ValidationError("Only PDF/jpg/jpeg/png format is allowed under section 80DD")
                if acp_size > 5:
                    raise ValidationError("Document allowed size less than 5MB under section 80DD")

    @api.constrains('handicapped_percent')
    def validate_percentage(self):
        for rec in self:
            if rec.handicapped_percent > 100 or rec.handicapped_percent < 0:
                raise ValidationError("Disability Percentage Should be in Between 1-100.")

    @api.onchange('handicapped_percent','actual_handicapped_percent')
    def onchange_handicapped_percent(self):
        for record in self:
            if record.handicapped_percent > 100 or record.handicapped_percent < 0:
                return {'warning': {
                    'title': ('Validation Error'),
                    'message': (
                        'Disability Percentage Should be in Between 1-100.')
                }}
            if record.actual_handicapped_percent > 100 or record.actual_handicapped_percent < 0:
                    return {'warning': {
                    'title': ('Validation Error'),
                    'message': (
                        'Disability Percentage Should be in Between 1-100.')
                }}

    @api.depends('handicapped_percent','actual_handicapped_percent')
    def compute_investment(self):
        for rec in self:
            if rec.handicapped_percent < 40:
                rec.investment = 0
            elif rec.handicapped_percent >= 40 and rec.handicapped_percent < 80:
                rec.investment = 75000
            else:
                rec.investment = 125000
            if rec.actual_handicapped_percent < 40:
                rec.actual_amt = 0
            elif rec.actual_handicapped_percent >= 40 and rec.actual_handicapped_percent < 80:
                rec.actual_amt = 75000
            else:
                rec.actual_amt = 125000

class SlabDeclarations_80ddb(models.Model):
    _name = 'declaration_slab_80ddb'
    _description = 'declaration.slab80dd'
    _order = 'saving_master'

    def set_80ddb_rules(self):
        current_rule = self.env['hr.itrule'].search([('code', '=','80ddb')])
        return current_rule

    deduction_id = fields.Selection([
        ('slab_80ddb_declaration', 'Deduction towards payments made towards Medical treatment specified diseases(For Self or Dependent)')], string='Deduction', default='slab_80ddb_declaration', track_visibility="always")

    slab_80ddb_id = fields.Many2one('hr.declaration', string='Slab', track_visibility="onchange")
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section',domain=[('code','=','80ddb')],default=set_80ddb_rules)
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Declaration Amount',digits=dp.get_precision('tds'))
    actual_amt = fields.Float(string='Actual Amount', digits=dp.get_precision('tds'))
    document = fields.Binary(string='Document', attachment=True)
    file_name = fields.Char(string='Document Name')

    @api.constrains('document')
    def _check_doc_size_and_type(self):
        allowed_file_list = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
        for record in self:
            if record.document:
                acp_size = ((len(record.document) * 3 / 4) / 1024) / 1024
                mimetype = guess_mimetype(base64.b64decode(record.document))
                if str(mimetype) not in allowed_file_list:
                    raise ValidationError("Only PDF/jpg/jpeg/png format is allowed under section 80DDB")
                if acp_size > 5:
                    raise ValidationError("Document allowed size less than 5MB under section 80DDB")


class EmployeeIncometax(models.Model):
    _name = 'tds_emp_integration'
    _description = "TDS Employees"

    def get_tds_data(self):
        fy_code = self.env['ir.config_parameter'].sudo().get_param('tds.financial_year')
        tds_details_ids = self.env.context.get('selected_active_ids')
        res = self.env['hr.declaration'].sudo().search(
            [('id', 'in', tds_details_ids), ('date_range.code', '=', fy_code)])
        return res

    tds_ids = fields.Many2many('hr.declaration', 'kw_employee_tds_rel', 'tds_id', 'emp_id', string='Employees',
                               default=get_tds_data)

    def button_compute_income_tax(self):
        if self.tds_ids:
            for rec in self.tds_ids:
                rec.button_compute_tax()
            # for payroll in self.payroll_ids:
            #     payroll.compute_sheet()
            self.env.user.notify_success(message='Tax computed successfully!.')


class ResUsers(models.Model):
	_inherit = 'res.users'

	php_user_id = fields.Char("User ID")