import werkzeug

from odoo.api import Environment
import odoo.http as http

from odoo.http import request
from odoo import SUPERUSER_ID
from odoo import registry as registry_get
import odoo.addons.calendar.controllers.main as main
from werkzeug.exceptions import BadRequest, Forbidden, NotFound
import base64
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


class RecruitmentMeetingView(http.Controller):

    @http.route('/recruitment/meeting/view/cv', type='http', auth="user", website=True)
    def view(self, db, token, action, id, applicant_id, view='calendar'):
        # Path to the file you want to download
        applicant_id = request.env['hr.applicant'].sudo().search(
            [('id', '=', int(applicant_id)), ('active', 'in', [True, False])], limit=1)
        file_data = applicant_id.document_ids.content_file
        if file_data:
            # Decode the binary data if it's encoded (assuming base64)
            decoded_file_data = base64.b64decode(file_data)
            # Determine content type
            content_type = ['application/pdf', 'application/msword']
            # Set filename for the downloaded file
            file_name = str(applicant_id.document_ids.file_name)
            # Set headers for file download
            headers = [
                ('Content-Type', content_type),
                ('Content-Disposition', http.content_disposition(file_name)),
            ]
            # Return the file as an HTTP response
            return http.request.make_response(decoded_file_data, headers=headers)
        else:
            raise NotFound()
            # return "CV not found"  # Handle error if PDF data is not available

    # @http.route('/recruitment/meeting/view', type='http', auth="user")
    # def view(self, db, token, action, id, applicant_id, view='calendar'):
    #     print("self-----------------------------------",self)
    #     print("db-----------------------------------",db)
    #     print("token-----------------------------------",token)
    #     print("id-----------------------------------",id)
    #     print("action-----------------------------------",action)
    #     print("applicant_id-----------------------------------",applicant_id)

    #     registry = registry_get(db)
    #     with registry.cursor() as cr:
    #         # Since we are in auth=none, create an env with SUPERUSER_ID
    #         env = Environment(cr, SUPERUSER_ID, {})
    #         attendee = env['kw_meeting_attendee'].search(
    #             [('access_token', '=', token), ('event_id', '=', int(id))])
    #         if not attendee:
    #             return request.not_found()
    #         # timezone = attendee.partner_id.tz
    #         lang = attendee.partner_id.lang or 'en_US'
           
    #         event = env['kw_meeting_events'].browse(int(id))

    #         if event.applicant_ids and request.session.uid and request.env['res.users'].browse(request.session.uid).user_has_groups('base.group_user'):
    #             meeting_action = request.env.ref(
    #                 'kw_recruitment_meeting_schedule.action_kw_meeting_events_attendee').id
    #             return werkzeug.utils.redirect('/web?db=%s#id=%s&view_type=form&model=kw_meeting_events&action=%s' % (db, id, meeting_action))
            
    #         response_content = env['ir.ui.view'].with_context(lang=lang).render_template(
    #             'kw_meeting_schedule.invitation_page_anonymous', {
    #                 'event': event,
    #                 'attendee': attendee,
    #             })
    #         return request.make_response(response_content, headers=[('Content-Type', 'text/html')])


