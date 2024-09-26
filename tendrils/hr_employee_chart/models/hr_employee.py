# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Employee(models.Model):

    _inherit = "hr_employee_info"

    child_all_count = fields.Integer(
        'Indirect Surbordinates Count',
        compute='_compute_child_all_count', store=False)

    @api.depends('child_ids.child_all_count')
    def _compute_child_all_count(self):
        for employee in self:
            employee.child_all_count = len(employee.child_ids) + sum(child.child_all_count for child in employee.child_ids)
            
class HR_Employee(models.Model):

    _inherit = "hr.employee"
    
    child_emp_all_count = fields.Integer(
        'Indirect Surbordinates Count',
        compute='_compute_emp_child_all_count', store=False)


    @api.depends('child_ids.child_emp_all_count')
    def _compute_emp_child_all_count(self):
        for employee in self:
            total_count = 0
            to_process = employee.child_ids.filtered(lambda x: x.employement_type.code != 'O')
            while to_process:
                total_count += len(to_process)
                next_level = to_process.mapped('child_ids').filtered(lambda x: x.employement_type.code != 'O')
                to_process = next_level
            employee.child_emp_all_count = total_count
            print("employee.child_emp_all_count = ", employee.child_emp_all_count)
