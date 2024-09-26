from datetime import date
from odoo import models, fields, api,tools
from odoo.exceptions import UserError, ValidationError


class AssessmentConfigWizard(models.TransientModel):
    _name = "induction_assessment_configuration_wizard"
    _description = "Induction Wizard"

    @api.model
    def default_get(self, fields):
        res = super(AssessmentConfigWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        res.update({
            'employee_ids': active_ids,
        })
        return res

    employee_ids = fields.Many2many('kw_employee_assessment_configuration','induction_config_emp_rel',column1='wizard_id',
        column2='induction_id',string='Employee Info',)
    induction_id = fields.Many2many('kw_skill_master', string="Induction", domain=[('skill_type', '=', 'Induction')])
    date_of_induction = fields.Date(string="Start Date")
    end_date_of_induction = fields.Date(string="End Date")
    induction_config_id = fields.Many2one('kw_employee_assessment_configuration',string="config id")
    emp_send_mail = fields.Boolean(string="send mail",required="True")
    emp_id = fields.Many2one('kw_employee_induction_assessment',string="Employee",default=lambda self: self._context.get('current_record'))
    
    
    
    @api.constrains('date_of_induction')
    def validate_induction_start_date(self):
        for induction in self:
            if induction.date_of_induction and date.today() > induction.date_of_induction:
                    raise ValidationError('You must configured induction from current date and after current date.')
    
    def update_induction_employee(self):
        self.emp_send_mail = True
        induction_emp = self.env['kw_employee_induction_assessment'].sudo().search([('emp_id','in',self.employee_ids.ids),('induction_id','in',self.induction_id.ids)])
        if induction_emp.exists():
            raise ValidationError("These employee induction configuration already configured")
        else:
            employee_id = []
            department_id = []
            if self.employee_ids:
                for recc in self.employee_ids:
                    employee_rec = self.env['hr.employee'].sudo().search([('onboarding_id','=',recc.onboard_id.id)])
                    if not employee_rec.exists():
                        raise ValidationError("Please create the Employee first then, You can configured the Induction Assessment")
                    else:
                        employee_id.append(employee_rec.id)
                        department_id.append(employee_rec.department_id.id)
                        user_group = self.env.ref('kw_onboarding_induction_feedback.group_kw_onboarding_induction_user')
                        skill_user_group = self.env.ref('kw_skill_assessment.group_kw_skill_assessment_user')
                        user = self.env['res.users'].sudo().search([('partner_id', '=', employee_rec.user_id.partner_id.id)])
                        if user:
                            groups_to_add = []
                            if user_group.id not in user.groups_id.ids:
                                groups_to_add.append((4, user_group.id))
                            if skill_user_group.id not in user.groups_id.ids:
                                groups_to_add.append((4, skill_user_group.id))

                            if groups_to_add:
                                user.write({
                                    'groups_id': groups_to_add
                                })  
                for rec in self.induction_id:
                    qus_set_config_record = self.env['kw_skill_question_set_config'].sudo().create({
                        'name': rec.name,
                        'dept': [(4, id, False) for id in department_id],
                        'skill_types': rec.skill_type.id,
                        'skill': rec.id,
                        'applicable_candidate': '3',
                        'frequency': "o",
                        'select_individual': [(4, id, False) for id in employee_id],
                        'assessment_type': 'Induction',
                        'duration': rec.assessment_duration,
                        'add_questions':[  (0, 0, {
                            'question_type': 1,
                            'no_of_question': rec.no_of_qus})],
                        'state': '2',
                        'active': True
                    })
                    for emp in self.employee_ids:
                        employee_rec = self.env['hr.employee'].sudo().search([('onboarding_id','=',emp.onboard_id.id)])
                        if employee_rec:
                            induction_emp.create({'emp_id':employee_rec.id,
                                            'induction_id':[(4, rec.id, False)],
                                            'start_date_of':self.date_of_induction,
                                            'assessment_id': qus_set_config_record.id,
                                            'end_date_of':self.end_date_of_induction})
            if self.emp_id:
                employee_id.append(self.emp_id.emp_id.id)
                department_id.append(self.emp_id.emp_id.department_id.id)
                for rec in self.induction_id:
                    qus_set_config_record = self.env['kw_skill_question_set_config'].sudo().create({
                        'name': rec.name,
                        'dept': [(4, id, False) for id in department_id],
                        'skill_types': rec.skill_type.id,
                        'skill': rec.id,
                        'applicable_candidate': '3',
                        'frequency': "o",
                        'select_individual': [(4, id, False) for id in employee_id],
                        'assessment_type': 'Induction',
                        'duration': rec.assessment_duration,
                        'add_questions':[  (0, 0, {
                            'question_type': 1,
                            'no_of_question': rec.no_of_qus})],
                        'state': '2',
                        'active': True
                    })
                    induction_emp.create({'emp_id':self.emp_id.emp_id.id,
                                    'induction_id':[(4, rec.id, False)],
                                    'start_date_of':self.date_of_induction,
                                    'assessment_id': qus_set_config_record.id,
                                    'end_date_of':self.end_date_of_induction})
                
            if self.emp_send_mail == True:
                if self.employee_ids:
                    for rec in self.employee_ids:
                        employee_rec = self.env['hr.employee'].sudo().search([('onboarding_id','=',rec.onboard_id.id)])
                        action_id = self.env.ref('kw_onboarding_induction_feedback.action_kw_induction_assessment_user_readonly_act_window').id
                        employee_name = rec.onboard_id.name
                        email_from=self.env.user.employee_ids.work_email
                        email_to = employee_rec.work_email
                        extra_params= {'email_to':email_to,'cc_mail':email_from,
                        'email_from':email_from,'record_id': induction_emp.id,
                        'emp_name':employee_name,'action_id':action_id,
                        }
                        self.env['hr.contract'].contact_send_custom_mail(res_id=self.id,
                                                                        notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                        template_layout='kw_onboarding_induction_feedback.kw_induction_assessment_email_template',
                                                                        ctx_params=extra_params,
                                                                        description="Induction Assessment")
                        self.env.user.notify_success("Mail Sent successfully.")
                else:
                    action_id = self.env.ref('kw_onboarding_induction_feedback.action_kw_induction_assessment_user_readonly_act_window').id
                    employee_name = self.emp_id.emp_id.name
                    email_from=self.env.user.employee_ids.work_email
                    email_to = self.emp_id.emp_id.work_email
                    
                    extra_params= {'email_to':email_to,'cc_mail':email_from,
                    'email_from':email_from,'record_id': induction_emp.id,
                    'emp_name':employee_name,'action_id':action_id,
                    }
                    self.env['hr.contract'].contact_send_custom_mail(res_id=self.id,
                                                                    notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                    template_layout='kw_onboarding_induction_feedback.kw_induction_assessment_email_template',
                                                                    ctx_params=extra_params,
                                                                    description="Induction Assessment")
                    self.env.user.notify_success("Mail Sent successfully.")
                    

class AssessmentrescheduleWizard(models.TransientModel):
    _name = "induction_assessment_wizard_resch"
    _description = "Induction Wizard"

    emp_induction_id = fields.Many2one('kw_employee_induction_assessment', string="Induction",default=lambda self: self._context.get('current_record'))
    start_date_of_induction = fields.Date(string="Start Date")
    end_date_of_induction = fields.Date(string="End Date")
    induction_assessment_id = fields.Many2one('kw_skill_master', string="Induction Assessment", compute='_compute_induction_assessment_id')
    
    
    @api.depends('emp_induction_id')
    def _compute_induction_assessment_id(self):
        for record in self:
            record.induction_assessment_id = record.emp_induction_id.induction_id.id

    
    
    @api.multi
    def confirm_for_induction_assessment(self):
        record = self.env['kw_employee_induction_assessment'].sudo()
        self.emp_induction_id.after_reschedule = True
        action_id = self.env.ref('kw_onboarding_induction_feedback.action_kw_induction_assessment_user_readonly_act_window').id
        
        employee_id = []
        department_id = []
        for recc in self.emp_induction_id.emp_id:
            employee_id.append(recc.id)
            department_id.append(recc.department_id.id)
        for rec in self.induction_assessment_id:
            qus_set_config_record = self.env['kw_skill_question_set_config'].sudo().create({
                'name': rec.name,
                'dept': [(4, id, False) for id in department_id],
                'skill_types': rec.skill_type.id,
                'skill': rec.id,
                'applicable_candidate': '3',
                'frequency': "o",
                'select_individual': [(4, id, False) for id in employee_id],
                'assessment_type': 'Induction',
                'duration': rec.assessment_duration,
                'add_questions':[  (0, 0, {
                    'question_type': 1,
                    'no_of_question': rec.no_of_qus})],
                'state': '2',
                'active': True
            })
            for emp in self.emp_induction_id.emp_id:   
                record.create({'emp_id':emp.id,
                                'induction_id':[(4, rec.id, False)],
                                'start_date_of':self.start_date_of_induction,
                                'assessment_id': qus_set_config_record.id,
                                'end_date_of':self.end_date_of_induction,
                                'percentage_scored':00.00,
                            })
                employee_name = emp.name
                email_from=self.env.user.employee_ids.work_email
                email_to = emp.work_email
                extra_params= {'email_to':email_to,'cc_mail':email_from,
                'email_from':email_from,'record_id': record.id,
                'emp_name':employee_name,'action_id':action_id,
                }
                self.env['hr.contract'].contact_send_custom_mail(res_id=self.id,
                                                                notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                template_layout='kw_onboarding_induction_feedback.kw_induction_assessment_email_template',
                                                                ctx_params=extra_params,
                                                                description="Induction Assessment")
                self.env.user.notify_success("Mail Sent successfully.")
                
                
class AssessmentfeedbackWizard(models.TransientModel):
    _name = "induction_assessment_feedback_wizard"
    _description = "Induction feedback Wizard"
    
    
    @api.model
    def _get_no_rating(self):
        return [(str(x), str(x)) for x in range(1, 6)]
    
    applicant_induction_id = fields.Many2one('kw_employee_induction_assessment', string="Induction",default=lambda self: self._context.get('current_record'))
    
    induction_rate = fields.Text(string=" How would you rate the induction overall?")
    induction_rate_no = fields.Selection('_get_no_rating',string="Induction rating")
    valuable_info = fields.Text(string=" Did it provide you with valuable information to help you do your job?")
    valuable_info_no = fields.Selection('_get_no_rating',string="valuable_info rating")
    understand_organisation = fields.Text(string="Did it help you understand more about the organisation?")
    understand_organisation_no = fields.Selection('_get_no_rating',string="understand_organisation rating")
    skill_of_inductor = fields.Text(string="How was the presentation skill of the Inductor?")
    skill_of_inductor_no = fields.Selection('_get_no_rating',string="skill_of_inductor rating")
    handel_queries = fields.Text(string="Did the Inductor handle your queries properly")
    handel_queries_no = fields.Selection('_get_no_rating',string="handel_queries rating")
    induction_coordinated = fields.Text(string="How would you rate the Indution coordinated for you?")
    induction_coordinated_no = fields.Selection('_get_no_rating',string="induction_coordinated rating")
    
    
    
    def confirm_for_induction_feedback(self):
        feedback_data = self.env['kw_employee_induction_assessment'].sudo().search(
                [('id', '=', self.env.context.get('current_record'))])
        # print(feedback_data,"feedback_data=================================")
        feedback_data.write({'induction_rate':self.induction_rate,
                             'induction_rate_no':self.induction_rate_no,
                             'valuable_info':self.valuable_info,
                             'valuable_info_no':self.valuable_info_no,
                             'understand_organisation':self.understand_organisation,
                             'understand_organisation_no':self.understand_organisation_no,
                             'skill_of_inductor':self.skill_of_inductor,
                             'skill_of_inductor_no':self.skill_of_inductor_no,
                             'handel_queries':self.handel_queries,
                             'handel_queries_no':self.handel_queries_no,
                             'induction_coordinated':self.induction_coordinated,
                             'induction_coordinated_no':self.induction_coordinated_no,
                             'feedback_hide_btn':True})