class Kw_Recruitment_Survey(http.Controller):
    # HELPER METHODS #

    def kw_recruitment_check_bad_cases(self, survey, token=None):
        # In case of bad survey, redirect to surveys list
        if not survey.sudo().exists():
            return werkzeug.utils.redirect("/survey/")

        # In case of auth required, block public user
        # if survey.auth_required and request.env.user._is_public():
        #     return request.render("kw_recruitment_meeting_schedule.auth_required", {'survey': survey, 'token': token})

        # In case of non open surveys
        if survey.stage_id.closed:
            return request.render("kw_recruitment_meeting_schedule.notopen")

        # If there is no pages
        if not survey.page_ids:
            return request.render("kw_recruitment_meeting_schedule.nopages", {'survey': survey})

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
                return request.render("kw_recruitment_meeting_schedule.notopen")
        return None

    # # ROUTES HANDLERS ##

    # Survey start
    @http.route(['/candidate/feedback/start/<model("survey.survey"):survey>',
                 '/candidate/feedback/start/<model("survey.survey"):survey>/<string:token>',
                 ],
                type='http', auth='public', website=True)
    def kw_recruitment_meeting_start_survey(self, survey, token=None, applicant_id=None, **post):
        # if applicant_id not None:
        #     pass
        UserInput = request.env['survey.user_input']

        # Controls if the survey can be displayed
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
                return request.render("kw_recruitment_meeting_schedule.error", {'survey': survey})

        # Do not open expired survey
        errpage = self.kw_recruitment_check_deadline(user_input)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # Intro page
            data = {'survey': survey, 'page': None, 'token': user_input.token, 'user_input': user_input}
            # return request.render('kw_recruitment.survey_init', data)
            return request.redirect('/candidate/feedback/fill/%s/%s' % (survey.id, user_input.token))
        else:
            return request.redirect('/candidate/feedback/fill/%s/%s' % (survey.id, user_input.token))

    @http.route(['/candidate/feedback/thankyou/<model("survey.survey"):survey>/<string:token>'], type='http', auth='public', website=True)
    def kw_recruitment_meeting_display_survey_thankyou(self, survey, token=None, applicant_id=None, **post):
        UserInput = request.env['survey.user_input']
        user_input = UserInput.sudo().search([('token', '=', token)], limit=1)
        data = {'survey': survey,'token': token,
                'user_input': user_input or False,
                }
        return request.render('kw_recruitment_meeting_schedule.sfinished', data)

    # Survey displaying
    @http.route(['/candidate/feedback/fill/<model("survey.survey"):survey>/<string:token>',
                 '/candidate/feedback/fill/<model("survey.survey"):survey>/<string:token>/<string:prev>'],
                type='http', auth='public', website=True)
    def kw_recruitment_meeting_fill_survey(self, survey, token, prev=None, **post):
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
            return request.render("kw_recruitment_meeting_schedule.error", {'survey': survey})

        # Do not display expired survey (even if some pages have already been
        # displayed -- There's a time for everything!)
        errpage = self.kw_recruitment_check_deadline(user_input)
        if errpage:
            return errpage

        # Select the right page
        if user_input.state == 'new':  # First page
            page, page_nr, last = Survey.next_page(user_input, 0, go_back=False)
            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'user_input': user_input}
            if last:
                data.update({'last': True})
            return request.render('kw_recruitment_meeting_schedule.survey', data)
        elif user_input.state == 'done':  # Display success message
            return request.render('kw_recruitment_meeting_schedule.sfinished', {'survey': survey,
                                                                                'token': token,
                                                                                'user_input': user_input})
        elif user_input.state == 'skip':
            flag = (True if prev and prev == 'prev' else False)
            page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=flag)

            # special case if you click "previous" from the last page, then leave the survey, then reopen it from the URL, avoid crash
            if not page:
                page, page_nr, last = Survey.next_page(user_input, user_input.last_displayed_page_id.id, go_back=True)

            data = {'survey': survey, 'page': page, 'page_nr': page_nr, 'token': user_input.token, 'user_input': user_input}
            if last:
                data.update({'last': True})
            return request.render('kw_recruitment_meeting_schedule.survey', data)
        else:
            return request.render("kw_recruitment_meeting_schedule.error", {'survey': survey})

    # AJAX pre filling of a survey
    @http.route(['/candidate/feedback/prefill/<model("survey.survey"):survey>/<string:token>',
                 '/candidate/feedback/prefill/<model("survey.survey"):survey>/<string:token>/<model("survey.page"):page>'],
                type='http', auth='public', website=True)
    def kw_recruitment_meeting_prefill(self, survey, token, page=None, **post):
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

    # AJAX scores loading for quiz correction mode
    @http.route(['/candidate/feedback/scores/<model("survey.survey"):survey>/<string:token>'],
                type='http', auth='public', website=True)
    def kw_recruitment_meeting_get_scores(self, survey, token, page=None, **post):
        ret = {}

        # Fetch answers
        previous_answers = request.env['survey.user_input_line'].sudo().search([('user_input_id.token', '=', token)])

        # Compute score for each question
        for answer in previous_answers:
            tmp_score = ret.get(answer.question_id.id, 0.0)
            ret.update({answer.question_id.id: tmp_score + answer.quizz_mark})
        return json.dumps(ret)

    # AJAX submission of a page
    @http.route(['/candidate/feedback/submit/<model("survey.survey"):survey>'], type='http', methods=['POST'], auth='public', website=True)
    def kw_recruitment_meeting_submit(self, survey, **post):
        _logger.debug('Incoming data: %s', post)
        page_id = int(post['page_id'])
        questions = request.env['survey.question'].search([('page_id', '=', page_id)])

        # Answer validation
        errors = {}
        for question in questions:
            answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
            errors.update(question.validate_question(post, answer_tag))

        ret = {}
        if len(errors):
            # Return errors messages to webpage
            ret['errors'] = errors
        else:
            # Store answers into database
            try:
                user_input = request.env['survey.user_input'].sudo().search([('token', '=', post['token'])], limit=1)
            except KeyError:  # Invalid token
                return request.render("kw_recruitment_meeting_schedule.error", {'survey': survey})
            user_id = request.env.user.id if user_input.type != 'link' else SUPERUSER_ID

            for question in questions:
                answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
                request.env['survey.user_input_line'].sudo(user=user_id).save_lines(
                    user_input.id, question, post, answer_tag)

            go_back = post['button_submit'] == 'previous'
            next_page, _, last = request.env['survey.survey'].next_page(
                user_input, page_id, go_back=go_back)
            vals = {'last_displayed_page_id': page_id}
            if next_page is None and not go_back:
                vals.update({'state': 'done'})
            else:
                vals.update({'state': 'skip'})
            user_input.sudo(user=user_id).write(vals)
            ret['redirect'] = '/candidate/feedback/thankyou/%s/%s' % (survey.id, post['token'])
            if go_back:
                ret['redirect'] += '/prev'
        return json.dumps(ret)

    # Printing routes
    @http.route(['/candidate/feedback/print/<model("survey.survey"):survey>',
                 '/candidate/feedback/print/<model("survey.survey"):survey>/<string:token>'],
                type='http', auth='public', website=True)
    def kw_recruitment_meeting_print_survey(self, survey, token=None, **post):
        """Display an survey in printable view; if <token> is set, it will
        grab the answers of the user_input_id that has <token>."""

        # if survey.auth_required and request.env.user == request.website.user_id:
        #     return request.render("kw_recruitment_meeting_schedule.auth_required", {'survey': survey, 'token': token})

        return request.render('kw_recruitment_meeting_schedule.survey_print',
                              {'survey': survey,
                               'token': token,
                               'page_nr': 0,
                               'quizz_correction': True if survey.quizz_mode and token else False})

    @http.route(['/candidate/feedback/results/<model("survey.survey"):survey>'],
                type='http', auth='user', website=True)
    def kw_recruitment_meeting_survey_reporting(self, survey, token=None, **post):
        """Display survey Results & Statistics for given survey."""
        result_template = 'kw_recruitment_meeting_schedule.result'
        current_filters = []
        filter_display_data = []
        filter_finish = False

        if not survey.user_input_ids or not [input_id.id for input_id in survey.user_input_ids if input_id.state != 'new']:
            result_template = 'kw_recruitment_meeting_schedule.no_result'
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

    def kw_recruitment_meeting_prepare_result_dict(self, survey, current_filters=None):
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
            # if user add some random data in query URI, ignore it
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
