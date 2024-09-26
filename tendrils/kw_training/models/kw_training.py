# -*- coding: utf-8 -*-
import pytz
from datetime import date,datetime
from odoo import models,fields,api
from odoo.exceptions import UserError,ValidationError
from odoo.addons.http_routing.models.ir_http import slug



def get_current_financial_dates():
    current_date = date.today()
    current_year = date.today().year
    if current_date < date(current_year, 4, 1):
        start_date = date(current_year - 1, 4, 1)
        end_date = date(current_year, 3, 31)
    else:
        start_date = date(current_year, 4, 1)
        end_date = date(current_year + 1, 3, 31)
    return start_date, end_date


start_date, end_date = get_current_financial_dates()


class Training(models.Model):
    _name = "kw_training"
    _order = "start_date desc"
    _description = "Kwantify Training"

    financial_year = fields.Many2one('account.fiscalyear', string="Financial Year",
                                     required=True)
    training_req_id = fields.Many2one('hr.employee',string="Training Requester")
    course_type_id = fields.Many2one('kw_skill_type_master', string="Course Type", required=True)

    course_id = fields.Many2one('kw_skill_master', string="Course", required=True)
    name = fields.Char(string="Training Title", required=True, size=50)
    start_date = fields.Date(string="Start Date", default=fields.Date.context_today, required=True)
    end_date = fields.Date(string="End Date", required=True, default=fields.Date.context_today)
    instructor_type = fields.Selection(string='Instructor',
                                       selection=[('internal', 'Internal'), ('external', 'External'),('oem','OEM')],
                                       default="internal", required=True)
    highlight = fields.Boolean(string="Highlighted ?")
    plan_ids = fields.One2many(string='Plan ID', comodel_name='kw_training_plan', inverse_name='training_id', )
    session_ids = fields.One2many('kw_training_schedule', 'training_id', string="Schedule ID", )
    material_ids = fields.One2many('kw_training_material', 'training_id', string="Materials")
    feedback_ids = fields.One2many('kw_training_feedback', 'training_id', string="Feedback ID")
    state = fields.Selection(string="State",
                             selection=[('draft', 'Draft'), ('planned', 'Planned'), ('scheduled', 'Scheduled')],
                             default="draft")

    subjects_attended = fields.Integer("Sessions Attended", compute="_compute_subject_attended")
    total_subjects = fields.Integer("Total Sessions", compute="_compute_subject_attended")  # All Subjects
    total_feedback_given = fields.Integer("Total Feedback Given", compute="_compute_given_feedback")
    plan_status = fields.Char("Plan Status", compute="_compute_plan_status", search="_search_plan_status")
    color = fields.Char(compute="_compute_plan_status")
    feedback_count = fields.Integer("Number Of Feedbacks", compute="_compute_feedback")  # All feedbacks
    session_count = fields.Integer("Number Of Sessions", compute="_compute_sessions")  # All sessions
    material_count = fields.Integer("Number Of Materials", compute="_compute_material")  # All Materials
    is_participant = fields.Boolean(compute='_compute_participant', )
    is_trainer = fields.Boolean(compute='_compute_trainer', )
    trainer_session_count = fields.Integer("Number Of Sessions Taken By Trainer", compute="_compute_trainer_session")
    current_financial_year = fields.Boolean("current Financial Year", compute='_compute_participant',
                                            search="_search_current_financial_year")

    assessment_ids = fields.One2many(string='Assessments', comodel_name='kw_training_assessment',
                                     inverse_name='training_id')
    test_available = fields.Boolean(string="Test Available ?", compute="compute_if_test_available", default=False)
    training_type = fields.Selection([('PIP', 'PIP'), ('Others','Others')],string="Training Type",default="Others")
    pip_training_id = fields.Many2one('performance_improvement_plan', string="PIP Training Ref No.", 
        help="Select the reference number from recommended trainings")
    pip_ref = fields.Char(string="PIP Ref")
    

    # show_pip_training_field = fields.Boolean(string='Show PIP Fields',default=False)

    # @api.onchange('course_type_id')
    # def _onchange_course_type(self):
    #     for rec in self:
    #         if rec.course_type_id.skill_type == 'PIP':
    #             self.show_pip_training_field = True
            
    #         else:
    #             self.show_pip_training_field = False

    # @api.depends('course_type_id')
    # def _compute_show_pip_training_fields(self):
    #     for rec in self:
    #         rec.show_pip_training_field = rec.course_type_id.skill_type in ['PIP']



    # @api.onchange('course_type_id')
    # def _onchange_course_type_id(self):
    #     if self.course_type_id and self.course_type_id.skill_type == 'PIP':  # Adjust this condition based on your actual value check
    #         self.course_id = False
    #         self._fields['course_id'].required = False
    #     else:
    #         self._fields['course_id'].required = True
            
    @api.model
    def check_pending_feedback(self, user_id):
        user = user_id
        feedback_url = False
        employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', user)], limit=1)
        if employee_id:
            curr_date = date.today()
            trainings = self.env['kw_training'].sudo().search([('session_ids', '!=', False), ('end_date', "<", curr_date)])

            for record in trainings:
                attendance_details = record.mapped('session_ids.attendance_id.attendance_detail_ids')
                attended = attendance_details.filtered(lambda recs: recs.participant_id.id == employee_id.id and recs.attended == True)
                if attended:
                    feedback_submitted = self.env['kw_training_feedback'].sudo().search(
                        [('emp_id', '=', employee_id.id), ('training_id', '=', record.id)])
                    if not feedback_submitted:
                        survey_id = self.env.ref('kw_training.kw_training_survey_feedback_form')
                        feedback_url = f"/training-feedback/{slug(record)}/{slug(employee_id)}/{slug(survey_id)}"
                        return feedback_url
        return feedback_url

    @api.multi
    def compute_if_test_available(self):
        for training in self:
            any_test_available = training.assessment_ids.filtered(lambda r: r.assessment_id != False and r.user_has_given_assessment == False and r.user_is_participant == True and r.assessment_started == True and r.assessment_expired == False)
            if any_test_available:
                training.test_available = True

    @api.multi
    def action_training_test(self):
        any_test_available = self.assessment_ids.filtered(lambda r: r.assessment_id != False and r.user_has_given_assessment == False and r.user_is_participant == True and r.assessment_started == True and r.assessment_expired == False)
        if not any_test_available:
            raise ValidationError("Probably you have missed the test time.")
        return any_test_available[-1].action_assessment_test()

    @api.multi
    def unlink(self):
        '''
        cases when a training can't be deleted.
            1-assessment having assessment_id from skill
            2-attendance updated for a session
            3-meeting is booked for a session i.e meeting id from meeting schedule
         '''
        for training in self:
            if training.session_ids:
                session_having_attendance_id = training.session_ids.filtered(lambda r: r.attendance_id.id > 0)
                if session_having_attendance_id:
                    raise ValidationError(f"Training {training.name} can't be deleted due to \
                        attendance is updated for session {session_having_attendance_id[0].subject}")
            if training.assessment_ids:
                assessment_having_assessment_id = training.assessment_ids.filtered(lambda r: r.assessment_id.id > 0)
                if assessment_having_assessment_id:
                    raise ValidationError(f"Training {training.name} can't be deleted due to \
                        test is configured for assessment {assessment_having_assessment_id[0].name}")
        result = super(Training, self).unlink()
        self.env.user.notify_success("Training(s) deleted successfully.")
        return result
    
    @api.multi
    def _compute_trainer_session(self):
        uid = self._uid
        emp_id = self.env['hr.employee'].search([('user_id', '=', uid)], limit=1)
        for record in self:
            record.trainer_session_count = 0
            if emp_id:
                trainer_sessions = self.env['kw_training_schedule'].search([
                    ('training_id', '=', record.id), ('instructor', '=', emp_id.id)])
                for session in trainer_sessions:
                    """ check whether current datetime is greater than session end time..
                    if so , then trainer has taken the session """
                    user_tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
                    curr_datetime = datetime.now(tz=user_tz)
                    s_date = session.date
                    to_time = session.to_time
                    session_end_time = datetime(s_date.year, s_date.month, s_date.day,
                                                int(to_time.split(':')[0]), int(to_time.split(':')[1]), 0).replace(tzinfo=user_tz)
                    if curr_datetime > session_end_time:
                        record.trainer_session_count += 1

    @api.multi
    def _search_current_financial_year(self, operator, value):
        return ['&', ('start_date', '>=', start_date), ('end_date', '<=', end_date)]

    @api.multi
    def _search_plan_status(self, operator, value):
        training_ids = self.env['kw_training'].with_context(active_test=False).search([])
        not_planned = training_ids.filtered(lambda rec : len(rec.plan_ids) == 0)
        if value == "Not Planned":
            return [('id', 'in', not_planned.ids)]
        if value == "Rejected":
            rejected_list = []
            training_ids = self.env['kw_training'].with_context(active_test=False).search([('plan_ids', '!=', False), ('plan_ids.state', '=', 'rejected')])
            for tr in training_ids:
                latest_plan_date = max(tr.plan_ids.mapped('write_date'))
                latest_plan_rejected = tr.plan_ids.filtered(lambda plan_list: plan_list.write_date == latest_plan_date and plan_list.state == 'rejected')
                if latest_plan_rejected:
                    rejected_list.append(latest_plan_rejected.training_id.id)
            return [('id', 'in', rejected_list)]

    @api.multi
    @api.depends('plan_ids', 'plan_ids.state')
    def _compute_plan_status(self):
        for record in self:
            rec = self.env['kw_training_plan'].with_context(active_test=False).sudo().search([('training_id', '=', record.id)], order="write_date desc", limit=1)
            if rec:
                if rec.state=="rejected":
                    record.plan_status = "Rejected"
                    record.color = 'red'
                elif rec.state == 'apply':
                    record.plan_status = "Applied"
                    record.color = 'orange'
                elif rec.state == "approved":
                    record.plan_status = "Approved"
                    record.color = 'green'
                elif rec.state == "draft":
                    record.plan_status = "Draft"
                    record.color = "purple"
            else:
                record.plan_status = "Not Planned"
                record.color = 'yellow'

    @api.multi
    def _compute_feedback(self):
        for record in self:
            feedbacks = self.env['kw_training_feedback'].search([('training_id', '=', record.id)])
            record.feedback_count = len(feedbacks)

    @api.multi
    def _compute_sessions(self):
        for record in self:
            sessions = self.env['kw_training_schedule'].search([('training_id', '=', record.id)])
            record.session_count = len(sessions)

    @api.multi
    def _compute_material(self):
        for record in self:
            materials = self.env['kw_training_material'].search([('training_id', '=', record.id)])
            record.material_count = len(materials)

    @api.multi
    def _compute_subject_attended(self):
        uid = self._uid
        emp_id = self.env['hr.employee'].search([('user_id', '=', uid)], limit=1)
        emp_partner_id = emp_id.user_id.partner_id.id if emp_id.user_id else False
        for record in self:
            if record.session_ids:
                record.total_subjects = len(record.session_ids)
                if emp_partner_id:
                    for r in record.session_ids:
                        if r.attendance_id and r.attendance_id.attendance_detail_ids:
                            attendance_present = r.attendance_id.attendance_detail_ids.filtered(lambda recs: recs.participant_id.id == emp_id.id and recs.attended == True)
                            if attendance_present:
                                record.subjects_attended += 1
            else:
                record.subjects_attended = 0

    @api.multi
    def _compute_given_feedback(self):
        for record in self:
            record.total_feedback_given = len(self.env['kw_training_feedback'].search(
                ['&', ('training_id', '=', record.id), ('create_uid', '=', self._uid)]))

    @api.multi
    def _compute_participant(self):
        uid = self._uid
        emp_id = self.env['hr.employee'].search([('user_id', '=', uid)], limit=1)
        for record in self:
            if record.plan_ids:
                for employee in record.plan_ids[0].participant_ids:
                    if employee.id == emp_id.id:
                        record.is_participant = True

    @api.multi
    def _compute_trainer(self):
        uid = self._uid
        emp_id = self.env['hr.employee'].search([('user_id', '=', uid)], limit=1)
        for record in self:
            if record.plan_ids:
                for emp in record.plan_ids[0].internal_user_ids:
                    if emp.id == emp_id.id:
                        record.is_trainer = True
            
    @api.multi
    def view_training_assessment(self):
        ''' if only one assessment is there then return direct form view of the 
        assessment otherwise return the tree view of assessment'''
        view_id = self.env.ref('kw_training.view_kw_training_assessment_form').id
        default_data = {
            "default_training_id":self.id,
            "default_name":self.name,
        }
        if not self.assessment_ids:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'kw_training_assessment',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'self',
                'context': default_data
            }
        else:
            tree_view_id = self.env.ref('kw_training.view_kw_training_assessment_tree').id
            form_view_id = self.env.ref('kw_training.view_kw_training_assessment_form').id
            kanban_view_id = self.env. ref('kw_training.view_kw_training_assessment_kanban').id

            return {
                'model': 'ir.actions.act_window',
                'name': 'Assessments',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form,tree,kanban',
                'res_model': 'kw_training_assessment',
                'views': [(kanban_view_id, 'kanban'), (tree_view_id, 'tree'), (form_view_id, 'form')],
                'domain': [('training_id', '=', self.ids[0])],
                'context': default_data
            }

    @api.multi
    def edit_assesment(self):
        for record in self:
            view_id = self.env.ref('kw_training.kw_training_question_set_config_form_view').id
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'kw_skill_question_set_config',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'res_id': record.question_set_config_id.id,
                'target': 'self',
                'flags': {'mode': 'edit', "toolbar": False}
            }

    @api.multi
    def view_training_feedback(self):
        tree_view_id = self.env.ref('kw_training.view_kw_training_feedback_tree').id
        form_view_id = self.env.ref('kw_training.view_kw_training_feedback_form').id
        return {
            'model': 'ir.actions.act_window',
            'name': 'Feedbacks',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'kw_training_feedback',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('training_id', '=', self.ids[0])],
        }

    @api.multi
    def view_training_participant_feedback(self):
        tree_view_id = self.env.ref('kw_training.view_kw_training_feedback_tree_participant').id
        form_view_id = self.env.ref('kw_training.view_kw_training_feedback_form').id
        return {
            'model': 'ir.actions.act_window',
            'name': 'Feedbacks',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'kw_training_feedback',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('training_id', '=', self.ids[0])],
        }

    @api.multi
    def view_training_session(self):
        tree_view_id = self.env.ref('kw_training.kw_training_schedule_tree').id
        form_view_id = self.env.ref('kw_training.kw_training_schedule_form').id
        kanban_view_id = self.env.ref('kw_training.view_kw_training_schedule_kanban').id

        return {
            'model': 'ir.actions.act_window',
            'name': 'Sessions',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree,kanban',
            'res_model': 'kw_training_schedule',
            'views': [(kanban_view_id, 'kanban'), (tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('training_id', '=', self.ids[0])],
            'context': {'default_training_id': self.ids[0]}
        }

    @api.multi
    def view_training_material(self):
        tree_view_id = self.env.ref('kw_training.view_kw_training_material_tree').id
        form_view_id = self.env.ref('kw_training.view_kw_training_material_form').id
        kanban_view_id = self.env.ref('kw_training.view_kw_training_material_kanban').id
        return {
            'model': 'ir.actions.act_window',
            'name': 'Contents',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree,kanban',
            'res_model': 'kw_training_material',
            'views': [(tree_view_id, 'tree'), (kanban_view_id, 'kanban'),  (form_view_id, 'form')],
            'domain': [('training_id', '=', self.ids[0])],
            'context': {'default_training_id': self.ids[0]}
        }

    @api.multi
    def action_redirect_assessment(self):
        kanban_view_id = self.env.ref('kw_training.view_kw_training_assessment_readonly_kanban').id
        tree_view_id = self.env.ref('kw_training.view_kw_training_assessment_readonly_tree').id
        form_view_id = self.env.ref('kw_training.view_kw_training_assessment_readonly_form').id
        return {
            'model': 'ir.actions.act_window',
            'name': 'Assessments',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree,kanban',
            'res_model': 'kw_training_assessment',
            'views': [(kanban_view_id, 'kanban'), (tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('training_id', '=', self.ids[0])],
        }

    @api.multi
    def view_given_feedback(self):
        res = self.env['ir.actions.act_window'].for_xml_id('kw_training', 'action_kw_training_feedback_act_window')
        res['domain'] = [('training_id', '=', self.id), ('create_uid', '=', self._uid)]
        return res

    @api.multi
    def give_feedback(self):
        survey_id = self.env.ref('kw_training.kw_training_survey_feedback_form')
        emp_id = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)

        return {
            'type': 'ir.actions.act_url',
            'name': f'Training Feedback For {self.name}',
            'target': 'self',
            'url': f"/training-feedback/{slug(self)}/{slug(emp_id)}/{slug(survey_id)}"
        }
    
    @api.multi
    def view_training_plan(self):
        plan_create_edit_form_view_id = self.env.ref('kw_training.kw_training_plan_create_edit_form') # for new plan create and edit
        plan_readonly_form_view_id = self.env.ref('kw_training.kw_training_plan_view_only_form')
        plan_editonly_form_view_id = self.env.ref('kw_training.kw_training_plan_edit_only_form')
        plan_createonly_form_view_id = self.env.ref('kw_training.kw_training_plan_create_only_form')
        participant_ids = self.pip_training_id.employee_id.ids if self.pip_training_id.employee_id else []
        default_data = {
                        'default_hide_training': True,
                        'default_financial_year': self.financial_year.id,
                        'default_training_req_id': self.training_req_id.id,
                        'default_training_id': self.id,
                        'default_period_from': self.start_date,
                        'default_period_to': self.end_date,
                        'default_instructor_type': self.instructor_type,
                        'default_participant_ids': [(6, 0, participant_ids)]
                        }
        _action = {
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_training_plan',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'self'
                    }
        if self.plan_status == "Not Planned":
            _action['context'] = default_data
            _action['view_id'] = plan_create_edit_form_view_id.id
        else:
            rec = self.env['kw_training_plan'].with_context(active_test=False).search([('training_id', '=', self.id)],order="write_date desc",limit=1)
            if rec.state == 'approved':
                _action['view_id'] = plan_readonly_form_view_id.id

            elif rec.state == 'rejected':
                _action['context'] = default_data
                _action['view_id'] = plan_createonly_form_view_id.id

            else:  
                # for draft and applied state 
                _action['view_id'] = plan_editonly_form_view_id.id
                
            _action['res_id']= rec.id

        return _action

    @api.multi
    def view_my_training_session(self):
        if self.is_trainer:
            tree_view_id = self.env.ref('kw_training.kw_training_schedule_view_only_tree_trainer').id
            form_view_id = self.env.ref('kw_training.kw_training_schedule_view_only_form').id
            kanban_view_id = self.env.ref('kw_training.kw_training_schedule_view_only_kanban_trainer').id
            return {
                    'model': 'ir.actions.act_window',
                    'name': 'Sessions',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form,tree,kanban',
                    'res_model': 'kw_training_schedule',
                    'views': [(kanban_view_id, 'kanban'), (tree_view_id, 'tree'), (form_view_id, 'form')],
                    'domain': [('training_id', '=', self.ids[0])],
                }
        else:
            
            kanban_view_id = self.env.ref('kw_training.kw_training_schedule_view_only_kanban').id
            tree_view_id = self.env.ref('kw_training.kw_training_schedule_view_only_tree').id
            form_view_id = self.env.ref('kw_training.kw_training_schedule_view_only_form').id
            return {
                'model': 'ir.actions.act_window',
                'name': 'Sessions',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form,tree,kanban',
                'res_model': 'kw_training_schedule',
                'views': [(kanban_view_id, 'kanban'), (tree_view_id, 'tree'), (form_view_id, 'form')],
                'domain': [('training_id', '=', self.ids[0])],
            }

    @api.multi
    def view_my_training_material(self):
        kanban_view_id = self.env.ref('kw_training.view_only_kw_training_material_kanban').id
        tree_view_id = self.env.ref('kw_training.view_kw_training_material_view_only_tree').id
        form_view_id = self.env.ref('kw_training.view_kw_training_material_view_only_form').id
        return {
            'model': 'ir.actions.act_window',
            'name': 'Contents',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree,kanban',
            'res_model': 'kw_training_material',
            'views': [(tree_view_id, 'tree'), (kanban_view_id, 'kanban'), (form_view_id, 'form')],
            'domain': [('training_id', '=', self.ids[0])],
        }

    @api.constrains('start_date', 'end_date')
    def validate_training_date(self):
        if not self.financial_year:
            raise ValidationError("Please Choose Financial Year")
        if self.start_date and not self.financial_year.date_start <= self.start_date <= self.financial_year.date_stop:
            raise ValidationError(f'Start date should inside {self.financial_year.date_start} and {self.financial_year.date_stop}')
        if self.end_date and not self.financial_year.date_start <= self.end_date <= self.financial_year.date_stop:
            raise ValidationError(f'End date should inside {self.financial_year.date_start} and {self.financial_year.date_stop}')
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError('End date should not less than start date.')

    @api.constrains('name','financial_year')
    def check_duplicate(self):
        for training in self:
            existing_training = self.search(
                [('financial_year', '=', training.financial_year.id), ('name', '=ilike', training.name)]) - training
            if existing_training:
                raise ValidationError(f"Training title {training.name} is already exists for financial year {training.financial_year.name}.")

    def get_cc_emails(self):
        cc_employees = self.env['hr.employee']

        training_cc_group = self.env.ref('kw_training.group_kw_training_mail_cc')
        cc_employees |= training_cc_group.users.mapped('employee_ids')

        if self.plan_ids and self.plan_ids[-1].participant_ids:
            cc_employees |= self.plan_ids[-1].participant_ids.mapped('parent_id')

        if self.plan_ids and self.plan_ids[-1].internal_user_ids:
            cc_employees |= self.plan_ids[-1].internal_user_ids

        if cc_employees:
            return ','.join(cc_employees.mapped('work_email'))

    @api.onchange('course_type_id')
    def _set_course(self):
        if self._context.get('pip_training') and  self.course_id :
            return {'domain': {'course_type_id': [('id', '=', self.course_id.skill_type.id)]}}
        else:
            self.course_id = False
            return {'domain': {'course_id': [('skill_type.id', '=', self.course_type_id.id)]}}
    #     @api.onchange('course_type_id')
    # def _set_course(self):
    #     if not self._context.get('pip_training'):
    #         self.course_id = False
    #         return {'domain': {'course_id': [('skill_type.id', '=', self.course_type_id.id)]}}
    #     else:
    #         if self.course_id == False:
    #             return {'domain': {'course_type_id': [('id', '=', self.course_id.skill_type.id)],'course_id': [('skill_type.id', '=', self.course_type_id.id)]}}
    #         else:
    #             return {'domain': {'course_type_id': [('id', '=', self.course_id.skill_type.id)]}}
            
            

    @api.model
    def get_calendar(self):
        fiscal_years = self.env['account.fiscalyear'].search([], order="date_start asc")
        current_fiscal = self.env['account.fiscalyear'].search(
            ['&', ('date_start', '=', start_date), ('date_stop', '=', end_date)])
        current_fiscal_id = current_fiscal.id if current_fiscal else False
        years = []
        if len(fiscal_years) > 0:
            years = [(year.id, year.name) for year in fiscal_years]
        data = self.env['kw_training'].search(
            ['&', ('start_date', '>=', start_date), ('end_date', '<=', end_date)])
        d_list = {"current_fiscal_id": current_fiscal_id,
                  "fiscal_years": years,
                  "financial_year": f"{start_date.year}-{end_date.year}",
                  "1": [], "2": [], "3": [], "4": [], "5": [], "6": [],
                  "7": [], "8": [], "9": [], "10": [], "11": [], "12": []
                  }
        for d in data:
            d_list[str(d.start_date.month)].append({
                'id': d.id,
                'name': d.name,
                'from': d.start_date,
                'to': d.end_date,
                'instructor': d.instructor_type,
            })
        for key, value in d_list.items():
            if not value and isinstance(value, list):
                d_list[key].append(0)
        return d_list

    @api.model
    def get_calendar_by_financial_year(self,vals):
        financial_id = vals.get('financial_id',False)
        return_value = False
        try:
            financial_year_id = int(financial_id)
            financial_record = self.env['account.fiscalyear'].browse(financial_year_id)
            if financial_record:
                start_date, end_date = financial_record.date_start, financial_record.date_stop
                d_list = {
                          "1": [], "2": [], "3": [], "4": [], "5": [], "6": [],
                          "7": [], "8": [], "9": [], "10": [], "11": [], "12": []
                          }
                data = self.env['kw_training'].search(
                    ['&', ('start_date', '>=', start_date), ('end_date', '<=', end_date)])
                for d in data:
                    d_list[str(d.start_date.month)].append({
                        'id': d.id,
                        'name': d.name,
                        'from': d.start_date,
                        'to': d.end_date,
                        'instructor': d.instructor_type,
                    })
                return d_list
        except ValueError:
            return return_value

    @api.model
    def create(self, vals):
        result = super(Training, self).create(vals)
        self.env.user.notify_success("Training created successfully.")
        return result

    @api.multi
    def write(self, values):
        ''' Check if user is trying to change the instructor_type. 
            if plan is 'approved' or 'applied' for a proposal then the user
            can't change the instructor type.'''
        for record in self:
            if "instructor_type" in values:
                ''' Check any plan is in approved or applied state '''
                plan_rec = record.plan_ids.filtered(lambda r: r.state == 'apply' or r.state == 'approved') if record.plan_ids else False
                if plan_rec:
                    raise ValidationError(f"Plan is in {plan_rec.state.title()} state. You can't modify the instructor type.")
                
        result = super(Training, self).write(values)
        self.env.user.notify_success("Training(s) updated successfully.")
        return result

    @api.multi
    def view_trainers_feedback(self):
        self.ensure_one()
        participants = self.plan_ids[0].participant_ids
        trainers_feedback_form_view_id = self.env.ref("kw_training.kw_trainer_feedback_form").id
        _action = {
            'name': 'TrainersFeedback',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_training_trainer_feedback',
            'view_type': 'form',
            'views': [(trainers_feedback_form_view_id, 'form')],
            'view_id': trainers_feedback_form_view_id
        }
        existing_feedback = self.env['kw_training_trainer_feedback'].search([('training_id','=',self.id)],limit=1)
        if existing_feedback: # show the form view of existing record
            _action['res_id'] = existing_feedback.id
            _action['context'] = {'create':False,'delete':False}
            _action['flags'] = {'mode': 'edit'}
        else:
            # open a new form
            _action['flags'] = {'action_buttons': True, 'mode': 'edit'}
            _action['context'] = {
                'default_course_type_id': self.course_type_id.id,
                'default_financial_year': self.financial_year.id,
                'default_course_id': self.course_id.id,
                'default_training_id': self.id,
                'default_feedback_detail_ids': [[0, 0, {
                    'participant_id': participant.id,
                    'training_id': self.id,
                    'designation': participant.job_id.name,
                    'department': participant.department_id.name,
                    'financial_year': self.financial_year.id,
                    'course_type_id': self.course_type_id.id,
                    'course_id': self.course_id.id,
                }] for participant in participants]}

        return _action
    
    def training_module_access_scheduler(self):
        user_group = self.env.ref('kw_training.group_kw_training_employee')
        users = self.env['res.users'].sudo().search([])

        for user in users:
            if user not in user_group.users:
                user_group.sudo().write({'users': [(4, user.id)]})

   
    @api.multi
    def generate_certificate(self):
        self.ensure_one()
        generate_certificate_tree_view_id = self.env.ref("kw_training.view_training_generate_certificate_tree").id
        existing_certificate = self.env['kw_training_certificate_generate'].search([('training_id', '=', self.id)], limit=1)
        employee_ids = self.plan_ids and self.plan_ids[-1].participant_ids 
        score_percentage = 0.0
        new_certificates = [] 
        new_certificate = None 
        cr = self.env.cr
        if not existing_certificate and not self.assessment_ids:
            raise UserError("No certificates were generated because no Assessment is configured.")
            
        if not existing_certificate and self.assessment_ids:
            for assess in self.assessment_ids:
                for rec in employee_ids :
                    skill_answer = self.env['kw_skill_answer_master'].sudo().search(
                        [('emp_rel', '=', rec.id), ('set_config_id', '=', assess.assessment_id.id)])
                    query = """
                            SELECT 
                                ROUND((COUNT(DISTINCT ta.id) * 100.0 / COUNT(DISTINCT s.id)), 2) AS attended_percentage
                            FROM kw_training a
                            JOIN kw_training_attendance ta ON ta.training_id = a.id
                            JOIN kw_training_schedule s ON s.training_id = a.id
                            JOIN kw_training_attendance_details p ON ta.id = p.attendance_id AND p.attended = True
                            JOIN hr_employee h ON h.id = p.participant_id
                            LEFT JOIN hr_job j ON h.job_id = j.id
                            WHERE a.id = %s and p.participant_id = %s
                            GROUP BY a.id, p.participant_id
                        """
                    cr.execute(query, (self.id,rec.id))
                    result = cr.fetchone()
                    attendance_percentage = result[0] or 0.0
                    score_percentage = skill_answer.percentage_scored if skill_answer else 0.0
                    # attendance_percentage = self.env['kw_training_attendance_details'].sudo().search([('training_id','=',self.id),('participant_id','=',rec.id),('attendance_percentage','>=',60.00)],limit=1)
                    if score_percentage >= 60 and assess.test_type == 'post' and attendance_percentage >= 60.00: 
                        certificate_vals = {
                            'course_type_id': self.course_type_id.id,
                            'course_id': self.course_id.id,
                            'financial_year': self.financial_year.id,
                            'training_id': self.id,
                            'start_date': self.start_date,
                            'end_date': self.end_date,
                            'instructor_type': self.instructor_type,
                            'score_percentage': score_percentage,
                            'trainee_id': rec.id, 
                            'domain' : [('training_id', '=', self.id)]
                        }
                        new_certificate = self.env['kw_training_certificate_generate'].create(certificate_vals)
                        new_certificates.append(new_certificate)  
            return {
                'name': 'Generate Certificate',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_training_certificate_generate',
                'view_mode': 'tree',
                'view_id': generate_certificate_tree_view_id,
                'target': 'self',
                'res_id': new_certificate,
                'domain' : [('training_id', '=', self.id)]
            }
        # else:
        #     if existing_certificate.search([('training_id', '=', self.id)]):
        #         for assess in self.assessment_ids:
        #             for rec in employee_ids :
        #                 skill_answer = self.env['kw_skill_answer_master'].sudo().search(
        #                     [('emp_rel', '=', rec.id), ('set_config_id', '=', assess.assessment_id.id)])
        #                 score_percentage = skill_answer.percentage_scored if skill_answer else 0.0
        #                 if existing_certificate.search([('training_id', '=', self.id),('trainee_id','=',skill_answer.emp_rel.id)]) and skill_answer.percentage_scored >= 60.00 and assess.test_type == 'post':
        #                     pass
        #                 else:
        #                     if skill_answer.percentage_scored >= 60.00 and assess.test_type == 'post':
        #                         existing_certificate.create({'course_type_id': self.course_type_id.id,
        #                         'course_id': self.course_id.id,
        #                         'financial_year': self.financial_year.id,
        #                         'training_id': self.id,
        #                         'start_date': self.start_date,
        #                         'end_date': self.end_date,
        #                         'instructor_type': self.instructor_type,
        #                         'score_percentage': score_percentage,
        #                         'trainee_id': rec.id, 
        #                     })
                            
        #         return {
        #             'name': 'Generate Certificate',
        #             'type': 'ir.actions.act_window',
        #             'res_model': 'kw_training_certificate_generate',
        #             'view_mode': 'tree',
        #             'view_id': generate_certificate_tree_view_id,
        #             'target': 'self',
        #             'res_id': existing_certificate.id,
        #             'domain' : [('training_id', '=', self.id)]
        #         }
        else:
            return {
                'name': 'Generate Certificate',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_training_certificate_generate',
                'view_mode': 'tree',
                'view_id': generate_certificate_tree_view_id,
                'target': 'self',
                'res_id': existing_certificate.id,
                'domain' : [('training_id', '=', self.id)]
            }

    # @api.multi
    # def generate_certificate(self):
    #     self.ensure_one()
    #     generate_certificate_tree_view_id = self.env.ref("kw_training.view_training_generate_certificate_tree").id

    #     existing_certificate = self.env['kw_training_certificate_generate'].search([('training_id', '=', self.id)], limit=1)

    #     if existing_certificate:
    #         return {
    #             'name': 'Generate Certificate',
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'kw_training_certificate_generate',
    #             'view_mode': 'tree',
    #             'view_id': generate_certificate_tree_view_id,
    #             'target': 'self',
    #             'res_id': existing_certificate.id,
    #         }
    #     else:
    #         employee_ids = self.plan_ids and self.plan_ids[-1].participant_ids 
    #         new_certificates = [] 
            
    #         # Note: Dictionary to track the latest qualifying score for each trainee
    #         last_scores = {}

    #         for assess in self.assessment_ids:
    #             for rec in employee_ids:
    #                 skill_answer = self.env['kw_skill_answer_master'].sudo().search(
    #                     [('emp_rel', '=', rec.id), ('set_config_id', '=', assess.assessment_id.id)],
    #                     order='id desc',  # Order by ID to get the latest score
    #                     limit=1
    #                 )

    #                 score_percentage = skill_answer.percentage_scored if skill_answer else 0.0

    #                 print(f"Trainee ID: {rec.id}, Assessment ID====================: {assess.assessment_id.id}, Score: {score_percentage}")

    #                 if score_percentage >= 60:
    #                     if rec.id not in last_scores or skill_answer.id > last_scores[rec.id]['skill_answer_id']:
    #                         last_scores[rec.id] = {
    #                             'skill_answer_id': skill_answer.id,
    #                             'assessment_id': assess.assessment_id.id,
    #                             'score_percentage': score_percentage
    #                         }
    #                         print(f"Updating last score for Trainee ID===============: {rec.id} to {score_percentage}")

    #         for emp_id, score_data in last_scores.items():
    #             certificate_vals = {
    #                 'course_type_id': self.course_type_id.id,
    #                 'course_id': self.course_id.id,
    #                 'financial_year': self.financial_year.id,
    #                 'training_id': self.id,
    #                 'start_date': self.start_date,
    #                 'end_date': self.end_date,
    #                 'instructor_type': self.instructor_type,
    #                 'score_percentage': score_data['score_percentage'],
    #                 'trainee_id': emp_id,
    #             }
    #             new_certificate = self.env['kw_training_certificate_generate'].create(certificate_vals)
    #             new_certificates.append(new_certificate)

    #             print(f"Created certificate for Trainee ID=====================: {emp_id} with Score: {score_data['score_percentage']}")

    #         if not new_certificates:  
    #             raise UserError("No certificates were generated because no trainees scored 60 or above.")  

    #         return {
    #             'name': 'Generate Certificate',
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'kw_training_certificate_generate',
    #             'view_mode': 'tree',
    #             'view_id': generate_certificate_tree_view_id,
    #             'target': 'self',
    #             'res_id': new_certificate.id,
    #         }






        
        
       
                
               


            
        
