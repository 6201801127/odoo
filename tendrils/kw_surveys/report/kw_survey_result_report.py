from odoo import models, fields, api
from odoo import tools


class KwantifySurveyResultReport(models.Model):
    _name = 'kw_survey_result_report'
    _description = 'Kwantify Survey Result Report'
    _auto = False
    _rec_name = "question"

    employee = fields.Char(string="Employee")
    designation = fields.Char(string="Designation")
    department = fields.Char(string="Department")
    division = fields.Char(string="Division")
    work_location = fields.Char(string="Work Location")
    question = fields.Char(string="Question")
    answer = fields.Char(string="Answer")

    @api.model_cr
    def init(self):
        surveys_id = self.env.context.get('surveys_id', 0)
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW {self._table} as (
            with ans AS
                    (
                    SELECT sui.survey_id,
                    sq.sequence, 
                    sq.question,
                    sui.partner_id,
                    row_number() over(partition by sq.sequence, sui.partner_id) AS slno,
                    case 
                    when suil.answer_type = 'text' then suil.value_text
                    when suil.answer_type = 'free_text' then suil.value_free_text
                    when suil.answer_type = 'suggestion' then Concat(sl.value,' ',suil.value_text)
                    when suil.answer_type = 'date' then TO_CHAR(suil.value_date, 'DD-Mon-YYYY')
                    when suil.answer_type = 'number' then  suil.value_number:: TEXT

                    else ''
                    end AS value
                    
                    FROM survey_user_input sui 
                    JOIN survey_user_input_line suil on suil.user_input_id = sui.id
                    JOIN survey_question sq ON sq.id = suil.question_id
                    LEFT JOIN survey_label sl ON sl.question_id = sq.id AND sl.id = suil.value_suggested
                    )
                SELECT ROW_NUMBER () OVER (ORDER BY he.id) AS id, 
                    concat(he.name,' (',he.emp_code,')') AS employee, 
                    (SELECT name FROM hr_job WHERE id = he.job_id) AS designation,
                    (SELECT name FROM hr_department WHERE id = he.department_id) AS department,
                    (SELECT name FROM hr_department WHERE id = he.division) AS division,
                    (SELECT alias FROM kw_res_branch WHERE id = he.job_branch_id) AS work_location,
                    question, value AS answer
                FROM kw_surveys ks
                JOIN kw_surveys_config_hr_employee_rel se ON se.kw_survey_id = ks.id
                JOIN hr_employee he ON he.id = se.employee_id
                JOIN res_users ru ON ru.id = he.user_id
                JOIN res_partner rp ON rp.id = ru.partner_id
                JOIN ans ON ans.survey_id = ks.survey_id AND ans.partner_id = ru.partner_id
                WHERE ks.id={surveys_id}   
                ORDER BY employee, sequence
        )""")
