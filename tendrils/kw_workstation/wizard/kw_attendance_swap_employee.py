from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import tools
from datetime import datetime, date, timedelta


class EmployeeAttendance(models.TransientModel):
    _name = 'kw_swap_attendance_wizard'
    _description = 'Attendance request record'

    location_name = fields.Selection(string="WFH/WFO",
                                     selection=[('1', 'WFH'), ('2', 'WFO')], required=True)
    date_of_start = fields.Date(string="Start Date")
    end_date_of = fields.Date(string="End Date")
    reason_shift = fields.Text(string="Reason")

    employee_id = fields.Many2one('kw_employee_workstation_attendance_report', string="Employee",
                                  default=lambda self: self._context.get('current_record'))

    shift_change_check = fields.Boolean(string="shift check")

    # def action_button_view_form(self):
    #     print("self---------",self.employee_id.employee_id)
    #     shift_record = self.env['kw_workstation_assign'].sudo().search([('employee_id','=',self.employee_id.employee_id.id)])
    #     if shift_record:
    #         template = self.env.ref('kw_workstation.kw_shift_change_email_template')
    #         if template:
    #             mail_to =
