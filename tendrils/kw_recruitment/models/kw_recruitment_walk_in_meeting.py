# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError

class WalkinMeeting(models.Model):
    
    _name = "kw_recruitment_walk_in_meeting"
    _description = "Meeting schedule with walk in applicants."

    @api.model
    def _get_time_list(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=7, minute=45, second=0, microsecond=0)
        end_loop = dt.replace(hour=22, minute=0, second=0, microsecond=0)

        time_list = []
        while start_loop < end_loop:
            start_loop = (start_loop + relativedelta(minutes=+15))
            time_list.append((start_loop.strftime('%H:%M:%S'),
                              start_loop.strftime('%I:%M %p')))
        return time_list

    @api.model
    def _get_location_domain(self):
        if self.env.user.has_group('kw_meeting_schedule.group_kw_meeting_schedule_manager'):
            return []
        else:
            return [('id', 'in', self.env.user.branch_ids.ids)]

    @api.model
    def _get_meeting_room_domain(self):
        if self.env.user.has_group('kw_meeting_schedule.group_kw_meeting_schedule_manager'):
            return [('restricted_access', '=', False), ('location_id', '=', self.env.user.company_id.id)]
        else:
            return [('location_id', '=', self.env.user.company_id.id),
                    ('restricted_access', '=', False), ]

    @api.model
    def _get_duration_list(self):
        return [(str(i / 60), '{:02d}:{:02d}'.format(*divmod(i, 60)) + ' hrs') for i in range(30, 855, 15)]

    name = fields.Char(string="Meeting Subject")
    date = fields.Date("Date")
    time = fields.Selection(string='Meeting Time', selection='_get_time_list')
    duration = fields.Selection(string='Duration(hh:mm)', selection='_get_duration_list', )
    location_id = fields.Many2one('kw_res_branch', string="Location",domain=_get_location_domain)
    meeting_room_id = fields.Many2one('kw_meeting_room_master',string='Meeting Room',ondelete='restrict',domain=_get_meeting_room_domain)
    member_ids = fields.Many2many("hr.employee",string="Panel Members")

    survey_id = fields.Many2one('survey.survey', string="Interview From", domain=[('survey_type.code', '=', 'recr')])

    meeting_detail_ids = fields.One2many(string='Meeting Details',
                                         comodel_name='kw_walk_in_meeting_details',
                                         inverse_name='walk_in_meeting_id', ondelete='restrict')

    response_ids = fields.One2many(string='Meeting Feedback', comodel_name='survey.user_input',
                                   inverse_name='walk_in_meeting_id',ondelete='restrict')
    
    @api.onchange('location_id')
    def _onchange_location_id(self):
        self.meeting_room_id = False
        if self.location_id:
            # if self.env.user.has_group('kw_meeting_schedule.group_kw_meeting_schedule_manager'):
            #     return {'domain': {
            #         'meeting_room_id': [('location_id', '=', self.location_id.id), ('restricted_access', '=', False) ]}}
            # else:
            return {'domain': {
                'meeting_room_id': [('location_id', '=', self.location_id.id),('restricted_access', '=', False)]}}
    
    @api.model
    def create(self, values):
        meeting = super(WalkinMeeting, self).create(values)
        applicants = meeting.meeting_detail_ids.mapped('applicant_id')
        if meeting.survey_id and applicants and meeting.member_ids:
            user_input=self.env['survey.user_input']
            for applicant in applicants:
                for attendee in meeting.member_ids:
                    user_input.create({
                        'walk_in_meeting_id': meeting.id,
                        'survey_id': meeting.survey_id.id,
                        'partner_id': attendee.user_id.partner_id.id,
                        'type': 'link',
                        'applicant_id': applicant.id
                    })
        return meeting
    
    @api.multi
    def write(self, values):
        
        result = super(WalkinMeeting, self).write(values)
    
        return result
    
    


