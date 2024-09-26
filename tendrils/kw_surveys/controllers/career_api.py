# -*- coding: utf-8 -*-
import json
from odoo import http


class CareerSurveyAPI(http.Controller):

    @http.route("/employee_survey_result", type="http", cors='*', auth="none", methods=["GET"], csrf=False)
    def save_applicant(self, **payload):

        data = {"result": []}
        survey = http.request.env['kw_surveys'].sudo().search(
            [('feedback_status', '=', 'published'), ('survey_details_id', '!=', False), ('id', '=', 3)])
        for details in survey.survey_details_id.filtered(lambda r: r.state == '4'):  # select published records
            temp_emp_dict = {"employee": details.employee_ids.name,
                             "designation": details.employee_ids.job_id and details.employee_ids.job_id.name or "",
                             "answer": ""}
            if details.user_input_id:
                input = details.user_input_id.user_input_line_ids.sorted(lambda r: r.question_id.sequence)
                if input:
                    ques = input[0]
                    if ques.answer_type == 'text':
                        temp_emp_dict['answer'] = ques.value_text

                    elif ques.answer_type == 'free_text':
                        temp_emp_dict['answer'] = ques.value_free_text

                    elif ques.answer_type == 'number':
                        temp_emp_dict['answer'] = int(ques.value_number)

                    elif ques.answer_type == 'date':
                        temp_emp_dict['answer'] = ques.value_date.strftime("%d-%b-%Y")

                    elif ques.answer_type == 'suggestion':
                        temp_emp_dict['answer'] = ques.value_suggested.value
            data["result"].append(temp_emp_dict)

        return json.dumps(data)
