from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, datetime


class kwWorkstationNotify(models.Model):
    _name = 'kw_workstation_notify'
    _description = 'Notify to workstation assign'

    emp_designation = fields.Many2many('hr.job', 'workstation_assign_notify_rel', 'workstation_emp_id',
                                       'designation_emp', string="Designation")

    cc_emp = fields.Many2many('hr.employee', 'workstation_emp_rel', 'workstation_cc_emp_id', 'employee_id',
                              string="Employee")

    employee_cc_log_ids = fields.One2many('kw_workstation_cc_notify_log', 'workstation_notify_id')

    @api.constrains('emp_designation')
    def get_notify_add_user(self):
        cc_notify_access = self.env['kw_workstation_notify'].search([])
        if len(cc_notify_access) > 1:
            raise ValidationError("Only one record is allowed to give cc notify access.")

    def update_cc_group_access(self):
        user_group = self.env.ref('kw_workstation.group_ws_cc_notify')
        employees_to_assign_group = []

        for record in self.emp_designation:
            designation_employee = self.env['hr.employee'].search([('job_id', 'in', record.ids)])
            for emp in designation_employee:
                employees_to_assign_group.extend(emp.user_id.ids)
        for emp in self.cc_emp:
            employees_to_assign_group.extend(emp.user_id.ids)
        employees_to_assign_group = list(set(employees_to_assign_group))

        current_group_members = user_group.users.ids

        employees_to_add = list(set(employees_to_assign_group) - set(current_group_members))
        for emp_id in employees_to_add:
            user_group.write({'users': [(4, emp_id)]})
        employees_to_add_records = [
            {'empl_id': self.env['hr.employee'].search([('user_id', '=', emp_id)]).id, 'workstation_notify_id': self.id}
            for emp_id in employees_to_add]
        self.write({'employee_cc_log_ids': [(0, 0, data) for data in employees_to_add_records]})

        employees_to_remove_ids = self.employee_cc_log_ids.filtered(
            lambda log: log.empl_id.user_id.id not in employees_to_assign_group).ids
        self.write({'employee_cc_log_ids': [(3, emp_log_id, 0) for emp_log_id in employees_to_remove_ids]})

        employees_to_remove = list(set(current_group_members) - set(employees_to_assign_group))
        user_group.write({'users': [(3, emp_id) for emp_id in employees_to_remove]})


class kwWorkstationNotify(models.Model):
    _name = 'kw_workstation_cc_notify_log'
    _description = 'Notify to workstation assign log'

    workstation_notify_id = fields.Many2one('kw_workstation_notify')
    empl_id = fields.Many2one('hr.employee', string="Employee")
    designation_id = fields.Many2one('hr.job', string="Designation", related="empl_id.job_id")
