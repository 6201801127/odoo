# Copyright 2016 Henry Zhou (http://www.maxodoo.com)
# Copyright 2016 Rodney (http://clearcorp.cr/)
# Copyright 2012 Agile Business Group
# Copyright 2012 Therp BV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import odoo.http as http
from odoo.http import request
from odoo.addons.web.controllers.main import ExcelExport


class ExcelExportView(ExcelExport):
    def __getattribute__(self, name):
        if name == 'fmt':
            raise AttributeError()
        return super(ExcelExportView, self).__getattribute__(name)

    @http.route('/web/export/xls_view', type='http', auth='user')
    def export_xls_view(self, data, token):
        data = json.loads(data)
        model = data.get('model', [])
        columns_headers = data.get('headers', [])
        rows = data.get('rows', [])

        return request.make_response(
            self.from_data(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )

    @http.route('/export-survey-result/<model("kw_surveys"):kwantify_surveys>', type='http', auth='user')
    def export_xls_survey(self, kwantify_surveys, token="csmpl"):
        data = kwantify_surveys
        kw_surveys_id = data.id
        survey_id = data.survey_id.id

        xls_headers = {}
        comment_counter = 0
        for pages in data.survey_id.page_ids:
            for questions in pages.question_ids:
                """add xls headers"""
                xls_headers.update({questions.question: questions.id})
                if questions.comments_allowed:
                    xls_headers.update({f"Comment {comment_counter}": questions.id})
                    comment_counter += 1
        """KW Survey Details"""
        surveys_detail = request.env['kw_surveys_details'].sudo().search([('kw_surveys_id', '=', kw_surveys_id)])
        fil_surveys_detail = surveys_detail.filtered(lambda x : x.state in ['3','4'])
        """Survey User inputs"""
        # user_input = request.env['survey.user_input'].sudo().search([('survey_id', '=', survey_id)])
        kw_surveys_user_inputs = surveys_detail.mapped("user_input_id.id") if surveys_detail else []
        user_input = request.env['survey.user_input'].sudo().search([('id', 'in', kw_surveys_user_inputs)])

        """employee section"""
        # employees_list = request.env['hr.employee'].sudo().search([('user_id.partner_id', 'in', user_input.mapped('partner_id').ids)])
        kw_surveys_employees = fil_surveys_detail.mapped('employee_ids.id') if fil_surveys_detail else []
        employees_list = request.env['hr.employee'].sudo().search([('id', 'in', kw_surveys_employees)])
        xls_emp_headers = {'Name': 'name', 'Code': 'code', 'Designation': 'job', 'Location': 'location', 'Department': 'department', 'Type': 'type', 'Gender':'gender','Mobile No':'mobile'}
        if kwantify_surveys.survey_id.survey_type.code == 'ignite':
            xls_emp_headers.update({
                'Started On':'started_on',
                'Submitted on':'submitted_on',
                'Duration in (Sec)':'duration_in_sec'
            })
        employees = {}
        # employee_ids = data.employee_ids
        """fetch employee details"""
        for emp in employees_list:
            employees.update({emp.sudo().user_id.partner_id.id: {"employee_id": emp.id,
                                                                 "name": emp.name,
                                                                 "code": emp.emp_code,
                                                                 "type": emp.sudo().employement_type.name or '',
                                                                 "gender": emp.sudo().gender or '',
                                                                 "job": emp.sudo().job_id.display_name or '',
                                                                 "location": emp.sudo().job_branch_id.display_name or '',
                                                                 "department": emp.department_id.name,
                                                                 "mobile": emp.mobile_phone or '',
                                                                 "partner_id": emp.sudo().user_id.partner_id.id,
                                                                 }})
        answers_dict = {}
        for survey_input in user_input:
            partner_id = survey_input.partner_id.id
            if kwantify_surveys.survey_id.survey_type.code == 'ignite':
                employees[partner_id].update({
                    'started_on':survey_input.start_time,
                    'submitted_on':survey_input.write_date,
                    'duration_in_sec':survey_input.duration
                })

            for ans in survey_input.user_input_line_ids:
                answers_dict.setdefault(partner_id, {})
                ans_item = {ans.question_id.id: {"partner_id": partner_id,
                                                 "question_id": ans.question_id.id,
                                                 "user_input_id": ans.user_input_id.id,
                                                 # "survey": ans.survey_id.title,
                                                 "question": ans.question_id.question,
                                                 "question_type": ans.question_id.type,
                                                 "question_comments_allowed": ans.question_id.comments_allowed,
                                                 "skipped": ans.skipped,
                                                 "answer_type": ans.answer_type,
                                                 "value_text": ans.value_text,
                                                 "value_number": ans.value_number,
                                                 "value_date": ans.value_date,
                                                 "value_free_text": ans.value_free_text,
                                                 "value_suggested": ans.value_suggested.value,
                                                 }}
                answers_dict[partner_id].update(ans_item)
        model = 'kw_surveys'
        columns_headers = list(xls_emp_headers.keys())
        columns_headers += list(xls_headers.keys())
        """generate final rows"""
        rows = []
        for emp in employees:
            tmp_list = []
            for key in xls_emp_headers.values():
                tmp_list.append(employees[emp][key])
            for key in xls_headers:
                res = answers_dict[emp].get(xls_headers.get(key, False), '') if key in xls_headers and emp in answers_dict else False
                if res:
                    # print('question_type >> ', res.get('question_type', False))
                    # print("key >> ", key)
                    """ text / free_text / textbox / numerical_box / date / simple_choice / multiple_choice / matrix """
                    if res.get('question_type', False) == 'simple_choice' and 'Comment' not in key:
                        answer = res.get('value_suggested', '')
                        tmp_list.append(answer)
                    elif res.get('question_type', False) == 'date' and 'Comment' not in key:
                        answer = res.get('value_date', '')
                        tmp_list.append(answer or '')
                    elif res.get('question_type', False) == 'text' and 'Comment' not in key:
                        answer = res.get('value_text', '')
                        tmp_list.append(answer or '')
                    elif res.get('question_type', False) == 'free_text' and 'Comment' not in key:
                        answer = res.get('value_free_text', '')
                        tmp_list.append(answer or '')
                    elif res.get('question_type', False) == 'textbox' and 'Comment' not in key:
                        answer = res.get('value_text', '')
                        tmp_list.append(answer or '')
                    elif res.get('question_type', False) == 'numerical_box' and 'Comment' not in key:
                        answer = res.get('value_number', '')
                        tmp_list.append(answer or '')

                    if res.get('question_comments_allowed', False) and 'Comment' in key:
                        answer = res.get('value_text', '')
                        tmp_list.append(answer)
                    # print("answer >> ", answer)
                else:
                    tmp_list.append('')

            rows.append(tmp_list)
        # return
        # data = json.loads(data)
        # model = data.get('model', [])
        # columns_headers = data.get('headers', [])
        # rows = data.get('rows', [])
        # token = 'csmpl'
        return request.make_response(
            self.from_data(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )