from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
from odoo import exceptions, _
from ast import literal_eval


class kw_feedback_publish_wizard(models.TransientModel):
    _name = 'kw_feedback_publish_wizard'
    _description = 'Publish Feedback wizard'

    def _get_default_assessment_feedback(self):
        result = self.env['kw_feedback_details'].browse(self.env.context.get('active_ids'))
        return result

    feedback = fields.Many2many('kw_feedback_details', readonly=1, default=_get_default_assessment_feedback)
    body = fields.Html('Mail Body', translate=True, sanitize=False)
    cc_users = fields.Many2many('hr.employee', string='Email CC')

    @api.multi
    def publish_feedback(self):
        for record in self.feedback:
            if record.feedback_status in ['3', '4', '5']:
                record.feedback_status = '6'
                if not record.goal_id:
                    record._get_goal_details()
                else:
                    pass

                if record.goal_id:
                    record.goal_id.state = '4'
                else:
                    pass

                if record.feedback_status == '6':
                    record.feedback_final_config_id.sudo().write({'feedback_status': '4', })

                if record.assessment_tagging_id.assessment_type == 'probationary':

                    if record.weightage_id and record.weightage_id.value == 'B' and record.prob_status not in  ['extended','failed_prob']:
                        raise ValidationError(f"Final Assessment status must be extended as the performance grade of {record.assessee_id.name} is '{record.weightage_id.value}'.")

                    if record.prob_status:
                        if record.prob_status == 'extended' and record.extend_date and record.next_assessment_date:
                            self._get_manage_probationary(record)  # # create and manage in period model

                        elif record.prob_status == 'failed_prob':
                            data_failed = {'on_probation': False}
                            record.assessee_id.sudo().write(data_failed)
                        elif record.prob_status == 'completed':
                            data = {'on_probation': False, 'date_of_completed_probation': record.effective_from_date}

                            if record.job_id and record.assessment_feedback_type == 'internship':
                                data['job_id'] = record.job_id.id

                            # write designation ,on probation , probation complete date
                            record.assessee_id.sudo().write(data)
                    else:
                        raise ValidationError(f"Please update the final assessment status for {record.assessee_id.name}.")

                if record.feedback_status == '6' and record.assessment_tagging_id.assessment_type == 'periodic' and self._context.get('value11'):
                    try:
                        template = self.env.ref('kw_assessment_feedback.kw_publish_feedback_email_template')
                        if template:
                            template.send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                    except Exception as e:
                        pass

                    if record.assessment_tagging_id.is_goal == True:
                        period_date = record.period_id.period_date
                        n_year = period_date.year
                        n_month = period_date.month + 1
                        if n_month > 12:
                            n_month = n_month - 12
                            n_year = n_year + 1

                        goal_milestone = self.env['kw_feedback_goal_and_milestone'].sudo().search(
                            [('emp_id', '=', record.assessee_id.id), ('year', '=', str(n_year)),
                             ('months', '=', str(n_month))])
                        for goal in goal_milestone:
                            try:
                                template = self.env.ref('kw_assessment_feedback.kw_goal_milestone_email_template')
                                if template:
                                    template.send_mail(goal.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                            except Exception as e:
                                pass

                elif record.feedback_status == '6' and record.assessment_tagging_id.assessment_type == 'probationary' \
                        and self._context.get('value12'):
                    cc_emails = ""
                    if self.cc_users and self.cc_users.filtered('work_email'):
                        cc_emails += ','.join(self.cc_users.mapped('work_email'))

                    if record.assessee_id.parent_id and record.assessee_id.parent_id.work_email:
                        cc_emails += cc_emails and f",{record.assessee_id.parent_id.work_email}" or record.assessee_id.parent_id.work_email
                    emp_cc_mail_list = []
                    hod_mail_list=[]
                    param = self.env['ir.config_parameter'].sudo()
                    mail_group = literal_eval(param.get_param('kw_assessment_feedback.assessment_ids') or '[]')
                    emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group),('active','=',True)])
                    emp_cc_mail_list += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
                    emp_cc_mail_list += cc_emails.split(',')
                    cc_emails = ','.join(set(emp_cc_mail_list))
                    hod_mail = record.assessee_id.department_id.manager_id
                    hod_mail_list += hod_mail.filtered(lambda r: r.work_email != False).mapped('work_email')
                    hod_mail_list += cc_emails.split(',')
                    cc_emails = ','.join(set(hod_mail_list))
                    if record.prob_status == 'extended':
                        if record.assessment_feedback_type == "internship":  # internship case
                            if record.is_machine_test_required:
                                if record.machine_test_result >= 60:
                                    template = self.env.ref('kw_assessment_feedback.kw_final_internship_extension_F2F_email_template')
                                    template.with_context(email_cc=cc_emails).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")

                                else:
                                    template = self.env.ref('kw_assessment_feedback.kw_practical_test_extension_email_template')
                                    template.with_context(email_cc=cc_emails).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                            else:
                                template = self.env.ref('kw_assessment_feedback.kw_final_internship_extension_F2F_email_template')
                                template.with_context(email_cc=cc_emails).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")

                        elif record.assessment_feedback_type == "probationary":  # probationary case
                            template = self.env.ref('kw_assessment_feedback.kw_probationary_extension_email_template')
                            template.with_context(email_cc=cc_emails).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                        
                        elif record.assessment_feedback_type == "traineeship":  # probationary case
                            template = self.env.ref('kw_assessment_feedback.kw_probationary_traineeship_extension_email_template')
                            template.with_context(email_cc=cc_emails).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                            
                    if record.prob_status == 'failed_prob':
                        if record.assessment_feedback_type == "probationary":
                            template = self.env.ref('kw_assessment_feedback.kw_probationary_failed_email_template')
                            template.with_context(email_cc=cc_emails).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")

                    if record.prob_status == 'completed':
                        if record.assessment_feedback_type == "internship":
                            template = self.env.ref('kw_assessment_feedback.kw_final_internship_completion_mail_email_template')
                            template.with_context(email_cc=cc_emails).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")

                        if record.assessment_feedback_type == "probationary":
                            template = self.env.ref('kw_assessment_feedback.kw_probationary_completion_email_template')
                            template.with_context(email_cc=cc_emails).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")

                        if record.assessment_feedback_type == "traineeship":
                            template = self.env.ref('kw_assessment_feedback.kw_traineeship_completion_email_template')
                            template.with_context(email_cc=cc_emails).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        self.env.user.notify_success("Assessment Published Successfully.")
        return {'type': 'ir.actions.act_window_close'}

    def _get_manage_probationary(self, record):
        model_period = self.env['kw_feedback_assessment_period'].sudo()

        month_name = calendar.month_name[record.next_assessment_date.month]
        full_name = str(month_name + "-" + str(record.next_assessment_date.year))

        model_period.create({
            'name': full_name,
            'period_date': record.next_assessment_date if record.next_assessment_date else date.today(),
            'assessees': [(6, 0, record.assessee_id.ids)],
            'assessors': [(6, 0, record.assessor_id.ids)],
            'survey_id': record.survey_id.id,
            'assessment_date': record.next_assessment_date if record.next_assessment_date else date.today(),
            'prob_assessment_tag_id': record.assessment_tagging_id.id if record.assessment_tagging_id else False
        })

        record.assessee_id.sudo().write({'on_probation': True, 'date_of_completed_probation': record.extend_date})
        return

    def _get_email_cc(self, record):
        values = ','.join(str(user.work_email) for user in self.cc_users if user.id != record.assessee_id.parent_id.id)
        return values
