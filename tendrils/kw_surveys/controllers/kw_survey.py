import json
import logging
from datetime import date  # datetime,
from odoo import fields, http, SUPERUSER_ID
from odoo.http import request
# from odoo.addons.web.controllers.main import ExcelExport
# import odoo.http as http

# import werkzeug
# from math import ceil
# import pytz
# from odoo.tools import ustr
# from odoo.addons.http_routing.models.ir_http import slug
# import collections 

_logger = logging.getLogger(__name__)


class kw_kwantify_survey(http.Controller):

    @http.route(['/kwantify/custom-survey/begin/<model("kw_surveys_details"):kwantify_surveys>/<string:token>',
                 '/kwantify/custom-survey/begin/<model("kw_surveys_details"):kwantify_surveys>/<string:token>/<model("res.users"):user>'],
                type='http', auth='public', method=['get', 'post'], website=True)
    def kwantify_survey_begin(self, kwantify_surveys, token=None, user=False, **post):
        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>11>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",kwantify_surveys,user)
        if not request.env.user:
            return http.request.redirect('/web/login')
        if request.env.user.employee_ids.id != kwantify_surveys.employee_ids.id:        
            return http.request.redirect('/web/session/logout')
        
        user_input = request.env['survey.user_input'].sudo().search([('token', '=', token)])
        # print('user_input....>>',user_input)
        show_skip_button = False
        if not request.session.get('skip_survey_feedback_form', False):
            show_skip_button = True
        data = {'kwantify_surveys': kwantify_surveys, 'token': token,'show_skip_button': show_skip_button}
       
        # print('skip button>>>>>',show_skip_button)

        if kwantify_surveys.state in ['1', '2']:
            if kwantify_surveys.state not in ['4']:
                kwantify_surveys.write({'state': '2'})
                user_input.write({'state': 'new', 'start_time': fields.Datetime.now() })

            if kwantify_surveys.end_date < date.today():
                return request.render("kw_surveys.kwantify_surveys_notopen_pages")
            else:
                return request.render('kw_surveys.kwantify_surveys_form', data)

        elif user and user.has_group('survey.group_survey_manager'):
            return request.render('kw_surveys.kwantify_surveys_form', data)
        else:
            return request.render('kw_surveys.kwantify_surveys_thanks_pages')


    @http.route(['/kwantify/survey/prefill/<model("kw_surveys_details"):kwantify_surveys>/<string:token>'], type='http',
                auth='public', website=True)
    def kwwantify_survey_prefill(self, kwantify_surveys, token=None, **post):
        UserInputLine = request.env['survey.user_input_line']
        ret = {}

        # Fetch previous answers
        previous_answers = UserInputLine.sudo().search([('user_input_id.token', '=', token)])
        # Return non empty answers in a JSON compatible format
        for answer in previous_answers:
            if not answer.skipped:
                answer_tag = '%s_%s_%s' % (answer.survey_id.id, answer.page_id.id, answer.question_id.id)
                answer_tag_comment = '%s_%s' % (answer_tag, 'comment')
                answer_value = None
                suggestion_remark_value = None

                if answer.answer_type == 'free_text':
                    answer_value = answer.value_free_text
                elif answer.answer_type == 'text' and answer.question_id.type == 'textbox':
                    answer_value = answer.value_text
                elif answer.answer_type == 'text' and answer.question_id.type != 'textbox':
                    # here come comment answers for matrices, simple choice and multiple choice
                    answer_tag = "%s_%s" % (answer_tag, 'comment')
                    answer_value = answer.value_text
                elif answer.answer_type == 'number':
                    answer_value = str(answer.value_number)
                elif answer.answer_type == 'date':
                    answer_value = fields.Date.to_string(answer.value_date)
                elif answer.answer_type == 'suggestion' and not answer.value_suggested_row:
                    answer_value = answer.value_suggested.id
                    if answer.value_text:
                        suggestion_remark_value = answer.value_text
                elif answer.answer_type == 'suggestion' and answer.value_suggested_row:
                    answer_tag = "%s_%s" % (answer_tag, answer.value_suggested_row.id)
                    answer_value = answer.value_suggested.id
                    if answer.value_text:
                        suggestion_remark_value = answer.value_text
                if answer_value:
                    ret.setdefault(answer_tag, []).append(answer_value)
                else:
                    _logger.warning(
                        "[survey] No answer has been found for question %s marked as non skipped" % answer_tag)

                if suggestion_remark_value:
                    ret.setdefault(answer_tag_comment, []).append(suggestion_remark_value)
        # print("final ret is", ret)
        return json.dumps(ret, default=str)

    @http.route('/kwantify/survey/submit/<model("kw_surveys_details"):kwantify_surveys>', type='http', methods=['POST'],
                auth='public', website=True)
    def kwantify_survey_submit(self, kwantify_surveys, **post):
        _logger.debug('Incoming data: %s', post)
        user_input_line = request.env['survey.user_input_line']
        # Answer validation
        errors = {}

        for page in kwantify_surveys.survey_id.page_ids:
            for question in page.question_ids:
                answer_tag = "%s_%s_%s" % (kwantify_surveys.survey_id.id, page.id, question.id)
                errors.update(question.validate_question(post, answer_tag))

        ret = {}
        if len(errors):
            # Return errors messages to webpage
            ret['errors'] = errors
        else:
            # Store answers into database
            try:
                user_input = request.env['survey.user_input'].sudo().search([('token', '=', post['token'])], limit=1)
                user_id = request.env.user.id or SUPERUSER_ID
            except KeyError as key:
                _logger.warning('KeyError: %s', key)

            for page in kwantify_surveys.survey_id.page_ids:
                for question in page.question_ids:
                    answer_tag = "%s_%s_%s" % (kwantify_surveys.survey_id.id, page.id, question.id)
                    user_input_line.sudo(user=user_id).save_lines(user_input.id, question, post, answer_tag)

            user_input.write({'state': 'done'})
            if kwantify_surveys.state not in ['3', '4']:
                kwantify_surveys.write({'state': '3', 'completed_on': date.today(), })
                user_input.write({'state': 'done', 'end_time': fields.Datetime.now(), })


            ret['redirect'] = '/kw/feedback/thank_you'

        return json.dumps(ret)
        # return request.redirect('/kw/feedback/thank_you',{'survey_score_data': survey_score_data})
        # demo={}
        # demo_data = request.env['survey.user_input'].sudo().search([('token', '=', post['token'])], limit=1)
        # # if demo_data:
        # #     demo['quizz_score'] = demo_data.quizz_score
        # # else:
        # #     demo['quizz_score'] = 0

        # if demo_data and demo_data.survey_id.survey_type.code == 'ignite':
        #     demo['quizz_score'] = demo_data.quizz_score if demo_data.quizz_score else 0
        #     total_score=sum(demo_data.mapped('survey_id.page_ids.question_ids.labels_ids.quizz_mark'))
        #     demo['total_score']= total_score
        #     demo['ignite']= 'ignite'
        # else:
        #     demo['ignite']= 'nonignite'
        # return request.render('kw_surveys.kwantify_surveys_thanks_pages', {'demo': demo})


    @http.route('/kw/feedback/thank_you', type='http', auth='public', website=True)
    def kwantify_feedback_thank_you(self, **kw):
        return request.render('kw_surveys.kwantify_surveys_thanks_pages')

    @http.route('/kwantify/custom-survey/results/<model("kw_surveys_details"):kwantify_surveys>/<string:token>',
                type='http', auth='user', website=True)
    def kwantify_survey_result(self, kwantify_surveys, token=None, **kw):
        data = {'kwantify_surveys': kwantify_surveys, 'token': token}
        return request.render('kw_surveys.kwantify_surveys_form_view', data)

    @http.route("/skip-now-survey-feedback-submit", type='http', auth='user', website=True)
    def skip_now_survey_feedback_submit(self):
        request.session['skip_survey_feedback_form'] = True
        return http.request.redirect('/web')


