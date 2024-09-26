from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class KwRecommendTraining(models.Model):
    _name = 'kw_recommend_training'
    _rec_name = 'reference'
    _description = 'Recommended Training PIP'

    reference = fields.Char(string="Reference No")
    pip_id = fields.Many2one('performance_improvement_plan',string="PIP Data")
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    raised_by = fields.Many2one('hr.employee', 'Raised By')
    applied_date = fields.Date(string="Applied Date")
    
    performance_reason_training = fields.Many2many('pip_reason_issue_config', 'pip_reason_training_rel', 'pip_id', 'training_reason_id',
                                          string="Reason for Performance Issue",
                                          required=True)   
    designation_id = fields.Many2one('hr.job', string="Designation", related="employee_id.job_id")
    recommendation_reason = fields.Text(string='Reason for Recommendation')

    approved_by = fields.Many2one('hr.employee', string='Approved By')
    pending_at_txt = fields.Char(string="Pending At")

    status = fields.Selection([('Draft', 'Draft'), ('Applied', 'Applied'),
                               ('Recommend PIP', 'Recommend Counselling'),('Recommend Training', 'Training Recommended'), ('Closed', 'Closed')
                               ], string='Status', readonly=True)

    lnk_feedback_ids = fields.One2many('kw_lnk_feedback', 'recommend_training_id', string='L&K Feedback')
    # final_feedback = fields.Char(string='Final Feedback')
    final_feedback_remarks = fields.Text(string='Remarks')
    final_feedback_status = fields.Selection([('positive', 'Positive Feedback'), ('negative', 'Negative Feedback')], string='Status')
    is_sent_to_hr = fields.Boolean(string='Sent to HR', default=False,)
    target_date = fields.Date(string="Target Date")
    skill = fields.Many2one('kw_skill_master',string="Skill")
    training_completion_date = fields.Date(string="Training Complete Date")


    has_training_created = fields.Boolean(string="Training Created", compute="_compute_has_training_created")
    assessment_score = fields.Float(string="Assessment Score", compute="_compute_assessment_score")


    @api.depends('employee_id', 'pip_id')
    def _compute_assessment_score(self):
        for record in self:
            assessments = self.env['kw_pip_training_recommendation_report'].search([
            ('id', '=', record.id)])
            record.assessment_score = assessments.assessment_score

   
    def _compute_has_training_created(self):
        for record in self:
            training_exists = self.env['kw_training'].search([('pip_training_id', '=', record.pip_id.id)], limit=1)
            if training_exists:
                record.has_training_created = True
            else:
                record.has_training_created = False

    def view_training_pip(self):
        training_exists = self.env['kw_training'].search([('pip_training_id', '=', self.pip_id.id)], limit=1)
        form_view_id = self.env.ref('kw_training.view_kw_training_form').id
        return {
            'name': 'Training',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_training',
            'view_mode': 'form',
            'view_id': form_view_id,
            'res_id' : training_exists.id,
            'target': 'current',

        }




    @api.multi
    def action_send_to_hr(self):
        # print(not self.final_feedback_status,"===========",not self.final_feedback_remarks,"==========",self.training_completion_date)
        if not self.final_feedback_status or not self.final_feedback_remarks or not self.training_completion_date:
            raise ValidationError("Please gives the status,feedback and completion date")
        self.ensure_one()
        assessment_date = self.lnk_feedback_ids and self.lnk_feedback_ids[0].assessment_date or False
        hr_user = self.env.ref("performance_improvement_plan.group_pip_hr_user").users.mapped('employee_ids')
        template_obj = self.env.ref('performance_improvement_plan.recommend_training_hr_final_close_email_template')
        manager_emp_hr = self.env['hr.employee'].sudo().search([('id', 'in', hr_user.ids), ('active', '=', True)])

        hr_group_users = self.env.ref("performance_improvement_plan.group_pip_hr_user").users.mapped('employee_ids') 
        pip_notify_emp = self.env.ref("performance_improvement_plan.group_pip_officer").users.mapped('employee_ids')
        pip_notify_user = self.env['hr.employee'].sudo().search([('id','in', pip_notify_emp.ids),('active','=',True)])
        email_to = ','.join(hr_group_users.mapped('work_email'))

        #  existing record
        existing_record = self.env['kw_pip_counselling_details'].search([
            ('reference', '=', self.reference),
            ('assessee_id', '=', self.employee_id.id),
            ('assessment_date', '=', assessment_date)
        ], limit=1)

        if not existing_record:
            final_feedbacks = []
            assessor_ids = []
            pip_counselling_details = {}
            

            for feedback in self.lnk_feedback_ids:
                # final_feedback = {
                #     'final_assessor_id': feedback.employee_id.id,
                #     'assessor_final_remark': feedback.remarks,
                # }
                # final_feedbacks.append((0, 0, final_feedback))
                assessor_ids.append(feedback.employee_id.id)

            pip_counselling_details = {
                'reference': self.reference,
                'pip_ref_id' : self.pip_id.id,
                'assessee_id': self.employee_id.id,
                'assessment_date': assessment_date,
                'reason_for_counselling': self.recommendation_reason,
                'feedback_status': '7',  
                'meeting_log_id':[(5, 0, 0)],
                'training_final_feedback':self.final_feedback_status,
                'remarks_hr':self.final_feedback_remarks,
                'final_assessor_feedback': final_feedbacks,
                'assign_assessors_ids': [(6, 0, assessor_ids)],
                'training_create_bool' : True,
                'training_completion_expected_date':self.target_date,
                'training_completion_actual_date' : self.training_completion_date
            
            }
            self.env['kw_pip_counselling_details'].create(pip_counselling_details)
            

            self.pending_at_txt = 'HR'
            template_obj = self.env.ref('performance_improvement_plan.recommend_training_hr_final_close_email_template')

            hr_group_users = self.env.ref("performance_improvement_plan.group_pip_hr_user").users.mapped('employee_ids')  
            email_to = ','.join(hr_group_users.mapped('work_email'))
            mail_cc = []
            if self.pip_id.employee_id.parent_id and self.pip_id.employee_id.parent_id.work_email:   ##RA
                mail_cc.append(self.pip_id.employee_id.parent_id.work_email)
            if self.approved_by and self.approved_by.work_email:      ##Approver
                mail_cc.append(self.approved_by.work_email)
            if self.raised_by and self.raised_by.work_email:   ##raised by
                mail_cc.append(self.raised_by.work_email)
            cc_mail = ','.join(set(mail_cc)) or ''
            if template_obj:
                template_obj.with_context(
                    subject=f"PIP Process | {self.employee_id.display_name} | Training Completed ",
                    # mail_for='sbu_pip_close',
                    email_to=email_to,
                    email_cc=cc_mail,
                    email_from=self.env.user.employee_ids.work_email,
                    name=self.raised_by.name,
                    raised_user=self.employee_id.display_name,
                ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            self.is_sent_to_hr = True
            self.env.user.notify_success("Mail Sent Successfully.")

    @api.multi
    def take_action_for_lnk(self):
        self.ensure_one()
        return {
            'name': 'Training',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_training',
            'view_mode': 'form',
            'view_id': self.env.ref('kw_training.view_kw_training_form').id,
            'target': 'current',
            'context': {'pip_training':True,
                'default_training_req_id': self.approved_by.id,
                        'default_training_type': 'PIP',
                        'default_pip_training_id': self.pip_id.id,
                        'default_course_id': self.skill.id if self.skill else False,
                        'default_pip_ref': self.pip_id.reference

                        }
        }


        

class KwLnkFeedback(models.Model):
    _name = 'kw_lnk_feedback'
    _description = 'L&K Feedback'

    recommend_training_id = fields.Many2one('kw_recommend_training', string='Recommended Training', ondelete='cascade')
    assessment_date = fields.Date(string="Training Assessment Date",required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    status = fields.Selection([('positive', 'Positive Feedback'), ('negative', 'Negative Feedback')], string='Status', required=True)
    remarks = fields.Char(string='Remarks',required=True)
