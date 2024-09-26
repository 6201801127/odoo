from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
from odoo.addons import decimal_precision as dp
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
import json, requests
# import json, requests
import re
# import pytz
import math
from math import floor,ceil
# import os
# import base64
# import zipfile


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
        
    def _default_employee(self):
        return self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('deduct_report'):
            ids = []
            if self.env.user.has_group('tds.group_report_manager_declaration'):
                query = "select id from hr_declaration"
                self._cr.execute(query)
                ids = self._cr.fetchall()
                args += [('id','in',ids)]
                
            else:
                user_id = self.env.uid
                query = f"select id from hr_declaration where create_uid = {user_id}"
                self._cr.execute(query)
                ids = self._cr.fetchall()
                args = [('id','in',ids)]

        return super(HrDeclaration, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

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
            payslip = self.env['hr.payslip'].sudo().search([('employee_id', '=', rec.employee_id.id),('date_from', '>=', rec.date_range.date_start),('date_to', '<=', rec.date_range.date_stop)])
            if len(payslip) > 0 and rec.allow_edit_bool== False:
                rec.tax_freeze_bool = True
            else:
                rec.tax_freeze_bool = False

    def btn_allow_edit_from_tree(self):
        query = f'update hr_declaration set allow_edit_bool= true where employee_id={self.employee_id.id}'
        self.env.cr.execute(query)


    emp_age = fields.Integer(track_visibility='always',default=calculateAge,readonly=True,string='Age')
    bank_account = fields.Char(string='Bank A/c#', compute='_compute_pan_num',)
    bank_name = fields.Char(compute='_compute_pan_num',)
    employee_id = fields.Many2one('hr.employee', string='Employee Name', default=_default_employee,)
    emp_name = fields.Char(related='employee_id.name', string='Name')
    image = fields.Binary(related='employee_id.image',string='Image')
    birthday = fields.Date(related='employee_id.birthday', string='Date of Birth')
    job_name = fields.Char(related='employee_id.job_id.name', string='Designation')
    employement_type = fields.Char(related="employee_id.employement_type.name")
    department_name = fields.Char(related='employee_id.department_id.name', string='Department')
    tax_freeze_bool = fields.Boolean(compute='_chk_payslip_exist')
    allow_edit_bool = fields.Boolean(default=True)
    gender = fields.Selection(related='employee_id.gender', string='Gender')
    emp_code = fields.Char(related='employee_id.emp_code', string='Employee Code')
    pan_number = fields.Char(string='PAN', compute='_compute_pan_num', track_visibility="always")
    date_range = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always',
                                 default=_default_financial_yr)
    comming_date_range = fields.Char(compute='comming_fy_formatted')
    mobile_phone = fields.Char(related='employee_id.mobile_phone', string='Contact no')
    date_of_joining = fields.Date(related='employee_id.date_of_joining', string='Date of Joining')
    last_working_day = fields.Char(compute='_compute_pan_num', string='Date of Leaving Service from Current Employer')

    previous_employer_income = fields.Float(string='Amount', digits=dp.get_precision('tds'), track_visibility="always")
    house_rent_paid = fields.Float(string='House Rent Declaration Amount', digits=dp.get_precision('tds'), track_visibility="always")
    actual_house_rent_paid = fields.Float(string='Actual Amount of House rent', digits=dp.get_precision('tds'), track_visibility="always")
    pan_landlord = fields.Binary(string='Rent Receipt')

    tax_regime=fields.Selection([('new_regime', 'New Regime'),('old_regime', 'Old Regime')], required=True, default='new_regime',
                             string='Tax Regime', track_visibility="alaways")

    slab_ids = fields.One2many('declaration.slab', 'slab_id', string='80C', track_visibility="onchange")
    housing_loan_ids = fields.One2many('housing_loan', 'housing_loan_id', string='Housing Loan Details')
    temp_interest_payment = fields.Float(string='', digits=dp.get_precision('tds'), track_visibility="always")
    actual_interest_payment = fields.Float(string='', digits=dp.get_precision('tds'), track_visibility="always")

    calculate_interest_payment = fields.Float(string='9 . Income/Loss From House Property', track_visibility="always",digits=dp.get_precision('tds'))
    allowed_rebate_under_80c = fields.Float(string='Allowed Rebate under Section 80C', track_visibility="always",digits=dp.get_precision('tds'))
    allowed_rebate_under_80b = fields.Float(string='Allowed Rebate under Section 80CCD1(B)', track_visibility="always",digits=dp.get_precision('tds'))
    allowed_rebate_under_80d = fields.Float(string='Allowed Rebate under Section 80D', track_visibility="always",digits=dp.get_precision('tds'))
    total_deductions = fields.Float(string='Total Deduction', track_visibility="always",digits=dp.get_precision('tds'))
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id, track_visibility="always")
    state = fields.Selection([('draft', 'Submitted'), ('approved', 'Approved')], default='draft',
                             string='Status', track_visibility='always')
    gross_salary = fields.Float(string='1 . Final Gross Salary', track_visibility="always",digits=dp.get_precision('tds'))
    basic_salary = fields.Float(string='Basic Salary', track_visibility="always",digits=dp.get_precision('tds'))
    actual_basic_salary = fields.Float(string='Actual Basic Salary', track_visibility="always",digits=dp.get_precision('tds'))
    projection_basic_salary = fields.Float(string='Projected Basic Salary', track_visibility="always",digits=dp.get_precision('tds'))

    hra = fields.Float(string='House Rent Allowance', track_visibility="always",digits=dp.get_precision('tds'))
    actual_hra = fields.Float(string='Actual HRA offered by the employer', track_visibility="always",digits=dp.get_precision('tds'))
    actual_payroll_hra = fields.Float(digits=dp.get_precision('tds'))
    projection_payroll_hra = fields.Float(digits=dp.get_precision('tds'))

    basic_40_percent = fields.Float(string='40% of Basic', track_visibility="always",digits=dp.get_precision('tds'))
    excess_10_percent = fields.Float(string='(Actual rent paid)-(10% of the basic salary)', tracking=True,digits=dp.get_precision('tds'))
    actual_excess_10_percent = fields.Float(string='Actual 10% of the basic salary', tracking=True,digits=dp.get_precision('tds'))
    hra_by_employee = fields.Float(string='HRA Paid By the Employee', track_visibility="always",digits=dp.get_precision('tds'))
    sub_total = fields.Float(string='1 . Sub Total', track_visibility="always",digits=dp.get_precision('tds'))
    lwop = fields.Float(string='LWOP', track_visibility="always",digits=dp.get_precision('tds'))
    actual_lwop = fields.Float(string='Actual LWOP', track_visibility="always",digits=dp.get_precision('tds'))
    projection_lwop = fields.Float(string='Actual LWOP', track_visibility="always",digits=dp.get_precision('tds'))

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
    income_from_pre_employer_doc = fields.Binary(string='Previous Income Document', track_visibility="always")
    doc_file_name_pre_emp = fields.Char(string='File Name')
    slab_80g_ids = fields.One2many('declaration_slab_80g', 'slab_80g_id', string='80G', track_visibility="always")
    slab_80e_ids = fields.One2many('declaration_slab_80e', 'slab_80e_id', string='80E', track_visibility="always")
    slab_ccd_ids = fields.One2many('declaration_slab_ccd', 'slab_ccd_id', string='80CCD', track_visibility="always")
    
    slab_80dd_ids = fields.One2many('declaration_slab_80dd', 'slab_80dd_id', string='80DD', track_visibility="always")
    slab_80u_ids = fields.One2many('declaration_slab_80u', 'slab_80u_id', string='80', track_visibility="always")
    pan_of_landlord = fields.Char(string='PAN of House Owner', track_visibility="always")
    previous_employer_income_final = fields.Float(string="2 . Income from Previous Employer (B)", track_visibility="always",digits=dp.get_precision('tds'))
    standard_deduction = fields.Float(string="Standard Deduction", track_visibility="always",digits=dp.get_precision('tds'))
    final_amount = fields.Float(string="Total Deductions", track_visibility="always",digits=dp.get_precision('tds'))
    prl_hlth_self = fields.Float(string="Health Insurance for Self", track_visibility="always",digits=dp.get_precision('tds'))
    prl_hlth_dependant = fields.Float(string="Health Insurance for Spouse,Children", track_visibility="always",digits=dp.get_precision('tds'))
    health_insurance_parent = fields.Float(string="Health Insurance for Parents", track_visibility="always",digits=dp.get_precision('tds'))
    tax_recovered = fields.Float(string='Tax Recovered Till Date', track_visibility="always",digits=dp.get_precision('tds'))
    balance_tax_payable = fields.Float(string='Balance Tax Payable/Refundable', track_visibility="always",digits=dp.get_precision('tds'))
    other_income = fields.Float(string='Other Allowance', track_visibility="always",digits=dp.get_precision('tds'))
    pan_landlord_file_name = fields.Char(string='Landlord File Name', track_visibility="always",attachment=True)
    tot_80c_epf = fields.Float(string='Total Amount of 80C', track_visibility="always",digits=dp.get_precision('tds'))
    tot_80ccd = fields.Float(string='Total Amount of 80CCD', track_visibility="always",digits=dp.get_precision('tds'))
    allowed_rebate_under_80ccd = fields.Float(string='Allowed Rebate under Section 80CCD', track_visibility="always",digits=dp.get_precision('tds'))
    tot_80d = fields.Float(string='Total Amount of 80D', track_visibility="always",digits=dp.get_precision('tds'))
    tot_80dd = fields.Float(string='Total Amount of 80DD', track_visibility="always",digits=dp.get_precision('tds'))
    allowed_rebate_under_80dd = fields.Float(string='Allowed Rebate under Section 80DD', track_visibility="always",digits=dp.get_precision('tds'))
    tot_80e = fields.Float(string='Total Amount of 80E', tracking=True,digits=dp.get_precision('tds'))
    allowed_rebate_under_80e = fields.Float(string='Allowed Rebate under Section 80E', track_visibility="always",digits=dp.get_precision('tds'))
    tot_80g = fields.Float(string='Total Amount of 80G', tracking=True,digits=dp.get_precision('tds'))
    allowed_rebate_under_80g = fields.Float(string='Allowed Rebate under Section 80G', track_visibility="always",digits=dp.get_precision('tds'))
    check_previous_emp_income = fields.Boolean(string='Check Income', compute='_cheak_month', track_visibility="always")
    hra_percent = fields.Char(string='', track_visibility="always")
    tds_previous_employer = fields.Float(string='TDS Paid', digits=dp.get_precision('tds'), track_visibility="always")
    tds_doc = fields.Binary(string='TDS Document', track_visibility="always")
    gross_annual_value = fields.Float(string='Gross Annual Value', digits=dp.get_precision('tds'), track_visibility="always")
    actual_gross_annual_value = fields.Float(string='Actual Gross Annual Value', digits=dp.get_precision('tds'), track_visibility="always")
    municipal_taxes = fields.Float(string='Less: Municipal Taxes', digits=dp.get_precision('tds'), track_visibility="always")
    actual_municipal_taxes = fields.Float(string='Actual Less: Municipal Taxes', digits=dp.get_precision('tds'), track_visibility="always")
    net_annual_value = fields.Float(string='Net annual Value', track_visibility="always",digits=dp.get_precision('tds'))
    actual_net_annual_value = fields.Float(string='Actual Net annual Value', track_visibility="always",digits=dp.get_precision('tds'))
    
    standard_30_deduction = fields.Float(string='Less: Standard Deduction at 30%', track_visibility="always",digits=dp.get_precision('tds'))
    actual_standard_30_deduction = fields.Float(string='Actual Less: Standard Deduction at 30%', track_visibility="always",digits=dp.get_precision('tds'))
    
    lowest_hra = fields.Float(string='Lowest', track_visibility="always",digits=dp.get_precision('tds'))
    total_income_interest = fields.Float(string='Income/Loss From House Property', track_visibility="always",digits=dp.get_precision('tds'))
    slab_80c_limit = fields.Float(string='Maximum amount allowed on 80C', compute='_compute_limit', digits=dp.get_precision('tds'), track_visibility="always")
    slab_80ccd_limit = fields.Float(string='Maximum amount allowed', compute='_compute_limit', digits=dp.get_precision('tds'), track_visibility="always")
    slab_80d_limit = fields.Char(string='Maximum amount allowed',
                                 default='Parent above 60 years : 50,000,Parent below 60 years : 25000,Self and Spouse,Children above 60 years : 50,000,Self and Spouse, Children below 60 years : 25,000',
                                 readonly=True, track_visibility="always")
    slab_80dd_limit = fields.Float(string='Threshold Limit on 80DD', compute='_compute_limit', digits=dp.get_precision('tds'), track_visibility="always")
    slab_80e_limit = fields.Char(string='Threshold Limit on 80E', default='No Limit', readonly=True, track_visibility="always")
    slab_80g_limit = fields.Char(string='Threshold Limit on 80G',
                                 default='Donations Eligible for 100% & 50% Deduction Without Qualifying Limit as per IT LIST',
                                 readonly=True, track_visibility="always")
    professional_tax_pad = fields.Float(string='Professional Tax Paid', track_visibility="always",digits=dp.get_precision('tds'))
    total_80c_payable = fields.Float(string='Total Contribution to 80C', track_visibility="always",digits=dp.get_precision('tds'))
    tds_by_company = fields.Char(compute='_cheak_month',)
    invisible = fields.Boolean(string='Month', compute='_cheak_month')
    house_loan_doc = fields.Binary(string='Housing Loan Document', attachment=True)
    house_loan_doc_file_name =  fields.Char(string='Housing Loan Document Name')
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
    income_from_other_sources_doc = fields.Binary(string='Other Income Document', attachment=True)
    other_source_income_file_name =  fields.Char(string='Other Income Document Name')
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
    interest_received_doc = fields.Binary(attachment=True,string='Received Interest Document')
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
    lta_document = fields.Binary(attachment=True,sting='LTA Document')
    lta_document_file_name = fields.Char(string='LTA Document Name')

    prof_persuit_spent_by_employee = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_prof_persuit_spent_by_employee = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    final_prof_persuit_spent_by_employee = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    prof_persuit_document = fields.Binary(attachment=True,string='Professional Persuit Document')
    prof_persuit_document_file_name = fields.Char(string='PP Document Name')

    taxable_salary_from_csm = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    total_taxable_salary = fields.Float(track_visibility="always",digits=dp.get_precision('tds'))

    monthly_tax_to_recover = fields.Integer(track_visibility="always")
    other_incentive  = fields.Float(track_visibility="always",digits=dp.get_precision('tds'),string='Other Incentive')
    previous_income_lock = fields.Boolean(track_visibility="always",)
    tds_previous_income_lock = fields.Boolean(track_visibility="always",)
    house_income_lock = fields.Boolean(track_visibility="always",)
    bank_income_lock = fields.Boolean(track_visibility="always",)
    other_income_lock = fields.Boolean(track_visibility="always",)
    hra_income_lock = fields.Boolean(track_visibility="always",)
    lta_lock = fields.Boolean(track_visibility="always",)
    pp_lock = fields.Boolean(track_visibility="always",)
    actual_previous_employer_income=fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    actual_tds_previous_employer=fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    final_tds_previous_employer=fields.Float(track_visibility="always",digits=dp.get_precision('tds'))
    total_gross_salary = fields.Float(track_visibility="always",digits=dp.get_precision('tds'),compute='compute_salry')
    total_exemption = fields.Float(track_visibility="always",digits=dp.get_precision('tds'),compute='compute_salry')
    tds = fields.Float(track_visibility="always",digits=dp.get_precision('tds'),compute='compute_salry')
    lwop_amt_negative = fields.Float(compute='compute_salry',digits=dp.get_precision('tds'))
    wo_balance_tax_payable = fields.Float(string='Without Balance Tax Payable/Refundable', track_visibility="always",digits=dp.get_precision('tds'))
    rent_agreement = fields.Binary(string='Rent Agreement',attachment=True)
    rent_agreementfile_name = fields.Char(string='Rent Agreement File Name')
    lta_mode_of_travel = fields.Selection([('neuro', 'Air'),('cancer', 'Rail'),('aids', 'Road'),], string='Travel mode', track_visibility="always")
    lta_travel_date = fields.Date(string='Travel Date', track_visibility="always")
    lta_from_date = fields.Date(string='Travel Date', track_visibility="always")
    lta_travel_from = fields.Char(string='Travel From', track_visibility="always")
    lta_travel_to = fields.Char(string='Destination Place ', track_visibility="always")
    allowed_rebate_under_80u =  fields.Float(string='Allowed Rebate under Section 80U', track_visibility="always",digits=dp.get_precision('tds'))
    slab_80u_limit = fields.Float(string='Threshold Limit on 80U', compute='_compute_limit', digits=dp.get_precision('tds'), track_visibility="always")
    slab_80ccd2_limit = fields.Float(string='Threshold Limit on 80CCD2', compute='_compute_limit', digits=dp.get_precision('tds'), track_visibility="always")
    allowed_rebate_under_80ccd2 =  fields.Float(string='Allowed Rebate under Section 80CCD2', track_visibility="always",digits=dp.get_precision('tds'))
    nps_projection = fields.Float(string='NPS Projection', track_visibility="always",digits=dp.get_precision('tds'))
    nps_actual = fields.Float(string='NPS Actual', track_visibility="always",digits=dp.get_precision('tds'))
    nps = fields.Float(string='NPS Actual', track_visibility="always",digits=dp.get_precision('tds'))
    pran = fields.Char(compute='_compute_pan_num')
    doc_boolean = fields.Selection([('submitted', 'Submitted'),('not_submitted', 'Not Submitted')], string='Document',compute='_check_document')
    # doc_boolean = fields.Boolean(compute='_check_document')
    
    def _check_document(self):
        for rec in self:
            if rec.tax_regime == 'new_regime':
                if (rec.interest_received_from_bank > 0 and not rec.interest_received_doc) or (rec.income_from_other_sources > 0 and not rec.income_from_other_sources_doc) or (rec.previous_employer_income > 0 and not rec.income_from_pre_employer_doc) or (rec.tds_previous_employer > 0 and not rec.tds_doc)  :
                    rec.doc_boolean = 'not_submitted'
                else:
                    rec.doc_boolean = 'submitted'
            else:
                check_80c = rec.slab_ids.filtered(lambda x:x.investment > 0 and not x.document)
                check_80ccd = rec.slab_ccd_ids.filtered(lambda x:x.investment > 0 and not x.document)
                check_80d = rec.slab_80d_ids.filtered(lambda x:x.investment > 0 and not x.document)
                check_80ddb = rec.slab_80ddb_ids.filtered(lambda x:x.investment > 0 and not x.document)
                check_80u = rec.slab_80u_ids.filtered(lambda x:x.handicapped_percent > 0 and not x.document)
                check_80dd = rec.slab_80dd_ids.filtered(lambda x:x.handicapped_percent > 0 and not x.document)
                check_80e = rec.slab_80e_ids.filtered(lambda x:x.investment > 0 and not x.document)      
                check_80g = rec.slab_80g_ids.filtered(lambda x:x.investment > 0 and not x.document)
                if (rec.interest_received_from_bank > 0 and not rec.interest_received_doc) or (rec.income_from_other_sources > 0 and not rec.income_from_other_sources_doc) or (rec.previous_employer_income > 0 and not rec.income_from_pre_employer_doc) or (rec.tds_previous_employer > 0 and not rec.tds_doc) or (rec.temp_interest_payment > 0 and not rec.house_loan_doc)  or (rec.house_rent_paid > 0 and  (not rec.rent_agreement or not rec.pan_landlord)) or (rec.lta_spent_by_employee > 0 and not rec.lta_document) or (rec.prof_persuit_spent_by_employee > 0 and not rec.prof_persuit_document) or (check_80c or check_80ccd or check_80d or check_80ddb or check_80u or check_80dd or check_80e or check_80g) :
                    rec.doc_boolean = 'not_submitted'
                else:
                    rec.doc_boolean = 'submitted'
                    
                    

    
    
    
    # def _auto_init(self):
    #     super(HrDeclaration, self)._auto_init()
    #     self.env.cr.execute("delete from declaration_slab where saving_master = (select id from saving_master where active=false) and slab_id = (select id from hr_declaration where date_range=25)")
    
    @api.depends('total_salary','previous_employer_income_final','calculate_interest_payment','final_income_from_bank_other','hra_exemption','professional_tax','final_lta_spent_by_employee','final_prof_persuit_spent_by_employee','standard_deduction','tax_recovered','final_tds_previous_employer','lwop')
    def compute_salry(self):
        for rec in self:
            rec.total_gross_salary = rec.total_salary + rec.previous_employer_income_final + rec.calculate_interest_payment + rec.final_income_from_bank_other
            rec.total_exemption =rec.hra_exemption+rec.professional_tax+rec.final_lta_spent_by_employee+rec.final_prof_persuit_spent_by_employee+rec.standard_deduction
            rec.tds = rec.tax_recovered - rec.final_tds_previous_employer
            rec.lwop_amt_negative = -(rec.lwop)
            
    
    
    
    def view_yearly_hr_declaration(self):
        view_id = self.env.ref('tds.hr_declaration_bifurcation_view_form').id
        rc = {
            'name': 'IT Declaration',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.declaration',
            'view_id': view_id,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'self',
        }
        return rc
    def view_payslips(self):
        if self.employee_id and self.date_range:
            kw_monthly_salary_report = self.env['kw_monthly_salary_report'].sudo().search([('date_to','>=',self.date_range.date_start),('date_to','<=',self.date_range.date_stop),('employee_id','=',self.employee_id.id)])
            if kw_monthly_salary_report:
                rc = {
                    'name': f'Payslips for {self.employee_id.name}',
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'views': [(self.env.ref('payroll_integration.finance_payslip_report_tree').id, 'tree')],
                    'view_id': self.env.ref('payroll_integration.finance_payslip_report_tree').id,
                    'res_model': 'kw_monthly_salary_report',
                    'domain':[('id','in',kw_monthly_salary_report.ids)],
                    'type': 'ir.actions.act_window',
                    'target': 'self',
                }
                return rc
            else:
                raise ValidationError('No Payslip Found!')
    
    @api.multi
    def write(self, vals):
        result = super(HrDeclaration, self).write(vals)
        if self.write_uid.id != 1 :
            if len(vals) > 0:
                logs = self.env['hr_declaration_log'].create({
                    'date_range':self.date_range.id,
                    'employee_id':self.employee_id.id,
                    'tax_regime':self.tax_regime
                })
        return result
    
   
    
    def calculate_oldregime_tax_first(self,date_range,salary_from,salary_to,emp_age):
        self.env.cr.execute(f"select tax_rate from tax_slab where date_range={date_range} and salary_from<= {salary_from} and salary_to >= {salary_to} and tax_regime= 'old_regime' and age_from <= {emp_age} and age_to >={emp_age}  LIMIT 1")
        tax_details = self._cr.dictfetchall()
        if not tax_details:
            return 0
        else:
            return tax_details[0]['tax_rate']
        
    def calculate_oldregime_tax_second(self,date_range,salary_from,salary_to,emp_age):
        self.env.cr.execute(f"select tax_rate from tax_slab where date_range={date_range} and salary_from >= {salary_from} and salary_to <= {salary_to} and tax_regime= 'old_regime' and age_from <= {emp_age} and age_to >={emp_age}  LIMIT 1")
        tax_details = self._cr.dictfetchall()
        if not tax_details:
            return 0
        else:
            return tax_details[0]['tax_rate']
        
    def calculate_newregime_tax_rate_first(self,date_range,salary_from,salary_to):
        self.env.cr.execute(f"select tax_rate from tax_slab where date_range={date_range} and salary_from <= {salary_from} and salary_to >= {salary_to} and tax_regime='new_regime'  LIMIT 1")
        
        tax_details = self._cr.dictfetchall()
        if not tax_details:
            return 0
        else:
            return tax_details[0]['tax_rate']
        
    def calculate_newregime_tax_rate_second(self,date_range,salary_from,salary_to):
        self.env.cr.execute(f"select tax_rate from tax_slab where date_range = {date_range} and salary_from >= {salary_from} and salary_to <= {salary_to} and tax_regime ='new_regime'  LIMIT 1")
        tax_details = self._cr.dictfetchall()
        if not tax_details:
            return 0
        else:
            return tax_details[0]['tax_rate']

    def calculate_tax_payable(self,emp_age,tax_amount,date_range):
        temp_tax_payable = 0
        if emp_age < 60:
            if tax_amount > 250000 and tax_amount <= 500000:
                tds_amount = tax_amount - 250000
                tax_rate_1 = self.calculate_oldregime_tax_first(date_range,tax_amount,tax_amount,emp_age)
                temp_tax_payable = tds_amount * tax_rate_1 / 100
            elif tax_amount > 500000 and tax_amount <= 1000000:
                tds_above5 = tax_amount - 500000
                tax_rate_1 = self.calculate_oldregime_tax_first(date_range,tax_amount,tax_amount,emp_age)
                tds_above5percentage = tds_above5 * tax_rate_1 / 100
                tax_rate_2 = self.calculate_oldregime_tax_second(date_range,250001,500000,emp_age)
                tds_below5percentage = 250000 * tax_rate_2 / 100
                temp_tax_payable = tds_above5percentage + tds_below5percentage
            elif tax_amount > 1000000:
                tds_above10 = tax_amount - 1000000
                tax_rate_1 = self.calculate_oldregime_tax_first(date_range,tax_amount,tax_amount,emp_age)
                tds_above10percentage = tds_above10 * tax_rate_1 / 100
                tax_rate_2 = self.calculate_oldregime_tax_second(date_range,500001,1000000,emp_age)
                tds_above5percentage = 500000 * tax_rate_2 / 100
                tax_rate_3 = self.calculate_oldregime_tax_second(date_range,250001,500000,emp_age)
                tds_below5percentage = 250000 * tax_rate_3 / 100
                temp_tax_payable = tds_above10percentage + tds_above5percentage + tds_below5percentage
        if 60 <= emp_age <= 80:
            if tax_amount > 300000 and tax_amount <= 500000:
                tds_amount = tax_amount - 300000
                tax_rate_1 = self.calculate_oldregime_tax_first(date_range,tax_amount,tax_amount,emp_age)
                temp_tax_payable = tds_amount * tax_rate_1 / 100
            elif tax_amount > 500000 and tax_amount <= 1000000:
                tds_above5 = tax_amount - 500000
                tax_rate_1 = self.calculate_oldregime_tax_first(date_range,tax_amount,tax_amount,emp_age)
                tds_above5percentage = tds_above5 * tax_rate_1 / 100
                tax_rate_2 = self.calculate_oldregime_tax_second(date_range,300001,500000,emp_age)
                tds_below5percentage = 200000 * tax_rate_2 / 100
                temp_tax_payable = tds_above5percentage + tds_below5percentage
            elif tax_amount > 1000000:
                tds_above10 = tax_amount - 1000000
                tax_rate_1 = self.calculate_oldregime_tax_first(date_range,tax_amount,tax_amount,emp_age)
                tds_above10percentage = tds_above10 * tax_rate_1 / 100
                tax_rate_2 = self.calculate_oldregime_tax_second(date_range,500001,1000000,emp_age)
                tds_above5percentage = 500000 * tax_rate_2 / 100
                tax_rate_3 = self.calculate_oldregime_tax_second(date_range,300001,500000,emp_age)
                tds_below5percentage = 200000 * tax_rate_3 / 100
                temp_tax_payable = tds_above10percentage + tds_above5percentage + tds_below5percentage
        if emp_age > 80:
            if tax_amount > 500001 and tax_amount <= 1000000:
                tds_amount = tax_amount - 500000
                tax_rate_1 = self.calculate_oldregime_tax_first(date_range,tax_amount,tax_amount,emp_age)
                temp_tax_payable = tds_amount * tax_rate_1 / 100
            elif tax_amount > 1000000:
                tds_above5 = tax_amount - 1000000
                tax_rate_1 = self.calculate_oldregime_tax_first(date_range,tax_amount,tax_amount,emp_age)
                tds_above5percentage = tds_above5 * tax_rate_1 / 100
                tax_rate_2 = self.calculate_oldregime_tax_second(date_range,500001,1000000,emp_age)
                tds_below5percentage = 500000 * tax_rate_2 / 100
                temp_tax_payable = tds_above5percentage + tds_below5percentage
        return temp_tax_payable
    def claculate_new_regime_tax(self,tax_amount,date_range):
        temp_tax_payable = 0
        if tax_amount > 300000 and tax_amount <= 700000:
            tds_amount = tax_amount - 400000
            tax_rate_1 = self.calculate_newregime_tax_rate_first(date_range,tax_amount,tax_amount)
            temp_tax_payable = tds_amount * tax_rate_1 / 100
        elif tax_amount > 700000 and tax_amount <= 1000000:
            tds_above5 = tax_amount - 700000
            tax_rate_1 = self.calculate_newregime_tax_rate_first(date_range,tax_amount,tax_amount)
            tds_above5percentage = tds_above5 * tax_rate_1 / 100
            tax_rate_2 = self.calculate_newregime_tax_rate_second(date_range,300001,700000)
            tds_below5percentage = 400000 * tax_rate_2/ 100
            temp_tax_payable = tds_above5percentage + tds_below5percentage
        elif tax_amount > 1000000 and tax_amount <= 1200000:
            tds_above75 = tax_amount - 1000000
            tax_rate_1 = self.calculate_newregime_tax_rate_first(date_range,tax_amount,tax_amount)
            tds_above75percentage = tds_above75 * tax_rate_1 / 100
            tax_rate_2 = self.calculate_newregime_tax_rate_second(date_range,700001,1000000)
            tds_above5percentage = 300000 * tax_rate_2 / 100
            tax_rate_3 = self.calculate_newregime_tax_rate_second(date_range,300001,700000)
            tds_below5percentage = 400000 * tax_rate_3 / 100
            temp_tax_payable = tds_above75percentage + tds_above5percentage + tds_below5percentage
        elif tax_amount > 1200000 and tax_amount <= 1500000:
            tds_above10 = tax_amount - 1200000
            tax_rate_1 = self.calculate_newregime_tax_rate_first(date_range,tax_amount,tax_amount)
            tds_above10percentage = tds_above10 * tax_rate_1 / 100
            tax_rate_2 = self.calculate_newregime_tax_rate_second(date_range,1000001,1200000)
            tds_above75percentage = 300000 * tax_rate_2 / 100
            tax_rate_3 = self.calculate_newregime_tax_rate_second(date_range,700001,1000000)
            tds_above5percentage = 300000 * tax_rate_3 / 100
            tax_rate_4 = self.calculate_newregime_tax_rate_second(date_range,300001,700000)
            tds_below5percentage = 400000 * tax_rate_4 / 100
            temp_tax_payable = tds_above10percentage + tds_above75percentage +tds_above5percentage + tds_below5percentage
        elif tax_amount > 1500000:
            tds_above15 = tax_amount - 1500000
            tax_rate_1 = self.calculate_newregime_tax_rate_first(date_range,tax_amount,tax_amount)
            tds_above15percentage = tds_above15 * tax_rate_1 / 100
            tax_rate_2 = self.calculate_newregime_tax_rate_first(date_range,1200001,1500000)
            tds_above12percentage = 300000 * tax_rate_2 / 100
            tax_rate_3 = self.calculate_newregime_tax_rate_first(date_range,1000001,1200000)
            tds_above10percentage = 300000 * tax_rate_3 / 100
            tax_rate_4 = self.calculate_newregime_tax_rate_first(date_range,700001,1000000)
            tds_above75percentage = 300000 * tax_rate_4 / 100
            tax_rate_5 = self.calculate_newregime_tax_rate_first(date_range,300001,700000)
            tds_above5percentage = 400000 * tax_rate_5/ 100
            temp_tax_payable = tds_above15percentage + tds_above12percentage + tds_above10percentage + tds_above75percentage +tds_above5percentage 
        return temp_tax_payable
    
    @api.multi
    # @profile
    def button_compute_tax(self, **kwargs):
        bs = lwop=ptd=epf=tds=conveyance = productivity=commitment= lta = prof_persuit =arrear=incentive=variable=splalw=equalw=leave_encahment=city_alw=trng_inc=erbonus=sum_prl=actual_nps=0
        for rec in self:
            self.env.cr.execute(f"select birthday,last_working_day,date_of_joining,active from hr_employee where id = {rec.employee_id.id}")
            emp_details = self._cr.dictfetchall()
            self.env.cr.execute(f"select date_start,date_stop from account_fiscalyear where id = {rec.date_range.id}")
            fy_details = self._cr.dictfetchall()
            date_start = fy_details[0]['date_start']
            date_stop = fy_details[0]['date_stop']
            birthday = emp_details[0].get('birthday')
            self.env.cr.execute(f"SELECT EXTRACT(YEAR FROM age('{date_start}'::DATE,'{birthday}'::DATE)) + EXTRACT(MONTH FROM age('{date_start}'::DATE, '{birthday}'::DATE)) / 12.0 + EXTRACT(DAY FROM age('{date_start}'::DATE, '{birthday}'::DATE)) / 365.0 AS age_decimal")
            dob = self._cr.dictfetchall()
            j_date = emp_details[0]['date_of_joining']
            emp_age = dob[0]['age_decimal']
            self.env.cr.execute(f"update hr_declaration set emp_age = {emp_age} where id = {rec.id}")
            if kwargs.get('date_to'):
                check_value = 1 if kwargs.get('date_to') <= date_stop else 0 
            else:
                check_value = 1 if date.today() < date_stop else 0
            contrct = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id),],order ='date_start desc',limit=1)
            if contrct:
                payslip = self.env['hr.payslip'].sudo().search([('employee_id', '=', rec.employee_id.id),('state', '=', 'done'),('date_from', '>=', date_start),('date_to', '<=', date_stop)])
                prl_id = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),('slip_id.state', '=', 'done'),('slip_id.date_from', '>=', date_start),('slip_id.date_to', '<=', date_stop)])
                month_limit = int((date_stop.year - j_date.year) * 12 + (date_stop.month - j_date.month)) + 1  if j_date >= date_start and j_date <= date_stop else 12
                blk_date_lst = []
                counter=last_counter=tds_month = 0
                block_payslips = self.env['hr_block_salary'].sudo().search([('employee_id','=',rec.employee_id.id)])
                for blk_payslp in block_payslips:
                    blk_year = int(blk_payslp.year)
                    blk_month = int(blk_payslp.month)
                    blk_date = date(blk_year,blk_month,1)
                    blk_date_lst.append(blk_date)
                for dates in blk_date_lst:
                    if date_start <= dates <= date_stop:
                        chk_payslip = payslip.filtered(lambda x:x.date_from <= dates <= x.date_to)
                        if not chk_payslip:
                            counter += 1
                if emp_details[0].get('last_working_day'):
                    last_counter =  ((date_stop.year -  emp_details[0].get('last_working_day').year) * 12 + date_stop.month - emp_details[0].get('last_working_day').month) if date_start <= emp_details[0].get('last_working_day') <= date_stop and emp_details[0]['active'] == False else 0
                remaining_month = month_limit - len(payslip) - counter - last_counter if check_value == 1 else 0
                tds_month = remaining_month
                if check_value == 1 and kwargs.get('date_to'):
                    remaining_month -= 1
                payslip_line = tuple(prl_id.ids)
                if payslip_line:
                    self.env.cr.execute(f"select sum(amount) filter(where code ='BASIC') as bs,sum(amount) filter(where code ='HRAMN') as sum_prl,sum(amount) filter(where code ='LWOP') as lwop,sum(amount) filter(where code ='PTD') as ptd,sum(amount) filter(where code ='EEPF') as epf,sum(amount) filter(where code ='TDS') as tds, sum(amount) filter(where code ='TCA') as conveyance,sum(amount) filter(where code ='PBONUS') as productivity,sum(amount) filter(where code ='CBONUS') as commitment,sum(amount) filter(where code ='LTC') as lta,sum(amount) filter(where code ='PP') as prof_persuit,sum(amount) filter(where code ='ARRE') as arrear,sum(amount) filter(where code ='INC') as incentive,sum(amount) filter(where code ='VAR') as variable,sum(amount) filter(where code ='SALW') as splalw,sum(amount) filter(where code ='EALW') as equalw,sum(amount) filter(where code ='LE') as leave_encahment,sum(amount) filter(where code ='CBDA') as city_alw,sum(amount) filter(where code ='TINC') as trng_inc,sum(amount) filter(where code ='ERBONUS') as erbonus from hr_payslip_line where id in {payslip_line}")
                    amount_dict = self._cr.dictfetchall()
                    bs = amount_dict[0]['bs'] if amount_dict[0]['bs'] else 0 
                    lwop = amount_dict[0]['lwop'] if amount_dict[0]['lwop'] else 0 
                    ptd = amount_dict[0]['ptd'] if amount_dict[0]['ptd'] else 0 
                    epf = amount_dict[0]['epf'] if amount_dict[0]['epf'] else 0 
                    tds = amount_dict[0]['tds'] if amount_dict[0]['tds'] else 0 
                    conveyance = amount_dict[0]['conveyance'] if amount_dict[0]['conveyance'] else 0 
                    productivity = amount_dict[0]['productivity'] if amount_dict[0]['productivity'] else 0 
                    commitment = amount_dict[0]['commitment'] if amount_dict[0]['commitment'] else 0 
                    lta = amount_dict[0]['lta'] if amount_dict[0]['lta'] else 0 
                    prof_persuit = amount_dict[0]['prof_persuit'] if amount_dict[0]['prof_persuit'] else 0 
                    arrear = amount_dict[0]['arrear'] if amount_dict[0]['arrear'] else 0 
                    incentive = amount_dict[0]['incentive'] if amount_dict[0]['incentive'] else 0 
                    variable = amount_dict[0]['variable'] if amount_dict[0]['variable'] else 0 
                    splalw = amount_dict[0]['splalw'] if amount_dict[0]['splalw'] else 0 
                    equalw = amount_dict[0]['equalw'] if amount_dict[0]['equalw'] else 0 
                    leave_encahment = amount_dict[0]['leave_encahment'] if amount_dict[0]['leave_encahment'] else 0 
                    city_alw = amount_dict[0]['city_alw'] if amount_dict[0]['city_alw'] else 0 
                    trng_inc = amount_dict[0]['trng_inc'] if amount_dict[0]['trng_inc'] else 0 
                    erbonus = amount_dict[0]['erbonus'] if amount_dict[0]['erbonus'] else 0 
                    sum_prl =  amount_dict[0]['sum_prl'] if amount_dict[0]['sum_prl'] else 0 
                    actual_nps +=  sum(payslip.mapped('actual_nps'))
                    # print('====================================actual_nps',actual_nps)
                    
                self.env.cr.execute(f"select current_basic,epf_percent,pf_deduction,enable_epf,house_rent_allowance_metro_nonmetro as contract_hra_percent,(current_basic*conveyance/100) as conveyance,conveyance as contract_conveyance,productivity,commitment,bonus,prof_persuit,ltc,pran_no,is_nps,contribution from hr_contract where id = {contrct.id}")
                contract_dict = self._cr.dictfetchall()
                gross_basic = contract_dict[0]['current_basic']  if contract_dict[0]['current_basic'] else 0
                gross_conveyance = contract_dict[0]['conveyance'] if contract_dict[0]['conveyance'] else 0 
                gross_pb = contract_dict[0]['productivity'] if contract_dict[0]['productivity'] else 0 
                gross_cb = contract_dict[0]['commitment'] if contract_dict[0]['commitment'] else 0 
                gross_bonus = contract_dict[0]['bonus'] if contract_dict[0]['bonus'] else 0 
                gross_pp = contract_dict[0]['prof_persuit'] if contract_dict[0]['prof_persuit'] else 0 
                gross_ltc = contract_dict[0]['ltc'] if contract_dict[0]['ltc'] else 0 
                contract_hra_percent = contract_dict[0]['contract_hra_percent'] if contract_dict[0]['contract_hra_percent'] else 0 
                contract_conveyance = contract_dict[0]['contract_conveyance'] if contract_dict[0]['contract_conveyance'] else 0 
                enable_epf = contract_dict[0]['enable_epf'] if contract_dict[0]['enable_epf'] else 'no' 
                pf_deduction = contract_dict[0]['pf_deduction'] if contract_dict[0]['pf_deduction'] else False 
                epf_percent =  contract_dict[0]['epf_percent']
                pran_no = contract_dict[0]['pran_no']  if contract_dict[0]['pran_no'] else ''
                is_nps = contract_dict[0]['is_nps']  if contract_dict[0]['is_nps'] else ''
                nps_contribution = contract_dict[0]['contribution']  if contract_dict[0]['contribution'] else ''
                
                hra_percentage_rec = self.env['city_wise_hra_config_master'].sudo().search([('city','=',rec.employee_id.base_branch_id.city)],limit=1) 
                hra_percentage = hra_percentage_rec.hra_percentage if hra_percentage_rec else contract_hra_percent
                gross_hra = gross_basic * hra_percentage/100
                current_month_basic = kwargs.get('basic') if kwargs.get('basic') else 0
                current_month_gross = kwargs.get('gross') if kwargs.get('gross')  else 0
                current_month_lwop = kwargs.get('LWOP') if kwargs.get('LWOP')  else 0
                current_month_productivity = kwargs.get('pb') if kwargs.get('pb') else 0
                current_month_commitment = kwargs.get('cb') if kwargs.get('cb') else 0
                current_month_lta = kwargs.get('lta') if kwargs.get('lta') else 0
                current_month_prof_persuit = kwargs.get('prof_persuit') if kwargs.get('prof_persuit') else 0
                current_month_arrear = kwargs.get('arrear') if kwargs.get('arrear') else 0
                current_month_incentive = kwargs.get('INC') if kwargs.get('INC') else 0
                current_month_variable = kwargs.get('VAR') if kwargs.get('VAR') else 0
                current_month_splalw = kwargs.get('SALW') if kwargs.get('SALW') else 0
                current_month_equalw = kwargs.get('EALW') if kwargs.get('EALW') else 0
                current_month_le = kwargs.get('LE') if kwargs.get('LE') else 0
                current_month_city = kwargs.get('CBDA') if kwargs.get('CBDA') else 0
                current_month_tinc = kwargs.get('TINC') if kwargs.get('TINC') else 0
                current_month_erbonus = kwargs.get('ERBONUS') if kwargs.get('ERBONUS') else 0
                current_month_nps = kwargs.get('NPS') if kwargs.get('NPS') else 0
                
                projection_payroll_hra =((rec.calculate_round_amount(gross_basic * contract_hra_percent / 100)) * remaining_month) + rec.calculate_round_amount(current_month_basic * contract_hra_percent / 100)
                projection_conveyance = ((rec.calculate_round_amount(gross_conveyance)) * remaining_month) + (current_month_basic * contract_conveyance / 100)
                projection_productivity =  current_month_productivity + rec.calculate_round_amount(gross_pb * remaining_month)
                projection_commitment = current_month_commitment + rec.calculate_round_amount(gross_cb * remaining_month)
                projection_lta  = current_month_lta + rec.calculate_round_amount(gross_ltc * remaining_month)
                projection_prof_persuit  = current_month_prof_persuit + rec.calculate_round_amount(gross_pp * remaining_month)
                projection_basic_salary=current_month_basic + (gross_basic * remaining_month)
                other_incentive = rec.other_incentive
                projection_nps = 0
                # print('current_month_nps==========',current_month_nps)
                # if len(pran_no) == 12 and is_nps == 'Yes' and nps_contribution in (5,7,10):
                #     projection_nps = current_month_nps + ((gross_basic * remaining_month) * int(nps_contribution)/100) 
                # else:
                #     if   len(pran_no) == 12 and is_nps == 'Yes' and int(nps_contribution) ==14 and rec.tax_regime == 'old_regime':
                #         projection_nps = (current_month_nps + (gross_basic * remaining_month * 10/100))
                #     elif   len(pran_no) == 12 and is_nps == 'Yes' and int(nps_contribution) ==14 and rec.tax_regime == 'new_regime':
                #         projection_nps = (current_month_nps + (gross_basic * remaining_month * 14/100))
                #     else:
                #         projection_nps = 0
                # print('projection_nps==========',projection_nps)
                actual_total_salary = bs-lwop+ sum_prl+ conveyance + productivity+ commitment + lta + prof_persuit + arrear + incentive + variable + splalw + equalw + leave_encahment+ city_alw + trng_inc + erbonus + rec.other_incentive
                projection_total_salary= projection_basic_salary - current_month_lwop + projection_payroll_hra + projection_conveyance + projection_productivity + projection_commitment + projection_lta + projection_prof_persuit + current_month_arrear+current_month_incentive+current_month_variable+current_month_splalw+current_month_equalw+current_month_le+current_month_city+current_month_tinc+current_month_erbonus
                total_salary = actual_total_salary + projection_total_salary
                self.env.cr.execute(f"update hr_declaration set actual_lwop={lwop},projection_lwop={current_month_lwop},lwop={lwop + current_month_lwop},actual_basic_salary={bs},projection_basic_salary={projection_basic_salary},basic_salary={bs + current_month_basic + (gross_basic * remaining_month)},actual_payroll_hra={sum_prl},projection_payroll_hra={projection_payroll_hra},actual_hra={sum_prl+projection_payroll_hra},hra={sum_prl+projection_payroll_hra},actual_conveyance = {conveyance},projection_conveyance={projection_conveyance},conveyance={projection_conveyance+conveyance},actual_productivity={productivity},projection_productivity={projection_productivity},productivity={productivity+projection_productivity},actual_commitment={commitment},projection_commitment={projection_commitment},commitment={commitment+projection_commitment},actual_lta={lta},projection_lta={projection_lta},lta={lta+projection_lta},actual_prof_persuit={prof_persuit},projection_prof_persuit={projection_prof_persuit},prof_persuit={projection_prof_persuit+prof_persuit},actual_arrear={arrear},projection_arrear={current_month_arrear},arrear={arrear+ current_month_arrear},actual_incentive={incentive},projection_incentive={current_month_incentive},incentive={current_month_incentive+incentive},actual_variable={variable},projection_variable={current_month_variable},variable={variable+current_month_variable},actual_splalw={splalw},projection_splalw={current_month_splalw},splalw={splalw+current_month_splalw},actual_equalw={equalw},projection_equalw={current_month_equalw},equalw={equalw+current_month_equalw},actual_leave_encahment={leave_encahment},projection_leave_encahment = {current_month_le},leave_encahment={current_month_le+leave_encahment},actual_city_alw={city_alw},projection_city_alw={current_month_city},city_alw={city_alw+current_month_city},actual_trng_inc={trng_inc},projection_trng_inc={current_month_tinc},trng_inc={current_month_tinc+trng_inc},actual_erbonus={erbonus},projection_erbonus={current_month_erbonus},erbonus={current_month_erbonus+erbonus},actual_total_salary ={actual_total_salary},projection_total_salary= {projection_total_salary},total_salary={total_salary} where id = {rec.id}")
                amount_config = self.env['tds_amount_config'].sudo().search([('date_range','=',rec.date_range.id)],limit=1)
                actual_bool = amount_config.enable_actual if amount_config else False
                previous_income = rec.actual_previous_employer_income if actual_bool == True or rec.actual_previous_employer_income > 0 else rec.previous_employer_income
                previous_tds = rec.actual_tds_previous_employer if actual_bool == True or rec.actual_tds_previous_employer >0 else  rec.tds_previous_employer
                allowed_rebate_under_80ccd2 = 0
                employees_epf = 0
                if enable_epf == 'yes':
                    if pf_deduction == 'other':
                        if epf_percent:
                            employees_epf = epf + (current_month_basic * epf_percent / 100) + (gross_basic * epf_percent / 100) * remaining_month
                        else:
                            employees_epf = epf + 0
                    elif pf_deduction == 'avail1800' and gross_basic >= 15000:
                        employees_epf = epf + 1800 + (1800 * remaining_month)
                    else:
                        employees_epf = rec.calculate_round_amount(epf + rec.calculate_round_amount(current_month_basic * 12 / 100) + rec.calculate_round_amount(gross_basic * 12 / 100) * remaining_month)
                else:
                    employees_epf = 0
                if rec.tax_regime == 'old_regime':
                    # employees_epf = 0
                    # if enable_epf == 'yes':
                    #     if pf_deduction == 'other':
                    #         if epf_percent:
                    #             employees_epf = epf + (current_month_basic * epf_percent / 100) + (gross_basic * epf_percent / 100) * remaining_month
                    #         else:
                    #             employees_epf = epf + 0
                    #     elif pf_deduction == 'avail1800' and gross_basic >= 15000:
                    #         employees_epf = epf + 1800 + (1800 * remaining_month)
                    #     else:
                    #         employees_epf = rec.calculate_round_amount(epf + rec.calculate_round_amount(current_month_basic * 12 / 100) + rec.calculate_round_amount(gross_basic * 12 / 100) * remaining_month)
                    # else:
                    #     employees_epf = 0
                    if len(pran_no) == 12 and is_nps == 'Yes' and nps_contribution in (5,7,10):
                        projection_nps = current_month_nps + ((gross_basic * remaining_month) * int(nps_contribution)/100) 
                    else:
                        if len(pran_no) == 12 and is_nps == 'Yes' and int(nps_contribution) ==14:
                            projection_nps = (current_month_nps + (gross_basic * remaining_month * 10/100))
                        else:
                            projection_nps = 0
                    allowed_rebate_under_80ccd2 = (projection_nps + actual_nps) if employees_epf + projection_nps + actual_nps <= 750000 else 750000
                    pt_gross = gross_basic + gross_hra + gross_conveyance + gross_pb + gross_cb + gross_bonus + gross_pp + gross_ltc
                    if pt_gross * 12 >= 300000:
                        extra_amount = 0 if remaining_month == 0 else 100
                        current_pt = 200 if current_month_gross != 0 else 0
                        pt = ptd + current_pt + (200 * remaining_month) + extra_amount
                    elif pt_gross * 12 >= 160000 and pt_gross * 12 < 300000:
                        current_pt = 125 if current_month_gross != 0 else 0
                        pt = ptd + current_pt + (125 * remaining_month)
                    else:
                        pt = 0
                    basic_40_percent = declared_excess_10_percent=actual_excess_10_percent=final_excess_10_percent=fid_amount=emi_amount=declared_hra_by_employee=actual_hra_by_employee=final_hra_by_employee=0.00
                    self.env.cr.execute(f"select id from health_insurance_dependant where employee_id={ rec.employee_id.id}  and date_range = {rec.date_range.id} and state='approved'")
                    insurance = self._cr.dictfetchall()
                    if insurance: 
                        health_dependant = self.env['health_insurance_dependant'].sudo().browse(insurance[0]['id'])
                        check_parent = health_dependant.family_details_ids.filtered(lambda x:x.relationship_id.kw_id in (3,4))
                        if check_parent:
                            fid_amount += sum(health_dependant.emi_details_ids.mapped('installment'))
                        else:
                            emi_amount += sum(health_dependant.emi_details_ids.mapped('installment'))
                    prl_hlth_dependant = rec.calculate_round_amount(emi_amount)
                    health_insurance_parent = rec.calculate_round_amount(fid_amount)
                    basic_40_percent = rec.calculate_round_amount((bs + current_month_basic + (gross_basic * remaining_month)) * hra_percentage / 100)
                    basic_10_percent = (gross_basic * remaining_month + current_month_basic + bs) * 10 / 100
                    
                    # excess_10_percent = (rec.actual_house_rent_paid - basic_10_percent) if rec.actual_house_rent_paid > 0 or actual_bool == True else (rec.house_rent_paid - basic_10_percent)
                    
                    # excess_10_percent = excess_10_percent if excess_10_percent > 0 else 0
                    
                    # hra_by_employee = rec.actual_house_rent_paid if rec.actual_house_rent_paid > 0 or actual_bool == True else rec.house_rent_paid
                    # lowest_hra = min(rec.actual_hra,excess_10_percent,basic_40_percent)
                    declared_excess_10_percent = rec.house_rent_paid - basic_10_percent
                    declared_excess_10_percent = declared_excess_10_percent if declared_excess_10_percent > 0 else 0
                    actual_excess_10_percent = rec.actual_house_rent_paid - basic_10_percent
                    actual_excess_10_percent = actual_excess_10_percent if actual_excess_10_percent > 0 else 0
                    final_excess_10_percent = actual_excess_10_percent if actual_excess_10_percent > 0 or actual_bool == True else declared_excess_10_percent
                    final_excess_10_percent = final_excess_10_percent if final_excess_10_percent > 0 else 0
                    
                    declared_hra_by_employee = rec.house_rent_paid
                    actual_hra_by_employee = rec.actual_house_rent_paid
                    final_hra_by_employee = actual_hra_by_employee if actual_hra_by_employee > 0 or actual_bool == True else declared_hra_by_employee
                    
                    lowest_hra = min(rec.actual_hra,final_excess_10_percent,basic_40_percent)
                    

                    
                    final_amount_bank_interest=rec.actual_interest_received if rec.actual_interest_received > 0 or actual_bool == True else  rec.interest_received_from_bank
                    final_amount_other_income=rec.actual_income_from_other_sources if rec.actual_income_from_other_sources > 0 or actual_bool == True else  rec.income_from_other_sources
                    actual_income_from_bank_other=rec.actual_interest_received + rec.actual_income_from_other_sources
                    final_income_from_bank_other=final_amount_bank_interest + final_amount_other_income

                    if actual_bool == False:
                        final_lta_spent_by_employee = rec.actual_lta_spent_by_employee  if rec.actual_lta_spent_by_employee > 0 and rec.actual_lta_spent_by_employee <= (lta+projection_lta) else (lta+projection_lta) if rec.actual_lta_spent_by_employee > (lta+projection_lta) else (lta+projection_lta) if rec.lta_spent_by_employee > (lta+projection_lta) and rec.actual_lta_spent_by_employee == 0 else rec.lta_spent_by_employee
                        
                        final_prof_persuit_spent_by_employee = rec.actual_prof_persuit_spent_by_employee  if rec.actual_prof_persuit_spent_by_employee > 0 and rec.actual_prof_persuit_spent_by_employee <= (projection_prof_persuit+prof_persuit) else (projection_prof_persuit+prof_persuit) if rec.actual_prof_persuit_spent_by_employee > (projection_prof_persuit+prof_persuit) else (projection_prof_persuit+prof_persuit) if rec.prof_persuit_spent_by_employee > (projection_prof_persuit+prof_persuit) and rec.actual_prof_persuit_spent_by_employee == 0 else rec.prof_persuit_spent_by_employee
                    else:
                        final_lta_spent_by_employee = rec.actual_lta_spent_by_employee  if rec.actual_lta_spent_by_employee > 0 and rec.actual_lta_spent_by_employee <= (lta+projection_lta) else (lta+projection_lta) if rec.actual_lta_spent_by_employee > (lta+projection_lta) else 0

                        final_prof_persuit_spent_by_employee = rec.actual_prof_persuit_spent_by_employee  if rec.actual_prof_persuit_spent_by_employee > 0 and rec.actual_prof_persuit_spent_by_employee <= (projection_prof_persuit+prof_persuit) else (projection_prof_persuit+prof_persuit) if rec.actual_prof_persuit_spent_by_employee > (projection_prof_persuit+prof_persuit) else 0

                    self.env.cr.execute(f"update hr_declaration set standard_deduction=50000,health_insurance_parent={health_insurance_parent},prl_hlth_dependant={prl_hlth_dependant},actual_professional_tax={ptd},projection_professional_tax={pt - ptd},professional_tax={pt},employees_epf={employees_epf},net_annual_value=gross_annual_value-municipal_taxes,actual_net_annual_value = actual_gross_annual_value-actual_municipal_taxes,standard_30_deduction =(gross_annual_value-municipal_taxes)*30/100,actual_standard_30_deduction = (actual_gross_annual_value-actual_municipal_taxes)*30/100,basic_40_percent={basic_40_percent},excess_10_percent={declared_excess_10_percent},actual_excess_10_percent={actual_excess_10_percent},hra_by_employee={final_hra_by_employee},previous_employer_income_final={previous_income},final_tds_previous_employer={previous_tds},lowest_hra ={lowest_hra},hra_exemption={lowest_hra},final_amount_bank_interest={final_amount_bank_interest},income_from_bank_other=interest_received_from_bank + income_from_other_sources,actual_income_from_bank_other={actual_income_from_bank_other},final_amount_other_income={final_amount_other_income},final_income_from_bank_other={final_income_from_bank_other},final_lta_spent_by_employee = {final_lta_spent_by_employee},final_prof_persuit_spent_by_employee={final_prof_persuit_spent_by_employee},allowed_rebate_under_80ccd2={allowed_rebate_under_80ccd2},nps_projection={projection_nps},nps_actual = {actual_nps},nps={projection_nps+actual_nps} where id = {rec.id}")
                    taxable_salary_from_csm = total_salary - lowest_hra - final_lta_spent_by_employee - final_prof_persuit_spent_by_employee
                    self.env.cr.execute(f"update hr_declaration set taxable_salary_from_csm = {taxable_salary_from_csm} where id = {rec.id}")
                    
                    total_taxable_salary =  taxable_salary_from_csm + previous_income - 50000 - pt
                    self.env.cr.execute(f"update hr_declaration set total_taxable_salary = {total_taxable_salary} where id = {rec.id}")
                    amnt_80c=tot_80c_invst =tot_80ccd= tot_80ccd_invst=amnt_80dd=total_80dd=total_80u=amnt_80e=amnt_80ddb=amnt_80g=actual_80c = declared_80c= actual_80ccd=declared_80ccd=amnt_80u=0
                    # Slab 80c calculation max limit 150000
                    self.env.cr.execute(f"select sum(l.actual_amt) as actual_amt,sum(l.investment) as investment from declaration_slab l join hr_itrule r on l.it_rule = r.id where l.slab_id = {rec.id}")
                    slab_ids_dict = self._cr.dictfetchall()
                    self.env.cr.execute(f"select sum(rebate)  filter (where it_rule in (select id from hr_itrule where code='80_c')) as slab_80c_rebate ,sum(rebate) filter (where it_rule in (select id from hr_itrule where code='80ccd')) as slab_80ccd_rebate ,sum(rebate)  filter (where it_rule in (select id from hr_itrule where code='80ddb')) as slab_80ddb_rebate from saving_master")
                    rebate_dict = self._cr.dictfetchall()
                    
                    actual_80c = slab_ids_dict[0]['actual_amt'] if  slab_ids_dict[0]['actual_amt'] else 0
                    declared_80c=  slab_ids_dict[0]['investment'] if  slab_ids_dict[0]['investment'] else 0
                    tot_80c_invst =  rebate_dict[0]['slab_80c_rebate'] if  rebate_dict[0]['slab_80c_rebate'] else 0
                    # if remaining_month < 1:
                    if actual_bool == True:
                            amnt_80c = actual_80c + employees_epf  if (actual_80c + employees_epf ) <= tot_80c_invst else tot_80c_invst
                    else:
                        if (declared_80c+ employees_epf )>=(actual_80c+ employees_epf):
                            amnt_80c = tot_80c_invst  if (declared_80c + employees_epf) >= tot_80c_invst else  (declared_80c + employees_epf )
                        else:
                            if (actual_80c + employees_epf) >= tot_80c_invst:
                                amnt_80c = tot_80c_invst
                            else:
                                amnt_80c = actual_80c +  employees_epf 
                    self.env.cr.execute(f"select sum(l.actual_amt) as actual_amt,sum(l.investment) as investment from declaration_slab_ccd l join hr_itrule r on l.it_rule = r.id where l.slab_ccd_id = {rec.id}")
                    slab_ccd_dict = self._cr.dictfetchall()
                    actual_80ccd= slab_ccd_dict[0]['actual_amt'] if  slab_ccd_dict[0]['actual_amt'] else 0
                    declared_80ccd= slab_ccd_dict[0]['investment'] if  slab_ccd_dict[0]['investment'] else 0
                    tot_80ccd_invst = rebate_dict[0]['slab_80ccd_rebate'] if  rebate_dict[0]['slab_80ccd_rebate'] else 0
                    if actual_bool == True:
                        tot_80ccd = actual_80ccd if actual_80ccd <= tot_80ccd_invst else tot_80ccd_invst
                    else:
                        if declared_80ccd >= actual_80ccd:
                            tot_80ccd = tot_80ccd_invst  if declared_80ccd >= tot_80ccd_invst else declared_80ccd
                        else:
                            tot_80ccd = tot_80ccd_invst if actual_80ccd >= tot_80ccd_invst else actual_80ccd
                    amnt_parent_above_60_rebate=amnt_parent_above_60=amnt_parent_below_60_rebate=amnt_parent_below_60=amnt_self_above_60_rebate=actual_80ddb=declared_80ddb=amnt_self_below_60=amnt_self_below_60_rebate=amnt_self_above_60=actual_80d=declared_80d=actual_80d_parent_below_60=declared_80d_parent_below_60=actual_80d_spouse_below_60=declared_80d_spouse_below_60=actual_80d_parent_above_60=declared_80d_parent_above_60=0
                    self.env.cr.execute(f"select sum(rebate) filter (where code = 'MIPB') as amnt_self_below_60_rebate,sum(rebate) filter (where code = 'MIPS') as amnt_self_above_60_rebate,sum(rebate) filter (where code = 'MIPSPB') as amnt_parent_below_60_rebate,sum(rebate) filter (where code = 'MIPSP') as amnt_parent_above_60_rebate from saving_master")
                    saving_master_dict = self._cr.dictfetchall()
                    amnt_self_below_60_rebate = saving_master_dict[0]['amnt_self_below_60_rebate'] if saving_master_dict[0]['amnt_self_below_60_rebate'] else 0
                    amnt_self_above_60_rebate = saving_master_dict[0]['amnt_self_above_60_rebate'] if saving_master_dict[0]['amnt_self_above_60_rebate'] else 0
                    amnt_parent_below_60_rebate = saving_master_dict[0]['amnt_parent_below_60_rebate'] if saving_master_dict[0]['amnt_parent_below_60_rebate'] else 0
                    amnt_parent_above_60_rebate = saving_master_dict[0]['amnt_parent_above_60_rebate'] if saving_master_dict[0]['amnt_parent_above_60_rebate'] else 0
        #             for lines in rec.slab_80d_ids:
                    self.env.cr.execute(f"select sum(l.actual_amt) filter (where m.code = 'MIPB') as actual_80d,sum(l.investment) filter (where m.code = 'MIPB') as declared_80d,sum(l.actual_amt) filter (where m.code = 'MIPS') as actual_80d_spouse_below_60,sum(l.investment) filter (where m.code = 'MIPS') as declared_80d_spouse_below_60,sum(l.actual_amt) filter (where m.code = 'MIPSPB') as actual_80d_parent_below_60,sum(l.investment) filter (where m.code = 'MIPSPB') as declared_80d_parent_below_60,sum(l.actual_amt) filter (where m.code = 'MIPSP') as actual_80d_parent_above_60,sum(l.investment) filter (where m.code = 'MIPSP') as declared_80d_parent_above_60 from slab_declaration_80d l join saving_master m on  l.saving_master = m.id where l.slab_80d_id={rec.id}")
                    slab_80d_dict = self._cr.dictfetchall()
                    if slab_80d_dict:
                        actual_80d = slab_80d_dict[0]['actual_80d']  if slab_80d_dict[0]['actual_80d'] else 0
                        declared_80d = slab_80d_dict[0]['declared_80d']  if slab_80d_dict[0]['declared_80d'] else 0
                        actual_80d_spouse_below_60 = slab_80d_dict[0]['actual_80d_spouse_below_60']  if slab_80d_dict[0]['actual_80d_spouse_below_60'] else 0
                        declared_80d_spouse_below_60 = slab_80d_dict[0]['declared_80d_spouse_below_60']  if slab_80d_dict[0]['declared_80d_spouse_below_60'] else 0
                        actual_80d_parent_below_60 =  slab_80d_dict[0]['actual_80d_parent_below_60']  if slab_80d_dict[0]['actual_80d_parent_below_60'] else 0
                        declared_80d_parent_below_60 = slab_80d_dict[0]['declared_80d_parent_below_60']  if slab_80d_dict[0]['declared_80d_parent_below_60'] else 0
                        actual_80d_parent_above_60 = slab_80d_dict[0]['actual_80d_parent_above_60']  if slab_80d_dict[0]['actual_80d_parent_above_60'] else 0
                        declared_80d_parent_above_60 = slab_80d_dict[0]['declared_80d_parent_above_60']  if slab_80d_dict[0]['declared_80d_parent_above_60'] else 0
                    if actual_bool == True:
                        amnt_self_below_60 = actual_80d if actual_80d <= amnt_self_below_60_rebate else amnt_self_below_60_rebate
                    else:
                        if declared_80d >= actual_80d:
                            amnt_self_below_60 = amnt_self_below_60_rebate  if declared_80d >= amnt_self_below_60_rebate else declared_80d
                        else:
                            amnt_self_below_60 = amnt_self_below_60_rebate if actual_80d >= amnt_self_below_60_rebate else actual_80d
                    if actual_bool == True:
                        amnt_self_above_60 = actual_80d_spouse_below_60 if actual_80d_spouse_below_60 <= amnt_self_above_60_rebate else amnt_self_above_60_rebate
                    else:
                        if declared_80d_spouse_below_60 >= actual_80d_spouse_below_60:
                            amnt_self_above_60 = amnt_self_above_60_rebate  if declared_80d_spouse_below_60 >= amnt_self_above_60_rebate else declared_80d_spouse_below_60
                        else:
                            amnt_self_above_60 = amnt_self_above_60_rebate if actual_80d_spouse_below_60 >= amnt_self_above_60_rebate else actual_80d_spouse_below_60
                    if actual_bool == True:
                        amnt_parent_below_60 = actual_80d_parent_below_60 if actual_80d_parent_below_60 <= amnt_parent_below_60_rebate else amnt_parent_below_60_rebate
                    else:
                        if declared_80d_parent_below_60 >= actual_80d_parent_below_60:
                            amnt_parent_below_60 = amnt_parent_below_60_rebate  if declared_80d_parent_below_60 >= amnt_parent_below_60_rebate else declared_80d_parent_below_60
                        else:
                            amnt_parent_below_60 = amnt_parent_below_60_rebate if actual_80d_parent_below_60 >= amnt_parent_below_60_rebate else actual_80d_parent_below_60
                    if actual_bool == True:
                        amnt_parent_above_60 = actual_80d_parent_above_60 if actual_80d_parent_above_60 <= amnt_parent_above_60_rebate else amnt_parent_above_60_rebate
                    else:
                        if declared_80d_parent_above_60 >= actual_80d_parent_above_60:
                            amnt_parent_above_60 = amnt_parent_above_60_rebate  if declared_80d_parent_above_60 >= amnt_parent_above_60_rebate else declared_80d_parent_above_60
                        else:
                            amnt_parent_above_60 = amnt_parent_above_60_rebate if actual_80d_parent_above_60 >= amnt_parent_above_60_rebate else actual_80d_parent_above_60
                    if amnt_self_above_60 > 0:
                        tot_self = amnt_self_above_60  + prl_hlth_dependant + amnt_self_below_60
                        deduction_self = tot_self if tot_self < amnt_self_above_60_rebate else amnt_self_above_60_rebate
                    else:
                        tot_self = amnt_self_below_60  + prl_hlth_dependant
                        deduction_self = tot_self if tot_self < amnt_self_below_60_rebate else amnt_self_below_60_rebate

                    if amnt_parent_above_60 > 0:
                        tot_dependent = amnt_parent_above_60 + health_insurance_parent + amnt_parent_below_60
                        deduction_dependent = tot_dependent if tot_dependent < amnt_parent_above_60_rebate else amnt_parent_above_60_rebate
                    else:
                        tot_dependent = amnt_parent_below_60 + health_insurance_parent
                        deduction_dependent = tot_dependent if tot_dependent < amnt_parent_below_60_rebate else amnt_parent_below_60_rebate
                    # tot_80dd_invst = 0
                    for lines in rec.slab_80dd_ids:
                        amnt_80dd += lines.investment if actual_bool == False else lines.actual_amt
                        # tot_80dd_invst += lines.saving_master.rebate
                    total_80dd += amnt_80dd
                    # tot_80u_invst = 0
                    for lines_80u in rec.slab_80u_ids:
                        amnt_80u += lines_80u.investment if actual_bool == False else lines_80u.actual_amt
                        # tot_80u_invst += lines_80u.saving_master.rebate
                    total_80u += amnt_80u
                    self.env.cr.execute(f"select sum(l.actual_amt) as actual_amt,sum(l.investment)  as investment from declaration_slab_80e l  where l.slab_80e_id = {rec.id}")
                    slab_80e_dict = self._cr.dictfetchall()
                    
                    if actual_bool == True:
                        amnt_80e = slab_80e_dict[0]['actual_amt'] if slab_80e_dict[0]['actual_amt'] else 0
                    else:
                        amnt_80e = max(slab_80e_dict[0]['actual_amt'] if slab_80e_dict[0]['actual_amt'] else 0,slab_80e_dict[0]['investment'] if slab_80e_dict[0]['investment'] else 0)
                    actual_80g = declared_80g =0
                    self.env.cr.execute(f"select sum(l.actual_amt) as actual_amt,sum(l.investment) as investment from  declaration_slab_80g l join saving_master m on l.saving_master =m.id where m.code='80GN' and slab_80g_id =  {rec.id}")
                    slab_80gn_dict = self._cr.dictfetchall()
                    self.env.cr.execute(f"select sum(l.actual_amt) as actual_amt ,sum(l.investment) as investment from  declaration_slab_80g l join saving_master m on l.saving_master =m.id where m.code='80G' and slab_80g_id = {rec.id}")
                    slab_80g_dict = self._cr.dictfetchall()
                    actual_80g = slab_80gn_dict[0]['actual_amt'] if slab_80gn_dict[0]['actual_amt'] else 0
                    declared_80g = slab_80gn_dict[0]['investment'] if slab_80gn_dict[0]['investment'] else 0
                    if actual_bool == True:
                        amnt_80g += actual_80g/2
                    else:
                        amnt_80g += max(actual_80g,declared_80g)/2
                    actual_80g = declared_80g=0
                    actual_80g = slab_80g_dict[0]['actual_amt']  if slab_80g_dict[0]['actual_amt'] else 0
                    declared_80g = slab_80g_dict[0]['investment']  if  slab_80g_dict[0]['investment'] else 0
                    if actual_bool == True:
                        amnt_80g += actual_80g
                    else:
                        amnt_80g += max(actual_80g,declared_80g)      
                    self.env.cr.execute(f"select sum(l.actual_amt) as actual_amt,sum(l.investment)  as investment from declaration_slab_80ddb l join hr_itrule r on r.id = l.it_rule where l.slab_80ddb_id = {rec.id}")
                    slab_80ddb_dict = self._cr.dictfetchall()
                    allowed_rebate_under_80ddb = 0
                    if slab_80ddb_dict:
                        actual_80ddb = slab_80ddb_dict[0]['actual_amt'] if slab_80ddb_dict[0]['actual_amt'] else 0
                        declared_80ddb = slab_80ddb_dict[0]['investment'] if slab_80ddb_dict[0]['investment'] else 0
                        tot_80ddb_invst = rebate_dict[0]['slab_80ddb_rebate'] if  rebate_dict[0]['slab_80ddb_rebate'] else 0
                        if actual_bool == True:
                            amnt_80ddb = actual_80ddb if actual_80ddb <= tot_80ddb_invst else tot_80ddb_invst
                        else:
                            if declared_80ddb >= actual_80ddb:
                                amnt_80ddb = tot_80ccd_invst  if declared_80ddb >= tot_80ccd_invst else declared_80ddb
                            else:
                                amnt_80ddb = tot_80ccd_invst if actual_80ddb >= tot_80ccd_invst else actual_80ddb
                    if emp_age >= 60:
                        allowed_rebate_under_80ddb = tot_80ddb_invst if  amnt_80ddb >= tot_80ddb_invst else amnt_80ddb
                    else:
                        allowed_rebate_under_80ddb = 40000 if  amnt_80ddb >= 40000 else amnt_80ddb
                    amount_80d = deduction_self + deduction_dependent
                    
                    # total_income_interest= rec.gross_annual_value-rec.municipal_taxes - (rec.gross_annual_value-rec.municipal_taxes)*30/100 - (rec.actual_interest_payment if actual_bool == True else rec.temp_interest_payment)
                    final_gross_annual_value = final_gross_30_percent=0
                    final_gross_annual_value = (rec.actual_gross_annual_value-rec.actual_municipal_taxes) if actual_bool == True or rec.actual_gross_annual_value > 0 else (rec.gross_annual_value-rec.municipal_taxes)
                    final_gross_30_percent = final_gross_annual_value *30/100
                    final_interest_payment = rec.actual_interest_payment if actual_bool == True or  rec.actual_interest_payment > 0 else rec.temp_interest_payment
                    total_income_interest= final_gross_annual_value - final_gross_30_percent - final_interest_payment
                     
                    self.env.cr.execute(f"update hr_declaration set allowed_rebate_under_80c = {amnt_80c},allowed_rebate_under_80ccd = {tot_80ccd},allowed_rebate_under_80ddb={allowed_rebate_under_80ddb},allowed_rebate_under_80g={amnt_80g},allowed_rebate_under_80e={amnt_80e},tot_80dd={amnt_80dd},allowed_rebate_under_80dd={total_80dd},allowed_rebate_under_80u={total_80u},allowed_rebate_under_80d={amount_80d},total_income_interest={total_income_interest} where id = {rec.id}")
                    self.env.cr.execute(f"select rebate from saving_master where code = 'IP'")
                    ip_rebate = self._cr.dictfetchall()[0]['rebate']
                    if total_income_interest < 0:
                        temp_income_interest = total_income_interest if -(total_income_interest) < ip_rebate else -(ip_rebate)
                    else:
                        temp_income_interest = total_income_interest
                    gross_total_income=(total_taxable_salary + temp_income_interest + final_income_from_bank_other) if (total_taxable_salary + temp_income_interest + final_income_from_bank_other) > 0 else 0
                    # final_amount_other_income= rec.actual_income_from_other_sources if remaining_month < 1 else rec.income_from_other_sources
                    final_amount= amnt_80c + tot_80ccd + allowed_rebate_under_80ddb + deduction_self + deduction_dependent  + amnt_80e + amnt_80g + total_80dd + total_80u + allowed_rebate_under_80ccd2
                    
                    self.env.cr.execute(f"update hr_declaration set calculate_interest_payment={temp_income_interest},final_amount={final_amount},gross_total_income={gross_total_income} where id = {rec.id}")
                    temp_taxable_income = gross_total_income - final_amount
                    if (temp_taxable_income % 10) >= 5:
                        z = 10 - (temp_taxable_income % 10)
                        tax_amount = temp_taxable_income + z
                    else:
                        tax_amount = temp_taxable_income - (temp_taxable_income % 10)
                    tax_amount = tax_amount if tax_amount > 0 else 0
                    self.env.cr.execute(f"update hr_declaration set taxable_income ={tax_amount} where id = {rec.id}")
                    temp_tax_payable = rec.calculate_tax_payable(emp_age,tax_amount,rec.date_range.id)
                    
                    temp_taxable_income_wo = gross_total_income - final_amount - current_month_arrear-current_month_incentive-current_month_variable-current_month_splalw-current_month_equalw-current_month_le-current_month_city-current_month_tinc-current_month_erbonus
                    if (temp_taxable_income_wo % 10) >= 5:
                        z = 10 - (temp_taxable_income_wo % 10)
                        tax_amount_wo = temp_taxable_income_wo + z
                    else:
                        tax_amount_wo = temp_taxable_income_wo - (temp_taxable_income_wo % 10)
                    tax_amount_wo = tax_amount_wo if tax_amount_wo > 0 else 0
                    temp_tax_payable_without_projection_al = rec.calculate_tax_payable(emp_age,tax_amount_wo,rec.date_range.id)
                    self.env.cr.execute(f"update hr_declaration set tax_payable={temp_tax_payable},rebate={temp_tax_payable if tax_amount < 500000 and temp_tax_payable > 0 else 0}  where id = {rec.id}")
                    # wo_rebate = temp_tax_payable_without_projection_al if tax_amount_wo < 500000 and temp_tax_payable_without_projection_al > 0 else 0
                    temp_net_tax_payable = temp_tax_payable - (temp_tax_payable if tax_amount < 500000 and temp_tax_payable > 0 else 0)
                    net_tax_payable = temp_net_tax_payable if temp_net_tax_payable > 0 else 0
                    self.env.cr.execute(f"update hr_declaration set net_tax_payable={net_tax_payable} where id = {rec.id}")
                    wo_temp_net_tax_payable = temp_tax_payable_without_projection_al - (temp_tax_payable_without_projection_al if tax_amount_wo < 500000 and temp_tax_payable_without_projection_al > 0 else 0)
                    wo_net_tax_payable = wo_temp_net_tax_payable if wo_temp_net_tax_payable > 0 else 0
                    self.env.cr.execute(f"select cess from tax_cess where date_range= {rec.date_range.id} and salary_from <= {tax_amount} and salary_to >= {tax_amount} and tax_regime = 'old_regime' and age_from <= {emp_age} and age_to >={emp_age} LIMIT 1")
                    cess_details = self._cr.dictfetchall()
                    
                    self.env.cr.execute(f"select cess from tax_cess where date_range= {rec.date_range.id} and salary_from <= {tax_amount_wo} and salary_to >= {tax_amount_wo} and tax_regime = 'old_regime' and age_from <= {emp_age} and age_to >={emp_age} LIMIT 1")
                    wo_cess_details = self._cr.dictfetchall()
                    
                    self.env.cr.execute(f"select surcharge from tax_surcharge where date_range= {rec.date_range.id} and salary_from <= {tax_amount} and salary_to >= {tax_amount} and tax_regime = 'old_regime' LIMIT 1")
                    surcharge_details = self._cr.dictfetchall()
                    
                    self.env.cr.execute(f"select surcharge from tax_surcharge where date_range= {rec.date_range.id} and salary_from <= {tax_amount_wo} and salary_to >= {tax_amount_wo} and tax_regime = 'old_regime' LIMIT 1")
                    wo_surcharge_details = self._cr.dictfetchall()
                    
                    additional_sub_chrg = additional_edu_cess= wo_additional_sub_chrg =wo_additional_edu_cess = 0
                    if surcharge_details:
                        additional_sub_chrg = rec.calculate_round_amount(net_tax_payable * (surcharge_details[0]['surcharge'] if surcharge_details[0]['surcharge'] else 0) / 100)
                    if cess_details:
                        additional_edu_cess = rec.calculate_round_amount(net_tax_payable *(cess_details[0]['cess']  if cess_details[0]['cess'] else 0) / 100)
                        
                    if wo_surcharge_details:
                        wo_additional_sub_chrg = rec.calculate_round_amount(wo_net_tax_payable * (wo_surcharge_details[0]['surcharge'] if surcharge_details[0]['surcharge'] else 0) / 100)
                    if wo_cess_details:
                        wo_additional_edu_cess = rec.calculate_round_amount(wo_net_tax_payable *(wo_cess_details[0]['cess']  if wo_cess_details[0]['cess'] else 0) / 100)
                    
                    self.env.cr.execute(f"update hr_declaration set additional_sub_chrg= {additional_sub_chrg},additional_edu_cess= {additional_edu_cess} where id = {rec.id}")
                        
                    total_tax_payable = net_tax_payable + additional_sub_chrg + additional_edu_cess
                    if (total_tax_payable % 10) >= 5:
                        z = 10 - (total_tax_payable % 10)
                        var_tax_payable = total_tax_payable + z
                    else:
                        var_tax_payable = total_tax_payable - (total_tax_payable % 10)
                        
                        
                    wo_total_tax_payable = wo_net_tax_payable + wo_additional_sub_chrg + wo_additional_edu_cess
                    if (wo_total_tax_payable % 10) >= 5:
                        z = 10 - (wo_total_tax_payable % 10)
                        wo_var_tax_payable = wo_total_tax_payable + z
                    else:
                        wo_var_tax_payable = wo_total_tax_payable - (wo_total_tax_payable % 10)
                    tax_recovered= tds + previous_tds
                    
                    self.env.cr.execute(f"update hr_declaration set total_tax_payable= {var_tax_payable},tax_recovered= {tax_recovered} where id = {rec.id}")
                    balance_tax_payable =  var_tax_payable-tds-previous_tds
                    wo_balance_tax_payable =  wo_var_tax_payable-tds-previous_tds
                    
                    self.env.cr.execute(f"update hr_declaration set balance_tax_payable={balance_tax_payable},wo_balance_tax_payable={wo_balance_tax_payable} where id = {rec.id}")
                    self.env.cr.execute(f"update hr_declaration set monthly_tax_to_recover={((balance_tax_payable)/tds_month) if (var_tax_payable - tax_recovered) >0 and tds_month > 0 else 0} where id = {rec.id}")
                    
                else:
                    total_income_interest = 0
                    total_income_interest = (rec.actual_gross_annual_value-rec.actual_municipal_taxes) if actual_bool == True or rec.actual_gross_annual_value > 0 else (rec.gross_annual_value-rec.municipal_taxes)
                    
                    
                    self.env.cr.execute(f"update hr_declaration set taxable_salary_from_csm=total_salary,standard_deduction=75000,allowed_rebate_under_80ccd=0,allowed_rebate_under_80ddb=0,allowed_rebate_under_80u = 0,allowed_rebate_under_80d=0,allowed_rebate_under_80dd = 0,allowed_rebate_under_80e = 0,allowed_rebate_under_80g = 0,final_lta_spent_by_employee = 0,final_prof_persuit_spent_by_employee = 0,actual_net_annual_value=actual_gross_annual_value - actual_municipal_taxes,previous_employer_income_final = {previous_income},final_tds_previous_employer={previous_tds},hra_by_employee = 0,excess_10_percent = 0,actual_excess_10_percent=0,actual_hra = 0,basic_40_percent = 0,lowest_hra = 0,standard_30_deduction = 0,actual_standard_30_deduction=0,net_annual_value = gross_annual_value - municipal_taxes,total_income_interest =  {total_income_interest},hra_exemption = 0,professional_tax = 0,actual_professional_tax = 0,projection_professional_tax = 0,employees_epf = 0,total_80c_payable = 0,allowed_rebate_under_80c = 0,final_amount_bank_interest= 0,final_amount_other_income= 0,final_income_from_bank_other = 0,actual_house_rent_paid = 0,house_rent_paid=0 where id = {rec.id};update declaration_slab set investment= 0,actual_amt=0 where slab_id = {rec.id};update declaration_slab_ccd set investment= 0,actual_amt=0 where slab_ccd_id = {rec.id};update slab_declaration_80d set investment=0,actual_amt=0 where slab_80d_id={rec.id};update declaration_slab_80dd set handicapped_percent=0,actual_handicapped_percent=0 where slab_80dd_id ={rec.id};update declaration_slab_80e set investment=0,actual_amt=0 where slab_80e_id={rec.id};update declaration_slab_80g set investment=0,actual_amt=0 where slab_80g_id={rec.id};update declaration_slab_80ddb set investment=0,actual_amt=0 where slab_80ddb_id={rec.id}")
                    self.env.cr.execute(f"select rebate from saving_master where code = 'IP'")
                    ip_rebate = self._cr.dictfetchall()[0]['rebate']
                    if total_income_interest < 0:
                        temp_income_interest = total_income_interest if -(total_income_interest) < ip_rebate else -(ip_rebate)
                    else:
                        temp_income_interest = total_income_interest
                        
                    calculate_interest_payment = temp_income_interest
                    final_amount_other_income = rec.actual_income_from_other_sources if rec.actual_income_from_other_sources > 0 or actual_bool == True else rec.income_from_other_sources
                    final_amount_bank_interest = rec.actual_interest_received if rec.actual_interest_received > 0 or actual_bool == True else  rec.interest_received_from_bank
                    

                    income_from_bank_other =rec.interest_received_from_bank + rec.income_from_other_sources

                    actual_income_from_bank_other=rec.actual_interest_received + rec.actual_income_from_other_sources

                    final_income_from_bank_other = final_amount_bank_interest + final_amount_other_income
                    
                          
                    total_taxable_salary =  actual_total_salary + projection_total_salary + previous_income - 75000 
                    temp_gross_total_income = (total_taxable_salary + calculate_interest_payment + final_income_from_bank_other)
                    gross_total_income = temp_gross_total_income if temp_gross_total_income > 0 else 0
                    if len(pran_no) == 12 and is_nps == 'Yes' and nps_contribution in (5,7,10,14):
                        projection_nps = current_month_nps + ((gross_basic * remaining_month) * int(nps_contribution)/100) 
                    else:
                        projection_nps = 0
                    allowed_rebate_under_80ccd2 = (projection_nps + actual_nps) if (employees_epf + projection_nps + actual_nps) <= 750000 else 750000
                    self.env.cr.execute(f"update hr_declaration set calculate_interest_payment={temp_income_interest},final_amount_other_income={final_amount_other_income},final_amount_bank_interest={final_amount_bank_interest},income_from_bank_other={income_from_bank_other},actual_income_from_bank_other={actual_income_from_bank_other},final_income_from_bank_other={final_income_from_bank_other},final_amount={allowed_rebate_under_80ccd2},total_taxable_salary={total_taxable_salary},gross_total_income={gross_total_income} where id = {rec.id}")
                    
                    temp_taxable_income = gross_total_income - (allowed_rebate_under_80ccd2)
                    
                    if (temp_taxable_income % 10) >= 5:
                        z = 10 - (temp_taxable_income % 10)
                        tax_amount = temp_taxable_income + z
                    else:
                        tax_amount = temp_taxable_income - (temp_taxable_income % 10)
                    tax_amount = tax_amount if tax_amount > 0 else 0
                    self.env.cr.execute(f"update hr_declaration set taxable_income = {tax_amount} where id = {rec.id}")
                    temp_tax_payable = rec.claculate_new_regime_tax(tax_amount,rec.date_range.id)
                    temp_taxable_income_wo = gross_total_income - current_month_arrear-current_month_incentive-current_month_variable-current_month_splalw-current_month_equalw-current_month_le-current_month_city-current_month_tinc-current_month_erbonus - allowed_rebate_under_80ccd2
                    if (temp_taxable_income_wo % 10) >= 5:
                        z = 10 - (temp_taxable_income_wo % 10)
                        tax_amount_wo = temp_taxable_income_wo + z
                    else:
                        tax_amount_wo = temp_taxable_income_wo - (temp_taxable_income_wo % 10)
                    tax_amount_wo = tax_amount_wo if tax_amount_wo > 0 else 0
                    temp_tax_payable_without_projection_al = rec.claculate_new_regime_tax(tax_amount_wo,rec.date_range.id)
                    wo_tax_payable = temp_tax_payable_without_projection_al if temp_tax_payable_without_projection_al > 0 else 0
                    
                    tax_payable = temp_tax_payable if temp_tax_payable > 0 else 0
                    rebate = tax_payable if tax_amount <= 700000 and tax_payable > 0 else 0
                    wo_rebate = wo_tax_payable if tax_amount_wo <= 700000 and wo_tax_payable > 0 else 0
                    
                    temp_net_tax_payable = tax_payable - rebate
                    wo_temp_net_tax_payable = wo_tax_payable - wo_rebate
                    
                    net_tax_payable = temp_net_tax_payable if temp_net_tax_payable  > 0 else 0
                    self.env.cr.execute(f"update hr_declaration set tax_payable={tax_payable},rebate = {rebate},net_tax_payable={net_tax_payable} where id = {rec.id}")
                  
                    wo_net_tax_payable = wo_temp_net_tax_payable if wo_temp_net_tax_payable > 0 else 0
                    self.env.cr.execute(f"select surcharge from tax_surcharge where date_range= {rec.date_range.id} and salary_from <= {tax_amount} and salary_to >= {tax_amount} and tax_regime = 'new_regime' LIMIT 1")
                    surcharge_details = self._cr.dictfetchall()
                    
                    self.env.cr.execute(f"select surcharge from tax_surcharge where date_range= {rec.date_range.id} and salary_from <= {tax_amount_wo} and salary_to >= {tax_amount_wo} and tax_regime = 'new_regime' LIMIT 1")
                    wo_surcharge_details = self._cr.dictfetchall()
                    
                    self.env.cr.execute(f"select cess from tax_cess where date_range = {rec.date_range.id} and salary_from <= {tax_amount} and salary_to >= {tax_amount} and tax_regime = 'new_regime' LIMIT 1")
                    cess_details = self._cr.dictfetchall()
                    
                    self.env.cr.execute(f"select cess from tax_cess where date_range= {rec.date_range.id} and salary_from <= {tax_amount_wo} and salary_to >= {tax_amount_wo} and tax_regime = 'new_regime' LIMIT 1")
                    wo_cess_details = self._cr.dictfetchall()
                    # print('tax_amount====================',tax_amount,'tax_amount_wo==============',tax_amount_wo)
                    additional_sub_chrg = additional_edu_cess = wo_additional_edu_cess=wo_additional_sub_chrg=0
                    if surcharge_details:
                        additional_sub_chrg = rec.calculate_round_amount(net_tax_payable * (surcharge_details[0]['surcharge'] if surcharge_details[0]['surcharge'] else 0) / 100)
                    if cess_details:
                        additional_edu_cess = rec.calculate_round_amount(net_tax_payable *(cess_details[0]['cess']  if cess_details[0]['cess'] else 0) / 100)
                    
                    if wo_surcharge_details:
                        wo_additional_sub_chrg = rec.calculate_round_amount(wo_net_tax_payable * (wo_surcharge_details[0]['surcharge'] if surcharge_details[0]['surcharge'] else 0) / 100)
                    if wo_cess_details:
                        wo_additional_edu_cess = rec.calculate_round_amount(wo_net_tax_payable *(wo_cess_details[0]['cess']  if wo_cess_details[0]['cess'] else 0) / 100)
                        
                    self.env.cr.execute(f"update hr_declaration set additional_sub_chrg= {additional_sub_chrg},additional_edu_cess= {additional_edu_cess} where id = {rec.id}")
                    total_tax_payable = net_tax_payable + additional_sub_chrg + additional_edu_cess
                    if (total_tax_payable % 10) >= 5:
                        z = 10 - (total_tax_payable % 10)
                        var_tax_payable = total_tax_payable + z
                    else:
                        var_tax_payable = total_tax_payable - (total_tax_payable % 10)
                    wo_total_tax_payable = wo_net_tax_payable + wo_additional_sub_chrg + wo_additional_edu_cess
                    # print('total_tax_payable==========',total_tax_payable,'wo_total_tax_payable==============',wo_total_tax_payable)
                    if (wo_total_tax_payable % 10) >= 5:
                        z = 10 - (wo_total_tax_payable % 10)
                        wo_var_tax_payable = wo_total_tax_payable + z
                    else:
                        wo_var_tax_payable = wo_total_tax_payable - (wo_total_tax_payable % 10)
                    # print('var_tax_payable=====================',var_tax_payable-tds-previous_tds)
                    wo_balance_tax_payable =  wo_var_tax_payable-tds-previous_tds
                    # print('wo_balance_tax_payable====================',wo_balance_tax_payable)
                    self.env.cr.execute(f"update hr_declaration set total_tax_payable= {var_tax_payable},tax_recovered= {tds + previous_tds}  where id = {rec.id}")
                    self.env.cr.execute(f"update hr_declaration set balance_tax_payable={var_tax_payable - (tds + previous_tds)},wo_balance_tax_payable={wo_balance_tax_payable},monthly_tax_to_recover={((var_tax_payable - (tds + previous_tds))/tds_month) if (var_tax_payable - (tds + previous_tds)) >0 and tds_month > 0 else 0} where id = {rec.id}")

       
    
    # @api.onchange('income_from_other_sources')
    # def change_income_from_other_sources(self):
    #     if self.income_from_other_sources == 0:
    #         self.income_from_other_sources_doc = False
    #         self.other_source_income_file_name = False

    @api.depends('state')
    def _compute_css(self):
        ir_config_params = self.env['ir.config_parameter'].sudo()
        actual_end_month = ir_config_params.get_param('tds.end_month') or False
        actual_end_day = ir_config_params.get_param('tds.end_day') or False
        if actual_end_month != False and actual_end_day != False:
            for record in self:
                actual_end_date = date(record.date_range.date_stop.year,int(actual_end_month),int(actual_end_day))
                if (record.state == 'approved' and not  self.env.user.has_group('tds.group_report_manager_declaration'))  or ( actual_end_date < datetime.today().date() and not  self.env.user.has_group('tds.group_report_manager_declaration')):
                    record.test_css = '<style>.o_form_button_edit {display: none !important;}</style>'
                else:
                    record.test_css = False


    # def current_dt(self):
    #     return (datetime.now().strftime("%d-%m-%Y"))

    
    # def recent_time(self):
    #     return str(datetime.now().strftime("%H:%M:%S")) + "+5'30'" 


    # def current_date(self):
    #     today_date = date.today()
    #     return today_date

    

    # def digital_signature(self):
    #     digital_sign = self.env['digital_sign'].sudo().search([],limit=1)
    #     return digital_sign.digital_signat

    # @api.multi  
    # def employer_pan(self):
    #     ir_config_parameter = self.env['ir.config_parameter'].sudo()
    #     company_pan = ir_config_parameter.get_param('tds.company_pan') or ''
    #     return company_pan

    # @api.multi  
    # def employer_tan(self):
    #     ir_config_parameter = self.env['ir.config_parameter'].sudo()
    #     company_tan = ir_config_parameter.get_param('tds.company_tan') or ''
    #     return company_tan

    # @api.model
    # def _check_tds_period_from(self):
    #     for rec in self:
    #         from_date = ''
    #         join_date = rec.date_of_joining
    #         resignation_employee = self.env['kw_resignation'].sudo().search([('applicant_id','=',rec.employee_id.id)])
    #         if resignation_employee:
    #             if join_date >= rec.date_range.date_start:
    #                 from_date = join_date
    #             else:
    #                 from_date = rec.date_range.date_start
    #         else:
    #             if join_date >= rec.date_range.date_start:
    #                 from_date = join_date
    #             else:
    #                 from_date = rec.date_range.date_start
    #         modified_from_date = from_date.strftime('%d-%b-%Y')
    #         return modified_from_date


    # def _check_tds_period_to(self):
    #     for rec in self:
    #         to_date = ''
    #         resignation_employee = self.env['kw_resignation'].sudo().search([('applicant_id','=',rec.employee_id.id),('state','not in',['apply','reject','cancel','waiting_for_rl_cancellation'])],order='id desc',limit=1)
    #         last_date = resignation_employee.last_working_date
    #         if resignation_employee:
    #             to_date = last_date
    #         else:
    #             to_date = rec.date_range.date_stop
    #         modified_to_date = to_date.strftime('%d-%b-%Y')
    #         return modified_to_date
        
    @api.constrains('temp_interest_payment')
    def check_house_loan_interest(self):
        for rec in self:
            if rec.temp_interest_payment > 200000:
                raise ValidationError("Interest on house loan can not be more than 2LK.")

    @api.onchange('tax_regime')
    def onchange_tax_regime(self):
        if self.tax_regime == 'old_regime':
            prvs_tds = self.env['hr.declaration'].sudo().search([('employee_id','=',self.employee_id.id),('tax_regime','=','old_regime'),('state','=','approved')])
            if prvs_tds:
                previous_tds = prvs_tds.filtered(lambda x:(self.date_range.date_start - x.date_range.date_stop).days == 1)
                if previous_tds:
                    self.house_rent_paid = previous_tds.actual_house_rent_paid
                    self.gross_annual_value = previous_tds.actual_gross_annual_value
                    self.municipal_taxes = previous_tds.actual_municipal_taxes
                    self.temp_interest_payment = previous_tds.actual_interest_payment
                    self.interest_received_from_bank = previous_tds.actual_interest_received
                    self.income_from_other_sources = previous_tds.actual_income_from_other_sources
                    for slab in self.slab_ids:
                        for rec in previous_tds.slab_ids:
                            slab.investment +=rec.filtered(lambda x:slab.saving_master.id == x.saving_master.id).actual_amt
                            
                    for ccd in self.slab_ccd_ids:
                        for rec in previous_tds.slab_ccd_ids:
                            ccd.investment += rec.filtered(lambda x:ccd.saving_master.code == x.saving_master.code).actual_amt
                    for d in self.slab_80d_ids:
                        for rec in previous_tds.slab_80d_ids:
                            d.investment += (rec.filtered(lambda x:d.saving_master.code == x.saving_master.code).actual_amt)
                    for dd in self.slab_80dd_ids:
                        for rec in previous_tds.slab_80dd_ids:
                            dd.handicapped_percent += (rec.filtered(lambda x:dd.saving_master.code == x.saving_master.code).handicapped_percent)
                    for e in self.slab_80e_ids:
                        for rec in previous_tds.slab_80e_ids:
                            e.investment += (rec.filtered(lambda x:e.saving_master.code == x.saving_master.code).actual_amt)
                    for g in self.slab_80g_ids:
                        for rec in previous_tds.slab_80g_ids:
                            g.investment += (rec.filtered(lambda x:g.saving_master.code == x.saving_master.code).actual_amt)
                    for ddb in self.slab_80ddb_ids:
                        for rec in previous_tds.slab_80ddb_ids:
                            ddb.investment += (rec.filtered(lambda x:ddb.saving_master.code == x.saving_master.code).actual_amt)
        elif self.tax_regime == 'new_regime':
            self.actual_excess_10_percent = 0
            self.actual_hra= 0
            self.pan_landlord = False
            self.pan_of_landlord = False
            self.house_rent_paid = False
            self.actual_house_rent_paid = False
            self.gross_annual_value =False
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
            self.allowed_rebate_under_80u = False
            self.allowed_rebate_under_80e = False
            self.allowed_rebate_under_80g = False
            self.final_amount_bank_interest= 0
            self.final_amount_other_income= 0
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
                if re.match("[A-Z]{5}[0-9]{4}[A-Z]{1}", str(record.pan_of_landlord)) == None:  # modified to allow + and space 24 april
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
            saving_80u = self.env['saving.master'].sudo().search([('it_rule.code', '=', '80u')])
            for u in saving_80u:
                rec.slab_80u_limit += u.rebate
            saving_80ccd2 = self.env['saving.master'].sudo().search([('it_rule.code', '=', '80ccd2')])
            for ccd2 in saving_80ccd2:
                rec.slab_80ccd2_limit += ccd2.rebate
            

    @api.onchange('gross_annual_value','actual_gross_annual_value')
    def validate_gross_annual_value(self):
        for rec in self:
            if rec.gross_annual_value <= 0:
                rec.municipal_taxes = 0
            if rec.actual_gross_annual_value <= 0:
                rec.actual_municipal_taxes = 0
                
    @api.onchange('previous_employer_income','actual_previous_employer_income')
    def onchange_income(self):
        for rec in self:
            if rec.previous_employer_income == 0:
                rec.tds_previous_employer = 0
                rec.tds_doc = 0
            if rec.actual_previous_employer_income == 0:
                rec.actual_tds_previous_employer = 0
                

    @api.constrains('slab_80dd_ids', 'slab_ids', 'slab_80d_ids', 'slab_80g_ids', 'slab_80e_ids', 'slab_ccd_ids','slab_80ddb_ids','slab_80u_ids')
    def validate_document(self):
        for rec in self.slab_80dd_ids:
            if rec.actual_handicapped_percent > 40 and rec.document == False:
                raise ValidationError(f"Kindly Upload the Document for {rec.saving_master.saving_type} under 80DD.")
            if rec.actual_handicapped_percent > 100 or rec.actual_handicapped_percent < 0 or rec.handicapped_percent > 100 or rec.handicapped_percent < 0:
                raise ValidationError("Disability Percentage Should be in Between 1-100.")
        for rec in self.slab_80u_ids:
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
        for rec in self.slab_80u_ids:
            if rec.actual_amt > 0 and rec.document == False:
                raise ValidationError(f"Kindly Upload the Document for {rec.saving_master.saving_type} under 80U.")


    @api.constrains('previous_employer_income', 'tds_previous_employer','actual_previous_employer_income','actual_tds_previous_employer')
    def check_tds_amount(self):
        for rec in self:
            if rec.tds_previous_employer and rec.previous_employer_income:
                if rec.tds_previous_employer >= rec.previous_employer_income:
                    raise ValidationError("Declared TDS amount should be less than declared previous employer income.")
            if rec.actual_tds_previous_employer and rec.actual_previous_employer_income:
                if rec.actual_tds_previous_employer >= rec.actual_previous_employer_income:
                    raise ValidationError("Actual TDS amount should be less than actual previous employer income.")

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
            if actual_start_month != False and actual_start_day != False and  actual_end_month != False and actual_end_day != False:
                actual_start_date = date(rec.date_range.date_stop.year,int(actual_start_month),int(actual_start_day))
                actual_end_date = date(rec.date_range.date_stop.year,int(actual_end_month),int(actual_end_day))
                rec.check_month = True if  actual_start_date <= datetime.today().date()  <= actual_end_date else False
                rec.invisible = True if datetime.today().date() >= actual_start_date else False

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
        between_days = ir_config_params.get_param('tds.between_days') or False
        fy_last_day = ir_config_params.get_param('tds.last_day') or False
        if start_date != False and end_date != False:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            start = datetime.strptime(start_date, "%Y-%m-%d")
            if start < datetime.now() < end: 
                current_fiscal = self.env['account.fiscalyear'].sudo().search([('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
                last_fy = self.env['account.fiscalyear'].sudo().search([('date_start', '<', datetime.today().date()), ('date_stop', '<', datetime.today().date())],order='date_stop desc',limit=1).name
                declaration = self.env['hr.declaration'].sudo().search([('date_range', '=',current_fiscal.id),('state','!=','approved')])
                for rec in declaration:
                    # slab_80c = rec.slab_ids.filtered(lambda x:x.investment > 0 and x.document != False)
                    # slab_80dd_ids =  rec.slab_80dd_ids.filtered(lambda x:x.investment > 0 and x.document != False)
                    # slab_80d_ids = rec.slab_80d_ids.filtered(lambda x:x.investment > 0 and x.document != False)
                    # slab_80g_ids = rec.slab_80g_ids.filtered(lambda x:x.investment > 0 and x.document != False)
                    # slab_80e_ids = rec.slab_80e_ids.filtered(lambda x:x.investment > 0 and x.document != False)
                    # slab_ccd_ids = rec.slab_ccd_ids.filtered(lambda x:x.investment > 0 and x.document != False)
                    # slab_80ddb_limit = rec.slab_80ddb_limit.filtered(lambda x:x.investment > 0 and x.document != False)
                    # if slab_80c or  slab_80dd_ids or  slab_80d_ids or  slab_80g_ids or  slab_80e_ids or  slab_ccd_ids  or  slab_80ddb_limit or (rec.actual_house_rent_paid > 0 and rec.pan_landlord != False) or  (rec.house_loan_doc!= False and rec.temp_interest_payment > 0):
                    #     pass
                    # else:
                    inform_template = self.env.ref('tds.actual_doc_verification_template')
                    inform_template.with_context(end_date = end.strftime("%d-%b-%Y"),current_fiscal=current_fiscal.name,last_fy = last_fy,between_days=between_days,fy_last_day=fy_last_day).send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")




    @api.model
    def create(self, vals):
        fy_month = self.env['ir.config_parameter'].sudo().get_param('tds.month')
        fy_day = self.env['ir.config_parameter'].sudo().get_param('tds.day')
        current_date=date.today()
        if fy_day and fy_month:
                fy_date = date(date.today().year,int(fy_month),int(fy_day))
                if fy_date and fy_date >= current_date:
                    raise ValidationError(f"IT Declaration can be filled after {fy_date.strftime('%d-%b-%Y')}.")
        new_record = super(HrDeclaration, self).create(vals)
        new_record.button_compute_tax()
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
            'context':{'edit':1,'create':0,'delete':0},
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
            'context':{'hide_button':1}
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
            for record in rec.employee_id.identification_ids:
                if record.name == '1':
                    rec.pan_number = record.doc_number
            contract = self.env['hr.contract'].sudo().search([('state','=','open'),('employee_id','=',rec.employee_id.id)])
            if contract:
                rec.bank_account = contract.bank_account if contract.bank_account else contract.personal_bank_account
                rec.bank_name = contract.bank_id.name if contract.bank_id else contract.personal_bank_name
                rec.pran = contract.pran_no if contract.pran_no else ''
            if rec.employee_id.last_working_day:
                rec.last_working_day = rec.employee_id.last_working_day.strftime('%d-%b-%Y')
            else:
                rec.last_working_day ='NA'

    @api.model
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


    @api.multi
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

    @api.multi
    def button_reset_to_draft(self):
        ir_config_params = self.env['ir.config_parameter'].sudo()
        actual_end_month = ir_config_params.get_param('tds.end_month') or False
        actual_end_day = ir_config_params.get_param('tds.end_day') or False
        if actual_end_month != False and actual_end_day != False:
            for record in self:
                actual_end_date = date(record.date_range.date_stop.year,int(actual_end_month),int(actual_end_day))
                if record.state == 'approved' and  actual_end_date >= datetime.today().date():
                    record.state='draft'
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    }
                else:
                    raise ValidationError("Cann't revert the approved TDS")
       

    def fillup_it_declaration(self):
        ir_config_params = self.env['ir.config_parameter'].sudo()
        company = ir_config_params.get_param('tds.tds_company_id') or False
        if company != False:
            contrct = self.env['hr.contract'].sudo().search([('state', '=', 'open'),('employee_id.active','=',True),('employee_id.enable_payroll','=','yes'),('company_id','=',int(company))])
            if contrct:
                for cnt in contrct:
                    # current_ctc = cnt.wage * 12
                    # if current_ctc >= 500000:
                    search_id = self.env['hr.declaration'].sudo().search(
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
                            extra_params = {'email':email,'name':name,'date':formatted_end_date,'fy':fy}
                            self.env['hr.contract'].contact_send_custom_mail(res_id=cnt.id,
                                                                                            notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                            template_layout='tds.user_tds_fillup_mail_template',
                                                                                            ctx_params=extra_params,
                                                                                            description="IT Declaration Reminder")




    def calculate_80d(self):
        for rec in self:
            return rec.prl_hlth_dependant + rec.health_insurance_parent
        
    def hr_declaration_cron(self):
        search_id = self.env['hr.declaration'].sudo().search([('state', 'not in', ['approved'])])
        declarations = search_id.filtered(lambda x:x.date_range.date_start <=datetime.today().date()<=x.date_range.date_stop)
        if declarations:
            for rec in declarations:
                rec.button_compute_tax()

    def create_ex_emp_tds(self):
        ir_config_params = self.env['ir.config_parameter'].sudo()
        company = ir_config_params.get_param('tds.tds_company_id') or False
        if company != False:
            current_fiscal = self.env['account.fiscalyear'].search(
                [('date_start', '<=', datetime.today().date()), ('date_stop', '<=', datetime.today().date())],order='date_stop desc',limit=1)
            employees = self.env['hr.employee'].sudo().search([('enable_payroll','=','yes'),('active','=',False),('company_id','=',int(company)),('last_working_day','>=',current_fiscal.date_start)])
            search_id = self.env['hr.declaration'].sudo().search([('date_range','=',current_fiscal.id)])
            active_emp =  self.env['hr.employee'].sudo().search([('date_of_joining','<=',current_fiscal.date_stop),('enable_payroll','=','yes'),('active','=',True),('company_id','=',int(company))])
            non_emp_list = []
            for emp in employees:
                declarations = search_id.filtered(lambda x:x.employee_id.id == emp.id)
                if not declarations:
                    non_emp_list.append(emp.id)
            for emps in active_emp:
                declarations = search_id.filtered(lambda x:x.employee_id.id == emps.id)
                if not declarations:
                    non_emp_list.append(emps.id)
            if len(non_emp_list) > 0:
                for employee in non_emp_list:
                    self.env.cr.execute(f"""insert into hr_declaration (employee_id,state,date_range,tax_regime) values({employee},'draft',{current_fiscal.id},'new_regime')""")

    def user_access_for_tds(self):
        ir_config_params = self.env['ir.config_parameter'].sudo()
        company = ir_config_params.get_param('tds.tds_company_id') or False
        if company != False:
            emp = f"select user_id from hr_employee where enable_payroll = 'yes' and company_id = {int(company)} and active = true"
            self._cr.execute(emp)
            employees = self._cr.dictfetchall()
            for ids in employees:
                user_id =ids['user_id'] if ids['user_id']!= None else False
                if user_id:
                    res_user = self.env['res.users'].sudo().browse(user_id)
                    if not res_user.has_group('tds.group_user_hr_declaration'):
                        gid = f"select id as user from res_groups where category_id = (select id from ir_module_category where name = 'IT Declaration') and name = 'User'"
                        self._cr.execute(gid)
                        group_dict = self._cr.dictfetchall()
                        group = group_dict[0]['user']
                        insert = f"INSERT INTO res_groups_users_rel (gid, uid) VALUES ({group},{user_id})"
                        self._cr.execute(insert)

    def create_default_tds(self):
        ir_config_params = self.env['ir.config_parameter'].sudo()
        company = ir_config_params.get_param('tds.tds_company_id') or False
        if company != False:
            employees = self.env['hr.employee'].sudo().search([('enable_payroll','=','yes'),('company_id','=',int(company))])
            search_id = self.env['hr.declaration'].sudo().search([])
            current_fiscal = self.env['account.fiscalyear'].search(
                [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
            non_emp_list = []
            for emp in employees:
                declarations = search_id.filtered(lambda x:x.date_range.date_start <=datetime.today().date()<=x.date_range.date_stop and x.employee_id.id == emp.id)
                if not declarations:
                    non_emp_list.append(emp.id)
            if len(non_emp_list) > 0:
                for employee in non_emp_list:
                    self.env.cr.execute(f"""insert into hr_declaration (employee_id,state,date_range,tax_regime) values({employee},'draft',{current_fiscal.id},'new_regime')""")

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
    document = fields.Binary(string='80 DD Document', attachment=True)
    file_name = fields.Char(string='Document Name')
    handicapped_percent = fields.Integer(string='Disability Percentage', )
    actual_handicapped_percent = fields.Integer(string='Actual Disability Percentage', )
    lock = fields.Boolean()

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


class SlabDeclarations_80u(models.Model):
    _name = 'declaration_slab_80u'
    _description = 'declaration.slab80u'
    _order = 'saving_master'

    def set_80u_rules(self):
        current_rule = self.env['hr.itrule'].search([('code', '=','80U')])
        return current_rule

    deduction_id = fields.Selection([
        ('slab_80u_declaration', 'A person with disability')], string='Deduction', default='slab_80u_declaration', track_visibility="always")

    slab_80u_id = fields.Many2one('hr.declaration', string='Slab', track_visibility="onchange")
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section',domain=[('code','=','80U')],default=set_80u_rules)
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Declaration Amount',digits=dp.get_precision('tds'))
    actual_amt = fields.Float(string='Actual Amount', digits=dp.get_precision('tds'))
    document = fields.Binary(string='80U Document', attachment=True)
    file_name = fields.Char(string='Document Name')
    lock = fields.Boolean()
    handicapped_percent = fields.Integer(string='Disability Percentage', )
    actual_handicapped_percent = fields.Integer(string='Actual Disability Percentage', )


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

    @api.onchange('handicapped_percent','actual_handicapped_percent')
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
    document = fields.Binary(string='80DDB Document', attachment=True)
    file_name = fields.Char(string='Document Name')
    lock = fields.Boolean()
    diseases = fields.Selection([
    ('neuro', 'Neurological Diseases'),
    ('cancer', 'Malignant Cancers'),
    ('aids', 'Full Blown Acquired Immune-Deficiency Syndrome (AIDS)'),
    ('renal', 'Chronic Renal failure'),
    ('blood', 'Haematological disorders')
], string='Diseases', track_visibility="always")

class SlabDeclarations_80ccd(models.Model):
    _name = 'declaration_slab_ccd'
    _description = 'declaration_slab_ccd'

    def set_80ccd_rules(self):
        current_rule = self.env['hr.itrule'].search([('code', '=','80ccd')])
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
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section',domain=[('code','=','80ccd')],default=set_80ccd_rules)
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Declaration Amount', digits=dp.get_precision('tds'))
    actual_amt = fields.Float(string='Actual Amount', digits=dp.get_precision('tds'))
    document = fields.Binary(string='80CCD Document', attachment=True)
    file_name = fields.Char(string='Document Name')
    lock = fields.Boolean()

class SlabDeclarations_80ccd2(models.Model):
    _name = 'declaration_slab_ccd2'
    _description = 'declaration_slab_ccd2'

    def set_80ccd_rules(self):
        current_rule = self.env['hr.itrule'].search([('code', '=','80ccd2')])
        return current_rule
    
    deduction_id = fields.Selection([('employer_nps','Contribution to pension scheme of Central Government by Employer')], string='Deduction', default='govn_nps')

    slab_ccd2_id = fields.Many2one('hr.declaration', string='Slab')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section',domain=[('code','=','80ccd2')],default=set_80ccd_rules)
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Declaration Amount', digits=dp.get_precision('tds'))
    actual_amt = fields.Float(string='Actual Amount', digits=dp.get_precision('tds'))
    document = fields.Binary(string='80CCD Document', attachment=True)
    file_name = fields.Char(string='Document Name')
    lock = fields.Boolean()


class SlabDeclarations_80e(models.Model):
    _name = 'declaration_slab_80e'
    _description = 'declaration_slab_80e'

    def set_80e_rules(self):
        current_rule = self.env['hr.itrule'].search([('code', '=','80e')])
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
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section',domain=[('code','=','80e')],default=set_80e_rules)
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Declaration Amount', digits=dp.get_precision('tds'))
    actual_amt = fields.Float(string='Actual Amount', digits=dp.get_precision('tds'))
    document = fields.Binary(string='80E Document', attachment=True)
    file_name = fields.Char(string='Document Name')
    lock = fields.Boolean()



class SlabDeclarations(models.Model):
    _name = 'declaration.slab'
    _description = 'declaration.slab'

    def set_80_c_rules(self):
        current_rule = self.env['hr.itrule'].search([('code', '=','80_c')])
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
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section',domain=[('code','=','80_c')],default=set_80_c_rules)
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Declaration Amount', digits=dp.get_precision('tds'))
    actual_amt = fields.Float(string='Actual Amount', digits=dp.get_precision('tds'))
    # ai_amt = fields.Float(string='AI Amount', digits=dp.get_precision('tds'))
    document = fields.Binary(string='80C Document', attachment=True)
    file_name = fields.Char(string='Document Name')
    lock = fields.Boolean()

    def unlink(self):
        return super(SlabDeclarations, self).unlink()
    
    # def create(self, vals):
    #     recs = super(SlabDeclarations, self).create(vals)
    #     for rec in recs:
    #         if rec.actual_amt != 0 and rec.file_name:
    #                 self.env['ai_slab_log'].create({
    #                     'slab_rec_id': rec.id,
    #                     'model_name':'declaration_slab_80C',
    #                     'document': rec.document
    #                 })
    #     return True
    
    
    # def write(self,vals):
    #     if 'actual_amt' in vals and 'file_name' in vals:
    #         if vals['actual_amt'] != 0 and vals['file_name']:
    #             self.env['ai_slab_log'].create({
    #                 'slab_rec_id': self.id,
    #                 'model_name':'declaration_slab_80C',
    #                 'document': vals['document']
    #             })
    #     elif 'actual_amt' in vals:
    #         if vals['actual_amt'] != 0:
    #             self.env['ai_slab_log'].create({
    #                 'slab_rec_id': self.id,
    #                 'model_name':'declaration_slab_80C',
    #                 'document': self.document
    #             })
    #     return super(SlabDeclarations, self).write(vals)
    
# import base64

# class AiSlabLog(models.Model):
#     _name = 'ai_slab_log'
    
#     slab_rec_id = fields.Integer(string='Slab ID')
#     model_name = fields.Char(string='Model Name')
#     payload = fields.Text(string='Payload')
#     status = fields.Char(string='Status')
#     response = fields.Text(string='Response')
#     document = fields.Binary()
#     task_id = fields.Integer(string='Task ID')
    
#     def _prepare_payload(self, file, file_type, financial_year):
#         encoded_file = base64.b64encode(file).decode('utf-8')
#         return {
#             'file': (None, encoded_file),
#             'file_type': (None, file_type),
#             'financial_year': (None, financial_year)
#         }
    
#     def _send_request_to_ai(self, payload):
#         ai_url = 'http://192.168.10.208:8007/upload'
#         try:
#             ai_request = requests.post(ai_url, files=payload)
#             ai_request.raise_for_status()  # Raise an exception for HTTP errors
#             ai_data = ai_request.json()
#             return ai_data, 200, payload
#         except requests.RequestException as e:
#             return {'error': str(e)}, ai_request.status_code if ai_request else 500, payload
    
#     def _process_response(self, ai_response, slab_details):
#         status_code = ai_response[1]
#         response_data = ai_response[0]
#         payload = ai_response[2]
        
#         if status_code == 200:
#             self.write({'task_id':response_data,'status': status_code, 'payload':payload})
#         else:
#             self.write({'status': status_code, 'payload':payload})
    
#     def process_ai_record(self, active_record_id):
#         current_rec_id = active_record_id if isinstance(active_record_id, int) else self.id
#         current_rec = self.env['ai_slab_log'].browse(current_rec_id)
#         if self.model_name == 'declaration_slab_80C':
#             slab_details = self.env['declaration.slab'].browse(current_rec.slab_rec_id)
#             if current_rec.document:
#                 file = base64.b64decode(current_rec.document)
#                 file_type = slab_details.saving_master.code
#                 financial_year = slab_details.slab_id.date_range.name
#                 payload = self._prepare_payload(file, file_type, financial_year)
#                 ai_response = self._send_request_to_ai(payload)
#                 self._process_response(ai_response, slab_details)

                


class SlabDeclarations_80g(models.Model):
    _name = 'declaration_slab_80g'
    _description = 'declaration.slab80g'

    def set_80G_rules(self):
        current_rule = self.env['hr.itrule'].search([('code', '=','80G')])
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
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section',domain=[('code','=','80G')],default=set_80G_rules)
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Declared Amount', digits=dp.get_precision('tds'))
    actual_amt = fields.Float(string='Actual Amount', digits=dp.get_precision('tds'))
    document = fields.Binary(string='80G Document', attachment=True)
    file_name = fields.Char(string='Document Name')
    lock = fields.Boolean()

class SlabDeclarations80_d(models.Model):
    _name = 'slab_declaration_80d'
    _description = 'slab 80 declaration'

    def set_80d_rules(self):
        current_rule = self.env['hr.itrule'].search([('code', '=','80d')])
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
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section',domain=[('code','=','80d')],default=set_80d_rules)
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Declaration Amount', digits=dp.get_precision('tds'))
    actual_amt = fields.Float(string='Actual Amount', digits=dp.get_precision('tds'))
    document = fields.Binary(string='80D Document', attachment=True)
    file_name = fields.Char(string='Document Name')
    lock = fields.Boolean()

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
    document = fields.Binary(string='Housing Loan Documents', attachment=True)
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
    active = fields.Boolean('Active')

    @api.multi
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



class EmployeeIncometax(models.Model):
    _name = 'tds_emp_integration'
    _description = "TDS Employees"
    
    def get_tds_data(self):
        fy_code = self.env['ir.config_parameter'].sudo().get_param('tds.financial_year')
        tds_details_ids = self.env.context.get('selected_active_ids')
        res = self.env['hr.declaration'].sudo().search([('id','in',tds_details_ids),('date_range.code','=',fy_code)])
        return res
    
    def get_tds_draft_data(self):
        fy_code = self.env['ir.config_parameter'].sudo().get_param('tds.financial_year')
        tds_details_ids = self.env.context.get('draft_ids')
        res = self.env['hr.declaration'].sudo().search([('id','in',tds_details_ids),('state','=','draft'),('date_range.code','=',fy_code)])
        return res
    
    tds_ids = fields.Many2many('hr.declaration','kw_employee_tds_rel','tds_id','emp_id',string='Employees',default=get_tds_data)
    draft_tds_ids = fields.Many2many('hr.declaration','tds_approved_tax_rel','record_id','tds_id',string='TDS',default=get_tds_draft_data)
    
    def button_compute_income_tax(self):
        if self.tds_ids:
            for rec in self.tds_ids:
                rec.button_compute_tax()
            self.env.user.notify_success(message='Tax computed successfully!.')

    def button_approve_income_tax(self):
        if self.draft_tds_ids:
            for rec in self.draft_tds_ids:
                rec.button_approved()
            self.env.user.notify_success(message='Tax Approved successfully!.')


class DownloadForm16(models.TransientModel):
    _name = 'download_form16_transient_model'
    _description = 'Form 16 Details'

    pdf_file = fields.Binary(string='PDF File')
    file_name = fields.Char(string="File Name")

