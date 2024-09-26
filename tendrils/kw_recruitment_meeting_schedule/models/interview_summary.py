# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime


class InterviewSummary(models.Model):
    _name = "kw_interview_summary_report"
    _description = "Interview Feedback"

    applicant_id = fields.Many2one('hr.applicant',string='Applicant')
    meeting_id = fields.Many2one('kw_meeting_events',string='Meeting')
    feedback_sent = fields.Selection(string='Feedback Sent', selection=[('pending', 'Pending'), ('done', 'Done')], default='pending')
    feedback_received = fields.Selection(string='Feedback Received', selection=[('pending', 'Pending'), ('received', 'Received')], default='pending')
    selection_status = fields.Selection(string='Selection Status', selection=[('pending', 'Pending'), ('reject', 'Reject'),('shortlist','Shortlisted')], default='pending')
    interview_status = fields.Selection(string='Interview Status', selection=[('pending', 'Pending'), ('done', 'Done')], default='pending')
    token = fields.Char('Survey Token')
    score = fields.Char(compute='_compute_score_remark',string='Score')
    panel_member = fields.Char('Panel')
    panel_remark = fields.Char(compute='_compute_score_remark',string='Status')
    interview_date = fields.Date('Interview Date')
    survey_id = fields.Many2one('survey.survey', string="Interview Feedback Form")
    userinput_id = fields.Many2one('survey.user_input', string="Survey User Input")
    mode_of_interview = fields.Selection(string='Mode Of Interview',
                                         selection=[
                                             ('face2face', 'Face to Face'),
                                             ('telephonic', 'Telephonic'),
                                             ('teamviewer', 'Team Viewer'),
                                             ('practical','Practical Test'),
                                             ('videoconf', 'Video Conference')])
    survey_sent = fields.Boolean(default=False)

    @api.multi
    def _compute_score_remark(self):
        for feedback in self:
            status = ''
            score = ''
            # if feedback.meeting_id.mapped('response_ids').filtered(lambda r: r.applicant_id == self.applicant_id):
            for input in feedback.meeting_id.mapped('response_ids').filtered(lambda r: r.applicant_id == feedback.applicant_id):
                for line in input.user_input_line_ids:
                    if line.question_id.question == 'Status':
                        if status == '':
                            status = line.value_suggested.value
                        else:
                            status += ' | '+ line.value_suggested.value
                    if line.question_id.question == 'Grand Total':
                        if score == '':
                            score = str(line.value_number)
                        else:
                            score += ' | '+ str(line.value_number)
            feedback.panel_remark = status
            feedback.score = score

    def marked_interview(self):
        return self.write({'interview_status': 'done'})

    def send_survey(self):
        """ Send Survey in mail"""
        for rec in self.meeting_id.applicant_ids:
            if self.mode_of_interview == 'face2face':
                survey_id = self.env['survey.survey'].sudo().search([('title','=','Interview Summary Candidate Feedback Form')])
            else:
                survey_id = self.env['survey.survey'].sudo().search([('title','=','Interview Summary Candidate Feedback Form Tel-Video')])

            user_input = self.env['survey.user_input'].sudo().create({
                'survey_id': survey_id.id,
                'type': 'link',
                'applicant_id': rec.id
            })
            self.write({'survey_id':survey_id.id, 'userinput_id':user_input.id,'survey_sent':True})

        db_name = self._cr.dbname
        candidate_template_id = self.env.ref('kw_recruitment_meeting_schedule.candidate_survey_feedback_template_f2f')
        survey_url= f"{survey_id.applicant_feedback_survey_url}/{user_input.token}"
        candidate_template_id.with_context(token=self.token,
                                           dbname=db_name,
                                           applicant_name=self.applicant_id.partner_name,
                                           applicant_email=self.applicant_id.email_from,
                                           survey=self.survey_id,
                                           survey_url = survey_url
                                           ).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Survey sent successfully.")
        return self.write({'selection_status': 'shortlist'})

    def reject(self):
        return self.write({'selection_status': 'reject'})

    @api.multi
    def view_survey(self):
        """ Open the website page with the survey printable view """

        trail = "/" + self.userinput_id.token if self.userinput_id else ""
        return {
            'type': 'ir.actions.act_url',
            'name': "View Feedback",
            'target': 'self',
            'url': self.userinput_id.survey_id.with_context(relative_url=True).applicant_feedback_print_url + trail
        }