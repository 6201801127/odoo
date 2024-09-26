# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo import models,api


class TrainingPlan(models.Model):
    _inherit = "kw_training_plan"
    
    @api.multi
    def approve_remark(self):
        self.write({'state': 'approved', 'action_taken_on': datetime.now()})
        # self.training_id.plan_status = "Plan Approved"
        template = self.env.ref('kw_training.training_plan_action_mail')
        template2 = self.env.ref('kw_training.training_plan_annouce_mail')

        if template:
            template.send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            
        # Send email to department members

        if template2 and self.department_ids:
            employees = self.env['hr.employee'].search([('department_id', 'in', self.department_ids.ids)])
            for emp in  employees:
                name = emp.name
                email = emp.work_email
                template2.with_context(email_to=email,emp_name=name).send_mail(self.id,
                    notif_layout="kwantify_theme.csm_mail_notification_light")
                                                                                
        # add trainers to trainer group in training mudule ,
        # so that they can create questions for assessment of participants
        survey_user_group = self.env.ref('survey.group_survey_user')
        dms_user_group = self.env.ref('kw_dms.group_dms_user')
        training_employee_group = self.env.ref(
            'kw_training.group_kw_training_employee')
        trainer_group = self.env.ref('kw_training.group_kw_training_trainer')
        meeting_user_group = self.env.ref(
            'kw_meeting_schedule.group_kw_meeting_schedule_user')
        skill_assessment_user_group = self.env.ref(
            'kw_skill_assessment.group_kw_skill_assessment_user')
        trainer_users = self.internal_user_ids.mapped('user_id')
        # print("trainer users are",trainer_users)
        for user in trainer_users:
            if not user.has_group('kw_training.group_kw_training_trainer'):
                trainer_group.sudo().write({'users': [(4, user.id)]})
                # user.write({'groups_id': [(4, trainer_group.id)]})
            if not user.has_group('survey.group_survey_user'):
                survey_user_group.sudo().write({'users': [(4, user.id)]})
                # user.write({'groups_id': [(4, survey_user_group.id)]})
            if not user.has_group('kw_dms.group_dms_user'):
                dms_user_group.sudo().write({'users': [(4, user.id)]})
                # user.write({'groups_id': [(4, dms_user_group.id)]})
            if not user.has_group('kw_meeting_schedule.group_kw_meeting_schedule_user'):
                meeting_user_group.sudo().write({'users': [(4, user.id)]})
                # user.write({'groups_id': [(4, meeting_user_group.id)]})
        participant_users = self.participant_ids.mapped('user_id')
        # print("participant users are",participant_users)
        for p_user in participant_users:
            if not p_user.has_group('kw_training.group_kw_training_employee'):
                training_employee_group.sudo().write(
                    {'users': [(4, p_user.id)]})
                # p_user.write({'groups_id': [(4, training_employee_group.id)]})
            if not p_user.has_group('survey.group_survey_user'):
                survey_user_group.sudo().write({'users': [(4, p_user.id)]})
                # p_user.write({'groups_id': [(4, survey_user_group.id)]})
            if not p_user.has_group('kw_dms.group_dms_user'):
                dms_user_group.sudo().write({'users': [(4, p_user.id)]})
                # p_user.write({'groups_id': [(4, dms_user_group.id)]})
            if not p_user.has_group('kw_meeting_schedule.group_kw_meeting_schedule_user'):
                meeting_user_group.sudo().write({'users': [(4, p_user.id)]})
                # p_user.write({'groups_id': [(4, meeting_user_group.id)]})
            if not p_user.has_group('kw_skill_assessment.group_kw_skill_assessment_user'):
                skill_assessment_user_group.sudo().write(
                    {'users': [(4, p_user.id)]})
                # p_user.write({'groups_id': [(4, skill_assessment_user_group.id)]})

        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload', }
        
        action_id = self.env.ref('kw_training.kw_training_plan_approve_act_window').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_training_plan&view_type=list',
            'target': 'self',
        }
