# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import datetime,calendar
from datetime import date, datetime, time
from odoo.exceptions import UserError, ValidationError


class RecordBlockSalary(models.Model):
    _name = 'hr_block_salary'
    _description = 'Block Salary for Employee'
    _rec_name="display_name"

    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
    ]

    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  domain="['|', ('active', '=', False), ('active', '=', True)]")

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year, 1998, -1)]
    display_name= fields.Char(string="Name", default="employee_id.name", compute='_emp_display_name')
    year = fields.Selection(string='Year', selection='_get_year_list', default=str(date.today().year), required=True)
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month), required=True)
    department_id = fields.Char(related='employee_id.department_id.name', string='Department')
    division = fields.Char(related='employee_id.division.name', string='Division')
    section = fields.Char(related='employee_id.section.name', string='Section')
    practise = fields.Char(related='employee_id.practise.name', string='Practice')
    job_id = fields.Char(related='employee_id.job_id.name', string='Designation')
    reason = fields.Text(string='Reason', required=True)
    active = fields.Boolean(string='Active',default=True)
    company_id = fields.Many2one('res.company')
    
    @api.onchange('employee_id')
    def onchange_employee(self):
        if self.employee_id:
            self.company_id = self.employee_id.company_id.id

    @api.model
    def _emp_display_name(self):
            for record in self:
                record.date_object = datetime.strptime(record.month, "%m")
                record.display_name = f'{record.employee_id.name}/{record.date_object.strftime("%b")}-{record.year}'

    @api.constrains('employee_id', 'year', 'month')
    def submit_block_salary(self):
        for rec in self:
            payslip = self.env['hr_block_salary'].sudo().search(
                [('employee_id', '=', rec.employee_id.id), ('year', '=', rec.year), ('month', '=', rec.month)]) - self
            if payslip:
                res = [item[1] for item in rec.MONTH_LIST if item[0] == payslip.month]
                month = res[0]
                raise ValidationError(
                    f"Salary is already blocked for {payslip.employee_id.name} for {month}-{payslip.year}.")

    @api.onchange('year', 'month')
    def onchange_company(self):
        for rec in self:
            if rec.year and rec.month:
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

                for employee in active_filter:
                    emp_lst.append(employee.id)
                for employee in inactive_filter:
                    emp_lst.append(employee.id)
                # att_emp = self.env['kw_payroll_monthly_attendance_report'].sudo().search([('attendance_year', '=', int(rec.year)),
                #                                                                           ('attendance_month', '=', int(rec.month)),
                #                                                                           ('emp_status','=',3)])
                # for attendance in att_emp:
                #     emp_lst.append(attendance.employee_id.id)
                return {'domain': {
                    'employee_id': [('id', 'in', emp_lst), '|', ('active', '=', False), ('active', '=', True)]}}
