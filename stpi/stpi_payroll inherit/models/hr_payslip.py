from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from math import floor
from datetime import date, datetime, time
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from odoo.addons.reimbursement_stpi.models.reimbursement_main import calculate_days


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'


    """
    Logic :-
    EPS = 8.33% of BASIC + DA
    CPF = 12% of BASIC + DA - EPS
    HPL = {(((BASIC + DA) / month_days)* 0.5} * Number of HPL)

    PF Exceptions :-
    * Once an employee reaches to 58 Years of age EPS amount stops deducting and 
    entire amount will be deposited aganist the CPF contribution. 
    * If an employee joins after Sept. 2014 (as a fresher only) then EPS contribution 
    should not be deducted and entire amount will be deposited aganist his/her CPF account.

    CCL Conditions :-
    If an employee takes more than 365 days of CCL leave then for exceeding number days will have 20% deduction of BASIC + DA
    * If CCL count is 365 before payslip from date then deduction will be for number leave taken in that month
    * If CCL count is not 365 before payslip from date but it is 365+ before payslip to date then deduction will be 
    for total_ccl_leave - ccl_before_payslip_from_date

    CCL Calculation:-
    * First calculate current month CCL leave.
    * Check how much CCL leaves has taken till payslip to date
    * If total ccl leave is more than 365 days, deduction will be done for current month CCL leave.
    """

    def get_arrear(self, payslip, basic_da_arrear=None):
        domain = [('employee_id', '=', payslip.employee_id),
                    ('state', '=', 'confirm')]
        if basic_da_arrear:
            domain += [('arrear_type', 'in', ('basic_inc', 'da_inc')), 
                        ('confirm_date', '>=', payslip.date_from),
                        ('confirm_date', '<=', payslip.date_to)]
        else:
            domain += [('arrear_type', 'in', ('dr', 'promotion')),
                        ('date_from', '=', payslip.date_from),
                        ('date_to', '=', payslip.date_to)]
        arrear = self.env['arrear.arrear'].search(domain)
        return arrear

    def calculate_employee_age(self,employee):
        dob = employee.birthday
        current_date = fields.Date.today()
        age = floor((abs(current_date - dob).days) / 365)
        return age
    
    def check_fresher(self,employee):
        pfObj = self.env['pf.employee'].sudo().search([('employee_id', '=', employee.id)])
        
        # is_fresher = False

        # doj = employee.date_of_join
        # if doj > date(2014, 9, 30):
        #     if pfObj.pf_start_data:
        #         if pfObj.pf_start_data >= doj:
        #             is_fresher = True
        #     else:
        #         raise ValidationError(f'Please set PF start date for {employee.name}')
            # try:
            #     # import pdb;pdb.set_trace();
            #     if pfObj.pf_start_data:
            #         if pfObj.pf_start_data >= doj:
            #             is_fresher = True
            #     else:
            #         raise UserError(f'Please set PF start date for {employee.name}')
            # except UserError as err:
            #     return {'warning': {
            #         'title': _('Warning'),
            #         'message': _(str(err))
            #     }}
        return False if pfObj.eps_deduct else True

    # Case - 1 If an employee joins mid of the month then eps amount will be calculated for the mid month
    # Case - 2 If an employee ages 58 then eps amount will be calculated till mid month
    def check_mid_month_eps_factor(self, empObj,  payslip=None, **kwargs):
        employee_age_58 = empObj.birthday + relativedelta(years=58)
        if payslip:
            mid_month_join = payslip.date_from >= empObj.date_of_join <= payslip.date_to
            mid_month_age = payslip.date_from >= employee_age_58 <= payslip.date_to
            mid_month_leave = payslip.date_from >= empObj.last_working_date <= payslip.date_to\
                                        if empObj.last_working_date else False
            if mid_month_age:
                no_of_days = (payslip.date_from - employee_age_58).days
            if mid_month_join:
                no_of_days = (payslip.date_to - empObj.date_of_join).days
            if mid_month_leave:
                no_of_days = (empObj.last_working_date - payslip.date_from).days
            if mid_month_join and mid_month_leave:
                no_of_days = (empObj.last_working_date - empObj.date_of_join).days
        else:
            date_from, date_to = kwargs.get('date_from'), kwargs.get('date_to')
            mid_month_join = date_from >= empObj.date_of_join <= date_to
            mid_month_age = date_from >= employee_age_58 <= date_to
            mid_month_leave = date_from >= empObj.last_working_date <= date_to\
                                    if empObj.last_working_date else False
            if mid_month_age:
                no_of_days = (date_from - employee_age_58).days
            if mid_month_join:
                no_of_days = (date_to - empObj.date_of_join).days
            if mid_month_leave:
                no_of_days = (empObj.last_working_date - date_from).days
            if mid_month_join and mid_month_leave:
                no_of_days = (empObj.last_working_date - empObj.date_of_join).days
        return no_of_days + 1

    def default_eps_calculation(self, empObj, BASIC, DA, payslip=None, **kwargs):
        if payslip:
            eps_per_day = (0.0833 * (BASIC+DA)) / self.calculate_month_days(payslip.date_to)
            no_of_days = self.check_mid_month_eps_factor(empObj, payslip=payslip)
            if not no_of_days:
                result = min((eps_per_day * no_of_days), 1250)
            else:
                result = min((0.0833 * (BASIC+DA)), 1250)
        else:
            eps_per_day = (0.0833 * (BASIC+DA)) / self.calculate_month_days(kwargs.get('date_to'))
            no_of_days = self.check_mid_month_eps_factor(empObj, date_from=kwargs.get('date_from'), 
                                                            date_to=kwargs.get('date_to'))
            if not no_of_days:
                result = min((eps_per_day * no_of_days), 1250)
            else:
                result = min((0.0833 * (BASIC+DA)), 1250)
        return result 

    def calculate_eps(self, employee_id, BASIC, DA, payslip=None, **kwargs):
        empObj = self.env['hr.employee'].browse(employee_id)
        age = self.calculate_employee_age(empObj)
        is_fresher = self.check_fresher(empObj)
        if payslip:
            arrear = self.get_arrear(payslip)
            if arrear:
                result = sum(arrear.arrear_due_ids.mapped('eps_amount'))
            else:
                if age > 58 or is_fresher:
                    result = 0
                else:
                    result = self.default_eps_calculation(empObj, BASIC, DA, payslip=payslip)
        else:
            if age > 58 or is_fresher:
                result = 0
            else:
                result = self.default_eps_calculation(empObj, BASIC, DA, date_from=kwargs.get('date_from'), 
                                                            date_to=kwargs.get('date_to'))
        return result

    def calculate_month_days(self, date_to):
        y, m = date_to.year, date_to.month
        days = monthrange(y, m)[1]
        return days

    def calculate_hp_deduction(self, payslip, BASIC, DA):
        result = 0
        relative_from = (payslip.date_from - relativedelta(months=1)).replace(day=26)
        relative_to = payslip.date_from.replace(day=25)
        num_days = (relative_to - relative_from).days
        hplLeaveCount = len(self.env['hr.leave'].sudo().get_employee_leave_detail('HPL', payslip.employee_id,
                                                                            relative_from, relative_to).get('days'))
        if hplLeaveCount:
            result = (((BASIC + DA) / num_days) * 0.5) * hplLeaveCount

        return result

    def calculate_ccl_deduction(self, payslip, BASIC, DA):
        result = 0
        employee_id = self.env['hr.employee'].sudo().browse(payslip.employee_id)
        relative_from = (payslip.date_from - relativedelta(months=1)).replace(day=26)
        relative_to = payslip.date_from.replace(day=25)
        num_days = (relative_to - relative_from).days + 1

        # Current month CCL leave
        currentMonthCCLleave = len(self.env['hr.leave'].sudo().get_employee_leave_detail('CCL', payslip.employee_id,
                                                                            relative_from, relative_to).get('days'))
        # CCL Leave till payslip to date
        CCLTillFromDate = len(self.env['hr.leave'].sudo().get_employee_leave_detail('CCL', payslip.employee_id, 
                                                                            employee_id.date_of_join, relative_from).get('days'))
        totalCCLleave = currentMonthCCLleave + CCLTillFromDate

        if CCLTillFromDate >= 365:
            result = currentMonthCCLleave * (((BASIC + DA) * 0.20) / num_days)
        else:
            if totalCCLleave > 365:
                result = (totalCCLleave - 365) * (((BASIC + DA) * 0.20) / num_days)
        return result

    def calculate_prof_tax_deduction(self, payslip, GROSS):
        result = 0
        deduction_month = payslip.date_to.month
        profTaxObj = self.env['hr_payslip_prof_tax'].sudo().search([('state_id', '=', payslip.branch_id.state_id.id),
                                                                    ('gross_from', '<=', GROSS),
                                                                    ('gross_to', '>=', GROSS)])
        deduction_amount = profTaxObj.prof_monthly_deduct if deduction_month != 3 else profTaxObj.prof_last_month_deduct

        if profTaxObj:
            if profTaxObj.state_id.code.lower() != 'mh':
                result = deduction_amount
            else:
                empObj = self.env['hr.employee'].sudo().browse(payslip.employee_id)
                if 7501 <= GROSS <= 10000:
                    if empObj.gende == 'female':
                        result = 0
                    else:
                        result = deduction_amount
                else:
                    result = deduction_amount

        return result

    def calculate_pmrf_deduction(self, payslip, BASIC, DA):
        result = 0
        pmrf_deduct_days = self.env['ir.config_parameter'].sudo().get_param('hr_payslip.pmrf_deduct_days')
        cur_month_days = self.calculate_month_days(payslip.date_to)

        try:
            if pmrf_deduct_days:
                result = ((BASIC + DA) / cur_month_days) * float(pmrf_deduct_days)
            else:
                raise ValidationError('Please set PMRF deduction days first!')
        except ValueError as err:
            raise ValidationError(f'{str(err).capitalize()}\n Please set correct value of PMRF deduction days in configuration.')

        return result

    def calculate_ta(self, contract, payslip=None):
        result = 0
        if payslip:
            arrear = self.get_arrear(payslip)
            if arrear:
                result = sum(arrear.arrear_due_ids.mapped('ta_amount'))
            else:
                if ((contract.city_tier != 'other') and (contract.pay_level_id.name in ['Pay Level 9','Pay Level 10','Pay Level 11',
                                                                                    'Pay Level 12','Pay Level 13','Pay Level 13A',
                                                                                    'Pay Level 14','Pay Level 15','Pay Level 16',
                                                                                    'Pay Level 17','Pay Level 18'])):
                    result = 7200+(7200*contract.da/100)
                elif ((contract.city_tier != 'other') and (contract.pay_level_id.name in ['Pay Level 3','Pay Level 4','Pay Level 5',
                                                                                            'Pay Level 6','Pay Level 7','Pay Level 8'])):
                    result = 3600+(3600*contract.da/100)
                elif ((contract.city_tier != 'other') and (contract.pay_level_id.name in ['Pay Level 1','Pay Level 2'])):
                    if contract.wage >= 24200:
                        result = 3600+(3600*contract.da/100)
                    else:
                        result = 1350 + (1350*(contract.da/100))
                elif ((contract.city_tier == 'other') and (contract.pay_level_id.name in ['Pay Level 9','Pay Level 10','Pay Level 11',
                                                                                            'Pay Level 12','Pay Level 13','Pay Level 13A',
                                                                                            'Pay Level 14','Pay Level 15','Pay Level 16',
                                                                                            'Pay Level 17','Pay Level 18'])):
                    result = 3600 + (3600*(contract.da/100))
                elif ((contract.city_tier == 'other') and (contract.pay_level_id.name in ['Pay Level 3','Pay Level 4','Pay Level 5',
                                                                                            'Pay Level 6','Pay Level 7','Pay Level 8'])):
                    result = 1800+ (1800*(contract.da/100))
                elif ((contract.city_tier == 'other') and (contract.pay_level_id.name in ['Pay Level 1','Pay Level 2'])):
                    if contract.wage >= 24200:
                        result = 1800+ (1800*(contract.da/100))
                    else:
                        result = 900 + (900*(contract.da/100))
                else:
                    result = 101
                employee_id = self.env['hr.employee'].browse(payslip.employee_id)
                join_dt, last_dt = employee_id.date_of_join, employee_id.last_working_date if employee_id.last_working_date else payslip.date_to
                dt_from, dt_to = payslip.date_from, payslip.date_to
                present_days = calculate_days(join_dt, last_dt, dt_from, dt_to)
                ta_per_day = result/((dt_to - dt_from).days + 1)
                result = ta_per_day * present_days
        else:
            if ((contract.city_tier != 'other') and (contract.pay_level_id.name in ['Pay Level 9','Pay Level 10','Pay Level 11',
                                                                                    'Pay Level 12','Pay Level 13','Pay Level 13A',
                                                                                    'Pay Level 14','Pay Level 15','Pay Level 16',
                                                                                    'Pay Level 17','Pay Level 18'])):
                result = 7200+(7200*contract.da/100)
            elif ((contract.city_tier != 'other') and (contract.pay_level_id.name in ['Pay Level 3','Pay Level 4','Pay Level 5',
                                                                                        'Pay Level 6','Pay Level 7','Pay Level 8'])):
                result = 3600+(3600*contract.da/100)
            elif ((contract.city_tier != 'other') and (contract.pay_level_id.name in ['Pay Level 1','Pay Level 2'])):
                if contract.wage >= 24200:
                    result = 3600+(3600*contract.da/100)
                else:
                    result = 1350 + (1350*(contract.da/100))
            elif ((contract.city_tier == 'other') and (contract.pay_level_id.name in ['Pay Level 9','Pay Level 10','Pay Level 11',
                                                                                        'Pay Level 12','Pay Level 13','Pay Level 13A',
                                                                                        'Pay Level 14','Pay Level 15','Pay Level 16',
                                                                                        'Pay Level 17','Pay Level 18'])):
                result = 3600 + (3600*(contract.da/100))
            elif ((contract.city_tier == 'other') and (contract.pay_level_id.name in ['Pay Level 3','Pay Level 4','Pay Level 5',
                                                                                        'Pay Level 6','Pay Level 7','Pay Level 8'])):
                result = 1800+ (1800*(contract.da/100))
            elif ((contract.city_tier == 'other') and (contract.pay_level_id.name in ['Pay Level 1','Pay Level 2'])):
                if contract.wage >= 24200:
                    result = 1800+ (1800*(contract.da/100))
                else:
                    result = 900 + (900*(contract.da/100))
            else:
                result = 101
        return result

    def calculate_hra(self, contract, payslip=None):
        result = 0
        if payslip:
            arrear = self.get_arrear(payslip)
            if arrear:
                result = sum(arrear.arrear_due_ids.mapped('hra_amount'))
            else:
                if contract.employee_hra_cat == 'x':
                    if contract.da > 50:
                        result = 0.3 * contract.wage
                    elif contract.da > 25:
                        result = 0.27 * contract.wage
                    else:
                        result = 0.24 * contract.wage
                    result = result if result > 5400 else 5400
                elif contract.employee_hra_cat == 'y':
                    if contract.da > 50:
                        result = 0.2 * contract.wage
                    elif contract.da > 25:
                        result = 0.18 * contract.wage
                    else:
                        result = 0.16 * contract.wage
                    result = result if result > 3600 else 3600
                elif contract.employee_hra_cat == 'z':
                    if contract.da > 50:
                        result = 0.1 * contract.wage
                    elif contract.da > 25:
                        result = 0.09 * contract.wage
                    else:
                        result = 0.08 * contract.wage
                    result = result if result > 1800 else 1800
                else:
                    result = 0
        else:
            if contract.employee_hra_cat == 'x':
                if contract.da > 50:
                    result = 0.3 * contract.wage
                elif contract.da > 25:
                    result = 0.27 * contract.wage
                else:
                    result = 0.24 * contract.wage
                result = result if result > 5400 else 5400
            elif contract.employee_hra_cat == 'y':
                if contract.da > 50:
                    result = 0.2 * contract.wage
                elif contract.da > 25:
                    result = 0.18 * contract.wage
                else:
                    result = 0.16 * contract.wage
                result = result if result > 3600 else 3600
            elif contract.employee_hra_cat == 'z':
                if contract.da > 50:
                    result = 0.1 * contract.wage
                elif contract.da > 25:
                    result = 0.09 * contract.wage
                else:
                    result = 0.08 * contract.wage
                result = result if result > 1800 else 1800
            else:
                result = 0

        return result

    def calculate_tds_till_date(self, payslip, TDS):
        ## FIXME: Uncomment this after TDS module is live
        # date_range_id = self.env['date.range'].sudo().search([('date_start', '<=', payslip.date_from),
        #                                                         ('date_end', '>=', payslip.date_to),
        #                                                         ('tds', '=', True)])
        # tds = self.env['hr.declaration'].sudo().search([('employee_id', '=', payslip.employee_id),
        #                                                     ('date_range', '=', date_range_id.id)])
        # result = sum(tds.tax_payment_ids.filtered(lambda x: x.paid).mapped('amount'))
        result = 0
        payslips = self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id), 
                                                    ('date_to', '<=', payslip.date_from),
                                                    ('state', '=', 'done')])
        for pay in payslips:
            result += sum(pay.line_ids.filtered(lambda x: x.code == 'TDS').mapped('amount'))


        result += TDS
        return result

    def calculate_basic(self, payslip, contract):
        arrear = self.get_arrear(payslip)
        if arrear:
            result = sum(arrear.arrear_due_ids.mapped('basic_amount'))
        else:
            employee_id = self.env['hr.employee'].browse(payslip.employee_id)
            join_dt, last_dt = employee_id.date_of_join, employee_id.last_working_date if employee_id.last_working_date else payslip.date_to
            dt_from, dt_to = payslip.date_from, payslip.date_to
            present_days = calculate_days(join_dt, last_dt, dt_from, dt_to)
            basic_per_day = contract.wage/((dt_to - dt_from).days + 1)
            result = present_days * basic_per_day
        return result

    def calculate_misc_allowence_deduction(self, payslip, code=None):
        result = 0
        if code:
            misc_allowence_deduct_id = self.env['misc.allowance.deduct']\
                                            .search([('salary_rule_id.code', '=', code),
                                                        ('employee_id', '=', payslip.employee_id),
                                                        ('date', '>=', payslip.date_from),
                                                        ('date', '<=', payslip.date_to)])
            result = sum(misc_allowence_deduct_id.mapped('amount'))
        return result

    def calculate_arrear(self, payslip):
        result = 0
        arrear = self.get_arrear(payslip, basic_da_arrear=True)
        if arrear:
            result = sum(arrear.arrear_payable_ids.mapped('diff_total_arrear_amount'))
        return result

    def calculate_mpf(self, BASIC, DA, ARRE, payslip):
        result = (0.12 * (BASIC+DA))
        employee_id = self.env['hr.employee'].browse(payslip.employee_id)
        if employee_id.state == 'deputation':
            result = self.env['misc.allowance.deduct'].sudo().search([('salary_rule_id.code', '=', 'MPF'),
                                                                    ('employee_id', '=', payslip.employee_id),
                                                                    ('date', '>=', payslip.date_from),
                                                                    ('date', '<=', payslip.date_to)], limit=1).amount
        else:
            if ARRE:
                arrear = self.get_arrear(payslip, basic_da_arrear=True)
                result += sum(arrear.arrear_payable_ids.
                                                    mapped('diff_mpf_amount'))
            else:
                arrear = self.get_arrear(payslip)
                if arrear:
                    result = sum(arrear.arrear_due_ids.mapped('mpf_amount'))
        return result

    def calculate_epf(self, MPF, EPS, ARRE, payslip):
        result = (MPF - EPS)
        employee_id = self.env['hr.employee'].browse(payslip.employee_id)
        if employee_id.state == 'deputation':
            result = self.env['misc.allowance.deduct'].sudo().search([('salary_rule_id.code', '=', 'EPF'),
                                                                    ('employee_id', '=', payslip.employee_id),
                                                                    ('date', '>=', payslip.date_from),
                                                                    ('date', '<=', payslip.date_to)], limit=1).amount
        else:
            if ARRE:
                arrear = self.get_arrear(payslip, basic_da_arrear=True)
                result += sum(arrear.arrear_payable_ids.
                                                    mapped('diff_mpf_amount'))
            else:
                arrear = self.get_arrear(payslip)
                if arrear:
                    result = sum(arrear.arrear_due_ids.mapped('mpf_amount'))
        return result

    def calculate_da(self, contract, BASIC, payslip):
        result = ((contract.da/100) * BASIC)
        ARRE = self.calculate_arrear(payslip)
        if ARRE:
            arrear = self.get_arrear(payslip, basic_da_arrear=True)
            result += sum(arrear.arrear_payable_ids.
                                                mapped('diff_da_amount'))
        else:
            arrear = self.get_arrear(payslip)
            if arrear:
                result = sum(arrear.arrear_due_ids.mapped('da_amount'))
        return result
