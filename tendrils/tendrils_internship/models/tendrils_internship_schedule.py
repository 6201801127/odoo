from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime


class TendrilInternshipSchedule(models.Model):
    _name = "td_internship_schedule"
    _description = "Internship Schedule"
    _rec_name = "sessioin"

    @api.model
    def _internship_get_time(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=7, minute=45, second=0, microsecond=0)
        end_loop = dt.replace(hour=22, minute=0, second=0, microsecond=0)
        time_list = []
        while start_loop < end_loop:
            start_loop += relativedelta(minutes=+15)
            time_list.append((start_loop.strftime('%H:%M:%S'),
                              start_loop.strftime('%I:%M %p')))
        return time_list

    instructor = fields.Many2one("hr.employee", string="Instructor")
    sessioin = fields.Char(string="Session", required=True)
    session_type = fields.Selection(string="Venue",
                                    selection=[('inside', 'Indoor'), ('outside', 'Outdoor'), ('online', 'Online')],
                                    required=True)
    date = fields.Date("Date", default=fields.Date.context_today, required=True ,track_visibility='onchange')
    from_time = fields.Selection(string='Start Time', selection='_internship_get_time', required=True)
    to_time = fields.Selection(string='End Time', selection='_internship_get_time', required=True)
    internship_id = fields.Many2one('lk_training_batch', string='Internship Id', ondelete="cascade")
    attendance_id = fields.Many2one("internship_update_attendance", string="Attendance")  # to take attendance manually

    @api.constrains('date')
    def _check_start_date(self):
        for rec in self:
            if rec.date and rec.date < fields.Date.today():
                raise ValidationError("Start date cannot be less than today.")

    @api.multi
    def update_attendance(self):
        attendance_form_view_id = self.env.ref("tendrils_internship.internship_update_attendance_form").id

        existing_attendance = self.env['internship_update_attendance'].search([
            ('internship_id', '=', self.internship_id.id),
            ('session_id', '=', self.id)
        ], limit=1)

        action = {
            'name': 'Attendance',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'internship_update_attendance',
            'views': [(attendance_form_view_id, 'form')],
            'flags': {'action_buttons': True, 'mode': 'edit'},
        }

        if existing_attendance:
            action['res_id'] = existing_attendance.id
        else:
            interns = self.internship_id.employee_ids
            attendance_details = [[0, 0, {"attend_intern_id": intern.id}] for intern in interns]
            action['context'] = {
                'default_internship_id': self.internship_id.id,
                'default_session_id': self.id,
                'default_internship_attendance_ids': attendance_details,
            }

        return action


class InternshipUpdateAttendance(models.Model):
    _name = "internship_update_attendance"
    _description = "Update Attendance"
    _rec_name = "session_id"

    @api.model
    def _get_time_list(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=7, minute=45, second=0, microsecond=0)
        end_loop = dt.replace(hour=22, minute=0, second=0, microsecond=0)
        time_list = []
        while start_loop < end_loop:
            start_loop += relativedelta(minutes=+15)
            time_list.append((start_loop.strftime('%H:%M:%S'),
                              start_loop.strftime('%I:%M %p')))
        return time_list

    internship_id = fields.Many2one("lk_training_batch", string='Internship', ondelete="restrict")
    internship_attendance_ids = fields.One2many("update_attendance_details", "attendance_id", string="Intern")
    session_id = fields.Many2one(string='Session', comodel_name='td_internship_schedule', ondelete='restrict')
    from_time = fields.Selection('_get_time_list', related='session_id.from_time', store=True)
    to_time = fields.Selection('_get_time_list', related='session_id.to_time', store=True)
    date = fields.Date("Date", related="session_id.date")


class UpdateAttendanceDetails(models.Model):
    _name = "update_attendance_details"
    _description = "Update Attendance Details"

    attend_intern_id = fields.Many2one('tendrils_internship')
    attendance_id = fields.Many2one('internship_update_attendance', string='Attendance ID')
    attended_bool = fields.Boolean('Attended', default=False, force_save=True)
