from odoo import api, fields, models, tools , _
from odoo.exceptions import UserError, ValidationError
import datetime, time
from dateutil.relativedelta import relativedelta

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'   

    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)

    @api.model
    def create(self, vals):
        res = super(HrPayslip, self).create(vals)
        payslip_ids = self.env['hr.payslip'].search([('employee_id','=',res.employee_id.id),
                                                     ('date_from','=',res.date_from),
                                                     ('date_to','=',res.date_to)]) - res
        if payslip_ids:
            raise ValidationError(_(f"{res.employee_id.name} has payslip for the month of {res.date_to.strftime('%B')}"))
        else:
            return res


    def compute_difference_two_date(self):
        s=self.date_from
        e=self.date_to
        start = s.day
        end = e.day
        date_days = end - start + 1
        return date_days
    
    #added by sangita
    def compute_net_pay(self):
        loan_amount = 0.0
        if self.line_ids:
            for line in self.line_ids:
                if line.code == 'LOAN':
                    loan_amount = line.amount
                if line.code == 'NET':
                    net = line.amount - loan_amount
                    return net

    def get_loan_installment_no(self, **kwargs):
        for rec in self:
            number = ''
            activeLoan = self.env['hr.loan'].sudo().search([('employee_id', '=', rec.employee_id.id), ('state', '=', 'grant')])
            if activeLoan:
                activeLoanLines = self.env['hr.loan.line'].sudo().search([('loan_id', '=', activeLoan.id)])
                sortedactiveLoanLines = activeLoanLines.sorted(key=lambda x: x.date)
                for i, loanline in enumerate(sortedactiveLoanLines, start=1):
                    if rec.date_from <= loanline.date and rec.date_to >= loanline.date:
                        number = str(i)
                rec.loan_label = f'Short Term Loan {number}/{len(sortedactiveLoanLines)}'
            else:
                rec.loan_label = 'Short Term Loan'
            if kwargs.get('get_loan_number'):
                return number

    loan_label = fields.Char("Loan Label", compute="get_loan_installment_no")

    @api.multi
    def compute_hpl_ccl(self, code):
        relative_from = (self.date_from - relativedelta(months=1)).replace(day=26)
        relative_to = self.date_from.replace(day=25)
        if code == 'HPL':
            leave_count = len(self.env['hr.leave'].sudo().get_employee_leave_detail('HPL', self.employee_id.id,
                                                                                    relative_from, relative_to).get('days'))
        else:
            currentMonthCCLleave = len(self.env['hr.leave'].sudo().get_employee_leave_detail('CCL', self.employee_id.id,
                                                                                            relative_from, relative_to).get('days'))
            CCLTillFromDate = len(self.env['hr.leave'].sudo().get_employee_leave_detail('CCL', self.employee_id.id, 
                                                                                        self.employee_id.date_of_join, relative_from).get('days'))
            totalCCLleave = currentMonthCCLleave + CCLTillFromDate

            if CCLTillFromDate >= 365:
                leave_count = currentMonthCCLleave
            else:
                if totalCCLleave > 365:
                    leave_count = totalCCLleave - 365
                else:
                    leave_count = 0
        return "" if not leave_count else leave_count
    
#     def get_l_coming(self):
#         l_coming = 0.0
#         if self.line_ids:
#             for line in self.line_ids:
#                 if line.code == 'LC':
#                     l_coming = line.amount
#                     return l_coming
#                 
#     def half_h_deducation(self):
#         half_hour = 0.0
#         if self.line_ids:
#             for line in self.line_ids:
#                 if line.code == 'HHD':
#                     half_hour = line.amount
#                     print("?????????????????????????",half_hour)
#                     return half_hour
            
#     def half_day_deducation(self):
#         half_day = 0.0
#         if self.line_ids:
#             for line in self.line_ids:
#                 if line.code == 'HDD':
#                     half_day = line.amount
#                     print("____000000000000000000000000000000",half_day)
#                     return half_day
                
#     def early_going_days(self):
#         early_going = 0.0
#         if self.line_ids:
#             for line in self.line_ids:
#                 if line.code == 'EGD':
#                     early_going = line.amount
#                     return early_going
                
   
    @api.depends('line_ids.amount')
    def _compute_amount_total_words(self):
        for s in self:
            for line in s.line_ids:
                if line.code == 'NET':
                    s.amount_total_words = s.currency_id.amount_to_text(line.amount)

    amount_total_words = fields.Char("Total (In Words)", compute="_compute_amount_total_words",store=True)

    
    def leaves_type_cal_earned(self):
