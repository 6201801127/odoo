from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
import datetime
from datetime import timedelta, MAXYEAR


class MeetingCalendarEvent(models.Model):
    _inherit = "calendar.event"

    @api.model
    def kw_get_display_time(self, start, stop, zduration, zallday):
        """ Return date and time (from to from) based on duration with timezone in string. Eg :
                1) if user add duration for 2 hours, return : August-23-2013 at (04-30 To 06-30) (Europe/Brussels)
                2) if event all day ,return : AllDay, July-31-2013
        """
        timezone = self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'
        timezone = pycompat.to_native(timezone)  # make safe for str{p,f}time()

        # get date/time format according to context
        format_date, format_time = self._get_date_formats()

        # convert date and time into user timezone
        self_tz = self.with_context(tz=timezone)
        date = fields.Datetime.context_timestamp(self_tz, fields.Datetime.from_string(start))
        date_deadline = fields.Datetime.context_timestamp(self_tz, fields.Datetime.from_string(stop))

        # convert into string the date and time, using user formats
        to_text = pycompat.to_text
        date_str = to_text(date.strftime(format_date))
        time_str = to_text(date.strftime(format_time))

        if zallday:
            display_time = _("AllDay , %s") % (date_str)
        elif zduration < 24:
            duration = date + timedelta(hours=zduration)
            duration_time = to_text(duration.strftime(format_time))
            display_time = _(u"%s from %s to %s (%s)") % (
                date_str,
                time_str,
                duration_time,
                timezone,
            )
        else:
            dd_date = to_text(date_deadline.strftime(format_date))
            dd_time = to_text(date_deadline.strftime(format_time))
            display_time = _(u"%s at %s To\n %s at %s (%s)") % (
                date_str,
                time_str,
                dd_date,
                dd_time,
                timezone,
            )
        return display_time

    # kw_meeting_id = fields.Many2one("kw_meeting_events", string="Meeting")

# class MeetingEvent(models.Model):
#     _inherit = 'kw_meeting_events'
#
#     @api.model
#     def create(self, values):
#         record = super(MeetingEvent, self).create(values)
#
#         event = self.env['calendar.event']
#
#         meeting_data = {
#             'name': record.name,
#             'partner_ids': [
#                 [6, 0, record.employee_ids.mapped('user_id.partner_id').ids]] if record.employee_ids else False,
#             'categ_ids': [[6, 0, record.meeting_type_id.ids]] if record.meeting_type_id else False,
#             'start': record.start_datetime,
#             'stop': record.stop_datetime,
#             'duration': record.duration,
#             'location': record.meeting_room_id and record.meeting_room_id.name or False,
#             'description': record.description,
#             # 'recurrency': record.recurrency,
#             # 'interval': record.recurrency and record.interval or False,
#             # 'rrule_type': record.recurrency and record.rrule_type,
#             # 'end_type': record.recurrency and record.end_type or False,
#             # 'count': record.recurrency and record.count or False,
#             'kw_meeting_id': record.id,
#         }
#         if record.reminder_id:
#             alarm_id = self.env['calendar.alarm'].search(
#                 [('duration_minutes', '=', record.reminder_id.duration_minutes)], limit=1)
#             if alarm_id:
#                 meeting_data['alarm_ids'] = [[6, 0, alarm_id.ids]]
#
#         event.create(meeting_data)
#         return record
#
#     @api.multi
#     def write(self, values):
#
#         result = super(MeetingEvent, self).write(values)
#         event = self.env['calendar.event']
#         for meeting in self:
#             event_id = event.search([('kw_meeting_id', '=', meeting.id)])
#             if event_id:
#                 write_data = {}
#                 if 'employee_ids' in values:
#                     write_data['partner_ids'] = [
#                         [6, 0, meeting.employee_ids.mapped('user_id.partner_id').ids]]
#                 if 'name' in values:
#                     write_data['name'] = meeting.name
#                 if 'meeting_type_id' in values:
#                     write_data['categ_ids'] = [
#                         [6, 0, meeting.meeting_type_id and meeting.meeting_type_id.ids or []]]
#                 if 'kw_start_meeting_date' in values or 'kw_start_meeting_time' in values or 'duration' in values:
#                     write_data['start'] = meeting.start_datetime
#                     write_data['stop'] = meeting.stop_datetime
#                     write_data['duration'] = meeting.duration
#                 if 'meeting_room_id' in values:
#                     write_data['location'] = meeting.meeting_room_id and meeting.meeting_room_id.name or False
#                 if 'description' in values:
#                     write_data['description'] = values['description']
#                 if 'reminder_id' in values:
#                     alarm = [[6, 0, []]]
#                     if meeting.reminder_id:
#                         alarm_id = self.env['calendar.alarm'].search(
#                             [('duration_minutes', '=', meeting.reminder_id.duration_minutes)], limit=1)
#                         if alarm_id:
#                             alarm = [[6, 0, alarm_id.ids]]
#                     write_data['alarm_ids'] = alarm
#
#                 event_id.write(write_data)
#         return result
