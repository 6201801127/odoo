# -*- coding: utf-8 -*-
from odoo import models, fields, api
from werkzeug import urls
from odoo.addons.http_routing.models.ir_http import slug
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from kw_utility_tools import kw_validations


class Kw_Survey(models.Model):
    _inherit = "survey.survey"

    # #----------- Additional fields----------------
    # survey_type = fields.Many2one(string='Survey Type', comodel_name='kw_survey_type', )
    recruitment_survey_url = fields.Char("Recruitment Public link", compute="_compute_recruitment_survey_url")
    recruitment_print_url = fields.Char("Recruitment Print link", compute="_compute_recruitment_survey_url")

    @api.model
    def _compute_recruitment_survey_url(self):
        base_url = '/' if self.env.context.get('relative_url') else \
            self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for survey in self:
            survey.recruitment_survey_url = urls.url_join(base_url, "kw_recruitment/survey/start/%s" % (slug(survey)))
            survey.recruitment_print_url = urls.url_join(base_url, "kw_recruitment/survey/print/%s" % (slug(survey)))

    @api.multi
    def action_start_kw_recruitment_survey(self):
        self.ensure_one()
        token = self.env.context.get('survey_token')
        # applicant_id = self.env.context.get('applicant_id')
        # if token and not applicant_id:
        #     trail = f"/{token}"
        # elif token and applicant_id:
        #     trail = f"/{token}/{applicant_id}"
        # elif applicant_id:
        #     trail = f"/{applicant_id}"
        # else:
        #     trail =""
        trail = "/%s" % token if token else ""
        return {
            'type': 'ir.actions.act_url',
            # 'name': 'Take Test',
            'target': 'self',
            'url': self.with_context(relative_url=True).recruitment_survey_url + trail
        }

    @api.multi
    def action_print_recruitment_survey(self):
        """ Open the website page with the survey printable view """
        self.ensure_one()
        token = self.env.context.get('survey_token')
        trail = "/" + token if token else ""
        return {
            'type': 'ir.actions.act_url',
            'name': "View Feedback",
            'target': 'new',
            'url': self.with_context(relative_url=True).recruitment_print_url + trail
        }


class kw_survey_questions(models.Model):
    _inherit = 'survey.question'

    type = fields.Selection([
        ('free_text', 'Multiple Lines Text Box'),
        ('textbox', 'Single Line Text Box'),
        ('numerical_box', 'Numerical Value'),
        ('date', 'Date'),
        ('simple_choice', 'Multiple choice: only one answer'),
        ('multiple_choice', 'Multiple choice: multiple answers allowed'),
        ('matrix', 'Matrix')], string='Type of Question', default='simple_choice', required=True)


class kw_SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input_line'

    @api.model
    def save_line_simple_choice(self, user_input_id, question, post, answer_tag):
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'survey_id': question.survey_id.id,
            'skipped': False
        }
        old_uil = self.search([
            ('user_input_id', '=', user_input_id),
            ('survey_id', '=', question.survey_id.id),
            ('question_id', '=', question.id)
        ])
        old_uil.sudo().unlink()

        if answer_tag in post and post[answer_tag].strip():
            comment_answer = post.pop(("%s_%s" % (answer_tag, 'comment')), '').strip()
            vals.update({'answer_type': 'suggestion', 'value_suggested': post[answer_tag], 'value_text': comment_answer})
        else:
            vals.update({'answer_type': None, 'skipped': True})

        # '-1' indicates 'comment count as an answer' so do not need to record it
        if post.get(answer_tag) and post.get(answer_tag) != '-1':
            self.create(vals)

        comment_answer = post.pop(("%s_%s" % (answer_tag, 'comment')), '').strip()
        if comment_answer:
            vals.update({'answer_type': 'text', 'value_text': comment_answer, 'skipped': False, 'value_suggested': False})
            self.create(vals)

        return True
