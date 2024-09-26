# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.addons.http_routing.models.ir_http import slug
from werkzeug import urls

class kwSurveySurvey(models.Model):
    _inherit = "survey.survey"

    questions_layout = fields.Selection([
        ('one_page', 'One page with all the questions'),
        ('page_per_section', 'One page per section'),
        ('page_per_question', 'One page per question')],
        string="Layout", required=True, default='one_page')
    progression_mode = fields.Selection([
        ('percent', 'Percentage'),
        ('number', 'Number')], string='Progression Mode', default='percent',
        help="If Number is selected, it will display the number of questions answered on the total number of question to answer.")

    questions_selection = fields.Selection([
        ('all', 'All questions'),
        ('random', 'Randomized per section')],
        string="Selection", required=True, default='all',
        help="If randomized is selected, you can configure the number of random questions by section. This mode is ignored in live session.")

    # scoring
    scoring_type = fields.Selection([
        ('no_scoring', 'No scoring'),
        ('scoring_with_answers', 'Scoring with answers at the end'),
        ('scoring_without_answers', 'Scoring without answers at the end')],
        string="Scoring", required=True, default='no_scoring')
    scoring_success_min = fields.Float('Success %', default=80.0)
    # attendees context: attempts and time limitation
    is_attempts_limited = fields.Boolean('Limited number of attempts',
                                         help="Check this option if you want to limit the number of attempts per user",
                                         compute="_compute_is_attempts_limited", store=True, readonly=False)
    attempts_limit = fields.Integer('Number of attempts', default=1)

    is_time_limited = fields.Boolean('The survey is limited in time')
    time_limit = fields.Float("Time limit (minutes)", default=10)
    question_and_page_ids = fields.One2many('survey.question', 'survey_id', string='Sections and Questions', copy=True)
    # security / access
    access_mode = fields.Selection([
        ('public', 'Anyone with the link'),
        ('token', 'Invited people only')], string='Access Mode',
        default='public', required=True)
    # access_token = fields.Char('Access Token', default=lambda self: self._get_default_access_token(), copy=False)
    users_login_required = fields.Boolean('Login Required',
                                          help="If checked, users have to login before answering even with a valid token.")
    users_can_go_back = fields.Boolean('Users can go back', help="If checked, users can go back to previous pages.")
    enable_scoring_check = fields.Boolean('Enable Scoring',)
    public_url = fields.Char("Public link", compute="_compute_survey_url")

    def _compute_survey_url(self):
        """ Computes a public URL for the survey """
        base_url = '/' if self.env.context.get('relative_url') else \
                   self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for survey in self:
            survey.public_url = urls.url_join(base_url, "survey/start/%s" % (slug(survey)))
            survey.print_url = urls.url_join(base_url, "survey/print/%s" % (slug(survey)))
            survey.result_url = urls.url_join(base_url, "survey/results/%s" % (slug(survey)))
            survey.public_url_html = '<a href="%s">%s</a>' % (survey.public_url, _("Click here to start survey"))


    # users_can_signup = fields.Boolean('Users can signup', compute='_compute_users_can_signup')
    @api.depends('question_and_page_ids')
    def _compute_page_and_question_ids(self):
        for survey in self:
            survey.page_ids = survey.question_and_page_ids.filtered(lambda question: question.is_page)
            survey.question_ids = survey.question_and_page_ids - survey.page_ids

    @api.depends('question_and_page_ids.is_conditional', 'users_login_required', 'access_mode')
    def _compute_is_attempts_limited(self):
        for survey in self:
            if not survey.is_attempts_limited or \
                    (survey.access_mode == 'public' and not survey.users_login_required) or \
                    any(question.is_conditional for question in survey.question_and_page_ids):
                survey.is_attempts_limited = False

    # @api.depends('question_and_page_ids.is_conditional')
    # def _compute_has_conditional_questions(self):
    #     for survey in self:
    #         survey.has_conditional_questions = any(question.is_conditional for question in survey.question_and_page_ids)

    # ------------------------------------------------------------
    # CONDITIONAL QUESTIONS MANAGEMENT
    # ------------------------------------------------------------

    def _get_conditional_maps(self):
        triggering_answer_by_question = {}
        triggered_questions_by_answer = {}
        for question in self.question_ids:
            triggering_answer_by_question[question] = question.is_conditional and question.triggering_answer_id

            if question.is_conditional:
                if question.triggering_answer_id in triggered_questions_by_answer:
                    triggered_questions_by_answer[question.triggering_answer_id] |= question
                else:
                    triggered_questions_by_answer[question.triggering_answer_id] = question
        return triggering_answer_by_question, triggered_questions_by_answer

    @api.multi
    def action_test_survey(self):
        ''' Open the website page with the survey form into test mode'''
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': "Results of the Survey",
            'target': 'self',
            'url': self.with_context(relative_url=True).public_url + "/phantom"
        }

