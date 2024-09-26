# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, date
import pytz


class kw_feedback_assessment_period(models.Model):
    _name = 'kw_feedback_assessment_period'
    _description = 'Assessment'
    _order = 'period_date'

    name = fields.Char(string='Period Name', autocomplete="off")
    period_date = fields.Date(string='Period Date', autocomplete="off")
    assessees = fields.Many2many('hr.employee', 'kw_feedback_period_assessee_rel', 'period_id', 'emp_id',
                                 string='Assessee')
    assessors = fields.Many2many('hr.employee', 'kw_feedback_period_assessor_rel', 'period_id', 'emp_id',
                                 string='Assessor')
    from_date = fields.Date(string='From Date', autocomplete="off")
    to_date = fields.Date(string='To Date', autocomplete="off")
    assessment_date = fields.Date(string='Assessment Date', autocomplete="off")
    survey_id = fields.Many2one(comodel_name='survey.survey', string='Template Type',
                                domain="[('survey_type.code','=','assessment_feedback')]", required=True)
    map_resource_id = fields.Many2one(comodel_name='kw_feedback_map_resources', string='Mapping Resource Name',
                                      ondelete='restrict')
    assessment_name = fields.Many2one(related='map_resource_id.assessment_tagging_id')
    state = fields.Selection(string='Schedule Status', selection=[('1', 'Not Scheduled'), ('2', 'Scheduled')],
                             default='1')
    feedback_id = fields.One2many('kw_feedback_details', 'period_id', string='Generated Feedbacks')
    show_generate_feedback_action_buttons = fields.Boolean(string="Show Generate Feedback Buttons",
                                                           compute="_show_current_month_generate_feedback_action_button",
                                                           default=False)
    hide_generate_button = fields.Boolean(string="Hide Generate Button",
                                          compute="_show_current_month_generate_feedback_action_button", default=False)
    rrule_type = fields.Selection(related='map_resource_id.assessment_tagging_id.frequency', string='Recurrence')
    assessment_type = fields.Selection(related='map_resource_id.assessment_tagging_id.assessment_type', string='Type')

    meeting_id = fields.Many2one(comodel_name='kw_meeting_events', string='Meeting Name', ondelete='restrict')
    meeting_date = fields.Date(related='meeting_id.kw_start_meeting_date')
    meeting_time = fields.Selection(related='meeting_id.kw_start_meeting_time')
    meeting_duration = fields.Selection(related='meeting_id.kw_duration')
    meeting_room = fields.Many2one(comodel_name='kw_meeting_room_master', related='meeting_id.meeting_room_id')
    prob_assessment_tag_id = fields.Many2one(comodel_name='kw_feedback_assessment', string='Assessment Type')
    active = fields.Boolean(string="Active", default=True)
    # deactive_records = fields.Boolean(compute='_get_deactivate_records', store=False)

    def toggle_active(self):
        if self.active == True:
            self.write({'active': False})
        else:
            self.write({'active': True})
            
    # @api.depends('map_resource_id.period_ids')
    # def cal_sequence(self):
    #     for record , i in zip(self,range(1,len(self)+1)):
    #             record.sequence = i

    # @api.multi
    # @api.depends('map_resource_id.period_ids')
    # def cal_sequence(self):
    #     for rec in self:
    #         print(rec)
    #         for i in range(1,len(self)+1):
    #             # print(i)
    #             rec.sequence =  i
    #             # x = self.env['kw_feedback_assessment_period'].search([])
    #             # x.write({'sequence': i})
    #             # print(x)
    #             # break
    #             # rec.sequence.write({'sequence':'i'})

    # @api.multi
    # def write(self, values):
    #     res = super('kw_feedback_assessment_period',self).write(values)
    #     print(values)
    #     return res

    # @api.multi
    # @api.depends('map_resource_id.period_ids')
    # def cal_sequence(self):
    #     for record in self:
    #         for i in range(1,len(self)+1):
    #             print(record.period_date)
    # record.write({'sequence':record.period_date})

    # x = self.env['kw_feedback_assessment_period'].search([])
    # x.write({'sequence':2})
    # print(x)

    # @api.multi
    # @api.depends('assessees')
    # def _get_deactivate_records(self):
    #     for record in self:
    #         if not record.assessees:
    #             record.write({'active': False})
    #         else:
    #             record.write({'active': True})

    @api.model
    def create(self, vals):
        new_record = super(kw_feedback_assessment_period, self).create(vals)
        if self._context and 'probationary' in self._context:
            if new_record.prob_assessment_tag_id and new_record.assessment_date:
                new_record.write({
                    'name': new_record.assessment_date.strftime("%B") + "-" + str(new_record.assessment_date.year),
                    'period_date': new_record.assessment_date,
                })
            new_record._add_to_specific_group()

        return new_record

    @api.multi
    def write(self, vals):
        update_record = super(kw_feedback_assessment_period, self).write(vals)
        if self._context and 'probationary' in self._context and ('assessors' in vals or 'assessees' in vals):
            self._add_to_specific_group()
        return update_record

    def _add_to_specific_group(self):
        assessor_group = self.env.ref('kw_assessment_feedback.group_assessment_feedback_assessor')
        assessee_group = self.env.ref('kw_assessment_feedback.group_assessment_feedback_assessee')
        assessor_users = self.assessors.mapped('user_id')
        for user in assessor_users:
            if not user.has_group('kw_assessment_feedback.group_assessment_feedback_assessor'):
                assessor_group.sudo().write({'users': [(4, user.id)]})

        assessee_users = self.assessees.mapped('user_id')
        for user in assessee_users:
            if not user.has_group('kw_assessment_feedback.group_assessment_feedback_assessee'):
                assessee_group.sudo().write({'users': [(4, user.id)]})

    # @api.constrains('assessees','assessors')
    # def assessor_assessee_validation(self):
    #     for record in self:
    #         if not record.assessors or not record.assessees:
    #             raise ValidationError("Assessor or Assessee should not blank.")

    @api.onchange('from_date', 'to_date')
    def date_validation(self):
        if self.from_date and self.to_date and self.period_date:
            if self.from_date > self.to_date:
                raise ValidationError('From Date must be less than to date.')
            if self.from_date.month != self.period_date.month:
                raise ValidationError("From Date's month should be equal to period date's month.")
            if self.to_date.month != self.period_date.month:
                raise ValidationError("To Date's month should be equal to period date's month.")

    def _show_current_month_generate_feedback_action_button(self):
        feedback_details = self.env['kw_feedback_details']
        for record in self:
            record.show_generate_feedback_action_buttons = True if record.period_date.month == datetime.today().month else False
            feedback_details_id = feedback_details.search(
                [('period_id.map_resource_id', '=', record.map_resource_id.id), ('feedback_status', 'not in', ['0'])])
            for rec in feedback_details_id:
                record.hide_generate_button = True if rec.period_id.period_date.month == record.period_date.month else False

    @api.multi
    def manage_feedback_meeting(self):
        self.ensure_one()
        participants = []

        if self.assessors:
            participants = self.assessors.ids

        participants += self.assessees.ids

        view_id = self.env.ref('kw_meeting_schedule.view_kw_meeting_calendar_event_form').id
        assessment_tag = self.env.ref('kw_meeting_schedule.meeting_type_63')

        context = {
            'create': False,
            'default_kw_start_meeting_date': self.assessment_date,
            'default_name': f'{self.prob_assessment_tag_id.name}',
            'default_email_subject_line': f'{self.prob_assessment_tag_id.name}',
            'default_employee_ids': [(6, 0, participants)],
            'default_meeting_category': 'general',
            'default_agenda_ids': [[0, 0, {'name': self.prob_assessment_tag_id.name}]],
            'default_meeting_type_id': assessment_tag.id,
            'default_categ_ids': [(6, 0, assessment_tag.ids)],
            'default_location_id': self.env.user.branch_id.id,
        }

        _action = {
            'name': 'Assessment Meeting Schedule',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_events',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            'flags': {'action_buttons': False, 'mode': 'edit', 'toolbar': False, },
        }

        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        dt = datetime.now(timezone)

        if (self.meeting_id and self.meeting_id.start_datetime
                and self.meeting_id.start_datetime.astimezone(timezone) >= dt):
            _action['res_id'] = self.meeting_id.id
        else:
            self.meeting_id = False
            _action['res_id'] = False

        if not self.meeting_id or (self.meeting_id and self.meeting_id.start_datetime
                                   and self.meeting_id.start_datetime.astimezone(timezone) < dt):
            _action['context'] = context
        else:
            _action['context'] = {'create': False}

        return _action
