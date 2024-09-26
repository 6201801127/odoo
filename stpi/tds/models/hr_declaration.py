from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
from calendar import monthrange

class HrDeclaration(models.Model):
    _name = 'hr.declaration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'IT Declaration'


    def _default_employee(self):
        return self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)


    @api.multi
    @api.depends('slab_ids','med_ins_ids','deduction_saving_ids','tax_home_ids','tax_education_ids','rgess_ids','dedmedical_ids','dedmedical_self_ids','deddonation_ids')
    def _compute_allowed_rebate(self):
        for rec in self:

            total_80c_80ccd1_investment = sum(rec.slab_ids.filtered(
                                                lambda x: x.it_rule.code.lower() in ['80_c', '80ccd1']).mapped('investment'))
            total_80c_80ccd1_rebate = sum(rec.slab_ids.filtered(
                                                lambda x: x.it_rule.code.lower() in ['80_c', '80ccd1']).mapped('saving_master.rebate'))
            total_80ccd1b_investment = sum(rec.slab_ids.filtered(
                                                lambda x: x.it_rule.code.lower() == '80ccd1b').mapped('investment'))
            total_80ccd1b_rebate = sum(rec.slab_ids.filtered(
                                                lambda x: x.it_rule.code.lower() == '80ccd1b').mapped('saving_master.rebate'))


            rec.allowed_rebate_under_80c = round(total_80c_80ccd1_investment) \
                                            if total_80c_80ccd1_investment < total_80c_80ccd1_rebate \
                                            else round(total_80c_80ccd1_rebate)
            rec.allowed_rebate_under_80b = round(total_80ccd1b_investment) \
                                            if total_80ccd1b_investment < total_80ccd1b_rebate \
                                            else round(total_80ccd1b_rebate)

            eligible_med_ins_amount = 0
            for med_ins_id in rec.med_ins_ids:
                if med_ins_id.saving_master.is_percent_req:
                    percent_val = (med_ins_id.investment) * (med_ins_id.saving_master.percent/100)
                    if med_ins_id.saving_master.with_max_limit:
                        eligible_med_ins_amount += med_ins_id.saving_master.rebate \
                                             if percent_val > med_ins_id.saving_master.rebate else percent_val
                    else:
                        eligible_med_ins_amount = percent_val
                else:
                    eligible_med_ins_amount += med_ins_id.saving_master.rebate \
                                        if med_ins_id.investment > med_ins_id.saving_master.rebate \
                                        else med_ins_id.investment

            rec.allowed_rebate_under_80d = round(eligible_med_ins_amount)

            eligible_deduction_saving_amount = 0
            for deduction_saving_id in rec.deduction_saving_ids:
                if deduction_saving_id.saving_master.is_percent_req:
                    percent_val = (deduction_saving_id.investment) * (deduction_saving_id.saving_master.percent/100)
                    if deduction_saving_id.saving_master.with_max_limit:
                        eligible_deduction_saving_amount += deduction_saving_id.saving_master.rebate \
                                             if percent_val > deduction_saving_id.saving_master.rebate else percent_val
                    else:
                        eligible_deduction_saving_amount = percent_val
                else:
                    eligible_deduction_saving_amount += deduction_saving_id.saving_master.rebate \
                                        if deduction_saving_id.investment > deduction_saving_id.saving_master.rebate \
                                        else deduction_saving_id.investment
            
            rec.allowed_rebate_under_80dsa = round(eligible_deduction_saving_amount)

            eligible_80ee_amount = 0
            eligible_24_amount = 0
            eligible_tbhl_amount = 0
            total_80ee_investment = sum(rec.tax_home_ids.filtered(lambda x: x.it_rule.code.lower() == '80ee').mapped('investment'))
            total_24_investment = sum(rec.tax_home_ids.filtered(lambda x: x.it_rule.code.lower() == '24').mapped('investment'))
            total_tbhl_investment = sum(rec.tax_home_ids.filtered(lambda x: x.it_rule.code.lower() == '80eea').mapped('investment'))

            for tax_home_id in rec.tax_home_ids:
                if tax_home_id.it_rule.code.lower() == '80ee':
                    if tax_home_id.saving_master.is_percent_req:
                        percent_val = total_80ee_investment * (tax_home_id.saving_master.percent/100)
                        if tax_home_id.saving_master.with_max_limit:
                            eligible_80ee_amount += tax_home_id.saving_master.rebate \
                                                 if percent_val > tax_home_id.saving_master.rebate else percent_val
                        else:
                            eligible_80ee_amount = percent_val
                    else:
                        eligible_80ee_amount += tax_home_id.saving_master.rebate \
                                        if total_80ee_investment > tax_home_id.saving_master.rebate \
                                        else total_80ee_investment
                elif tax_home_id.it_rule.code.lower() == '80eea':
                    if tax_home_id.saving_master.is_percent_req:
                        percent_val = total_tbhl_investment * (tax_home_id.saving_master.percent/100)
                        if tax_home_id.saving_master.with_max_limit:
                            eligible_tbhl_amount += tax_home_id.saving_master.rebate \
                                                 if percent_val > tax_home_id.saving_master.rebate else percent_val
                        else:
                            eligible_tbhl_amount = percent_val
                    else:
                        eligible_tbhl_amount += tax_home_id.saving_master.rebate \
                                        if total_tbhl_investment > tax_home_id.saving_master.rebate \
                                        else total_tbhl_investment
                else:
                    if tax_home_id.saving_master.is_percent_req:
                        percent_val = total_24_investment * (tax_home_id.saving_master.percent/100)
                        if tax_home_id.saving_master.with_max_limit:
                            eligible_24_amount += tax_home_id.saving_master.rebate \
                                                 if percent_val > tax_home_id.saving_master.rebate else percent_val
                        else:
                            eligible_24_amount = percent_val
                    else:
                        eligible_24_amount += tax_home_id.saving_master.rebate \
                                        if total_24_investment > tax_home_id.saving_master.rebate \
                                        else total_24_investment

            rec.allowed_rebate_under_80ee = round(eligible_80ee_amount)
            rec.allowed_rebate_under_tbhl = round(eligible_tbhl_amount)
            rec.allowed_rebate_under_24 = round(eligible_24_amount)

            eligible_80e_amount = 0
            for tax_education_id in rec.tax_education_ids:
                if tax_education_id.saving_master.is_percent_req:
                    percent_val = (tax_education_id.investment) * (tax_education_id.saving_master.percent/100)
                    if tax_education_id.saving_master.with_max_limit:
                        eligible_80e_amount += tax_education_id.saving_master.rebate \
                                             if percent_val > tax_education_id.saving_master.rebate else percent_val
                    else:
                        eligible_80e_amount = percent_val
                else:
                    eligible_80e_amount += tax_education_id.saving_master.rebate \
                                        if tax_education_id.investment > tax_education_id.saving_master.rebate \
                                        else tax_education_id.investment

            rec.allowed_rebate_under_80e = round(eligible_80e_amount)
            
            eligible_80ccg_amount = 0
            for rgess_id in rec.rgess_ids:
                if rgess_id.saving_master.is_percent_req:
                    percent_val = (rgess_id.investment) * (rgess_id.saving_master.percent/100)
                    if rgess_id.saving_master.with_max_limit:
                        eligible_80ccg_amount += rgess_id.saving_master.rebate \
                                             if percent_val > rgess_id.saving_master.rebate else percent_val
                    else:
                        eligible_80ccg_amount = percent_val
                else:
                    eligible_80ccg_amount += rgess_id.saving_master.rebate \
                                        if rgess_id.investment > rgess_id.saving_master.rebate \
                                        else rgess_id.investment

            rec.allowed_rebate_under_80ccg = round(eligible_80ccg_amount)

            eligible_80cdd_amount = 0
            for dedmedical_id in rec.dedmedical_ids:
                if dedmedical_id.saving_master.is_percent_req:
                    percent_val = (dedmedical_id.investment) * (dedmedical_id.saving_master.percent/100)
                    if dedmedical_id.saving_master.with_max_limit:
                        eligible_80cdd_amount += dedmedical_id.saving_master.rebate \
                                             if percent_val > dedmedical_id.saving_master.rebate else percent_val
                    else:
                        eligible_80cdd_amount = percent_val
                else:
                    eligible_80cdd_amount += dedmedical_id.saving_master.rebate \
                                        if dedmedical_id.investment > dedmedical_id.saving_master.rebate \
                                        else dedmedical_id.investment

            rec.allowed_rebate_under_80cdd = round(eligible_80cdd_amount)
            
            eligible_80mesdr_amount = 0
            for dedmedical_self_id in rec.dedmedical_self_ids:
                if dedmedical_self_id.saving_master.is_percent_req:
                    percent_val = (dedmedical_self_id.investment) * (dedmedical_self_id.saving_master.percent/100)
                    if dedmedical_self_id.saving_master.with_max_limit:
                        eligible_80mesdr_amount += dedmedical_self_id.saving_master.rebate \
                                             if percent_val > dedmedical_self_id.saving_master.rebate else percent_val
                    else:
                        eligible_80mesdr_amount = percent_val
                else:
                    eligible_80mesdr_amount += dedmedical_self_id.saving_master.rebate \
                                        if dedmedical_self_id.investment > dedmedical_self_id.saving_master.rebate \
                                        else dedmedical_self_id.investment
                
            rec.allowed_rebate_under_80mesdr = round(eligible_80mesdr_amount)

            eligible_donation_amount = 0
            for deddonation_id in rec.deddonation_ids:
                if deddonation_id.saving_master.is_percent_req:
                    percent_val = (deddonation_id.investment) * (deddonation_id.saving_master.percent/100)
                    if deddonation_id.saving_master.with_max_limit:
                        eligible_donation_amount += deddonation_id.saving_master.rebate if percent_val > deddonation_id.saving_master.rebate \
                                                    else percent_val
                    else:
                        eligible_donation_amount = percent_val
                else:
                    eligible_donation_amount += deddonation_id.saving_master.rebate \
                                        if deddonation_id.investment > deddonation_id.saving_master.rebate else deddonation_id.investment

            rec.allowed_rebate_under_donation = round(eligible_donation_amount)


            rec.total_deductions =  rec.allowed_rebate_under_80c + rec.allowed_rebate_under_80b + rec.allowed_rebate_under_80d + \
                                    rec.allowed_rebate_under_80dsa + rec.allowed_rebate_under_80ee + rec.allowed_rebate_under_24 + \
                                    rec.allowed_rebate_under_tbhl + rec.allowed_rebate_under_80e+ rec.allowed_rebate_under_80ccg + \
                                    rec.allowed_rebate_under_80cdd + rec.allowed_rebate_under_80mesdr + rec.allowed_rebate_under_donation


    # @api.multi
    # @api.depends('rent_paid_ids')
    # def compute_rent_lines(self):
    #     for rec in self:
    #         sum = 0
    #         for lines in rec.rent_paid_ids:
    #             if lines.date_to <= datetime.now().date():
    #                 sum += lines.amount
    #         rec.rent_paid = round(sum)
    #         if rec.rent_paid > 100000.00:
    #             rec.rent_paid_attach_files = True
    #         else:
    #             rec.rent_paid_attach_files = False

    @api.multi
    @api.depends('tax_payment_ids','tax_payable_after_rebate')
    def compute_tax_paid_pending(self):
        total_paid = 0.0
        for rec in self:
            for lines in rec.tax_payment_ids:
                if lines.paid:
                    total_paid += lines.amount
            rec.tax_paid = round(total_paid)
            rec.pending_tax = round(rec.tax_payable_after_rebate - rec.tax_paid)
    
    @api.depends('tax_payment_ids.paid', 'total_tds_paid')
    def calculate_tds_paid(self):
        for rec in self:
            rec.tds_paid_current = sum(rec.tax_payment_ids.filtered(lambda x: x.paid).mapped('amount'))
            rec.tds_total_paid = rec.tds_paid_current + rec.total_tds_paid

    def get_current_financial_year(self):
        curr_date = date.today()
        dateRangeObj = self.env['date.range'].sudo().search([('type_id.name', '=', 'Fiscal Year'),
                                                                ('date_start', '<=', curr_date),
                                                                ('date_end', '>=', curr_date)])
        return [('id', 'in', dateRangeObj.mapped('id'))]

    # @api.multi
    # @api.depends('employee_id','date_range')
    # def _compute_bda_salary(self):
    #     for rec in self:
    #         bs = 0.00
    #         da = 0.00
    #         dstart = rec.date_range.date_start
    #         dend = rec.date_range.date_end
    #         prl_id = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),
    #                                                            ('slip_id.state', '=', 'done'),
    #                                                            ('slip_id.date_from', '>=', dstart),
    #                                                            ('slip_id.date_to', '<=', dend),
    #                                                            # ('slip_id.date_to', '<=', datetime.now().date())
    #                                                             ],order ="date_to desc")
    #         for pr in prl_id:
    #             if pr.code == 'BASIC':
    #                 bs += pr.amount
    #             elif pr.code == 'DA':
    #                 da += pr.amount
    #         rec.basic_salary = round(bs)
    #         rec.da_salary = round(da)




    employee_id = fields.Many2one('hr.employee', string='Requested By', default=_default_employee, track_visibility='always')
    job_id = fields.Many2one('hr.job', string="Functional Designation", store=True, track_visibility='always')
    branch_id = fields.Many2one('res.branch', string='Center', store=True, track_visibility='always')
    department_id = fields.Many2one('hr.department', string="Department", store=True, track_visibility='always')
    address_employee = fields.Text('Address Employee')
    date_range = fields.Many2one('date.range','Financial Year', domain=get_current_financial_year,
                                    track_visibility='always')
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True, track_visibility='always')
    rent_paid_ids = fields.One2many('rent.paid', 'rent_paid_id')
    rent_paid = fields.Float()
    # birthday = fields.Date('Birthday')
    rent_paid_attach_files = fields.Boolean(string='Attach Files?')
    pan_card = fields.Binary(string = 'Attach Pan Card')
    document_pan = fields.Char()
    owner_address = fields.Char(string='Address of the owner')

    tax_salary_final = fields.Float(string='Yearly Gross', store=True, track_visibility='always')
    forecast_gross = fields.Float(string='Forecast Gross')
    basic_salary = fields.Float(string='Basic Salary')
    da_salary = fields.Float(string='DA')
    total_tds_paid = fields.Float(string='Total TDS from Previous Employer')
    tds_paid_current = fields.Float('Total TDS Paid from Current Employer', compute="calculate_tds_paid")
    tds_total_paid = fields.Float('Total TDS Paid', compute="calculate_tds_paid")
    previous_employer_income = fields.Float(string='Previous Employer Income')
    income_after_exemption = fields.Float(string='Income after Exemption')
    income_after_std_ded = fields.Float(string='Income after Std. Deduction')
    income_after_pro_tax = fields.Float(string='Income after Professional Tax')
    income_after_dednew = fields.Float(string='Income after Deduction')
    taxable_income = fields.Float(string='Taxable Income')

    exemption_ids = fields.One2many('declaration.exemption', 'exemption_id', string='Exemption Ids')
    std_ded_ids = fields.One2many('declaration.standard', 'std_ded_id', string='Standard Deduction')
    rebate_ids = fields.One2many('declaration.rebate', 'rebate_id', string='Rebate Ids')
    slab_ids = fields.One2many('declaration.slab', 'slab_id', string='Slab 80 Ids')
    hra_ids = fields.One2many('declaration.hra', 'hra_id', string='HRA - House Rent Allowances ')
    med_ins_ids = fields.One2many('declaration.medical', 'med_ins_id', string='Medical Insurance Premium paid ')
    deduction_saving_ids = fields.One2many('declaration.deduction', 'deduction_saving_id', string='Deductions on Interest on Savings Account')
    tax_home_ids = fields.One2many('declaration.taxhome', 'tax_home_id', string='Tax Benefits on Home Loan')
    tax_education_ids = fields.One2many('declaration.taxeducation', 'tax_education_id', string='Tax benefit on Education Loan (80E)')
    rgess_ids = fields.One2many('declaration.rgess', 'rgess_id', string='Deductions on Rajiv Gandhi Equity Saving Scheme')
    dedmedical_ids = fields.One2many('declaration.dedmedical', 'dedmedical_id', string='Deductions on Medical Expenditure for a Handicapped Relative')
    dedmedical_self_ids = fields.One2many('declaration.dedmedicalself', 'dedmedical_self_id', string='Deductions on Medical Expenditure on Self or Dependent Relative')
    deddonation_ids = fields.One2many('declaration.donation', 'deddonation_id', string='Deductions on Donation')
    dednew_rule_ids = fields.One2many('declaration.80c.newded', 'dednew_rule_id')
    income_house_ids = fields.One2many('income.house','income_house_id','Income from House Property')
    income_other_ids = fields.One2many('income.other','income_other_id','Income from Other Sources')
    # net_allowed_rebate = fields.Float('Net Allowed Rebate', compute='compute_net_allowed_rebate')
    # income_after_rebate = fields.Float('Income after Rebate')
    income_after_house_property = fields.Float()
    income_after_other_sources = fields.Float()
    allowance_current = fields.Float('Allowance')
    el_encashment = fields.Float('EL Encashment(LTC and Reimbursement) and medical reimbursement')
    income_from_home= fields.Float(string='Income from Income from Rent')
    income_dividend= fields.Float(string='Dividend Income')
    income_interest= fields.Float(string='Interest Income')
    income_pension= fields.Float(string='Pension Income')
    income_other= fields.Float(string='Other Income')


    tax_payable = fields.Float('Tax Payable')


    tax_payable_after_rebate = fields.Float('Tax Payable after Rebate')

    rebate_received = fields.Float(string='Rebate Received')

    tax_payable_zero = fields.Boolean('Tax Payable greater than equal to zero')
    tax_computed_bool = fields.Boolean('Tax computed bool', default = False)
    tax_payment_ids = fields.One2many('tax.payment','tax_payment_id', string='Tax Payment')
    allowed_rebate_under_80c = fields.Float(string='Allowed Rebate under Section 80', compute='_compute_allowed_rebate')
    allowed_rebate_under_80b = fields.Float(string='Allowed Rebate under Section 80CCD1(B)', compute='_compute_allowed_rebate')
    allowed_rebate_under_80d = fields.Float(string='Allowed Rebate under Section 80D', compute='_compute_allowed_rebate')
    allowed_rebate_under_80dsa = fields.Float(string='Allowed Rebate under Interest on Savings Account', compute='_compute_allowed_rebate')
    allowed_rebate_under_tbhl = fields.Float(string='Allowed Rebate under Tax Benefits on Home Loan', compute='_compute_allowed_rebate')

    allowed_rebate_under_80ee = fields.Float(string='Allowed Rebate under Section 80 EE', compute='_compute_allowed_rebate')
    allowed_rebate_under_24 = fields.Float(string='Allowed Rebate under Section 24', compute='_compute_allowed_rebate')


    allowed_rebate_under_80e = fields.Float(string='Allowed Rebate under Section 80 E', compute='_compute_allowed_rebate')
    allowed_rebate_under_80ccg = fields.Float(string='Allowed Rebate under Section 80 CCG', compute='_compute_allowed_rebate')
    allowed_rebate_under_80cdd = fields.Float(string='Allowed Rebate under Section 80 DD', compute='_compute_allowed_rebate')
    allowed_rebate_under_80mesdr = fields.Float(string='Allowed Rebate under Medical Expenditure on Self or Dependent Relative', compute='_compute_allowed_rebate')
    allowed_rebate_under_donation = fields.Float(string='Allowed Rebate under Donations', compute='_compute_allowed_rebate')
    total_deductions = fields.Float(string='Total Deductions', compute='_compute_allowed_rebate')

    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)

    tax_paid = fields.Float(string='Tax Paid', compute='compute_tax_paid_pending', store=True)
    pending_tax = fields.Float(string='Pending Tax', compute='compute_tax_paid_pending', store=True)

    which_it = fields.Selection(
        [('old', 'Old Tax Regime'), ('new', 'New Tax Regime')
         ], default='old', string='IT', track_visibility='always')

    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('verified', 'Verified')
         ], required=True, default='draft', string='Status', track_visibility='always')

    basic_actual_forecast = fields.Float('Basic Actual Forecast', track_visibility='onchange')
    da_actual_forecast = fields.Float('DA Actual Forecast', track_visibility='onchange')
    ta_actual_forecast = fields.Float('TA', track_visibility='onchange')
    misc_salary = fields.Float('Misc', track_visibility='onchange')
    hra_actual_forecast = fields.Float('HRA', track_visibility='onchange')
    gross_actual_forecast = fields.Float('Gross', track_visibility='onchange')
    medical_salary = fields.Float('Medical', track_visibility='onchange')
    el_encash_salary = fields.Float('EL Encash', track_visibility='onchange')
    hostel_salary = fields.Float('Hostel', track_visibility='onchange')
    tuition_salary = fields.Float('Tuition', track_visibility='onchange')
    lunch_salary = fields.Float('Lunch', track_visibility='onchange')
    ltc_advance_salary = fields.Float('LTC Advance', track_visibility='onchange')
    house_income_salary = fields.Float('House Income', track_visibility='onchange')
    other_income_salary = fields.Float(track_visibility='onchange')
    total_gross_salary = fields.Float('Total Gross', track_visibility='onchange')

    @api.onchange('employee_id')
    @api.constrains('employee_id')
    def onchange_emo_get_basic(self):
        for record in self:
            my_add = ''
            record.job_id = record.employee_id.job_id
            record.branch_id = record.employee_id.branch_id
            record.department_id = record.employee_id.department_id
            for rec in record.employee_id.address_ids:
                if rec.address_type == 'permanent_add':
                    record.address_employee = str(rec.street) + ' ' + str(rec.street2) + ', ' + str(rec.city) + ', ' + str(
                        rec.state_id.name) + ', ' + str(rec.country_id.name) + ' - ' + str(rec.zip)
    #
    # @api.depends('exemption_ids','rebate_ids','allowed_rebate_under_80c','allowed_rebate_under_80b','allowed_rebate_under_80d','allowed_rebate_under_80dsa','allowed_rebate_under_80e','allowed_rebate_under_80ccg','allowed_rebate_under_tbhl','allowed_rebate_under_80ee','allowed_rebate_under_24','allowed_rebate_under_80cdd', 'allowed_rebate_under_80mesdr')
    # def compute_net_allowed_rebate(self):
    #     for rec in self:
    #         sum=0.00
    #         sum1 = 0.00
    #         for de in rec.exemption_ids:
    #             sum+=de.allowed_rebate
    #         for de in rec.rebate_ids:
    #             sum+=de.allowed_rebate
    #         sum1 = rec.allowed_rebate_under_80c + rec.allowed_rebate_under_80b + rec.allowed_rebate_under_80d + rec.allowed_rebate_under_80dsa + rec.allowed_rebate_under_80e + rec.allowed_rebate_under_80ccg + rec.allowed_rebate_under_tbhl + rec.allowed_rebate_under_80ee + rec.allowed_rebate_under_24 + rec.allowed_rebate_under_80cdd + rec.allowed_rebate_under_80mesdr
    #         rec.net_allowed_rebate = sum + sum1


    @api.onchange('date_range')
    # @api.constrains('date_range')
    def get_rent_lines_ids(self):
        for rec in self:
            rec.rent_paid_ids.unlink()
            rent_paid_ids = []
            sdate = rec.date_range.date_start
            edate = rec.date_range.date_end
            while sdate < edate:
                eadate = sdate + relativedelta(months=1) - relativedelta(days=1)
                rent_paid_ids.append((0, 0, {
                    'rent_paid_id': rec.id,
                    'date_from': sdate,
                    'date_to': eadate,
                    # 'amount': 0.00,
                }))
                sdate = sdate + relativedelta(months=1)
            rec.rent_paid_ids = rent_paid_ids


    @api.multi
    @api.depends('employee_id')
    def name_get(self):
        res = []
        name = ''
        for record in self:
            if record.employee_id:
                name = str(record.employee_id.name) + ' - HR Declaration'
            else:
                name = 'HR Declaration'
            res.append((record.id, name))
        return res


    @api.multi
    def button_to_approve(self):
        for rec in self:
            rec.write({'state': 'to_approve'})

    @api.multi
    def button_forecast_gross(self):
        for rec in self:
            sum = 0
            proll = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),
                                                        ('slip_id.state', '=', 'done'),
                                                       ('code', '=', 'NET'),
                                                        ('slip_id.date_to', '>', rec.date_range.date_start)
                                                    ],order ="date_to desc", limit=1)
            for pr in proll:
                rec.forecast_gross = round(pr.amount*12)
        return True



    @api.multi
    def button_calculate_el_encash(self):
        for rec in self:
            contract = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id),
                                                                    ('state', '=', 'open')], limit=1)
            january_basic_da = sum(contract.change_log_ids\
                                    .filtered(lambda r: r.date.strftime('%B') == 'January' and r.date.year == fields.Date.today().year)\
                                    .sorted(key = lambda r:r.date,reverse=True).mapped('basic_da'))

            calc_basic_da = (january_basic_da / 4) if january_basic_da else (contract.updated_basic / 4)
            reimbursement_ids =  self.env['reimbursement'].sudo().search([('employee_id', '=', rec.employee_id.id),
                                                                            ('date_range.date_start', '>=', rec.date_range.date_start),
                                                                            ('date_range.date_end', '<=', rec.date_range.date_end),
                                                                            ('state', '=', 'approved')])
            medical_reimbursement_ids = reimbursement_ids.filtered(lambda x: x.reimbursement_type_id.code == 'medical')
            encash = sum(reimbursement_ids.filtered(lambda x: x.reimbursement_type_id.code == 'el_encashment').mapped('approved_amount'))
            medical_actual = sum(medical_reimbursement_ids.mapped('approved_amount'))
            medical_forecast = calc_basic_da * (4 - len(medical_reimbursement_ids))
            ltc_ids =  self.env['employee.ltc.advance'].sudo().search([('employee_id', '=', rec.employee_id.id),
                                                                        ('depart_date', '>=', rec.date_range.date_start),
                                                                        ('arrival_date', '<=', rec.date_range.date_end),
                                                                        ('state', '=', 'approved')])
            ltc = sum(ltc_ids.mapped('amount'))
            medical_actual_forecast = sum((medical_actual, medical_forecast))
            rec.el_encashment = encash + ltc + medical_actual_forecast
            _body = (_(
                (
                    "<ul>Medical Reimbursement: {0} </ul>"
                    "<ul>EL Encashment - Reimbursement: {1} </ul>"
                    "<ul>EL Encashment - LTC: {2} </ul>"

                ).format(medical_actual_forecast,encash,ltc)))
            rec.message_post(body=_body)
        return True


    @api.multi
    def button_calculate_allowance(self):
        for rec in self:
            contract = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id),
                                                                ('state', '=', 'open')], limit=1)
            TA = self.env['hr.payslip'].sudo().calculate_ta(contract)
            DA = (contract.da/100) * contract.wage
            HRA = self.env['hr.payslip'].sudo().calculate_hra(contract)
            MISC = contract.supplementary_allowance
            rec.allowance_current = MISC + HRA + DA + TA
        return True


    @api.multi
    def button_approved(self):
        for rec in self:
            rec.write({'state': 'approved'})
        return True

    @api.multi
    def button_reject(self):
        for rec in self:
            rec.write({'state': 'rejected'})
        return True

    @api.multi
    def button_reset_to_draft(self):
        rc = {
            'name': 'Register actions',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('tds.view_reason_revert_tds_wizard').id,
            'res_model': 'revert.tds.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
            }
        }
        return rc
    
    @api.multi
    def calculate_breakup(self, month, contract, payslip_line_ids, actual_gross, lunch_total_amount,
                            actual_tuition_amount, actual_hostel_amount, reimbursement_ids):
        ltc_ids =  self.env['employee.ltc.advance'].sudo()\
                            .search([('employee_id', '=', self.employee_id.id),
                                    ('depart_date', '>=', self.date_range.date_start),
                                    ('arrival_date', '<=', self.date_range.date_end),
                                    ('state', '=', 'approved')])

        basic_actual, basic_forecast = self.basic_salary, (contract.wage * month)
        self.basic_actual_forecast = basic_actual + basic_forecast

        da_actual, da_forecast = self.da_salary, (((contract.da / 100) * contract.wage) * month)
        self.da_actual_forecast = da_actual + da_forecast

        ta_actual = sum(payslip_line_ids.filtered(lambda x: x.code == 'TA').mapped('amount'))
        ta_forecast = self.env['hr.payslip'].sudo().calculate_ta(contract) * month
        self.ta_actual_forecast = ta_actual + ta_forecast

        self.misc_salary = contract.supplementary_allowance

        hra_actual = sum(payslip_line_ids.filtered(lambda x: x.code == 'HRA').mapped('amount'))
        hra_forecast = self.env['hr.payslip'].sudo().calculate_hra(contract) * month
        self.hra_actual_forecast = hra_actual + hra_forecast

        gross_actual, gross_forecast = actual_gross, (contract.wage + self.allowance_current) * month
        self.gross_actual_forecast = gross_actual + gross_forecast

        self.medical_salary = sum(reimbursement_ids.filtered(lambda x: x.reimbursement_type_id.code == 'medical')\
                                    .mapped('approved_amount'))
        self.el_encash_salary = sum(reimbursement_ids.filtered(lambda x: x.reimbursement_type_id.code == 'el_encashment')\
                                    .mapped('approved_amount'))
        self.hostel_salary = actual_hostel_amount
        self.tuition_salary = actual_tuition_amount
        self.lunch_salary = lunch_total_amount
        self.ltc_advance_salary = sum(ltc_ids.mapped('amount'))
        self.house_income_salary = sum(self.income_house_ids.mapped('investment'))
        self.other_income_salary = sum(self.income_other_ids.mapped('investment'))
        self.total_gross_salary = self.gross_actual_forecast + self.medical_salary +\
                                    self.el_encash_salary + self.hostel_salary + self.tuition_salary +\
                                    self.lunch_salary + self.ltc_advance_salary + self.house_income_salary +\
                                    self.other_income_salary
        return True


    @api.multi
    def button_compute_tax(self, *args, **kwargs):
        month_dict = {1: 3, 2: 2, 3: 1, 4: 12, 5: 11, 6: 10, 7: 9, 8: 8, 9: 7, 10: 6, 11: 5, 12: 4}
        currentMonth = kwargs.get('date_to').month if kwargs.get('date_to') else datetime.now().month
        month = month_dict.get(currentMonth)
        for rec in self:
            rec.income_after_house_property = round(sum(rec.income_house_ids.mapped('investment')))
            rec.income_after_other_sources = round(sum(rec.income_other_ids.mapped('investment')))
            rec.rent_paid = round(sum(rec.rent_paid_ids.filtered(lambda x: x.date_to <= rec.date_range.date_end).mapped('amount')))
            rec.rent_paid_attach_files = rec.rent_paid > 100000
            payslip_line_ids = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),
                                                                        ('slip_id.state', '=', 'done'),
                                                                        ('slip_id.date_from', '>=', rec.date_range.date_start),
                                                                        ('slip_id.date_to', '<=', rec.date_range.date_end),
                                                                        ], order="date_to desc")
            rec.basic_salary = round(sum(payslip_line_ids.filtered(lambda x: x.code == 'BASIC').mapped('amount')))
            rec.da_salary = round(sum(payslip_line_ids.filtered(lambda x: x.code == 'DA').mapped('amount')))
            
            rec.sudo().button_forecast_gross()
            rec.sudo().button_calculate_allowance()
            rec.allowance_current += round(sum(payslip_line_ids.filtered(lambda x: x.code == 'ARRE').mapped('amount')))
            birthday_cheque = self.env['cheque.requests'].sudo().search([('approve_date', '>=', rec.date_range.date_start),
                                                                        ('approve_date', '<=', rec.date_range.date_end)],
                                                                        limit=1)
            rec.allowance_current += birthday_cheque.amount if birthday_cheque else 0
            rec.sudo().button_calculate_el_encash()

            actual_gross = round(sum(payslip_line_ids\
                                    .filtered(lambda x: x.salary_rule_id.taxable_percentage > 0 and x.code == 'GROSS')\
                                    .mapped('taxable_amount')))

            contract = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')], limit=1)
            employee = self.env['hr.employee'].sudo().browse(rec.employee_id.id)

            wage, updated_basic = contract.wage, contract.updated_basic

            _body = (_(f"<ul><b>Yearly Gross -:</b></ul>\
                            <ul>Basic Wage: {wage} </ul>\
                            <ul>Allowance: {rec.allowance_current} </ul>\
                            <ul>Actual Gross: {actual_gross} </ul>\
                            <ul>Income from House Property: {rec.income_after_house_property} </ul>\
                            <ul>Income from Other Sources: {rec.income_after_other_sources} </ul>\
                            <ul>EL Encashment and Medical Reimbursement: {rec.el_encashment} </ul>"))
            rec.message_post(body=_body)

            rec.std_ded_ids.unlink()
            rec.exemption_ids.unlink()
            rec.rebate_ids.unlink()

            exemption_ids = []
            slab_ids = []
            deduction_saving_ids = []

            reimbursement_ids =  self.env['reimbursement'].sudo().search([('employee_id', '=', rec.employee_id.id),
                                                                            ('date_range.date_start', '>=', rec.date_range.date_start),
                                                                            ('date_range.date_end', '<=', rec.date_range.date_end),
                                                                            ('state', '=', 'approved')])
            lunch_investment_amount = sum(reimbursement_ids.filtered(lambda x: x.reimbursement_type_id.code == 'lunch').mapped('lunch_tds_amt'))
            lunch_total_amount = sum(reimbursement_ids.filtered(lambda x: x.reimbursement_type_id.code == 'lunch').mapped('approved_amount'))

            # 80TTA
            saving_account = rec.income_other_ids.filtered(lambda x: x.it_rule.code == 'Saving Account')
            deduct_80tta_id = rec.deduction_saving_ids.filtered(lambda x: x.it_rule.code == '80tta')
            ex_80tta_id = self.env['saving.master'].sudo().search(
                    [('saving_type', '=', 'Deduction from Gross Total Income for Interest on Savings Bank Account')])
            
            if saving_account and not deduct_80tta_id:
                deduction_saving_ids.append((0, 0, {
                    'deduction_saving_id': rec.id,
                    'deduction_id': 'Deductions on Interest on Savings Account',
                    'it_rule': ex_80tta_id.it_rule.id,
                    'saving_master': ex_80tta_id.id,
                    'investment': min(sum(saving_account.mapped('investment')), ex_80tta_id.rebate),
                }))
                rec.deduction_saving_ids = deduction_saving_ids

            # 80C Exemption
            ex_80c_id = self.env['saving.master'].sudo().search(
                    [('saving_type', '=', 'Investment in PPF &  Employee’s share of PF contribution')])
            payslip_80c_line_ids = payslip_line_ids.filtered(lambda x: x.salary_rule_id.pf_register)
            investment_80c_amount = sum(payslip_80c_line_ids.filtered(lambda x: x.code in ['CEPF', 'VCPF']).mapped('amount'))
            allowed_80c_rebate = min(investment_80c_amount, ex_80c_id.rebate)
            is_80c_present = rec.slab_ids.filtered(lambda x: x.saving_master.saving_type == "Investment in PPF &  Employee’s share of PF contribution" and\
                                            x.it_rule.code == '80_c')
            if ex_80c_id and len(is_80c_present) == 0:
                slab_ids.append((0, 0, {
                    'slab_id': rec.id,
                    'deduction_id': 'slab_80_declaration',
                    'it_rule': ex_80c_id.it_rule.id,
                    'saving_master': ex_80c_id.id,
                    'investment': investment_80c_amount,
                    'allowed_rebate': allowed_80c_rebate,
                }))
                rec.slab_ids = slab_ids

            tuition_ids = reimbursement_ids.filtered(lambda x: x.reimbursement_type_id.code == 'tuition_fee')
            hostel_ids = reimbursement_ids.filtered(lambda x: x.reimbursement_type_id.code == 'hostel')
            actual_tuition_amount = sum(tuition_ids.mapped('approved_amount'))
            actual_hostel_amount = sum(hostel_ids.mapped('approved_amount'))
            actual_hostel_tution_amount = actual_tuition_amount + actual_hostel_amount
            
            rec.sudo().calculate_breakup(month, contract, payslip_line_ids, actual_gross, lunch_total_amount,
                                            actual_tuition_amount, actual_hostel_amount, reimbursement_ids)

            _body = (_(f"<ul>Lunch Approved: {lunch_total_amount} </ul>\
                        <ul>Tuition Approved: {actual_tuition_amount} </ul>\
                        <ul>Hostel Approved: {actual_hostel_amount} </ul>"))
            rec.message_post(body=_body)

            rec.tax_salary_final = (int(wage + rec.allowance_current) * int(month)) + round(actual_gross) +\
                                    rec.income_after_house_property + rec.income_after_other_sources +\
                                    rec.el_encashment + actual_hostel_tution_amount + lunch_total_amount
            
            age = relativedelta(date.today(), employee.birthday).years if employee.birthday else 30

            if rec.which_it == 'old':
                tax_slab, tax_slab_charge = 'income.tax.slab', 'income.tax.charge'

                # Lunch Exemption
                ex_lunch_id = self.env['saving.master'].sudo().search([('saving_type', '=', 'Lunch Subsidy Allowance')], limit=1)
                if ex_lunch_id:
                    exemption_ids.append((0, 0, {
                        'exemption_id': rec.id,
                        'it_rule': ex_lunch_id.it_rule.id,
                        'saving_master': ex_lunch_id.id,
                        'investment': round(lunch_investment_amount),
                        'allowed_rebate': round(lunch_investment_amount),
                    }))

                # CCA Exemption
                ex_child_id = self.env['saving.master'].sudo().search(
                        [('saving_type', '=', 'Child Education Allowance & Hostel Expenditure Allowance')])
                total_cca_ex = sum(tuition_ids.mapped('tuition_exempt_amount') + hostel_ids.mapped('hostel_exempt_amount'))

                if ex_child_id:
                    exemption_ids.append((0, 0, {
                        'exemption_id': rec.id,
                        'it_rule': ex_child_id.it_rule.id,
                        'saving_master': ex_child_id.id,
                        'investment': total_cca_ex,
                        'allowed_rebate': total_cca_ex,
                    }))
                
                # HRA Exemption
                ex_hra_id = self.env['saving.master'].sudo().search([('saving_type', '=', 'HRA Exemption')], limit=1)
                hra_payslip_line_ids = payslip_line_ids.filtered(lambda x: x.code == 'HRA')
                actual_hra = sum(hra_payslip_line_ids.mapped('amount'))
                forecasted_hra = self.env['hr.payslip'].sudo().calculate_hra(contract) * month
                total_hra = actual_hra + forecasted_hra
                actual_basic_da = rec.basic_salary + rec.da_salary
                forecasted_basic_da = updated_basic * month
                if rec.employee_id.branch_id.city_id.metro:
                    basic_metro_nonmetro = (actual_basic_da + forecasted_basic_da) * 0.5
                else:
                    basic_metro_nonmetro = (actual_basic_da + forecasted_basic_da) * 0.4
                taxable_rent_amount = rec.rent_paid - (actual_basic_da + forecasted_basic_da) * 0.1\
                                    if rec.rent_paid > 0 else 0
                hra_investment = min(total_hra, basic_metro_nonmetro, taxable_rent_amount)
                hra_investment = 0 if hra_investment < 0 else hra_investment
                if ex_hra_id:
                    exemption_ids.append((0, 0, {
                        'exemption_id': rec.id,
                        'it_rule': ex_hra_id.it_rule.id,
                        'saving_master': ex_hra_id.id,
                        'investment': hra_investment,
                        'allowed_rebate': hra_investment if not contract.xnohra else 0,
                    }))

                # Standard Deduction
                ex_std_id = self.env['saving.master'].sudo().search([('saving_type', '=', 'Std. Deduction')], limit=1)
                if ex_std_id:
                    std_investment = min(ex_std_id.rebate, rec.tax_salary_final)
                    std_ded_ids = []
                    std_ded_ids.append((0, 0, {
                            'std_ded_id': rec.id,
                            'it_rule': ex_std_id.it_rule.id,
                            'saving_master': ex_std_id.id,
                            'investment': std_investment,
                            'allowed_rebate': std_investment,
                        }))
                    rec.std_ded_ids = std_ded_ids
                std_deduct_tot_rebate = sum(rec.std_ded_ids.mapped('allowed_rebate'))
                professional_tax_line_ids = payslip_line_ids.filtered(lambda x: x.code == 'PTD')
                total_professional_tax = sum(professional_tax_line_ids.mapped('amount'))
                total_deduction_rebate = rec.allowed_rebate_under_80c + rec.allowed_rebate_under_80b +\
                                            rec.allowed_rebate_under_80d + rec.allowed_rebate_under_80dsa +\
                                            rec.allowed_rebate_under_80e + rec.allowed_rebate_under_80ccg +\
                                            rec.allowed_rebate_under_tbhl + rec.allowed_rebate_under_80ee +\
                                            rec.allowed_rebate_under_24 + rec.allowed_rebate_under_80cdd +\
                                            rec.allowed_rebate_under_80mesdr + rec.allowed_rebate_under_donation

            else:
                tax_slab, tax_slab_charge = 'income.tax.newslab', 'income.tax.newcharge'
                if employee.differently_abled == 'yes' and any((employee.is_blind, employee.is_deaf, employee.is_dumb, employee.is_ortho_handicapp)):
                    ex_trans_id = self.env['saving.master'].sudo().search([('saving_type', '=', 'Transport Allowance')],
                                                                            limit=1)
                    if ex_trans_id:
                        ta_payslip_line_count = len(payslip_line_ids.filtered(lambda x: x.code == 'TA'))

                        exemption_ids.append((0, 0, {
                            'exemption_id': rec.id,
                            'it_rule': ex_trans_id.it_rule.id,
                            'saving_master': ex_trans_id.id,
                            'investment': ta_payslip_line_count * 3200,
                            'allowed_rebate': ta_payslip_line_count * 3200,
                        }))
                total_deduction_rebate = 0

            rec.exemption_ids = exemption_ids
            exempt_tot_rebate = sum(rec.exemption_ids.mapped('allowed_rebate'))

            rec.income_after_exemption = round(rec.tax_salary_final + rec.previous_employer_income - exempt_tot_rebate)\
                                            if (rec.tax_salary_final + rec.previous_employer_income - exempt_tot_rebate) > 0.00\
                                            else 0
            if rec.which_it != 'old':
                rec.income_after_pro_tax, rec.income_after_std_ded = rec.income_after_exemption, rec.income_after_exemption
            else:
                rec.income_after_std_ded = round(rec.income_after_exemption - std_deduct_tot_rebate)\
                                            if rec.income_after_exemption - std_deduct_tot_rebate > 0.00\
                                            else 0
                rec.income_after_pro_tax = round(rec.income_after_std_ded - total_professional_tax)\
                                            if rec.income_after_std_ded - total_professional_tax > 0.00\
                                            else 0

            if (rec.income_after_pro_tax - rec.total_tds_paid - total_deduction_rebate) > 0.00:
                rec.taxable_income = round(rec.income_after_pro_tax - rec.total_tds_paid - total_deduction_rebate)
            else:
                rec.taxable_income = 0.00

            # Income tax slab
            income_slab = self.env[tax_slab].sudo().search([('salary_from', '<=', rec.taxable_income),
                                                            ('age_from', '<=', age),('age_to', '>=', age)],
                                                            order ="salary_from")
            total_tax_amt = 0
            if income_slab:
                for inc in income_slab:
                    if rec.taxable_income < inc.salary_to:
                        tax_amt = (rec.taxable_income - inc.salary_from) * (inc.tax_rate / 100)
                        total_tax_amt += tax_amt
                        _body = (
                            _(f" 111 --- {rec.taxable_income} - {inc.salary_from} - {tax_amt} - {total_tax_amt}"))
                        rec.message_post(body=_body)
                    else:
                        tax_amt = (inc.salary_to - inc.salary_from) *  (inc.tax_rate / 100)
                        total_tax_amt += tax_amt
                        _body = (
                            _(f" 222 --- {rec.taxable_income} - {inc.salary_from} - {tax_amt} - {total_tax_amt}"))
                        rec.message_post(body=_body)

            rec.tax_payable = round(total_tax_amt)
            income_charge = self.env[tax_slab_charge].sudo().search([('salary_from', '<=', rec.taxable_income),
                                                                        ('salary_to', '>=', rec.taxable_income), 
                                                                        ('age_from', '<=', age), 
                                                                        ('age_to', '>=', age)], limit=1)
            if income_charge:
                n_sur = (rec.tax_payable * income_charge.surcharge / 100)
                n_ces = (rec.tax_payable * income_charge.cess / 100)
                rec.tax_payable += (n_sur + n_ces)
                rec.tax_payable = round(rec.tax_payable)
            if rec.tax_payable <= 0.00:
                rec.tax_payable_zero = False
                rec.tax_payable = 0.00
            else:
                rec.tax_payable_zero = True

            # Rebate
            rebate_ids = []
            ex_rebate_id = self.env['saving.master'].sudo().search([('saving_type', '=', 'Revised Rebate under Section 87A (2019-20)')],
                                                                        limit=1)
            if ex_rebate_id:
                rebate_investment = rec.tax_payable if rec.taxable_income <= 500000 else 0
                allowed_rebate = min(rebate_investment, ex_rebate_id.rebate)
                rebate_ids.append((0, 0, {
                    'rebate_id': rec.id,
                    'it_rule': ex_rebate_id.it_rule.id,
                    'saving_master': ex_rebate_id.id,
                    'investment': rebate_investment,
                    'allowed_rebate': allowed_rebate,
                }))
                rec.rebate_ids = rebate_ids

            total_allowed_rebate = sum(rec.rebate_ids.mapped('allowed_rebate'))
            if rec.tax_payable >= total_allowed_rebate:
                rec.tax_payable_after_rebate = rec.tax_payable - total_allowed_rebate
                rec.rebate_received = total_allowed_rebate
            else:
                rec.tax_payable_after_rebate = 0.00
                rec.rebate_received = rec.tax_payable

            rec.tax_computed_bool = True
            rec.sudo().button_payment_tax()
        return True



    # @api.multi
    # def button_compute_tax(self):
    #     for rec in self:
    #         if rec.which_it == 'old':
    #             month = 1
    #             currentMonth = datetime.now().month
    #             print(currentMonth)
    #             if currentMonth == 4:
    #                 month = 12
    #             elif currentMonth == 5:
    #                 month = 11
    #             elif currentMonth == 6:
    #                 month = 10
    #             elif currentMonth == 7:
    #                 month = 9
    #             elif currentMonth == 8:
    #                 month = 8
    #             elif currentMonth == 9:
    #                 month = 7
    #             elif currentMonth == 10:
    #                 month = 6
    #             elif currentMonth == 11:
    #                 month = 5
    #             elif currentMonth == 12:
    #                 month = 4
    #             elif currentMonth == 1:
    #                 month = 3
    #             elif currentMonth == 2:
    #                 month = 2
    #             elif currentMonth == 3:
    #                 month = 1
    #             sum = 0
    #             for line in rec.income_house_ids:
    #                 sum+=line.investment
    #             rec.income_after_house_property = sum
    #             sum = 0
    #             for line in rec.income_other_ids:
    #                 sum+=line.investment
    #             rec.income_after_other_sources = sum
    #             sum = 0
    #             for lines in rec.rent_paid_ids:
    #                 if lines.date_to <= datetime.now().date():
    #                     sum += lines.amount
    #             rec.rent_paid = round(sum)
    #             if rec.rent_paid > 100000.00:
    #                 rec.rent_paid_attach_files = True
    #             else:
    #                 rec.rent_paid_attach_files = False
    #             bs = 0.00
    #             da = 0.00
    #             dstart = rec.date_range.date_start
    #             dend = rec.date_range.date_end
    #             prl_id = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),
    #                                                                 ('slip_id.state', '=', 'done'),
    #                                                                 ('slip_id.date_from', '>=', dstart),
    #                                                                 ('slip_id.date_to', '<=', dend),
    #                                                                 ], order="date_to desc")
    #             for pr in prl_id:
    #                 if pr.code == 'BASIC':
    #                     bs += pr.amount
    #                 elif pr.code == 'DA':
    #                     da += pr.amount
    #             rec.basic_salary = round(bs)
    #             rec.da_salary = round(da)
    #             rec.sudo().button_forecast_gross()
    #             rec.sudo().button_calculate_allowance()
    #             rec.sudo().button_calculate_el_encash()
    #             sum = 0
    #             dstart = rec.date_range.date_start
    #             dend = rec.date_range.date_end
    #             proll =  self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),
    #                                                                 ('slip_id.state', '=', 'done'),
    #                                                                 ('salary_rule_id.taxable_percentage', '>', 0),
    #                                                                 ('slip_id.date_from', '>=', dstart),
    #                                                                 ('salary_rule_id.code', '=', 'GROSS'),
    #                                                                 ('slip_id.date_to', '<=', dend)
    #                                                                 ],order ="date_to desc")
    #             for i in proll:
    #                 sum += i.taxable_amount
    #             contrct = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id),
    #                                                                ('state', '=', 'open')
    #                                                                ],limit=1)

    #             wage = 0
    #             updated_basic = 0
    #             for cnt in contrct:
    #                 wage = cnt.wage
    #                 updated_basic = cnt.updated_basic

    #             _body = (_(
    #                 (
    #                     "<ul><b>Yearly Gross -:</b></ul>"
    #                         "<ul>Basic Wage: {0} </ul>"
    #                         "<ul>Allowance: {1} </ul>"
    #                         "<ul>Actual Gross: {2} </ul>"
    #                         "<ul>Income from House Property: {3} </ul>"
    #                         "<ul>Income from Other Sources: {4} </ul>"
    #                         "<ul>EL Encashment and Medical Reimbursement: {5} </ul>"

    #                 ).format(wage,rec.allowance_current,sum,rec.income_after_house_property,rec.income_after_other_sources,rec.el_encashment)))
    #             rec.message_post(body=_body)
    #             if sum == 0:
    #                 rec.tax_salary_final = int(wage + rec.allowance_current) * int(month) + rec.income_after_house_property + rec.income_after_other_sources + rec.el_encashment
    #             else:
    #                 rec.tax_salary_final = int(wage + rec.allowance_current)*(int(month) - 1) + round(sum) + rec.income_after_house_property + rec.income_after_other_sources + rec.el_encashment
    #             age = 0
    #             rec.std_ded_ids.unlink()
    #             rec.exemption_ids.unlink()
    #             rec.rebate_ids.unlink()
    #             ex_std_id = self.env['saving.master'].sudo().search(
    #                 [('saving_type', '=', 'Std. Deduction')], limit=1)
    #             my_investment = 0.00
    #             if ex_std_id:
    #                 my_investment = 0.00
    #                 my_allowed_rebate = 0.00
    #                 if rec.tax_salary_final >= ex_std_id.rebate:
    #                     my_investment = ex_std_id.rebate
    #                 else:
    #                     my_investment = rec.tax_salary_final

    #                 if my_investment <= ex_std_id.rebate:
    #                     my_allowed_rebate = my_investment
    #                 else:
    #                     my_allowed_rebate = ex_std_id.rebate
    #                 std_ded_ids = []
    #                 std_ded_ids.append((0, 0, {
    #                      'std_ded_id': rec.id,
    #                     'it_rule': ex_std_id.it_rule.id,
    #                     'saving_master': ex_std_id.id,
    #                     'investment': my_investment,
    #                     'allowed_rebate': my_allowed_rebate,
    #                 }))
    #                 rec.std_ded_ids = std_ded_ids
    #             ex_child_id = self.env['saving.master'].sudo().search(
    #                 [('saving_type', '=', 'Child Education Allowance & Hostel Expenditure Allowance')], limit=1)
    #             child_id = self.env['employee.relative'].sudo().search(
    #                 [('employee_id', '=', rec.employee_id.id)])
    #             prl_id = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),('slip_id.state', '=', 'done'),('code', '=', 'CCA'),('slip_id.date_from', '>=', rec.date_range.date_start),('slip_id.date_to', '<=', rec.date_range.date_end)],order ="date_to desc")
    #             count = 0
    #             my_investment = 0.00
    #             my_allowed_rebate = 0.00
    #             pl_amount = 0.00
    #             count_paylines = 0.00
    #             if ex_child_id:
    #                 print('inside ex_child_id ==>')
    #                 for cc in child_id:
    #                     if cc.relate_type_name == 'Son' or cc.relate_type_name == 'Daughter':
    #                         count += 1
    #                 for pl in prl_id:
    #                     count_paylines += 1
    #                     pl_amount += pl.amount
    #                 print(f'count ==> {count} count_paylines ==> {count_paylines}\
    #                      pl_amount ==> {pl_amount} prl_id ==> {prl_id}')
    #                 if rec.employee_id.date_of_join and rec.date_range.date_start < rec.employee_id.date_of_join <= rec.date_range.date_end:
    #                     nm = ((rec.date_range.date_end - rec.employee_id.date_of_join).days)/30
    #                     relative_sum = count * 100 * round(nm)
    #                 else:
    #                     relative_sum = count * 100 * round(count_paylines)
    #                 print(f'pl_amount ==> {pl_amount} relative_sum ==> {relative_sum}')
    #                 if pl_amount < relative_sum:
    #                     my_investment = pl_amount
    #                 else:
    #                     my_investment = relative_sum
    #                 print('my_investment ==>', my_investment)
    #                 if my_investment <= ex_child_id.rebate:
    #                     my_allowed_rebate = my_investment
    #                 else:
    #                     my_allowed_rebate = ex_child_id.rebate
    #                 exemption_ids = []
    #                 exemption_ids.append((0, 0, {
    #                     'exemption_id': rec.id,
    #                     'it_rule': ex_child_id.it_rule.id,
    #                     'saving_master': ex_child_id.id,
    #                     'investment': my_investment,
    #                     'allowed_rebate': my_allowed_rebate,
    #                 }))
    #                 rec.exemption_ids = exemption_ids
    #             contrct = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id),
    #                                                              ('state', '=', 'open')
    #                                                              ], limit=1)
    #             print('HRA EXEMPTION START ========>')
    #             ex_hra_id = self.env['saving.master'].sudo().search([('saving_type', '=', 'HRA Exemption')], limit=1)
    #             prl_id = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),
    #                                                     ('slip_id.state', '=', 'done'),('code', '=', 'HRA'),
    #                                                     ('slip_id.date_from', '>', rec.date_range.date_start),
    #                                                     ('slip_id.date_to', '<', rec.date_range.date_end)],order ="date_to desc")
    #             # prl_current_id = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),
    #             #                                         ('slip_id.state', '=', 'done'),('code', '=', 'HRA'),
    #             #                                         ('slip_id.date_from', '=', datetime.now().replace(day=1)),('slip_id.date_to', '=', datetime.now().replace(day=1) + relativedelta(months=1) - relativedelta(days=1))])
    #             HRA = 0
    #             contrct = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id), 
    #                                                             ('state', '=', 'open')], limit=1)
    #             for contract in contrct:
    #                 if contract.employee_hra_cat == 'x':
    #                     HRA = 0.24 * contract.wage
    #                 elif contract.employee_hra_cat == 'y':
    #                     HRA = 0.16 * contract.wage
    #                 elif contract.employee_hra_cat == 'z':
    #                     HRA = 0.08 * contract.wage
    #                 else:
    #                     HRA = 0
    #             sum_bs = 0.00
    #             sum_rent = 0.00
    #             sum_prl = 0.00
    #             sum_prl_current = 0.00
    #             sum=0.00
    #             my_investment = 0.00
    #             my_allowed_rebate = 0.00
    #             sum_list = []
    #             for cc in prl_id:
    #                 sum_prl+=cc.amount
    #             sum_prl_current = int(HRA) *int(month)
    #             sum_prl = sum_prl + sum_prl_current
    #             print(f'sum_prl_current ==> {sum_prl_current} sum_prl ==> {sum_prl}')
    #             if rec.employee_id.branch_id.city_id.metro == True:
    #                 sum_bs = ((rec.basic_salary + rec.da_salary + int(updated_basic)*int(month))*50)/100
    #             else:
    #                 sum_bs = ((rec.basic_salary + rec.da_salary + int(updated_basic)*int(month))*40)/100
    #             sum_rent = rec.rent_paid - (((rec.basic_salary + rec.da_salary + int(updated_basic)*int(month) )*10)/100)

    #             sum_list.append(sum_prl)
    #             sum_list.append(sum_bs)
    #             sum_list.append(sum_rent)
    #             print(f'sum_list ==> {sum_list}')
    #             compare = 0.00
    #             compare_value = 10000000000000.00
    #             for i in sum_list:
    #                 if compare_value > i and i > compare:
    #                     compare_value = i
    #             sum = compare_value
    #             print(f'sum ==> {sum}')
    #             if ex_hra_id:
    #                 my_investment = sum
    #                 if my_investment <= ex_hra_id.rebate:
    #                     my_allowed_rebate = my_investment
    #                 else:
    #                     my_allowed_rebate = ex_hra_id.rebate
    #                 if int(rec.rent_paid) == 0 or contrct.xnohra == True:
    #                     my_allowed_rebate = 0
    #                 print(f'sum ==> {sum} my_investment ==> {my_investment} my_allowed_rebate ==> {my_allowed_rebate}')
    #                 exemption_ids = []
    #                 exemption_ids.append((0, 0, {
    #                     'exemption_id': rec.id,
    #                     'it_rule': ex_hra_id.it_rule.id,
    #                     'saving_master': ex_hra_id.id,
    #                     'investment': my_investment,
    #                     'allowed_rebate': my_allowed_rebate,
    #                 }))
    #                 rec.exemption_ids = exemption_ids
    #             ex_lunch_id = self.env['saving.master'].sudo().search([('saving_type', '=', 'Lunch Subsidy Allowance')], limit=1)
    #             reimbursement_id =  self.env['reimbursement'].sudo().search([('employee_id', '=', rec.employee_id.id),('name', '=', 'lunch'),('date_range.date_start', '>', rec.date_range.date_start),('date_range.date_end', '<', rec.date_range.date_end),('state', '=', 'approved')])
    #             sum=0.00
    #             my_investment = 0.00
    #             my_allowed_rebate = 0.00
    #             for cc in reimbursement_id:
    #                 sum+=float(cc.lunch_tds_amt)
    #             if ex_lunch_id:
    #                 my_investment = sum
    #                 if my_investment <= ex_lunch_id.rebate:
    #                     my_allowed_rebate = my_investment
    #                 else:
    #                     my_allowed_rebate = ex_lunch_id.rebate
    #                 exemption_ids = []
    #                 exemption_ids.append((0, 0, {
    #                     'exemption_id': rec.id,
    #                     'it_rule': ex_lunch_id.it_rule.id,
    #                     'saving_master': ex_lunch_id.id,
    #                     'investment': my_investment,
    #                     'allowed_rebate': my_allowed_rebate,
    #                 }))
    #                 rec.exemption_ids = exemption_ids
    #             ex_80_c_id = self.env['saving.master'].sudo().search(
    #                 [('saving_type', '=', 'Investment in PPF &  Employee’s share of PF contribution')], limit=1)
    #             prl_80c_id = self.env['hr.payslip.line'].sudo().search(
    #                 [('slip_id.employee_id', '=', rec.employee_id.id),
    #                  ('slip_id.state', '=', 'done'),
    #                  ('salary_rule_id.pf_register', '=', True),
    #                  ('slip_id.date_from', '>', rec.date_range.date_start),
    #                  ('slip_id.date_to', '<', rec.date_range.date_end)],order ="date_to desc")
    #             sum = 0
    #             for sr in prl_80c_id:
    #                 if sr.code == 'CEPF' or sr.code == 'VCPF':
    #                     sum += sr.amount
    #             my_investment = 0.00
    #             my_allowed_rebate = 0.00
    #             if ex_80_c_id:
    #                 my_investment = sum
    #                 if my_investment <= ex_80_c_id.rebate:
    #                     my_allowed_rebate = my_investment
    #                 else:
    #                     my_allowed_rebate = ex_80_c_id.rebate
    #                 slab_ids = []
    #                 slab_ids.append((0, 0, {
    #                     'slab_id': rec.id,
    #                     'deduction_id': 'slab_80_declaration',
    #                     'it_rule': ex_80_c_id.it_rule.id,
    #                     'saving_master': ex_80_c_id.id,
    #                     'investment': my_investment,
    #                     'allowed_rebate': my_allowed_rebate,
    #                 }))
    #                 emp_id = self.env['declaration.slab'].sudo().search(
    #                     [('saving_master.saving_type', '=', 'Investment in PPF &  Employee’s share of PF contribution'), ('it_rule.code', '=', '80_c'),
    #                      ('slab_id', '=', rec.id)])
    #                 if not emp_id:
    #                     rec.slab_ids = slab_ids
    #             exempt_am = 0.00
    #             std_am = 0.00
    #             sum_pt = 0.00
    #             for std in rec.std_ded_ids:
    #                 std_am += std.allowed_rebate
    #             for ex in rec.exemption_ids:
    #                 exempt_am += ex.allowed_rebate
    #             pr_pt_id = self.env['hr.payslip.line'].sudo().search(
    #                 [('slip_id.employee_id', '=', rec.employee_id.id), ('slip_id.state', '=', 'done'), ('code', '=', 'PTD'),
    #                  ('slip_id.date_from', '>', rec.date_range.date_start),
    #                  ('slip_id.date_to', '<', rec.date_range.date_end)],order ="date_to desc")
    #             for pt in pr_pt_id:
    #                 sum_pt += pt.amount
    #             if (rec.tax_salary_final + rec.previous_employer_income - exempt_am) > 0.00:
    #                 rec.income_after_exemption = round(rec.tax_salary_final + rec.previous_employer_income - exempt_am)
    #             else:
    #                 rec.income_after_exemption = 0.00
    #             if rec.income_after_exemption - std_am > 0.00:
    #                 rec.income_after_std_ded = round(rec.income_after_exemption - std_am)
    #             else:
    #                 rec.income_after_std_ded = 0.00
    #             if rec.income_after_std_ded - sum_pt > 0.00:
    #                 rec.income_after_pro_tax = round(rec.income_after_std_ded - sum_pt)
    #             else:
    #                 rec.income_after_pro_tax = 0.00
    #             if (rec.income_after_pro_tax - rec.total_tds_paid - (rec.allowed_rebate_under_80c + rec.allowed_rebate_under_80b + rec.allowed_rebate_under_80d + rec.allowed_rebate_under_80dsa + rec.allowed_rebate_under_80e + rec.allowed_rebate_under_80ccg + rec.allowed_rebate_under_tbhl + rec.allowed_rebate_under_80ee + rec.allowed_rebate_under_24 + rec.allowed_rebate_under_80cdd + rec.allowed_rebate_under_80mesdr + rec.allowed_rebate_under_donation)) > 0.00:
    #                 rec.taxable_income = round(rec.income_after_pro_tax - rec.total_tds_paid - (rec.allowed_rebate_under_80c + rec.allowed_rebate_under_80b + rec.allowed_rebate_under_80d + rec.allowed_rebate_under_80dsa + rec.allowed_rebate_under_80e + rec.allowed_rebate_under_80ccg + rec.allowed_rebate_under_tbhl + rec.allowed_rebate_under_80ee + rec.allowed_rebate_under_24 + rec.allowed_rebate_under_80cdd + rec.allowed_rebate_under_80mesdr + rec.allowed_rebate_under_donation))
    #             else:
    #                 rec.taxable_income = 0.00
    #             employee = self.env['hr.employee'].sudo().search([('id', '=', rec.employee_id.id),
    #                                                               ], limit=1)
    #             years = 30
    #             if employee and employee.birthday:
    #                 years = relativedelta(date.today(), employee.birthday).years
    #             income_slab = self.env['income.tax.slab'].sudo().search(
    #                 [('salary_from', '<=', rec.taxable_income),('age_from', '<=', years),('age_to', '>=', years)],
    #                 order ="salary_from")
    #             total_tax_amt = 0
    #             surcharge = 0
    #             cess = 0
    #             if income_slab:
    #                 for inc in income_slab:
    #                     if rec.taxable_income < inc.salary_to:
    #                         tax_amt = (rec.taxable_income - inc.salary_from) * (inc.tax_rate / 100)
    #                         total_tax_amt += tax_amt
    #                         _body = (
    #                             _(" 111 --- {0} - {1} - {2} - {3}").format(rec.taxable_income,inc.salary_from,tax_amt,total_tax_amt))
    #                         rec.message_post(body=_body)
    #                     else:
    #                         tax_amt = (inc.salary_to - inc.salary_from) *  (inc.tax_rate / 100)
    #                         total_tax_amt += tax_amt
    #                         _body = (
    #                             _(" 222 --- {0} - {1} - {2} - {3}").format(rec.taxable_income,inc.salary_from, tax_amt,
    #                                                                  total_tax_amt))
    #                         rec.message_post(body=_body)
    #                     surcharge = inc.surcharge
    #                     cess = inc.cess

    #             rec.tax_payable = round(total_tax_amt)
    #             income_charge = self.env['income.tax.charge'].sudo().search(
    #                 [('salary_from', '<=', rec.taxable_income),('salary_to', '>=', rec.taxable_income), ('age_from', '<=', years), ('age_to', '>=', years)],limit=1
    #                 )
    #             if income_charge:
    #                 for inc in income_charge:
    #                     n_sur = (rec.tax_payable * inc.surcharge / 100)
    #                     n_ces = (rec.tax_payable * inc.cess / 100)
    #                     rec.tax_payable += (n_sur + n_ces)
    #                 rec.tax_payable = round(rec.tax_payable)
    #             if rec.tax_payable <= 0.00:
    #                 rec.tax_payable_zero = False
    #                 rec.tax_payable = 0.00
    #             else:
    #                 rec.tax_payable_zero = True
    #             ex_rebate_id = self.env['saving.master'].sudo().search(
    #                 [('saving_type', '=', 'Revised Rebate under Section 87A (2019-20)')],
    #                 limit=1)
    #             my_investment = 0.00
    #             my_allowed_rebate = 0.00
    #             if ex_rebate_id:
    #                 if rec.taxable_income <= 500000:
    #                     my_investment = rec.tax_payable
    #                 else:
    #                     my_investment = 0.00
    #                 if my_investment <= ex_rebate_id.rebate:
    #                     my_allowed_rebate = my_investment
    #                 else:
    #                     my_allowed_rebate = ex_rebate_id.rebate
    #                 rebate_ids = []
    #                 rebate_ids.append((0, 0, {
    #                     'rebate_id': rec.id,
    #                     'it_rule': ex_rebate_id.it_rule.id,
    #                     'saving_master': ex_rebate_id.id,
    #                     'investment': my_investment,
    #                     'allowed_rebate': my_allowed_rebate,
    #                 }))
    #                 rec.rebate_ids = rebate_ids
    #             sum_rbt=0.0
    #             for rbt in rec.rebate_ids:
    #                 sum_rbt += rbt.allowed_rebate
    #             if rec.tax_payable >= sum_rbt:
    #                 rec.tax_payable_after_rebate = rec.tax_payable - sum_rbt
    #                 rec.rebate_received = sum_rbt
    #             else:
    #                 rec.tax_payable_after_rebate = 0.00
    #                 rec.rebate_received = rec.tax_payable
    #             rec.tax_computed_bool = True
    #             rec.sudo().button_payment_tax()
    #         else:
    #             currentMonth = datetime.now().month
    #             print(currentMonth)
    #             if currentMonth == 4:
    #                 month = 12
    #             elif currentMonth == 5:
    #                 month = 11
    #             elif currentMonth == 6:
    #                 month = 10
    #             elif currentMonth == 7:
    #                 month = 9
    #             elif currentMonth == 8:
    #                 month = 8
    #             elif currentMonth == 9:
    #                 month = 7
    #             elif currentMonth == 10:
    #                 month = 6
    #             elif currentMonth == 11:
    #                 month = 5
    #             elif currentMonth == 12:
    #                 month = 4
    #             elif currentMonth == 1:
    #                 month = 3
    #             elif currentMonth == 2:
    #                 month = 2
    #             elif currentMonth == 3:
    #                 month = 1
    #             sum = 0
    #             for line in rec.income_house_ids:
    #                 sum+=line.investment
    #             rec.income_after_house_property = sum
    #             sum = 0
    #             for line in rec.income_other_ids:
    #                 sum+=line.investment
    #             rec.income_after_other_sources = sum
    #             sum = 0
    #             for lines in rec.rent_paid_ids:
    #                 if lines.date_to <= datetime.now().date():
    #                     sum += lines.amount
    #             rec.rent_paid = round(sum)
    #             if rec.rent_paid > 100000.00:
    #                 rec.rent_paid_attach_files = True
    #             else:
    #                 rec.rent_paid_attach_files = False
    #             bs = 0.00
    #             da = 0.00
    #             dstart = rec.date_range.date_start
    #             dend = rec.date_range.date_end
    #             prl_id = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),
    #                                                                 ('slip_id.state', '=', 'done'),
    #                                                                 ('slip_id.date_from', '>=', dstart),
    #                                                                 ('slip_id.date_to', '<=', dend),
    #                                                                 ], order="date_to desc")
    #             for pr in prl_id:
    #                 if pr.code == 'BASIC':
    #                     bs += pr.amount
    #                 elif pr.code == 'DA':
    #                     da += pr.amount
    #             rec.basic_salary = round(bs)
    #             rec.da_salary = round(da)
    #             rec.sudo().button_forecast_gross()
    #             rec.sudo().button_calculate_allowance()
    #             rec.sudo().button_calculate_el_encash()
    #             sum = 0
    #             dstart = rec.date_range.date_start
    #             dend = rec.date_range.date_end
    #             proll =  self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),
    #                                                                 ('slip_id.state', '=', 'done'),
    #                                                                 ('salary_rule_id.taxable_percentage', '>', 0),
    #                                                                 ('slip_id.date_from', '>=', dstart),
    #                                                                 ('salary_rule_id.code', '=', 'GROSS'),
    #                                                                 ('slip_id.date_to', '<=', dend)
    #                                                                 ],order ="date_to desc")
    #             for i in proll:
    #                 sum += i.taxable_amount
    #             contrct = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id),
    #                                                                ('state', '=', 'open')
    #                                                                ],limit=1)

    #             wage = 0
    #             updated_basic = 0
    #             for cnt in contrct:
    #                 wage = cnt.wage
    #                 updated_basic = cnt.updated_basic
    #             _body = (_(
    #                 (
    #                     "<ul><b>Yearly Gross -:</b></ul>"
    #                         "<ul>Basic Wage: {0} </ul>"
    #                         "<ul>Allowance: {1} </ul>"
    #                         "<ul>Actual Gross: {2} </ul>"
    #                         "<ul>Income from House Property: {3} </ul>"
    #                         "<ul>Income from Other Sources: {4} </ul>"
    #                         "<ul>EL Encashment and Medical Reimbursement: {5} </ul>"

    #                 ).format(wage,rec.allowance_current,sum,rec.income_after_house_property,rec.income_after_other_sources,rec.el_encashment)))
    #             rec.message_post(body=_body)
    #             rec.tax_salary_final = int(wage + rec.allowance_current)*int(month) + round(sum) + rec.income_after_house_property + rec.income_after_other_sources + rec.el_encashment
    #             age = 0
    #             rec.std_ded_ids.unlink()
    #             rec.exemption_ids.unlink()
    #             rec.rebate_ids.unlink()
    #             # rec.slab_ids.unlink()
    #             ex_std_id = self.env['saving.master'].sudo().search(
    #                 [('saving_type', '=', 'Std. Deduction')], limit=1)
    #             my_investment = 0.00
    #             if ex_std_id:
    #                 my_investment = 0.00
    #                 my_allowed_rebate = 0.00
    #                 if rec.tax_salary_final >= ex_std_id.rebate:
    #                     my_investment = ex_std_id.rebate
    #                 else:
    #                     my_investment = rec.tax_salary_final

    #                 if my_investment <= ex_std_id.rebate:
    #                     my_allowed_rebate = my_investment
    #                 else:
    #                     my_allowed_rebate = ex_std_id.rebate
    #                 std_ded_ids = []
    #                 std_ded_ids.append((0, 0, {
    #                      'std_ded_id': rec.id,
    #                     'it_rule': ex_std_id.it_rule.id,
    #                     'saving_master': ex_std_id.id,
    #                     'investment': my_investment,
    #                     'allowed_rebate': my_allowed_rebate,
    #                 }))
    #                 rec.std_ded_ids = std_ded_ids
    #             employee = self.env['hr.employee'].sudo().search([('id', '=', rec.employee_id.id),
    #                                                               ], limit=1)
    #             if employee.differently_abled == 'yes':
    #                 ex_trans_id = self.env['saving.master'].sudo().search([('saving_type', '=', 'Transport Allowance')],
    #                                                                       limit=1)
    #                 dis_paytrans = self.env['hr.payslip.line'].sudo().search(
    #                     [('slip_id.employee_id', '=', rec.employee_id.id),
    #                      ('slip_id.state', '=', 'done'),
    #                      ('code', '=', 'TA'),
    #                      ('slip_id.date_from', '>=', dstart),
    #                      ('slip_id.date_to', '<=', dend),
    #                      ], order="date_to desc")
    #                 coun=0
    #                 for ct in dis_paytrans:
    #                     coun+=1
    #                 amt = coun*3200
    #                 exemption_ids = []
    #                 exemption_ids.append((0, 0, {
    #                     'exemption_id': rec.id,
    #                     'it_rule': ex_trans_id.it_rule.id,
    #                     'saving_master': ex_trans_id.id,
    #                     'investment': amt,
    #                     'allowed_rebate': amt,
    #                 }))
    #                 rec.exemption_ids = exemption_ids
    #             # ex_child_id = self.env['saving.master'].sudo().search(
    #             #     [('saving_type', '=', 'Child Education Allowance & Hostel Expenditure Allowance')], limit=1)
    #             # child_id = self.env['employee.relative'].sudo().search(
    #             #     [('employee_id', '=', rec.employee_id.id)])
    #             # prl_id = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),('slip_id.state', '=', 'done'),('code', '=', 'CCA'),('slip_id.date_from', '>', rec.date_range.date_start),('slip_id.date_to', '<', rec.date_range.date_end)],order ="date_to desc")
    #             # count = 0
    #             # my_investment = 0.00
    #             # my_allowed_rebate = 0.00
    #             # pl_amount = 0.00
    #             # count_paylines = 0.00
    #             # if ex_child_id:
    #             #     for cc in child_id:
    #             #         if cc.relate_type_name == 'Son' or cc.relate_type_name == 'Daughter':
    #             #             count += 1
    #             #     for pl in prl_id:
    #             #         count_paylines += 1
    #             #         pl_amount += pl.amount
    #             #     if rec.employee_id.date_of_join and rec.date_range.date_start < rec.employee_id.date_of_join <= rec.date_range.date_end:
    #             #         nm = ((rec.date_range.date_end - rec.employee_id.date_of_join).days)/30
    #             #         relative_sum = count * 100 * round(nm)
    #             #     else:
    #             #         relative_sum = count * 100 * round(count_paylines)
    #             #     if pl_amount < relative_sum:
    #             #         my_investment = pl_amount
    #             #     else:
    #             #         my_investment = relative_sum
    #             #
    #             #     if my_investment <= ex_child_id.rebate:
    #             #         my_allowed_rebate = my_investment
    #             #     else:
    #             #         my_allowed_rebate = ex_child_id.rebate
    #             #     exemption_ids = []
    #             #     exemption_ids.append((0, 0, {
    #             #         'exemption_id': rec.id,
    #             #         'it_rule': ex_child_id.it_rule.id,
    #             #         'saving_master': ex_child_id.id,
    #             #         'investment': my_investment,
    #             #         'allowed_rebate': my_allowed_rebate,
    #             #     }))
    #                 # rec.exemption_ids = exemption_ids
    #             # contrct = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id),
    #             #                                                  ('state', '=', 'open')
    #             #                                                  ], limit=1)
    #             #
    #             # ex_hra_id = self.env['saving.master'].sudo().search([('saving_type', '=', 'HRA Exemption')], limit=1)
    #             # prl_id = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),('slip_id.state', '=', 'done'),('code', '=', 'HRA'),('slip_id.date_from', '>', rec.date_range.date_start),('slip_id.date_to', '<', rec.date_range.date_end)],order ="date_to desc")
    #             # prl_current_id = self.env['hr.payslip.line'].sudo().search([('slip_id.employee_id', '=', rec.employee_id.id),('slip_id.state', '=', 'done'),('code', '=', 'HRA'),('slip_id.date_from', '=', datetime.now().replace(day=1)),('slip_id.date_to', '=', datetime.now().replace(day=1) + relativedelta(months=1) - relativedelta(days=1))])
    #             # HRA = 0
    #             # DA = 0
    #             # TA = 0
    #             # contrct = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id),
    #             #                                                  ('state', '=', 'open')
    #             #                                                  ], limit=1)
    #             # for contract in contrct:
    #             #     if contract.employee_hra_cat == 'x':
    #             #         HRA = 0.24 * contract.wage
    #             #     elif contract.employee_hra_cat == 'y':
    #             #         HRA = 0.16 * contract.wage
    #             #     elif contract.employee_hra_cat == 'z':
    #             #         HRA = 0.08 * contract.wage
    #             #     else:
    #             #         HRA = 0
    #             # sum_bs = 0.00
    #             # sum_rent = 0.00
    #             # sum_prl = 0.00
    #             # sum_prl_current = 0.00
    #             # sum=0.00
    #             # my_investment = 0.00
    #             # my_allowed_rebate = 0.00
    #             # sum_list = []
    #             # for cc in prl_id:
    #             #     sum_prl+=cc.amount
    #             # sum_prl_current = int(HRA) *int(month)
    #             # sum_prl = sum_prl + sum_prl_current
    #             # if rec.employee_id.branch_id.city_id.metro == True:
    #             #     sum_bs = ((rec.basic_salary + rec.da_salary + int(updated_basic)*int(month))*50)/100
    #             # else:
    #             #     sum_bs = ((rec.basic_salary + rec.da_salary + int(updated_basic)*int(month))*40)/100
    #             # sum_rent = rec.rent_paid - (((rec.basic_salary + rec.da_salary + int(updated_basic)*int(month) )*10)/100)
    #             #
    #             # sum_list.append(sum_prl)
    #             # sum_list.append(sum_bs)
    #             # sum_list.append(sum_rent)
    #             # compare = 0.00
    #             # compare_value = 10000000000000.00
    #             # for i in sum_list:
    #             #     if compare_value > i and i > compare:
    #             #         compare_value = i
    #             # sum = compare_value
    #             # if ex_hra_id:
    #             #     my_investment = sum
    #             #     if my_investment <= ex_hra_id.rebate:
    #             #         my_allowed_rebate = my_investment
    #             #     else:
    #             #         my_allowed_rebate = ex_hra_id.rebate
    #             #     print('====================rec.rent_paid========================',int(rec.rent_paid))
    #             #     print('====================contrct.xnohrad========================',contrct.xnohra)
    #             #     if int(rec.rent_paid) == 0 or contrct.xnohra == True:
    #             #         my_allowed_rebate = 0
    #             #         print('====================True========================')
    #             #
    #             #     exemption_ids = []
    #             #     exemption_ids.append((0, 0, {
    #             #         'exemption_id': rec.id,
    #             #         'it_rule': ex_hra_id.it_rule.id,
    #             #         'saving_master': ex_hra_id.id,
    #             #         'investment': my_investment,
    #             #         'allowed_rebate': my_allowed_rebate,
    #             #     }))
    #                 # rec.exemption_ids = exemption_ids
    #             ex_lunch_id = self.env['saving.master'].sudo().search([('saving_type', '=', 'Lunch Subsidy Allowance')], limit=1)
    #             reimbursement_id =  self.env['reimbursement'].sudo().search([('employee_id', '=', rec.employee_id.id),('name', '=', 'lunch'),('date_range.date_start', '>', rec.date_range.date_start),('date_range.date_end', '<', rec.date_range.date_end),('state', '=', 'approved')])
    #             sum=0.00
    #             my_investment = 0.00
    #             my_allowed_rebate = 0.00
    #             for cc in reimbursement_id:
    #                 sum+=float(cc.lunch_tds_amt)
    #             if ex_lunch_id:
    #                 my_investment = sum
    #                 if my_investment <= ex_lunch_id.rebate:
    #                     my_allowed_rebate = my_investment
    #                 else:
    #                     my_allowed_rebate = ex_lunch_id.rebate
    #                 exemption_ids = []
    #                 exemption_ids.append((0, 0, {
    #                     'exemption_id': rec.id,
    #                     'it_rule': ex_lunch_id.it_rule.id,
    #                     'saving_master': ex_lunch_id.id,
    #                     'investment': my_investment,
    #                     'allowed_rebate': my_allowed_rebate,
    #                 }))

    #             ex_80_c_id = self.env['saving.master'].sudo().search(
    #                 [('saving_type', '=', 'Investment in PPF &  Employee’s share of PF contribution')], limit=1)
    #             prl_80c_id = self.env['hr.payslip.line'].sudo().search(
    #                 [('slip_id.employee_id', '=', rec.employee_id.id),
    #                  ('slip_id.state', '=', 'done'),
    #                  ('salary_rule_id.pf_register', '=', True),
    #                  ('slip_id.date_from', '>', rec.date_range.date_start),
    #                  ('slip_id.date_to', '<', rec.date_range.date_end)],order ="date_to desc")
    #             sum = 0
    #             for sr in prl_80c_id:
    #                 if sr.code == 'CEPF' or sr.code == 'VCPF':
    #                     sum += sr.amount
    #             my_investment = 0.00
    #             my_allowed_rebate = 0.00
    #             if ex_80_c_id:
    #                 my_investment = sum
    #                 if my_investment <= ex_80_c_id.rebate:
    #                     my_allowed_rebate = my_investment
    #                 else:
    #                     my_allowed_rebate = ex_80_c_id.rebate
    #                 slab_ids = []
    #                 slab_ids.append((0, 0, {
    #                     'slab_id': rec.id,
    #                     'deduction_id': 'slab_80_declaration',
    #                     'it_rule': ex_80_c_id.it_rule.id,
    #                     'saving_master': ex_80_c_id.id,
    #                     'investment': my_investment,
    #                     'allowed_rebate': my_allowed_rebate,
    #                 }))
    #                 emp_id = self.env['declaration.slab'].sudo().search(
    #                     [('saving_master.saving_type', '=', 'Investment in PPF &  Employee’s share of PF contribution'), ('it_rule.code', '=', '80_c'),
    #                      ('slab_id', '=', rec.id)])
    #                 if not emp_id:
    #                     rec.slab_ids = slab_ids
    #             exempt_am = 0.00
    #             std_am = 0.00
    #             sum_pt = 0.00
    #             for std in rec.std_ded_ids:
    #                 std_am += std.allowed_rebate
    #             for ex in rec.exemption_ids:
    #                 exempt_am += ex.allowed_rebate
    #             pr_pt_id = self.env['hr.payslip.line'].sudo().search(
    #                 [('slip_id.employee_id', '=', rec.employee_id.id), ('slip_id.state', '=', 'done'), ('code', '=', 'PTD'),
    #                  ('slip_id.date_from', '>', rec.date_range.date_start),
    #                  ('slip_id.date_to', '<', rec.date_range.date_end)],order ="date_to desc")
    #             for pt in pr_pt_id:
    #                 sum_pt += pt.amount
    #             if (rec.tax_salary_final + rec.previous_employer_income - exempt_am) > 0.00:
    #                 rec.income_after_exemption = round(rec.tax_salary_final + rec.previous_employer_income - exempt_am)
    #             else:
    #                 rec.income_after_exemption = 0.00
    #             sum = 0
    #             for line in rec.dednew_rule_ids:
    #                 sum+=line.investment

    #             if (rec.income_after_exemption - sum) > 0:
    #                 rec.income_after_dednew = rec.income_after_exemption - sum
    #             else:
    #                 rec.income_after_dednew = 0
    #             if rec.income_after_exemption - std_am > 0.00:
    #                 rec.income_after_std_ded = round(rec.income_after_exemption - std_am)
    #             else:
    #                 rec.income_after_std_ded = 0.00
    #             if rec.income_after_std_ded - sum_pt >   0.00:
    #                 rec.income_after_pro_tax = round(rec.income_after_std_ded - sum_pt)
    #             else:
    #                 rec.income_after_pro_tax = 0.00
    #             rec.income_after_pro_tax = round(rec.income_after_std_ded - sum_pt)
    #             if (rec.income_after_pro_tax - rec.total_tds_paid) > 0.00:
    #                 rec.taxable_income = round(rec.income_after_pro_tax - rec.total_tds_paid)
    #             else:
    #                 rec.taxable_income = 0.00
    #             rec.taxable_income = rec.income_after_dednew
    #             employee = self.env['hr.employee'].sudo().search([('id', '=', rec.employee_id.id),
    #                                                               ], limit=1)
    #             years = 30
    #             if employee and employee.birthday:
    #                 years = relativedelta(date.today(), employee.birthday).years
    #             income_slab = self.env['income.tax.newslab'].sudo().search(
    #                 [('salary_from', '<=', rec.taxable_income), ('age_from', '<=', years), ('age_to', '>=', years)],
    #                 order="salary_from")
    #             total_tax_amt = 0
    #             surcharge = 0
    #             cess = 0
    #             if income_slab:
    #                 for inc in income_slab:
    #                     if rec.taxable_income < inc.salary_to:
    #                         tax_amt = (rec.taxable_income - inc.salary_from) * (inc.tax_rate / 100)
    #                         total_tax_amt += tax_amt
    #                         _body = (
    #                             _(" 111 --- {0} - {1} - {2} - {3}").format(rec.taxable_income, inc.salary_from, tax_amt,
    #                                                                        total_tax_amt))
    #                         rec.message_post(body=_body)
    #                     else:
    #                         tax_amt = (inc.salary_to - inc.salary_from) * (inc.tax_rate / 100)
    #                         total_tax_amt += tax_amt
    #                         _body = (
    #                             _(" 222 --- {0} - {1} - {2} - {3}").format(rec.taxable_income, inc.salary_from, tax_amt,
    #                                                                        total_tax_amt))
    #                         rec.message_post(body=_body)
    #                     surcharge = inc.surcharge
    #                     cess = inc.cess
    #             rec.tax_payable = round(total_tax_amt)
    #             income_charge = self.env['income.tax.newcharge'].sudo().search(
    #                 [('salary_from', '<=', rec.taxable_income), ('salary_to', '>=', rec.taxable_income),
    #                  ('age_from', '<=', years), ('age_to', '>=', years)], limit=1
    #             )
    #             if income_charge:
    #                 for inc in income_charge:
    #                     n_sur = (rec.tax_payable * inc.surcharge / 100)
    #                     n_ces = (rec.tax_payable * inc.cess / 100)
    #                     rec.tax_payable += (n_sur + n_ces)
    #                 rec.tax_payable = round(rec.tax_payable)
    #             if rec.tax_payable <= 0.00:
    #                 rec.tax_payable_zero = False
    #                 rec.tax_payable = 0.00
    #             else:
    #                 rec.tax_payable_zero = True
    #             ex_rebate_id = self.env['saving.master'].sudo().search(
    #                 [('saving_type', '=', 'Revised Rebate under Section 87A (2019-20)')],
    #                 limit=1)
    #             my_investment = 0.00
    #             my_allowed_rebate = 0.00
    #             if ex_rebate_id:
    #                 if rec.taxable_income <= 500000:
    #                     my_investment = rec.tax_payable
    #                 else:
    #                     my_investment = 0.00
    #                 if my_investment <= ex_rebate_id.rebate:
    #                     my_allowed_rebate = my_investment
    #                 else:
    #                     my_allowed_rebate = ex_rebate_id.rebate
    #                 rebate_ids = []
    #                 rebate_ids.append((0, 0, {
    #                     'rebate_id': rec.id,
    #                     'it_rule': ex_rebate_id.it_rule.id,
    #                     'saving_master': ex_rebate_id.id,
    #                     'investment': my_investment,
    #                     'allowed_rebate': my_allowed_rebate,
    #                 }))
    #                 rec.rebate_ids = rebate_ids
    #             sum_rbt=0.0
    #             for rbt in rec.rebate_ids:
    #                 sum_rbt += rbt.allowed_rebate
    #             if rec.tax_payable >= sum_rbt:
    #                 rec.tax_payable_after_rebate = rec.tax_payable - sum_rbt
    #                 rec.rebate_received = sum_rbt
    #             else:
    #                 rec.tax_payable_after_rebate = 0.00
    #                 rec.rebate_received = rec.tax_payable
    #             rec.tax_computed_bool = True
    #             rec.sudo().button_payment_tax()
    #     return True

    @api.multi
    def button_payment_tax(self):
        for rec in self:
            rec.tax_payment_ids.filtered(lambda x: not x.paid).unlink()
            edate = rec.date_range.date_end
            print('================edate===================',edate)
            relative_from = date.today().replace(day=1)
            rel_from_tax_rec = rec.tax_payment_ids.filtered(lambda x: x.date == relative_from)
            last_day = int(monthrange(relative_from.year, relative_from.month)[1])
            relative_to = relative_from.replace(day=last_day)
            payslip = self.env['hr.payslip'].sudo().search([('employee_id', '=', rec.employee_id.id),
                                                            ('date_from', '=', relative_from),
                                                            ('date_to', '=', relative_to),
                                                            ('state', '=', 'done')])
            relative_date = relative_from if not payslip and not rel_from_tax_rec\
                                else relative_from + relativedelta(months=1)
            month_cal = (edate.year - relative_date.year) * 12 + (edate.month - relative_date.month)
            print('==================month_cal===============',month_cal)
            if month_cal > 0:
                print('==================rec.pending_tax===============', rec.pending_tax)
                amount = (rec.pending_tax)/month_cal
                print('==================amount===============', amount)
                for _ in range(int(month_cal)):
                    self.env['tax.payment'].create({
                        'tax_payment_id': rec.id,
                        'date': relative_date,
                        'amount': amount,
                    })
                    relative_date += relativedelta(months=1)
        return True


    @api.model
    def create(self, values):
        res = super(HrDeclaration, self).create(values)
        search_id = self.env['hr.declaration'].sudo().search(
            [
                ('employee_id', '=', res.employee_id.id),
                ('state', '!=', 'rejected'),
                ('id', '!=', res.id)
            ])
        for emp in search_id:
            if res.date_range.date_start <= emp.date_range.date_start or res.date_range.date_start >= emp.date_range.date_end:
                if res.date_range.date_end <= emp.date_range.date_start or res.date_range.date_end >= emp.date_range.date_end:
                    if not (
                            res.date_range.date_start <= emp.date_range.date_start and res.date_range.date_end >= emp.date_range.date_end):
                        index = True
                    else:
                        raise ValidationError(
                            "This declaration is already applied for this duration, please correst the dates")
                else:
                    raise ValidationError(
                        "This declaration is already applied for this duration, please correct the dates")
            else:
                raise ValidationError(
                    "This declaration is already applied for this duration, please correct the dates")
        sum = 0
        for lines in res.tax_payment_ids:
            sum += lines.amount
        if sum != res.tax_payable_after_rebate:
            raise ValidationError(
                "Tax payment lines amount must be equal to Tax payable after rebate")
        return res


    @api.constrains('tax_payment_ids')
    def tax_payment_onc(self):
        for res in self:
            sum = 0
            for lines in res.tax_payment_ids:
                sum += lines.amount
            if sum != res.tax_payable_after_rebate:
                raise ValidationError(
                    "Tax payment lines amount must be equal to Tax payable after rebate")



    @api.multi
    def unlink(self):
        for data in self:
            if data.state not in ('draft', 'rejected'):
                raise UserError(
                    'You cannot delete a Tax which is not in draft or Rejected state')
            data.tax_payment_ids.sudo().unlink()
        return super(HrDeclaration, self).unlink()


    @api.multi
    def button_verify(self):
        for data in self:
            data.write({'state': 'verified'})



