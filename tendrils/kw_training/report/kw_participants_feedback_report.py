from odoo import models, fields, api
from odoo import tools

class ParticipantsFeedbackReport(models.Model):
    _name = 'kw_participants_feedback_report'
    _description = 'Participant wise report'

    _auto = False



    emp_id = fields.Many2one('hr.employee', "Employee")
    financial_year = fields.Many2one('account.fiscalyear', "Financial Year")
    training_id = fields.Many2one('kw_training', "Training")
    course_id = fields.Many2one('kw_skill_master','Course')
    course_type_id = fields.Many2one('kw_skill_type_master',string="Course Type")
    response_id = fields.Many2one('survey.user_input', "Response", ondelete="set null")
    question_id = fields.Many2one('survey.question',"Question Name")
    question_name = fields.Char(related='question_id.question',string = "Question")
    mark = fields.Float("Marks")
    remark = fields.Text("Remarks")


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as 
            (select ROW_NUMBER () OVER (order by a.training_id) as id,  a.emp_id,
        a.financial_year,
        a.training_id,
        a.response_id,
        c.question_id,
        k.course_type_id,
        k.course_id,
        (select quizz_mark from survey_user_input_line where question_id = c.question_id 
        and user_input_id = a.response_id  and value_text is null) as mark,
        (select value_text from survey_user_input_line where question_id = c.question_id 
        and user_input_id = a.response_id  and quizz_mark is null) as remark
        from kw_training_feedback as a
        join kw_training as k on k.id = a.training_id
        join survey_user_input_line as c
        on c.user_input_id = a.response_id 
        group by c.question_id,emp_id,a.financial_year,a.training_id,a.response_id,k.course_type_id,k.course_id)
            """ % (self._table))