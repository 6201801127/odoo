from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date,datetime


class KwShiftAssignment(models.TransientModel):
    _name           = 'kw_shift_assignment_wizard'
    _description    = 'Kwantify Shift Assignment Wizard'

    def _get_default_employee_records(self):
        datas = self.env['hr.employee'].browse(self.env.context.get('active_ids'))
        return datas

    branch_id = fields.Many2one('kw_res_branch', string="Branch/SBU")
    # department = fields.Many2many('hr.department',string="Department")
    employee_id = fields.Many2many('hr.employee', string="Employee", default=_get_default_employee_records)
    shift_id = fields.Many2one('resource.calendar', string="Shift", domain=[('employee_id', '=', False)])
    effective_from = fields.Date(string='Effective From', default=fields.Date.context_today, autocomplete="off")

    @api.onchange('branch_id')
    def show_employee(self):
        if self.branch_id:
            self.employee_id = False
            return {'domain': {'employee_id': ([('user_id.branch_id', '=', self.branch_id.id)])}}
        else:
            pass

    @api.model
    def create(self, vals):
        new_record = super(KwShiftAssignment, self).create(vals)
        for employees in new_record.employee_id:
            values={}
            if employees.resource_calendar_id.id != new_record.shift_id.id:
                values['resource_calendar_id'] = new_record.shift_id.id
                values['tz'] = new_record.shift_id.tz
            values['effective_from'] = new_record.effective_from
            employees.write(values)
        self.env.user.notify_success(message='Employee Shift Assigned successfully.')
        return new_record