class StandardDeclarations(models.Model):
    _name = 'declaration.standard'
    _description = 'Declaration Standard'


    std_ded_id = fields.Many2one('hr.declaration', string='Std Deduction')

    # it_rule = fields.Selection([
    #     ('mus10ale', 'U/S 10 '),
    # ], string='IT Rule -Section ')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')
    saving_master = fields.Many2one('saving.master', string='Saving Type')

    investment = fields.Float(string='investment')
    allowed_rebate = fields.Float(string='Total Std. Deduction')



class ExemptionsDeclarations(models.Model):
    _name = 'declaration.exemption'
    _description = 'declaration.exemption'


    exemption_id = fields.Many2one('hr.declaration', string='Exemption')

    # it_rule = fields.Selection([
    #     ('mus10ale', 'U/S 10 '),
    # ], string='IT Rule -Section ')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')
    saving_master = fields.Many2one('saving.master', string='Saving Type', domain=[('it_rule.code', '=', 'mus10ale')])

    investment = fields.Float(string='Amount Received')
    allowed_rebate = fields.Float(string='Total Exemption')




class RebateDeclarations(models.Model):
    _name = 'declaration.rebate'
    _description = 'declaration.rebate'

    rebate_id = fields.Many2one('hr.declaration', string='Rebate')

    # it_rule = fields.Selection([
    #     ('section87a', 'Section 87A '),
    # ], string='IT Rule -Section ')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Investment')
    allowed_rebate = fields.Float(string='Allowed Rebate')


