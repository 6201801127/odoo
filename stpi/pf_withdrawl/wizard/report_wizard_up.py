# commit history
# shift january to march to the last (after december) while report creation 20 June 2021 (Gouranga Kala)
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import time, datetime,timedelta
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date, datetime
import datetime
from odoo.tools import float_utils
from collections import defaultdict
from pytz import utc
from calendar import monthrange


class WizardLateComing(models.TransientModel):
    _name = 'pf.ledger.wizard'
    _description = 'PF Ledger'
    

    @api.onchange('employee_id')
    def get_branch_job(self):
        for rec in self:
            rec.branch_id = rec.employee_id.branch_id
            rec.job_id = rec.employee_id.job_id

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    def _get_employee_ids(self):
        domain = []
        if self.env.user.has_group('pf_withdrawl.group_pf_withdraw_approver'):
            domain += [('branch_id', 'in', self.env.user.branch_ids.mapped('id'))]
        else:
            domain += [('user_id', '=', self.env.uid)]
        return domain

    
    report_of = fields.Selection([('pf_ledger','PF Ledger'),
                                  ],string="Report On", default='pf_ledger')

    employee_id = fields.Many2one('hr.employee','Requested By', default=_default_employee, domain=_get_employee_ids)
    # interest_rate = fields.Float('Interest Rate') , domain="[('date_start', '<=', date.today()), ('date_end', '>=', date.today())]"
    ledger_for_year = fields.Many2one('date.range', string='Ledger for the year')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    branch_id = fields.Many2one('res.branch', string='Center')
    branch_ids = fields.Many2many('res.branch', string='Centers')
    job_id = fields.Many2one('hr.job', string='Functional Designation')




    # @api.onchange('branch_id','ledger_for_year')
    # @api.constrains('branch_id','ledger_for_year')
    # def check_existing_branch_sr(self):
    #     self.from_date = self.ledger_for_year.date_start
    #     self.to_date = self.ledger_for_year.date_end
    #     company = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)], limit=1)
    #     if company:
    #         for com in company:
    #             if self.ledger_for_year.date_start and self.ledger_for_year.date_end and self.branch_id:
    #                 for line in com.pf_table:
    #                     if line.from_date >= self.ledger_for_year.date_start and line.to_date <= self.ledger_for_year.date_end:
    #                         self.interest_rate = line.interest_rate



    # @api.multi
    # def confirm_report(self):
    #     for rec in self:
    #         company_id = self.env['res.company'].sudo().browse(rec.employee_id.user_id.company_id.id)
    #         start_date, end_date = rec.ledger_for_year.date_start, rec.ledger_for_year.date_end
    #         interest_rate = sum(company_id.pf_table.filtered(lambda x: x.from_date >= start_date and x.to_date <= end_date)\
    #                             .mapped('interest_rate'))
    #         print('=============interest_rate===============', interest_rate)
    #         dr = self.env['pf.ledger.report'].search([('employee_id', '=', rec.employee_id.id),('ledger_for_year', '=', rec.ledger_for_year.id)])
    #         for lines in dr:
    #             lines.unlink()

    #         pay_rules_old = self.env['pf.employee.details'].search(
    #                 [('pf_details_id.employee_id', '=', rec.employee_id.id),
    #                  ('date', '<', rec.ledger_for_year.date_start)
    #                  ])
    #         total = 0.00
    #         for ln in pay_rules_old:
    #             if ln.type == 'Deposit':
    #                 total += ln.amount
    #             else:
    #                 total -= ln.amount
    #         relative_from_date = start_date - relativedelta(months=1)
    #         month_last_day = monthrange(relative_from_date.year, relative_from_date.month)[1]
    #         relative_to_date = relative_from_date.replace(day=month_last_day)
    #         emp_opening_deposit_bal = sum(pay_rules_old.filtered(lambda x: x.type == 'Deposit'\
    #                                     and x.pf_code in ['CEPF','VCPF',('CEPF + VCPF')] and x.date <= relative_to_date).mapped('amount'))
    #         emp_opening_withdrawl_bal = sum(pay_rules_old.filtered(lambda x: x.type == 'Withdrawal'\
    #                                         and x.pf_code in ['CEPF','VCPF',('CEPF + VCPF')] and x.date <= relative_to_date).mapped('amount'))
    #         emplr_opening_deposit_bal = sum(pay_rules_old.filtered(lambda x: x.type == 'Deposit'\
    #                                         and x.pf_code == 'CPF' and x.date <= relative_to_date).mapped('amount'))
    #         emplr_opening_withdrawl_bal = sum(pay_rules_old.filtered(lambda x: x.type == 'Withdrawal'\
    #                                         and x.pf_code == 'CPF' and x.date <= relative_to_date).mapped('amount'))
    #         emp_closing_contribution = emp_opening_deposit_bal - emp_opening_withdrawl_bal
    #         emplr_closing_contribution = emplr_opening_deposit_bal - emplr_opening_withdrawl_bal
    #         cr_lines = self.env['pf.ledger.report'].create({
    #             'employee_id': rec.employee_id.id,
    #             'ledger_for_year': rec.ledger_for_year.id,
    #             'branch_id': rec.employee_id.branch_id.id,
    #             'month': 'Opening',
    #             'epmloyee_contribution': str(round(emp_closing_contribution)),
    #             'voluntary_contribution': str(round(emplr_closing_contribution)),
    #             'employer_contribution': '0',
    #             'interest_employee_voluntary': '0',
    #             'interest_employer': '0',
    #             'total': str(round(total)),
    #         })



    #         pay_rules = self.env['pf.employee.details'].search(
    #                 [('pf_details_id.employee_id', '=', rec.employee_id.id),
    #                  ('date', '>=', rec.ledger_for_year.date_start),
    #                  ('date', '<=', rec.ledger_for_year.date_end)
    #                  ])
    #         print('=============lines===============',pay_rules)
    #         """emp = 0
    #         volun = 0
    #         emplyr = 0
    #         employee_interest = 0
    #         employer_contribution = 0
    #         month = 'January'
    #         for ln in pay_rules:
    #             if str(ln.date.month) == '1':
    #                 month = 'January'
    #                 if ln.pf_code == 'CPF':
    #                     if ln.type == 'Deposit':
    #                         emp += ln.amount
    #                     else:
    #                         emp -= ln.amount
    #                 elif ln.pf_code == 'VCPF' or ln.pf_code == 'CEPF' or ln.pf_code == 'CEPF + VCPF':
    #                     if ln.type == 'Deposit':
    #                         volun += ln.amount
    #                     else:
    #                         volun -= ln.amount
    #                 # elif ln.pf_code == 'CEPF':
    #                 #     if ln.type == 'Deposit':
    #                 #         emplyr += ln.amount
    #                 #     else:
    #                 #         emplyr -= ln.amount

    #         employee_interest = (((emp) * interest_rate) * 3) / 12
    #         employer_contribution = (((volun) * interest_rate) * 3) / 12
    #         total = emp + volun + employee_interest + employer_contribution
    #         jan = self.env['pf.ledger.report'].create({
    #                 'employee_id': rec.employee_id.id,
    #                 'ledger_for_year': rec.ledger_for_year.id,
    #                 'branch_id': rec.employee_id.branch_id.id,
    #                 'month': str(month),
    #                 'epmloyee_contribution': str(round(emp)),
    #                 'voluntary_contribution': str(round(volun)),
    #                 'employer_contribution': str(round(emplyr)),
    #                 'interest_employee_voluntary': str(round(employee_interest)),
    #                 'interest_employer': str(round(employer_contribution)),
    #                 'total': str(round(total)),
    #             })
    #         #print('================creation lines================', cr_lines)
            
            

    #         emp = 0
    #         volun = 0
    #         emplyr = 0
    #         employee_interest = 0
    #         employer_contribution = 0
    #         month = 'February'
    #         for ln in pay_rules:
    #             if str(ln.date.month) == '2':
    #                 month = 'February'
    #                 if ln.pf_code == 'CPF':
    #                     if ln.type == 'Deposit':
    #                         emp += ln.amount
    #                     else:
    #                         emp -= ln.amount
    #                 elif ln.pf_code == 'VCPF' or ln.pf_code == 'CEPF' or ln.pf_code == 'CEPF + VCPF':
    #                     if ln.type == 'Deposit':
    #                         volun += ln.amount
    #                     else:
    #                         volun -= ln.amount
    #                 # elif ln.pf_code == 'CEPF':
    #                 #     if ln.type == 'Deposit':
    #                 #         emplyr += ln.amount
    #                 #     else:
    #                 #         emplyr -= ln.amount

    #         employee_interest = (((emp) * interest_rate) * 2) / 12
    #         employer_contribution = (((volun) * interest_rate) * 2) / 12
    #         total = emp + volun + employee_interest + employer_contribution
    #         feb = self.env['pf.ledger.report'].create({
    #                 'employee_id': rec.employee_id.id,
    #                 'ledger_for_year': rec.ledger_for_year.id,
    #                 'branch_id': rec.employee_id.branch_id.id,
    #                 'month': str(month),
    #                 'epmloyee_contribution': str(round(emp)),
    #                 'voluntary_contribution': str(round(volun)),
    #                 'employer_contribution': str(round(emplyr)),
    #                 'interest_employee_voluntary': str(round(employee_interest)),
    #                 'interest_employer': str(round(employer_contribution)),
    #                 'total': str(round(total)),
    #             })
    #         #print('================creation lines================', cr_lines)
            
            

            
            
    #         emp = 0
    #         volun = 0
    #         emplyr = 0
    #         employee_interest = 0
    #         employer_contribution = 0
    #         month = 'March'
    #         for ln in pay_rules:
    #             if str(ln.date.month) == '3':
    #                 month = 'March'
                    
    #                 if ln.pf_code == 'CPF':
    #                     if ln.type == 'Deposit':
    #                         emp += ln.amount
    #                     else:
    #                         emp -= ln.amount
    #                 elif ln.pf_code == 'VCPF' or ln.pf_code == 'CEPF' or ln.pf_code == 'CEPF + VCPF':
    #                     if ln.type == 'Deposit':
    #                         volun += ln.amount
    #                     else:
    #                         volun -= ln.amount
    #                 # elif ln.pf_code == 'CEPF':
    #                 #     if ln.type == 'Deposit':
    #                 #         emplyr += ln.amount
    #                 #     else:
    #                 #         emplyr -= ln.amount

    #         employee_interest = (((emp) * interest_rate) * 1) / 12
    #         employer_contribution = (((volun) * interest_rate) * 1) / 12
    #         total = emp + volun + employee_interest + employer_contribution
    #         mar = self.env['pf.ledger.report'].create({
    #                 'employee_id': rec.employee_id.id,
    #                 'ledger_for_year': rec.ledger_for_year.id,
    #                 'branch_id': rec.employee_id.branch_id.id,
    #                 'month': str(month),
    #                 'epmloyee_contribution': str(round(emp)),
    #                 'voluntary_contribution': str(round(volun)),
    #                 'employer_contribution': str(round(emplyr)),
    #                 'interest_employee_voluntary': str(round(employee_interest)),
    #                 'interest_employer': str(round(employer_contribution)),
    #                 'total': str(round(total)),
    #             })
    #         #print('================creation lines================', cr_lines)"""
            
            

            
            
    #         emp = 0
    #         volun = 0
    #         emplyr = 0
    #         employee_interest = 0
    #         employer_contribution = 0
    #         month = 'April'
    #         for ln in pay_rules:
    #             if str(ln.date.month) == '4':
    #                 month = 'April'
    #                 if ln.pf_code == 'CPF':
    #                     if ln.type == 'Deposit':
    #                         emp += ln.amount
    #                     else:
    #                         emp -= ln.amount
    #                 elif ln.pf_code == 'VCPF' or ln.pf_code == 'CEPF' or ln.pf_code == 'CEPF + VCPF':
    #                     if ln.type == 'Deposit':
    #                         volun += ln.amount
    #                     else:
    #                         volun -= ln.amount
    #                 # elif ln.pf_code == 'CEPF':
    #                 #     if ln.type == 'Deposit':
    #                 #         emplyr += ln.amount
    #                 #     else:
    #                 #         emplyr -= ln.amount

    #         employee_interest = ((emp * (interest_rate / 100)) * 12) / 12
    #         employer_contribution = ((volun * (interest_rate /100)) * 12) / 12
    #         total = emp + volun + employee_interest + employer_contribution
    #         apr = self.env['pf.ledger.report'].create({
    #                 'employee_id': rec.employee_id.id,
    #                 'ledger_for_year': rec.ledger_for_year.id,
    #                 'branch_id': rec.employee_id.branch_id.id,
    #                 'month': str(month),
    #                 'epmloyee_contribution': str(round(emp)),
    #                 'voluntary_contribution': str(round(volun)),
    #                 'employer_contribution': str(round(emplyr)),
    #                 'interest_employee_voluntary': str(round(employee_interest)),
    #                 'interest_employer': str(round(employer_contribution)),
    #                 'total': str(round(total)),
    #             })
    #         #print('================creation lines================', cr_lines)
            
            

            
            
    #         emp = 0
    #         volun = 0
    #         emplyr = 0
    #         employee_interest = 0
    #         employer_contribution = 0
    #         month = 'May'
    #         for ln in pay_rules:
    #             if str(ln.date.month) == '5':
    #                 month = 'May'
    #                 if ln.pf_code == 'CPF':
    #                     if ln.type == 'Deposit':
    #                         emp += ln.amount
    #                     else:
    #                         emp -= ln.amount
    #                 elif ln.pf_code == 'VCPF' or ln.pf_code == 'CEPF' or ln.pf_code == 'CEPF + VCPF':
    #                     if ln.type == 'Deposit':
    #                         volun += ln.amount
    #                     else:
    #                         volun -= ln.amount

    #                 # elif ln.pf_code == 'CEPF':
    #                 #     if ln.type == 'Deposit':
    #                 #         emplyr += ln.amount
    #                 #     else:
    #                 #         emplyr -= ln.amount
    #         employee_interest = ((emp * (interest_rate / 100)) * 11) / 12
    #         employer_contribution = ((volun * (interest_rate / 100)) * 11) / 12
    #         total = emp + volun + employee_interest + employer_contribution
    #         may = self.env['pf.ledger.report'].create({
    #                 'employee_id': rec.employee_id.id,
    #                 'ledger_for_year': rec.ledger_for_year.id,
    #                 'branch_id': rec.employee_id.branch_id.id,
    #                 'month': str(month),
    #                 'epmloyee_contribution': str(round(emp)),
    #                 'voluntary_contribution': str(round(volun)),
    #                 'employer_contribution': str(round(emplyr)),
    #                 'interest_employee_voluntary': str(round(employee_interest)),
    #                 'interest_employer': str(round(employer_contribution)),
    #                 'total': str(round(total)),
    #             })
    #         #print('================creation lines================', cr_lines)
            
            

            
            
    #         emp = 0
    #         volun = 0
    #         emplyr = 0
    #         employee_interest = 0
    #         employer_contribution = 0
    #         month = 'June'
    #         for ln in pay_rules:
    #             if str(ln.date.month) == '6':
    #                 month = 'June'

    #                 if ln.pf_code == 'CPF':
    #                     if ln.type == 'Deposit':
    #                         emp += ln.amount
    #                     else:
    #                         emp -= ln.amount
    #                 elif ln.pf_code == 'VCPF' or ln.pf_code == 'CEPF' or ln.pf_code == 'CEPF + VCPF':
    #                     if ln.type == 'Deposit':
    #                         volun += ln.amount
    #                     else:
    #                         volun -= ln.amount
    #                 # elif ln.pf_code == 'CEPF':
    #                 #     if ln.type == 'Deposit':
    #                 #         emplyr += ln.amount
    #                 #     else:
    #                 #         emplyr -= ln.amount

    #         employee_interest = ((emp * (interest_rate / 100)) * 10) / 12
    #         employer_contribution = ((volun * (interest_rate / 100)) * 10) / 12
    #         total = emp + volun + employee_interest + employer_contribution
    #         jun = self.env['pf.ledger.report'].create({
    #                 'employee_id': rec.employee_id.id,
    #                 'ledger_for_year': rec.ledger_for_year.id,
    #                 'branch_id': rec.employee_id.branch_id.id,
    #                 'month': str(month),
    #                 'epmloyee_contribution': str(round(emp)),
    #                 'voluntary_contribution': str(round(volun)),
    #                 'employer_contribution': str(round(emplyr)),
    #                 'interest_employee_voluntary': str(round(employee_interest)),
    #                 'interest_employer': str(round(employer_contribution)),
    #                 'total': str(round(total)),
    #             })
    #         #print('================creation lines================', cr_lines)
            
            

            
            
    #         emp = 0
    #         volun = 0
    #         emplyr = 0
    #         employee_interest = 0
    #         employer_contribution = 0
    #         month = 'July'
    #         for ln in pay_rules:
    #             if str(ln.date.month) == '7':
    #                 month = 'July'
    #                 if ln.pf_code == 'CPF':
    #                     if ln.type == 'Deposit':
    #                         emp += ln.amount
    #                     else:
    #                         emp -= ln.amount
    #                 elif ln.pf_code == 'VCPF' or ln.pf_code == 'CEPF' or ln.pf_code == 'CEPF + VCPF':
    #                     if ln.type == 'Deposit':
    #                         volun += ln.amount
    #                     else:
    #                         volun -= ln.amount
    #                 # elif ln.pf_code == 'CEPF':
    #                 #     if ln.type == 'Deposit':
    #                 #         emplyr += ln.amount
    #                 #     else:
    #                 #         emplyr -= ln.amount
    #         employee_interest = ((emp * (interest_rate / 100)) * 9) / 12
    #         employer_contribution = ((volun * (interest_rate / 100)) * 9) / 12
    #         total = emp + volun + employee_interest + employer_contribution
    #         jul = self.env['pf.ledger.report'].create({
    #                 'employee_id': rec.employee_id.id,
    #                 'ledger_for_year': rec.ledger_for_year.id,
    #                 'branch_id': rec.employee_id.branch_id.id,
    #                 'month': str(month),
    #                 'epmloyee_contribution': str(round(emp)),
    #                 'voluntary_contribution': str(round(volun)),
    #                 'employer_contribution': str(round(emplyr)),
    #                 'interest_employee_voluntary': str(round(employee_interest)),
    #                 'interest_employer': str(round(employer_contribution)),
    #                 'total': str(round(total)),
    #             })
    #         #print('================creation lines================', cr_lines)
            
            

            
            
    #         emp = 0
    #         volun = 0
    #         emplyr = 0
    #         employee_interest = 0
    #         employer_contribution = 0
    #         month = 'August'
    #         for ln in pay_rules:
    #             if str(ln.date.month) == '8':
    #                 month = 'August'
    #                 if ln.pf_code == 'CPF':
    #                     if ln.type == 'Deposit':
    #                         emp += ln.amount
    #                     else:
    #                         emp -= ln.amount
    #                 elif ln.pf_code == 'VCPF' or ln.pf_code == 'CEPF' or ln.pf_code == 'CEPF + VCPF':
    #                     if ln.type == 'Deposit':
    #                         volun += ln.amount
    #                     else:
    #                         volun -= ln.amount
    #                 # elif ln.pf_code == 'CEPF':
    #                 #     if ln.type == 'Deposit':
    #                 #         emplyr += ln.amount
    #                 #     else:
    #                 #         emplyr -= ln.amount
    #         employee_interest = ((emp * (interest_rate / 100)) * 8) / 12
    #         employer_contribution = ((volun * (interest_rate / 100)) * 8) / 12
    #         total = emp + volun + employee_interest + employer_contribution
    #         aug = self.env['pf.ledger.report'].create({
    #                 'employee_id': rec.employee_id.id,
    #                 'ledger_for_year': rec.ledger_for_year.id,
    #                 'branch_id': rec.employee_id.branch_id.id,
    #                 'month': str(month),
    #                 'epmloyee_contribution': str(round(emp)),
    #                 'voluntary_contribution': str(round(volun)),
    #                 'employer_contribution': str(round(emplyr)),
    #                 'interest_employee_voluntary': str(round(employee_interest)),
    #                 'interest_employer': str(round(employer_contribution)),
    #                 'total': str(round(total)),
    #             })
    #         #print('================creation lines================', cr_lines)
            
            

            
            
    #         emp = 0
    #         volun = 0
    #         emplyr = 0
    #         employee_interest = 0
    #         employer_contribution = 0
    #         month = 'September'
    #         for ln in pay_rules:
    #             if str(ln.date.month) == '9':
    #                 month = 'September'
    #                 if ln.pf_code == 'CPF':
    #                     if ln.type == 'Deposit':
    #                         emp += ln.amount
    #                     else:
    #                         emp -= ln.amount
    #                 elif ln.pf_code == 'VCPF' or ln.pf_code == 'CEPF' or ln.pf_code == 'CEPF + VCPF':
    #                     if ln.type == 'Deposit':
    #                         volun += ln.amount
    #                     else:
    #                         volun -= ln.amount
    #                 # elif ln.pf_code == 'CEPF':
    #                 #     if ln.type == 'Deposit':
    #                 #         emplyr += ln.amount
    #                 #     else:
    #                 #         emplyr -= ln.amount
    #         employee_interest = ((emp * (interest_rate / 100)) * 7) / 12
    #         employer_contribution = ((volun * (interest_rate / 100)) * 7) / 12
    #         total = emp + volun + employee_interest + employer_contribution
    #         sept = self.env['pf.ledger.report'].create({
    #                 'employee_id': rec.employee_id.id,
    #                 'ledger_for_year': rec.ledger_for_year.id,
    #                 'branch_id': rec.employee_id.branch_id.id,
    #                 'month': str(month),
    #                 'epmloyee_contribution': str(round(emp)),
    #                 'voluntary_contribution': str(round(volun)),
    #                 'employer_contribution': str(round(emplyr)),
    #                 'interest_employee_voluntary': str(round(employee_interest)),
    #                 'interest_employer': str(round(employer_contribution)),
    #                 'total': str(round(total)),
    #             })
    #         #print('================creation lines================', cr_lines)
            
            

            
            
    #         emp = 0
    #         volun = 0
    #         emplyr = 0
    #         employee_interest = 0
    #         employer_contribution = 0
    #         month = 'October'
    #         for ln in pay_rules:
    #             if str(ln.date.month) == '10':
    #                 month = 'October'
    #                 if ln.pf_code == 'CPF':
    #                     if ln.type == 'Deposit':
    #                         emp += ln.amount
    #                     else:
    #                         emp -= ln.amount
    #                 elif ln.pf_code == 'VCPF' or ln.pf_code == 'CEPF' or ln.pf_code == 'CEPF + VCPF':
    #                     if ln.type == 'Deposit':
    #                         volun += ln.amount
    #                     else:
    #                         volun -= ln.amount
    #                 # elif ln.pf_code == 'CEPF':
    #                 #     if ln.type == 'Deposit':
    #                 #         emplyr += ln.amount
    #                 #     else:
    #                 #         emplyr -= ln.amount
    #         employee_interest = ((emp * (interest_rate / 100)) * 6) / 12
    #         employer_contribution = ((volun * (interest_rate / 100)) * 6) / 12
    #         total = emp + volun + employee_interest + employer_contribution
    #         oct = self.env['pf.ledger.report'].create({
    #                 'employee_id': rec.employee_id.id,
    #                 'ledger_for_year': rec.ledger_for_year.id,
    #                 'branch_id': rec.employee_id.branch_id.id,
    #                 'month': str(month),
    #                 'epmloyee_contribution': str(round(emp)),
    #                 'voluntary_contribution': str(round(volun)),
    #                 'employer_contribution': str(round(emplyr)),
    #                 'interest_employee_voluntary': str(round(employee_interest)),
    #                 'interest_employer': str(round(employer_contribution)),
    #                 'total': str(round(total)),
    #             })
    #         #print('================creation lines================', cr_lines)
            
            

            
            
    #         emp = 0
    #         volun = 0
    #         emplyr = 0
    #         employee_interest = 0
    #         employer_contribution = 0
    #         month = 'November'
    #         for ln in pay_rules:
    #             if str(ln.date.month) == '11':
    #                 month = 'November'
    #                 if ln.pf_code == 'CPF':
    #                     if ln.type == 'Deposit':
    #                         emp += ln.amount
    #                     else:
    #                         emp -= ln.amount
    #                 elif ln.pf_code == 'VCPF' or ln.pf_code == 'CEPF' or ln.pf_code == 'CEPF + VCPF':
    #                     if ln.type == 'Deposit':
    #                         volun += ln.amount
    #                     else:
    #                         volun -= ln.amount
    #                 # elif ln.pf_code == 'CEPF':
    #                 #     if ln.type == 'Deposit':
    #                 #         emplyr += ln.amount
    #                 #     else:
    #                 #         emplyr -= ln.amount
    #         employee_interest = ((emp * (interest_rate / 100)) * 5) / 12
    #         employer_contribution = ((volun * (interest_rate / 100)) * 5) / 12
    #         total = emp + volun + employee_interest + employer_contribution
    #         nov = self.env['pf.ledger.report'].create({
    #                 'employee_id': rec.employee_id.id,
    #                 'ledger_for_year': rec.ledger_for_year.id,
    #                 'branch_id': rec.employee_id.branch_id.id,
    #                 'month': str(month),
    #                 'epmloyee_contribution': str(round(emp)),
    #                 'voluntary_contribution': str(round(volun)),
    #                 'employer_contribution': str(round(emplyr)),
    #                 'interest_employee_voluntary': str(round(employee_interest)),
    #                 'interest_employer': str(round(employer_contribution)),
    #                 'total': str(round(total)),
    #             })
    #         #print('================creation lines================', cr_lines)
            
            
            
    #         emp = 0
    #         volun = 0
    #         emplyr = 0
    #         employee_interest = 0
    #         employer_contribution = 0
    #         month = 'December'
    #         for ln in pay_rules:
    #             if str(ln.date.month) == '12':
    #                 month = 'December'
    #                 if ln.pf_code == 'CPF':
    #                     if ln.type == 'Deposit':
    #                         emp += ln.amount
    #                     else:
    #                         emp -= ln.amount
    #                 elif ln.pf_code == 'VCPF' or ln.pf_code == 'CEPF' or ln.pf_code == 'CEPF + VCPF':
    #                     if ln.type == 'Deposit':
    #                         volun += ln.amount
    #                     else:
    #                         volun -= ln.amount
    #                 # elif ln.pf_code == 'CEPF':
    #                 #     if ln.type == 'Deposit':
    #                 #         emplyr += ln.amount
    #                 #     else:
    #                 #         emplyr -= ln.amount
    #         employee_interest = ((emp * (interest_rate / 100)) * 4) / 12
    #         employer_contribution = ((volun * (interest_rate / 100)) * 4) / 12
    #         total = emp + volun + employee_interest + employer_contribution
    #         dec = self.env['pf.ledger.report'].create({
    #                 'employee_id': rec.employee_id.id,
    #                 'ledger_for_year': rec.ledger_for_year.id,
    #                 'branch_id': rec.employee_id.branch_id.id,
    #                 'month': str(month),
    #                 'epmloyee_contribution': str(round(emp)),
    #                 'voluntary_contribution': str(round(volun)),
    #                 'employer_contribution': str(round(emplyr)),
    #                 'interest_employee_voluntary': str(round(employee_interest)),
    #                 'interest_employer': str(round(employer_contribution)),
    #                 'total': str(round(total)),
    #             })
    #         #print('================creation lines================', cr_lines)
    #         emp = 0
    #         volun = 0
    #         emplyr = 0
    #         employee_interest = 0
    #         employer_contribution = 0
    #         month = 'January'
    #         for ln in pay_rules:
    #             if str(ln.date.month) == '1':
    #                 month = 'January'
    #                 if ln.pf_code == 'CPF':
    #                     if ln.type == 'Deposit':
    #                         emp += ln.amount
    #                     else:
    #                         emp -= ln.amount
    #                 elif ln.pf_code == 'VCPF' or ln.pf_code == 'CEPF' or ln.pf_code == 'CEPF + VCPF':
    #                     if ln.type == 'Deposit':
    #                         volun += ln.amount
    #                     else:
    #                         volun -= ln.amount
    #                 # elif ln.pf_code == 'CEPF':
    #                 #     if ln.type == 'Deposit':
    #                 #         emplyr += ln.amount
    #                 #     else:
    #                 #         emplyr -= ln.amount
    #         employee_interest = ((emp * (interest_rate / 100)) * 3) / 12
    #         employer_contribution = ((volun * (interest_rate / 100)) * 3) / 12
    #         total = emp + volun + employee_interest + employer_contribution
    #         jan = self.env['pf.ledger.report'].create({
    #                 'employee_id': rec.employee_id.id,
    #                 'ledger_for_year': rec.ledger_for_year.id,
    #                 'branch_id': rec.employee_id.branch_id.id,
    #                 'month': str(month),
    #                 'epmloyee_contribution': str(round(emp)),
    #                 'voluntary_contribution': str(round(volun)),
    #                 'employer_contribution': str(round(emplyr)),
    #                 'interest_employee_voluntary': str(round(employee_interest)),
    #                 'interest_employer': str(round(employer_contribution)),
    #                 'total': str(round(total)),
    #             })
    #         #print('================creation lines================', cr_lines)
            
            

    #         emp = 0
    #         volun = 0
    #         emplyr = 0
    #         employee_interest = 0
    #         employer_contribution = 0
    #         month = 'February'
    #         for ln in pay_rules:
    #             if str(ln.date.month) == '2':
    #                 month = 'February'
    #                 if ln.pf_code == 'CPF':
    #                     if ln.type == 'Deposit':
    #                         emp += ln.amount
    #                     else:
    #                         emp -= ln.amount
    #                 elif ln.pf_code == 'VCPF' or ln.pf_code == 'CEPF' or ln.pf_code == 'CEPF + VCPF':
    #                     if ln.type == 'Deposit':
    #                         volun += ln.amount
    #                     else:
    #                         volun -= ln.amount
    #                 # elif ln.pf_code == 'CEPF':
    #                 #     if ln.type == 'Deposit':
    #                 #         emplyr += ln.amount
    #                 #     else:
    #                 #         emplyr -= ln.amount
    #         employee_interest = ((emp * (interest_rate / 100)) * 2) / 12
    #         employer_contribution = ((volun * (interest_rate / 100)) * 2) / 12
    #         total = emp + volun + employee_interest + employer_contribution
    #         feb = self.env['pf.ledger.report'].create({
    #                 'employee_id': rec.employee_id.id,
    #                 'ledger_for_year': rec.ledger_for_year.id,
    #                 'branch_id': rec.employee_id.branch_id.id,
    #                 'month': str(month),
    #                 'epmloyee_contribution': str(round(emp)),
    #                 'voluntary_contribution': str(round(volun)),
    #                 'employer_contribution': str(round(emplyr)),
    #                 'interest_employee_voluntary': str(round(employee_interest)),
    #                 'interest_employer': str(round(employer_contribution)),
    #                 'total': str(round(total)),
    #             })
    #         #print('================creation lines================', cr_lines)
            
            

            
            
    #         emp = 0
    #         volun = 0
    #         emplyr = 0
    #         employee_interest = 0
    #         employer_contribution = 0
    #         month = 'March'
    #         for ln in pay_rules:
    #             if str(ln.date.month) == '3':
    #                 month = 'March'
                    
    #                 if ln.pf_code == 'CPF':
    #                     if ln.type == 'Deposit':
    #                         emp += ln.amount
    #                     else:
    #                         emp -= ln.amount
    #                 elif ln.pf_code == 'VCPF' or ln.pf_code == 'CEPF' or ln.pf_code == 'CEPF + VCPF':
    #                     if ln.type == 'Deposit':
    #                         volun += ln.amount
    #                     else:
    #                         volun -= ln.amount
    #                 # elif ln.pf_code == 'CEPF':
    #                 #     if ln.type == 'Deposit':
    #                 #         emplyr += ln.amount
    #                 #     else:
    #                 #         emplyr -= ln.amount
    #         employee_interest = ((emp * (interest_rate / 100)) * 1) / 12
    #         employer_contribution = ((volun * (interest_rate / 100)) * 1) / 12
    #         total = emp + volun + employee_interest + employer_contribution
    #         mar = self.env['pf.ledger.report'].create({
    #                 'employee_id': rec.employee_id.id,
    #                 'ledger_for_year': rec.ledger_for_year.id,
    #                 'branch_id': rec.employee_id.branch_id.id,
    #                 'month': str(month),
    #                 'epmloyee_contribution': str(round(emp)),
    #                 'voluntary_contribution': str(round(volun)),
    #                 'employer_contribution': str(round(emplyr)),
    #                 'interest_employee_voluntary': str(round(employee_interest)),
    #                 'interest_employer': str(round(employer_contribution)),
    #                 'total': str(round(total)),
    #             })
    #         #print('================creation lines================', cr_lines)
    #         # FIXME: closing balance calculation will be updated in the future
    #         clos_bal = self.env['pf.ledger.report'].create({
    #                 'employee_id': rec.employee_id.id,
    #                 'ledger_for_year': rec.ledger_for_year.id,
    #                 'branch_id': rec.employee_id.branch_id.id,
    #                 'month': 'Closing',
    #                 'epmloyee_contribution': str(int(jan.epmloyee_contribution) + int(feb.epmloyee_contribution) + int(mar.epmloyee_contribution) + int(apr.epmloyee_contribution) + int(may.epmloyee_contribution) + int(jun.epmloyee_contribution) + int(jul.epmloyee_contribution) + int(aug.epmloyee_contribution) + int(sept.epmloyee_contribution) + int(oct.epmloyee_contribution) + int(nov.epmloyee_contribution) + int(dec.epmloyee_contribution)),
    #                 'voluntary_contribution': str(int(jan.voluntary_contribution) + int(feb.voluntary_contribution) + int(mar.voluntary_contribution) + int(apr.voluntary_contribution) + int(may.voluntary_contribution) + int(jun.voluntary_contribution) + int(jul.voluntary_contribution) + int(aug.voluntary_contribution) + int(sept.voluntary_contribution) + int(oct.voluntary_contribution) + int(nov.voluntary_contribution) + int(dec.voluntary_contribution)),
    #                 'employer_contribution': str(int(jan.employer_contribution) + int(feb.employer_contribution) + int(mar.employer_contribution) + int(apr.employer_contribution) + int(may.employer_contribution) + int(jun.employer_contribution) + int(jul.employer_contribution) + int(aug.employer_contribution) + int(sept.employer_contribution) + int(oct.employer_contribution) + int(nov.employer_contribution) + int(dec.employer_contribution)),
    #                 'interest_employee_voluntary': str(int(jan.interest_employee_voluntary) + int(feb.interest_employee_voluntary) + int(mar.interest_employee_voluntary) + int(apr.interest_employee_voluntary) + int(may.interest_employee_voluntary) + int(jun.interest_employee_voluntary) + int(jul.interest_employee_voluntary) + int(aug.interest_employee_voluntary) + int(sept.interest_employee_voluntary) + int(oct.interest_employee_voluntary) + int(nov.interest_employee_voluntary) + int(dec.interest_employee_voluntary)),
    #                 'interest_employer': str(int(jan.interest_employer) + int(feb.interest_employer) + int(mar.interest_employer) + int(apr.interest_employer) + int(may.interest_employer) + int(jun.interest_employer) + int(jul.interest_employer) + int(aug.interest_employer) + int(sept.interest_employer) + int(oct.interest_employer) + int(nov.interest_employer) + int(dec.interest_employer)),
    #                 'total': str(int(jan.total) + int(feb.total) + int(mar.total) + int(apr.total) + int(may.total) + int(jun.total) + int(jul.total) + int(aug.total) + int(sept.total) + int(oct.total) + int(nov.total) + int(dec.total)),
    #             })
    #         #print('================creation lines================', cr_lines)

    #         return {
    #             'name': 'PF Forecasted Ledger',
    #             'view_type': 'form',
    #             'view_mode': 'tree',
    #             'res_model': 'pf.ledger.report',
    #             'type': 'ir.actions.act_window',
    #             'target': 'current',
    #             'domain': [('employee_id', '=', rec.employee_id.id),('ledger_for_year', '=', rec.ledger_for_year.id)]
    #         }

    @api.multi
    def confirm_report(self):
        for rec in self:
            contract_id = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id),
                                                                ('state', '=', 'open')])
            basic = contract_id.wage 
            da = (contract_id.da/100) * basic
            company_id = self.env['res.company'].sudo().browse(rec.employee_id.user_id.company_id.id)
            start_date, end_date = rec.ledger_for_year.date_start, rec.ledger_for_year.date_end
            interest_rate = sum(company_id.pf_table.filtered(lambda x: x.from_date >= start_date and x.to_date <= end_date)\
                                .mapped('interest_rate'))
            cur_year, cur_month = date.today().year, date.today().month
            month_last = monthrange(cur_year, cur_month)[1]
            month_last_date = date(cur_year, cur_month, month_last)
            month_first_date = date(cur_year, cur_month, 1)
            eps = self.env['hr.payslip'].calculate_eps(rec.employee_id.id, basic, da, date_from=month_first_date, 
                                                            date_to=month_last_date)
            cepf = round(0.12 * (basic + da))
            vcpf = round(contract_id.voluntary_provident_fund)
            cpf = round((0.12 * (basic + da)) - eps)

            self.env['pf.ledger.report'].search([('employee_id', '=', rec.employee_id.id),
                                                ('ledger_for_year', '=', rec.ledger_for_year.id)]).unlink()
            closing_bal_pf_rec = self.env['pf.employee.details'].search([('pf_details_id.employee_id', '=', rec.employee_id.id),
                                                                    ('date', '<', rec.ledger_for_year.date_start)])

            deposit_employee_contribution = sum(closing_bal_pf_rec.filtered(lambda x: x.type == 'Deposit'\
                                        and x.pf_code in ['CEPF','VCPF',('CEPF + VCPF')]).mapped('amount'))
            withdraw_employee_contribution = sum(closing_bal_pf_rec.filtered(lambda x: x.type == 'Withdrawal' \
                                                and x.pf_code in ['CEPF','VCPF',('CEPF + VCPF')]).mapped('amount'))
            deposit_employer_contribution = sum(closing_bal_pf_rec.filtered(lambda x: x.type == 'Deposit'\
                                        and x.pf_code == 'CPF').mapped('amount'))
            withdraw_employer_contribution = sum(closing_bal_pf_rec.filtered(lambda x: x.type == 'Withdrawal' \
                                                and x.pf_code == 'CPF').mapped('amount'))
            opening_employee_balance, opening_employer_balance = (deposit_employee_contribution - withdraw_employee_contribution),\
                                                                    (deposit_employer_contribution - withdraw_employer_contribution)

            self.env['pf.ledger.report'].create({
                'employee_id': rec.employee_id.id,
                'branch_id': rec.employee_id.branch_id.id,
                'month': 'Opening',
                'ledger_for_year': rec.ledger_for_year.id,
                'epmloyee_contribution': str(round(opening_employer_balance)),
                'voluntary_contribution': str(round(opening_employee_balance)),
                'interest_employee_voluntary': '0',
                'interest_employer': '0',
                'total': str(round(opening_employee_balance + opening_employer_balance))
            })

            closing_emp_contrib, closing_emplr_contrib, closing_inters_emp, closing_interes_emplr, closing_total = 0, 0, 0, 0, 0

            for r in range(13):
                relative_from_date = start_date + relativedelta(months=r)
                month_last_day = monthrange(relative_from_date.year, relative_from_date.month)[1]
                relative_to_date = relative_from_date.replace(day=month_last_day)

                interest_employer_contribution = round(((cpf * interest_rate / 100) * (12 - r)) / 12)
                interest_employee_contribution = round((((cepf + vcpf) * interest_rate / 100) * (12 - r)) / 12)
                
                if r < 12:
                    self.env['pf.ledger.report'].create({
                        'employee_id': rec.employee_id.id,
                        'branch_id': rec.employee_id.branch_id.id,
                        'month': relative_to_date.strftime('%B'),
                        'ledger_for_year': rec.ledger_for_year.id,
                        'epmloyee_contribution': cpf,
                        'voluntary_contribution': cepf + vcpf,
                        'interest_employee_voluntary': str(interest_employer_contribution),
                        'interest_employer': str(interest_employee_contribution),
                        'total': str(cpf + (cepf + vcpf) +\
                                            interest_employer_contribution + interest_employee_contribution)
                    })

                    closing_emp_contrib += cpf
                    closing_emplr_contrib += (cepf + vcpf)
                    closing_inters_emp += interest_employee_contribution
                    closing_interes_emplr += interest_employer_contribution
                else:
                    self.env['pf.ledger.report'].create({
                        'employee_id': rec.employee_id.id,
                        'branch_id': rec.employee_id.branch_id.id,
                        'month': 'Closing',
                        'ledger_for_year': rec.ledger_for_year.id,
                        'epmloyee_contribution': closing_emplr_contrib,
                        'voluntary_contribution': closing_emp_contrib,
                        'interest_employee_voluntary': str(closing_interes_emplr),
                        'interest_employer': str(closing_inters_emp),
                        'total': str(closing_emplr_contrib + closing_emp_contrib +\
                                            closing_interes_emplr + closing_inters_emp)
                    })
            
        return {
            'name': 'PF Forecasted Ledger',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'pf.ledger.report',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('employee_id', '=', rec.employee_id.id),('ledger_for_year', '=', rec.ledger_for_year.id)]
        }



