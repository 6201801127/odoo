from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AttendanceShiftLog(models.Model):
    _name = 'kw_attendance_shift_log'
    _description = 'Attendance Shift Log'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(string="Employee Name", comodel_name='hr.employee')
    shift_id = fields.Many2one(string="Shift", comodel_name='resource.calendar')
    effective_from = fields.Date(string='Effective From')
    effective_to = fields.Date(string='Effective To')

    # branch_id       = fields.Many2one('kw_res_branch', string="Branch/SBU", related="employee_id.user_id.branch_id", store=True)
    # branch_location = fields.Many2one('kw_location_master', string="Location",related="branch_id.location",store=True)

    @api.constrains('effective_from', 'effective_to')
    def attendance_shift_log_validation(self):
        for record in self:
            if record.effective_from and record.effective_to and record.effective_from >= record.effective_to:
                raise ValidationError("Shift effective from date should be less than effective to date.")