class SlabDeclarations(models.Model):
    _name = 'declaration.slab'
    _description = 'declaration.slab'

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
    ], string='Deduction', default='slab_80_declaration')

    slab_id = fields.Many2one('hr.declaration', string='Slab')

    # it_rule = fields.Selection([
    #     ('80_c', '80 C'),
    #     ('80ccd1', '80CCD (1)'),
    #     ('80ccd1b', '80CCD (1B)'),
    # ], string='IT Rule -Section ')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Investment')
    document = fields.Binary(string='Document')


class Declarations(models.Model):
    _name = 'declaration.hra'
    _description = 'declaration.hra'

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
    ], string='Deduction')

    hra_id = fields.Many2one('hr.declaration', string='HRA')

    # it_rule = fields.Selection([
    #     ('1013a', '10 (13A)'),
    # ], string='IT Rule -Section ')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')
    saving_master = fields.Many2one('saving.master', string='Saving Type')

    investment = fields.Float(string='Investment')
    allowed_rebate = fields.Float(string='Allowed Rebate', compute='compute_allowed_rebate')
    document = fields.Binary(string='Document')



class MedicalDeclarations(models.Model):
    _name = 'declaration.medical'
    _description = 'declaration.medical'

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
    ], string='Deduction', default='Medical Insurance Premium paid')

    med_ins_id = fields.Many2one('hr.declaration', string='Medical')
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    # it_rule = fields.Selection([
    #     ('80d', '80D'),
    # ], string='IT Rule -Section ')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')

    investment = fields.Float(string='Investment')
    document = fields.Binary(string='Document')



