# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError
import re


class ForwardWizardPIP(models.TransientModel):
    _name = "kw_pip_remark_wizard"
    _description = "PIP remark wizard"

    pip_id = fields.Many2one('performance_improvement_plan', string="Ref",
                             default=lambda self: self._context.get('current_record'))
    pip_details_id = fields.Many2one('kw_pip_counselling_details', string="Ref",
                                     default=lambda self: self._context.get('default_active_rec'))
    remark = fields.Text('Remarks')
    keep_observation = fields.Selection(string="To Keep under observation", selection=[('Yes', 'Yes'), ('No', 'No')])
    observation_remarks = fields.Text(string="Describe The Reason")
    observation_duration = fields.Selection(string="Observation Duration",
                                            selection=[('7', '7 Days'), ('15', '15 Days'), ('30', '30 Days'),
                                                       ('45', '45 Days'), ('60', '60 Days')], )
    release_duration = fields.Integer(string="Notice period to release(days)")
    deliverable_rec = fields.Text(string="Deliverables")
    excepted_achivement_rec = fields.Text(string="Expected Outcome")
    timeline_improvement = fields.Selection(string="Timeline for Performance Improvement Plan",
                                            selection=[('7', '7 Days'), ('15', '15 Days'), ('30', '30 Days'),
                                                       ('45', '45 Days'), ('60', '60 Days')], )
    improvement_data = fields.Text(string="Final Feedback")
    assessee_id = fields.Many2one('hr.employee', string='Assessee',related="pip_id.employee_id")
    assessor_id = fields.Many2many('hr.employee',string='Assessor', domain="[('id','!=',assessee_id)]")
    counselling_date = fields.Date(string='Counselling Date')
    feedback_ids = fields.One2many('kw_accessor_feedback_wizard', 'feedback_wizard_id', string="Final Feedback",)
    documents = fields.Binary(string=u'Document', attachment=True)
    file_name = fields.Char(string='Document Name')
    assessor_final_outcome=fields.Selection(string="Final Outcome",selection=[('Meet Expectations', 'Meet Expectations'), ('Doesn’t meet expectation', 'Doesn’t meet expectation')])
    assessor_final_remark= fields.Text(string="Final remark")
    cc_mails = fields.Many2many('hr.employee','pip_emp_id','emp_id',string="Email cc")

    # required_feedback = fields.Boolean(compute="_compute_required_feedback", store=True)

    # @api.depends('keep_observation')
    # def _compute_required_feedback(self):
    #     for record in self:
    #         record.required_feedback = record.keep_observation == 'Yes'

    @api.multi
    def pip_approve_btn(self):
        pip_data = self.env['performance_improvement_plan'].sudo().search([('id', '=', self.pip_id.id)])
        pip_feedback_data = self.env['kw_pip_counselling_details'].sudo().search([('id', '=', self.pip_details_id.id)])
        template_obj = self.env.ref('performance_improvement_plan.email_template_for_approve_pip')
        pip_notify_emp = self.env.ref("performance_improvement_plan.group_pip_officer").users.mapped('employee_ids')
        pip_notify_user = self.env['hr.employee'].sudo().search([('id','in', pip_notify_emp.ids),('active','=',True)])
        hr_user = self.env.ref("performance_improvement_plan.group_pip_hr_user").users.mapped('employee_ids')

        l_and_k_users = self.env.ref("performance_improvement_plan.group_pip_l_and_k").users.mapped('employee_ids')  
        
        manager_emp_hr = self.env['hr.employee'].sudo().search([('id', 'in', hr_user.ids), ('active', '=', True)])
        if pip_data and self._context.get('button') == 'approve':
            # if pip_data.suggestion_reviewer_sbu == False and self.pip_id.suggestion_reviewer  == False:
            #     raise ValidationError("Please give your remark.")
            #    or self.pip_id.suggestion_reviewer == 'RP'
            if pip_data.suggestion_reviewer_sbu == 'RP':
                self.pip_id.write({'status': 'Recommend PIP',
                                   'approved_user_id': self.env.user.employee_ids.id,
                                   'date_of_action': date.today()})
                email_to = self.pip_id.employee_id.work_email
                mail_cc = []
                if self.env.user.employee_ids.work_email:   ##approver
                    mail_cc.append(self.env.user.employee_ids.work_email)
                if self.pip_id.raised_by.work_email:      ##raised by
                    mail_cc.append(self.pip_id.raised_by.work_email)

                if self.pip_id.employee_id.parent_id and self.pip_id.employee_id.parent_id.work_email:     ##RA
                    mail_cc.append(self.pip_id.employee_id.parent_id.work_email)

                if self.pip_id.employee_id.department_id.manager_id.work_email:        ##HOD
                    mail_cc.append(self.pip_id.employee_id.department_id.manager_id.work_email)
                if pip_notify_user:                 ##notify(CHRO,RCM)
                    mail_cc.extend(pip_notify_user.mapped('work_email'))
                if manager_emp_hr:      ## PMS
                    mail_cc.extend(manager_emp_hr.mapped('work_email'))

                if self.pip_id.raised_by and self.pip_id.raised_by.work_email:
                    mail_cc.append(self.pip_id.raised_by.work_email)
                cc_mail = ','.join(set(mail_cc)) or ''

                if template_obj:
                    template_obj.with_context(
                        subject=f"PIP process | {self.pip_id.employee_id.display_name} | Counselling Recommended",
                        mail_for='SBU_Approved',
                        email_to=email_to,
                        mail_cc=cc_mail,
                        name=self.pip_id.employee_id.name
                    ).send_mail(self.pip_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success("Mail Sent Successfully.")
            else:
                if pip_data.suggestion_reviewer_sbu == 'RT':
                    self.pip_id.write({'status': 'Recommend Training',
                                       'approved_user_id': self.env.user.employee_ids.id,
                                       'date_of_action': date.today()})
                    # Create the kw_recommend_training record
                    performance_reason_ids = [(6, 0, self.pip_id.performance_reason.ids)]
                    self.env['kw_recommend_training'].create({
                        'pip_id':self.pip_id.id,
                        'employee_id': self.pip_id.employee_id.id,
                        'recommendation_date': date.today(),
                        'recommendation_reason': self.pip_id.remarks_pm or '',
                        'approved_by': self.env.user.employee_ids.id,
                        'performance_reason_training': performance_reason_ids,
                        'designation_id': self.pip_id.designation_id.id,
                        'reference': self.pip_id.reference,
                        'raised_by': self.pip_id.raised_by.id,
                        'applied_date': self.pip_id.applied_date,
                        'pending_at_txt': self.pip_id.pending_at_txt,
                        'status': 'Recommend Training',
                        'target_date':self.pip_id.target_date,
                        'skill':self.pip_id.add_skill.id
                    })
                    # email_to = ','.join(l_and_k_users.mapped('work_email'))
                    email_to = self.pip_id.employee_id.work_email
                    mail_cc = []
                    if self.pip_id.raised_by.work_email:      ##raised by
                        mail_cc.append(self.pip_id.raised_by.work_email)
                    if self.pip_id.employee_id.parent_id and self.pip_id.employee_id.parent_id.work_email:    ##RA
                        mail_cc.append(self.pip_id.employee_id.parent_id.work_email)
                    if self.pip_id.employee_id.department_id.manager_id.work_email:   ##HOD
                        mail_cc.append(self.pip_id.employee_id.department_id.manager_id.work_email)
                    if pip_notify_user:      ##notify(CHRO,RCM)
                        mail_cc.extend(pip_notify_user.mapped('work_email'))
                    if manager_emp_hr:
                        mail_cc.extend(manager_emp_hr.mapped('work_email'))     ##pms
                    if l_and_k_users:
                        mail_cc.extend(l_and_k_users.mapped('work_email'))    ## Lk
                    mail_cc.extend(self.env.user.employee_ids.mapped('work_email'))   ## Approver
                    cc_mail = ','.join(set(mail_cc)) or ''
                    if template_obj:
                        template_obj.with_context(
                            subject=f"PIP Process | {self.pip_id.employee_id.display_name} | Training Recommended ",
                            mail_for='sbu_pip_close',
                            email_to=email_to,
                            email_from='tendrils@csm.tech',
                            mail_cc=cc_mail,
                            name = self.pip_id.employee_id.name,
                            raised_user=self.pip_id.employee_id.display_name
                        ).send_mail(self.pip_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                    self.env.user.notify_success("Mail Sent Successfully.")
                action_id = self.env.ref('performance_improvement_plan.performance_improvement_plan_take_action').id
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web#action={action_id}&model=performance_improvement_plan&view_type=list',
                    'target': 'self',
                }
        elif pip_data and self._context.get('button') == 'hod_approve':
            if pip_data.suggestion_reviewer == 'RP':
                self.pip_id.write({'status': 'Recommend PIP',
                                   'approved_user_id': self.env.user.employee_ids.id,
                                   'date_of_action': date.today()})
                email_to = self.pip_id.employee_id.work_email
                mail_cc = []
                if self.env.user.employee_ids.work_email:       ##approver
                    mail_cc.append(self.env.user.employee_ids.work_email)
                if self.pip_id.raised_by.work_email:          ##raised by
                    mail_cc.append(self.pip_id.raised_by.work_email)

                if self.pip_id.employee_id.parent_id and self.pip_id.employee_id.parent_id.work_email:    ##RA
                    mail_cc.append(self.pip_id.employee_id.parent_id.work_email)

                if self.pip_id.employee_id.department_id.manager_id.work_email:     ###HOD
                    mail_cc.append(self.pip_id.employee_id.department_id.manager_id.work_email)
                if pip_notify_user:                                 ##notify(CHRO,RCM)
                    mail_cc.extend(pip_notify_user.mapped('work_email'))
                if manager_emp_hr:        ##PMS
                    mail_cc.extend(manager_emp_hr.mapped('work_email'))

                cc_mail = ','.join(set(mail_cc)) or ''
                if template_obj:
                    template_obj.with_context(
                        subject=f"PIP process | {self.pip_id.employee_id.display_name} | Counselling Recommended",
                        mail_for='SBU_Approved',
                        email_to=email_to,
                        mail_cc=cc_mail,
                        # email_from=self.env.user.employee_ids.work_email,
                        name=self.pip_id.employee_id.name
                    ).send_mail(self.pip_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success("Mail Sent Successfully.")
            else:
                if pip_data.suggestion_reviewer == 'RT':
                    self.pip_id.write({'status': 'Recommend Training',
                                       'approved_user_id': self.env.user.employee_ids.id,
                                       'date_of_action': date.today()})
                    performance_reason_ids = [(6, 0, self.pip_id.performance_reason.ids)]
                    self.env['kw_recommend_training'].create({
                        'pip_id':self.pip_id.id,
                        'employee_id': self.pip_id.employee_id.id,
                        'recommendation_date': date.today(),
                        'recommendation_reason': self.pip_id.remarks_pm or '',
                        'approved_by': self.env.user.employee_ids.id,
                        'performance_reason_training': performance_reason_ids,
                        'designation_id': self.pip_id.designation_id.id,
                        'reference': self.pip_id.reference,
                        'raised_by': self.pip_id.raised_by.id,
                        'applied_date': self.pip_id.applied_date,
                        'pending_at_txt': self.pip_id.pending_at_txt,
                        'status': 'Recommend Training',
                        'target_date':self.pip_id.target_date,
                        'skill':self.pip_id.add_skill.id
                    })
                    # email_to = ','.join(l_and_k_users.mapped('work_email'))
                    email_to = self.pip_id.employee_id.work_email
                   
                    mail_cc = []
                    if self.pip_id.employee_id.parent_id and self.pip_id.employee_id.parent_id.work_email:    ##RA
                        mail_cc.append(self.pip_id.employee_id.parent_id.work_email)
                    if self.pip_id.employee_id.department_id.manager_id.work_email:     ##HOD
                        mail_cc.append(self.pip_id.employee_id.department_id.manager_id.work_email)
                    if pip_notify_user:      ## notify(CHRO,RCM)
                        mail_cc.extend(pip_notify_user.mapped('work_email'))
                    if manager_emp_hr:     ##PMS
                        mail_cc.extend(manager_emp_hr.mapped('work_email'))
                    if self.env.user.employee_ids.work_email:       ##approver
                        mail_cc.append(self.env.user.employee_ids.work_email)
                    if self.pip_id.raised_by.work_email:          ##raised by
                        mail_cc.append(self.pip_id.raised_by.work_email)
                    mail_cc.extend(l_and_k_users.mapped('work_email'))    ## Lk
                    cc_mail = ','.join(set(mail_cc)) or ''

                    if template_obj:
                        template_obj.with_context(
                            subject=f"PIP Process | {self.pip_id.employee_id.display_name} | Training Recommended ",
                            mail_for='sbu_pip_close',
                            email_to=email_to,
                            email_from="tendrils@csm.tech",
                            mail_cc=cc_mail,
                            name = self.pip_id.raised_by.name,
                            raised_user=self.pip_id.employee_id.display_name
                        ).send_mail(self.pip_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                    self.env.user.notify_success("Mail Sent Successfully.")
                action_id = self.env.ref('performance_improvement_plan.performance_improvement_plan_take_action').id
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web#action={action_id}&model=performance_improvement_plan&view_type=list',
                    'target': 'self',
                }
           
           
        elif pip_feedback_data and self._context.get('button') == 'Assessors':
            if self.keep_observation is False:
                raise ValidationError("Please Check 'To Keep Under Observation' Yes/No. ")
            if pip_feedback_data.meeting_time and self.keep_observation == 'Yes':
                template_obj = self.env.ref('performance_improvement_plan.mail_notify_counselling')

                email_to = self.pip_details_id.assessee_id.work_email or ''

                # email_to = ','.join(manager_emp_hr.mapped('work_email')) or ''
                cc_mail = []
                if self.pip_details_id.sudo().pip_ref_id.raised_by.work_email:   ## raised by
                    cc_mail.append(self.pip_details_id.sudo().pip_ref_id.raised_by.work_email)

                if self.pip_details_id.sudo().pip_ref_id.employee_id.parent_id and self.pip_id.employee_id.parent_id.work_email:   ##RA
                    cc_mail.append(self.pip_details_id.sudo().pip_ref_id.employee_id.parent_id.work_email)

                if self.pip_details_id.sudo().pip_ref_id.employee_id.department_id.manager_id.work_email:    ##HOD
                    cc_mail.append(self.pip_details_id.sudo().pip_ref_id.employee_id.department_id.manager_id.work_email)

                if self.pip_details_id.assign_assessors_ids:     ## Assessors
                    cc_mail.extend(self.pip_details_id.assign_assessors_ids.mapped('work_email'))
                if manager_emp_hr:     ##PMS
                    cc_mail.extend(manager_emp_hr.mapped('work_email'))
                if self.pip_details_id.sudo().pip_ref_id.approved_user_id and self.pip_details_id.sudo().pip_ref_id.approved_user_id.work_email :   ##Approver
                    cc_mail.append(self.pip_details_id.sudo().pip_ref_id.approved_user_id.work_email )
                mail_cc = ','.join(set(cc_mail)) or ''
                if template_obj:
                    template_obj.with_context(
                        subject=f"PIP Process | {self.pip_details_id.assessee_id.display_name} | Deliverables Assigned ",
                        mail_for='First_feedback',
                        email_to=email_to,
                        mail_cc=mail_cc,
                        observation_period = self.observation_duration,
                        name = self.pip_details_id.assessee_id.name,
                        email_from='tendrils@csm.tech',
                    ).send_mail(self.pip_details_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                self.env.user.notify_success("Mail Sent Successfully.")

                # start_time_str = pip_feedback_data.meeting_time
                # start_time = datetime.strptime(start_time_str, '%H:%M:%S')
                # meeting_duration = float(pip_feedback_data.meeting_duration)
                # hours = int(meeting_duration)
                # minutes = int((meeting_duration - hours) * 60)
                # duration = timedelta(hours=hours, minutes=minutes)
                # end_time = start_time + duration
                # current_datetime = datetime.now() + timedelta(hours=5, minutes=30)
                # print("current_datetime=======================",current_datetime.time(),end_time.time(), pip_feedback_data.assessment_date,date.today())
                # if current_datetime.time() > end_time.time() and pip_feedback_data.assessment_date < date.today():
                    
                self.pip_details_id.write(
                    {'in_observe': True,'hr_assessor_details_ids': [[0, 0, {'assessor_id': self.env.user.employee_ids.id,
                                                         'assessee_id': self.pip_details_id.assessee_id.id,
                                                         'keep_observation': self.keep_observation,
                                                         'observation_duration': self.observation_duration if self.keep_observation == 'Yes' else 0,
                                                         'improve_remark': self.observation_remarks,
                                                         'pip_assessor_counselling_id': self.pip_details_id.id,
                                                         'assessor_status': '1',
                                                         }]]})
                for rec in self.feedback_ids:
                    self.pip_details_id.write( {'hr_feedback_details_ids': [[0, 0, {'deliverable_rec': rec.deliverable_rec,
                                                        'excepted_achivement_rec': rec.excepted_achivement_rec,
                                                        'pip_counselling_id':self.pip_details_id.id}]]})
            else:
               self.pip_details_id.write(
                    {'feedback_status': '2',
                    'hide_hr_feedback': True,
                    'hr_assessor_details_ids': [[0, 0, {'assessor_id': self.env.user.employee_ids.id,
                                                         'assessee_id': self.pip_details_id.assessee_id.id,
                                                         'keep_observation': self.keep_observation,
                                                         'observation_duration': self.observation_duration if self.keep_observation == 'Yes' else 0,
                                                         'improve_remark': self.observation_remarks,
                                                         'pip_assessor_counselling_id': self.pip_details_id.id,
                                                         'assessor_status': '1',
                                                         }]]})
                
                # print("self.pip_details_id===========",self.pip_details_id.hr_assessor_details_ids)
                # else:
                #     raise ValidationError("Meeting is not yet concluded.")
        elif pip_feedback_data and self._context.get('button') == 'improve_Assessors':
                update_data = []
                final_feedback = []
                for rec in self.feedback_ids:
                    # print(rec.accessor_final_feedback,"===============feedback",rec.improvement_data,"=======remark====")
                    if rec.accessor_final_feedback == False and  rec.improvement_data == False:
                        raise ValidationError("Please Give the Remark and Feedback")
                    update_data.append([0, 0, {'assessor_id': self.env.user.employee_ids.id,
                                               'deliverable_rec': rec.deliverable_rec,
                                               'excepted_achivement_rec': rec.excepted_achivement_rec,
                                               'accessor_final_feedback': rec.accessor_final_feedback,
                                               'areas_improvement_data': rec.improvement_data,
                                               'pip_improve_counselling_id': self.pip_details_id.id,
                                               'assessor_status': '2'}])
                final_feedback.append([0,0,{'pip_final_assessor_feedback_id':self.pip_details_id.id,'final_assessor_id':self.env.user.employee_ids.id,'assessor_final_outcome':self.assessor_final_outcome,'assessor_final_remark':self.assessor_final_remark,}])
                pip_feedback_data.write({'hr_improvement_details_ids': update_data,'final_assessor_feedback':final_feedback})
                template_obj = self.env.ref('performance_improvement_plan.mail_notify_counselling')
                email_to = ','.join(manager_emp_hr.mapped('work_email')) or ''
                mail_cc = []
                if self.pip_id.employee_id.parent_id and self.pip_id.employee_id.parent_id.work_email:   ##RA
                    mail_cc.append(self.pip_id.employee_id.parent_id.work_email)
                if self.pip_id.employee_id.department_id.manager_id.work_email:            ##HOD
                    mail_cc.append(self.pip_id.employee_id.department_id.manager_id.work_email)
                if self.pip_id.raised_by.work_email:           ##raised by
                    mail_cc.append(self.pip_id.raised_by.work_email)
                if pip_notify_user:      ## notify(CHRO,RCM)
                    mail_cc.extend(pip_notify_user.mapped('work_email'))
                if self.pip_id.approved_user_id:      ## Approver
                    mail_cc.extend(self.pip_id.approved_user_id.mapped('work_email'))    
                if self.pip_details_id.assign_assessors_ids:     ## Assessors
                    mail_cc.extend(self.pip_details_id.assign_assessors_ids.mapped('work_email'))
                cc_mail = ','.join(set(mail_cc)) or ''
               
                if template_obj:
                    template_obj.with_context(
                        subject=f"PIP Process | {self.pip_details_id.assessee_id.display_name} | Final Feedback",
                        mail_for='Final_feedback',
                        mail_cc=cc_mail,
                        email_to=email_to,
                        email_from=self.env.user.employee_ids.work_email,
                    ).send_mail(self.pip_details_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                    # * len(pip_feedback_data.assign_assessors_ids)
                if (len(pip_feedback_data.hr_feedback_details_ids)  == len(pip_feedback_data.hr_improvement_details_ids)
                        and pip_feedback_data.feedback_status == '4'):
                    pip_feedback_data.write({'feedback_status': '5'})

                self.env.user.notify_success("Mail Sent Successfully.")
        elif pip_feedback_data and self._context.get('button') == 'add_deliverables':
            add_deliverables = []
            if self.feedback_ids:
                for rec in self.feedback_ids:
                    add_deliverables.append([0, 0, {'deliverable_rec': rec.deliverable_rec,
                                               'excepted_achivement_rec': rec.excepted_achivement_rec,}])
                update_deliver = [(5, 0, 0)]
                update_deliver.extend(add_deliverables)

                pip_feedback_data.write({'hr_feedback_details_ids': update_deliver,'user_agree_observation':'','feedback_status':'3'})
                template_obj = self.env.ref('performance_improvement_plan.mail_notify_counselling')
                mail_cc = []
                mail_to = pip_feedback_data.assessee_id.work_email
                if pip_feedback_data.assessee_id.parent_id and pip_feedback_data.assessee_id.parent_id.work_email:
                    mail_cc.append(pip_feedback_data.assessee_id.parent_id.work_email)
                if pip_feedback_data.raised_by.work_email:
                    mail_cc.append(pip_feedback_data.raised_by.work_email)
                if pip_feedback_data.assessee_id.department_id.manager_id.work_email:
                    mail_cc.append(pip_feedback_data.assessee_id.department_id.manager_id.work_email)
                hr_user = self.env.ref("performance_improvement_plan.group_pip_hr_user").users.mapped('employee_ids')
                pip_notify_emp = self.env.ref("performance_improvement_plan.group_pip_officer").users.mapped('employee_ids')
                hr_notify_emp = []
                hr_notify_emp.extend(pip_notify_emp.ids)
                hr_notify_emp.extend(hr_user.ids)
                manager_emp_hr = self.env['hr.employee'].sudo().search([('id','in', hr_notify_emp),('active','=',True)])
                cc_mail = ','.join(set(mail_cc)) + ',' + ','.join(manager_emp_hr.mapped('work_email'))
                if template_obj:
                    template_obj.with_context(
                        subject=f"PIP Process | {pip_feedback_data.assessee_id.display_name} | Your Deliverables ",
                        mail_for='revies_deliverables',
                        email_to=mail_to,
                        mail_cc=cc_mail,
                        email_from=self.env.user.employee_ids.work_email,
                        period_observ=pip_feedback_data.timeline_improvement,
                        name=pip_feedback_data.assessee_id.name
                    ).send_mail(pip_feedback_data.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        elif pip_feedback_data and self._context.get('button') == 'closed_pip':
            pip_rec = self.env['performance_improvement_plan'].search(
                [('employee_id', '=', pip_feedback_data.assessee_id.id),('status', 'in', ['Recommend PIP','Recommend Training']),('id','=',pip_feedback_data.pip_ref_id.id)])
            if pip_feedback_data.feedback_status in ['5','7']:
                template_obj = self.env.ref('performance_improvement_plan.mail_notify_counselling')
                if pip_feedback_data.final_decision and pip_feedback_data.final_decision == 'Meet Expectations':
                    mail_cc = []
                    mail_to = pip_feedback_data.assessee_id.work_email
                    if pip_feedback_data.assessee_id.parent_id and pip_feedback_data.assessee_id.parent_id.work_email:
                        mail_cc.append(pip_feedback_data.assessee_id.parent_id.work_email)
                    if pip_feedback_data.raised_by.work_email:
                        mail_cc.append(pip_feedback_data.raised_by.work_email)
                    if pip_feedback_data.assessee_id.department_id.manager_id.work_email:
                        mail_cc.append(pip_feedback_data.assessee_id.department_id.manager_id.work_email)
                    hr_user = self.env.ref("performance_improvement_plan.group_pip_hr_user").users.mapped('employee_ids')
                    pip_notify_emp = self.env.ref("performance_improvement_plan.group_pip_officer").users.mapped('employee_ids')
                    hr_notify_emp = []
                    hr_notify_emp.extend(pip_notify_emp.ids)
                    hr_notify_emp.extend(hr_user.ids)
                    mail_cc.extend(self.cc_mails.mapped('work_email')) if self.cc_mails else ''
                    manager_emp_hr = self.env['hr.employee'].sudo().search([('id','in', hr_notify_emp),('active','=',True)]).mapped('work_email')
                    mail_cc.extend(manager_emp_hr)
                    cc_mail = ','.join(set(mail_cc))
                    
                    if template_obj:
                        template_obj.with_context(
                            subject=f"PIP Process | {pip_feedback_data.assessee_id.display_name} | Final Feedback ",
                            mail_for='final_hr',
                            email_to=mail_to,
                            mail_cc=cc_mail,
                            email_from=self.env.user.employee_ids.work_email, 
                            name=pip_feedback_data.assessee_id.name
                        ).send_mail(pip_feedback_data.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                elif pip_feedback_data.final_decision and pip_feedback_data.final_decision == 'Doesn’t meet expectation':
                    mail_cc = []
                    mail_to = pip_feedback_data.assessee_id.work_email
                    if pip_feedback_data.assessee_id.parent_id and pip_feedback_data.assessee_id.parent_id.work_email:
                        mail_cc.append(pip_feedback_data.assessee_id.parent_id.work_email)
                    if pip_feedback_data.raised_by.work_email:
                        mail_cc.append(pip_feedback_data.raised_by.work_email)
                    if pip_feedback_data.assessee_id.department_id.manager_id.work_email:
                        mail_cc.append(pip_feedback_data.assessee_id.department_id.manager_id.work_email)
                    hr_user = self.env.ref("performance_improvement_plan.group_pip_hr_user").users.mapped('employee_ids')
                    pip_notify_emp = self.env.ref("performance_improvement_plan.group_pip_officer").users.mapped('employee_ids')
                    hr_notify_emp = []
                    hr_notify_emp.extend(pip_notify_emp.ids)
                    hr_notify_emp.extend(hr_user.ids)
                    manager_emp_hr = self.env['hr.employee'].sudo().search(
                        [('id', 'in', hr_notify_emp), ('active', '=', True)])
                    mail_cc.extend(self.cc_mails.mapped('work_email'))
                    cc_mail = ','.join(set(mail_cc)) + ',' + ','.join(manager_emp_hr.mapped('work_email'))
                    if template_obj:
                        template_obj.with_context(
                            subject=f"PIP Process | {pip_feedback_data.assessee_id.display_name} | Final Feedback ",
                            mail_for='final_hr_release',
                            email_to=mail_to,
                            mail_cc=cc_mail,
                            email_from=self.env.user.employee_ids.work_email,
                            name=pip_feedback_data.assessee_id.name
                        ).send_mail(pip_feedback_data.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                else:
                    raise ValidationError("Warning! Give the final decision.")
            pip_feedback_data.write({'feedback_status': '6',
                      'pip_close_date': date.today(),
                      })
            if pip_rec:
                pip_rec.write({'status':'Closed'})
                self.env['kw_recommend_training'].sudo().search([('pip_id','=',pip_rec.id)]).write({'status':'Closed'})
            
            
                
    def pip_closed_btn(self):
        if self.remark:
            pip_rec = self.env['performance_improvement_plan'].search(
                    [('id', '=', self.pip_details_id.pip_ref_id.id), ('status', '=', 'Recommend PIP')])
            self.pip_details_id.write({'feedback_status': '6',
                                    'closed_remarks_hr':self.remark,
                                    'documents':self.documents,
                                    'file_name':self.file_name,
                                    'pip_close_date': date.today(),})
            if pip_rec:
                pip_rec.write({'status':'Closed'})
        else:
            raise ValidationError("Please give the Remark.")
        


class FeedbackWizardAssessor(models.TransientModel):
    _name = "kw_accessor_feedback_wizard"
    _description = "Feedback wizard o2m"

    feedback_wizard_id = fields.Many2one('kw_pip_remark_wizard')
    pip_assessor_counselling_id = fields.Integer('pip_assessor_counselling_id')
    deliverable_rec = fields.Text(string="Deliverables")
    excepted_achivement_rec = fields.Text(string="Outcome")
    accessor_final_feedback = fields.Selection(string="Feedback",
                                               selection=[('Meet Expectations', 'Meet Expectations'),
                                                          ('Doesn’t meet expectation', 'Doesn’t meet expectation'),('Not Applicable','Not Applicable')])
    improvement_data = fields.Text(string="Remark")
    
    required_feedback = fields.Boolean(compute="_compute_required_feedback", store=True)

    @api.depends('feedback_wizard_id')
    def _compute_required_feedback(self):
        for record in self:
            record.required_feedback = record.feedback_wizard_id.keep_observation == 'Yes'