#         
        for leave in self:
            if leave.employee_id:
                print("///////////////////////////////////")
                SQL = """
                    
                select  sum(leave.number_of_days) as rem_leave
                    --leave.employee_id as employee
                    from hr_leave_report as leave
                    inner join hr_leave_type as hly on hly.id = leave.holiday_status_id
                    where leave.employee_id = %s and 
                    hly.leave_type.code = 'Earned Leave' and
                    state not in ('refuse')
                    group by
                    leave.employee_id,
                    leave.holiday_status_id;
                """
                self.env.cr.execute(SQL,(
                                          leave.employee_id.id,
                                          ))
                res = self.env.cr.fetchall()
                r = [i[0] for i in res]
#                 print("??????????????????????",[i[0] for i in res])
                return r
            
    def leaves_type_cal_half_pay_leave(self):
#        
        for leave in self:
            if leave.employee_id:
#                 print("///////////////////////////////////",to_date)
                SQL = """
                   select  sum(leave.number_of_days) as rem_leave
                    --leave.employee_id as employee
                    from hr_leave_report as leave
                    inner join hr_leave_type as hly on hly.id = leave.holiday_status_id
                    where leave.employee_id = %s and 
                    hly.leave_type.code = 'Half Pay Leave' and
                    state not in ('refuse')
                    group by
                    leave.employee_id,
                    leave.holiday_status_id;
                """
                self.env.cr.execute(SQL,(
                                          leave.employee_id.id,
                                          ))
                res = self.env.cr.fetchall()
                r = [i[0] for i in res]
#                 print("??????????????????????sick_leavessick_leaves",res)
                return r
    
    def leaves_type_cal_casual(self):
#        
        for leave in self:
            if leave.employee_id:
#                 print("///////////////////////////////////",to_date)
                SQL = """
                    select  sum(leave.number_of_days) as rem_leave
                    --leave.employee_id as employee
                    from hr_leave_report as leave
                    inner join hr_leave_type as hly on hly.id = leave.holiday_status_id
                    where leave.employee_id = %s and 
                    hly.leave_type.code = 'Casual Leave' and
                    state not in ('refuse')
                    group by
                    leave.employee_id,
                    leave.holiday_status_id;
                """
                self.env.cr.execute(SQL,(
                                          leave.employee_id.id,
                                          ))
                res = self.env.cr.fetchall()
                r = [i[0] for i in res]
#                 print("??????????????????????casual_leavescasual_leaves",res)
                return r
            
    def leaves_type_cal_maternity(self):
#        
        for leave in self:
            if leave.employee_id:
#                 print("///////////////////////////////////",to_date)
                SQL = """
                    select  sum(leave.number_of_days) as rem_leave
                    --leave.employee_id as employee
                    from hr_leave_report as leave
                    inner join hr_leave_type as hly on hly.id = leave.holiday_status_id
                    where leave.employee_id = %s and 
                    hly.leave_type.code = 'Maternity Leave' and
                    state not in ('refuse')
                    group by
                    leave.employee_id,
                    leave.holiday_status_id;
                """
                self.env.cr.execute(SQL,(
                                          leave.employee_id.id,
                                          ))
                res = self.env.cr.fetchall()
                r = [i[0] for i in res]
#                 print("??????????????????????casual_leavescasual_leaves",res)
                return r
            
    def leaves_type_cal_special_casual(self):
#        
        for leave in self:
            if leave.employee_id:
#                 print("///////////////////////////////////",to_date)
                SQL = """
                    select  sum(leave.number_of_days) as rem_leave
                    --leave.employee_id as employee
                    from hr_leave_report as leave
                    inner join hr_leave_type as hly on hly.id = leave.holiday_status_id
                    where leave.employee_id = %s and 
                    hly.leave_type.code = 'Special Casual Leave' and
                    state not in ('refuse')
                    group by
                    leave.employee_id,
                    leave.holiday_status_id;
                """
                self.env.cr.execute(SQL,(
                                          leave.employee_id.id,
                                          ))
                res = self.env.cr.fetchall()
                r = [i[0] for i in res]
#                 print("??????????????????????casual_leavescasual_leaves",res)
                return r
            
    def leaves_type_cal_extra_ordinary_leave(self):
#        
        for leave in self:
            if leave.employee_id:
#                 print("///////////////////////////////////",to_date)
                SQL = """
                    select  sum(leave.number_of_days) as rem_leave
                    --leave.employee_id as employee
                    from hr_leave_report as leave
                    inner join hr_leave_type as hly on hly.id = leave.holiday_status_id
                    where leave.employee_id = %s and 
                    hly.leave_type.code = 'Extra Ordinary Leave' and
                    state not in ('refuse')
                    group by
                    leave.employee_id,
                    leave.holiday_status_id;
                """
                self.env.cr.execute(SQL,(
                                          leave.employee_id.id,
                                          ))
                res = self.env.cr.fetchall()
                r = [i[0] for i in res]
#                 print("??????????????????????casual_leavescasual_leaves",res)
                return r
            
    def leaves_type_cal_paternity_leave(self):
#        
        for leave in self:
            if leave.employee_id:
#                 print("///////////////////////////////////",to_date)
                SQL = """
                    select  sum(leave.number_of_days) as rem_leave
                    --leave.employee_id as employee
                    from hr_leave_report as leave
                    inner join hr_leave_type as hly on hly.id = leave.holiday_status_id
                    where leave.employee_id = %s and 
                    hly.leave_type.code = 'Paternity Leave' and
                    state not in ('refuse')
                    group by
                    leave.employee_id,
                    leave.holiday_status_id;
                """
                self.env.cr.execute(SQL,(
                                          leave.employee_id.id,
                                          ))
                res = self.env.cr.fetchall()
                r = [i[0] for i in res]
#                 print("??????????????????????casual_leavescasual_leaves",res)
                return r
            
    def leaves_type_cal_chlid_care_leave(self):
#        
        for leave in self:
            if leave.employee_id:
#                 print("///////////////////////////////////",to_date)
                SQL = """
                    select  sum(leave.number_of_days) as rem_leave
                    --leave.employee_id as employee
                    from hr_leave_report as leave
                    inner join hr_leave_type as hly on hly.id = leave.holiday_status_id
                    where leave.employee_id = %s and 
                    hly.leave_type.code = 'Child Care Leave' and
                    state not in ('refuse')
                    group by
                    leave.employee_id,
                    leave.holiday_status_id;
                """
                self.env.cr.execute(SQL,(
                                          leave.employee_id.id,
                                          ))
                res = self.env.cr.fetchall()
                r = [i[0] for i in res]
#                 print("??????????????????????casual_leavescasual_leaves",res)
                return r
    
    
    def unused_leaves_cal(self):
        unused = 0
        a = []
        unused_leaves_id = self.env['hr.leave'].search([('holiday_type','=','employee'),('employee_id','=',self.employee_id.id),('state','in',('confirm','validate'))])
        for i in unused_leaves_id:
            a += [i.number_of_days]
            unused = sum(a)
        return unused
    
    
    def used_leaves_cal(self):
        used = 0
        a = []
        used_leaves_id = self.env['hr.leave'].search([('holiday_type','=','employee'),('employee_id','=',self.employee_id.id), ('state','in',('confirm','validate'))])
        for i in used_leaves_id:
            a += [-i.number_of_days]
            used = sum(a)
        return used
    
    def get_late_coming_h(self):
        late_com_h = 0.0
        for s in self:
            attendance_ids = self.env['currated.attendance'].search([('employee_id','=',self.employee_id.id),('expected_start','>=',self.date_from),('expected_end','<=',self.date_to)])
#             print("???????/-?????????????????????????",attendance_ids)
            for attendance in attendance_ids:
                late_com_h = attendance.late_coming_min
                print("[[[[[[[[[[[[[[[[[[[[",late_com_h)
        return  late_com_h
    