class DeductionDeclarations(models.Model):
    _name = 'declaration.deduction'
    _description = 'declaration.deduction'

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
    ], string='Deduction', default='Deductions on Interest on Savings Account')

    deduction_saving_id = fields.Many2one('hr.declaration', string='Deduction Saving')

    # it_rule = fields.Selection([
    #     ('80tta', '80 TTA'),
    #     ('80ttb', '80 TTB'),
    #     ('80gg', '80 GG'),
    #     ('80e', '80E'),
    # ], string='IT Rule -Section ')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')

    saving_master = fields.Many2one('saving.master', string='Saving Type')

    investment = fields.Float(string='Investment')
    document = fields.Binary(string='Document')



class taxhomeDeclarations(models.Model):
    _name = 'declaration.taxhome'
    _description = 'declaration.taxhome'

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
    ], string='Deduction', default='Tax Benefits on Home Loan')

    tax_home_id = fields.Many2one('hr.declaration', string='TaxHome')

    # it_rule = fields.Selection([
    #     ('80C', '80C'),
    #     ('24', '24'),
    #     ('80ee', 'Section 80EE'),
    #     ('80c', '80c'),
    # ], string='IT Rule -Section ')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')
    saving_master = fields.Many2one('saving.master', string='Saving Type')

    investment = fields.Float(string='Investment')
    document = fields.Binary(string='Document')



