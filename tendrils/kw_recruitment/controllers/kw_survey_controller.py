# -*- coding: utf-8 -*-

import json
import logging
import werkzeug
from datetime import datetime
from math import ceil

from odoo import fields, http, SUPERUSER_ID
from odoo.http import request
from odoo.tools import ustr

_logger = logging.getLogger(__name__)


class Kw_Recruitment_Survey(http.Controller):
    # HELPER METHODS #

    def kw_recruitment_check_bad_cases(self, survey, token=None):
        # In case of bad survey, redirect to surveys list
        if not survey.sudo().exists():
            return werkzeug.utils.redirect("/survey/")

        # In case of auth required, block public user
        if survey.auth_required and request.env.user._is_public():
            return request.render("kw_recruitment.auth_required", {'survey': survey, 'token': token})

        # In case of non open surveys
        if survey.stage_id.closed:
            return request.render("kw_recruitment.notopen")

        # If there is no pages
        if not survey.page_ids:
            return request.render("kw_recruitment.nopages", {'survey': survey})

        # Everything seems to be ok
        return None

    def kw_recruitment_check_deadline(self, user_input):
        """ Prevent opening of the survey if the deadline has turned out

        ! This will NOT disallow access to users who have already partially filled the survey ! """
        deadline = user_input.deadline
        if deadline:
            dt_deadline = fields.Datetime.from_string(deadline)
            dt_now = datetime.now()
            if dt_now > dt_deadline:  # survey is not open anymore
                return request.render("kw_recruitment.notopen")
        return None

    # # ROUTES HANDLERS ##

    # Survey start
    @http.route(['/kw_recruitment/survey/start/<model("survey.survey"):survey>',
                 '/kw_recruitment/survey/start/<model("survey.survey"):survey>/<string:token>',
                 #  Extra added to take the applicant id  #
                 #  '/kw_recruitment/survey/start/<model("survey.survey"):survey>/<string:applicant_id>',
                 #  '/kw_recruitment/survey/start/<model("survey.survey"):survey>/<string:token>/<string:applicant_id>',
                 #  Extra added to take the applicant id  #
                 ],
                type='http', auth='user', website=True)
    def kw_recruitment_start_survey(self, survey, token=None, applicant_id=None, **post):
        # if applicant_id not None:
        #     pass
        UserInput = request.env['survey.user_input']

        """# Controls if the survey can be displayed"""
        errpage = self.kw_recruitment_check_bad_cases(survey, token=token)
        if errpage:
            return errpage

        # Manual surveying
        if not token:
            vals = {'survey_id': survey.id}
            if not request.env.user._is_public():
                vals['partner_id'] = request.env.user.partner_id.id
            user_input = UserInput.create(vals)
        else:
            user_input = UserInput.sudo().search([('token', '=', token)], limit=1)
            if not user_input:
                return request.render("kw_recruitment.error", {'survey': survey})

        """# Do not open expired survey"""
        err_page = self.kw_recruitment_check_deadline(user_input)
        if err_page:
            return err_page

        """# Select the right page"""
        # if user_input.state == 'new':  # Intro page
        #     data = {'survey': survey, 'page': None, 'token': user_input.token, 'user_input': user_input}
        #     # return request.render('kw_recruitment.survey_init', data)
        #     return request.redirect('/kw_recruitment/survey/fill/%s/%s' % (survey.id, user_input.token))
        # else:
        #     return request.redirect('/kw_recruitment/survey/fill/%s/%s' % (survey.id, user_input.token))
        return request.redirect('/kw_recruitment/survey/fill/%s/%s' % (survey.id, user_input.token))

    @http.route(['/kw_recruitment/survey/thankyou/<model("survey.survey"):survey>/<string:token>'], type='http', auth='user', website=True)
    def display_survey_thankyou(self, survey, token=None, applicant_id=None, **post):
        UserInput = request.env['survey.user_input']
        user_input = UserInput.sudo().search([('token', '=', token)], limit=1)
        menu_id = request.env.ref('kw_meeting_schedule.main_menu_kw_meeting_schedule').id
        data = {'survey': survey,'token': token,
                'user_input': user_input or False,
                'menu_id':menu_id
                }
        # print(data)
        return request.render('kw_recruitment.sfinished', data)

    # Survey displaying
    @http.route(['/kw_recruitment/survey/fill/<model("survey.survey"):survey>/<string:token>',
                 '/kw_recruitment/survey/fill/<model("survey.survey"):survey>/<string:token>/<string:prev>'],
                type='http', auth='user', website=True)
    def kw_recruitment_fill_survey(self, survey, token, prev=None, **post):
        """Display and validates a survey"""
        Survey = request.env['survey.survey']
        UserInput = request.env['survey.user_input']

        # Controls if the survey can be displayed
        errpage = self.kw_recruitment_check_bad_cases(survey)
        if errpage:
            return errpage

        # Load the user_input
        user_input = UserInput.sudo().search([('token', '=', token)], limit=1)
        if not user_input:  # Invalid token
            return request.render("kw_recruitment.error", {'survey': survey})

        # Do not display expired survey (even if some pages have already been
        # displayed -- There's a time for everything!)
        errpage = self.kw_recruitment_check_deadline(user_input)
        if errpage:
            return errpage
        show_skip_button = False
        if request.env.user.employee_ids.grade.name in ['M10', 'E1', 'E2', 'E3', 'E4', 'E5']:
            show_skip_button = True
        # Select the right page
        if user_input.state == 'new':  # First page
            page, page_nr, last = Survey.next_page(user_input, 0, go_back=False)
            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token,
                    'user_input': user_input, 'show_skip_button': show_skip_button}
            if last:
                data.update({'last': True})
            return request.render('kw_recruitment.survey', data)
        elif user_input.state == 'done':  # Display success message
            return request.render('kw_recruitment.sfinished', {'survey': survey,
                                                               'token': token,
                                                               'user_input': user_input})
        elif user_input.state == 'skip':
            flag = (True if prev and prev == 'prev' else False)
            page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=flag)

            # special case if you click "previous" from the last page, then leave the survey, then reopen it from the URL, avoid crash
            if not page:
                page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=True)

            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token,
                    'user_input': user_input, 'show_skip_button': show_skip_button}
            if last:
                data.update({'last': True})
            return request.render('kw_recruitment.survey', data)
        else:
            return request.render("kw_recruitment.error", {'survey': survey})

    # AJAX pre filling of a survey
    @http.route(['/kw_recruitment/survey/prefill/<model("survey.survey"):survey>/<string:token>',
                 '/kw_recruitment/survey/prefill/<model("survey.survey"):survey>/<string:token>/<model("survey.page"):page>'],
                type='http', auth='user', website=True)
    def kw_recruitment_prefill(self, survey, token, page=None, **post):
        UserInputLine = request.env['survey.user_input_line']
        ret = {}

        # Fetch previous answers
        if page:
            previous_answers = UserInputLine.sudo().search([('user_input_id.token', '=', token), ('page_id', '=', page.id)])
        else:
            previous_answers = UserInputLine.sudo().search([('user_input_id.token', '=', token)])

        # Return non empty answers in a JSON compatible format
        for answer in previous_answers:
            if not answer.skipped:
                answer_tag = '%s_%s_%s' % (answer.survey_id.id, answer.page_id.id, answer.question_id.id)
                answer_value = None
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
                elif answer.answer_type == 'suggestion' and answer.value_suggested_row:
                    answer_tag = "%s_%s" % (answer_tag, answer.value_suggested_row.id)
                    answer_value = answer.value_suggested.id
                if answer_value:
                    ret.setdefault(answer_tag, []).append(answer_value)
                else:
                    _logger.warning("[survey] No answer has been found for question %s marked as non skipped" % answer_tag)
        return json.dumps(ret, default=str)

    """# AJAX scores loading for quiz correction mode"""
    @http.route(['/kw_recruitment/survey/scores/<model("survey.survey"):survey>/<string:token>'],
                type='http', auth='user', website=True)
    def kw_recruitment_get_scores(self, survey, token, page=None, **post):
        ret = {}

        # Fetch answers
        previous_answers = request.env['survey.user_input_line'].sudo().search([('user_input_id.token', '=', token)])

        # Compute score for each question
        for answer in previous_answers:
            tmp_score = ret.get(answer.question_id.id, 0.0)
            ret.update({answer.question_id.id: tmp_score + answer.quizz_mark})
        return json.dumps(ret)

    """# AJAX submission of a page"""
    @http.route(['/kw_recruitment/survey/submit/<model("survey.survey"):survey>'], type='http', methods=['POST'], auth='public', website=True)
    def kw_recruitment_submit(self, survey, **post):
        _logger.debug('Incoming data: %s', post)
        page_id = int(post['page_id'])
        questions = request.env['survey.question'].search([('page_id', '=', page_id)])

        """# Answer validation"""
        errors = {}
        for question in questions:
            answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
            errors.update(question.validate_question(post, answer_tag))

        ret = {}
        if len(errors):
            """# Return errors messages to webpage"""
            ret['errors'] = errors
        else:
            """# Store answers into database"""
            try:
                user_input = request.env['survey.user_input'].sudo().search([('token', '=', post['token'])], limit=1)
            except KeyError:  # Invalid token
                return request.render("kw_recruitment.error", {'survey': survey})
            user_id = request.env.user.id if user_input.type != 'link' else SUPERUSER_ID

            for question in questions:
                answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
                request.env['survey.user_input_line'].sudo(user=user_id).save_lines(
                    user_input.id, question, post, answer_tag)

            go_back = post['button_submit'] == 'previous'
            next_page, _, last = request.env['survey.survey'].next_page(
                user_input, page_id, go_back=go_back)
            vals = {'last_displayed_page_id': page_id}
            # if next_page is None and not go_back:
            #     vals.update({'state': 'skip'})
            # else:
            vals.update({'state': 'skip'})
            user_input.sudo(user=user_id).write(vals)
            ret['redirect'] = '/kw_recruitment/survey/thankyou/%s/%s' % (survey.id, post['token'])
            if go_back:
                ret['redirect'] += '/prev'
        return json.dumps(ret)

    """# Printing routes"""
    @http.route(['/kw_recruitment/survey/print/<model("survey.survey"):survey>',
                 '/kw_recruitment/survey/print/<model("survey.survey"):survey>/<string:token>'],
                type='http', auth='user', website=True)
    def kw_recruitment_print_survey(self, survey, token=None, **post):
        """Display an survey in printable view; if <token> is set, it will
        grab the answers of the user_input_id that has <token>."""

        if survey.auth_required and request.env.user == request.website.user_id:
            return request.render("kw_recruitment.auth_required", {'survey': survey, 'token': token})

        return request.render('kw_recruitment.survey_print',
                              {'survey': survey,
                               'token': token,
                               'page_nr': 0,
                               'quizz_correction': True if survey.quizz_mode and token else False})

    @http.route(['/kw_recruitment/survey/results/<model("survey.survey"):survey>'],
                type='http', auth='user', website=True)
    def kw_recruitment_survey_reporting(self, survey, token=None, **post):
        """Display survey Results & Statistics for given survey."""
        result_template = 'kw_recruitment.result'
        current_filters = []
        filter_display_data = []
        filter_finish = False

        if not survey.user_input_ids or not [input_id.id for input_id in survey.user_input_ids if input_id.state != 'new']:
            result_template = 'kw_recruitment.no_result'
        if 'finished' in post:
            post.pop('finished')
            filter_finish = True
        if post or filter_finish:
            filter_data = self.get_filter_data(post)
            current_filters = survey.filter_input_ids(filter_data, filter_finish)
            filter_display_data = survey.get_filter_display_data(filter_data)
        return request.render(result_template,
                              {'survey': survey,
                               'survey_dict': self.prepare_result_dict(survey, current_filters),
                               'page_range': self.page_range,
                               'current_filters': current_filters,
                               'filter_display_data': filter_display_data,
                               'filter_finish': filter_finish
                               })

    def kw_recruitment_prepare_result_dict(self, survey, current_filters=None):
        """Returns dictionary having values for rendering template"""
        current_filters = current_filters if current_filters else []
        Survey = request.env['survey.survey']
        result = {'page_ids': []}
        for page in survey.page_ids:
            page_dict = {'page': page, 'question_ids': []}
            for question in page.question_ids:
                question_dict = {
                    'question': question,
                    'input_summary': Survey.get_input_summary(question, current_filters),
                    'prepare_result': Survey.prepare_result(question, current_filters),
                    'graph_data': self.get_graph_data(question, current_filters),
                }

                page_dict['question_ids'].append(question_dict)
            result['page_ids'].append(page_dict)
        return result

    def kw_recruitment_get_filter_data(self, post):
        """Returns data used for filtering the result"""
        filters = []
        for ids in post:
            """# if user add some random data in query URI, ignore it"""
            try:
                row_id, answer_id = ids.split(',')
                filters.append({'row_id': int(row_id), 'answer_id': int(answer_id)})
            except:
                return filters
        return filters

    def kw_recruitment_page_range(self, total_record, limit):
        """Returns number of pages required for pagination"""
        total = ceil(total_record / float(limit))
        return range(1, int(total + 1))

    def kw_recruitment_get_graph_data(self, question, current_filters=None):
        """Returns formatted data required by graph library on basis of filter"""
        # TODO refactor this terrible method and merge it with prepare_result_dict
        current_filters = current_filters if current_filters else []
        Survey = request.env['survey.survey']
        result = []
        if question.type == 'multiple_choice':
            result.append({'key': ustr(question.question), 'values': Survey.prepare_result(question, current_filters)['answers']})
        if question.type == 'simple_choice':
            result = Survey.prepare_result(question, current_filters)['answers']
        if question.type == 'matrix':
            data = Survey.prepare_result(question, current_filters)
            for answer in data['answers']:
                values = []
                for row in data['rows']:
                    values.append({'text': data['rows'].get(row), 'count': data['result'].get((row, answer))})
                result.append({'key': data['answers'].get(answer), 'values': values})
        return json.dumps(result)

    @http.route("/skip-now-interview-feedback-submit", type='http', auth='user', website=True)
    def skip_now_interview_feedback_submit(self):
        request.session['skip_interview_feedback_form'] = True
        return http.request.redirect('/web')
