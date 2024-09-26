from odoo import models, fields, api
from odoo.addons.http_routing.models.ir_http import slug
from werkzeug import urls
from odoo.http import request


class kw_survey(models.Model):
    _inherit = "survey.survey"

    users_can_go_back = fields.Boolean('Users can go back', help="If checked, users can go back to previous pages.",
                                       default=True)
    appraisal_survey_url = fields.Char("Appraisal Public link", compute="_compute_appraisal_survey_url")
    appraisal_survey_result_url = fields.Char("Result Public link", compute="_compute_appraisal_survey_url")
    appraisal_survey_score_url = fields.Char("Score Public link", compute="_compute_appraisal_survey_url")

    def _compute_appraisal_survey_url(self):
        base_url = '/' if self.env.context.get('relative_url') else \
            self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for survey in self:
            survey.appraisal_survey_url = urls.url_join(base_url, "kw/survey/start/%s" % (slug(survey)))
            survey.appraisal_survey_result_url = urls.url_join(base_url, "kw/survey/results/%s" % (slug(survey)))
            survey.appraisal_survey_score_url = urls.url_join(base_url, "kw/survey/score/%s" % (slug(survey)))

    @api.multi
    def action_test_kw_survey(self):
        self.ensure_one()
        token = self.env.context.get('survey_token')
        self_employee_id = self.env.context.get('employee_id')
        request.session['empl_id'] = self_employee_id
        trail = "/%s" % token if token else ""
        return {
            'type': 'ir.actions.act_url',
            'name': 'Take Test',
            'target': 'self',
            'url': self.with_context(relative_url=True).appraisal_survey_url + trail
        }

    @api.multi
    def action_kw_survey_result(self):
        self.ensure_one()
        self_employee_id = self.env.context.get('employee_id')
        request.session['empl_id'] = self_employee_id
        token = self.env.context.get('survey_token')
        trail = "/" + token if token else ""
        return {
            'type': 'ir.actions.act_url',
            'name': "view Survey",
            'target': 'self',
            'url': self.with_context(relative_url=True).appraisal_survey_result_url + trail
        }

    @api.multi
    def get_survey_url(self):
        self.ensure_one()
        self_employee_id = self.env.context.get('employee_id')
        request.session['empl_id'] = self_employee_id
        token = self.env.context.get('survey_token')
        trail = "/" + token if token else ""
        url = self.with_context(relative_url=True).appraisal_survey_result_url + trail
        return url

    @api.multi
    def action_kw_survey_score(self):
        self.ensure_one()
        self_employee_id = self.env.context.get('employee_id')
        token = self.env.context.get('survey_token')
        trail = "/" + token if token else ""
        return {
            'type': 'ir.actions.act_url',
            'name': "view Survey",
            'target': 'self',
            'url': self.with_context(relative_url=True).appraisal_survey_score_url + trail
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

    indicator = fields.Text()

    @api.onchange('type')
    def change_indicator(self):
        if self.type not in  ['numerical_box','simple_choice']:
            self.indicator = ''

    @api.multi
    def validate_simple_choice(self, post, answer_tag):
        self.ensure_one()
        errors = {}
        comment = answer_tag + '_comment'
        if self.comments_allowed:
            comment_tag = "%s_%s" % (answer_tag, 'comment')
        if self.constr_mandatory and answer_tag not in post:
            errors.update({answer_tag: self.constr_error_msg})
        if self.constr_mandatory and answer_tag in post and not post[answer_tag].strip():
            errors.update({answer_tag: self.constr_error_msg})
        if self.constr_mandatory and answer_tag in post and post[
            answer_tag] == "-1" and self.comment_count_as_answer and comment_tag in post and not post[
            comment_tag].strip():
            errors.update({answer_tag: self.constr_error_msg})
        if comment in post and not post[comment].strip():
            errors.update({comment: self.constr_error_msg})
        return errors

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
            vals.update(
                {'answer_type': 'suggestion', 'value_suggested': post[answer_tag], 'value_text': comment_answer})
        else:
            vals.update({'answer_type': None, 'skipped': True})
        # '-1' indicates 'comment count as an answer' so do not need to record it
        if post.get(answer_tag) and post.get(answer_tag) != '-1':
            self.create(vals)

        comment_answer = post.pop(("%s_%s" % (answer_tag, 'comment')), '').strip()
        if comment_answer:
            vals.update(
                {'answer_type': 'text', 'value_text': comment_answer, 'skipped': False, 'value_suggested': False})
            self.create(vals)

        return True

   

    @api.model
    def save_line_numerical_box(self, user_input_id, question, post, answer_tag):
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'survey_id': question.survey_id.id,
            'skipped': False
        }
        # print('answer_tag==================,answer_tag',answer_tag)
        # print('answer_tag==================,answer_tag',post[answer_tag])
        if answer_tag in post and post[answer_tag].strip():
            comment_answer = post.pop(("%s_%s" % (answer_tag, 'comment')), '').strip()
            if comment_answer:
                vals.update({'answer_type': 'number', 'value_number': float(post[answer_tag]),'value_text': comment_answer,})
            else:
                vals.update({'answer_type': 'number', 'value_number': float(post[answer_tag])})

        else:
            vals.update({'answer_type': None, 'skipped': True})
        comment_answer = post.pop(("%s_%s" % (answer_tag, 'comment')), '').strip()
        if comment_answer:
            vals.update(
                {'answer_type': 'text', 'value_text': comment_answer, 'skipped': False, 'value_suggested': False})
            # self.create(vals)
        old_uil = self.search([
            ('user_input_id', '=', user_input_id),
            ('survey_id', '=', question.survey_id.id),
            ('question_id', '=', question.id)
        ])
        if old_uil:
            old_uil.write(vals)
        else:
            old_uil.create(vals)
        return True
    
    @api.model
    def save_line_textbox(self, user_input_id, question, post, answer_tag):
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'survey_id': question.survey_id.id,
            'skipped': False
        }
        if answer_tag in post and post[answer_tag].strip():
            comment_answer = post.pop(("%s_%s" % (answer_tag, 'comment')), '').strip()
            if comment_answer:
                vals.update({'answer_type': 'text', 'value_text':comment_answer})
            else:
                vals.update({'answer_type': 'text', 'value_text': post[answer_tag]})
        else:
            vals.update({'answer_type': None, 'skipped': True})
        comment_answer = post.pop(("%s_%s" % (answer_tag, 'comment')), '').strip()
        if comment_answer:
            vals.update(
                {'answer_type': 'text', 'value_text': comment_answer, 'skipped': False, 'value_suggested': False})
        old_uil = self.search([
            ('user_input_id', '=', user_input_id),
            ('survey_id', '=', question.survey_id.id),
            ('question_id', '=', question.id)
        ])
        if old_uil:
            old_uil.write(vals)
        else:
            old_uil.create(vals)
        return True
    


class kw_SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    emp_code = fields.Char(string='Employee code')
    year = fields.Char(related='appraisal_id.appraisal_year')