class taxeducationDeclarations(models.Model):
    _name = 'declaration.taxeducation'
    _description = 'declaration.taxhome'

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
    ], string='Deduction', default='Tax benefit on Education Loan (80E)')

    tax_education_id = fields.Many2one('hr.declaration', string='Tax Education')

    # it_rule = fields.Selection([
    #     ('80E', '80 E'),
    # ], string='IT Rule -Section ')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')
    saving_master = fields.Many2one('saving.master', string='Saving Type')

    investment = fields.Float(string='Investment')
    document = fields.Binary(string='Document')


class rgessDeclarations(models.Model):
    _name = 'declaration.rgess'
    _description = 'declaration.rgess'

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
    ], string='Deduction', default='RGESS')

    rgess_id = fields.Many2one('hr.declaration', string='RGESS')

    # it_rule = fields.Selection([
    #     ('80ccg', '80 CCG'),
    # ], string='IT Rule -Section ')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Investment')
    document = fields.Binary(string='Document')

class dedmedicalDeclarations(models.Model):
    _name = 'declaration.dedmedical'
    _description = 'declaration.dedmedical'

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
    ], string='Deduction', default='Deductions on Medical Expenditure for a Handicapped Relative')

    dedmedical_id = fields.Many2one('hr.declaration', string='DedMedical')

    # it_rule = fields.Selection([
    #     ('80dd', '80 DD'),
    # ], string='IT Rule -Section ')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')
    saving_master = fields.Many2one('saving.master', string='Saving Type')

    investment = fields.Float(string='Investment')
    document = fields.Binary(string='Document')


