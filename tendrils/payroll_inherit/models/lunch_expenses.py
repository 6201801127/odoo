# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
import datetime,calendar
from datetime import date, datetime, time
from odoo.exceptions import ValidationError, UserError


class lunch_expenses(models.Model):
    _name = 'lunch_expenses'
    _description = "Lunch Expenses"

    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
    ]

    def _get_fiscal_year(self):
        current_date = datetime.now().date()
        fy_rec = self.env['account.fiscalyear'].sudo().search(
            [('date_start', '<=', current_date), ('date_stop', '>=', current_date)], limit=1)
        for record in self:
            record.fiscal_year_id = fy_rec.id

    fiscal_year_id = fields.Many2one('account.fiscalyear', string="Fiscal Year", compute="_get_fiscal_year", store=True)

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year, 1998, -1)]

    @api.multi
    def _compute_salary_rule(self):
        domain = []
        rules = self.env['hr.salary.rule'].sudo().search([])
        if self.env.context.get('other_deduction'):
            other = rules.filtered(lambda x: x.code == 'OD')
            domain = [('id','=',other.id)]
            return domain
        else:
            other = rules.filtered(lambda x: x.code in ('OD','FC'))
            domain = [('id','=',other.ids)]
            return domain 


    year = fields.Selection(string='Year', selection='_get_year_list', default=str(date.today().year),
                            required=True)
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month), required=True)
    department_id = fields.Char(related='employee_id.department_id.name', string="Department", store=True)
    division = fields.Char(related='employee_id.division.name', string="Division")
    section = fields.Char(related='employee_id.section.name', string="Section")
    practice = fields.Char(related='employee_id.practise.name', string="Practice")
    country_id = fields.Many2one('res.country', string="Country")
    employee_id = fields.Many2one('hr.employee', string="Name", required=True,
                                  domain="['|', ('active', '=', False), ('active', '=', True)]")
    designation = fields.Char(related='employee_id.job_id.name', string="Designation")
    # reg_meal        = fields.Integer(string="Guest Meal",required=True)
    tot_meal = fields.Integer(string="Amount")
    amount = fields.Integer(string="Amount", required=True)
    deduction_id = fields.Many2one('hr.salary.rule', string="Select Deduction", domain=_compute_salary_rule)
                                #    domain="[('category_id.name','=','Variable Deduction')]"
    # guest_meal      = fields.Integer(string="Regular Meal Amount",required=True)
    boolean_readonly = fields.Boolean(string='Printed In Payslip', default=False)
    current_month = fields.Boolean(search="_search_current_month", compute='_compute_current_month')
    purpose = fields.Text()
    company_id = fields.Many2one('res.company')

    @api.constrains('employee_id', 'year', 'month', 'amount')
    def validate_lunch_expenses(self):
        for rec in self:
            record = self.env['lunch_expenses'].sudo().search(
                [('year', '=', rec.year), ('month', '=', rec.month), ('employee_id', '=', rec.employee_id.id),
                 ('deduction_id', '=', rec.deduction_id.id)]) - self
            if record:
                res = [item[1] for item in rec.MONTH_LIST if item[0] == record.month]
                month = res[0]
                raise ValidationError(
                    f"Duplicate entry found for {record.employee_id.emp_display_name} for {month}-{record.year}.")
            # if rec.amount <= 0:
            #     raise ValidationError("Enter a Valid Amount")

    # @api.onchange('employee_id')
    # def onchange_employee_id(self):
    #     for rec in self:
    #         if rec.employee_id.contract_id.struct_id:
    #             ids = []
    #             for rule in rec.employee_id.contract_id.struct_id.rule_ids:
    #                 if rule.category_id.name == 'Variable Deduction':
    #                     ids.append(rule.id)
    #             return {'domain': {'deduction_id': [('id', 'in', ids)]}}

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id.contract_id.struct_id:
            ids = []
            for rule in self.employee_id.contract_id.struct_id.rule_ids:
                if rule.category_id.name == 'Variable Deduction':
                    ids.append(rule.id)
            # Get the company_id from the employee_id
            self.company_id = self.employee_id.company_id.id
            return {'domain': {'deduction_id': [('id', 'in', ids)]}}

    @api.multi
    def _compute_current_month(self):
        for record in self:
            pass

    @api.multi
    def _search_current_month(self, operator, value):
        month = date.today().month
        year = date.today().year
        return ['&', ('month', '=', str(month)), ('year', '=', str(year))]

    @api.onchange('year', 'month')
    def onchange_company(self):
        for rec in self:
            if rec.year and rec.month:
                date_part = date(int(rec.year), int(self.month), 1)
                emp_lst = []
                emp_rec = self.env['hr.employee']
                emp = emp_rec.sudo().search([('enable_payroll', '=', 'yes'), ('active', '=', True)])
                inactive_emp = emp_rec.sudo().search([('enable_payroll', '=', 'yes'), ('active', '=', False),('last_working_day','!=',False)])
                last_date = calendar.monthrange(int(rec.year), int(rec.month))[1]
                date_of_join = datetime(int(rec.year), int(rec.month), int(last_date))
                active_filter = emp.filtered(
                    lambda x: x.date_of_joining <= date_of_join.date())
                previous_month = datetime(int(rec.year), int(rec.month)-1, 26) if int(rec.month) != 1 else datetime(int(rec.year)-1,12, 26)
                previous_month_date = previous_month.date()
                inactive_filter = inactive_emp.filtered(
                    lambda x: x.last_working_day >= previous_month_date and x.date_of_joining <= date_of_join.date())
                # att_emp = self.env['kw_payroll_monthly_attendance_report'].sudo().search([('attendance_year', '=', int(rec.year)),
                #                                                                           ('attendance_month', '=', int(rec.month)),
                #                                                                           ('emp_status','=',3)])
                # for attendance in att_emp:
                #     emp_lst.append(attendance.employee_id.id)
                for employee in active_filter:
                    emp_lst.append(employee.id)
                for employee in inactive_filter:
                    emp_lst.append(employee.id)

                return {'domain': {
                    'employee_id': [('id', 'in', emp_lst), '|', ('active', '=', False), ('active', '=', True)]}}
