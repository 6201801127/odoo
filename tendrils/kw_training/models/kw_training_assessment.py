# -*- coding: utf-8 -*-
import time
import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TrainingAssessment(models.Model):
    _name = "kw_training_assessment"
    _description = "Kwantify Training Assessment"

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
    

    training_id = fields.Many2one(
        "kw_training", string="Training ID", required=True, ondelete="cascade")
    name = fields.Char(string="Assessment Name", required=True)
    marks = fields.Integer(string="Full Marks")   #
    assessment_type = fields.Selection(string="Assessment Type",
                    selection=[('offline', 'Offline'),('online', 'Online')],
                    default="online",required=True)
    date = fields.Date(string='Date',default=fields.Date.context_today,required=True)
    from_time = fields.Selection(
        string='From', selection='_get_time_list', required=True)
    to_time = fields.Selection(
        string='To', selection='_get_time_list', required=True)
    
    assessment_id = fields.Many2one(string='Assessment',comodel_name='kw_skill_question_set_config')
    question_bank_id = fields.Many2one('kw_skill_question_bank_master',string="Question Bank")
    score_id = fields.Many2one('kw_training_score',string="Score")
    user_is_trainer = fields.Boolean(string='Is Trainer?', default=False, compute="_compute_if_trainer")
    user_is_participant = fields.Boolean(string='Is Participant?', default=False, compute="_compute_if_participant")
    user_is_manager = fields.Boolean(string='Is Manager?', default=False, compute="_compute_if_manager")
    user_has_given_assessment = fields.Boolean(string='Assessment Given?', default=False, 
                                                compute="_compute_if_user_given_assessment")
    assessment_expired = fields.Boolean(string='Assessment Expired?', default=False,
                                        compute="_compute_assessment_status")
    assessment_started = fields.Boolean(string='Assessment Expired?', default=False,
                                        compute="_compute_assessment_status")
    
    test_type = fields.Selection(string="Test Type", selection=[('pre', 'Pre Test'),('post', 'Post Test')],default="pre",required=True)
    duration = fields.Char("Duration",compute="_compute_duration")

    @api.onchange('assessment_type')
    def on_change_state(self):
        if self.assessment_type != 'offline':
            self.marks = False

    def format_duration(self,duration):
        formatted_duration = ''
        hour = duration.split(':')[0]
        minute = duration.split(':')[1]
        if int(hour) > 0:
            formatted_duration = hour + ' Hour(s)'
        if int(minute) > 0:
            if len(formatted_duration) > 0:
                formatted_duration += formatted_duration + \
                    ' ' + minute + ' Minutes'
            else:
                formatted_duration = minute + ' Minutes'
        return formatted_duration

    @api.multi
    def _compute_duration(self):
        for record in self:
            if record.assessment_id:
                duration = time.strftime('%H:%M:%S', time.gmtime(int(record.assessment_id.duration)))
                record.duration = self.format_duration(duration)
            
            else:
                tdelta = datetime.strptime(record.to_time, '%H:%M:%S') - datetime.strptime(record.from_time, '%H:%M:%S')
                duration = time.strftime('%H:%M:%S', time.gmtime(tdelta.total_seconds()))
                record.duration = self.format_duration(duration)
    @api.constrains('date', 'from_time', 'to_time')
    def validate_schedule_date(self):
        for record in self:
            if record.from_time > record.to_time:
                raise ValidationError(f'From time should not greater than to time.')
    
    @api.multi
    def _compute_assessment_status(self):
        user_tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
        curr_datetime = datetime.now(tz=user_tz).replace(tzinfo=None)
        for session in self:
            if session.date and session.from_time and session.to_time:
                session_date = session.date
                session_from = session.from_time
                session_to = session.to_time
                session_from_time = datetime(session_date.year, session_date.month, session_date.day,
                                        int(session_from.split(':')[0]), int(session_from.split(':')[1]), 0)
                session_to_time = datetime(session_date.year, session_date.month, session_date.day,
                                        int(session_to.split(':')[0]), int(session_to.split(':')[1]), 0)
                if curr_datetime > session_from_time:
                    session.assessment_started = True
                if curr_datetime > session_to_time:
                    session.assessment_expired=True

    @api.multi
    def action_add_questions(self):
        view_id = self.env.ref('kw_training.kw_training_ques_bank_master_view_form').id
        question_action = {
                'type': 'ir.actions.act_window',
                'res_model': 'kw_skill_question_bank_master',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'self',
            }
        if self.question_bank_id:
            question_action['res_id'] = self.question_bank_id.id
        else:
            question_action['context'] = {
                'default_name':f"{self.name} Test",
                'default_type':'training',
                'default_skill_types': self.training_id.course_type_id.id,
                'default_skill': self.training_id.course_id.id,
            }
        return question_action
    @api.multi
    def _compute_if_user_given_assessment(self):
        for assessment in self:
            if assessment.assessment_type == 'online' and assessment.assessment_id:
                # check if user has given assessment
                assessmnet_given = self.env['kw_skill_answer_master'].sudo().search(
                    [('user_id', '=', self._uid), ('set_config_id', '=', assessment.assessment_id.id)])
                if assessmnet_given:
                    assessment.user_has_given_assessment = True


    def get_root_departments(self, departments):
        parent_departments = departments.mapped('parent_id')
        root_departments = departments.filtered(lambda r : r.parent_id.id == 0)
        if parent_departments:
            root_departments |= self.get_root_departments(parent_departments)
        return root_departments

    @api.multi
    def view_assessment(self):
        view_id = self.env.ref('kw_training.kw_training_question_set_config_form_view').id
        res = {
                'type': 'ir.actions.act_window',
                'res_model': 'kw_skill_question_set_config',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'self',
            }
        if self.assessment_id:
            res['res_id'] =  self.assessment_id.id
        else:
            plan = self.training_id.plan_ids[0] if self.training_id.plan_ids else False
            participants = []
            departments = []
            if plan and plan.participant_ids:
                    participants = plan.participant_ids.ids
                    root_departments = self.get_root_departments(plan.participant_ids.mapped('department_id'))
                    departments = root_departments.ids if root_departments else []
            res['context'] = {
                'default_training_id': self.training_id.id,
                'default_name': f"{self.training_id.name} Test",
                'default_dept': departments,
                'default_skill_types': self.training_id.course_type_id.id,
                'default_skill': self.training_id.course_id.id,
                'default_applicable_candidate': "3",
                'default_frequency': "o",
                'default_select_individual': participants,
                'default_assessment_type': 'training',
                'default_state': 2,
                'default_question_bank_id': self.question_bank_id.id if self.question_bank_id else False
            }
        return res

    @api.multi
    def view_assessment_score(self):
        employee_ids = self.training_id.plan_ids and self.training_id.plan_ids[-1].participant_ids.ids or []
        ctx = self.env.context.copy()
        ctx.update({'set_config_id': self.assessment_id.id,
                    'employee_ids': employee_ids})
        self.env['kw_training_assessment_result'].with_context(ctx).init()
        res = self.env['ir.actions.act_window'].for_xml_id(
            'kw_training', 'action_kw_training_assessment_result_act_window')
        return res
        
    @api.multi
    def view_update_assessment_score(self):
        if self.score_id:
            view_id = self.env.ref(
                'kw_training.view_kw_training_score_form').id
            res = {
                'type': 'ir.actions.act_window',
                'res_model': 'kw_training_score',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'self',
                'res_id':self.score_id.id,
            }
        else:
            view_id = self.env.ref('kw_training.view_kw_training_score_form').id
            participants = []
            if self.training_id.plan_ids and self.training_id.plan_ids[0].participant_ids:
                participants = self.training_id.plan_ids[0].participant_ids.ids
            res =  {
                'type': 'ir.actions.act_window',
                'res_model': 'kw_training_score',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'self',
                'context':{
                    'default_assessment_id':self.id,
                    'default_score_detail_ids': [(0, 0, {'participant_id': pid, 'score':0, 'attendance' : 'attended'}) for pid in participants],
                }
            }
        return res  
    
    @api.multi
    def _compute_if_participant(self):
        current_employee_id = self.env['hr.employee'].search(
            [('user_id', '=', self._uid)], limit=1)
        employee_id = current_employee_id.id if current_employee_id else False
        for assessment in self:
            if employee_id and assessment.training_id.plan_ids and assessment.training_id.plan_ids[0].participant_ids:
                employee_participant = assessment.training_id.plan_ids[0].participant_ids.filtered(
                    lambda r: r.id == employee_id)
                if employee_participant:
                        assessment.user_is_participant = True
    
    @api.multi
    def _compute_if_trainer(self):
        current_employee_id = self.env['hr.employee'].search(
            [('user_id', '=', self._uid)], limit=1)
        employee_id = current_employee_id.id if current_employee_id else False
        for assessment in self:
            if employee_id and assessment.training_id.plan_ids and assessment.training_id.plan_ids[0].internal_user_ids:
                employee_trainer = assessment.training_id.plan_ids[0].internal_user_ids.filtered(
                    lambda r: r.id == employee_id)
                if employee_trainer:
                    assessment.user_is_trainer = True

    @api.multi
    def _compute_if_manager(self):
        for assessment in self:
            if self.env.user.has_group('kw_training.group_kw_training_manager'):
                assessment.user_is_manager = True
    
    @api.multi
    def view_assessment_readonly_score(self):
        if self.score_id:
           view_id = self.env.ref(
               'kw_training.view_kw_training_score_readonly_form').id
           res =  {
               'type': 'ir.actions.act_window',
               'res_model': 'kw_training_score',
               'view_mode': 'form',
               'view_type': 'form',
               'view_id': view_id,
               'res_id':self.score_id.id,
               'target': 'self',
           }
        #take to own score page
        if self.assessment_id:
            res = self.env['ir.actions.act_window'].for_xml_id(
                'kw_training', 'kw_user_trainingtest_report_action_window')
            res['domain'] = [('set_config_id', '=', self.assessment_id.id)]
        return res
            
    
    @api.multi
    def view_assessment_participant_score(self):
        # print("participant result method called")
        if self.assessment_id:
            assessment_given = self.env['kw_skill_answer_master'].sudo().search(
                [('user_id', '=', self._uid), ('set_config_id', '=', self.assessment_id.id)], limit=1)
            view_id = self.env.ref(
                'kw_skill_assessment.kw_question_user_report_form_view').id
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'kw_skill_answer_master',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'res_id': assessment_given.id,
                'target': 'self',
                'flags': {"toolbar": False}
            }
        if self.score_id:
            view_id = self.env.ref('kw_training.view_kw_training_assessment_readonly_participant_form').id
            current_employee = self.env['hr.employee'].search(
                [('user_id', '=', self.env.user.id)], limit=1)
            employee_id = current_employee.id if current_employee else False
            emp_score_id = self.score_id.score_detail_ids.filtered(
                lambda r: r.participant_id.id == employee_id)
            return {
                # 'name':'Result',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_training_score_details',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'res_id': emp_score_id.id,
                'target': 'self',
            }

    @api.multi
    def action_assessment_test(self):
        # print("in assessment test=================================================")
        if self.assessment_id:
            return self.assessment_id.take_test(extra_params=self.test_type.capitalize()+' Test')