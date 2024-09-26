# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from operator import truediv
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date, timedelta


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'
    _description = 'Generate payslips for all selected employees'

    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees',
                                    domain=['|', ('active', '=', False), ('active', '=', True)])
    block_user = fields.Text(string='Block User')
    not_enabled_user = fields.Text(string='Payroll Not Enabled')

    @api.model
    def create(self, vals):
        msg = ""
        date_end_str = self.env.context.get('date_end')
        date_end = datetime.strptime(str(date_end_str), DEFAULT_SERVER_DATE_FORMAT).date()
        new_emp_list = []
        name_lst = []
        employee_ids = vals['employee_ids'][0][2]
        payroll_employees = self.env['hr.employee'].sudo().search(
            [('enable_payroll', '=', 'yes'), ('id', 'in', employee_ids),('date_of_joining','<=',date_end), '|', ('active', '=', False),
             ('active', '=', True)]).mapped('id')
        not_payroll_emp = self.env['hr.employee'].sudo().search(
            [('enable_payroll', '=', 'no'), ('id', 'in', employee_ids)]).mapped('name')
        disabled_user = ",".join(not_payroll_emp)
        if payroll_employees:
            for emp in payroll_employees:
                block_rec = self.env['hr_block_salary'].sudo().search(
                    [('employee_id', '=', emp), ('year', '=', date_end.year), ('month', '=', date_end.month)])
                for blk in block_rec:
                    name_lst.append(blk.employee_id.name)
                if not block_rec:
                    new_emp_list.append(emp)
            msg = ",".join(name_lst)
            new_vals = {'employee_ids': [[6, False, new_emp_list]],
                        'block_user': msg,
                        'not_enabled_user': disabled_user}
        else:
            new_vals = {'employee_ids': [[6, False, payroll_employees]],
                        'not_enabled_user': disabled_user}
        res = super(HrPayslipEmployees, self).create(new_vals)

        return res

    @api.multi
    def write(self, vals):
        msg = ""
        date_end_str = self.env.context.get('date_end')
        date_end = datetime.strptime(str(date_end_str), DEFAULT_SERVER_DATE_FORMAT).date()
        new_emp_list = []
        name_lst = []
        employee_ids = vals['employee_ids'][0][2]
        payroll_employees = self.env['hr.employee'].sudo().search(
            [('enable_payroll', '=', 'yes'), ('id', 'in', employee_ids),('date_of_joining','<=',date_end), '|', ('active', '=', False),
             ('active', '=', True)]).mapped('id')
        not_payroll_emp = self.env['hr.employee'].sudo().search(
            [('enable_payroll', '=', 'no'), ('id', 'in', employee_ids)]).mapped('name')
        disabled_user = ",".join(not_payroll_emp)
        if payroll_employees:
            for emp in payroll_employees:
                block_rec = self.env['hr_block_salary'].sudo().search(
                    [('employee_id', '=', emp), ('year', '=', date_end.year), ('month', '=', date_end.month)])
                for blk in block_rec:
                    name_lst.append(blk.employee_id.name)
                if not block_rec:
                    new_emp_list.append(emp)
            msg = ",".join(name_lst)
            new_vals = {'employee_ids': [[6, False, new_emp_list]],
                        'block_user': msg,
                        'not_enabled_user': disabled_user}
        else:
            new_vals = {'employee_ids': [[6, False, payroll_employees]],
                        'not_enabled_user': disabled_user}
        # self.env.user.notify_warning(message=f"Salary has been blocked for {msg}")
        res = super(HrPayslipEmployees, self).write(new_vals)
        return res