class ActualPFLedgerWizard(models.TransientModel):
    _name = 'stpi_pf_ledger_wizard'
    _description = 'Actual PF Ledger Wizard'


    def _get_employee_ids(self):
        domain = []
        if self.env.user.has_group('pf_withdrawl.group_pf_withdraw_approver'):
            domain += [('branch_id', 'in', self.env.user.branch_ids.mapped('id'))]
        else:
            domain += [('user_id', '=', self.env.uid)]
        return domain

    employee_id = fields.Many2one('hr.employee','Requested By', 
                    default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).id,
                    domain=_get_employee_ids)
    date_range_id = fields.Many2one('date.range', 'Ledger for the year')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    branch_id = fields.Many2one('res.branch', 'Center')
    job_id = fields.Many2one('hr.job', 'Functional Designation')

    @api.onchange('employee_id', 'date_range_id')
    def get_details(self):
        if self.employee_id:
            self.branch_id, self.job_id = self.employee_id.branch_id.id, self.employee_id.job_id.id
        if self.date_range_id:
            self.from_date, self.to_date = self.date_range_id.date_start, self.date_range_id.date_end

    @api.multi
    def confirm_report(self):
        for rec in self:
            company_id = self.env['res.company'].sudo().browse(rec.employee_id.user_id.company_id.id)
            interest_rate = sum(company_id.pf_table.filtered(lambda x: x.from_date >= rec.from_date and x.to_date <= rec.to_date)\
                                .mapped('interest_rate'))
            self.env['stpi_pf_ledger_report_main'].search([('employee_id', '=', rec.employee_id.id),
                                                        ('date_range_id', '=', rec.date_range_id.id)]).unlink()
            self.env['stpi_pf_ledger_report'].search([('employee_id', '=', rec.employee_id.id),
                                                        ('date_range_id', '=', rec.date_range_id.id)]).unlink()

            closing_bal_pf_rec = self.env['pf.employee.details'].search([('pf_details_id.employee_id', '=', rec.employee_id.id),
                                                                            ('date', '<', rec.from_date)])
            deposit_employee_contribution = sum(closing_bal_pf_rec.filtered(lambda x: x.type == 'Deposit'\
                                        and x.pf_code in ['CEPF','VCPF',('CEPF + VCPF')]).mapped('amount'))
            withdraw_employee_contribution = sum(closing_bal_pf_rec.filtered(lambda x: x.type == 'Withdrawal' \
                                                and x.pf_code in ['CEPF','VCPF',('CEPF + VCPF')]).mapped('amount'))
            deposit_employer_contribution = sum(closing_bal_pf_rec.filtered(lambda x: x.type == 'Deposit'\
                                        and x.pf_code == 'CPF').mapped('amount'))
            withdraw_employer_contribution = sum(closing_bal_pf_rec.filtered(lambda x: x.type == 'Withdrawal' \
                                                and x.pf_code == 'CPF').mapped('amount'))
            opening_employee_deposit, opening_employer_deposit = deposit_employee_contribution, deposit_employer_contribution

            pf_employee = self.env['pf.employee'].sudo().search([('employee_id', '=', rec.employee_id.id)])

            main_record = self.env['stpi_pf_ledger_report_main'].create({
                    'employee_id': rec.employee_id.id,
                    'branch_id': rec.employee_id.branch_id.id,
                    'date_range_id': rec.date_range_id.id,
                    'is_closed': pf_employee.is_closed,
                    'closed_on': pf_employee.closed_on,
            })

            self.env['stpi_pf_ledger_report'].create({
                'employee_id': rec.employee_id.id,
                'branch_id': rec.employee_id.branch_id.id,
                'month': 'Opening',
                'date_range_id': rec.date_range_id.id,
                'employee_contribution': 0,
                'employee_volun_contribution': 0,
                'deposit_employer_contribution': deposit_employer_contribution,
                'deposit_employee_contribution': deposit_employee_contribution,
                'withdraw_employer_contribution': withdraw_employer_contribution,
                'withdraw_employee_contribution': withdraw_employee_contribution,
                'total_employer_contribution': round(deposit_employer_contribution - withdraw_employer_contribution),
                'total_employee_contribution': round(deposit_employee_contribution - withdraw_employee_contribution),
                'total_pf_contribution': round(deposit_employer_contribution - withdraw_employer_contribution) +\
                                            round(deposit_employee_contribution - withdraw_employee_contribution),
                'main_rel' : main_record.id
            })

            ledger_year_pf_rec = self.env['pf.employee.details'].search([('pf_details_id.employee_id', '=', rec.employee_id.id),
                                                                        ('date', '>=', rec.from_date), ('date', '<=', rec.to_date)])
            total_opening_employer_balance = round(deposit_employer_contribution - withdraw_employer_contribution)
            total_opening_employee_balance = round(deposit_employee_contribution - withdraw_employee_contribution)
            # Logic to show PF ledger report till current month
            # if rec.date_range_id.date_start <= date.today() <= rec.date_range_id.date_end:
            #     if date.today().day != 1:
            #         month_last_day = monthrange(date.today().year, date.today().month)[1]
            #         relative_to_date = date.today().replace(day=month_last_day)
            #     else:
            #         relative_to_date = date.today()
            #     range_count = relativedelta(relative_to_date, rec.date_range_id.date_start).months + 2
            # else:
            #     range_count = 13
            range_count = 13

            for r in range(range_count):
                relative_from_date = rec.from_date + relativedelta(months=r)
                month_last_day = monthrange(relative_from_date.year, relative_from_date.month)[1]
                relative_to_date = relative_from_date.replace(day=25)
                monthly_pf_rec = ledger_year_pf_rec.filtered(lambda x: x.date >= relative_from_date and x.date <= relative_to_date)

                employee_contribution = sum(monthly_pf_rec.filtered(lambda x: x.type == 'Deposit' and x.pf_code == 'CEPF')\
                                                                .mapped('amount'))
                employee_volun_contribution = sum(monthly_pf_rec.filtered(lambda x: x.type == 'Deposit' and x.pf_code == 'VCPF')\
                                                                .mapped('amount'))
                deposit_employer_contribution = sum(monthly_pf_rec.filtered(lambda x: x.type == 'Deposit' and x.pf_code == 'CPF')\
                                                                .mapped('amount'))
                deposit_employee_contribution = sum(monthly_pf_rec.filtered(lambda x: x.type == 'Deposit' and\
                                                            x.pf_code in ['CEPF','VCPF',('CEPF + VCPF')]).mapped('amount'))
                withdraw_employer_contribution = sum(monthly_pf_rec.filtered(lambda x: x.type == 'Withdrawal' and x.pf_code == 'CPF')\
                                                                .mapped('amount'))
                withdraw_employee_contribution = sum(monthly_pf_rec.filtered(lambda x: x.type == 'Withdrawal' and\
                                                            x.pf_code in ['CEPF','VCPF',('CEPF + VCPF')]).mapped('amount'))
                total_opening_employer_balance += (deposit_employer_contribution - withdraw_employer_contribution)
                total_opening_employee_balance += (deposit_employee_contribution - withdraw_employee_contribution)

                if r < (range_count - 1):
                    self.env['stpi_pf_ledger_report'].create({
                        'employee_id': rec.employee_id.id,
                        'branch_id': rec.employee_id.branch_id.id,
                        'month': relative_to_date.strftime('%B'),
                        'date_range_id': rec.date_range_id.id,
                        'employee_contribution': employee_contribution,
                        'employee_volun_contribution': employee_volun_contribution,
                        'deposit_employer_contribution': deposit_employer_contribution,
                        'deposit_employee_contribution': deposit_employee_contribution,
                        'withdraw_employer_contribution': withdraw_employer_contribution,
                        'withdraw_employee_contribution': withdraw_employee_contribution,
                        'total_employer_contribution': total_opening_employer_balance,
                        'total_employee_contribution': total_opening_employee_balance,
                        'total_pf_contribution': total_opening_employer_balance + total_opening_employee_balance,
                        'main_rel' : main_record.id
                    })
                else:
                    # FIXME: closing balance calculation will be updated in the future
                    employee_contribution = sum(ledger_year_pf_rec.filtered(lambda x: x.type == 'Deposit' and x.pf_code == 'CEPF' and x.date <= relative_to_date)\
                                                                .mapped('amount'))
                    employee_volun_contribution = sum(ledger_year_pf_rec.filtered(lambda x: x.type == 'Deposit' and x.pf_code == 'VCPF' and x.date <= relative_to_date)\
                                                                .mapped('amount'))
                    closing_employer_deposit = sum(ledger_year_pf_rec.filtered(lambda x: x.type == 'Deposit' and x.pf_code == 'CPF' and x.date <= relative_to_date)\
                                                                .mapped('amount'))
                    closing_employee_deposit = sum(ledger_year_pf_rec.filtered(lambda x: x.type == 'Deposit' and x.date <= relative_to_date and\
                                                            x.pf_code in ['CEPF','VCPF',('CEPF + VCPF')]).mapped('amount'))
                    closing_employer_withdraw = sum(ledger_year_pf_rec.filtered(lambda x: x.type == 'Withdrawal' and x.date <= relative_to_date\
                                                                and x.pf_code == 'CPF').mapped('amount'))
                    closing_employee_withdraw = sum(ledger_year_pf_rec.filtered(lambda x: x.type == 'Withdrawal' and x.date <= relative_to_date and\
                                                            x.pf_code in ['CEPF','VCPF',('CEPF + VCPF')]).mapped('amount'))

                    total_employeer_interest = sum(ledger_year_pf_rec.filtered(lambda x: x.type == 'Deposit' and x.pf_code == 'CPF' and 'Interest' in x.reference
                                                                                    and rec.date_range_id.date_start <= x.date <= rec.date_range_id.date_end).mapped('amount'))


                    total_employee_interest = sum(ledger_year_pf_rec.filtered(lambda x: x.type == 'Deposit' and x.pf_code == 'CEPF + VCPF' and 'Interest' in x.reference
                                                                                    and rec.date_range_id.date_start <= x.date <= rec.date_range_id.date_end).mapped('amount'))


                    self.env['stpi_pf_ledger_report'].create({
                        'employee_id': rec.employee_id.id,
                        'branch_id': rec.employee_id.branch_id.id,
                        'month': 'Interest',
                        'date_range_id': rec.date_range_id.id,
                        'employee_contribution': 0,
                        'employee_volun_contribution': 0,
                        'deposit_employer_contribution': total_employeer_interest,
                        'deposit_employee_contribution': total_employee_interest,
                        'withdraw_employer_contribution': 0,
                        'withdraw_employee_contribution': 0,
                        'total_employer_contribution': total_employeer_interest,
                        'total_employee_contribution': total_employee_interest,
                        'total_pf_contribution': total_employeer_interest + total_employee_interest,
                        'main_rel' : main_record.id
                    }) 

                    self.env['stpi_pf_ledger_report'].create({
                        'employee_id': rec.employee_id.id,
                        'branch_id': rec.employee_id.branch_id.id,
                        'month': 'Closing',
                        'date_range_id': rec.date_range_id.id,
                        'employee_contribution': employee_contribution,
                        'employee_volun_contribution': employee_volun_contribution,
                        'deposit_employer_contribution': closing_employer_deposit + opening_employer_deposit,
                        'deposit_employee_contribution': closing_employee_deposit + opening_employee_deposit,
                        'withdraw_employer_contribution': closing_employer_withdraw,
                        'withdraw_employee_contribution': closing_employee_withdraw,
                        'total_employer_contribution': total_opening_employer_balance,
                        'total_employee_contribution': total_opening_employee_balance,
                        'total_pf_contribution': total_opening_employer_balance + total_opening_employee_balance,
                        'main_rel' : main_record.id
                    }) 
        return {
            'name': 'PF Ledger',
            'view_type': 'form',
            'res_id' : main_record.id,
            'view_mode': 'form',
            'res_model': 'stpi_pf_ledger_report_main',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('employee_id', '=', rec.employee_id.id),('date_range_id', '=', rec.date_range_id.id)]
        }