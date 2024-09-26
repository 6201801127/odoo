from odoo import api, models,fields
from ast import literal_eval

# from odoo.exceptions import UserError,ValidationError
# from datetime import datetime,date

class send_mail(models.TransientModel):
    _name       ='send_mail'
    _description= 'Send Mail wizard'

    def _get_default_assessment_feedback(self):
        datas = self.env['kw_feedback_details'].browse(self.env.context.get('active_ids'))
        return datas

    feedback = fields.Many2many('kw_feedback_details', readonly=1, default=_get_default_assessment_feedback)
    mail_type = fields.Selection(string='Mail Type', selection=[('schedule', 'Schedule'), ('publish', 'Publish')])
    body = fields.Html('Mail Body', translate=True, sanitize=False)

    # @api.onchange('mail_type')
    # def _change_body_content(self):
    #     if self.mail_type == 'schedule':
    #         self.body = '' or False
    #     else:
    #         pass

    @api.multi
    def action_send_mail(self):
        self.ensure_one()

        if self.mail_type == 'schedule':
            for record in self.feedback:
                if record.assessment_tagging_id.assessment_type == 'periodic' and record.feedback_status in ['1']:
                    for config_record in record.feedback_final_config_id:
                        try:
                            template = self.env.ref('kw_assessment_feedback.kw_schedule_periodic_feedback_email_template')
                            if template:
                                template.send_mail(config_record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                        except Exception as e:
                            pass
                elif record.assessment_tagging_id.assessment_type == 'probationary' and record.feedback_status in ['1']:

                    try:
                        template = self.env.ref('kw_assessment_feedback.kw_schedule_probationary_feedback_email_template')
                        if template:
                            template.send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                    except Exception as e:
                        pass

        elif self.mail_type == 'publish':
            for record in self.feedback:
                if record.assessment_tagging_id.assessment_type == 'periodic' and self._context.get('value111') and record.feedback_status == '6':
                    try:
                        template = self.env.ref('kw_assessment_feedback.kw_publish_feedback_email_template')
                        if template:
                            template.send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
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
                                    template.send_mail(goal.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                            except Exception as e:
                                pass

                elif record.assessment_tagging_id.assessment_type == 'probationary' and self._context.get('value112') and record.feedback_status == '6':
                    # final and published
                    emp_cc_mail_list = []
                    final_list = ''
                    param = self.env['ir.config_parameter'].sudo()
                    mail_group = literal_eval(param.get_param('kw_assessment_feedback.assessment_ids') or '[]')
                    emp = self.env['hr.employee'].sudo().search([('id', 'in', mail_group)])
                    emp_cc_mail_list += emp.filtered(lambda r: r.work_email != False).mapped('work_email')
                    parent_mail = record.assessee_id.parent_id.work_email
                    emp_cc_mail_list += parent_mail.split(',')
                    if emp_cc_mail_list:
                        final_list = ','.join(set(emp_cc_mail_list))

                    if record.prob_status == 'extended':

                        if record.assessment_feedback_type == "internship":  # internship case
                            if record.is_machine_test_required:
                                if record.machine_test_result >= 60:
                                    template = self.env.ref('kw_assessment_feedback.kw_final_internship_extension_F2F_email_template')
                                    template.with_context(email_cc=final_list).send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                                else:
                                    template = self.env.ref('kw_assessment_feedback.kw_practical_test_extension_email_template')
                                    template.with_context(email_cc=final_list).send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                            else:
                                template = self.env.ref('kw_assessment_feedback.kw_final_internship_extension_F2F_email_template')
                                template.with_context(email_cc=final_list).send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                        
                        elif record.assessment_feedback_type == "probationary":  # probationary case
                            template = self.env.ref('kw_assessment_feedback.kw_probationary_extension_email_template')
                            template.with_context(email_cc=final_list).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")

                    if record.prob_status == 'completed':

                        if record.assessment_feedback_type == "internship":
                            template = self.env.ref('kw_assessment_feedback.kw_final_internship_completion_mail_email_template')
                            template.with_context(email_cc=final_list).send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                        
                        if record.assessment_feedback_type == "probationary":
                            template = self.env.ref('kw_assessment_feedback.kw_probationary_completion_email_template')
                            template.with_context(email_cc=final_list).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        
        self.env.user.notify_success("Mail Sent Successfully.")
        return {'type': 'ir.actions.act_window_close'}
