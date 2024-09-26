from odoo import models, fields, api


class ApplicantFeedbackReport(models.Model):
    _name = 'kw_recruitment_appicant_feedback_report'
    _description = 'Applicant Feedback Report'

    meeting_id = fields.Many2one('kw_meeting_events', string='Meeting')
    applicant_id = fields.Many2one('hr.applicant', string='Name')
    position_id = fields.Many2one('hr.job', string='Position', related='applicant_id.job_id')
    interview_date = fields.Date(string='Interview Date')
    panel_ids = fields.Many2many('hr.employee', string='Panel Members')
    score = fields.Integer('Score')
    remark = fields.Char('Remarks')
