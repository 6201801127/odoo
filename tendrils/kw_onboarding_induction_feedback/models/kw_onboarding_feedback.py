# -*- coding: utf-8 -*-

from datetime import date
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class OnboardSurveyForm(models.Model):
    _name = 'onboard_survey_type_master'
    _description = 'onboard_survey_type_master'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string="Code", required=True)


class KwOnboardFeedback(models.Model):
    _name = 'kw_onboarding_feedback'
    _description = "Onboarding Induction & Feedback"
    _rec_name = 'emp_id'

    emp_id = fields.Many2one("hr.employee", store=True)
    deg_id = fields.Many2one('hr.job', string='Designation', related="emp_id.job_id", store=True)
    dept_id = fields.Many2one('hr.department', string='Department', related="emp_id.department_id", store=True)
    work_email = fields.Char(related="emp_id.work_email", string="Work Email", store=True)
    form_assign = fields.Many2many('onboard_survey_type_master', string="form")
    tagged_id = fields.Many2one('kw_onboard_induction_emp_tagged', string="Tagged")

    ##### Onboarding and Induction Feedback Form field #######
    onboarding_spoc = fields.Selection([('yes', 'Yes, I was welcomed immediately after I reached office.'),
                                        ('no', 'No, I was not welcomed properly'),
                                        ('other', 'I felt lost when I reached office')], )
    tour_completed = fields.Selection(
        [('yes', 'Yes, my organizational tour got completed immediately after I joined CSM'),
         ('no', 'No I was not toured on the first day of my joining.')], )
    all_assistance = fields.Selection([('yes', 'Yes'),
                                       ('no', 'No')], )
    onboarding_experience = fields.Selection([('yes', 'Fully Satisfied'),
                                              ('no', 'Not Satisfied'), ('other', 'Satisfied, but needs improvement')], )
    inductions_completed = fields.Selection([('yes', 'Yes'),
                                             ('no', 'No')], )
    inductions_completed_specify = fields.Text(string="Please specify which Induction is still pending")
    how_satisfied = fields.Selection([('yes', 'Satisfied'),
                                      ('no', 'Not Satisfied'), ('other', 'Partly Satisfied')], )
    hr_processes = fields.Selection([('yes', 'Yes'),
                                     ('no', 'No')], )
    with_workstation = fields.Selection([('yes', 'Yes'),
                                         ('no', 'No')], )
    reporting_authority = fields.Selection([('yes', 'Yes, I know whom to report for work assignments.'),
                                            ('no', 'No, I still don’t know whom to report.')], )
    use_kwantify = fields.Selection([('yes', 'Yes, am confident.'),
                                     ('no', 'No, I am still confused.')], )
    specify = fields.Text(string="Please specify")
    additional_comments = fields.Text()

    ##### boolean field check hr ,it, reviewer,onboard, company checking #######
    onboard_ind_bool = fields.Boolean()
    user_check_bool = fields.Boolean(compute='onboard_field_required')

    record_bool_onboard = fields.Boolean(compute="onboard_field_required")

    submit_bool = fields.Boolean()

    onboard_ind_officer_bool = fields.Boolean(compute="onboard_field_required")
    officer_manger = fields.Boolean(compute="onboard_field_required")
    manager_check_bool = fields.Boolean(compute="onboard_field_required")
    reviewer_employees = fields.Many2many('hr.employee')

    onboard_forward_to_manager = fields.Boolean(string="Forward")

    manager_confirm_form = fields.Boolean()
    status_feedback = fields.Selection(string='Status',
                                       selection=[('Configured', 'Configured'), ('Reasssign', 'Reassign'),
                                                  ('Completed', 'Completed'),
                                                  ('Inprogress', 'Inprogress'), ('Published', 'Published')])
    remark_reviewer = fields.Text(string="Remarks")

    @api.model
    def _get_employee_onboard_assessment_url(self, user_id):
        emp_assessment_url = f"/employee-view-feedback"
        return emp_assessment_url

    def onboard_field_required(self):
        if self.env.user.has_group('kw_onboarding_induction_feedback.group_kw_onboarding_induction_manager'):
            self.manager_check_bool = True
        if self.env.user.has_group('kw_onboarding_induction_feedback.group_kw_onboarding_induction_user'):
            self.user_check_bool = True
            self.remark_reviewer = False
        reviewer_emp = self.env['kw_onboarding_induction_configuration'].sudo().search([])
        for record in self:
            onboard_list = []
            for recc in reviewer_emp.admin_reviewer:
                onboard_list.append(recc.id)
                if self.env.user.employee_ids.id in onboard_list:
                    record.onboard_ind_officer_bool = True
        if self.env.user.has_group('kw_onboarding_induction_feedback.group_kw_onboarding_induction_manager') and self.onboard_ind_officer_bool == True:
            self.officer_manger = True

    @api.constrains('onboarding_spoc', 'tour_completed', 'all_assistance', 'onboarding_experience',
                    'inductions_completed',
                    'how_satisfied', 'hr_processes', 'with_workstation', 'reporting_authority', 'use_kwantify',
                    'additional_comments')
    def onchange_boolean_field(self):
        if self.onboard_ind_bool == True:
            if self.onboarding_spoc == False or self.tour_completed == False or self.all_assistance == False or \
                    self.onboarding_experience == False or self.inductions_completed == False or self.how_satisfied == False or self.hr_processes == False or \
                    self.with_workstation == False or self.reporting_authority == False or self.use_kwantify == False or not self.additional_comments:
                raise ValidationError(
                    'Please appear all the Induction Assessment & Feedback and submit the record for evalution.')

    def feedback_submit_button(self):
        submit_rec = []
        reviewer_emp = self.env['kw_onboarding_induction_configuration'].sudo().search([])
        template_obj = self.env.ref('kw_onboarding_induction_feedback.submit_emp_mail_to_manager')
        if self.onboard_ind_bool == True:
            submit_rec.append('onboard')
            if self.onboarding_spoc == False or self.tour_completed == False or self.all_assistance == False or \
                    self.onboarding_experience == False or self.inductions_completed == False or self.how_satisfied == False or self.hr_processes == False or \
                    self.with_workstation == False or self.reporting_authority == False or self.use_kwantify == False or not self.additional_comments:
                raise UserError(
                    'Please appear all the Induction Assessment & Feedback and submit the record for evalution.')

        if len(self.form_assign) != len(submit_rec):
            raise ValidationError("Please fill all the Onboarding feedback .")

        else:
            self.write({'status_feedback': 'Inprogress',
                        'submit_bool': True})
            record_log = self.env['feedback_assessment_feedback_log'].sudo().search([('emp_name', '=', self.emp_id.id)])
            for rec in record_log:
                rec.write({'status_feedback': 'Inprogress'})
            record_tagged = self.env['kw_onboard_induction_emp_tagged'].sudo().search([('id', '=', self.tagged_id.id)])
            record_tagged.write({'status_submit': 'inprogress'})

        reviewer_list = []
        if template_obj:
            if self.onboard_ind_bool == True:
                for rec in reviewer_emp.admin_reviewer:
                    reviewer_list.append(rec.work_email)
            users = self.env['res.users'].sudo().search([])
            manager = users.filtered(lambda user: user.has_group(
                'kw_onboarding_induction_feedback.group_kw_onboarding_induction_manager') == True)
            mail_to = ','.join(reviewer_list)
            cc_mail = ','.join(manager.mapped('email'))
            template_obj.with_context(email_to=mail_to,
                                      emp_name=self.emp_id.name,
                                      cc_mail=cc_mail,
                                      ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success('Thanks for completing this survey. We hope you settle in well.')

    #### score marking of all assessment feedback #########
    def feedback_reviewer_submit_button(self):
        if self._context.get('button') == 'onboard':
            record = self.env['kw_onboard_induction_emp_tagged'].sudo().search([('id', '=', self.tagged_id.id)])
            record.write({'status_submit': 'completed'})
            self.write({'status_feedback': 'Completed',
                            'onboard_forward_to_manager': True})
            record_log = self.env['feedback_assessment_feedback_log'].sudo().search([('emp_name', '=', self.emp_id.id)])
            for rec in record_log:
                rec.write({'status_feedback': 'Completed'})
            template_obj = self.env.ref("kw_onboarding_induction_feedback.submit_confirmed_mail_to_manager")
            mail_from = self.env.user.employee_ids.work_email
            users = self.env['res.users'].sudo().search([])
            manager = users.filtered(lambda user: user.has_group(
                'kw_onboarding_induction_feedback.group_kw_onboarding_induction_manager') == True)
            mail_to = ','.join(manager.mapped('email'))
            template_obj.with_context(mail_for='onboard confirm',
                                      cc_mail=mail_to,
                                      email_from=mail_from,
                                      name=self.emp_id.name,
                                      reviewer_name=self.env.user.employee_ids.name,
                                      email_to=self.emp_id.work_email,
                                      ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success('Mail sent successfully.')
      
    #### submit the manager all the assessment is confirmed and reviewed ######
    def feedback_manager_submit_button(self):
        submit_rec = []
        record = self.env['kw_onboard_induction_emp_tagged'].sudo().search([('id', '=', self.tagged_id.id)])
        if self.env.user.has_group('kw_onboarding_induction_feedback.group_kw_onboarding_induction_manager'):
            if self.onboard_forward_to_manager == True:
                submit_rec.append('True')
        if len(self.form_assign) == len(submit_rec):
            self.manager_confirm_form = True
            self.write({'status_feedback': 'Published'})
            record.write({'status_submit': 'completed'})

            record_log = self.env['feedback_assessment_feedback_log'].sudo().search([('emp_name', '=', self.emp_id.id)])
            for rec in record_log:
                rec.write({'status_feedback': 'Completed'})
            mail_template = self.env.ref("kw_onboarding_induction_feedback.submit_feedback_mail_to_employee")
            mail_template.with_context(mail_for='submit confirm',
                                       email_to=self.emp_id.work_email,
                                       mail_from=self.env.user.employee_ids.work_email,
                                       name=self.emp_id.name
                                       ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        else:
            raise ValidationError("Please confirm the onboarding feedback")
    def feedback_submit_manger_officer_check(self):
        submit_rec = []
        if self.officer_manger == True:
            submit_rec.append('True')
            record = self.env['kw_onboard_induction_emp_tagged'].sudo().search([('id', '=', self.tagged_id.id)])
            if len(self.form_assign) == len(submit_rec):
                self.manager_confirm_form = True
                self.write({'status_feedback': 'Published'})
                record.write({'status_submit': 'completed'})

                record_log = self.env['feedback_assessment_feedback_log'].sudo().search([('emp_name', '=', self.emp_id.id)])
                for rec in record_log:
                    rec.write({'status_feedback': 'Completed'})
                mail_template = self.env.ref("kw_onboarding_induction_feedback.submit_feedback_mail_to_employee")
                mail_template.with_context(mail_for='submit confirm',
                                        email_to=self.emp_id.work_email,
                                        mail_from=self.env.user.employee_ids.work_email,
                                        name=self.emp_id.name
                                        ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            else:
                raise ValidationError("Please confirm the onboarding feedback")
            
            


class OnboardInductionAnswer(models.Model):
    _name = "onboard_induction_answer_sheet"
    _description = "onboard_induction_answer_sheet"

    levels_hierarchy = fields.Char()
    many_departments = fields.Char()
    procurement_division = fields.Char()
    sbu_is = fields.Char()

    attendance_procedure = fields.Char()
    regular_shift = fields.Char()
    approves_leaves = fields.Char()
    is_en_cashable = fields.Char()
    consecutive_medical_leaves = fields.Char()
    maternity_leave = fields.Char()
    paternity_leave = fields.Char()
    special_leave = fields.Char()
    tour_settlement = fields.Char()
    fixed_holidays = fields.Char()
    amount_accidental = fields.Char()
    conducts_appraisals = fields.Char()
    minimum_effort = fields.Char()
    Salary_linked = fields.Char()
    dress_code = fields.Char()
    use_local_language = fields.Char()
    how_many_days = fields.Char()
    csm_firewall = fields.Char()
    iP_extension_phone = fields.Char()
    server_30 = fields.Char()
    server_9 = fields.Char()
    extension_number_it = fields.Char()
    established_yr = fields.Char()
    acronym_system = fields.Char()
    csm_values = fields.Char()
    crossed_onshore = fields.Char()
    landmark_project = fields.Char()
    e_Gov_Award = fields.Char()
    certified_for_cmmi = fields.Char()
    csm_hockey_world_cup = fields.Char()
    handling_the_recruitment = fields.Char()
    heads_the_hr = fields.Char()
    hold_quality = fields.Char()
    transformation_framework = fields.Char()
    score = fields.Integer(string="Score")


class kw_feedback_confirmed_wizard(models.TransientModel):
    _name = 'kw_feedback_induction_confirmed_wizard'
    _description = 'Confirmed Feedback wizard'

    emp_score_confirm = fields.Many2one('kw_onboarding_feedback')
    note = fields.Text(string="Note")

    def mail_confirmed_manager(self):
        context = dict(self._context)
        int_details = self.env["kw_onboarding_feedback"].browse(context.get("active_id"))
        if context['button_name'] == 'Onboard confirm':
            for rec in self.env['kw_onboarding_feedback'].sudo().search([('id', '=', int_details.id)]):
                template_obj = self.env.ref("kw_onboarding_induction_feedback.submit_confirmed_mail_to_manager")
                mail_from = self.env.user.employee_ids.work_email
                users = self.env['res.users'].sudo().search([])
                manager = users.filtered(lambda user: user.has_group(
                    'kw_onboarding_induction_feedback.group_kw_onboarding_induction_manager') == True)
                mail_to = ','.join(manager.mapped('email'))
                # print("self.emp_id.work_email--------------------", rec.emp_id.work_email, rec.emp_id.name, mail_to,
                #       mail_from)
                template_obj.with_context(email_to=mail_to,
                                          email_from=mail_from,
                                          emp_name=rec.emp_id.name,
                                          reviewer_name=self.env.user.employee_ids.name,
                                          cc_mail=rec.emp_id.work_email,
                                          ).send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")

    def get_employee_submit_form(self):
        pass

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}
