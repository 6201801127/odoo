# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64

import babel.dates
import collections
import datetime
from datetime import datetime, timedelta, MAXYEAR,date
from dateutil import rrule
from dateutil.relativedelta import relativedelta
import logging
from operator import itemgetter
import pytz
import re
import time
import uuid
import json
from lxml import etree

from odoo import api, fields, models, tools
from odoo.osv import expression
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
from odoo.exceptions import UserError, ValidationError, Warning
import random
# import secrets
from odoo.addons.http_routing.models.ir_http import slug
from werkzeug import urls

from odoo.addons.kw_utility_tools import kw_validations

_logger = logging.getLogger(__name__)

VIRTUALID_DATETIME_FORMAT = "%Y%m%d%H%M%S"
DEFAULT_SMS_CONTENT = """Meeting scheduled by {meeting_scheduler},TIME: {meeting_date} for {meeting_subject},Venue: {meeting_venue}"""

SORT_ALIASES = {
    'start': 'sort_start',
    'start_date': 'sort_start',
    'start_datetime': 'sort_start',
}


def sort_remap(f):
    return SORT_ALIASES.get(f, f)


class MeetingEvent(models.Model):
    """ Model for Calendar Event

        Special context keys :
            - `no_mail_to_attendees` : disabled sending email to attendees when creating/editing a meeting
    """

    _name = 'kw_meeting_events'
    _description = "Meeting Information"
    _order = "id desc"
    _inherit = ["mail.thread"]

    @api.model
    def _get_meeting_room_domain(self):
        if self.env.user.has_group('kw_meeting_schedule.group_kw_meeting_schedule_manager'):
            return [('location_id', '=', self.env.user.company_id.id),
                    '|', ('restricted_access', '=', True),
                    ('restricted_access', '!=', True)]
        else:
            return ['&', ('location_id', '=', self.env.user.company_id.id), ('restricted_access', '!=', True),
                    '|',
                    ('department_ids', '=', False),
                    ('department_ids', 'in', self.env.user.employee_ids.department_id.ids)]

    @api.model
    def default_get(self, fields):
        """# super default_model='crm.lead' for easier use in addons"""
        if self.env.context.get('default_res_model') and not self.env.context.get('default_res_model_id'):
            self = self.with_context(
                default_res_model_id=self.env['ir.model'].sudo().search([
                    ('model', '=', self.env.context['default_res_model'])
                ], limit=1).id
            )

        defaults = super(MeetingEvent, self).default_get(fields)

        """# support active_model / active_id as replacement of default_* if not already given"""
        if 'res_model_id' not in defaults and 'res_model_id' in fields and \
                self.env.context.get('active_model') and self.env.context['active_model'] != 'kw_meeting_events':
            defaults['res_model_id'] = self.env['ir.model'].sudo().search(
                [('model', '=', self.env.context['active_model'])], limit=1).id
        if 'res_id' not in defaults and 'res_id' in fields and \
                defaults.get('res_model_id') and self.env.context.get('active_id'):
            defaults['res_id'] = self.env.context['active_id']
        """#Add logged user as internal participant"""
        """#Start : modified by Gouranga for training_integration - 27 july 2020"""
        if self._context.get('default_start'):
            defaults['start'] = self._context['default_start']
        if self._context.get('default_stop'):
            defaults['stop'] = self._context['default_stop']
        if self._context.get('default_start_datetime'):
            defaults['start_datetime'] = self._context['default_start_datetime']
        if self._context.get('default_stop_datetime'):
            defaults['stop_datetime'] = self._context['default_stop_datetime']
        if self._context.get('default_duration'):
            defaults['duration'] = self._context['default_duration']
        if self._context.get('default_meeting_type_id'):
            defaults['meeting_type_id'] = self._context['default_meeting_type_id']
        if self._context.get('default_categ_ids'):
            defaults['categ_ids'] = self._context['default_categ_ids']

        if self._context.get('default_agenda_ids'):
            defaults['agenda_ids'] = self._context['default_agenda_ids']
        if self._context.get('default_email_subject_line'):
            defaults['email_subject_line'] = self._context['default_email_subject_line']

        if self._context.get('default_employee_ids'):
            defaults['employee_ids'] = self._context['default_employee_ids']
        else:
            emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
            if emp:
               defaults['employee_ids'] = [(6, 0, self.env.user.employee_ids.ids)]

        """#End : modified by Gouranga for training_integration - 27 july 2020"""
        survey_input_data_list = []
        interview_input_data = self.search(
            [('state', 'not in', ['cancelled']), ('meeting_type_id.code', '=', 'interview'),
             '|', ('employee_ids.user_id', 'in', self.env.user.ids),
             ('mom_controller_id.user_id', '=', self.env.user.id)])
        # print('interview_input_data', interview_input_data, len(interview_input_data))
        base_url = '/' if self.env.context.get('relative_url') else \
            self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec_interview in interview_input_data:
            survey_input_data = self.env['survey.user_input'].search(
                [('state', '=', 'new'), ('partner_id', '=', self.env.user.partner_id.id),
                 ('kw_meeting_id', '=', rec_interview.id)])
            # print('survey_input_data',rec_interview,len(survey_input_data))
            for rec in survey_input_data:
                token = rec.token
                trail = "/%s" % token if token else ""
                url = base_url+rec.survey_id.with_context(relative_url=True).recruitment_survey_url + trail
                # print("=====================", url)
        
        return defaults

    @api.model
    def _default_partners(self):
        """ When active_model is res.partner, the current partners should be attendees """
        partners = self.env.user.partner_id
        active_id = self._context.get('active_id')
        if self._context.get('active_model') == 'res.partner' and active_id:
            if active_id not in partners.ids:
                partners |= self.env['res.partner'].browse(active_id)
        return partners

    @api.multi
    def _get_recurrent_dates_by_event(self):
        """ Get recurrent start and stop dates based on Rule string"""
        start_dates = self._get_recurrent_date_by_event(date_field='start')
        stop_dates = self._get_recurrent_date_by_event(date_field='stop')
        return list(pycompat.izip(start_dates, stop_dates))

    @api.multi
    def _get_recurrent_date_by_event(self, date_field='start'):
        """ Get recurrent dates based on Rule string and all event where recurrent_id is child
        date_field: the field containing the reference date information for recurrence computation
        """
        self.ensure_one()
        if date_field in self._fields and self._fields[date_field].type in ('date', 'datetime'):
            reference_date = self[date_field]
        else:
            reference_date = self.start

        timezone = pytz.timezone(self._context.get('tz') or 'UTC')
        event_date = pytz.UTC.localize(fields.Datetime.from_string(reference_date))  # Add "+hh:mm" timezone
        if not event_date:
            event_date = datetime.datetime.now()

        use_naive_datetime = self.allday and self.rrule and 'UNTIL' in self.rrule and 'Z' not in self.rrule
        if not use_naive_datetime:
            """  Convert the event date to saved timezone (or context tz) as it'll"""
            """  define the correct hour/day asked by the user to repeat for recurrence."""
            event_date = event_date.astimezone(timezone)

        """  The start date is naive"""
        """  the timezone will be applied, if necessary, at the very end of the process"""
        """  to allow for DST timezone reevaluation"""
        rset1 = rrule.rrulestr(str(self.rrule), dtstart=event_date.replace(tzinfo=None), forceset=True, ignoretz=True)

        recurring_meetings = self.sudo().search([('recurrent_id', '=', self.id), '|', ('active', '=', False), ('active', '=', True)])

        """  We handle a maximum of 50,000 meetings at a time, and clear the cache at each step to"""
        """  control the memory usage."""
        invalidate = False
        for meetings in self.env.cr.split_for_in_conditions(recurring_meetings, size=50000):
            if invalidate:
                self.invalidate_cache()
            for meeting in meetings:
                recurring_date = fields.Datetime.from_string(meeting.recurrent_id_date)
                if recurring_date:
                    if use_naive_datetime:
                        recurring_date = recurring_date.replace(tzinfo=None)
                    else:
                        if not recurring_date.tzinfo:
                            recurring_date = pytz.UTC.localize(recurring_date)
                        recurring_date = recurring_date.astimezone(timezone).replace(tzinfo=None)
                    if date_field == "stop":
                        recurring_date += timedelta(hours=self.duration)
                    rset1.exdate(recurring_date)
            invalidate = True

        def naive_tz_to_utc(d):
            return timezone.localize(d).astimezone(pytz.UTC)

        return [naive_tz_to_utc(d) if not use_naive_datetime else d for d in rset1 if d.year < MAXYEAR]

    @api.multi
    def _get_recurrency_end_date(self):
        """ Return the last date a recurring event happens, according to its end_type. """
        self.ensure_one()
        data = self.read(['final_date', 'recurrency', 'rrule_type', 'count', 'end_type', 'stop', 'interval'])[0]

        if not data.get('recurrency'):
            return False

        end_type = data.get('end_type')
        final_date = data.get('final_date')
        if end_type == 'count' and all(data.get(key) for key in ['count', 'rrule_type', 'stop', 'interval']):
            # count = (data['count'] + 1) * data['interval']
            # delay, mult = {
            #     'daily': ('days', 1),
            #     'weekly': ('days', 7),
            #     'monthly': ('months', 1),
            #     'yearly': ('years', 1),
            # }[data['rrule_type']]

            deadline = fields.Datetime.from_string(data['stop'])
            # computed_final_date = False
            # while not computed_final_date and count > 0:
            #     try:  # may crash if year > 9999 (in case of recurring events)
            #         computed_final_date = deadline + relativedelta(**{delay: count * mult})
            #     except ValueError:
            #         count -= data['interval']
            return deadline
        return final_date

    def _compute_is_highlighted(self):
        if self.env.context.get('active_model') == 'res.partner':
            partner_id = self.env.context.get('active_id')
            for event in self:
                if event.employee_ids.mapped('partner_id').filtered(lambda s: s.id == partner_id):
                    event.is_highlighted = True

    @api.model
    def _default_employees(self):
        """ When active_model is res.partner, the current partners should be attendees """
        employees = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        return employees

    @api.model
    def _get_partner_domain(self):
        employee_partners = self.env['hr.employee'].sudo().search([]).mapped('user_id.partner_id').ids
        return [('is_company', '=', False), ('id', 'not in', self.env.user.company_id.partner_id.child_ids.ids),
                ('id', 'not in', employee_partners)]

    @api.model
    def _get_location_domain(self):
        if self.env.user.has_group('kw_meeting_schedule.group_kw_meeting_schedule_manager'):
            return []
        else:
            return [('id', 'in', self.env.user.branch_ids.ids)]

    @api.model
    def _get_default_whatsapp_template(self):
        whatsapp_template = self.env['kw_whatsapp_template'].sudo().search([('model_id.model', '=', 'kw_meeting_events')], limit=1)
        if whatsapp_template:
            return whatsapp_template.message
        return ""

    @api.model
    def get_recurrent_staus(self):
        for rec in self:
            if rec.recurrency or rec.recurrent_id:
                rec.recurrent_status = 'Recurrent'
            else:
                rec.recurrent_status = 'General'

    @api.multi
    def _check_date(self):
        for rec in self:
            c_t = datetime.strptime(str(datetime.today()),'%Y-%m-%d %H:%M:%S.%f').strftime("%Y-%m-%d %H:%M:%S")
            current_time = datetime.strptime(str(c_t),"%Y-%m-%d %H:%M:%S")
            if current_time and current_time > rec.stop:
                rec.check_end_Date = True
            else:
                rec.check_end_Date = False

    meeting_category = fields.Selection(
        string='Meeting Category', required=True,
        selection=[('project', 'Project'), ('general', 'General')], default="general"
    )
    meeting_code = fields.Char(string='Code')
    name = fields.Char('Meeting Title', required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('attendance_complete', 'Attendance Status Updated'),
         ('draft_mom', 'Draft MOM Generated'), ('final_mom', 'Final MOM Generated'), ('cancelled', 'Cancelled')],
        string='Status', readonly=True, track_visibility='onchange', default='draft')

    display_time = fields.Char('Meeting Time', compute='_compute_display_time')
    display_start = fields.Char('Date', compute='_compute_display_start', store=True)
    start = fields.Datetime('Date', required=False, help="Start date of an event, without time for full days events")
    stop = fields.Datetime('Time', required=False, help="Stop date of an event, without time for full days events")

    allday = fields.Boolean('All Day', default=False)
    start_date = fields.Date('Start Date', compute='_compute_dates', inverse='_inverse_dates', store=True,
                             track_visibility='onchange')
    start_datetime = fields.Datetime('Start DateTime', compute='_compute_dates', inverse='_inverse_dates', store=True,
                                     track_visibility='onchange')
    stop_date = fields.Date('End Date', compute='_compute_dates', inverse='_inverse_dates', store=True,
                            track_visibility='onchange')
    stop_datetime = fields.Datetime('End Datetime', compute='_compute_dates', inverse='_inverse_dates', store=True,
                                    track_visibility='onchange')  # old date_deadline
    duration = fields.Float('Duration(hh:mm)')
    description = fields.Text('Description')
    privacy = fields.Selection(
        [('public', 'Everyone'), ('private', 'Only me'), ('confidential', 'Only internal users')], 'Privacy',
        default='public')
    """ linked document"""
    res_id = fields.Integer('Document ID')
    res_model_id = fields.Many2one('ir.model', 'Document Model', ondelete='cascade')
    res_model = fields.Char('Document Model Name', related='res_model_id.model', readonly=True, store=True)
    message_ids = fields.One2many(auto_join=False)
    """ RECURRENCE FIELD"""
    rrule = fields.Char('Recurrent Rule', compute='_compute_rrule', inverse='_inverse_rrule', store=True)
    rrule_type = fields.Selection([
        ('daily', 'Day(s)'),
        ('weekly', 'Week(s)'),
        ('monthly', 'Month(s)'),
        ('yearly', 'Year(s)')
    ], string='Recurrence', help="Let the event automatically repeat at that interval")
    recurrency = fields.Boolean('Recurrent', help="Recurrent Meeting")
    recurrent_id = fields.Integer('Recurrent ID')
    recurrent_id_date = fields.Datetime('Recurrent ID date')
    recurrent_status = fields.Char(compute='get_recurrent_staus',string="Type")
    end_type = fields.Selection([('count', 'Number of repetitions'), ('end_date', 'End date')],
                                string='Recurrence Termination', default='count')
    interval = fields.Integer(string='Repeat Every', default=1, help="Repeat every (Days/Week/Month/Year)")
    count = fields.Integer(string='Repeat', help="Repeat x times", default=1)
    mo = fields.Boolean('Mon')
    tu = fields.Boolean('Tue')
    we = fields.Boolean('Wed')
    th = fields.Boolean('Thu')
    fr = fields.Boolean('Fri')
    sa = fields.Boolean('Sat')
    su = fields.Boolean('Sun')
    month_by = fields.Selection([
        ('date', 'Date of month'),
        ('day', 'Day of month')
    ], string='Option', default='date')
    day = fields.Integer('Date of month', default=1)
    week_list = fields.Selection([
        ('MO', 'Monday'),
        ('TU', 'Tuesday'),
        ('WE', 'Wednesday'),
        ('TH', 'Thursday'),
        ('FR', 'Friday'),
        ('SA', 'Saturday'),
        ('SU', 'Sunday')
    ], string='Weekday')
    byday = fields.Selection([
        ('1', 'First'),
        ('2', 'Second'),
        ('3', 'Third'),
        ('4', 'Fourth'),
        ('5', 'Fifth'),
        ('-1', 'Last')
    ], string='By day')
    final_date = fields.Date('Repeat Until')
    user_id = fields.Many2one('res.users', 'Owner', default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Responsible', related='user_id.partner_id', readonly=True)
    active = fields.Boolean('Active', default=True,
                            help="If the active field is set to false, it will allow you to hide the event alarm information without removing it.")
    categ_ids = fields.Many2many('calendar.event.type', 'kwmeeting_category_rel', 'event_id', 'type_id', 'Meeting Types')
    meeting_type_id = fields.Many2one(comodel_name='calendar.event.type', string='Meeting Type', ondelete='restrict')
    attendee_ids = fields.One2many('kw_meeting_attendee', 'event_id', 'Participants', ondelete='cascade')
    is_highlighted = fields.Boolean(compute='_compute_is_highlighted', string='Is the Event Highlighted')
    reminder_id = fields.Many2one(string='Send Reminder Mail', comodel_name='kw_meeting_reminder', ondelete='restrict', )
    reminder_datetime = fields.Datetime('Reminder Datetime', compute='_compute_reminder_datetime', store=True)
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id, required=True)
    location_id = fields.Many2one('kw_res_branch', string="Location", required=False, domain=_get_location_domain)
    meeting_room_id = fields.Many2one(
        string='Meeting Room',
        comodel_name='kw_meeting_room_master',
        ondelete='restrict',
        domain=_get_meeting_room_domain,
        required=False
    )
    project_category = fields.Many2one('crm.stage', string="Project Type", domain=[('code', 'in', ['workorder', 'opportunity'])])
    project = fields.Many2one(string='Project Name', comodel_name='crm.lead', ondelete='restrict')

    project_id = fields.Many2one(string='Project Name', comodel_name='project.project', ondelete='restrict')
    agenda_ids = fields.One2many(string='Agenda', required=True, comodel_name='kw_meeting_agenda',
                                 inverse_name='meeting_id', ondelete='cascade', )
    agenda_proposals = fields.One2many(string='Agenda Proposals', related="agenda_ids.proposal_ids")
    agenda_tasks = fields.One2many(string='Agenda Task', related="agenda_ids.activity_ids")
    employee_ids = fields.Many2many(
        string='Employee', required=True,
        comodel_name='hr.employee',
        domain=[('user_id', '!=', False)],
        ondelete='cascade'
    )
    internal_attendee_ids = fields.One2many('kw_meeting_attendee', 'event_id', 'Participants', ondelete='cascade')

    external_participant_ids = fields.Many2many(comodel_name='res.partner',
                                                relation='kw_meeting_schedule_res_partner_rel',
                                                domain=_get_partner_domain, string='External Participants Old',
                                                ondelete='cascade')  # [('is_company','=',False)]
    external_attendee_ids = fields.One2many('kw_meeting_external_participants', 'meeting_id', 'External Participants',
                                            ondelete='cascade')
    mom_required = fields.Boolean(string='MOM Required')
    mom_controller_id = fields.Many2one(
        string='MOM Controller',
        comodel_name='hr.employee',
        ondelete='restrict',
        default=lambda self: self.env.user.employee_ids.ids,
        readonly=[('state', 'in', ['confirmed', 'attendance_complete', 'draft_mom', 'final_mom', 'cancelled'])]
    )
    parent_id = fields.Many2one('kw_meeting_events', string='Parent Meeting', index=True)
    child_ids = fields.One2many('kw_meeting_events', 'parent_id', string='Child Meetings')

    send_email = fields.Boolean(string='Send E-mail', default=True, readonly=True)
    email_subject_line = fields.Char(string='Email Subject Line',related='name')
    send_whatsapp = fields.Boolean(string='Send WhatsApp')
    whatsapp_message = fields.Text(string='Message', readonly=True, default=_get_default_whatsapp_template)
    send_sms = fields.Boolean(string='Send SMS')
    sms_content = fields.Char(string='SMS Content', readonly=True, default=DEFAULT_SMS_CONTENT)

    reference_document = fields.Binary(string=u'Reference Document', attachment=True)
    ref_name = fields.Char("File Name")

    draft_mom = fields.Binary(string=u'Draft MOM', attachment=True)
    file_name = fields.Char(string='Document Name')
    draft_mom_content = fields.Html(string='Draft MOM Content')
    generate_mom_doc = fields.Boolean(string='Generate Final MOM',default=True)
    meeting_room_availability_status = fields.Boolean(string='Room Availability', )  # compute='_compute_availability', store=False
    notify_to_nsa = fields.Boolean(string='Notify NSA Authority')
    notify_to_admin = fields.Boolean(string='Notify Admin Authority')
    is_meeting_responsible = fields.Boolean('Meeting Responsible', compute='_compute_meeting_responsible')
    meeting_start_status = fields.Boolean(string='Meeting Status', compute='_compute_meeting_datetime_status')
    color = fields.Integer(string='Color Index')
    kw_duration = fields.Selection(string='Duration(hh:mm)', selection='_get_duration_list', )
    kw_start_meeting_date = fields.Date(string='Meeting Date')
    kw_start_meeting_time = fields.Selection(string='Meeting Time', selection='_get_time_list')
    meeting_cancel_reason = fields.Text(string='Reason of Cancellation', )
    total_attendee_count = fields.Integer(string="Total Attendees", compute='_compute_total_attendee')
    total_feedback_count = fields.Integer(string="Total Feedback", compute='_compute_total_feedbackdee')
    check_feedback_pending_count = fields.Boolean(string='Check Feedback Pending Count', default=False, compute='_compute_total_feedbackdee')
    check_feedback_complete_count = fields.Boolean(string='Check Feedback Complete Count', default=False, compute='_compute_total_feedbackdee')
    mom_info_count = fields.Integer(string="MOM Info Count", compute='_compute_mom_statistics', store=True)
    mom_activity_count = fields.Integer(string="MOM Activity Count", compute='_compute_mom_statistics', store=True)
    enable_attendance = fields.Boolean('Enable', compute='_compute_enable_attendance',default=False)
    organiser_id = fields.Many2one('hr.employee')
    has_info_act = fields.Boolean(compute='_compute_get_agenda_details',store=True)
    has_activity_act = fields.Boolean(compute='_compute_get_agenda_details',store=True)
    mpin = fields.Integer(string="Mpin")
    end_meeting_reason = fields.Char(string="End Meeting Reason")
    closed_meeting = fields.Boolean(string="Closed Meeting",default=False)
    check_end_Date = fields.Boolean(string="Check end date",compute='_check_date',default=False,store=False)
    meeting_group_id = fields.Many2one('kw_meeting_user_groups',string='Meeting Group')

    # @api.model
    # def _compute_get_organiser(self):
    #     for res in self:
    #         if res.create_uid:
    #             res.organiser_id = self.env['hr.employee'].sudo().search([('user_id','=',res.create_uid.id)]).id

    @api.onchange('meeting_group_id')
    def set_employee_ids(self):
        if self.meeting_group_id:
            for record in self:
                record.employee_ids = [(6, 0, [rec.employee_ids.id for rec in record.meeting_group_id.users])]

    @api.multi
    def _compute_get_agenda_details(self):
        for meeting in self:
            if meeting.agenda_ids:
                for agenda in meeting.agenda_ids:
                    for activity in agenda.activity_ids:
                        if activity.activity_type == 'info':
                            meeting.has_info_act = True
                        else:
                            meeting.has_activity_act = True

    @api.onchange('meeting_type_id')
    def set_categ_ids(self):
        for record in self:
            record.categ_ids = record.meeting_type_id

    @api.constrains('categ_ids')
    def _check_categ_ids(self):
        all_data = self.env['kw_meeting_events'].sudo().search([])
        for record in self:
            if len(record.categ_ids) > 1:
                raise ValidationError("Maximum one Meeting Types allowed.")

    """# #populate the time duration selection list"""
    @api.model
    def _get_duration_list(self):
        return [(str(i / 60), '{:02d}:{:02d}'.format(*divmod(i, 60)) + ' hrs') for i in range(30, 855, 15)]

    """# #populate the time selection list"""
    @api.model
    def _get_time_list(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=7, minute=45, second=0, microsecond=0)
        end_loop = dt.replace(hour=22, minute=0, second=0, microsecond=0)

        time_list = []
        while start_loop < end_loop:
            start_loop = (start_loop + relativedelta(minutes=+15))
            time_list.append((start_loop.strftime('%H:%M:%S'), start_loop.strftime('%I:%M %p')))
        return time_list

    attendee_notify_option = fields.Selection(
        string='If changes made to the list of attendees. Choose one of the following',
        selection=[('new_attendee', 'Send updates only to added attendees'),
                   ('all_attendee', 'Send updates to all attendees')], default="new_attendee")

    """####################################################
    # Calendar Business, Validations, Constraints        ...
    ####################################################"""
    @api.multi
    def _compute_meeting_datetime_status(self):
        for record in self:
            if record.start <= datetime.now():
                record.meeting_start_status = True

    """ compute total attendee count"""
    @api.multi
    def _compute_total_attendee(self):
        for record in self:
            record.total_attendee_count = len(record.external_attendee_ids) + len(record.employee_ids)
            # record.external_attendee_count  = len(record.external_participant_ids)
            # record.internal_attendee_count  = len(record.employee_ids)
    
    """ compute total attendee count"""
    @api.multi
    def _compute_total_feedbackdee(self):
        for record in self:
            survey_input_data = record.response_ids.filtered(lambda s: s.partner_id.id == self.env.user.partner_id.id)
            feedback_submit = survey_input_data.filtered(lambda s: s.state != 'skip')
            if survey_input_data:
                record.total_feedback_count = len(survey_input_data)
            if len(feedback_submit) >= 1:
                record.check_feedback_pending_count = True
            else:
                record.check_feedback_complete_count = True

    @api.depends('stop')
    def _compute_enable_attendance(self):
        for res in self:
            if res.stop > datetime.now():
                res.enable_attendance = True
            else:
                res.enable_attendance = False

    """ compute mom statistics"""
    @api.depends('agenda_ids','state')
    def _compute_mom_statistics(self):
        for record in self:
            # if record.agenda_ids:
            # print('sssss')
            # print(record.agenda_ids.mapped('activity_ids').filtered(lambda r: r.activity_type == 'info'))
            record.mom_info_count = len(
                record.agenda_ids.mapped('activity_ids').filtered(lambda r: r.activity_type == 'info'))
            record.mom_activity_count = len(
                record.agenda_ids.mapped('activity_ids').filtered(lambda r: r.activity_type == 'activity'))

    @api.constrains('agenda_ids', 'meeting_room_id', 'categ_ids', 'meeting_category')
    def validate_agenda(self):
        for record in self:
            if not record.meeting_room_id:
                raise ValidationError("Please select meeting room.")

            if not record.agenda_ids:
                raise ValidationError("Please enter meeting agenda details.")

            if not record.categ_ids and not self._context.get('pass_validation'):
                raise ValidationError("Please select at least one Meeting Type.")

            if not record.meeting_category:
                raise ValidationError("Please select meeting category.")

    """ for meeting room availability validation"""
    @api.constrains('meeting_room_id', 'start', 'stop', 'duration', 'recurrency', 'interval')
    def validate_meeting_room_availability(self):
        for record in self:
            meeting_events = self.env['kw_meeting_events']

            if not record.meeting_room_id:
                raise ValidationError("Please select meeting room.")

            if record.meeting_room_id and record.start and record.stop and record.interval and record.duration:
                start_datetime = record.start.strftime("%Y-%m-%d %H:%M:%S")
                stop_datetime = record.stop.strftime("%Y-%m-%d %H:%M:%S")
                # #for recurring meetings
                if record.recurrency:
                    rdates = record._get_recurrent_dates_by_event()
                    meeting_start_date = rdates[0][0].strftime("%Y-%m-%d")
                    meeting_end_date = rdates[-1][0].strftime("%Y-%m-%d")

                    # date_range_diff             = rdates[-1][0].replace(tzinfo=None) - record.start
                    # print(date_range_diff.days)
                    # if date_range_diff.days >60:
                    #     raise ValidationError("You can book for more than 2 months in advance. Please select a date range less than 60 days and try again. ")

                    domain = [('recurrency', '=', False), ('meeting_room_id', '=', record.meeting_room_id.id),
                              ('start', '>=', meeting_start_date), ('start', '<=', meeting_end_date),
                              ('id', '<>', record.id), ('state', '=', 'confirmed')]
                    existing_event_data = meeting_events.sudo().search(domain)
                    # overlapping_event_data      = self.env['kw_meeting_events']

                    error_emp_string = ''
                    available_date_count = 0
                    for r_start_date, r_stop_date in rdates:
                        # #check for overlapping days events
                        overlapping_events = existing_event_data.filtered(lambda event: not (
                                    event.stop <= r_start_date.replace(tzinfo=None) or event.start >= r_stop_date.replace(tzinfo=None)))

                        if not overlapping_events:
                            # overlapping_event_data |= overlapping_events                           
                            # error_emp_string    += """\n"""+str(overlapping_events.mapped('name'))+" on "+str(overlapping_events.mapped('display_time'))
                            # else:
                            available_date_count += 1

                    # #if there is not a single available date
                    if available_date_count == 0:
                        raise ValidationError('There is no available date in the selected date range. Please choose another date range and try again. ')
                    # #if there are overlapping dates
                    # if len(error_emp_string)>0:
                    #     raise Warning("""This following Date(s) are already booked for another meetings. \n"""+error_emp_string+"""\n\n The overlapping date(s) will be skipped """)

                else:
                    """ for one time meetings"""
                    domain = [('id', '!=', record.id), ('recurrency', '=', False),
                              ('meeting_room_id', '=', record.meeting_room_id.id), ('state', '=', 'confirmed'),
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
                        # for \"" + str(calendar_events.mapped('name')) + " on " + str(calendar_events.mapped('display_time')) + "\"
                        # #if the meeting details are not sufficient
            else:
                raise ValidationError("Please enter meeting details.")

    """ for resource availability validation"""
    @api.constrains('employee_ids', 'start', 'stop', 'duration', 'recurrency', 'interval')
    def validate_partcipant_availability(self):
        for record in self:
            meeting_events = self.env['kw_meeting_events']

            if not record.employee_ids:
                raise ValidationError("Please add at least one participant.")

            if record.employee_ids and record.start and record.stop and record.interval and record.duration:

                start_datetime = record.start.strftime("%Y-%m-%d %H:%M:%S")
                stop_datetime = record.stop.strftime("%Y-%m-%d %H:%M:%S")
                # #for recurring meetings
                if record.recurrency:

                    rdates = record._get_recurrent_dates_by_event()
                    meeting_start_date = rdates[0][0].strftime("%Y-%m-%d")
                    meeting_end_date = rdates[-1][0].strftime("%Y-%m-%d")

                    domain = [('recurrency', '=', False), ('start', '>=', meeting_start_date),
                              ('start', '<=', meeting_end_date), ('id', '<>', record.id), ('state', '=', 'confirmed')]
                    existing_event_data = meeting_events.sudo().search(domain)
                    # overlapping_event_data      = self.env['kw_meeting_events']

                    error_emp_string = ''
                    for r_start_date, r_stop_date in rdates:
                        # #check for overlapping days events
                        overlapping_events = existing_event_data.filtered(lambda event: not (
                                    event.stop <= r_start_date.replace(tzinfo=None) or event.start >= r_stop_date.replace(tzinfo=None)))

                        available_rec_slot_events = existing_event_data.filtered(
                            lambda event: event.meeting_room_id.id == record.meeting_room_id.id and not (
                                        event.stop <= r_start_date.replace(tzinfo=None) or event.start >= r_stop_date.replace(tzinfo=None)))

                        if overlapping_events and available_rec_slot_events:
                            # overlapping_event_data |= overlapping_events

                            # #check for same employee existing on the overlapping days events
                            existing_employee_ids_in_overlapping = record.employee_ids & overlapping_events.employee_ids
                            if existing_employee_ids_in_overlapping:
                                existing_employee_names_in_overlapping = existing_employee_ids_in_overlapping.mapped('name')

                                error_emp_string += """\n""" + str(existing_employee_names_in_overlapping) + " on " + str(overlapping_events.mapped('display_time'))

                    if len(error_emp_string) > 0:
                        raise ValidationError(
                            """This following Participant(s) present already exists in another meetings. \n""" + error_emp_string + """\n  
                            Remove the participants from list and try again.""")

                else:
                    """ for one time meetings"""
                    domain = [('id', '!=', record.id), ('recurrency', '=', False), ('state', '=', 'confirmed'),
                              '|', '|',
                              '&', ('start', '<=', start_datetime), ('stop', '>=', start_datetime),
                              '|',
                              '&', ('start', '<=', stop_datetime), ('stop', '>=', stop_datetime),
                              '&', ('start', '<=', start_datetime), ('stop', '>=', stop_datetime),
                              '|',
                              '&', ('start', '>=', start_datetime), ('start', '<=', stop_datetime),
                              '&', ('stop', '>=', start_datetime), ('stop', '<=', stop_datetime)]
                    calendar_events = meeting_events.sudo().search(domain)

                    for event in calendar_events:
                        existing_employee_ids = record.employee_ids & event.employee_ids
                        if existing_employee_ids:
                            existing_employee_names = existing_employee_ids.mapped('name')

                            raise ValidationError("The Participant(s) \"" + str(
                                existing_employee_names) + "\" already present in another meeting. Remove the participants from list and try again .")
                            # #if the meeting details are not sufficient
            else:
                raise ValidationError("Please enter meeting details.")

    """ validate current datetime"""
    @api.constrains('start')
    def validate_meeting_start(self):
        for record in self:
            if record.start <= datetime.now():
                raise ValidationError("Meeting schedule start time should be greater than current date and time.")

    """####################################################
    # Calendar Onchange Events      ...
    ####################################################"""
    @api.onchange('employee_ids', 'attendee_ids')
    def _onchange_internal_emp(self):
        meeting_events = self.env['kw_meeting_events']
        for emp in self.employee_ids:
            if not emp:
                raise ValidationError("Please add at least one participant.")
            if emp and self.start and self.stop and self.interval and self.duration:
                start_datetime = self.start.strftime("%Y-%m-%d %H:%M:%S")
                stop_datetime = self.stop.strftime("%Y-%m-%d %H:%M:%S")
                own = False
                if self.meeting_code:
                    own = self.env['kw_meeting_events'].sudo().search([('meeting_code','=', self.meeting_code)])

                if self.recurrency:

                    rdates = self._get_recurrent_dates_by_event()
                    meeting_start_date = rdates[0][0].strftime("%Y-%m-%d")
                    meeting_end_date = rdates[-1][0].strftime("%Y-%m-%d")
                    domain = [('recurrency', '=', False), ('start', '>=', meeting_start_date), ('start', '<=', meeting_end_date)]
                    if own:
                        existing_event_data = meeting_events.sudo().search(domain) - own
                    else:
                        existing_event_data = meeting_events.sudo().search(domain)

                    error_emp_string = ''
                    for r_start_date, r_stop_date in rdates:
                        # #check for overlapping days events
                        overlapping_events = existing_event_data.filtered(lambda event: not (
                                    event.stop <= r_start_date.replace(tzinfo=None) or event.start >= r_stop_date.replace(tzinfo=None)))

                        available_rec_slot_events = existing_event_data.filtered(
                            lambda event: event.meeting_room_id.id == self.meeting_room_id.id and not (
                                        event.stop <= r_start_date.replace(tzinfo=None) or event.start >= r_stop_date.replace(tzinfo=None)))

                        if overlapping_events and available_rec_slot_events:
                            existing_employee_ids_in_overlapping = self.employee_ids & overlapping_events[0].employee_ids
                            if existing_employee_ids_in_overlapping:
                                existing_employee_names_in_overlapping = existing_employee_ids_in_overlapping.mapped('name')
                                error_emp_string += """\n""" + str(existing_employee_names_in_overlapping) + " on " + str(overlapping_events.mapped('display_time'))

                    if len(error_emp_string) > 0:
                        raise ValidationError(
                            """This following Participant(s) present already exists in another meetings. \n""" + error_emp_string + """\n  
                            Please select another participants from list.""")

                # #for one time meetings
                else:
                    domain = [('recurrency', '=', False), ('state', '=', 'confirmed'),
                              '|', '|',
                              '&', ('start', '<=', start_datetime), ('stop', '>=', start_datetime),
                              '|',
                              '&', ('start', '<=', stop_datetime), ('stop', '>=', stop_datetime),
                              '&', ('start', '<=', start_datetime), ('stop', '>=', stop_datetime),
                              '|',
                              '&', ('start', '>=', start_datetime), ('start', '<=', stop_datetime),
                              '&', ('stop', '>=', start_datetime), ('stop', '<=', stop_datetime)]
                    if own:
                        calendar_events = meeting_events.sudo().search(domain) - own
                    else:
                        calendar_events = meeting_events.sudo().search(domain)

                    for event in calendar_events:
                        existing_employee_ids = self.employee_ids & event.employee_ids
                        if existing_employee_ids:
                            existing_employee_names = existing_employee_ids.mapped('name')

                            raise ValidationError("The Participant(s) \"" + str(
                                existing_employee_names) + "\" already present in another meeting. Please select another participants from list.")

    @api.onchange('duration', 'recurrency', 'interval', 'count', 'month_by', 'day', 'byday', 'week_list', 'final_date',
                  'end_type', 'rrule_type', 'start', 'mo', 'tu', 'we', 'th', 'fr', 'sa', 'su')
    def _onchange_meeting_details(self):
        self.meeting_room_id = False
        self.location_id = False

    @api.onchange('meeting_room_id')
    def _onchange_meeting_room(self):
        if self.meeting_room_id:
            if not self.kw_start_meeting_date or not self.kw_start_meeting_time:
                return {'warning': {'title': 'Warning!', 'message': 'Please select meeting start date and time '}}
            if not self.kw_duration or not self.duration:
                return {'warning': {'title': 'Warning!', 'message': 'Please select meeting duration '}}

            if self.recurrency:
                if not (self.interval or self.rrule_type or self.end_type) or not (self.final_date or self.count):
                    return {'warning': {'title': 'Warning!', 'message': 'Please enter the recurring meeting details. '}}
                if self.rrule_type == 'weekly' and not (self.mo or self.tu or self.we or self.th or self.fr or self.sa or self.su):
                    return {'warning': {'title': 'Warning!', 'message': 'Please select a week day. '}}
                if self.rrule_type == 'monthly' and not (self.month_by) and not (self.day or (self.byday and self.week_list)):
                    return {'warning': {'title': 'Warning!', 'message': 'Please select recurring month details.'}}

                if self.end_type == 'end_date' and self.final_date and self.final_date <= self.start.date():
                    self.meeting_room_id = False
                    return {'warning': {'title': 'Warning!', 'message': 'End date should be greater than start date.'}}

    @api.onchange('kw_duration')
    def _onchange_kw_duration(self):
        if self.kw_duration:
            self.duration = float(self.kw_duration)
        else:
            self.duration = 0

    @api.onchange('kw_start_meeting_date', 'kw_start_meeting_time')
    def _onchange_meeting_date_time(self):
        if self.kw_start_meeting_date and self.kw_start_meeting_time:

            meeting_date = self.kw_start_meeting_date.strftime("%Y-%m-%d")
            local_dt = datetime.strptime((meeting_date + ' ' + self.kw_start_meeting_time), "%Y-%m-%d %H:%M:%S")

            user_tz = self.env.user.tz or 'UTC'
            local = pytz.timezone(user_tz)
            utc_dt = datetime.strftime(pytz.utc.localize(datetime.now()).astimezone(local), "%Y-%m-%d %H:%M:%S")
            UTC_OFFSET_TIMEDELTA = datetime.utcnow() - datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S")

            result_utc_datetime = local_dt + UTC_OFFSET_TIMEDELTA
            result_utc_datetime.strftime("%Y-%m-%d %H:%M:%S")

            # print(result_utc_datetime)
            self.start_datetime = result_utc_datetime
        else:
            self.start_datetime = False

    @api.onchange('location_id')
    def _onchange_location_id(self):
        self.meeting_room_id = False
        if self.location_id:
            if self.env.user.has_group('kw_meeting_schedule.group_kw_meeting_schedule_manager'):
                return {'domain': {'meeting_room_id': [('location_id', '=', self.location_id.id),
                                                       '|',
                                                       ('restricted_access', '=', True),
                                                       ('restricted_access', '!=', True)], }}
            else:
                return {'domain': {'meeting_room_id': ['&',
                                                       ('location_id', '=', self.location_id.id),
                                                       ('restricted_access', '!=', True),
                                                       '|',
                                                       ('department_ids', '=', False),
                                                       ('department_ids', 'in', self.env.user.employee_ids.department_id.ids)]}}

    @api.onchange('name')
    def _onchange_name(self):
        self.email_subject_line = self.name
        if self.name and not self.agenda_ids:
            self.agenda_ids = [[0, 0, {'name': self.name}]]

    @api.onchange('employee_ids')
    def _onchange_employee_ids(self):
        # self.partner_ids = [employee.user_id.partner_id.id for employee in self.employee_ids if employee.user_id]      
        self.mom_controller_id = False
        return {'domain': {'mom_controller_id': [('id', 'in', [employee.id for employee in self.employee_ids if employee.user_id])]}}

    @api.onchange('mom_required')
    def _onchange_mom_required(self):
        if not self.mom_required:
            self.mom_controller_id = False
        return {'domain': {
            'mom_controller_id': [('id', 'in', [employee.id for employee in self.employee_ids if employee.user_id])], }}

    @api.multi
    def _compute_meeting_responsible(self):
        for meeting in self:
            meeting.is_meeting_responsible = (meeting.user_id == self.env.user or meeting.mom_controller_id.id in [emp.id for emp in self.env.user.employee_ids])

    @api.depends('reminder_id')
    def _compute_reminder_datetime(self):
        for meeting in self:
            if meeting.reminder_id:
                meeting.reminder_datetime = meeting.start - timedelta(minutes=meeting.reminder_id.duration_minutes)
            else:
                meeting.reminder_datetime = False

    """####################################################
    # Calendar Existing methods      ...
    ####################################################"""

    @api.multi
    def _compute_display_time(self):
        for meeting in self:
            display_time = self.env['calendar.event'].kw_get_display_time(meeting.start, meeting.stop, meeting.duration, meeting.allday)
            meeting.display_time = display_time[0:display_time.rfind("(")]

    @api.multi
    @api.depends('allday', 'start_date', 'start_datetime')
    def _compute_display_start(self):
        for meeting in self:
            meeting.display_start = meeting.start_date if meeting.allday else meeting.start_datetime

    @api.multi
    @api.depends('allday', 'start', 'stop')
    def _compute_dates(self):
        """ Adapt the value of start_date(time)/stop_date(time) according to start/stop fields and all day. Also, compute
            the duration for not all day meeting ; otherwise the duration is set to zero, since the meeting last all the day.
        """
        for meeting in self:
            if meeting.allday and meeting.start and meeting.stop:
                meeting.start_date = meeting.start.date()
                meeting.start_datetime = False
                meeting.stop_date = meeting.stop.date()
                meeting.stop_datetime = False
                meeting.duration = 0.0
            else:
                meeting.start_date = False
                meeting.start_datetime = meeting.start
                meeting.stop_date = False
                meeting.stop_datetime = meeting.stop
                meeting.duration = self.env['calendar.event']._get_duration(meeting.start, meeting.stop)

    @api.multi
    def _inverse_dates(self):
        for meeting in self:
            if meeting.allday:

                """ Convention break:
                 stop and start are NOT in UTC in allday event
                 in this case, they actually represent a date
                 i.e. Christmas is on 25/12 for everyone
                 even if people don't celebrate it simultaneously"""
                enddate = fields.Datetime.from_string(meeting.stop_date)
                enddate = enddate.replace(hour=18)

                startdate = fields.Datetime.from_string(meeting.start_date)
                startdate = startdate.replace(hour=8)  # Set 8 AM

                meeting.write({'start': startdate.replace(tzinfo=None), 'stop': enddate.replace(tzinfo=None)})
            else:
                meeting.write({'start': meeting.start_datetime, 'stop': meeting.stop_datetime})

    @api.depends('byday', 'recurrency', 'final_date', 'rrule_type', 'month_by', 'interval', 'count', 'end_type', 'mo',
                 'tu', 'we', 'th', 'fr', 'sa', 'su', 'day', 'week_list')
    def _compute_rrule(self):
        """ Gets Recurrence rule string according to value type RECUR of iCalendar from the values given.
            :return dictionary of rrule value.
        """
        for meeting in self:
            if meeting.recurrency:
                meeting.rrule = meeting._rrule_serialize()
            else:
                meeting.rrule = ''

    @api.multi
    def _inverse_rrule(self):
        for meeting in self:
            if meeting.rrule:
                data = self.env['calendar.event']._rrule_default_values()
                data['recurrency'] = True
                data.update(self.env['calendar.event']._rrule_parse(meeting.rrule, data, meeting.start))
                meeting.update(data)

    @api.constrains('start_datetime', 'stop_datetime', 'start_date', 'stop_date')
    def _check_closing_date(self):
        for meeting in self:
            if meeting.start_datetime and meeting.stop_datetime and meeting.stop_datetime < meeting.start_datetime:
                raise ValidationError(
                    _('The ending date and time cannot be earlier than the starting date and time.') + '\n' +
                    _("Meeting '%s' starts '%s' and ends '%s'") % (
                    meeting.name, meeting.start_datetime, meeting.stop_datetime)
                )
            if meeting.start_date and meeting.stop_date and meeting.stop_date < meeting.start_date:
                raise ValidationError(
                    _('The ending date cannot be earlier than the starting date.') + '\n' +
                    _("Meeting '%s' starts '%s' and ends '%s'") % (meeting.name, meeting.start_date, meeting.stop_date)
                )

    @api.onchange('start_datetime', 'duration')
    def _onchange_duration(self):
        if self.start_datetime:
            start = self.start_datetime
            self.start = self.start_datetime
            self.stop = start + timedelta(hours=self.duration) - timedelta(seconds=1)

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date:
            self.start = datetime.datetime.combine(self.start_date, datetime.time.min)

    @api.onchange('stop_date')
    def _onchange_stop_date(self):
        if self.stop_date:
            self.stop = datetime.datetime.combine(self.stop_date, datetime.time.max)

    @api.constrains('draft_mom')
    def _check_draft_mom(self):
        allowed_file_list = ['application/pdf']
        for record in self:
            kw_validations.validate_file_mimetype(record.draft_mom, allowed_file_list)
            kw_validations.validate_file_size(record.draft_mom,20)

    """####################################################
    # Calendar Business, Reccurency, ...
    ####################################################"""

    @api.multi
    def _get_ics_file(self):
        """ Returns iCalendar file for the event invitation.
            :returns a dict of .ics file content for each meeting
        """
        result = {}

        def ics_datetime(idate, allday=False):
            if idate:
                if allday:
                    return idate
                else:
                    return idate.replace(tzinfo=pytz.timezone('UTC'))
            return False

        try:
            # FIXME: why isn't this in CalDAV?
            import vobject
        except ImportError:
            _logger.warning("The `vobject` Python module is not installed, so iCal file generation is unavailable. Please install the `vobject` Python module")
            return result

        for meeting in self:
            cal = vobject.iCalendar()
            event = cal.add('vevent')
            if not meeting.start or not meeting.stop:
                raise UserError(_("First you have to specify the date of the invitation."))
            event.add('created').value = ics_datetime(fields.Datetime.now())
            event.add('dtstart').value = ics_datetime(meeting.start, meeting.allday)
            event.add('dtend').value = ics_datetime(meeting.stop, meeting.allday)
            event.add('summary').value = meeting.name
            meeting_room_name = meeting.meeting_room_id.name.lower() if meeting.meeting_room_id.name else 'virtual'
            if meeting.description:
                event.add('description').value = meeting.description
            if 'online_meeting_join_url' in self._fields and meeting.online_meeting and meeting.online_meeting_join_url:
                event.add('location').value = meeting.online_meeting_join_url
            elif meeting.location_id and meeting_room_name != 'virtual':
                event.add('location').value = f'{meeting.location_id.alias}-{meeting.meeting_room_id.display_name}'
            elif meeting.location_id and meeting_room_name == 'virtual':
                event.add('location').value = meeting.location_id.alias
            if meeting.rrule:
                event.add('rrule').value = meeting.rrule

            # if meeting.alarm_ids:
            #     for alarm in meeting.alarm_ids:
            #         valarm = event.add('valarm')
            #         interval = alarm.interval
            #         duration = alarm.duration
            #         trigger = valarm.add('TRIGGER')
            #         trigger.params['related'] = ["START"]
            #         if interval == 'days':
            #             delta = timedelta(days=duration)
            #         elif interval == 'hours':
            #             delta = timedelta(hours=duration)
            #         elif interval == 'minutes':
            #             delta = timedelta(minutes=duration)
            #         trigger.value = delta
            #         valarm.add('DESCRIPTION').value = alarm.name or u'Odoo'
            for attendee in meeting.attendee_ids:
                attendee_add = event.add('attendee')
                attendee_add.value = u'MAILTO:' + (attendee.email or u'')
            result[meeting.id] = cal.serialize().encode('utf-8')
        return result

    @api.multi
    def create_attendees(self):
        current_user = self.env.user
        result = {}
        for meeting in self:
            # employee_ids
            alreay_meeting_employees = meeting.attendee_ids.mapped('employee_id')

            meeting_attendees = self.env['kw_meeting_attendee']
            meeting_partners = self.env['res.partner']
            meeting_employees = self.env['hr.employee']

            for employee in meeting.employee_ids.filtered(lambda employee: employee not in alreay_meeting_employees):
                values = {
                    'partner_id': employee.user_id.partner_id.id,
                    'employee_id': employee.id,
                    'email': employee.work_email,
                    'event_id': meeting.id,
                    'is_saved_attendee': True,
                }

                # current user don't have to accept his own meeting
                if employee.user_id.partner_id == self.env.user.partner_id:
                    values['state'] = 'accepted'

                attendee = self.env['kw_meeting_attendee'].create(values)

                meeting_attendees |= attendee
                meeting_partners |= employee.user_id.partner_id
                meeting_employees |= employee

            if meeting_attendees:
                """ if one time meeting and not recurring child meeting then send mail"""
                if (not meeting.recurrency and meeting.recurrent_id == 0) or (meeting.recurrency):
                    # to_notify = meeting_attendees.filtered(lambda a: a.email != current_user.email)
                    to_notify = meeting_attendees
                    if meeting.meeting_type_id.code != 'interview':
                        invitation_template = self.env.ref('kw_meeting_zoom_integration.kw_meeting_calendar_template_meeting_invitation_zoom')
                        if not invitation_template:
                            to_notify._send_mail_to_attendees('kw_meeting_schedule.kw_meeting_calendar_template_meeting_invitation', force_send=False)
                        else:
                            to_notify._send_mail_to_attendees('kw_meeting_zoom_integration.kw_meeting_calendar_template_meeting_invitation_zoom', force_send=False)

                    """ send whatsapp message to all attendees"""
                    if meeting.send_whatsapp:
                        to_notify.send_whatsAppmessage_to_attendees()

                    # #send sma to all attendees
                    if meeting.send_sms:
                        meeting_datetime = meeting.display_time
                        if meeting.recurrency:
                            meeting_datetime = " ; ".join(meeting.child_ids.mapped('display_time'))
                        message = meeting.sms_content.format(meeting_scheduler=meeting.user_id.name,
                                                             meeting_subject=meeting.name,
                                                             meeting_date=meeting_datetime,
                                                             meeting_venue=meeting.meeting_room_id.name)
                        to_notify.send_sms_to_attendees(message, 'Meeting Schedule')

                meeting.write({'attendee_ids': [(4, meeting_attendee.id) for meeting_attendee in meeting_attendees]})
            # #comment the subscription
            if meeting_partners:
                meeting.message_subscribe(partner_ids=meeting_partners.ids)

            # We remove old attendees who are not in partner_ids now.
            all_employees = meeting.employee_ids
            all_employee_attendees = meeting.attendee_ids.mapped('employee_id')
            old_attendees = meeting.attendee_ids

            employee_to_remove = all_employee_attendees + meeting_employees - all_employees
            attendees_to_remove = self.env["kw_meeting_attendee"]
            if employee_to_remove:
                attendees_to_remove = self.env["kw_meeting_attendee"].sudo().search(
                    [('employee_id', 'in', employee_to_remove.ids), ('event_id', '=', meeting.id)])
                attendees_to_remove.unlink()

            result[meeting.id] = {
                'new_attendees': meeting_attendees,
                'old_attendees': old_attendees,
                'removed_attendees': attendees_to_remove,
                'removed_partners': employee_to_remove
            }
        return result

    @api.multi
    def create_external_attendees(self):
        result = {}
        for meeting in self:
            # external_attendee_ids
            alreay_meeting_partners = meeting.external_attendee_ids.mapped('partner_id')

            meeting_external_attendees = self.env['kw_meeting_external_participants']
            meeting_partners = self.env['res.partner']

            for partner in meeting.external_participant_ids.filtered(lambda partner: partner not in alreay_meeting_partners):
                values = {
                    'partner_id': partner.id,
                    'name': partner.name,
                    'designation': partner.function,
                    'email': partner.email,
                    'mobile_no': partner.mobile,
                    'meeting_id': meeting.id,
                }

            meeting_external_attendees = self.env['kw_meeting_external_participants']
            meeting_partners = self.env['res.partner']

            for partner in meeting.external_participant_ids.filtered(lambda partner: partner not in alreay_meeting_partners):
                values = {
                    'partner_id': partner.id,
                    'name': partner.name,
                    'designation': partner.function,
                    'email': partner.email,
                    'mobile_no': partner.mobile,
                    'meeting_id': meeting.id,
                }

                external_attendee = self.env['kw_meeting_external_participants'].create(values)

                meeting_external_attendees |= external_attendee
                meeting_partners |= partner
            if meeting_external_attendees:
                meeting.write({'external_attendee_ids': [(4, meeting_attendee.id) for meeting_attendee in meeting_external_attendees]})

            """# We remove old attendees who are not in partner_ids now."""
            all_ext_participants = meeting.external_participant_ids
            all_external_attendees = meeting.external_attendee_ids.mapped('partner_id')
            old_attendees = meeting.external_attendee_ids

            partners_to_remove = all_external_attendees + meeting_partners - all_ext_participants
            attendees_to_remove = self.env["kw_meeting_attendee"]
            if partners_to_remove:
                attendees_to_remove = self.env["kw_meeting_external_participants"].sudo().search(
                    [('partner_id', 'in', partners_to_remove.ids), ('meeting_id', '=', meeting.id)])
                attendees_to_remove.unlink()

            result[meeting.id] = {
                'new_attendees': meeting_partners,
                'old_attendees': old_attendees,
                'removed_attendees': attendees_to_remove,
                'removed_partners': attendees_to_remove
            }
        return result

    @api.multi
    def _rrule_serialize(self):
        """ Compute rule string according to value type RECUR of iCalendar
            :return: string containing recurring rule (empty if no rule)
        """
        if self.interval and self.interval < 0:
            raise UserError(_('interval cannot be negative.'))
        if self.count and self.count <= 0:
            raise UserError(_('Event recurrence interval cannot be negative.'))

        def get_week_string(freq):
            weekdays = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
            if freq == 'weekly':
                byday = [field.upper() for field in weekdays if self[field]]
                if byday:
                    return ';BYDAY=' + ','.join(byday)
            return ''

        def get_month_string(freq):
            if freq == 'monthly':
                if self.month_by == 'date' and (self.day < 1 or self.day > 31):
                    raise UserError(_("Please select a proper day of the month."))

                if self.month_by == 'day' and self.byday and self.week_list:  # Eg : Second Monday of the month
                    return ';BYDAY=' + self.byday + self.week_list
                elif self.month_by == 'date':  # Eg : 16th of the month
                    return ';BYMONTHDAY=' + str(self.day)
            return ''

        def get_end_date():
            final_date = fields.Date.to_string(self.final_date)
            end_date_new = ''.join((re.compile('\d')).findall(final_date)) + 'T235959Z' if final_date else False
            return (self.end_type == 'count' and (';COUNT=' + str(self.count)) or '') + \
                   ((end_date_new and self.end_type == 'end_date' and (';UNTIL=' + end_date_new)) or '')

        freq = self.rrule_type  # day/week/month/year
        result = ''
        if freq:
            interval_string = self.interval and (';INTERVAL=' + str(self.interval)) or ''
            result = 'FREQ=' + freq.upper() + get_week_string(freq) + interval_string + get_end_date() + get_month_string(freq)
        return result

    @api.multi
    def get_interval(self, interval, tz=None):
        """ Format and localize some dates to be used in email templates
            :param string interval: Among 'day', 'month', 'dayname' and 'time' indicating the desired formatting
            :param string tz: Timezone indicator (optional)
            :return unicode: Formatted date or time (as unicode string, to prevent jinja2 crash)
        """
        self.ensure_one()
        date = fields.Datetime.from_string(self.start)

        if tz:
            timezone = pytz.timezone(tz or 'UTC')
            date = date.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)

        if interval == 'day':
            # Day number (1-31)
            result = pycompat.text_type(date.day)

        elif interval == 'month':
            # Localized month name and year
            result = babel.dates.format_date(date=date, format='MMMM y', locale=self._context.get('lang') or 'en_US')

        elif interval == 'dayname':
            # Localized day name
            result = babel.dates.format_date(date=date, format='EEEE', locale=self._context.get('lang') or 'en_US')

        elif interval == 'time':
            # Localized time
            # FIXME: formats are specifically encoded to bytes, maybe use babel?
            dummy, format_time = self.env['calendar.event']._get_date_formats()
            # result = tools.ustr(date.strftime(format_time + " %Z"))
            result = date.strftime("%I:%M %p")

        return result

    @api.multi
    def get_display_time_tz(self, tz=False):
        """ get the display_time of the meeting, forcing the timezone.
        This method is called from email template, to not use sudo(). """
        self.ensure_one()
        if tz:
            self = self.with_context(tz=tz)
        return self.env['calendar.event'].kw_get_display_time(self.start, self.stop, self.duration, self.allday)

    @api.multi
    def action_open_calendar_event(self):
        if self.res_model and self.res_id:
            return self.env[self.res_model].browse(self.res_id).get_formview_action()
        return False

    def action_meeting_attendance(self):
        view_id = self.env.ref('kw_meeting_schedule.view_meeting_schedule_take_action_form').id
        target_id = self.id
        mode = 'readonly' if self.state in ['attendance_complete', 'draft_mom', 'final_mom', 'cancelled'] else 'edit'
        return {
            'name': 'Meeting Activities',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_events',
            'res_id': target_id,
            'target': 'new',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'flags': {'action_buttons': False, 'mode': mode, 'toolbar': False, },
        }

    """# #display meeting mom"""
    def get_meeting_mom(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Meeting MOM',
            'view_mode': 'form',
            'res_id': self.id,
            'view_id': self.env.ref('kw_meeting_schedule.view_kw_meeting_schedule_draft_mom_form').id,
            'res_model': 'kw_meeting_events',
            # 'domain'    : [('event_id', '=',self.id)] , 
            'context': "{'create': False,'edit': False}"
        }
    """ action to view meeting participants"""
    def action_meeting_partcipants(self):
        view_id = self.env.ref('kw_meeting_schedule.view_meeting_schedule_partcipants_popup_form').id
        target_id = self.id
        return {
            'name': 'Meeting Partcipants',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_events',
            'res_id': target_id,
            'target': 'new',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'context': {"create": False, "edit": False},
            'flags': {'toolbar': False, 'action_buttons': False, 'mode': 'readonly'},
        }

    """ action to view agenda of the meeting"""
    def action_meeting_agenda(self):
        view_id = self.env.ref('kw_meeting_schedule.view_meeting_schedule_agenda_popup_form').id
        target_id = self.id
        return {
            'name': 'Meeting Agenda',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_events',
            'res_id': target_id,
            'target': 'new',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'context': {"create": False, "edit": False},
            'flags': {'toolbar': False, 'mode': 'readonly'},
        }

    """ action to update the attendance status"""
    @api.multi
    def action_meeting_attendance_completed(self):
        for record in self:
            attendance_status = False
            for attendee in record.attendee_ids:
                if attendee.attendance_status:
                    attendance_status = True

            if attendance_status:
                record.write({'state': 'attendance_complete',
                              'employee_ids': [[6, 'false', record.attendee_ids.mapped('employee_id').ids]],
                              'external_attendee_ids': [[6, 'false', record.external_attendee_ids.mapped('partner_id').ids]]
                              })

            else:
                raise ValidationError(_('At least one participant must have attended the meeting. '))

        return True

    """ action to update the draft MOM/share status"""
    @api.multi
    def action_share_draft_mom(self):
        self.ensure_one()
        for record in self:
            res = record._generate_draft_mom_content()
            if record.state != 'draft_mom':
                record.write({'state': 'draft_mom'})
            """ notify the attendee about the MOM generation"""
            # if len(record.draft_mom_content) > 0:
            # template        = self.env.ref('kw_meeting_schedule.kw_meeting_calendar_template_draft_mom')
            #     template_data   = self.env['mail.template'].browse(template.id)
            #     template_data.send_mail(record.id)

            # compose_form = self.env.ref(
            #     'mail.email_compose_message_wizard_form',
            #     False,
            # )
            # ctx = dict(
            #     default_model='kw_meeting_events',
            #     default_res_id=self.id,
            #     default_use_template=bool(template),
            #     default_template_id=template and template.id or False,
            #     default_composition_mode='comment',
            # )
            # return {
            #     'name': _('Compose Email'),
            #     'type': 'ir.actions.act_window',
            #     'view_type': 'form',
            #     'view_mode': 'form',
            #     'res_model': 'mail.compose.message',
            #     'views': [(compose_form.id, 'form')],
            #     'view_id': compose_form.id,
            #     'target': 'new',
            #     'context': ctx,
            # }
            form_view_id = self.env.ref("kw_meeting_zoom_integration.kw_mom_mail_wizard_wizard_form").id
            return {
                'name': 'Meeting Draft MOM',
                'type': 'ir.actions.act_window',
                'res_model': 'mom_mail_wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': form_view_id,
                'target': 'new',
                'context': {
                    'default_meeting_id': self.id,
                    'default_draft_mom_content': self.draft_mom_content,
                },
            }

        # return True

    """##generate system generated Draft MOM Content"""
    @api.multi
    def _generate_draft_mom_content(self):
        self.ensure_one()
        record = self
        error_string = ''
        strdraft_mom = ''
        date_format = self.env["res.lang"].get_date_format()
        for agenda in record.agenda_ids:
            if not agenda.is_deferred and not agenda.activity_ids:
                error_string += """ \n """ + agenda.name

        if len(error_string) > 0:
            raise ValidationError(""" Please enter the activities or mark it deferred against the below agenda   \n""" + error_string)
        else:
            strdraft_mom_points_discussed = ''
            points_discussed_count = 0
            strdraft_mom_activity_with_target = ''
            activity_count = 0

            for agenda in record.agenda_ids:
                for agenda_activity in agenda.activity_ids:
                    if agenda_activity.activity_type == 'info':
                        points_discussed_count += 1

                        if points_discussed_count == 1:
                            strdraft_mom_points_discussed += """<div><p><br></p><span style="color: rgb(0, 0, 0); font-family: Roboto; font-size: 14.6667px; font-weight: 700;">Points Discussed</span><br></div>  <table class="table table-bordered"><tbody>
                <tr><td>Sl.#</td><td style="width:45%">AGENDA</td><td style="width:45%">DETAILS<br></td></tr>  """

                        strdraft_mom_points_discussed += """<tr><td>""" + str(
                            points_discussed_count) + """</td><td>""" + agenda.name + """</td><td>""" + agenda_activity.name + """</td></tr> """

                    elif agenda_activity.activity_type == 'activity':

                        activity_count += 1
                        if activity_count == 1:
                            strdraft_mom_activity_with_target += """<div><span style="color: rgb(0, 0, 0); font-family: Roboto; font-size: 14.6667px; font-weight: 700;">Activity with Target:</span><br></div>
                <table class="table table-bordered"><tbody>
                <tr><td>Sl.#</td><td style="width:35%">AGENDA</td><td style="width:35%">DETAILS</td><td style="width:11%">RESPONSIBILITY</td><td style="width:14%">TARGET DATE</td></tr> """

                        strdraft_mom_activity_with_target += """<tr><td>""" + str(
                            activity_count) + """</td><td>""" + agenda.name + """</td><td>""" + agenda_activity.name + """</td><td>""" + agenda_activity.assigned_to.name + """</td><td>""" + agenda_activity.target_date.strftime(
                            date_format) + """</td></tr> """

            # #if any points discussed and activity
            if points_discussed_count > 0 or activity_count > 0:
                strdraft_mom += """<div>"""

                if points_discussed_count > 0:
                    strdraft_mom_points_discussed += """ </tbody></table> """
                    strdraft_mom += strdraft_mom_points_discussed

                if activity_count > 0:
                    strdraft_mom_activity_with_target += """ </tbody></table> """
                    strdraft_mom += strdraft_mom_activity_with_target

            record.write({'draft_mom_content': strdraft_mom})
        return True

    """ get attendee email list"""
    @api.multi
    def get_attendee_emails_list(self):
        email_ids = self.attendee_ids.filtered(lambda r: r.email or r.employee_id.work_email).mapped(lambda r: r.email or r.employee_id.work_email)
        # print(email_ids)
        # for record in self:
        #     for attendee in record.attendee_ids:
        #         email_ids = email_ids + ',' + str(attendee.email)
        return ','.join(email_ids) if email_ids else ''

    def action_draft_mom(self):
        view_id = self.env.ref('kw_meeting_schedule.view_kw_meeting_schedule_draft_mom_form').id
        target_id = self.id

        mode = 'readonly' if self.state == 'final_mom' else 'edit'
        return {
            'name': 'Draft MOM',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_events',
            'res_id': target_id,
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'flags': {'action_buttons': True, 'mode': mode},
        }

    """ generate final MOM, By : T Ketaki Dedadarshini"""
    @api.multi
    def action_generate_mom(self):
        """ this method called from button action in view xml """
        # generate pdf from report, use report's id as reference
        for record in self:

            record._generate_draft_mom_content()

            draft_mom = record.draft_mom
            if record.generate_mom_doc:
                report_name = "kw_meeting_schedule.report_meeting_draft_mom"
                pdf = self.env.ref(report_name).sudo().render_qweb_pdf([self.id])
                draft_mom = base64.encodestring(pdf[0])
            elif not record.draft_mom:
                raise ValidationError("Please upload MOM or choose to generate the final MOM by system . ")
                # print(pdf) 
            record.write({'draft_mom': draft_mom, 'file_name': (record.name + '_' + record.start.strftime("%Y-%m-%d" + '.pdf')), 'state': 'final_mom'})

            """ send mail to participants"""
            meeting_attachment_id = False
            if record.draft_mom:
                meeting_attachment_id = self.env['ir.attachment'].create({'name': record.file_name, 'datas_fname': record.file_name, 'datas': record.draft_mom})

            template_id = self.env.ref('kw_meeting_zoom_integration.kw_meeting_calendar_template_final_mom_zoom')
            if not template_id:
                template_id = self.env.ref('kw_meeting_schedule.kw_meeting_calendar_template_final_mom')
            template_data = self.env['mail.template'].browse(template_id.id)
            # #send attachment if any
            if meeting_attachment_id:
                template_data.attachment_ids = [(6, 0, [meeting_attachment_id.id])]
            # print(meeting_attachment_id)
            template_data.send_mail(record.id, notif_layout='kwantify_theme.csm_mail_notification_light')

    """ action button cancel the meeting list view"""
    def action_cancel_meeting_list_bulk(self, reason='Cancelled'):
        records_to_cancel = self.env['kw_meeting_events'].sudo().search([('id','=', self._context['active_ids'])])
        meeting_completed = self.env['kw_meeting_events'].with_context(recompute=False)

        for meeting in self:
            # #if recurring Meeting
            if meeting.create_uid.id != self.env.user.id:
                raise Warning("You can not cancel other's meetings.")
            if meeting.recurrency:
                recurring_meetings = meeting.child_ids
                meeting_completed = recurring_meetings.filtered(lambda r: r.start <= datetime.now())

                if not meeting_completed:
                    records_to_cancel |= recurring_meetings
                    records_to_cancel |= meeting
            else:
                if meeting.start <= datetime.now():
                    meeting_completed |= meeting
                else:
                    records_to_cancel |= meeting

        if meeting_completed:
            raise Warning("You can not cancel a meeting that is already taken place.")

        if records_to_cancel:
            for res in records_to_cancel:
                res.write({'meeting_cancel_reason': reason, 'state': 'cancelled', 'color': 9})

    """ action to open meeting form in edit mode"""
    def action_open_meeting_form_edit_mode(self):
        view_id = self.env.ref('kw_meeting_schedule.view_kw_meeting_calendar_event_form').id
        target_id = self.id
        return {
            'name': 'Meeting: Cancel',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_events',
            'res_id': target_id,
            'target': 'self',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'flags': {'action_buttons': True, 'mode': 'edit'},
        }

    """ action to open cancel the meeting form"""
    def action_open_cancel_meeting_form(self):
        view_id = self.env.ref('kw_meeting_schedule.view_meeting_schedule_cancel_popup_form').id
        target_id = self.id
        return {
            'name': 'Meeting: Cancel',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_events',
            'res_id': target_id,
            'target': 'new',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'flags': {'action_buttons': True, 'mode': 'edit'},
        }

    """ action to Open Close the meeting"""
    def action_open_close_meeting(self):
        view_id = self.env.ref('kw_meeting_schedule.view_meeting_schedule_close_popup_form').id
        target_id = self.id
        return {
            'name': 'Meeting: Close',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_events',
            'res_id': target_id,
            'target': 'new',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'flags': {'action_buttons': True, 'mode': 'edit'},
        }
    
    """ action to Close the meeting"""
    def action_close_meeting(self):
        time_val = datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
        self.write({'stop': datetime.strptime(time_val, "%Y-%m-%d %H:%M:%S"),
                    'closed_meeting': True, })

    """ action to open cancel the recurrent meeting form"""
    def action_open_cancel_meeting_form_recurrent(self):
        view_id = self.env.ref('kw_meeting_schedule.view_meeting_schedule_cancel_popup_recurrent_form').id
        target_id = self.id
        return {
            'name': 'Meeting: Cancel',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_events',
            'res_id': target_id,
            'target': 'new',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'flags': {'action_buttons': True, 'mode': 'edit'},
        }

    """ action to cancel the meeting"""
    def action_cancel_meeting(self):
        records_to_cancel = self.env['kw_meeting_events']
        meeting_completed = self.env['kw_meeting_events'].with_context(recompute=False)

        for meeting in self:
            """ if recurring Meeting"""
            # print('MEETING',meeting)
            if meeting.recurrency:
                recurring_meetings = meeting.child_ids
                meeting_completed = recurring_meetings.filtered(lambda r: r.start <= datetime.now())

                if not meeting_completed:
                    records_to_cancel |= recurring_meetings
                    records_to_cancel |= meeting
            else:
                """ for one time meeting"""
                if meeting.start <= datetime.now():
                    meeting_completed |= meeting
                else:
                    records_to_cancel |= meeting

        if meeting_completed:
            raise Warning("You can not cancel a meeting that is already taken place.")

        if not self.meeting_cancel_reason:
            raise Warning("Please enter meeting cancel reason.")

            # result = False
        if records_to_cancel:
            for res in records_to_cancel:
                res.write({'meeting_cancel_reason': self.meeting_cancel_reason, 'state': 'cancelled', 'color': 9})

    """ action to cancel the meeting"""
    def action_cancel_recurrent_meeting(self):
        records_to_cancel = self.env['kw_meeting_events']
        meeting_completed = self.env['kw_meeting_events'].with_context(recompute=False)

        for meeting in self:
            # #if recurring Meeting
            if meeting.recurrency:
                recurring_meetings = meeting.child_ids
                meeting_completed = recurring_meetings.filtered(lambda r: r.start <= datetime.now())

                if not meeting_completed:
                    records_to_cancel |= recurring_meetings
                    records_to_cancel |= meeting
            # if recurring Meeting: child
            elif meeting.recurrent_id:
                mainrecmeetings = self.env['kw_meeting_events'].browse(meeting.recurrent_id)
                recurring_meetings = meeting.child_ids - mainrecmeetings
                meeting_completed = recurring_meetings.filtered(lambda r: r.start <= datetime.now())
                if not meeting_completed:
                    records_to_cancel |= recurring_meetings
                    records_to_cancel |= meeting

        if meeting_completed:
            raise Warning("You can not cancel a meeting that is already taken place.")

        if not self.meeting_cancel_reason:
            raise Warning("Please enter meeting cancel reason.")

            # result = False
        if records_to_cancel:
            for res in records_to_cancel:
                res.write({'meeting_cancel_reason': self.meeting_cancel_reason, 'state': 'cancelled', 'color': 9})

    def action_open_reschedule_meeting_form(self):
        view_id = self.env.ref('kw_meeting_schedule.view_kw_meeting_calendar_event_form').id
        target_id = self.id
        return {
            'name': 'Reschedule Meeting',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_events',
            'res_id': target_id,
            'target': 'new',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'flags': {'action_buttons': True, 'mode': 'edit'},
            'context': {'reschedule_option': True},
        }

    """####################################################
    # ORM Overrides
    ####################################################"""
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(MeetingEvent, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                        submenu=submenu)

        # print(self.env.context.get('reschedule_option'))

        """ condition for readonly fields, for other user groups"""
        if view_type == 'form':
            # res['arch'] = self.fields_view_get_address(res['arch'])
            doc = etree.XML(res['arch'])
            if self.env.context.get('reschedule_option'):

                for node in doc.xpath("//field"):  # All the view fields to readonly
                    if node.get('name') not in ['start_datetime', 'kw_start_meeting_date', 'kw_start_meeting_time',
                                                'kw_duration', 'location_id', 'meeting_room_id', 'recurrency',
                                                'interval', 'rrule_type', 'end_type', 'count', 'final_date', 'mo', 'tu',
                                                'we', 'th', 'fr', 'sa', 'su', 'day', 'week_list', 'month_by', 'day',
                                                'byday', 'meeting_room_availability_status']:
                        modifiers = node.get('modifiers')
                        json_dict_mod = json.loads(modifiers)
                        json_dict_mod['readonly'] = True
                        node.set('modifiers', json.dumps(json_dict_mod))

                for node in doc.xpath("//button[@name='action_open_cancel_meeting_form']"):
                    node.set('modifiers', '{"invisible": true}')

            res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            record_name = record.name + (' (' + str(record.meeting_code) + ')' if record.meeting_code else '')
            result.append((record.id, record_name))
        return result

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('mymeetings'):
            args += ['|', '|', ('user_id', '=', self.env.user.id), ('mom_controller_id.user_id', '=', self.env.user.id),
                     ('employee_ids', 'in', [emp.id for emp in self.env.user.employee_ids])]
        if self._context.get('my_all_meetings'):
            # print("search calleddd--------------------------------------",self.env.user.employee_ids)
            args += ['|', ('employee_ids.user_id', 'in', self.env.user.ids), ('mom_controller_id.user_id', '=', self.env.user.id)]

        if self._context.get('meetingparticipant'):
            args += ['|', ('user_id', '=', self.env.user.id),
                     ('employee_ids', 'in', [emp.id for emp in self.env.user.employee_ids]), ]

        if self._context.get('hiderecurringmeetings'):
            args += [('recurrent_id', '=', 0)]

        # if self._context.get('mymeetingattendance'):
        #     args += [('employee_ids', 'in', [emp.id for emp in self.env.user.employee_ids] )]

        if self._context.get('mymeetings_responsible'):
            args += ['|', ('user_id', '=', self.env.user.id), ('mom_controller_id.user_id', '=', self.env.user.id)]

        return super(MeetingEvent, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
        # return events.ids

    @api.model
    def create(self, values):
        """ creating mpin fpr meeting """
        values['mpin'] = random.randint(1000,9999)
        # values['mpin'] = secrets.randbelow(9000) + 1000

        """# FIXME: never ending recurring events"""
        if 'rrule' in values:
            values['rrule'] = self.env['calendar.event']._fix_rrule(values)

        if 'user_id' not in values:
            """# Else bug with quick_create when we are filter on an other user"""
            values['user_id'] = self.env.user.id

        """# compute duration, if not given"""
        if 'duration' not in values:
            values['duration'] = self.env['calendar.event']._get_duration(values['start'], values['stop'])

        if 'recurrent_id' not in values or values['recurrent_id'] == 0:
            values['meeting_code'] = self.env['ir.sequence'].next_by_code('kw_meeting_events')

        values['state'] = 'confirmed'
        values['organiser_id'] = self.env.user.employee_ids.id
        # values['color'] = 0 if not 'recurrency' in values and not 'recurrent_id' in values else 4

        if values.get('external_attendee_ids'):
            attnlist = []
            for attn in values.get('external_attendee_ids'):
                attn[2]['is_saved_attendee'] = True
                attnlist.append(attn[2].get('partner_id'))
            values['external_participant_ids'] = [(6, 0, attnlist)]

        """ Make internal attendee non editable on save"""
        """ # FIXME: code migrate?"""
        # if values.get('internal_attendee_ids'):
        #     for intattn in values.get('internal_attendee_ids'):
        #         if intattn[2] != False:
        #             intattn[2]['is_saved_attendee'] = True

        meeting = super(MeetingEvent, self).create(values)
        meeting_end_date = False
        if meeting.meeting_type_id.code == 'interview':
            # print("meeting.meeting_type_id.code=======create====",meeting.meeting_type_id.code)
            emp_grade = [rec.grade.name for rec in meeting.employee_ids]
            # print("emp_grade======create=====",emp_grade)
            if any(grade in ['M10', 'M11', 'M12', 'M13', 'M14'] for grade in emp_grade):
                survey_id_form = self.env['survey.survey'].sudo().search([('title', '=', 'New Interview Feedback_HR')])
                meeting.survey_id = survey_id_form.id
            else:
                survey_id_form = self.env['survey.survey'].sudo().search([('title', '=',meeting.survey_id.title )])
                # print("survey_id_form==in else==========================",survey_id_form)
                meeting.survey_id = survey_id_form.id
                
           
               
            
        if meeting.recurrency:
            recurrency_datas = []

            rdates = meeting._get_recurrent_dates_by_event()
            # data            = self._rrule_default_values()

            meeting_events = self.env['kw_meeting_events']

            meeting_start_date = rdates[0][0].strftime("%Y-%m-%d")
            meeting_end_date = rdates[-1][0].strftime("%Y-%m-%d")

            existing_event_data = meeting_events.sudo().search(
                [('recurrency', '=', False), ('meeting_room_id', '=', meeting.meeting_room_id.id),
                 ('start', '>=', meeting_start_date), ('start', '<=', meeting_end_date), ('id', '<>', meeting.id),('state','!=','cancelled')])
            # error_emp_string            =''
            for r_start_date, r_stop_date in rdates:
                """# #check for overlapping days events"""
                overlapping_events = existing_event_data.filtered(lambda event: not (
                            event.stop <= r_start_date.replace(tzinfo=None) or event.start >= r_stop_date.replace(tzinfo=None)))

                if not overlapping_events:
                    recurrency_datas.append({
                                             'meeting_code': meeting.meeting_code,
                                             'meeting_type_id':  meeting.meeting_type_id.id,
                                             'project': meeting.project.id,
                                             'description': meeting.description,
                                             'kw_start_meeting_date': r_start_date.strftime('%Y-%m-%d'),
                                             'kw_start_meeting_time': meeting.kw_start_meeting_time,
                                             'user_id': meeting.user_id.id,
                                             'meeting_room_id': meeting.meeting_room_id.id,
                                             'location_id': meeting.location_id.id,
                                             'meeting_category': values['meeting_category'] if 'meeting_category' in values else 'general',
                                             'categ_ids': values['categ_ids'],
                                            'name': meeting.name,
                                             'parent_id': meeting.id,
                                            'recurrent_id': meeting.id,
                                             'recurrent_id_date': r_start_date.strftime('%Y-%m-%d %H:%M:%S'),
                                             'start': r_start_date.strftime('%Y-%m-%d %H:%M:%S'),
                                             'stop': r_stop_date.strftime('%Y-%m-%d %H:%M:%S'),
                                             'start_datetime': r_start_date.strftime('%Y-%m-%d %H:%M:%S'),
                                             'stop_datetime': r_stop_date.strftime('%Y-%m-%d %H:%M:%S'),
                                             'duration': meeting.duration,
                                            'kw_duration': meeting.kw_duration,
                                             'agenda_ids': values['agenda_ids'],
                                             'employee_ids': values['employee_ids'],
                                             'external_attendee_ids': values['external_attendee_ids'] if 'external_attendee_ids' in values else False,
                                             'mom_required': meeting.mom_required,
                                             'mom_controller_id': meeting.mom_controller_id.id,
                                             'email_subject_line': meeting.email_subject_line,
                                             'sms_content': meeting.sms_content,
                                             'whatsapp_message': meeting.whatsapp_message,
                                            'send_sms': meeting.send_sms,
                                             'state': meeting.state,
                                            'send_whatsapp': meeting.send_whatsapp,
                                             'notify_to_nsa': meeting.notify_to_nsa,
                                             'notify_to_admin': meeting.notify_to_admin})

            # print(recurrency_datas)
            if len(recurrency_datas) > 0:
                meeting_events.create(recurrency_datas)
                # print(recurrency_meetings)

        # meeting._sync_activities(values)
        if meeting_end_date:
            final_date = meeting_end_date
        else:
            final_date = meeting._get_recurrency_end_date()
        # `dont_notify=True` in context to prevent multiple notify_next_alarm
        meeting.with_context(dont_notify=True).write({'final_date': final_date})
        meeting.with_context(dont_notify=True).create_attendees()

        to_notify = meeting.external_attendee_ids
        template_mail = self.env.ref('kw_meeting_zoom_integration.kw_meeting_calendar_template_meeting_invitation_external_zoom')
        if not template_mail:
            to_notify._send_mail_to_external_attendees('kw_meeting_schedule.kw_meeting_calendar_template_meeting_invitation_external', force_send=False)
        else:
            to_notify._send_mail_to_external_attendees('kw_meeting_zoom_integration.kw_meeting_calendar_template_meeting_invitation_external_zoom', force_send=False)

        # Whatsapp msg to external participant  
        if meeting.send_whatsapp:
            to_notify.send_whatsAppmessage_to_participants()

        """  START : send mail to IT and Admin Authority"""
        if (not meeting.recurrency and not meeting.parent_id) or (meeting.recurrency):
            if meeting.notify_to_nsa or meeting.notify_to_admin:
                autorities = meeting.get_authority_group_users_email()
                if autorities is not None:
                    invitation_authority_template = self.env.ref('kw_meeting_zoom_integration.kw_meeting_calendar_template_meeting_invitation_to_authorities_zoom')
                    if not invitation_authority_template:
                        invitation_authority_template = self.env.ref('kw_meeting_schedule.kw_meeting_calendar_template_meeting_invitation_to_authorities')
                    # mail_id = invitation_authority_template.send_mail(meeting.id, notif_layout='mail.mail_notification_light')
                    mail_id = invitation_authority_template.send_mail(meeting.id, notif_layout='kwantify_theme.csm_mail_notification_light')

                    vals = {}
                    """ We don't want to have the mail in the chatter while in queue!"""
                    vals['model'] = None
                    vals['res_id'] = False
                    current_mail = self.env['mail.mail'].browse(mail_id)
                    current_mail.mail_message_id.write(vals)

        return meeting

    @api.multi
    def write(self, values):
        """ FIXME: never ending recurring events"""
        if 'rrule' in values:
            values['rrule'] = self.env['calendar.event']._fix_rrule(values)

        """# compute duration, only if start and stop are modified"""
        if not 'duration' in values and 'start' in values and 'stop' in values:
            values['duration'] = self.env['calendar.event']._get_duration(values['start'], values['stop'])

        start = self.start_datetime
        duration = self.duration

        if 'kw_duration' in values:
            duration = float(values.get('kw_duration'))

        if 'start_datetime' in values and 'stop_datetime' not in values:
            start = datetime.strptime(values.get('start_datetime'), '%Y-%m-%d %H:%M:%S')
            values['stop_datetime'] = start + timedelta(hours=duration) - timedelta(seconds=1)
        # self._sync_activities(values)

        """  Change state to attendance_complete if list got attendance_status=True"""
        empllist = []
        if values.get('attendee_ids'):
            for rec in values.get('attendee_ids'):
                if len(rec) > 2:
                    if rec[2] != False:
                        rec[2]['is_saved_attendee'] = True
                        empllist.append(rec[2].get('employee_id'))
                    if rec[2] != False and rec[2].get('attendance_status'):
                        values['state'] = 'attendance_complete'
                        break
            # values['employee_ids'] = [(4, empl) for empl in empllist]   

        """ Make internal attendee non editable on save"""
        if values.get('external_attendee_ids'):
            for intattn in values.get('external_attendee_ids'):
                if intattn[2] != False:
                    intattn[2]['is_saved_attendee'] = True

        super(MeetingEvent, self).write(values)
        if values.get('employee_ids'):
            if self.meeting_type_id.code == 'interview':
                # print("meeting.meeting_type_id.code===========",self.meeting_type_id.code)
                emp_grade = [rec.grade.name for rec in self.employee_ids]
                # print("emp_grade===========",emp_grade)
                if any(grade in ['M10', 'M11', 'M12', 'M13', 'M14'] for grade in emp_grade):
                    survey_id_form = self.env['survey.survey'].sudo().search([('title', '=', 'New Interview Feedback_HR')])
                    # print("survey_id_form====================",survey_id_form)
                    # print(k)
                    self.survey_id = survey_id_form.id

        if values.get('state') == 'attendance_complete':
            self.env.user.notify_success(message='Attendance updated successfully.')

        """ process events one by one"""
        for meeting in self:
            attendees_create = False
            if values.get('employee_ids', False):
                """ to prevent multiple notify_next_alarm"""
                attendees_create = meeting.with_context(dont_notify=True).create_attendees()

            """ We are directly creating external attendees now"""
            # if values.get('external_attendee_ids', False):
            #     meeting.with_context(dont_notify=True).create_external_attendees()

            # if (values.get('start_date') or values.get('start_datetime') or
            #         (values.get('start') and self.env.context.get('from_ui'))) and values.get('active', True):

            # print(values)

            if not meeting.meeting_start_status \
                    and (meeting.state in ['confirmed']
                         and ((values.get('name') or values.get('meeting_category') or values.get('categ_ids')
                               or values.get('reference_document') or values.get('mom_required')
                               or (values.get('mom_controller_id') and values.get('mom_controller_id') != meeting.mom_controller_id)
                               or values.get('description') or values.get('agenda_ids') or values.get('start_date')
                               or values.get('start_datetime')
                               or (values.get('start') and self.env.context.get('from_ui')))
                              and values.get('active', True))) \
                    or (meeting.state in ['cancelled'] and values.get('meeting_cancel_reason') and values.get('state')):
                if attendees_create:
                    attendees_create = attendees_create[meeting.id]
                    attendee_to_email = attendees_create['old_attendees'] - attendees_create['removed_attendees']
                else:
                    attendee_to_email = meeting.attendee_ids
                if attendee_to_email and meeting.meeting_type_id.code != 'interview':
                    template_mail = self.env.ref('kw_meeting_zoom_integration.kw_meeting_calendar_template_meeting_changedate_zoom')
                    if not template_mail:
                        attendee_to_email._send_mail_to_attendees('kw_meeting_schedule.kw_meeting_calendar_template_meeting_changedate', force_send=False)
                    else:
                        attendee_to_email._send_mail_to_attendees('kw_meeting_zoom_integration.kw_meeting_calendar_template_meeting_changedate_zoom', force_send=False)
                to_notify = meeting.external_attendee_ids
                if to_notify:
                    template_mail = self.env.ref('kw_meeting_zoom_integration.kw_meeting_calendar_template_meeting_dataupdate_external_zoom')
                    if not template_mail:
                        to_notify._send_mail_to_external_attendees('kw_meeting_schedule.kw_meeting_calendar_template_meeting_dataupdate_external', force_send=False)
                    else:
                        to_notify._send_mail_to_external_attendees('kw_meeting_zoom_integration.kw_meeting_calendar_template_meeting_dataupdate_external_zoom', force_send=False)

            elif attendees_create and meeting.attendee_notify_option == 'all_attendee':
                """ if new attendee created  and send option modified to all attendee"""
                attendees_create = attendees_create[meeting.id]
                attendee_to_email = (attendees_create['old_attendees'] - attendees_create['removed_attendees']) - attendees_create['new_attendees']
                if attendee_to_email:
                    invitation_template = self.env.ref('kw_meeting_zoom_integration.kw_meeting_calendar_template_meeting_invitation_zoom')
                    if not invitation_template:
                        attendee_to_email._send_mail_to_attendees('kw_meeting_schedule.kw_meeting_calendar_template_meeting_invitation', force_send=False)
                    else:
                        attendee_to_email._send_mail_to_attendees('kw_meeting_zoom_integration.kw_meeting_calendar_template_meeting_invitation_zoom', force_send=False)

            """ default attendee present if mom_option is not selected and meeting has not been started"""

            if not meeting.meeting_start_status and meeting.state in ['confirmed']:
                if not meeting.mom_required:
                    meeting.attendee_ids.write({'attendance_status': True})
                else:
                    meeting.attendee_ids.write({'attendance_status': False})

        """  START : send mail to NSA and Admin Authority"""
        if values.get('notify_to_nsa') or values.get('notify_to_admin'):
            if (not meeting.recurrency and not meeting.parent_id) or (meeting.recurrency):
                if meeting.notify_to_nsa or meeting.notify_to_admin:
                    autorities = self.get_authority_group_users_email()
                    if autorities is not None:
                        invitation_authority_template = self.env.ref('kw_meeting_zoom_integration.kw_meeting_calendar_template_meeting_invitation_to_authorities_zoom')
                        if not invitation_authority_template:
                            invitation_authority_template = self.env.ref('kw_meeting_schedule.kw_meeting_calendar_template_meeting_invitation_to_authorities')
                        # mail_id = invitation_authority_template.send_mail(meeting.id, notif_layout='mail.mail_notification_light')
                        mail_id = invitation_authority_template.send_mail(meeting.id, notif_layout='kwantify_theme.csm_mail_notification_light')

                        vals = {}
                        """ We don't want to have the mail in the chatter while in queue!"""
                        vals['model'] = None
                        vals['res_id'] = False
                        current_mail = self.env['mail.mail'].browse(mail_id)
                        current_mail.mail_message_id.write(vals)
        """  END : send mail to NSA and Admin Authority"""

        """ Send WhatsApp message to external attendee"""
        if values.get('send_whatsapp') and not values.get('external_attendee_ids'):
            to_notify = meeting.external_attendee_ids
            if to_notify:
                to_notify.send_whatsAppmessage_to_participants()

        """ Send WhatsApp message to internal attendee"""
        if values.get('send_whatsapp') and not values.get('employee_ids'):
            to_notify = meeting.attendee_ids
            if to_notify:
                to_notify.send_whatsAppmessage_to_attendees()

        return True

    """ override the unlink method"""
    @api.multi
    def unlink(self, can_be_deleted=True):
        """  Get concerned attendees to notify them if there is an alarm on the unlinked events,"""
        """  as it might have changed their next event notification"""

        # events              = self.search([('id', 'in', self.ids)])
        records_to_exclude = self.env['kw_meeting_events']
        records_to_unlink = self.env['kw_meeting_events'].with_context(recompute=False)

        for meeting in self:
            # #if recurring Meeting
            if meeting.recurrency:
                recurring_meetings = self.env['kw_meeting_events'].sudo().search([('recurrent_id', '=', meeting.id)])
                meeting_completed = recurring_meetings.filtered(lambda r: r.start <= datetime.now())
                if meeting_completed:
                    records_to_exclude |= meeting
                else:
                    records_to_unlink |= meeting
                    records_to_unlink |= recurring_meetings
            # #for one time meeting
            else:
                if meeting.start <= datetime.now():
                    records_to_exclude |= meeting
                else:
                    records_to_unlink |= meeting

        result = False
        if records_to_unlink:
            result = super(MeetingEvent, records_to_unlink).unlink()

        if records_to_exclude:
            # print(records_to_exclude)
            raise Warning(_("You can not delete a meeting that is already taken place."))

        return result

    @api.multi
    def get_authority_group_users_email(self):
        nsa_authority_group = self.env.ref('kw_meeting_schedule.group_kw_meeting_schedule_nsa_authority')
        admin_authority_group = self.env.ref('kw_meeting_schedule.group_kw_meeting_schedule_admin_authority')

        authority_emps = self.env['hr.employee']
        if (self.notify_to_nsa or self.notify_to_admin) and (nsa_authority_group.users or admin_authority_group.users):
            if self.notify_to_nsa:
                authority_emps |= self.env['hr.employee'].sudo().search([('user_id', 'in', nsa_authority_group.users.ids)])
            if self.notify_to_admin:
                authority_emps |= self.env['hr.employee'].sudo().search([('user_id', 'in', admin_authority_group.users.ids)])

            # print("Manager emp mail=====",authority_emps)
            if authority_emps:
                emails = authority_emps.mapped('work_email')
                return ','.join(emails)

    def action_post_your_input(self):
        view_id = self.env.ref('kw_meeting_schedule.kw_meeting_agenda_proposals_view_form').id
        meeting_id = self.id
        # mode = 'readonly' if self.state in ['attendance_complete','draft_mom','final_mom','cancelled'] else 'edit'
        return {
            'name': 'Post Your Input',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_agenda_proposals',
            'target': 'new',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'domain': [{'agenda_id': [('meeting_id', '=', self.id)]}],
            'context': {'default_meeting_id': self.id},
            'flags': {'action_buttons': True},
        }

    def action_cancel_meeting_all(self):
        # print("call function======================")
        for meeting in self:
            if meeting.recurrency:
                recurring_meetings = meeting.child_ids
                for rec in recurring_meetings:
                    if rec.kw_start_meeting_date and date.today()<= rec.kw_start_meeting_date:
                        rec.write({'state': 'cancelled', 'color': 9})

    """ meeting MOM Preview : added by : T Ketaki Debadarshini, On : 07-July-2020"""
    def action_meeting_mom_preview(self):
        self._generate_draft_mom_content()
        view_id = self.env.ref('kw_meeting_schedule.view_kw_meeting_schedule_mom_preview_form').id
        return {
            'name': 'Preview MOM',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_events',
            'res_id': self.id,
            'target': 'new',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'context': {"create": False, "edit": False},
            'flags': {'action_buttons': False, 'mode': 'readonly', 'toolbar': False, },
        }
