# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class kw_meeting_agenda_activities(models.Model):
    _name           = 'kw_meeting_agenda_activities'
    _description    = 'Meeting Activities'
    _inherit        = ["mail.thread"]

    name = fields.Text(
        string='Description',
        required=True,
    )

    agenda_id = fields.Many2one(
        string='Agenda',
        comodel_name='kw_meeting_agenda',
        ondelete='restrict', required=True,
    )

    meeting_id = fields.Many2one(
        string='Meeting ',
        related='agenda_id.meeting_id',
        readonly=True,
        store=False
    )

    target_date = fields.Date(
        string='Target Date',
        # default=fields.Date.context_today,
    )

    @api.model
    def _get_default_employee_domain(self):
        event_id = self._context.get('default_meeting_id', False)
        if event_id:
            present_emplyees = self.env['kw_meeting_attendee'].search(
                [('event_id', '=', event_id)])
            # if present_emplyees:
                         
            return [('id', 'in', [employee.employee_id.id for employee in present_emplyees])]
            

    assigned_to = fields.Many2one(
        string='Assigned To',
        comodel_name='hr.employee',
        ondelete='restrict',
        # domain=[('user_id','!=',False),('id','in',[1,2])],
        domain=_get_default_employee_domain
    )

    activity_remark = fields.Html(
        string='Remark',
        track_visibility='onchange'

    )

    activity_document = fields.Binary(
        string='Document',
        attachment=True
    )

    STATE_SELECTION = [

        ('info', 'Informational'),
        ('activity', 'Action Item'),
    ]

    activity_type = fields.Selection(STATE_SELECTION, string='Activity Type')
    mom_info = fields.Html(string='Information', )

    state = fields.Selection(
        string='Status',
        selection=[('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('completed', 'Completed')],
        default='not_started', track_visibility='onchange',
    )

    @api.constrains('target_date', 'activity_type')
    def _check_target_date(self):
        for meeting in self:
            if meeting.activity_type == 'activity' and not meeting.target_date:
                raise ValidationError('Please enter target date')

            if meeting.activity_type == 'activity' and meeting.target_date < meeting.agenda_id.meeting_id.kw_start_meeting_date:
                raise ValidationError('Target date should not be less than meeting date')

    @api.constrains('activity_type', 'assigned_to')
    def _check_assigned_to(self):
        for meeting in self:
            if meeting.activity_type == 'activity' and not meeting.assigned_to:
                raise ValidationError('Please select responsible employee for the activity')

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('mymeetingtasks'):
            args += [('assigned_to', 'in', [emp.id for emp in self.env.user.employee_ids]),
                     ('meeting_id.state', '=', 'final_mom')]

        if self._context.get('participantmeetingtasks'):
            args += [('meeting_id.employee_ids', 'in', [emp.id for emp in self.env.user.employee_ids])]

        return super(kw_meeting_agenda_activities, self)._search(args, offset=offset, limit=limit, order=order,
                                                                 count=count, access_rights_uid=access_rights_uid)

    @api.model
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """

        result = super(kw_meeting_agenda_activities, self).create(values)

        for activity in result:
            if self.env.user.id != activity.meeting_id.user_id.id and self.env.user.id != activity.meeting_id.mom_controller_id.user_id.id:
                raise ValidationError("You are not allowed to create a activity for the selected meeting.")

        return result

    @api.multi
    def unlink(self):
        for record in self:
            if record.meeting_id.state in ('final_mom'):
                raise UserError(
                    'You cannot delete an activity after final MOM has been generated!'
                )
        return super(kw_meeting_agenda_activities, self).unlink()

    # def send_meeting_task_reminder_to_employee(self):

    #     recurrent_events = self.env['kw_meeting_agenda_activities'].search([('state','!=','completed'),('parent_id','>',0),('start','>=',today),('start','<',tomorrow)])

   