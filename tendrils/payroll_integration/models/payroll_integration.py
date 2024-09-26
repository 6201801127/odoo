from odoo import fields, models, api
import datetime
from datetime import datetime, date
import xlsxwriter, random, string
from odoo.exceptions import UserError, ValidationError
import requests
import math
import secrets
from dateutil.relativedelta import relativedelta
# from odoo.tools.profiler import profile



class payroll_integration(models.Model):
    _inherit = 'hr.payslip'

    # _description = 'Payroll Timesheet Deduction'

    def round_up_to_nearest_100(self, num):
        return round(num / 100) * 100

    # @api.multi
    # def calculate_salary_advance(self, payslipid):
    #     payslip_rec = self.env['hr.payslip'].sudo().search([('id', '=', payslipid)])
    #     date_to = payslip_rec.date_to
    #     advance_amount,amount = 0,0
    #     attendance_report = self.env['kw_payroll_monthly_attendance_report'].sudo().search(
    #             [('attendance_year', '=', date_to.year), ('attendance_month', '=', date_to.month),
    #              ('employee_id', '=', payslip_rec.employee_id.id),('zero_payslip_boolean','=',True)])
    #     if attendance_report:
    #         amount = 0
    #     else:
    #         salary_rec = self.env['kw_advance_apply_salary_advance'].sudo().search(
    #             [('employee_id', '=', payslip_rec.employee_id.id), ('state', '=', 'release')])
    #         if salary_rec:
    #             for rec in salary_rec:
    #                 deduction_rec = rec.deduction_line_ids.filtered(lambda r: r.status == 'draft' and r.deduction_date.month == date_to.month and r.deduction_date.year == date_to.year).mapped("amount")
    #                 advance_amount += sum(deduction_rec)
    #                 amount = self.calculate_round_amount(advance_amount)
    #     return amount
    
    @api.multi
    # @profile
    def calculate_salary_advance(self, payslipid,employee_id,date_to,date_start,year,month):
        amount = 0
        self.env.cr.execute(f"select id from kw_payroll_monthly_attendance_report where attendance_year={year} and attendance_month = {month} and employee_id = {employee_id} and (zero_payslip_boolean is null or zero_payslip_boolean is false)")
        attendance_info = self._cr.dictfetchall()
        if not attendance_info: 
            return 0
        else:
            advance_amt_dict = {}
            self.env.cr.execute(f"select id from kw_advance_apply_salary_advance where state='release' and employee_id={employee_id}")
            advance_dict = self._cr.dictfetchall()
            id_values = [d['id'] for d in advance_dict]
            if advance_dict:
                advance = tuple(id_values)
                if len(advance) > 1:
                    self.env.cr.execute(f"select sum(amount) as installment from kw_advance_deduction_line where status = 'draft' and deduction_id in {advance} and deduction_date between '{date_start}' and '{date_to}' and (is_preclosure is null or is_preclosure is false)")
                    advance_amt_dict = self._cr.dictfetchall()
                elif len(advance) == 1:
                    self.env.cr.execute(f"select sum(amount) as installment from kw_advance_deduction_line where status = 'draft' and deduction_id = {advance_dict[0]['id']} and deduction_date between '{date_start}' and '{date_to}' and (is_preclosure is null or is_preclosure is false)")
                    advance_amt_dict = self._cr.dictfetchall()
                if advance_amt_dict:
                    amount = self.calculate_round_amount(advance_amt_dict[0]['installment'] if advance_amt_dict[0]['installment'] else 0)
        return amount

    @api.multi
    def action_payslip_done(self):
        query=''
        for payslip in self:
            payslip.write({
                'salary_confirm_year': int(payslip.date_to.year),
                'salary_confirmation_month': int(payslip.date_to.month),
                'department_id': payslip.employee_id.department_id.id,
                'employement_type':payslip.employee_id.employement_type.id,
                'branch_id': payslip.employee_id.base_branch_id.id
            })
           
            payroll_report = self.env['kw_payroll_monthly_attendance_report'].sudo().search(
                [('attendance_year', '=', payslip.date_to.year), ('attendance_month', '=', payslip.date_to.month),
                 ('employee_id', '=', payslip.employee_id.id)])
            if payroll_report:
                query += f"update kw_payroll_monthly_attendance_report set boolean_readonly = true where id={payroll_report.id};"
            ir_config_params = self.env['ir.config_parameter'].sudo()
            enable_el_deduction = ir_config_params.get_param('payroll_inherit.check_el_deduction') or False
            if enable_el_deduction != False:
                if payroll_report.timesheet_el_deduct_in_day > 0:
                    self.env['hr.leave.allocation'].lapse_el_timesheet_integration(payroll_report.employee_id.id, 'EL',payroll_report.timesheet_el_deduct_in_day)
            
            month_dict = {'January': 1,'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7,
                                  'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
            health_dependant = self.env['health_insurance_dependant'].sudo().search(
                    [('employee_id', '=', payslip.employee_id.id),
                        ('state', '=', 'approved')],order='id desc', limit=1)
            hid_amt = 0
            if payslip.line_ids.filtered(lambda x:x.code == 'HID' and x.amount > 0):
                if len(health_dependant) > 0:
                    deduction_rec = health_dependant.emi_details_ids.filtered(lambda r: r.status == 'unpaid' and  int(payslip.date_to.month) == month_dict.get(r.month) and r.year == int(payslip.date_to.year))
                    hid_amt +=  deduction_rec.installment
                    if self.calculate_round_amount(hid_amt) == self.calculate_round_amount(payslip.line_ids.filtered(lambda x:x.code == 'HID').amount):
                        if payroll_report.zero_payslip_boolean == False:
                            deduction_rec.write({'status': 'paid'})
                            if health_dependant.boolean_readonly == False:
                                health_dependant.times_of_ded += 1
                            if health_dependant.times_of_ded == health_dependant.no_of_installment:
                                health_dependant.write({'boolean_readonly': True,'state':'closed'})
            
            elif payroll_report.zero_payslip_boolean == True and payslip.line_ids.filtered(lambda x:x.code == 'HID' and x.amount == 0):
                if payslip.line_ids.filtered(lambda x:x.code == 'HID' and x.amount == 0):
                    month_numb = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
                    emi_rec = self.env['health_insurance_emi'].sudo()
                    max_date_rec = emi_rec.search([('emi_details_id','=',health_dependant.id)],order='emi_date desc',limit=1)
                    current_emi_rec = emi_rec.search([('emi_date' ,'>=',payslip.date_from),('emi_date','<=', payslip.date_to),('emi_details_id','=',health_dependant.id)],limit=1)
                    max_date = max_date_rec.emi_date + relativedelta(months=1)
                    current_emi_rec.write({'emi_date':max_date,'year':max_date.year,'month': month_numb.get(max_date.month)})
           
            salary_rec = self.env['kw_advance_apply_salary_advance'].sudo().search(
                    [('employee_id', '=', payslip.employee_id.id), ('state', '=', 'release')])
            if payslip.line_ids.filtered(lambda x:x.code == 'SALADV' and x.amount > 0):
                if salary_rec:
                    for adv in salary_rec:
                        deduction_rec = adv.deduction_line_ids.filtered(lambda r: r.status == 'draft' and r.deduction_date.month == payslip.date_to.month and r.deduction_date.year == payslip.date_to.year)
                        deduction_rec.write({'status': 'paid', 'pay_slip': payslip.number})
                    
            elif payroll_report.zero_payslip_boolean == True and payslip.line_ids.filtered(lambda x:x.code == 'SALADV' and x.amount == 0):
                adv_emi_rec = self.env['kw_advance_deduction_line'].sudo()
                for advance in salary_rec:
                    adv_current_emi_rec = adv_emi_rec.search([('deduction_date' ,'>=',payslip.date_from),('deduction_date','<=', payslip.date_to),('deduction_id','=',advance.id)])
                    adv_max_date_rec = adv_emi_rec.search([('deduction_id','=',advance.id)],order='deduction_date desc',limit=1)
                    adv_max_date = adv_max_date_rec.deduction_date + relativedelta(months=1)
                    for emi in adv_current_emi_rec:
                        # emi_val  = emi.monthly_interest * 2 
                        emi.write({'deduction_date':adv_max_date,'skipped_by_payroll':True})
                        
        query +=f" update payroll_increment set state='close' where  state='open' and employee_id = {payslip.employee_id.id};"
        query += f"update allowance_allocation_master set boolean_readonly = true where month='{str(payslip.date_to.month)}' and year='{str(payslip.date_to.year)}' and employee ={payslip.employee_id.id};"
        query += f"update kw_payslip_ledger set boolean_readonly = true where month='{str(payslip.date_to.month)}' and year='{str(payslip.date_to.year)}' and employee_id ={payslip.employee_id.id};"
        query += f"update lunch_expenses set boolean_readonly = true where  month='{str(payslip.date_to.month)}' and year='{str(payslip.date_to.year)}' and employee_id ={payslip.employee_id.id};"
        query += f"update hr_payslip set state = 'done' where id={payslip.id};"
       
        if len(query)> 0:
            self.env.cr.execute(query)

            # tds_rec = self.env['hr.declaration'].sudo().search([('employee_id', '=', payslip.employee_id.id)])
            # if len(tds_rec) > 0:
            #     deduction_rec = tds_rec.filtered(lambda r: r.date_range.date_start <= payslip.date_from and r.date_range.date_stop >= payslip.date_to)
            #     if deduction_rec:
            #         deduction_rec.button_compute_tax()
            #         deduction_rec.write({'tax_freeze': True})

            # if payslip.date_to.month == 3:
            #     print('called????????????????/')
            #     deduction_rec.button_compute_tax(date_to=payslip.date_to)

    # @api.model
    # @profile
    # def calculate_lwop(self, payslipid, basic, allowance, bonus):
    #     """Old code for payroll"""
    #     # payslip_rec = self.env['hr.payslip'].sudo().search([('id','=',payslipid)])
    #     # to_date = payslip_rec.date_to
    #     # attendance_info = self.env['kw_employee_monthly_payroll_info'].sudo().search(
    #     #     [('attendance_year', '=', to_date.year), ('attendance_month', '=', to_date.month),
    #     #      ('employee_id', '=', payslip_rec.employee_id.id)])
    #     # if attendance_info:
    #     #     absent_days = attendance_info.num_absent_days
    #     #     total_wpc = attendance_info.num_total_late_days_pc
    #     #     leave_lwop = attendance_info.num_leave_lwop
    #     #     total_absent_days = absent_days + total_wpc + leave_lwop
    #     #     # day_salary = (basic + allowance)/attendance_info.num_shift_working_days
    #     #     # total_ded = day_salary * total_absent_days
    #     #     gross = basic + allowance + bonus
    #     #     total_ded = gross/attendance_info.num_shift_working_days*total_absent_days
    #     #     return total_ded
    #     # else:
    #     #     return 0
    #     """New code for employee"""
    #     payslip_rec = self.env['hr.payslip'].sudo().search([('id', '=', payslipid)])
    #     to_date = payslip_rec.date_to
    #     attendance_info = self.env['kw_payroll_monthly_attendance_report'].sudo().search(
    #         [('attendance_year', '=', to_date.year), ('attendance_month', '=', to_date.month),
    #         ('employee_id', '=', payslip_rec.employee_id.id),('zero_payslip_boolean','=',False)])
    #     ir_config_params = self.env['ir.config_parameter'].sudo()
    #     enable_month_days = ir_config_params.get_param('payroll_inherit.enable_month') or False
    #     if attendance_info:
    #         total_paycut_days = attendance_info.total_pay_cut
    #         working_days = attendance_info.calculation_days if enable_month_days else attendance_info.actual_working 
    #         if working_days > 0:
    #             gross = basic + allowance + bonus
    #             total_ded = gross / working_days * total_paycut_days
    #             # return total_ded
    #             total = self.calculate_round_amount(total_ded)
    #             return total
    #         else:
    #             return 0
    #     else:
    #         return 0
    @api.model
    def calculate_lwop(self, basic, allowance, bonus,employee_id,year,month):
        """New code for lwop"""
        self.env.cr.execute(f"select total_pay_cut,calculation_days,actual_working from kw_payroll_monthly_attendance_report where attendance_year={year} and attendance_month = {month} and employee_id = {employee_id} and (zero_payslip_boolean is null or zero_payslip_boolean is false)")
        attendance_info = self._cr.dictfetchall()
        if not attendance_info:
            return 0
        else:
            self.env.cr.execute(f"select value from ir_config_parameter where key = 'payroll_inherit.enable_month'")
            config_month_days =  self._cr.dictfetchall()
            enable_month_days = config_month_days[0]['value'] if len(config_month_days)>0 else False
            working_days = attendance_info[0]['calculation_days'] if enable_month_days else attendance_info[0]['actual_working'] 
            if working_days > 0:
                gross = basic + allowance + bonus
                total_ded = gross / working_days * attendance_info[0]['total_pay_cut']
                return self.calculate_round_amount(total_ded)
            else:
                return 0

    @api.model
    # @profile
    def calculate_basic(self,contract_basic,employee_id,year,month,date_from,date_to,month_days,code):
        
        """New code for payroll"""
        # self.env.cr.execute(f"select emp_status,num_shift_working_days,actual_working,month_days,calculation_days from kw_payroll_monthly_attendance_report where attendance_year={year} and attendance_month = {month} and employee_id = {employee_id} and (zero_payslip_boolean is null or zero_payslip_boolean is false)")
        self.env.cr.execute(f"select emp_status,num_shift_working_days,actual_working,month_days,calculation_days,total_pay_cut from kw_payroll_monthly_attendance_report where attendance_year={year} and attendance_month = {month} and employee_id = {employee_id} and (zero_payslip_boolean is null or zero_payslip_boolean is false)")

        attendance_info = self._cr.dictfetchall()
        if not attendance_info:
            return 0
        else:
            if code == 'BASIC':
                if attendance_info[0]['emp_status'] == 1:
                    self.env.cr.execute(f"select employee_id,increment_date from payroll_increment where increment_date between '{date_from}' and '{date_to}' and employee_id={employee_id}")
                    increment_info = self._cr.dictfetchall()
                    if not increment_info:
                        return self.calculate_round_amount(contract_basic)
                    else:
                        self.env.cr.execute(f"select current_basic from hr_contract where state='close' and employee_id = {employee_id} order by id desc LIMIT 1")
                        exp_basic_dict = self._cr.dictfetchall()
                        ex_basic = (exp_basic_dict[0]['current_basic']/month_days) * (increment_info[0]['increment_date'].day - 1)
                        current_basic = (contract_basic/month_days)*(month_days-increment_info[0]['increment_date'].day +1)
                        return self.calculate_round_amount(ex_basic+current_basic)
                        
                else:
                    self.env.cr.execute(f"select value from ir_config_parameter where key = 'payroll_inherit.enable_month'")
                    config_month_days =  self._cr.dictfetchall()
                    enable_month_days = config_month_days[0]['value'] if len(config_month_days)>0 else False
                    working_days = attendance_info[0]['month_days'] if enable_month_days else  attendance_info[0]['num_shift_working_days']
                    actual_working =attendance_info[0]['calculation_days'] if enable_month_days else attendance_info[0]['actual_working']
                    return self.calculate_round_amount((actual_working /working_days) * contract_basic)
            else:
                if attendance_info[0]['emp_status'] == 1:
                    self.env.cr.execute(f"select employee_id,increment_date from payroll_increment where increment_date between '{date_from}' and '{date_to}' and employee_id={employee_id}")
                    increment_info = self._cr.dictfetchall()
                    if not increment_info:
                        lwop_basic = (contract_basic/month_days)*attendance_info[0]['total_pay_cut']
                        return self.calculate_round_amount(contract_basic-lwop_basic)
                    else:
                        self.env.cr.execute(f"select current_basic from hr_contract where state='close' and employee_id = {employee_id} order by id desc LIMIT 1")
                        exp_basic_dict = self._cr.dictfetchall()
                        ex_basic = (exp_basic_dict[0]['current_basic']/month_days) * (increment_info[0]['increment_date'].day - 1)
                        current_basic = (contract_basic/month_days)*(month_days-increment_info[0]['increment_date'].day +1)
                        return self.calculate_round_amount(ex_basic+current_basic)
                        
                else:
                    self.env.cr.execute(f"select value from ir_config_parameter where key = 'payroll_inherit.enable_month'")
                    config_month_days =  self._cr.dictfetchall()
                    enable_month_days = config_month_days[0]['value'] if len(config_month_days)>0 else False
                    working_days = attendance_info[0]['month_days'] if enable_month_days else  attendance_info[0]['num_shift_working_days']
                    actual_working =attendance_info[0]['calculation_days'] if enable_month_days else attendance_info[0]['actual_working']
                    lwop_basic = (contract_basic/month_days)*attendance_info[0]['total_pay_cut']
                    basic_after_lwop = contract_basic - lwop_basic
                    return self.calculate_round_amount((actual_working /working_days) * basic_after_lwop)
    # @api.model
    # def calculate_basic(self, payslipid):
    #     """ Previous code for payroll"""

    #     # payslip_rec = self.env['hr.payslip'].sudo().search([('id', '=', payslipid)])
    #     # date_end = payslip_rec.date_to
    #     # date_start = payslip_rec.date_from
    #     # emp_rec = self.env['hr.employee'].sudo().search([('id','=',payslip_rec.employee_id.id)])
    #     # if emp_rec:
    #     #     if date_start <= emp_rec.date_of_joining <= date_end:
    #     #         attendance_info = self.env['kw_employee_monthly_payroll_info'].sudo().search(
    #     #             [('attendance_year', '=', date_end.year), ('attendance_month', '=', date_end.month),
    #     #              ('employee_id', '=', payslip_rec.employee_id.id)])
    #     #         working_days = attendance_info.num_shift_working_days
    #     #         present_days = attendance_info.num_present_days
    #     #         emp_basic = payslip_rec.contract_id.current_basic
    #     #         final_basic = (present_days/working_days)*emp_basic
    #     #         return final_basic
    #     #     else:
    #     #         emp_basic = payslip_rec.contract_id.current_basic
    #     #         return emp_basic
    #     # else:
    #     #     return 0

    #     """New code for payroll"""
    #     payslip_rec = self.env['hr.payslip'].sudo().search([('id', '=', payslipid)])
    #     date_end = payslip_rec.date_to
    #     date_start = payslip_rec.date_from
    #     attendance_info = self.env['kw_payroll_monthly_attendance_report'].sudo().search(
    #         [('attendance_year', '=', date_end.year), ('attendance_month', '=', date_end.month),
    #          ('employee_id', '=', payslip_rec.employee_id.id),('zero_payslip_boolean','=',False)])
    #     if attendance_info:
    #         if attendance_info.emp_status == 1:
    #             emp_basic = payslip_rec.contract_id.current_basic
    #             total = self.calculate_round_amount(emp_basic)
    #             return total
    #         else:
    #             ir_config_params = self.env['ir.config_parameter'].sudo()
    #             enable_month_days = ir_config_params.get_param('payroll_inherit.enable_month') or False
    #             working_days = attendance_info.month_days if enable_month_days else  attendance_info.num_shift_working_days
    #             actual_working = attendance_info.calculation_days if enable_month_days else attendance_info.actual_working 
    #             emp_basic = payslip_rec.contract_id.current_basic
    #             final_basic = (actual_working / working_days) * emp_basic
    #             total = self.calculate_round_amount(final_basic)
    #             return total
    #     else:
    #         return 0

    # @api.model
    # # @profile
    # def calculate_pbonus(self, payslipid,productivity):
    #     """Changed by monalisha on 2 Aug,2023"""
    #     payslip_rec = self.env['hr.payslip'].sudo().browse(payslipid)
    #     self.env.cr.execute(f"select id,emp_status,attendance_year,attendance_month,num_mt_leave_days,num_shift_working_days,actual_working,month_days,calculation_days from kw_payroll_monthly_attendance_report where attendance_year={payslip_rec.date_to.year} and attendance_month = {payslip_rec.date_to.month} and employee_id = {payslip_rec.employee_id.id} and zero_payslip_boolean = false")
    #     attendance_info = self._cr.dictfetchall()
    #     self.env.cr.execute(f"select gender from hr_employee where id = {payslip_rec.employee_id.id}")
    #     gender = self._cr.dictfetchall()
    #     if not attendance_info:
    #         return 0
    #     else:
    #         self.env.cr.execute(f"select value from ir_config_parameter where key = 'payroll_inherit.enable_month'")
    #         config_month_days =  self._cr.dictfetchall()
    #         enable_month_days = config_month_days[0]['value'] if len(config_month_days)>0 else False
    #         start_date = date(int(attendance_info[0]['attendance_year']), int(attendance_info[0]['attendance_month'])-1, 26) if int(attendance_info[0]['attendance_month']) != 1 else date(int(attendance_info[0]['attendance_year'])-1,12, 26)
    #         payroll_end_date =date(int(attendance_info[0]['attendance_year']), int(attendance_info[0]['attendance_month']),25)
    #         monthly_payable_days = (payroll_end_date - start_date).days + payslip.write({'line_ids': lines, 'number': number})
    #         if gender[0]['gender'] == 'female' and attendance_info[0]['num_mt_leave_days'] > 0:
    #             if enable_month_days:
    #                 if attendance_info[0]['emp_status'] == 1:
    #                     tot_working = monthly_payable_days - attendance_info[0]['num_mt_leave_days']
    #                     return self.calculate_round_amount(tot_working / monthly_payable_days * productivity)
    #                 else:
    #                     total_working = 0 if (attendance_info[0]['calculation_days'] - attendance_info[0]['num_mt_leave_days']) < 0 else (attendance_info[0]['calculation_days'] - attendance_info[0]['num_mt_leave_days'])
    #                     return self.calculate_round_amount((total_working / monthly_payable_days) * productivity)
    #             else: 
    #                 if attendance_info[0]['emp_status'] == 1:
    #                     tot_working = attendance_info[0]['num_shift_working_days'] - attendance_info[0]['num_mt_leave_days']
    #                     return self.calculate_round_amount(tot_working / attendance_info[0]['num_shift_working_days'] * productivity)
    #                 else:
    #                     working_days = attendance_info[0]['num_shift_working_days']
    #                     total_working = 0 if (attendance_info[0]['actual_working'] - attendance_info[0]['num_mt_leave_days']) < 0 else (attendance_info[0]['actual_working'] - attendance_info[0]['num_mt_leave_days'])
    #                     return self.calculate_round_amount((total_working / working_days) * productivity)
    #         else:
    #             if attendance_info[0]['emp_status'] == 1:
    #                 return self.calculate_round_amount(productivity)
    #             else:
    #                 working_days =  attendance_info[0]['month_days'] if enable_month_days else attendance_info[0]['num_shift_working_days']
    #                 actual_working = attendance_info[0]['calculation_days'] if enable_month_days else  attendance_info[0]['actual_working']
    #                 return self.calculate_round_amount((actual_working / working_days) * productivity)
                
    # @api.model
    # def calculate_pbonus(self, payslipid):
    #     """Changed by monalisha on 20 Sep,2022"""
    #     payslip_rec = self.env['hr.payslip'].sudo().search([('id', '=', payslipid)])
    #     date_end = payslip_rec.date_to
    #     attendance_info = self.env['kw_payroll_monthly_attendance_report'].sudo().search(
    #         [('attendance_year', '=', date_end.year), ('attendance_month', '=', date_end.month),
    #          ('employee_id', '=', payslip_rec.employee_id.id),('zero_payslip_boolean','=',False)])
    #     if attendance_info:
    #         ir_config_params = self.env['ir.config_parameter'].sudo()
    #         enable_month_days = ir_config_params.get_param('payroll_inherit.enable_month') or False
    #         start_date = date(int(attendance_info.attendance_year), int(attendance_info.attendance_month)-1, 26) if int(attendance_info.attendance_month) != 1 else date(int(attendance_info.attendance_year)-1,12, 26)
    #         payroll_end_date =date(int(attendance_info.attendance_year), int(attendance_info.attendance_month),25)
    #         monthly_payable_days = (payroll_end_date - start_date).days + 1
    #         if payslip_rec.employee_id.gender == 'female' and attendance_info.num_mt_leave_days > 0:
    #             if enable_month_days:
    #                 if attendance_info.emp_status == 1:
    #                     tot_working = monthly_payable_days - attendance_info.num_mt_leave_days
    #                     pb = tot_working / monthly_payable_days * payslip_rec.contract_id.productivity
    #                     total = self.calculate_round_amount(pb)
    #                     return total
    #                 else:
    #                     working_days = monthly_payable_days
    #                     total_working = 0 if (attendance_info.calculation_days - attendance_info.num_mt_leave_days) < 0 else (
    #                                 attendance_info.calculation_days - attendance_info.num_mt_leave_days)
    #                     emp_pbonus = payslip_rec.contract_id.productivity
    #                     pb = (total_working / working_days) * emp_pbonus
    #                     total = self.calculate_round_amount(pb)
    #                     return total
    #             else: 
    #                 if attendance_info.emp_status == 1:
    #                     tot_working = attendance_info.num_shift_working_days - attendance_info.num_mt_leave_days
    #                     pb = tot_working / attendance_info.num_shift_working_days * payslip_rec.contract_id.productivity
    #                     total = self.calculate_round_amount(pb)
    #                     return total
    #                 else:
    #                     working_days = attendance_info.num_shift_working_days
    #                     total_working = 0 if (attendance_info.actual_working - attendance_info.num_mt_leave_days) < 0 else (
    #                                 attendance_info.actual_working - attendance_info.num_mt_leave_days)
    #                     emp_pbonus = payslip_rec.contract_id.productivity
    #                     pb = (total_working / working_days) * emp_pbonus
    #                     total = self.calculate_round_amount(pb)
    #                     return total
    #         else:
    #             if attendance_info.emp_status == 1:
    #                 pb = payslip_rec.contract_id.productivity
    #                 total = self.calculate_round_amount(pb)
    #                 return total
    #             else:
    #                 working_days =  attendance_info.month_days if enable_month_days else attendance_info.num_shift_working_days
    #                 actual_working = attendance_info.calculation_days if enable_month_days else  attendance_info.actual_working
    #                 emp_pbonus = payslip_rec.contract_id.productivity
    #                 pb = (actual_working / working_days) * emp_pbonus
    #                 total = self.calculate_round_amount(pb)
    #                 return total
    #     else:
    #         return 0
    @api.model
    # @profile
    def calculate_cbonus(self, amount,year,month,employee_id,gender,code,date_to):
        self.env.cr.execute(f"select emp_status,attendance_year,attendance_month,num_mt_leave_days,num_shift_working_days,actual_working,month_days,calculation_days from kw_payroll_monthly_attendance_report where attendance_year={year} and attendance_month = {month} and employee_id = {employee_id} and (zero_payslip_boolean is null or zero_payslip_boolean is false)")
        attendance_info = self._cr.dictfetchall()
        if not attendance_info:
            return 0
        else:
            self.env.cr.execute(f"select value from ir_config_parameter where key = 'payroll_inherit.enable_month'")
            config_month_days =  self._cr.dictfetchall()
            enable_month_days = config_month_days[0]['value'] if len(config_month_days)>0 else False
            start_date = date(int(attendance_info[0]['attendance_year']), int(attendance_info[0]['attendance_month'])-1, 26) if int(attendance_info[0]['attendance_month']) != 1 else date(int(attendance_info[0]['attendance_year'])-1,12, 26)
            payroll_end_date =date(int(attendance_info[0]['attendance_year']), int(attendance_info[0]['attendance_month']),25)
            monthly_payable_days = (payroll_end_date - start_date).days + 1
            self.env.cr.execute(f"select employee_id,increment_date from payroll_increment where increment_date between '{start_date}' and '{payroll_end_date}' and employee_id={employee_id}")
            increment_info = self._cr.dictfetchall()
            self.env.cr.execute(f"select productivity,commitment from hr_contract where state='close' and employee_id = {employee_id} order by id desc LIMIT 1")
            exp_productivity_dict = self._cr.dictfetchall()
            contract_value = 0
            if exp_productivity_dict:
                contract_value = exp_productivity_dict[0]['productivity'] if code =='PB' else exp_productivity_dict[0]['commitment']
                contract_value = contract_value if contract_value else 0
            if gender == 'female' and attendance_info[0]['num_mt_leave_days'] > 0:
                if enable_month_days:
                    if attendance_info[0]['emp_status'] == 1:
                        tot_working = monthly_payable_days - attendance_info[0]['num_mt_leave_days']
                        if tot_working >0:
                            if not increment_info:
                                return self.calculate_round_amount(tot_working / monthly_payable_days * amount)
                            else:
                                self.env.cr.execute(f"select id,request_unit_half_to_period,request_date_to,request_date_from from hr_leave where employee_id = {employee_id} and (request_date_to between '{start_date}' and '{payroll_end_date}' or request_date_from between '{start_date}' and '{payroll_end_date}') and state='validate'")
                                leave_info = self._cr.dictfetchall()
                                if leave_info:
                                    if start_date <=leave_info[0]['request_date_to'] <= payroll_end_date:
                                        if leave_info[0]['request_date_to'] < increment_info[0]['increment_date']:
                                            new_days = abs(payroll_end_date - increment_info[0]['increment_date']).days +1
                                            per_day_new_pb = amount/monthly_payable_days
                                            new_pb = per_day_new_pb * new_days
                                            old_days = abs(increment_info[0]['increment_date'] - leave_info[0]['request_date_to']).days -1 
                                            per_day_old_pb = contract_value/monthly_payable_days
                                            old_pb = per_day_old_pb * old_days
                                            if old_pb+new_pb > 0:
                                                return self.calculate_round_amount(old_pb+new_pb)
                                            else:
                                                return 0
                                        else:
                                            left_days = monthly_payable_days - attendance_info[0]['num_mt_leave_days']
                                            per_day_new_pb = amount / monthly_payable_days
                                            left_day_new_pb = per_day_new_pb * left_days
                                            return self.calculate_round_amount(left_day_new_pb)
                                    elif start_date <=leave_info[0]['request_date_from'] <= payroll_end_date:
                                        if leave_info[0]['request_date_from'] < increment_info[0]['increment_date']:
                                            return self.calculate_round_amount(tot_working/ monthly_payable_days * contract_value)
                                        else:
                                            day_count_till_increment = abs(start_date - increment_info[0]['increment_date']).days
                                            day_count_till_leave = abs(leave_info[0]['request_date_from'] - increment_info[0]['increment_date']).days
                                            per_day_old_pb = contract_value/monthly_payable_days
                                            old_pb = per_day_old_pb * day_count_till_increment
                                            per_day_new_pb = amount/monthly_payable_days
                                            new_pb = per_day_new_pb * day_count_till_leave
                                            return self.calculate_round_amount(old_pb+new_pb)
                        else:
                            return 0
                    else:
                        total_working = 0 if (attendance_info[0]['calculation_days'] - attendance_info[0]['num_mt_leave_days']) < 0 else (attendance_info[0]['calculation_days'] - attendance_info[0]['num_mt_leave_days'])
                        return self.calculate_round_amount((total_working / monthly_payable_days) * amount)
                else: 
                    if attendance_info[0]['emp_status'] == 1:
                        tot_working = attendance_info[0]['num_shift_working_days'] - attendance_info[0]['num_mt_leave_days']
                        return self.calculate_round_amount(tot_working / attendance_info[0]['num_shift_working_days'] * amount)
                    else:
                        total_working = 0 if (attendance_info[0]['actual_working'] - attendance_info[0]['num_mt_leave_days']) < 0 else (attendance_info[0]['actual_working'] - attendance_info[0]['num_mt_leave_days'])
                        return self.calculate_round_amount((total_working / attendance_info[0]['num_shift_working_days']) * amount)
            else:
                if attendance_info[0]['emp_status'] == 1:
                    if not increment_info:
                        return self.calculate_round_amount(amount)
                    else:
                        month_days = attendance_info[0]['month_days']
                        old_days = (increment_info[0]['increment_date'].day - 1)
                        old_pb_per_day = contract_value/month_days
                        old_pb = old_pb_per_day * old_days
                        new_days = (date_to - increment_info[0]['increment_date']).days + 1
                        new_pb_per_day = amount/month_days
                        new_pb = new_pb_per_day * new_days
                        return self.calculate_round_amount(old_pb+new_pb)
                else:
                    working_days =  attendance_info[0]['month_days'] if enable_month_days else attendance_info[0]['num_shift_working_days']
                    actual_working = attendance_info[0]['calculation_days'] if enable_month_days else  attendance_info[0]['actual_working']
                    return self.calculate_round_amount((actual_working / working_days) * amount)

    # @api.model
    # def calculate_cbonus(self, payslipid):
    #     """Changed by monalisha on 20 Sep,2022"""
    #     payslip_rec = self.env['hr.payslip'].sudo().search([('id', '=', payslipid)])
    #     date_end = payslip_rec.date_to
    #     attendance_info = self.env['kw_payroll_monthly_attendance_report'].sudo().search(
    #         [('attendance_year', '=', date_end.year), ('attendance_month', '=', date_end.month),
    #          ('employee_id', '=', payslip_rec.employee_id.id),('zero_payslip_boolean','=',False)])
    #     if attendance_info:
    #         ir_config_params = self.env['ir.config_parameter'].sudo()
    #         enable_month_days = ir_config_params.get_param('payroll_inherit.enable_month') or False
    #         start_date = date(int(attendance_info.attendance_year), int(attendance_info.attendance_month)-1, 26) if int(attendance_info.attendance_month) != 1 else date(int(attendance_info.attendance_year)-1,12, 26)
    #         payroll_end_date = date(int(attendance_info.attendance_year), int(attendance_info.attendance_month),25)
    #         monthly_payable_days = (payroll_end_date - start_date).days + 1
    #         if payslip_rec.employee_id.gender == 'female' and attendance_info.num_mt_leave_days > 0:
    #             if enable_month_days:
    #                 if attendance_info.emp_status == 1:
    #                     tot_working = monthly_payable_days - attendance_info.num_mt_leave_days
    #                     cb = tot_working / monthly_payable_days * payslip_rec.contract_id.commitment
    #                     total = self.calculate_round_amount(cb)
    #                     return total
    #                 else:
    #                     working_days = monthly_payable_days
    #                     total_working = 0 if (attendance_info.calculation_days - attendance_info.num_mt_leave_days) < 0 else (
    #                                 attendance_info.calculation_days - attendance_info.num_mt_leave_days)
    #                     emp_cbonus = payslip_rec.contract_id.commitment
    #                     cb = (total_working / working_days) * emp_cbonus
    #                     total = self.calculate_round_amount(cb)
    #                     return total
    #             else:
    #                 if attendance_info.emp_status == 1:
    #                     tot_working = attendance_info.num_shift_working_days - attendance_info.num_mt_leave_days
    #                     cb = tot_working / attendance_info.num_shift_working_days * payslip_rec.contract_id.commitment
    #                     total = self.calculate_round_amount(cb)
    #                     return total
    #                 else:
    #                     working_days = attendance_info.num_shift_working_days
    #                     total_working = 0 if (attendance_info.actual_working - attendance_info.num_mt_leave_days) < 0 else (
    #                                 attendance_info.actual_working - attendance_info.num_mt_leave_days)
    #                     emp_cbonus = payslip_rec.contract_id.commitment
    #                     cb = (total_working / working_days) * emp_cbonus
    #                     total = self.calculate_round_amount(cb)
    #                     return total

    #         else:
    #             if attendance_info.emp_status == 1:
    #                 cb = payslip_rec.contract_id.commitment
    #                 total = self.calculate_round_amount(cb)
    #                 return total
    #             else:
    #                 working_days = attendance_info.month_days if enable_month_days else attendance_info.num_shift_working_days
    #                 actual_working = attendance_info.calculation_days if enable_month_days else attendance_info.actual_working
    #                 emp_cbonus = payslip_rec.contract_id.commitment
    #                 cb = (actual_working / working_days) * emp_cbonus
    #                 total = self.calculate_round_amount(cb)
    #                 return total
    #     else:
    #         return 0

    @api.model
    def method_calculate_tax(self, amount,emp_age,date_range):
        if emp_age < 60:
            if 250000 < amount <= 500000:
                tds_amount = amount - 250000
                tax_slab = self.env['tax_slab'].sudo().search(
                    [('date_range', '=', date_range), ('salary_from', '<=', amount), ('salary_to', '>=', amount),
                     ('tax_regime', '=', 'old_regime'), ('age_from', '<=', emp_age), ('age_to', '>=', emp_age)],
                    limit=1)
                tds = tds_amount * tax_slab.tax_rate / 100
                after_rebate = tds - 12500 if amount < 500000 else 0
                if after_rebate <= 0:
                    return 0
                else:
                    cess = after_rebate * tax_slab.cess / 100
                    # return after_rebate + cess
                    total = after_rebate + cess
                    if (total % 10) >= 5:
                        z = 10 - (total % 10)
                        return total + z
                    else:
                        return total - (total % 10)
            elif 500000 < amount <= 1000000:
                tds_above5 = amount - 500000
                tax_slab = self.env['tax_slab'].sudo().search(
                    [('date_range', '=', date_range), ('salary_from', '<=', amount), ('salary_to', '>=', amount),
                     ('tax_regime', '=', 'old_regime'), ('age_from', '<=', emp_age), ('age_to', '>=', emp_age)],
                    limit=1)
                tds_above5percentage = tds_above5 * tax_slab.tax_rate / 100
                tax_slab_1 = self.env['tax_slab'].sudo().search(
                    [('date_range', '=', date_range), ('salary_from', '>=', 250001), ('salary_to', '<=', 5000000),
                     ('tax_regime', '=', 'old_regime'), ('age_from', '<=', emp_age), ('age_to', '>=', emp_age)],
                    limit=1)
                tds_below5percentage = 250000 * tax_slab_1.tax_rate / 100
                tds = tds_above5percentage + tds_below5percentage
                # tax_slab_rec = self.env['tax_slab'].sudo().search([('salary_from','<=',amount),('salary_to','>=',amount),('tax_regime','=','old_regime'),('age_from','<=',emp_age),('age_to','>=',emp_age)],limit=1)
                cess = tds * tax_slab.cess / 100
                # return tds + cess
                total = tds + cess
                if (total % 10) >= 5:
                    z = 10 - (total % 10)
                    return total + z
                else:
                    return total - (total % 10)
            elif amount > 1000000:
                tds_above10 = amount - 1000000
                tax_slab = self.env['tax_slab'].sudo().search(
                    [('date_range', '=', date_range), ('salary_from', '<=', amount), ('salary_to', '>=', amount),
                     ('tax_regime', '=', 'old_regime'), ('age_from', '<=', emp_age), ('age_to', '>=', emp_age)],
                    limit=1)
                tds_above10percentage = tds_above10 * tax_slab.tax_rate / 100
                tax_slab_1 = self.env['tax_slab'].sudo().search(
                    [('date_range', '=', date_range), ('salary_from', '>=', 500001), ('salary_to', '<=', 1000000),
                     ('tax_regime', '=', 'old_regime'), ('age_from', '<=', emp_age), ('age_to', '>=', emp_age)],
                    limit=1)
                tds_above5percentage = 500000 * tax_slab_1.tax_rate / 100
                tax_slab_2 = self.env['tax_slab'].sudo().search(
                    [('date_range', '=', date_range), ('salary_from', '>=', 250001), ('salary_to', '<=', 5000000),
                     ('tax_regime', '=', 'old_regime'), ('age_from', '<=', emp_age), ('age_to', '>=', emp_age)],
                    limit=1)
                tds_below5percentage = 250000 * tax_slab_2.tax_rate / 100
                tds = tds_above10percentage + tds_above5percentage + tds_below5percentage
                tax_slab_rec = self.env['tax_slab'].sudo().search(
                    [('date_range', '=', date_range), ('salary_from', '<=', amount), ('salary_to', '>=', amount),
                     ('tax_regime', '=', 'old_regime'), ('age_from', '<=', emp_age), ('age_to', '>=', emp_age)],
                    limit=1)
                if amount >= 5000000:
                    subcharge = tds * tax_slab_rec.surcharge / 100
                else:
                    subcharge = 0
                cess = tds * tax_slab_rec.cess / 100
                total =  tds + cess + subcharge
                if (total % 10) >= 5:
                    z = 10 - (total % 10)
                    return total + z
                else:
                    return total - (total % 10)
            else:
                return 0
        elif 60 <= emp_age <= 80:
            if 300000 < amount <= 500000:
                tds_amount = amount- 300000
                tax_slab = self.env['tax_slab'].sudo().search(
                    [('date_range', '=', date_range), ('salary_from', '<=', amount), ('salary_to', '>=', amount),
                     ('tax_regime', '=', 'old_regime'), ('age_from', '<=', emp_age), ('age_to', '>=', emp_age)],
                    limit=1)
                tds = tds_amount * tax_slab.tax_rate / 100
                after_rebate = tds - 12500 if amount < 500000 else 0
                if after_rebate <= 0:
                    return 0
                else:
                    cess = after_rebate * tax_slab.cess / 100
                    total = after_rebate + cess
                    if (total % 10) >= 5:
                        z = 10 - (total % 10)
                        return total + z
                    else:
                        return total - (total % 10)
            elif 500000 < amount <= 1000000:
                tds_above5 = amount - 500000
                tax_slab = self.env['tax_slab'].sudo().search(
                    [('date_range', '=', date_range), ('salary_from', '<=', amount), ('salary_to', '>=', amount),
                     ('tax_regime', '=', 'old_regime'), ('age_from', '<=', emp_age), ('age_to', '>=', emp_age)],
                    limit=1)
                tds_above5percentage = tds_above5 * tax_slab.tax_rate / 100
                tax_slab_1 = self.env['tax_slab'].sudo().search(
                    [('date_range', '=', date_range), ('salary_from', '>=', 300001), ('salary_to', '<=', 500000),
                     ('tax_regime', '=', 'old_regime'), ('age_from', '<=', emp_age), ('age_to', '>=', emp_age)],
                    limit=1)
                tds_below5percentage = 200000 * tax_slab_1.tax_rate / 100
                tds = tds_above5percentage + tds_below5percentage
                # tax_slab_rec = self.env['tax_slab'].sudo().search([('salary_from','<=',amount),('salary_to','>=',amount),('tax_regime','=','old_regime'),('age_from','<=',emp_age),('age_to','>=',emp_age)],limit=1)
                cess = tds * tax_slab.cess / 100
                total = tds + cess
                if (total % 10) >= 5:
                    z = 10 - (total % 10)
                    return total + z
                else:
                    return total - (total % 10)
            elif amount > 1000000:
                tds_above10 = amount - 1000000
                tax_slab = self.env['tax_slab'].sudo().search(
                    [('date_range', '=', date_range), ('salary_from', '<=', amount), ('salary_to', '>=', amount),
                     ('tax_regime', '=', 'old_regime'), ('age_from', '<=', emp_age), ('age_to', '>=', emp_age)],
                    limit=1)
                tds_above10percentage = tds_above10 * tax_slab.tax_rate / 100
                tax_slab_1 = self.env['tax_slab'].sudo().search(
                    [('date_range', '=', date_range), ('salary_from', '>=', 500001), ('salary_to', '<=', 1000000),
                     ('tax_regime', '=', 'old_regime'), ('age_from', '<=', emp_age), ('age_to', '>=', emp_age)],
                    limit=1)
                tds_above5percentage = 500000 * tax_slab_1.tax_rate / 100
                tax_slab_2 = self.env['tax_slab'].sudo().search(
                    [('date_range', '=', date_range), ('salary_from', '>=', 300001), ('salary_to', '<=', 500000),
                     ('tax_regime', '=', 'old_regime'), ('age_from', '<=', emp_age), ('age_to', '>=', emp_age)],
                    limit=1)
                tds_below5percentage = 200000 * tax_slab_2.tax_rate / 100
                tds = tds_above10percentage + tds_above5percentage + tds_below5percentage
                cess = tds * tax_slab.cess / 100
                total = tds + cess
                if (total % 10) >= 5:
                    z = 10 - (total % 10)
                    return total + z
                else:
                    return total - (total % 10)
            else:
                return 0
        elif emp_age > 80:
            if 500001 < amount <= 1000000:
                tds_amount = amount - 500000
                tax_slab = self.env['tax_slab'].sudo().search(
                    [('date_range', '=', date_range), ('salary_from', '<=', amount), ('salary_to', '>=', amount),
                     ('tax_regime', '=', 'old_regime'), ('age_from', '<=', emp_age), ('age_to', '>=', emp_age)],
                    limit=1)
                tds = tds_amount * tax_slab.tax_rate / 100
                cess = tds * tax_slab.cess / 100
                total = tds + cess
                if (total % 10) >= 5:
                    z = 10 - (total % 10)
                    return total + z
                else:
                    return total - (total % 10)
            elif amount > 1000000:
                tds_above5 = amount - 1000000
                tax_slab = self.env['tax_slab'].sudo().search(
                    [('date_range', '=', date_range), ('salary_from', '<=', amount), ('salary_to', '>=', amount),
                     ('tax_regime', '=', 'old_regime'), ('age_from', '<=', emp_age), ('age_to', '>=', emp_age)],
                    limit=1)
                tds_above5percentage = tds_above5 * tax_slab.tax_rate / 100
                tax_slab_1 = self.env['tax_slab'].sudo().search(
                    [('date_range', '=', date_range), ('salary_from', '>=', 500001), ('salary_to', '<=', 1000000),
                     ('tax_regime', '=', 'old_regime'), ('age_from', '<=', emp_age), ('age_to', '>=', emp_age)],
                    limit=1)
                tds_below5percentage = 500000 * tax_slab_1.tax_rate / 100
                tds = tds_above5percentage + tds_below5percentage
                cess = tds * tax_slab.cess / 100
                total = tds + cess
                if (total % 10) >= 5:
                    z = 10 - (total % 10)
                    return total + z
                else:
                    return total - (total % 10)
        else:
            return 0
        
    @api.model
    def method_calculate_new_regime_tax(self, amount,date_range):
        if 300000 < amount <= 600000:
            tds_amount = amount - 300000
            tax_slab = self.env['tax_slab'].sudo().search(
                [('date_range', '=', date_range), ('salary_from', '<=', amount), ('salary_to', '>=', amount),
                 ('tax_regime', '=', 'new_regime')], limit=1)
            temp_tax_payable = tds_amount * tax_slab.tax_rate / 100
            rebate = temp_tax_payable if amount <= 700000 else 0
            after_rebate = temp_tax_payable - rebate
            if after_rebate <= 0:
                return 0
            else:
                cess = after_rebate * tax_slab.cess / 100
                total = after_rebate + cess
                if (total % 10) >= 5:
                    z = 10 - (total % 10)
                    return total + z
                else:
                    return total - (total % 10)
        elif 600000 < amount <= 900000:
            tds_above5 = amount - 600000
            tax_slab = self.env['tax_slab'].sudo().search(
                [('date_range', '=', date_range), ('salary_from', '<=', amount), ('salary_to', '>=', amount),
                 ('tax_regime', '=', 'new_regime')], limit=1)
            tds_above5percentage = tds_above5 * tax_slab.tax_rate / 100
            tax_slab_1 = self.env['tax_slab'].sudo().search(
                [('date_range', '=', date_range), ('salary_from', '>=', 300001), ('salary_to', '<=', 600000),
                 ('tax_regime', '=', 'new_regime')], limit=1)
            tds_below5percentage = 300000 * tax_slab_1.tax_rate / 100
            temp_tax_payable = tds_above5percentage + tds_below5percentage
            rebate = temp_tax_payable if amount <= 700000 else 0
            after_rebate = temp_tax_payable - rebate
            if after_rebate <= 0:
                return 0
            else:
                cess = after_rebate * tax_slab.cess / 100
                total = after_rebate + cess

                if (total % 10) >= 5:
                    z = 10 - (total % 10)
                    return total + z
                else:
                    return total - (total % 10)
        elif 900000 < amount <= 1200000:
            tds_above75 = amount - 900000
            tax_slab = self.env['tax_slab'].sudo().search(
                [('date_range', '=', date_range), ('salary_from', '<=', amount), ('salary_to', '>=', amount),
                 ('tax_regime', '=', 'new_regime')], limit=1)
            tds_above75percentage = tds_above75 * tax_slab.tax_rate / 100
            tax_slab_1 = self.env['tax_slab'].sudo().search(
                [('date_range', '=', date_range), ('salary_from', '>=', 600001), ('salary_to', '<=', 900000),
                 ('tax_regime', '=', 'new_regime')], limit=1)
            tds_above5percentage = 300000 * tax_slab_1.tax_rate / 100
            tax_slab_2 = self.env['tax_slab'].sudo().search(
                [('date_range', '=', date_range), ('salary_from', '>=', 300001), ('salary_to', '<=', 600000),
                 ('tax_regime', '=', 'new_regime')], limit=1)
            tds_below5percentage = 300000 * tax_slab_2.tax_rate / 100
            temp_tax_payable = tds_above75percentage + tds_above5percentage + tds_below5percentage
            cess = temp_tax_payable * tax_slab.cess / 100
            total = temp_tax_payable + cess
            if (total % 10) >= 5:
                z = 10 - (total % 10)
                return total + z
            else:
                return total - (total % 10)
        elif 1200000 < amount <= 1500000:
            tds_above10 = amount - 1200000
            tax_slab = self.env['tax_slab'].sudo().search(
                [('date_range', '=', date_range), ('salary_from', '<=', amount), ('salary_to', '>=', amount),
                 ('tax_regime', '=', 'new_regime')], limit=1)
            tds_above10percentage = tds_above10 * tax_slab.tax_rate / 100
            
            tax_slab_1 = self.env['tax_slab'].sudo().search(
                [('date_range', '=', date_range), ('salary_from', '>=', 900001), ('salary_to', '<=', 1200000),
                 ('tax_regime', '=', 'new_regime')], limit=1)
            tds_above75percentage = 300000 * tax_slab_1.tax_rate / 100
            
            tax_slab_2 = self.env['tax_slab'].sudo().search(
                [('date_range', '=', date_range), ('salary_from', '>=', 600001), ('salary_to', '<=', 900000),
                 ('tax_regime', '=', 'new_regime')], limit=1)
            tds_above5percentage = 300000 * tax_slab_2.tax_rate / 100
            
            tax_slab_3 = self.env['tax_slab'].sudo().search(
                [('date_range', '=', date_range), ('salary_from', '>=', 300001), ('salary_to', '<=', 600000),
                 ('tax_regime', '=', 'new_regime')], limit=1)
            tds_below5percentage = 300000 * tax_slab_3.tax_rate / 100
            
            temp_tax_payable = tds_above10percentage + tds_above75percentage + tds_above5percentage + tds_below5percentage
            cess = temp_tax_payable * tax_slab.cess / 100
            total = temp_tax_payable + cess
            if (total % 10) >= 5:
                z = 10 - (total % 10)
                return total + z
            else:
                return total - (total % 10)
        elif amount > 1500000:
            tds_above15 = amount - 1500000
            tax_slab_15 = self.env['tax_slab'].sudo().search(
                [('date_range', '=', date_range), ('salary_from', '<=', amount), ('salary_to', '>=', amount),
                 ('tax_regime', '=', 'new_regime')], limit=1)
            tds_above15percentage = tds_above15 * tax_slab_15.tax_rate / 100
            
            tax_slab_12 = self.env['tax_slab'].sudo().search(
                [('date_range', '=', date_range), ('salary_from', '<=', 1200001), ('salary_to', '>=', 1500000),
                 ('tax_regime', '=', 'new_regime')], limit=1)
            tds_above12percentage = 300000 * tax_slab_12.tax_rate / 100
            
            tax_slab = self.env['tax_slab'].sudo().search(
                [('date_range', '=', date_range), ('salary_from', '<=', 900001), ('salary_to', '>=', 1200000),
                 ('tax_regime', '=', 'new_regime')], limit=1)
            tds_above10percentage = 300000 * tax_slab.tax_rate / 100
            
            tax_slab_1 = self.env['tax_slab'].sudo().search(
                [('date_range', '=', date_range), ('salary_from', '>=', 600001), ('salary_to', '<=', 900000),
                 ('tax_regime', '=', 'new_regime')], limit=1)
            tds_above75percentage = 300000 * tax_slab_1.tax_rate / 100
            
            tax_slab_2 = self.env['tax_slab'].sudo().search(
                [('date_range', '=', date_range), ('salary_from', '>=', 300001), ('salary_to', '<=', 600000),
                 ('tax_regime', '=', 'new_regime')], limit=1)
            tds_above5percentage = 300000 * tax_slab_2.tax_rate / 100
            
            temp_tax_payable = tds_above15percentage + tds_above12percentage + tds_above10percentage + tds_above75percentage + tds_above5percentage
            cess = temp_tax_payable * tax_slab_15.cess / 100
            total = temp_tax_payable + cess
            if (total % 10) >= 5:
                z = 10 - (total % 10)
                return total + z
            else:
                return total - (total % 10)
        else:
            return 0
        
    @api.model
    # @profile
    def calculate_tds(self, payslipid, basic, allowance, bonus, gross, pb, cb, lta, prof_persuit, arrear, INC, VAR,SALW, EALW, LE, CBDA, TINC, ERBONUS, lwop,employee_id,year,month,to_date,date_from,date_of_joining,last_working_day,active,NPS):
        self.env.cr.execute(f"select id from kw_payroll_monthly_attendance_report where attendance_year={year} and attendance_month = {month} and employee_id = {employee_id} and (zero_payslip_boolean is null or zero_payslip_boolean is false)")
        attendance_info = self._cr.dictfetchall()
        if not attendance_info: 
            return 0
        else:
            self.env.cr.execute(f"select value from ir_config_parameter where key = 'tds.enable_tds'")
            config_tds =  self._cr.dictfetchall()
            enable_tds = config_tds[0]['value'] if len(config_tds)>0 else False
            if enable_tds != False :
                self.env.cr.execute(f"select id,date_range from hr_declaration where employee_id = {employee_id} and  date_range = (select id from account_fiscalyear where date_start <= '{date_from}' and date_stop >= '{to_date}')")
                tds_lst = self._cr.dictfetchall()
                if not tds_lst:
                    return 0
                else:
                    deduction_rec = self.env['hr.declaration'].sudo().browse(tds_lst[0]['id'])
                    self.env.cr.execute(f"update hr_declaration set allow_edit_bool=false where id = {tds_lst[0]['id']}")
                    deduction_rec.button_compute_tax(date_to=to_date,date_from=date_from,basic=basic,allowance=allowance,bonus=bonus,gross=gross,pb=pb,cb=cb,lta=lta,prof_persuit=prof_persuit,arrear=arrear,INC=INC,VAR=VAR,SALW=SALW,EALW=EALW,LE=LE,CBDA=CBDA,TINC=TINC,ERBONUS=ERBONUS,LWOP=lwop,NPS=NPS)
                    self.env.cr.execute(f"select date_start,date_stop from account_fiscalyear where id = {tds_lst[0]['date_range']}")
                    fy_info = self._cr.dictfetchall()
                    date_start = fy_info[0]['date_start']
                    date_stop = fy_info[0]['date_stop']
                    if date_of_joining >= date_start and date_of_joining <= date_stop:
                        remain_months = (date_stop.year - date_of_joining.year) * 12 + (date_stop.month - date_of_joining.month)
                        month_limit = int(remain_months) + 1
                    else:
                        month_limit = 12
                    blk_date_lst = []
                    counter = 0
                    last_counter = 0
                    payslip = self.env['hr.payslip'].search([('employee_id', '=', employee_id),('state', '=', 'done'),('date_from', '>=',date_start),('date_to', '<=', date_stop)])
                    block_payslips = self.env['hr_block_salary'].sudo().search([('employee_id','=',employee_id)])
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
                    if last_working_day:
                        if date_start <= last_working_day <= date_stop and active == False:
                            last_counter =  (date_stop.year -  last_working_day.year) * 12 + date_stop.month -  last_working_day.month
                    remaining_month = month_limit - len(payslip) - counter - last_counter
                    g = 0
                    if remaining_month > 0:
                        self.env.cr.execute(f"select balance_tax_payable,wo_balance_tax_payable from hr_declaration where id = {deduction_rec.id}")
                        data = self._cr.dictfetchall()
                        balance_tax_payable = wo_balance_tax_payable =0
                        if data:
                            # Access the values
                            balance_tax_payable = data[0]['balance_tax_payable']
                            wo_balance_tax_payable = data[0]['wo_balance_tax_payable']
                        # print('payroll=========balance_tax_payable===========',balance_tax_payable)
                        # print('payroll=========wo_balance_tax_payable===========',wo_balance_tax_payable)
                        
                        g = (wo_balance_tax_payable / remaining_month) + (balance_tax_payable-wo_balance_tax_payable)
                    if g < 0:
                        return 0
                    else:
                        if to_date.month == 3:
                            return round(g)
                        elif last_working_day:
                            return round(g)
                        else:
                            amt = self.round_up_to_nearest_100(g)
                            return amt
            else:
                return 0
               
    # @api.model
    # @profile
    # def calculate_tds(self, payslipid, basic, allowance, bonus, gross, pb, cb, lta, prof_persuit, arrear, INC, VAR,SALW, EALW, LE, CBDA, TINC, ERBONUS, lwop):
    #     payslip_rec = self.env['hr.payslip'].sudo().search([('id', '=', payslipid)])
    #     to_date = payslip_rec.date_to
    #     payslip_ledger = self.env['kw_payslip_ledger'].sudo().search(
    #         [('year', '=', str(to_date.year)),
    #          ('employee_id', '=', payslip_rec.employee_id.id), ('month', '=', str(to_date.month)),
    #          ('salary_rule_id.code', '=', 'TDS'), ('boolean_readonly', '=', False)])
    #     if payslip_ledger:
    #         return payslip_ledger.amount
    #     else:
    #         ir_config_params = self.env['ir.config_parameter'].sudo()
    #         enable_tds = ir_config_params.get_param('tds.enable_tds') or False
    #         attendance_info = self.env['kw_payroll_monthly_attendance_report'].sudo().search(
    #         [('attendance_year', '=',to_date.year), ('attendance_month', '=', to_date.month),
    #          ('employee_id', '=', payslip_rec.employee_id.id),('zero_payslip_boolean','=',False)])
    #         if enable_tds != False:
    #             # month_dict = {1: 3, 2: 2, 3: 1, 4: 12, 5: 11, 6: 10, 7: 9, 8: 8, 9: 7, 10: 6, 11: 5, 12: 4}
    #             # c = 0
    #             # month = month_dict.get(to_date.month)
    #             tds_rec = self.env['hr.declaration'].sudo().search([('employee_id', '=', payslip_rec.employee_id.id)])
    #             if len(tds_rec) > 0:
    #                 deduction_rec = tds_rec.filtered(lambda r: r.date_range.date_start <= payslip_rec.date_from and r.date_range.date_stop >= payslip_rec.date_to)
    #                 if deduction_rec and attendance_info:
    #                         deduction_rec.sudo().write({'allow_edit_bool':False})
    #                     # if deduction_rec.tax_regime == 'old_regime':
    #                         # Execute the compute tax method of Income Tax
    #                         deduction_rec.button_compute_tax(date_to=to_date,date_from= payslip_rec.date_from,basic=basic,allowance=allowance,bonus=bonus,gross=gross,pb=pb,cb=cb,lta=lta,prof_persuit=prof_persuit,arrear=arrear,INC=INC,VAR=VAR,SALW=SALW,EALW=EALW,LE=LE,CBDA=CBDA,TINC=TINC,ERBONUS=ERBONUS,LWOP=lwop)
    #                         # Calculate all the variable allowance for the current month
    #                     #     alw_rec = self.env['allowance_allocation_master'].sudo().search(
    #                     #         [('month', '=', str(to_date.month)), ('year', '=', str(to_date.year)),
    #                     #         ('employee', '=', payslip_rec.employee_id.id), ('boolean_readonly', '=', False)])
    #                     #     # Calculate the total of all the variable allowance
    #                     #     if alw_rec:
    #                     #         for alw in alw_rec:
    #                     #             c += alw.amount
    #                     #     else:
    #                     #         c = 0
    #                     #     # print('c===========', c)
    #                     #     # Total taxable Income
    #                     #     a = deduction_rec.taxable_income

    #                     #     # print('a====================', a)
    #                     #     # Total Tax Payable
    #                     #     b = deduction_rec.total_tax_payable
    #                     #     # print('b====================', b)
    #                     #     # taxable income excluding variable allowance
    #                     #     d = 0 if (a - c) < 0 else (a - c)
    #                     #     # print('d====================', d)

    #                         # temp_e = self.method_calculate_tax(d, deduction_rec.emp_age, deduction_rec.date_range.id)
    #                         # # Extra tax calculated
    #                         # if (temp_e % 10) >= 5:
    #                         #     z = 10 - (temp_e % 10)
    #                         #     # print(temp_e + z)
    #                         #     tax_amount = temp_e + z
    #                         # else:
    #                         #     # print(temp_e - (temp_e % 10))
    #                         #     tax_amount = temp_e - (temp_e % 10)
    #                         # e = tax_amount
    #                         # # print('e====================', e)
    #                         # f = 0 if (b - e) < 0 else (b - e)
    #                         # # print('f====================', f)
    #                         # # Tax to be deducted 
    #                         # g = f + ((e - (deduction_rec.tax_recovered)) / int(month))
    #                         # print('g====================', g)
    #                         j_date = deduction_rec.employee_id.date_of_joining
    #                         if j_date >= deduction_rec.date_range.date_start and j_date <= deduction_rec.date_range.date_stop:
    #                             remain_months = (deduction_rec.date_range.date_stop.year - j_date.year) * 12 + (
    #                                     deduction_rec.date_range.date_stop.month - j_date.month)
    #                             month_limit = int(remain_months) + 1
    #                         else:
    #                             month_limit = 12

    #                         blk_date_lst = []
    #                         counter = 0
    #                         last_counter = 0
    #                         remaining_month = 0
    #                         payslip = self.env['hr.payslip'].sudo().search([('employee_id', '=', deduction_rec.employee_id.id),
    #                                                         ('state', '=', 'done'),
    #                                                         ('date_from', '>=', deduction_rec.date_range.date_start),
    #                                                         ('date_to', '<=', deduction_rec.date_range.date_stop),
    #                                                         ])
    #                         block_payslips = self.env['hr_block_salary'].sudo().search([('employee_id','=',deduction_rec.employee_id.id)])
    #                         for blk_payslp in block_payslips:
    #                             blk_year = int(blk_payslp.year)
    #                             blk_month = int(blk_payslp.month)
    #                             blk_date = date(blk_year,blk_month,1)
    #                             blk_date_lst.append(blk_date)
    #                         for dates in blk_date_lst:
    #                             if deduction_rec.date_range.date_start <= dates <= deduction_rec.date_range.date_stop:
    #                                 chk_payslip = payslip.filtered(lambda x:x.date_from <= dates <= x.date_to)
    #                                 if not chk_payslip:
    #                                     counter += 1
    #                         if deduction_rec.employee_id.last_working_day:
    #                             if deduction_rec.date_range.date_start <= deduction_rec.employee_id.last_working_day <= deduction_rec.date_range.date_stop and deduction_rec.employee_id.active == False:
    #                                 last_counter =  (deduction_rec.date_range.date_stop.year -  deduction_rec.employee_id.last_working_day.year) * 12 + deduction_rec.date_range.date_stop.month -  deduction_rec.employee_id.last_working_day.month
    #                         remaining_month = month_limit - len(payslip) - counter - last_counter
    #                         g = 0
    #                         if remaining_month > 0:
    #                             g = deduction_rec.balance_tax_payable / remaining_month
    #                         if g < 0:
    #                             return 0
    #                         else:
    #                             if payslip_rec.date_to.month == 3:
    #                                 return round(g)
    #                             elif payslip_rec.employee_id.last_working_day:
    #                                 # if payslip_rec.date_from <= payslip_rec.employee_id.last_working_day <= to_date:
    #                                     return round(g)
    #                             else:
    #                                 amt = self.round_up_to_nearest_100(g)
    #                                 return amt
    #                         # else:
    #                         #     return 0
                                
    #                     # else:
    #                     #     # Execute the new regime compute tax method of Income Tax
    #                     #     deduction_rec.button_compute_tax(date_to=to_date, basic=basic, allowance=allowance,
    #                     #                                      bonus=bonus, gross=gross, pb=pb, cb=cb, lta=lta,
    #                     #                                      prof_persuit=prof_persuit, arrear=arrear, INC=INC, VAR=VAR,
    #                     #                                      SALW=SALW, EALW=EALW, LE=LE, CBDA=CBDA, TINC=TINC,
    #                     #                                      ERBONUS=ERBONUS, LWOP=lwop)
    #                     #     # Calculate all the variable allowance for the current month
    #                     #     alw_rec = self.env['allowance_allocation_master'].sudo().search(
    #                     #         [('month', '=', str(to_date.month)), ('year', '=', str(to_date.year)),
    #                     #         ('employee', '=', payslip_rec.employee_id.id), ('boolean_readonly', '=', False)])
    #                     #     # Calculate the total of all the variable allowance
    #                     #     if alw_rec:
    #                     #         for alw in alw_rec:
    #                     #             c += alw.amount
    #                     #     else:
    #                     #         c = 0
    #                     #     # print('c===========', c)
    #                     #     # Total taxable Income
    #                     #     a = deduction_rec.taxable_income

    #                     #     # print('a====================', a)
    #                     #     # Total Tax Payable
    #                     #     b = deduction_rec.total_tax_payable
    #                     #     # print('b====================', b)
    #                     #     # taxable income excluding variable allowance
    #                     #     d = 0 if (a - c) < 0 else (a - c)
    #                     #     # print('d====================', d)

    #                     #     temp_e = self.method_calculate_new_regime_tax(d, deduction_rec.date_range.id)
    #                     #     # Extra tax calculated
    #                     #     if (temp_e % 10) >= 5:
    #                     #         z = 10 - (temp_e % 10)
    #                     #         # print(temp_e + z)
    #                     #         tax_amount = temp_e + z
    #                     #     else:
    #                     #         # print(temp_e - (temp_e % 10))
    #                     #         tax_amount = temp_e - (temp_e % 10)
    #                     #     e = tax_amount
    #                     #     # print('e====================', e)
    #                     #     f = 0 if (b - e) < 0 else (b - e)
    #                     #     # print('f====================', f)
    #                     #     # Tax to be deducted 
    #                     #     g = f + ((e - (deduction_rec.tax_recovered)) / int(month))
    #                     #     # print('g====================', g)
    #                     #     if g < 0:
    #                     #         return 0
    #                     #     else:
    #                     #         if payslip_rec.date_to.month == 3:
    #                     #             return round(g)
    #                     #         else:
    #                     #             amt = self.round_up_to_nearest_100(g)
    #                     #             return amt
    #                 else:
    #                     return 0
    #             else:
    #                 return 0
    #         else:
    #             return 0


class EmployeeProfilePayslip(models.Model):
    _inherit = 'kw_emp_profile'

    def view_employee_payslip(self):
        check_active_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)]).id
        if check_active_id:
            check_payslip = self.env['hr.payslip'].sudo().search([('employee_id', '=', check_active_id),
                                                                  ('state', '=', 'done')])
            if check_payslip:
                number = ''
                # otp_value = ''.join(random.choice(string.digits) for _ in range(4))
                otp_value = ''.join(secrets.choice(string.digits) for _ in range(4))
                template_id = self.env.ref('payroll_inherit.payslip_otp_mail_notification')
                email_id = self.env.user.employee_ids.work_email
                name = self.env.user.employee_ids.name

                otp = otp_value
                template_id.with_context(email_id=email_id, name=name, otp=otp).sudo().send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light",force_send=True)
                model = self.env['payslip_otp_log']
                model.sudo().create({'employee_id': self.env.user.employee_ids.id, 'otp': otp_value})

                view_id = self.env.ref('payroll_inherit.payslip_otp_view_form').id

                try:
                    formatted_msg = f"Please use OTP {otp} to view Payslips.\n CSM Technologies"
                    html_msg = formatted_msg.replace('\\n', '\n')
                    message = html_msg
                    # print("message=================", message)
                    header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                    number = self.env.user.employee_ids.mobile_phone if self.env.user.employee_ids.mobile_phone else ''
                    url = f'https://api.bulksmsgateway.in/sendmessage.php?user=csmwebu&password=Csmpl$4980&mobile={number}&message={message}&sender=CSMTEC&type=3&template_id=1207165900901935259'
                    response = requests.post(url, headers=header)
                except:
                    pass

                action = {
                    'name': 'OTP Validation',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'views': [(view_id, 'form')],
                    'res_model': 'payslip_otp',
                    'view_id': view_id,
                    'target': 'new',
                }
                return action
            else:
                raise ValidationError(f"You don't have any confirmed payslips yet.")



class EmployeeNpsDetails(models.Model):
    _inherit = 'kw_emp_profile'
    
    employee_nps_id = fields.One2many('nps_employee_data','emp_profile_id',string='Corporate NPS')
    employee_nps_eligible = fields.Boolean(compute='_check_employee_nps_eligibility')


    def _check_employee_nps_eligibility(self):
        for rec in self:
            if (rec.emp_id.company_id.id == 1 and rec.emp_id.enable_payroll == 'yes') and len(self.employee_nps_id) == 0:
                rec.employee_nps_eligible = True
            else:
                rec.employee_nps_eligible = False