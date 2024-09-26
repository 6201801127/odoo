###################################################################################

from datetime import datetime, timedelta, date
from pytz import timezone, UTC
import pytz
from odoo import models, fields, api


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    late_check_in = fields.Integer(string="Late Check-in(Minutes)", compute="get_late_minutes")
    check_in_status = fields.Selection(string='Office-in Status',
                                       selection=[('late', 'Late'),
                                                  ('ontime', 'On Time')], readonly=True,
                                       compute='_compute_checkin_status', store=True)

    def get_late_minutes(self):
        for rec in self:

            rec.late_check_in = 0.0
            week_day = rec.sudo().check_in.weekday()
            if rec.employee_id.contract_id:
                work_schedule = rec.sudo().employee_id.contract_id.resource_calendar_id
                for schedule in work_schedule.sudo().attendance_ids:
                    if schedule.dayofweek == str(week_day) and schedule.day_period == 'morning':
                        work_from = schedule.hour_from
                        result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_from * 60, 60))

                        user_tz = self.env.user.tz
                        dt = rec.check_in

                        if user_tz in pytz.all_timezones:
                            old_tz = pytz.timezone('UTC')
                            new_tz = pytz.timezone(user_tz)
                            dt = old_tz.localize(dt).astimezone(new_tz)
                        str_time = dt.strftime("%H:%M")
                        check_in_date = datetime.strptime(str_time, "%H:%M").time()
                        start_date = datetime.strptime(result, "%H:%M").time()
                        print("hhhhhhhhhhhhhhhhhhh",check_in_date, start_date)
                        t1 = timedelta(hours=check_in_date.hour, minutes=check_in_date.minute)
                        t2 = timedelta(hours=start_date.hour, minutes=start_date.minute)
                        if check_in_date > start_date:
                            final = t1 - t2
                            rec.sudo().late_check_in = final.total_seconds() / 60
                            self._compute_checkin_status()

    def _compute_checkin_status(self):
        for rec in self:
            if rec.late_check_in > 0:
                rec.check_in_status = 'late'
            else:
                rec.check_in_status = 'ontime'