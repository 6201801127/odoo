# -*- coding:utf-8 -*-

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    slip_ids = fields.One2many('hr.payslip', 'employee_id', string='Payslips / भुगतान पर्ची', readonly=True)
    payslip_count = fields.Integer(compute='_compute_payslip_count', string='Payslip Count / पेस्लिप काउंट',
                                   groups="bsscl_hr_payroll.group_hr_payroll_user")

    def _compute_payslip_count(self):
        for employee in self:
            employee.payslip_count = len(employee.slip_ids)