class dedmedicalselfDeclarations(models.Model):
    _name = 'declaration.dedmedicalself'
    _description = 'declaration.dedmedicalself'

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
    ], string='Deduction', default='Deductions on Medical Expenditure on Self or Dependent Relative')

    dedmedical_self_id = fields.Many2one('hr.declaration', string='Ded Medical Self')
    document = fields.Binary(string='Document')

    # it_rule = fields.Selection([
    #     ('80ddb', '80DDB'),
    #     ('80gg', '80 GG'),
    #     ('us_194_aa', 'u/s 194A'),
    # ], string='IT Rule -Section', default='80ddb')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Investment')


class DonationG(models.Model):
    _name = 'declaration.donation'
    _description = 'Declaration donation'


    deduction_id = fields.Selection([
        ('slab_80_declaration','Slab - 80 Declaration'),
        ('Medical Insurance Premium paid','Medical Insurance Premium paid'),
        ('Deductions on Interest on Savings Account','Deductions on Interest on Savings Account'),
        ('Tax Benefits on Home Loan','Tax Benefits on Home Loan'),
        ('Tax benefit on Education Loan (80E)','Tax benefit on Education Loan (80E)'),
        ('RGESS','RGESS'),
        ('Deductions on Medical Expenditure for a Handicapped Relative','Deductions on Medical Expenditure for a Handicapped Relative'),
        ('Deductions on Medical Expenditure on Self or Dependent Relative','Deductions on Medical Expenditure on Self or Dependent Relative'),
        ('Deductions on Donations','Deductions on Donations'),
    ],string='Deduction',default='Deductions on Donations')

    deddonation_id = fields.Many2one('hr.declaration', string='Donation')
    document = fields.Binary(string='Document')
    # it_rule = fields.Selection([
    #     ('section80g', 'Section 80G'),
    # ], string='IT Rule -Section', default='section80g')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    saving_master_related = fields.Char(related='saving_master.saving_type', string='Saving Type Related')
    investment = fields.Float(string='Amount')
    other = fields.Char('Other(If any)')