class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'
    
    
    date_from = fields.Date(string='Date From', readonly=True)
    date_to = fields.Date(string='Date To', readonly=True) 
    state = fields.Selection([('draft', 'Draft'),
                        ('verify', 'Waiting'),
                        ('done', 'Done'),
                        ('cancel', 'Rejected')
                    ],string="Status",related="slip_id.state")  
    paid = fields.Boolean(string="Made Payment Order",related="slip_id.paid")
    date_from = fields.Date(string="Date From", related="slip_id.date_from")
    date_to = fields.Date(string="Date To", related="slip_id.date_to")
    payslip_batch = fields.Many2one(string="Payslip Batch",related="slip_id.payslip_run_id")
    is_current_month = fields.Boolean(compute="_check_current_month", store=True)
    # identify_id = fields.Char("Identification No", related="employee_id.identify_id")
    # job_id = fields.Many2one('hr.job', 'Designation', related="employee_id.job_id")
    # paylevel_id = fields.Many2one('hr.payslip.paylevel', 'Pay Level', default=lambda self: self.env['hr.contract'].search([('employee_id', '=', '1')], limit=1))
    emp = fields.Char('Employee(C)', compute="_check_current_month", store=True)
    identify_id = fields.Char("Identification No", compute="_check_current_month", store=True)
    job_id = fields.Many2one('hr.job', 'Designation', compute="_check_current_month", store=True)
    paylevel_id = fields.Many2one('hr.payslip.paylevel', 'Pay Level', compute="_check_current_month", store=True)

    @api.depends('date_from')
    def _check_current_month(self):
        for rec in self:
            if rec.date_from:
                first_day = datetime.date.today().replace(day=1)
                last_day = datetime.date.today().replace(day=1)+ relativedelta(months=1) - relativedelta(days=1)
                if rec.date_from:
                    if first_day <= rec.date_from <= last_day:
                        rec.is_current_month = True
                    else:
                        rec.is_current_month = False
                rec.emp = f"{rec.employee_id.name} ({rec.employee_id.identify_id}) | {rec.employee_id.job_id.name}"
                rec.identify_id = rec.employee_id.identify_id
                rec.job_id = rec.employee_id.job_id.id
                contract_id = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id),
                                                                        ('state','=','open')], limit=1)
                rec.paylevel_id = contract_id.pay_level_id.id


class PayrollAdviceReport(models.AbstractModel):
    _inherit = 'report.l10n_in_hr_payroll.report_payrolladvice'

    def get_detail(self, line_ids):
        result = []
        boi_line_ids = line_ids.filtered(lambda x: x.employee_id.bank_account_id.bank_id.name.lower().strip() == 'bank of india')
        self.total_bysal = sum(boi_line_ids.mapped('bysal'))
        for l in boi_line_ids:
            res = {}
            res.update({
                    'name': l.employee_id.name,
                    'acc_no': l.employee_id.bank_account_id.acc_number,
                    'ifsc_code': l.employee_id.bank_account_id.bank_id.bic or '',
                    'bysal': l.bysal,
                    'bank_name': l.employee_id.bank_account_id.bank_id.name,
                    'debit_credit': l.debit_credit,
                    })
            result.append(res)
        return result

class PayrollAdviceReport(models.AbstractModel):
    _name = 'report.payslip_report.report_non_boi_payrolladvice'
    _description = "Report non boi payrolladvice"

    def get_month(self, input_date):
        res = {
               'from_name': '', 'to_name': ''
               }
        slip = self.env['hr.payslip'].search([('date_from', '<=', input_date), ('date_to', '>=', input_date)], limit=1)
        if slip:
            from_date = slip.date_from
            to_date = slip.date_to
            res['from_name'] = from_date.strftime('%d') + '-' + from_date.strftime('%B') + '-' + from_date.strftime('%Y')
            res['to_name'] = to_date.strftime('%d') + '-' + to_date.strftime('%B') + '-' + to_date.strftime('%Y')
        return res

    def get_detail(self, line_ids):
        result = []
        for l in line_ids.filtered(lambda x: x.employee_id.bank_account_id.bank_id.name.lower().strip() != 'bank of india'):
            res = {}
            res.update({
                    'name': l.employee_id.name,
                    'acc_no': l.employee_id.bank_account_id.acc_number,
                    'ifsc_code': l.employee_id.bank_account_id.bank_id.bic or '',
                    'bysal': l.bysal,
                    'bank_name': l.employee_id.bank_account_id.bank_id.name,
                    'debit_credit': l.debit_credit,
                    })
            result.append(res)
        return result
    
    def get_bysal_total(self, line_ids):
        non_boi_line_ids = line_ids.filtered(lambda x: x.employee_id.bank_account_id.bank_id.name.lower().strip() != 'bank of india')
        self.total_bysal = sum(non_boi_line_ids.mapped('bysal'))
        return self.total_bysal


    @api.model
    def _get_report_values(self, docids, data=None):
        advice = self.env['hr.payroll.advice'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'hr.payroll.advice',
            'data': data,
            'docs': advice,
            'time': time,
            'get_month': self.get_month,
            'get_detail': self.get_detail,
            'get_bysal_total': self.get_bysal_total,
        }
