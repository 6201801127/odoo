# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
import datetime
from datetime import date, datetime, time
from odoo.exceptions import ValidationError, UserError


class KwPayslipLedger(models.Model):
    _name = 'kw_payslip_ledger'
    _description = "Payslip Ledger"

    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
    ]

    # def _default_financial_yr(self):
    #     fiscal_years = self.env['account.fiscalyear'].search([])
    #     for rec in fiscal_years:
    #         current_fiscal = self.env['account.fiscalyear'].search(
    #             [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
    #         return current_fiscal

    # year = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always',
    #                        default=_default_financial_yr, required=True)
    year = fields.Selection(string='Year', selection='_get_year_list', default=str(date.today().year), required=True)
    
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month), required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True,
                                  domain="['|', ('active', '=', False), ('active', '=', True)]")
    contract_id = fields.Many2one('hr.contract', string="Contract",  readonly=True)
    boolean_readonly = fields.Boolean(string='Printed In Payslip', default=False)
    salary_rule_id = fields.Many2one('hr.salary.rule', string="Rule", required=True,
                                     domain="[('code', 'in', ['CMT', 'HID','TDS','PTD','NPS'])]", )
    amount = fields.Integer(string="Amount", required=True)
    current_month = fields.Boolean(search="_search_current_month", compute='_compute_current_month')
    job_branch_id  = fields.Many2one('kw_res_branch')
    company_id = fields.Many2one('res.company')

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year + 7, 2010, -1)]

    @api.onchange('employee_id')
    def change_contract(self):
        self.contract_id = self.env['hr.contract'].sudo().search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')])
        self.job_branch_id = self.employee_id.job_branch_id.id
        self.company_id = self.employee_id.company_id.id
        

    @api.constrains('employee_id', 'year', 'month', 'salary_rule_id')
    def validate_lunch_expenses(self):
        for rec in self:
            record = self.env['kw_payslip_ledger'].sudo().search(
                [('year', '=', rec.year), ('month', '=', rec.month), ('employee_id', '=', rec.employee_id.id),
                 ('salary_rule_id', '=', rec.salary_rule_id.id)]) - self
            if record:
                res = [item[1] for item in rec.MONTH_LIST if item[0] == record.month]
                month = res[0]
                raise ValidationError(
                    f"Duplicate entry found for {record.employee_id.emp_display_name} for {month}-{record.year}.")


    @api.onchange('year', 'month')
    def onchange_company(self):
        for rec in self:
            if rec.year and rec.month:
                emp_lst = []
                emp_rec = self.env['hr.employee']
                emp = emp_rec.sudo().search([('enable_payroll', '=', 'yes'), ('active', '=', True)])
                inactive_emp = emp_rec.sudo().search([('enable_payroll', '=', 'yes'), ('active', '=', False),('last_working_day','!=',False)])
                active_filter = emp.filtered(
                    lambda x: x.date_of_joining.month <= int(rec.month) if x.date_of_joining.year == int(
                        rec.year) else x.date_of_joining.year < int(rec.year))
                inactive_filter = inactive_emp.filtered(
                    lambda x: x.last_working_day.month >= int(rec.month) if x.last_working_day.year == int(
                        rec.year) else x.last_working_day.year < int(rec.year))
                att_emp = self.env['kw_payroll_monthly_attendance_report'].sudo().search([('attendance_year', '=', int(rec.year)),
                                                                                          ('attendance_month', '=', int(rec.month)),
                                                                                          ('emp_status','=',3)])
                for attendance in att_emp:
                    emp_lst.append(attendance.employee_id.id)
                for employee in active_filter:
                    emp_lst.append(employee.id)
                for employee in inactive_filter:
                    emp_lst.append(employee.id)

                return {'domain': {
                    'employee_id': [('id', 'in', emp_lst), '|', ('active', '=', False), ('active', '=', True)]}}

    @api.multi
    def _compute_current_month(self):
        for record in self:
            pass

    @api.multi
    def _search_current_month(self, operator, value):
        month = date.today().month
        year = date.today().year
        return ['&', ('month', '=', str(month)), ('year', '=', str(year))]