class DeductionNew(models.Model):
    _name = 'declaration.80c.newded'
    _description = 'Declaration New Deduction'


    deduction_id = fields.Selection([
        ('slab_80_declaration','Slab - 80 Declaration'),
        ('Medical Insurance Premium paid','Medical Insurance Premium paid'),
        ('Deductions on Interest on Savings Account','Deductions on Interest on Savings Account'),
        ('Tax Benefits on Home Loan','Tax Benefits on Home Loan'),
        ('Tax benefit on Education Loan (80E)','Tax benefit on Education Loan (80E)'),
        ('RGESS','RGESS'),
        ('Deductions on Medical Expenditure for a Handicapped Relative','Deductions on Medical Expenditure for a Handicapped Relative'),
        ('Deductions on Medical Expenditure on Self or Dependent Relative','Deductions on Medical Expenditure on Self or Dependent Relative'),
        ('Deductions on Donations','Deductions on Donations'),
        ('Deduction - Pension Scheme under section 80CCD(2)', 'Deduction - Pension Scheme under section 80CCD(2)'),
    ],string='Deduction',default='Deduction - Pension Scheme under section 80CCD(2)')

    dednew_rule_id = fields.Many2one('hr.declaration', string='Donation')
    document = fields.Binary(string='Document')
    # it_rule = fields.Selection([
    #     ('section80g', 'Section 80G'),
    # ], string='IT Rule -Section', default='section80g')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    saving_master_related = fields.Char(related='saving_master.saving_type', string='Saving Type Related')
    investment = fields.Float(string='Amount')


