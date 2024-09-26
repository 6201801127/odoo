# -*- coding: utf-8 -*-
from odoo import models , fields , api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

class TrainingAttendance(models.Model):
    _name = 'kw_training_attendance'
    _description = "Kwantify Training Attendance"
    _rec_name = "training_id"

    @api.model
    def _get_time_list(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=7, minute=45, second=0, microsecond=0)
        end_loop = dt.replace(hour=22, minute=0, second=0, microsecond=0)
        time_list = []
        while start_loop < end_loop:
            start_loop = (start_loop+relativedelta(minutes=+15))
            time_list.append((start_loop.strftime('%H:%M:%S'),
                              start_loop.strftime('%I:%M %p')))
        return time_list

    training_id = fields.Many2one("kw_training",string='Training',ondelete="restrict")
    attendance_detail_ids = fields.One2many("kw_training_attendance_details","attendance_id",string="Participant")
    session_id = fields.Many2one(string='Session',comodel_name='kw_training_schedule',ondelete='restrict',)
    from_time = fields.Selection('_get_time_list', related='session_id.from_time', store=True)
    to_time = fields.Selection('_get_time_list', related='session_id.to_time', store=True)
    date = fields.Date("Date", related="session_id.date")

    @api.constrains('training_id','attendance_detail_ids')
    def _check_participants(self):
        for record in self:
            if record.training_id and not record.attendance_detail_ids:
                raise ValidationError(
                    "At least one partictipant should be added to attendance.")
            elif record.training_id and record.attendance_detail_ids:
                participants = record.training_id.plan_ids[0].participant_ids if record.training_id.plan_ids else False
                if participants:
                    '''check attendance details contains all the training participants'''
                    for participant in participants:
                        exist_participant = record.attendance_detail_ids.filtered(
                            lambda r: r.participant_id.id == participant.id)
                        if not exist_participant:
                            raise ValidationError(f"Participant {participant.name} should be added to attendance.")
    
    @api.model
    def create(self, values):
        # print("training attendance create called")
        result = super(TrainingAttendance, self).create(values)
        if 'active_model' and 'active_id' in self._context:
            if self._context['active_model'] == 'kw_training_schedule':
                schedule_id = self._context['active_id']
                schedule_rec = self.env['kw_training_schedule'].browse(schedule_id)
                if schedule_rec and not schedule_rec.attendance_id:
                    schedule_rec.attendance_id = result.id
        plan = result.training_id.plan_ids[-1] if result.training_id.plan_ids else False
        if plan :
            new_participants = result.attendance_detail_ids.mapped('participant_id') - plan.participant_ids

            survey_user_group = self.env.ref('survey.group_survey_user')
            dms_user_group = self.env.ref('kw_dms.group_dms_user')
            training_employee_group = self.env.ref('kw_training.group_kw_training_employee')
            skill_assessment_user_group = self.env.ref('kw_skill_assessment.group_kw_skill_assessment_user')

            for participant_emp in new_participants:
                plan.write({'participant_ids': [(4, participant_emp.id)]})

                if participant_emp.user_id:
                    p_user = participant_emp.user_id

                    if not p_user.has_group('kw_training.group_kw_training_employee'):
                        training_employee_group.sudo().write({'users': [(4, p_user.id)]})
                    if not p_user.has_group('survey.group_survey_user'):
                        survey_user_group.sudo().write({'users': [(4, p_user.id)]})
                    if not p_user.has_group('kw_dms.group_dms_user'):
                        dms_user_group.sudo().write({'users': [(4, p_user.id)]})
                    if not p_user.has_group('kw_skill_assessment.group_kw_skill_assessment_user'):
                        skill_assessment_user_group.sudo().write({'users': [(4, p_user.id)]})
        return result

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if 'active_model' and 'active_id' in self._context:
                if self._context['active_model'] == 'kw_training_schedule':
                    schedule_id = self._context['active_id']
                    schedule_rec = self.env['kw_training_schedule'].browse(schedule_id)
                    if schedule_rec and schedule_rec.subject:
                        result.append((record.id, schedule_rec.subject))
        return result
    
    @api.multi
    def write(self, values):
        # print("training attendance write called")
        result = super(TrainingAttendance, self).write(values)
        for record in self:
            plan = record.training_id.plan_ids[-1] if record.training_id.plan_ids else False
            if plan:
                new_participants = record.attendance_detail_ids.mapped('participant_id') - plan.participant_ids
                survey_user_group = self.env.ref('survey.group_survey_user')
                dms_user_group = self.env.ref('kw_dms.group_dms_user')
                training_employee_group = self.env.ref('kw_training.group_kw_training_employee')
                skill_assessment_user_group = self.env.ref('kw_skill_assessment.group_kw_skill_assessment_user')

                for participant_emp in new_participants:
                    plan.write({'participant_ids': [(4, participant_emp.id)]})

                    if participant_emp.user_id:
                        p_user = participant_emp.user_id

                        if not p_user.has_group('kw_training.group_kw_training_employee'):
                            training_employee_group.sudo().write({'users': [(4, p_user.id)]})
                        if not p_user.has_group('survey.group_survey_user'):
                            survey_user_group.sudo().write({'users': [(4, p_user.id)]})
                        if not p_user.has_group('kw_dms.group_dms_user'):
                            dms_user_group.sudo().write({'users': [(4, p_user.id)]})
                        if not p_user.has_group('kw_skill_assessment.group_kw_skill_assessment_user'):
                            skill_assessment_user_group.sudo().write({'users': [(4, p_user.id)]})
        return result