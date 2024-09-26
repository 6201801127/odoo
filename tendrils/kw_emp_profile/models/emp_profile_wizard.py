# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _


class EmployeeProfileActionApprove(models.Model):
    _name = "employee.profile.action.approve"
    _description = "Employees Profile Approval"

    def _default_active_ids(self):
        final_list = []
        list_test = []
        result = []
        test = self.env['kw_emp_profile_new_data'].browse(self._context.get('active_ids'))
        for rec in test:
            list_test.append(rec.name)
        for i in list_test:
            if i not in result:
                result.append(i)
        for emp in result:
            test_final = self.env['hr.employee'].search([('name', '=', emp)])
            for rec_test in test_final:
                final_list.append(rec_test.id)
        # print('list_testlist_test', final_list)
        return final_list

    # employee_ids = fields.One2many('hr.employee', 'emp_wiz', 'Employee Profile', default=_default_active_ids)
    employee_ids = fields.Many2many('hr.employee',default=_default_active_ids)


    @api.multi
    def profile_requests_action_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for employee in self.env['kw_emp_profile_new_data'].browse(active_ids):
            if employee.state == 'pending':
                employee.sudo().button_approve()

    @api.multi
    def profile_requests_action_reject_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for employee in self.env['kw_emp_profile_new_data'].browse(active_ids):
            if employee.state == 'pending':
                employee.sudo().button_reject()


# class Employee(models.Model):
#     _inherit = "hr.employee"

#     emp_wiz = fields.Many2one('employee.profile.action.approve', 'Employee Profile')