class IncomeHouse(models.Model):
    _name = 'income.house'
    _description = 'Income from House'

    income_house_id = fields.Many2one('hr.declaration', string='Income from House Property')
    document = fields.Binary(string='Document')
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
    ], string='Deduction', default='Income from House Property')
    # it_rule = fields.Selection([
    #     ('income_house', 'Income from House Property')
    # ], string='IT Rule -Section', default='income_house')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    investment = fields.Float(string='Amount')


    @api.constrains('saving_master')
    def check_unique_saving(self):
        for rec in self:
            count = 0
            emp_id = self.env['income.house'].sudo().search(
                [('saving_master', '=', rec.saving_master.id), ('income_house_id', '=', rec.income_house_id.id)])
            for e in emp_id:
                count += 1
            if count > 1:
                raise ValidationError("Income from House Property")

class IncomeOther(models.Model):
    _name = 'income.other'
    _description = 'Income from other Sources'

    income_other_id = fields.Many2one('hr.declaration', string='Income from other Sources')
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
    ], string='Deduction', default='Income from Other Sources')
    document = fields.Binary(string='Document')
    # it_rule = fields.Selection([
    #     ('income_other', 'Income from other Sources')
    # ], string='IT Rule -Section', default='income_other')
    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')
    saving_master = fields.Many2one('saving.master', string='Saving Type')
    saving_master_related = fields.Char(related='saving_master.saving_type', string='Saving Type Related')
    investment = fields.Float(string='Amount')
    other = fields.Char('Other(If any)')


    @api.constrains('saving_master')
    def check_unique_saving(self):
        for rec in self:
            count = 0
            emp_id = self.env['income.other'].sudo().search(
                [('saving_master', '=', rec.saving_master.id), ('income_other_id', '=', rec.income_other_id.id)])
            for e in emp_id:
                count += 1
            if count > 1:
                raise ValidationError("Income from other Sources Type must be unique")


class SavingsMaster(models.Model):
    _name = 'saving.master'
    _description = 'Saving Master'

    @api.constrains('is_percent_req', 'percent')
    def check_percent(self):
        if self.is_percent_req and self.percent == 0:
            raise ValidationError('Please set percent value as percent required is checked.')

    # deduction_id = fields.Selection([
    #     ('slab_80_declaration','Slab - 80 Declaration'),
    #     ('Medical Insurance Premium paid','Medical Insurance Premium paid'),
    #     ('Deductions on Interest on Savings Account','Deductions on Interest on Savings Account'),
    #     ('Tax Benefits on Home Loan','Tax Benefits on Home Loan'),
    #     ('Tax benefit on Education Loan (80E)','Tax benefit on Education Loan (80E)'),
    #     ('RGESS','RGESS'),
    #     ('Deductions on Medical Expenditure for a Handicapped Relative','Deductions on Medical Expenditure for a Handicapped Relative'),
    #     ('Deductions on Medical Expenditure on Self or Dependent Relative','Deductions on Medical Expenditure on Self or Dependent Relative'),
    #     ('Deductions on Donations','Deductions on Donations'),
    # ],string='Deduction')
    # it_rule = fields.Selection([
    #     ('mus10ale', 'U/S 10 '),
    #     ('section87a', 'Section 87A '),
    #     ('80_c', '80 C'),
    #     ('80ccd1', '80CCD (1)'),
    #     ('80ccd1b', '80CCD (1B)'),
    #     ('1013a', '10 (13A)'),
    #     ('80d', '80D'),
    #     ('80tta', '80 TTA'),
    #     ('80ttb', '80 TTB'),
    #     ('80gg', '80 GG'),
    #     ('80e', '80E'),
    #     ('80C', '80C'),
    #     ('24', '24'),
    #     ('80ee', 'Section 80EE'),
    #     ('80c', '80c'),
    #     ('80E', '80 E'),
    #     ('80ccg', '80 CCG'),
    #     ('80dd', '80 DD'),
    #     ('80ddb', '80DDB'),
    #     ('section80g', 'Section 80G'),
    #     ('80gg', '80 GG'),
    #     ('us_194_aa', 'u/s 194A'),
    #     ('income_house', 'Income from House Property'),
    #     ('income_other', 'Income from other Sources'),
    # ], string='IT Rule -Section ')

    it_rule = fields.Many2one('hr.itrule', string='IT Rule -Section')
    saving_type = fields.Char('Saving Type')
    description = fields.Text('Description')
    rebate = fields.Float('Max. Allowed Limit', store=True)
    is_percent_req = fields.Boolean('Percent required', default=False)
    percent = fields.Float('Percent')
    with_max_limit = fields.Boolean('With Max Limit', default=False)


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



class RentPaid(models.Model):
    _name = 'rent.paid'
    _description = 'Rent Paid'


    rent_paid_id = fields.Many2one('hr.declaration', string='Rent Paid')
    date_from = fields.Date(string='Date from')
    date_to = fields.Date(string='Date to')
    amount = fields.Float(string='Amount')
    attchment = fields.Binary(string='Attachment')

    @api.constrains('date_from','date_to')
    def validate_date_f_t(self):
        for rec in self:
            if rec.date_from and rec.rent_paid_id.date_range.date_start and rec.rent_paid_id.date_range.date_end:
                if rec.date_from < rec.rent_paid_id.date_range.date_start or rec.date_from > rec.rent_paid_id.date_range.date_end:
                    raise ValidationError(
                                "From Date must be within Financial year selected")
            if rec.date_to and rec.rent_paid_id.date_range.date_start and rec.rent_paid_id.date_range.date_end:
                if rec.date_to < rec.rent_paid_id.date_range.date_start or rec.date_to > rec.rent_paid_id.date_range.date_end:
                    raise ValidationError(
                                "To Date must be within Financial year selected")
            if rec.date_from and rec.date_to:
                if rec.date_from > rec.date_to:
                    raise ValidationError(
                        "From Date must be less than To Date - Rent Paid")




class TaxPayment(models.Model):
    _name = 'tax.payment'
    _description = 'Tax Payment'

    tax_payment_id = fields.Many2one('hr.declaration', string='Tax Payment')
    payslip_id = fields.Many2one('hr.payslip')
    date = fields.Date(string='Date')
    amount = fields.Float(string='Amount')
    paid = fields.Boolean(string="Paid")
    mona_payslip_id = fields.Many2one('hr.payslip')
    branch_id = fields.Many2one('res.branch', 'Center')

    # tax_payslip_id = fields.Many2one('hr.payslip', string='Tax Payment Payslip')
    # payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.")
    # tax_payslip_ref_id = fields.Many2one('hr.payslip', string="Payslip Ref.")
    # employee_id = fields.Many2one('hr.employee', string="Employee Ref.")
    #
    # @api.constrains('tax_payment_id')
    # def _select_emp_from_m2o(self):
    #     for rec in self:
    #         rec.employee_id = rec.tax_payment_id.employee_id.id

