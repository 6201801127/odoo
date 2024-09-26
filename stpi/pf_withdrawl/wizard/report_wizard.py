from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import time, datetime,timedelta
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date, datetime
import datetime
from odoo.tools import float_utils
from collections import defaultdict
from pytz import utc


class WizardLateComing(models.TransientModel):
    _name = 'pf.ledger.wizard'
    _description = 'PF Ledger'


    # def _default_employee(self):
    #     return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    # def _default_from_date(self):
    #     epoch_year = date.today().year
    #     year_start = date(epoch_year, 4, 1)
    #     return year_start
    #
    # def _default_to_date(self):
    #     epoch_year = date.today().year
    #     year_end = date(epoch_year, 3, 31)
    #     return year_end

    # @api.onchange('ledger_for_year')
    # def get_dates(self):
    #     for rec in self:
    #         rec.from_date = rec.ledger_for_year.date_start
    #         rec.to_date = rec.ledger_for_year.date_end

    @api.onchange('employee_id')
    def get_branch_job(self):
        for rec in self:
            rec.branch_id = rec.employee_id.branch_id
            rec.job_id = rec.employee_id.job_id

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    
    report_of = fields.Selection([('pf_ledger','PF Ledger'),
                                  ],string="Report On", default='pf_ledger')
    employee_id = fields.Many2one('hr.employee','Requested By', default=_default_employee)
    interest_rate = fields.Float('Interest Rate')
    ledger_for_year = fields.Many2one('date.range', string='Ledger for the year')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    branch_id = fields.Many2one('res.branch', string='Center')
    job_id = fields.Many2one('hr.job', string='Functional Designation')




    @api.onchange('branch_id','ledger_for_year')
    @api.constrains('branch_id','ledger_for_year')
    def check_existing_branch_sr(self):
        self.from_date = self.ledger_for_year.date_start
        self.to_date = self.ledger_for_year.date_end
        company = self.env['res.company'].search([('id', '=', self.env.user.company_id.id)], limit=1)
        if company:
            for com in company:
                if self.ledger_for_year.date_start and self.ledger_for_year.date_end and self.branch_id:
                    for line in com.pf_table:
                        if line.from_date >= self.ledger_for_year.date_start and line.to_date <= self.ledger_for_year.date_end:
                            self.interest_rate = line.interest_rate



    @api.multi
    def confirm_report(self):
        for rec in self:
            X = rec.interest_rate
            print('=============X===============', X)
            dr = self.env['pf.ledger.report'].search([('employee_id', '=', rec.employee_id.id),('ledger_for_year', '=', rec.ledger_for_year.id)])
            for lines in dr:
                lines.unlink()
            from_date = rec.from_date = rec.ledger_for_year.date_start
            to_date = rec.to_date = rec.ledger_for_year.date_end

            print('===============from date initial===================', from_date)
            print('===============To date initial===================', rec.to_date)
            while from_date < to_date:
                print('===============from date===================',from_date)
                print('===============To date===================',rec.to_date)
                pay_rules = self.env['hr.payslip.line'].search(
                    [('slip_id.employee_id', '=', rec.employee_id.id),
                     ('slip_id.state', '=', 'done'),
                     ('slip_id.date_from', '>=', from_date),
                     ('slip_id.date_to', '<', from_date + relativedelta(months=1)),
                     ('salary_rule_id.pf_register', '=', True),
                     ])
                print('=============Payslip===============',pay_rules)
                emp = 0
                volun = 0
                emplyr = 0
                employee_interest = 0
                employer_contribution = 0
                for ln in pay_rules:
                    if ln.salary_rule_id.pf_eve_type == 'employee':
                        emp += ln.total
                    elif ln.salary_rule_id.pf_eve_type == 'voluntary':
                        volun += ln.total
                    elif ln.salary_rule_id.pf_eve_type == 'employer':
                        emplyr += ln.total
                print('==================Employee===================',emp)
                print('==================Voluntary===================',volun)
                print('==================Employer===================',emplyr)
                if str(from_date.month) == '1':
                    month = 'January'
                    employee_interest = (((emp + volun) * X) * 3) / 12
                    employer_contribution = (((emplyr) * X) * 3) / 12
                elif str(from_date.month) == '2':
                    month = 'February'
                    employee_interest = (((emp + volun) * X) * 2) / 12
                    employer_contribution = (((emplyr) * X) * 2) / 12
                elif str(from_date.month) == '3':
                    month = 'March'
                    employee_interest = (((emp + volun) * X) * 1) / 12
                    employer_contribution = (((emplyr) * X) * 1) / 12
                elif str(from_date.month) == '4':
                    month = 'April'
                    employee_interest = (((emp + volun) * X) * 12) / 12
                    employer_contribution = (((emplyr) * X) * 12) / 12
                elif str(from_date.month) == '5':
                    month = 'May'
                    employee_interest = (((emp + volun) * X) * 11) / 12
                    employer_contribution = (((emplyr) * X) * 11) / 12
                elif str(from_date.month) == '6':
                    month = 'June'
                    employee_interest = (((emp + volun) * X) * 10) / 12
                    employer_contribution = (((emplyr) * X) * 10) / 12
                elif str(from_date.month) == '7':
                    month = 'July'
                    employee_interest = (((emp + volun) * X) * 9) / 12
                    employer_contribution = (((emplyr) * X) * 9) / 12
                elif str(from_date.month) == '8':
                    month = 'August'
                    employee_interest = (((emp + volun) * X) * 8) / 12
                    employer_contribution = (((emplyr) * X) * 8) / 12
                elif str(from_date.month) == '9':
                    month = 'September'
                    employee_interest = (((emp + volun) * X) * 7) / 12
                    employer_contribution = (((emplyr) * X) * 7) / 12
                elif str(from_date.month) == '10':
                    month = 'October'
                    employee_interest = (((emp + volun) * X) * 6) / 12
                    employer_contribution = (((emplyr) * X) * 6) / 12
                elif str(from_date.month) == '11':
                    month = 'November'
                    employee_interest = (((emp + volun) * X) * 5) / 12
                    employer_contribution = (((emplyr) * X) * 5) / 12
                elif str(from_date.month) == '12':
                    month = 'December'
                    employee_interest = (((emp + volun) * X) * 4) / 12
                    employer_contribution = (((emplyr) * X) * 4) / 12
                else:
                    month = ''
                    employee_interest = 0
                    employer_contribution = 0
                total = emp + volun + emplyr + employee_interest + employer_contribution
                cr_lines = self.env['pf.ledger.report'].create({
                    'employee_id': rec.employee_id.id,
                    'ledger_for_year': rec.ledger_for_year.id,
                    'branch_id': rec.employee_id.branch_id.id,
                    'month': str(month),
                    'epmloyee_contribution': str(round(emp)),
                    'voluntary_contribution': str(round(volun)),
                    'employer_contribution': str(round(emplyr)),
                    'interest_employee_voluntary': str(round(employee_interest)),
                    'interest_employer': str(round(employer_contribution)),
                    'total': str(round(total)),
                })
                from_date = from_date + relativedelta(months=1)
                print('================creation lines================', cr_lines)
            return {
                'name': 'PF Ledger',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'pf.ledger.report',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('employee_id', '=', rec.employee_id.id),('ledger_for_year', '=', rec.ledger_for_year.id)]
            }


    #
    # @api.multi
    # def confirm_report(self):
    #     for rec in self:
    #         dr = self.env['pf.ledger.report'].search([('branch_id', 'in', rec.branch_ids.ids)])
    #         for lines in dr:
    #             lines.unlink()
    #         dr_b = self.env['resource.calendar.leaves'].search([('calendar_id.branch_id', 'in', rec.branch_ids.ids)])
    #         for emp in dr_b:
    #             print('========================================================',emp.date)
    #         # for emp in rec.employee_id.resource_calendar_id.global_leave_ids:
    #             if rec.from_date and rec.to_date and rec.from_date <= emp.date <= rec.to_date:
    #                 month = ''
    #                 if str(emp.date.month) == '1':
    #                     month = 'January'
    #                 elif str(emp.date.month) == '2':
    #                     month = 'February'
    #                 elif str(emp.date.month) == '3':
    #                     month = 'March'
    #                 elif str(emp.date.month) == '4':
    #                     month = 'April'
    #                 elif str(emp.date.month) == '5':
    #                     month = 'May'
    #                 elif str(emp.date.month) == '6':
    #                     month = 'June'
    #                 elif str(emp.date.month) == '7':
    #                     month = 'July'
    #                 elif str(emp.date.month) == '8':
    #                     month = 'August'
    #                 elif str(emp.date.month) == '9':
    #                     month = 'September'
    #                 elif str(emp.date.month) == '10':
    #                     month = 'October'
    #                 elif str(emp.date.month) == '11':
    #                     month = 'November'
    #                 elif str(emp.date.month) == '12':
    #                     month = 'December'
    #                 else:
    #                     month = ''
    #                 cr = self.env['pf.ledger.report'].create({
    #                     'name': emp.name,
    #                     'date': emp.date,
    #                     'branch_id': emp.calendar_id.branch_id.id,
    #                     'holiday_id': emp.calendar_id.id,
    #                     'month': month,
    #                 })
    #
    #     return {
    #         'name': 'Leave Holiday Report',
    #         'view_type': 'form',
    #         'view_mode': 'tree',
    #         'res_model': 'pf.ledger.report',
    #         'type': 'ir.actions.act_window',
    #         'target': 'current',
    #         'domain': [('branch_id', '=', self.branch_ids.ids)],
    #         'context': {
    #                         'name': 'Sunday',
    #                     }
    #         }
    #

    #
    # @api.multi
    # def confirm_existing_report(self):
    #     for rec in self:
    #         dr = self.env['pf.ledger.report'].search([('branch_id', 'in', rec.branch_ids.ids)])
    #         for lines in dr:
    #             lines.unlink()
    #         emp_ids = self.env['hr.employee'].search([('branch_id', 'in', rec.branch_ids.ids)])
    #         for employees in emp_ids:
    #             for emp in employees.resource_calendar_id.global_leave_ids:
    #                 if rec.from_date <= emp.date <= rec.to_date:
    #                     month = ''
    #                     if str(emp.date.month) == '1':
    #                         month = 'January'
    #                     elif str(emp.date.month) == '2':
    #                         month = 'February'
    #                     elif str(emp.date.month) == '3':
    #                         month = 'March'
    #                     elif str(emp.date.month) == '4':
    #                         month = 'April'
    #                     elif str(emp.date.month) == '5':
    #                         month = 'May'
    #                     elif str(emp.date.month) == '6':
    #                         month = 'June'
    #                     elif str(emp.date.month) == '7':
    #                         month = 'July'
    #                     elif str(emp.date.month) == '8':
    #                         month = 'August'
    #                     elif str(emp.date.month) == '9':
    #                         month = 'September'
    #                     elif str(emp.date.month) == '10':
    #                         month = 'October'
    #                     elif str(emp.date.month) == '11':
    #                         month = 'November'
    #                     elif str(emp.date.month) == '12':
    #                         month = 'December'
    #                     else:
    #                         month = ''
    #                     cr = self.env['pf.ledger.report'].create({
    #                         'employee_id': rec.employee_id.id,
    #                         'name': emp.name,
    #                         'date': emp.date,
    #                         'branch_id': emp.calendar_id.branch_id.id,
    #                         'holiday_id': emp.calendar_id.id,
    #                         'month': month,
    #                     })
    #
    #     return {
    #         'name': 'Leave Holiday Report',
    #         'view_type': 'form',
    #         'view_mode': 'tree',
    #         'res_model': 'pf.ledger.report',
    #         'type': 'ir.actions.act_window',
    #         'target': 'current',
    #         'domain': [('branch_id', 'in', self.branch_ids.ids)],
    #     }
