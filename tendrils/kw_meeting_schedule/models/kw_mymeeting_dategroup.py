# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, tools
import datetime
from datetime import  datetime

class KWMeetingScheduleDategroup(models.Model):
    _name = "kw_my_meeting_dategroup_report"
    _description = "Meeting dategroup view"

    _auto = False

    event_id = fields.Many2one('kw_meeting_events', string='Event ID')
    name = fields.Char(string='Name', )
    user_id = fields.Many2one(string='User', comodel_name='res.users', readonly="True")
    categ_ids = fields.Many2many(string='Categories', related="event_id.categ_ids")
    # start                = fields.Char(string='Name',related="event_id.categ_ids")
    display_time = fields.Char(string='Display Time', related="event_id.display_time")
    meeting_room_id = fields.Many2one(string='Meeting Room', comodel_name='kw_meeting_room_master', readonly="True")
    color = fields.Integer(string='color', related="event_id.color")
    employee_ids = fields.Many2many(string='Participants', related="event_id.employee_ids")
    attendee_ids = fields.One2many(string='Attendees', related="event_id.attendee_ids")
    external_participant_ids = fields.Many2many(string='External Participants old', related="event_id.external_participant_ids")
    external_attendee_ids = fields.One2many(string='External Participants', related="event_id.external_attendee_ids")
    agenda_ids = fields.One2many(string='Agenda', related="event_id.agenda_ids")

    agenda_proposals = fields.One2many(string='Agenda Proposals', related="event_id.agenda_ids.proposal_ids")
    agenda_tasks = fields.One2many(string='Agenda Task', related="event_id.agenda_ids.activity_ids")

    state = fields.Selection(string='State', related="event_id.state")
    meeting_category = fields.Selection(string='meeting_category', related="event_id.meeting_category")
    project = fields.Many2one(string='Project', related="event_id.project")

    start = fields.Datetime(string='start',)
    stop = fields.Datetime(string='stop',)
    time_over = fields.Boolean(string="Time Over",compute='compute_status' )
    
    duration = fields.Float(string='Duration(hh:mm)', )
    kw_duration = fields.Selection(string='Duration(hh:mm)', selection='_get_duration_list', )
    mom_required = fields.Boolean(string='MOM Required', related="event_id.mom_required")
    mom_controller_id = fields.Many2one(string='MOM Controller', related="event_id.mom_controller_id")
    event_status = fields.Char(string='Event Status', )

    company_id = fields.Many2one(string='Company', related="event_id.company_id", readonly="True")
    location_id = fields.Many2one(string='Location', comodel_name='kw_res_branch', readonly="True")

    reference_document = fields.Binary(string="Reference Document", related="event_id.reference_document")
    description = fields.Text('Required Information/ Pre Preparatory', related="event_id.description")

    draft_mom = fields.Binary(string='Draft MOM', related="event_id.draft_mom")
    file_name = fields.Char(string='Document Name', related="event_id.file_name")

    total_attendee_count = fields.Integer(string='Attendee Count', related="event_id.total_attendee_count")
    is_meeting_responsible = fields.Boolean(string='Meeting Responsible', compute='_compute_meeting_responsible')
    meeting_start_status = fields.Boolean(string='Meeting Started?', related="event_id.meeting_start_status")

    mom_activity_count  = fields.Integer(string="Action Items",related="event_id.mom_activity_count")
    organiser_id = fields.Many2one('hr.employee',compute='_compute_get_organiser',store=True)

    @api.depends('user_id')
    def _compute_get_organiser(self):
        for res in self:
            if res.user_id:
                res.organiser_id = [self.env['hr.employee'].search([('user_id', '=', user.id)]) for user in res.user_id]

    @api.multi
    def compute_status(self):
        current_time = datetime.now()
        for record in self:
            record.time_over = True if current_time > record.stop else False

    # #populate the time duration selection list
    @api.model
    def _get_duration_list(self):
        return [(str(i / 60), '{:02d}:{:02d}'.format(*divmod(i, 60)) + ' hrs') for i in range(30, 855, 15)]

    @api.model_cr
    def init(self):
        """ Event Question main report """
        tools.drop_view_if_exists(self._cr, 'kw_my_meeting_dategroup_report')
        self._cr.execute("""
            CREATE VIEW kw_my_meeting_dategroup_report AS (
            select name,id,id as event_id, start, stop, duration, kw_duration, meeting_room_id,location_id,user_id,organiser_id,CASE
                            WHEN date(start) < now()::date THEN 'Past'
                            WHEN date(start) = now()::date THEN 'Today'
                            WHEN date(start) = now()::date+1 THEN 'Tomorrow'
                            ELSE 'UpComing'
            END as event_status from kw_meeting_events where recurrency = False and state != 'cancelled' order by start asc
        )
    """)

    # WHEN date(start) < now()::date THEN 'Past' start >= now()::date and

    @api.multi
    def _compute_current_datetime(self):
        return datetime.now()

    @api.multi
    def _compute_meeting_responsible(self):
        for meeting in self:
            meeting.is_meeting_responsible = (
                        meeting.user_id == self.env.user or meeting.mom_controller_id in [emp.id for emp in
                                                                                          self.env.user.employee_ids])

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('meetingparticipant'):
            args += [('employee_ids', 'in', [emp.id for emp in self.env.user.employee_ids])]

        return super(KWMeetingScheduleDategroup, self)._search(args, offset=offset, limit=limit, order=order,
                                                               count=count, access_rights_uid=access_rights_uid)

    def action_post_your_input(self):
        view_id = self.env.ref('kw_meeting_schedule.kw_meeting_agenda_proposals_view_form').id
        meeting_id = self.id
        # mode         = 'readonly' if self.state in ['attendance_complete','draft_mom','final_mom','cancelled'] else 'edit'
        return {
            'name': 'Post Your Input',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_agenda_proposals',
            # 'res_id'    : target_id,
            'target': 'new',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'domain': [{'agenda_id': [('meeting_id', '=', meeting_id)]}],
            'context': {'default_meeting_id': meeting_id},
            'flags': {'action_buttons': True, },
        }

    # #display meeting mom
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

    # #action to open cancel the meeting form
    def action_open_cancel_meeting_form(self):
        view_id = self.env.ref('kw_meeting_schedule.view_meeting_schedule_cancel_popup_form').id
        target_id = self.id
        return {
            'name': 'Draft MOM',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_events',
            'res_id': target_id,
            'target': 'new',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'flags': {'action_buttons': True, 'mode': 'edit'},
        }

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
