# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
import re
import json
from datetime import datetime
# from backports.datetime_fromisoformat import MonkeyPatch
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from .zoomus.client import ZoomClient


class MeetingEvent(models.Model):
    _inherit = "kw_meeting_events"
    _order = 'id'

    """##Online zoom meeting integration"""

    @api.depends('logged_user_id')
    def _check_logged_user(self):
        """Check if logged user same as meeting crated user"""
        for res in self:
            # if self.env.user.zoom_id:
            #     res.update({'zoom_enabled_user': True})

            if res.create_uid.id == self.env.user.id:
                res.update({'is_create_user': True})
            else:
                res.update({'is_create_user': False})

    online_meeting = fields.Selection(string='Online Meeting', selection=[('zoom', 'Zoom'), ('other', 'Others')])
    other_meeting_url = fields.Char('Other Meeting URL')
    online_meeting_id = fields.Many2one('kw_zoom_meeting', string='Online Meeting ID')
    online_meeting_start_url = fields.Char('Online Meeting Start URL', readonly=True)
    online_meeting_join_url = fields.Char('Online Meeting Join URL', readonly=True)
    location_id = fields.Many2one('kw_res_branch', string="Location", required=False)
    logged_user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    is_create_user = fields.Boolean('is created uid', default=True, compute='_check_logged_user')
    zoom_enabled_user = fields.Boolean('Enabled Zoom User', default=False)
    disable_meeeting = fields.Boolean('Enable', compute='_compute_disable_meeting', default=False, store=False)
    participant_meeeting = fields.Boolean('Enable', compute='_compute_is_participant', default=False, store=False)
    other_attendees = fields.One2many('kw_meeting_zoom_oth_attendee', 'meeting_id', string='Other Attendees')


    def isValidURL(self, url):
        # Regex to check valid URL
        regex = ("((http|https)://)(www.)?" +
                 "[a-zA-Z0-9@:%._\\-+~#?&//=]" +
                 "{2,256}\\.[a-z]" +
                 "{2,6}\\b([-a-zA-Z0-9@:%" +
                 "._\\+~#?&//=]*)")

        # Compile the ReGex
        p = re.compile(regex)

        # If the string is empty
        # return false
        if (url == None):
            return False

        # Return if the string
        # matched the ReGex
        if (re.search(p, url)):
            return True
        else:
            return False

    @api.constrains('other_meeting_url')
    def validate_other_meeting_url(self):
        if self.other_meeting_url:
            if not (self.isValidURL(self.other_meeting_url) == True):
                raise ValidationError("Please use a proper URL.")


    def _compute_is_participant(self):
        for res in self:
            if self.env.user.employee_ids in res.employee_ids:
                res.participant_meeeting = True
            else:
                res.participant_meeeting = False

    @api.onchange('online_meeting')
    def onchange_online_meeting(self):
        if self.online_meeting == 'zoom':
            self.other_meeting_url = None
            if not self.env.user.zoom_id:
                raise UserError(_("Please link your zoom account to create zoom meeting."))
            if self.env.user.zoom_id.active == False:
                raise UserError(_("Zoom account activation still pending. Please wait."))

    @api.depends('stop')
    def _compute_disable_meeting(self):
        """ Disable meeting button after meeting over"""
        for res in self:
            if res.stop:
                if res.stop < datetime.now():
                    res.disable_meeeting = True
                else:
                    res.disable_meeeting = False

    @api.constrains('agenda_ids', 'meeting_room_id', 'categ_ids', 'meeting_category')
    def validate_agenda(self):
        for record in self:
            if not record.meeting_room_id and not record.online_meeting:
                raise ValidationError("Please select meeting room.")

            if not record.agenda_ids:
                raise ValidationError("Please enter meeting agenda details.")

            if not record.categ_ids and not self._context.get('pass_validation'):
                raise ValidationError("Please select at least one Meeting Type.")

            if not record.meeting_category:
                raise ValidationError("Please select meeting category.")

    @api.constrains('meeting_room_id', 'start', 'stop', 'duration', 'recurrency', 'interval')
    def validate_meeting_room_availability(self):
        for record in self:
            meeting_events = self.env['kw_meeting_events']
            # if not record.meeting_room_id and not record.online_meeting:
            #     raise ValidationError("Please select meeting room.")
            if record.meeting_room_id and record.start and record.stop and record.interval and record.duration:
                start_datetime = record.start.strftime("%Y-%m-%d %H:%M:%S")
                stop_datetime = record.stop.strftime("%Y-%m-%d %H:%M:%S")
                if record.recurrency:
                    rdates = record._get_recurrent_dates_by_event()
                    meeting_start_date = rdates[0][0].strftime("%Y-%m-%d")
                    meeting_end_date = rdates[-1][0].strftime("%Y-%m-%d")
                    existing_event_data = meeting_events.search(
                        [('recurrency', '=', False), ('meeting_room_id', '=', record.meeting_room_id.id),
                         ('start', '>=', meeting_start_date), ('start', '<=', meeting_end_date),
                         ('id', '<>', record.id), ('state', '=', 'confirmed')])
                    available_date_count = 0
                    for r_start_date, r_stop_date in rdates:
                        # #check for overlapping days events
                        overlapping_events = existing_event_data.filtered(lambda event: not (
                                event.stop <= r_start_date.replace(tzinfo=None) or event.start >= r_stop_date.replace(
                            tzinfo=None)))
                        if not overlapping_events:
                            available_date_count += 1
                    if available_date_count == 0:
                        raise ValidationError(
                            'There is no available date in the selected date range. Please choose another date range and try again. ')
                else:
                    domain = [('meeting_room_id.name','!=','Virtual'),('id', '!=', record.id), ('recurrency', '=', False),
                              ('meeting_room_id', '=', record.meeting_room_id.id),
                              ('state', '=', 'confirmed'),
                              '|', '|',
                              '&', ('start', '<=', start_datetime), ('stop', '>=', start_datetime),
                              '|',
                              '&', ('start', '<=', stop_datetime), ('stop', '>=', stop_datetime),
                              '&', ('start', '<=', start_datetime), ('stop', '>=', stop_datetime),
                              '|',
                              '&', ('start', '>=', start_datetime), ('start', '<=', stop_datetime),
                              '&', ('stop', '>=', start_datetime), ('stop', '<=', stop_datetime)]
                    calendar_events = meeting_events.sudo().search(domain)
                    if calendar_events:
                        raise ValidationError("The meeting room \"" + str(
                            record.meeting_room_id.name) + "\" has already been booked. Please choose another meeting room.")

    """
    @Create: Creation of zoom meeting if user is zoom user
    @Delete: Delete the created zoom meeting if meeting not created.
    """
    @api.model
    def create(self, values):
        online_meet = False
        if values.get('recurrent_id'):
            parent = self.env['kw_meeting_events'].search([('id', '=', values.get('recurrent_id'))])
            values['online_meeting'] = parent.online_meeting
            values['meeting_room_id'] = parent.meeting_room_id.id

        if values.get('online_meeting') == 'zoom':
            online_meet = self.env['kw_zoom_meeting'].create_zoom_meeting(values)
            if online_meet:
                values['online_meeting_id'] = online_meet.id
                values['online_meeting_start_url'] = online_meet.start_url
                values['online_meeting_join_url'] = online_meet.join_url
        elif values.get('online_meeting') == 'other':
            values['online_meeting_start_url'] = values.get('other_meeting_url')
            values['online_meeting_join_url'] = values.get('other_meeting_url')
        if values.get('online_meeting') and not values.get('meeting_room_id'):
            values['meeting_room_id'] = self.env['kw_meeting_room_master'].search([('name','=', 'Virtual'),('active','=', False)]).id
        meeting = super(MeetingEvent, self).create(values)

        if not meeting and online_meet:
            """delete zoom meeting api"""
            self.env['kw_zoom_meeting'].delete_zoom_meeting(online_meet)
        elif meeting and online_meet:
            online_meet.write({"meeting_id": meeting.id})
        return meeting

    @api.multi
    def action_start_meeting(self):
        return {
            'type': 'ir.actions.act_url',
            'url': self.online_meeting_start_url,
            'target': 'new',
        }

    @api.multi
    def action_join_meeting(self):
        return {
            'type': 'ir.actions.act_url',
            'url': self.online_meeting_join_url,
            'target': 'new',
        }

    @api.multi
    def unlink(self):
        for meeting in self:
            if meeting.online_meeting and meeting.online_meeting == 'zoom':
                online_meet = self.env['kw_zoom_meeting'].delete_zoom_meeting(meeting)

        return super(MeetingEvent, self).unlink()

    @api.multi
    def write(self, values):
        self.ensure_one()
        if values.get('online_meeting') == 'zoom':
            vals = {'name': self.name, 'duration': values.get('duration') if values.get('duration') else self.duration}
            online_meet = self.env['kw_zoom_meeting'].create_zoom_meeting(vals)
            values['online_meeting_id'] = online_meet.id
            values['online_meeting_start_url'] = online_meet.start_url
            values['online_meeting_join_url'] = online_meet.join_url
        elif values.get('online_meeting') == 'other':
            values['online_meeting_start_url'] = values.get('other_meeting_url')
            values['online_meeting_join_url'] = values.get('other_meeting_url')
        if values.get('attendee_ids'):
            for attendee in values.get('attendee_ids'):
                if attendee[0] == 0:
                    values['employee_ids'] = [[4, attendee[2].get('employee_id')]]

        result = super(MeetingEvent, self).write(values)
        if self.env.context.get('zoomattendaceview'):
            values.pop('employee_ids')
        if result:
            if self.online_meeting and self.online_meeting == 'zoom' and not self.env.context.get('zoomattendaceview'):
                if self.online_meeting_id:
                    params = {
                        "id": self.online_meeting_id.zoom_id,
                        "meeting_id": self.online_meeting_id.id,
                        'topic': self.name,
                        'start_time': self.start_datetime,
                        'duration': self.duration * 60
                    }
                    self.env['kw_zoom_meeting'].update_zoom_meeting(params)
            # Send email to attendees
            if values.get('employee_ids'):
                if self.attendee_ids and self.meeting_type_id.code != 'interview':
                    template_mail = self.env.ref('kw_meeting_zoom_integration.kw_meeting_calendar_template_meeting_changedate_zoom')
                    if not template_mail:
                        self.attendee_ids._send_mail_to_attendees('kw_meeting_schedule.kw_meeting_calendar_template_meeting_changedate', force_send=False)
                    else:
                        self.attendee_ids._send_mail_to_attendees('kw_meeting_zoom_integration.kw_meeting_calendar_template_meeting_changedate_zoom', force_send=False)
        return result

    @api.multi
    def update_participant_webhook(self, values):
        meeting_id = values.get('id')
        participant = values.get('participant')
        meeting = self.env['kw_zoom_meeting'].sudo().search([('zoom_id', '=', meeting_id)])
        if meeting:
            event_id = self.sudo().search([('online_meeting_id', '=', meeting.id)])
            if event_id:
                zoom_user = self.env['kw_zoom_users'].sudo().search([('zoom_id', '=', participant.get('id'))], limit=1)
                if zoom_user:
                    for attendee in event_id.attendee_ids:
                        if attendee.employee_id in zoom_user.user_id.sudo().employee_ids:
                            attendee.sudo().write({'attendance_status': True})
        return

    @api.multi
    def action_update_attendance(self, *args, **kwargs):
        for rec in self:
            meeting_id = rec.id
            attendee = self.env['kw_meeting_attendee']
            # event = self.env['kw_meeting_events']
            params = self.env['kw_zoom_users'].sudo().get_config_params()
            if params.get('jwt_api_key') and params.get('jwt_api_secret'):
                client = ZoomClient(params.get('jwt_api_key'), params.get('jwt_api_secret'))
                zoom_res = json.loads(client.past_meeting.get_participants(meeting_id=rec.online_meeting_id.zoom_id,
                                                                           page_size=300).content)
                if zoom_res and zoom_res["participants"]:
                    for rec in zoom_res["participants"]:
                        if rec.get('id') == '':
                            oth = self.env['kw_meeting_zoom_oth_attendee'].search([('name', '=', rec.get('name')), ('meeting_id', '=', meeting_id)])
                            if not oth:
                                self.env['kw_meeting_zoom_oth_attendee'].create({'meeting_id': meeting_id,'name': rec.get('name')})
                    participants = list(set([rec.get('id') for rec in zoom_res["participants"] if rec.get('id')]))
                    # print('participants >> ', participants)
                    zoom_users = self.env['kw_zoom_users'].search([('zoom_id', 'in', participants)])
                    # print('zoom_users >> ', zoom_users)
                    for user in zoom_users:
                        employee = user.user_id.employee_ids
                        values = {
                            'partner_id': employee.user_id.partner_id.id,
                            'employee_id': employee.id,
                            'email': employee.work_email,
                            'event_id': meeting_id,
                            'attendance_status': True,
                            'is_saved_attendee': True,
                            'state': 'needsAction'
                        }
                        event_exist = attendee.search(
                            [('employee_id', '=', values['employee_id']), ('event_id', '=', values['event_id'])])
                        # print("event_exist >> ", event_exist)
                        if event_exist:
                            res = event_exist.write({'attendance_status': True})
                        else:
                            res = attendee.create(values)
                            res.event_id.employee_ids = [(4, 0, res.employee_id.id)]
                        # print("res >> ", res)
        self.env.user.notify_success(message='Zoom participants updated successfully.')
        return True

    @api.multi
    def action_view_attendance(self):
        view_id = self.env.ref('kw_meeting_zoom_integration.kw_meeting_zoom_attendance_form').id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_events',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            'res_id': self.id,
            'flags': {'form': {'action_buttons': False}},
            'context': {'zoomattendaceview': True}
        }
        return action

    @api.model
    def get_report_data(self):
        datadict = {
            'columns': [{'title0': 'Name'}, {'title1': 'Department'}, {'title2': 'Attended'},
                        {'title3': 'Attendance %'}, {'title4': 'Missed'}]
        }

        fy = self.env['account.fiscalyear'].search([('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        records = self.search([('meeting_type_id.code', '=', 'MM'), ('kw_start_meeting_date', '>=', fy.date_start),
                               ('kw_start_meeting_date', '<=', fy.date_stop)], order='id desc', limit=15)
        total_mm = len(records)
        # print('monday meetings >> ', len(records), ' >> ', records)
        # attendee = {}
        attend = {}
        meeting_dates = []
        for index, meet in enumerate(records, start=5):
            datadict['columns'].append({f'title{index}': meet.kw_start_meeting_date.strftime("%Y-%m-%d")})
            meeting_dates.append(meet.kw_start_meeting_date.strftime("%Y-%m-%d"))
            for att in meet.attendee_ids:
                if att.attendance_status:
                    if attend.get(att.employee_id.id):
                        attend[att.employee_id.id].append(meet.kw_start_meeting_date.strftime("%Y-%m-%d"))
                    else:
                        attend[att.employee_id.id] = [meet.kw_start_meeting_date.strftime("%Y-%m-%d")]

        mmgroup = self.env['kw_meeting_user_groups'].search([('meeting_type_id.code', '=', 'MM')], limit=1)
        emp_ids = []
        if mmgroup and mmgroup.users:
            data_dict = {}
            for i, user in enumerate(mmgroup.users):
                employee = user.employee_ids
                emp_ids.append(employee.id)
                data_dict[employee.id] = {
                    'name': employee.name,
                    'department': employee.department_id.name,
                    'attended': len(attend[employee.id]) if attend.get(employee.id) else 0,
                    'percentage': (len(attend[employee.id]) / total_mm) * 100 if attend.get(employee.id) else 0,
                    'missed': total_mm - len(attend[employee.id]) if attend.get(employee.id) else total_mm,
                }
        for meet in meeting_dates:
            for emp_id in emp_ids:
                if attend.get(emp_id):
                    if meet in attend.get(emp_id):
                        data_dict[emp_id].update({meet: True})
                    else:
                        data_dict[emp_id].update({meet: False})
                else:
                    data_dict[emp_id].update({meet: False})
        datadict['data'] = data_dict
        return datadict


class ZoomMeetingOtherAttendee(models.Model):
    _name = 'kw_meeting_zoom_oth_attendee'
    _description = "Zoom Attendees"
    _order = 'id'

    meeting_id = fields.Many2one('kw_meeting_events', string='Event')
    name = fields.Char('Name')
    attendance_status = fields.Boolean(string='Attended Meeting', default=False)
