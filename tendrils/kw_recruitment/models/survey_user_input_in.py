# -*- coding: utf-8 -*-
# import datetime
# import logging
# import re
# from collections import Counter, OrderedDict
# from itertools import product
# from werkzeug import urls
# from odoo import tools, SUPERUSER_ID, _
# from odoo.addons.http_routing.models.ir_http import slug

# email_validator = re.compile(r"[^@]+@[^@]+\.[^@]+")
# _logger = logging.getLogger(__name__)
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, date, datetime
from dateutil.relativedelta import relativedelta


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    applicant_id = fields.Many2one('hr.applicant', string="Applicant ID")
    meeting_id = fields.Many2one('calendar.event', string="Meeting ID")
    score = fields.Integer(compute='_compute_score_remark', help='Total score of the applicant.')
    remark = fields.Char(compute='_compute_score_remark', help='Remarks of the applicant.')
    current_user = fields.Boolean(compute='_get_current_user')
    applicant_name = fields.Char("Applicant Name", related="applicant_id.partner_name")
    walk_in_meeting_id = fields.Many2one('kw_recruitment_walk_in_meeting', string="Walk-in Meeting")
    recruitment_integration_id = fields.Many2one('kw_recruitment_documents', string="recruitment id")
    relevant_exp = fields.Char(compute='_compute_exp_remark', help='Experience of the applicant.')

    @api.multi
    def view_feedback(self, data=None):
        return self.survey_id.with_context(survey_token=self.token).action_print_recruitment_survey()
        # report = self.env['ir.actions.report']._get_report_from_name('kw_recruitment.kw_print_feedback_report')
        # return report.report_action(self, config=False)

    @api.multi
    def print_feedback(self, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('kw_recruitment.kw_print_feedback_report')
        return report.report_action(self, config=False)

    @api.multi
    def view_cv(self):
        wizard_form = self.env.ref('kw_recruitment_dms_integration.doc_one2many_list_view', False)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': wizard_form.id,
            'res_model': 'kw_recruitment_documents',
            'target': 'new',
            # 'res_id': self.applicant_id.document_ids.id,
            'domain': [('applicant_id', '=', self.applicant_id.id)],
            'create': False,
            'edit': False
        }

    @api.multi
    def give_feedback(self):
        # print("in recruitment------------",self.survey_id)
        u_id = self.env['res.users'].sudo().search([('partner_id','=',self.partner_id.id)])
        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",u_id)
        if self.env.user.id != u_id.id:
            raise UserError(_("You cannot submit feedback for other panel. This feedback belongs to %s and you are logged in as %s." % (u_id.name , self.env.user.name)))
        else:
            # print("self.survey_id>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.",self.survey_id)
            return self.survey_id.with_context(survey_token=self.token).action_start_kw_recruitment_survey()

    @api.multi
    def _compute_score_remark(self):
        for feedback in self:
            for input in feedback.user_input_line_ids:
                # if input.question_id.question == 'Remark':
                #     feedback.remark = input.value_free_text
                if input.question_id.question == 'Status':
                    feedback.remark = input.value_suggested.value
                if input.question_id.question == 'Grand Total':
                    feedback.score = input.value_number

    @api.multi
    def _compute_exp_remark(self):
        for feedback in self:
            for input in feedback.user_input_line_ids:
                if input.question_id.question == 'Relevant Experience':
                    feedback.relevant_exp = input.value_text

    @api.multi
    def _get_current_user(self):
        for record in self:
            if self.env.user.has_group('hr_recruitment.group_hr_recruitment_manager'):
                record.current_user = True
            else:
                if record.partner_id.id == self.env.user.partner_id.id:
                    record.current_user = True
                else:
                    record.current_user = False
    
    @api.model
    def check_pending_interview_feedback(self, user_id):
        interview_feedback_url = False
        current_employee = self.env['hr.employee'].search([('user_id', '=', user_id.id)], limit=1)
        if not current_employee:
            return f"/web/"
        else:
            interview_feedback_date = self.env['ir.config_parameter'].sudo().get_param('kw_recruitment.interview_feedback_date') or datetime.now()
            config_interview_date = datetime.strptime(str(interview_feedback_date), "%Y-%m-%d")
            domain = [('partner_id', '=', user_id.partner_id.id), ('state', '=', 'new'),
                      ('kw_meeting_id', '!=', False), ('kw_meeting_id.stop', '>', interview_feedback_date)]
            interview_feedback_record = self.env['survey.user_input'].sudo().search(domain, limit=1)
            # interview_time = self.env['kw_meeting_events'].sudo().search([('kw_start_meeting_date', '>=', feedback_date)], limit=1)
            # and interview_time
            if interview_feedback_record and interview_feedback_record.kw_meeting_id:
                meeting_end_time = interview_feedback_record.kw_meeting_id.stop
                end_time = datetime.strptime((meeting_end_time + relativedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                if config_interview_date < end_time < datetime.now():
                    interview_feedback_url = interview_feedback_record.survey_id.with_context(survey_token=interview_feedback_record.token).action_start_kw_recruitment_survey()
            else:
                interview_feedback_url = f"/web/"
        return interview_feedback_url if interview_feedback_url else f"/web/"
