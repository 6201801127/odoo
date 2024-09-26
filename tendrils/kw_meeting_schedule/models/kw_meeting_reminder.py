from datetime import datetime, timedelta
from odoo import models, fields, api


class KwMeetingReminder(models.Model):
    _name = 'kw_meeting_reminder'
    _description = 'Meeting Schedule Alarm'

    @api.depends('interval', 'duration')
    def _compute_duration_minutes(self):
        for alarm in self:
            if alarm.interval == "minutes":
                alarm.duration_minutes = alarm.duration
            elif alarm.interval == "hours":
                alarm.duration_minutes = alarm.duration * 60
            elif alarm.interval == "days":
                alarm.duration_minutes = alarm.duration * 60 * 24
            else:
                alarm.duration_minutes = 0

    _interval_selection = {'minutes': 'Minute(s)', 'hours': 'Hour(s)', 'days': 'Day(s)'}

    name = fields.Char('Name', translate=True, required=True)
    # type = fields.Selection([('notification', 'Notification'), ('email', 'Email')], 'Type', required=True, default='email')
    duration = fields.Integer('Remind Before', required=True, default=1)
    interval = fields.Selection(list(_interval_selection.items()), 'Unit', required=True, default='hours')
    duration_minutes = fields.Integer('Duration in minutes', compute='_compute_duration_minutes', store=True,
                                      help="Duration in minutes")

    @api.onchange('duration', 'interval')
    def _onchange_duration_interval(self):
        display_interval = self._interval_selection.get(self.interval, '')
        self.name = str(self.duration) + ' ' + display_interval

    # def _update_cron(self):
    #     try:
    #         cron = self.env['ir.model.data'].sudo().get_object('calendar', 'ir_cron_scheduler_alarm')
    #     except ValueError:
    #         return False
    #     return cron.toggle(model=self._name, domain=[('type', '=', 'email')])


    # #send reminder mail to attendees
    def send_reminder_mail_to_attendees(self):
        now = fields.Datetime.to_string(fields.Datetime.now())
        last_notif_mail = self.env['ir.config_parameter'].sudo().get_param('kw_meeting_schedule.last_notif_mail',
                                                                           default=now)
        now_plus_5m = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
        

        reminder_events = self.env['kw_meeting_events'].search(
            [('state', '=', 'confirmed'), ('reminder_datetime', '>=', last_notif_mail),
             ('reminder_datetime', '<=', now_plus_5m)])
        

        for meeting in reminder_events:
            template_mail = self.env.ref('kw_meeting_zoom_integration.kw_meeting_calendar_template_reminder_zoom')
            if not template_mail:
                meeting.attendee_ids.filtered(lambda r: r.state != 'declined')._send_mail_to_attendees('kw_meeting_schedule.kw_meeting_calendar_template_reminder', force_send=True)
            else:
                meeting.attendee_ids.filtered(lambda r: r.state != 'declined')._send_mail_to_attendees('kw_meeting_zoom_integration.kw_meeting_calendar_template_reminder_zoom', force_send=True)


            meeting.attendee_ids.filtered(lambda r: r.state != 'declined').mapped('employee_id.user_id').notify_default(
                message="You have a meeting " + str(meeting.name) + " starting on " + meeting.display_time + " , venue : " + str(
                    meeting.meeting_room_id.name), title='Meeting Reminder', sticky=True)

        self.env['ir.config_parameter'].sudo().set_param('kw_meeting_schedule.last_notif_mail', now)

    # #reminder mail for recurrence meetings
    def send_recurrent_reminder_mail_to_attendees(self):

        # now             = fields.Datetime.to_string(fields.Datetime.now())

        today = fields.Datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        # print(now_plus_5m)

        recurrent_events = self.env['kw_meeting_events'].search(
            [('state', '=', 'confirmed'), ('recurrency', '=', False), ('parent_id', '!=', False),
             ('start', '>=', today), ('start', '<', tomorrow)])
        # print(recurrent_events)  ## ,('parent_id','>',0)

        for meeting in recurrent_events:
            template_mail = self.env.ref('kw_meeting_zoom_integration.kw_meeting_calendar_template_reminder_zoom')
            if not template_mail:
                meeting.attendee_ids.filtered(lambda r: r.state != 'declined')._send_mail_to_attendees('kw_meeting_schedule.kw_meeting_calendar_template_reminder', force_send=True)
            else:
                meeting.attendee_ids.filtered(lambda r: r.state != 'declined')._send_mail_to_attendees('kw_meeting_zoom_integration.kw_meeting_calendar_template_reminder_zoom', force_send=True)

    # #reminder mail for meeting task
    def send_reminder_mail_to_attendee_for_task(self):

        today = fields.Datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        day_after_tomorrow = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        # print(now_plus_5m)

        pending_meeting_task = self.env['kw_meeting_agenda_activities'].search(
            ['&', ('meeting_id.state', '=', 'final_mom'), '&', ('state', '=', 'not_started'), '|',
             ('target_date', '=', today), '|', ('target_date', '=', tomorrow),
             ('target_date', '=', day_after_tomorrow)])
        # print(pending_meeting_task)  # # ,('parent_id','>',0)

        for task in pending_meeting_task:
            task_template = self.env.ref('kw_meeting_zoom_integration.kw_meeting_calendar_template_assigned_task_zoom')
            if not task_template:
                task_template = self.env.ref('kw_meeting_schedule.kw_meeting_calendar_template_assigned_task')
                
            task_template.send_mail(task.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            # task_template.send_mail(task.id, notif_layout='mail.mail_notification_light')

            # vals = {}
            # vals['model']       = None  # We don't want to have the mail in the chatter while in queue!
            # vals['res_id']      = False
            # current_mail        = self.env['mail.mail'].browse(mail_id)                
            # current_mail.mail_message_id.write(vals)
