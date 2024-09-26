from odoo import models, fields, api

from odoo import tools



class PIPTrainingRecommendationReport(models.Model):
    _name = "kw_pip_training_recommendation_report"
    _auto = False
    _description = "Training and Recommendation Report"


    financial_year = fields.Many2one('account.fiscalyear', string="Financial Year")
    course_type_id = fields.Many2one('kw_skill_type_master', string="Course Type")
    course_id = fields.Many2one('kw_skill_master', string="Course")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    pip_ref = fields.Char(string="PIP Ref")

    employee_id = fields.Many2one('hr.employee', string='Employee')
    raised_by = fields.Many2one('hr.employee', string='Raised By')
    applied_date = fields.Date(string="Applied Date")
    assessment_score = fields.Float(string="Assessment Score")


    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'kw_pip_training_recommendation_report')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW kw_pip_training_recommendation_report AS (
            SELECT
                r.id as id,
                t.course_type_id AS course_type_id,
                t.course_id AS course_id,
                t.start_date AS start_date,
                t.end_date AS end_date,
                t.pip_ref AS pip_ref,
                r.employee_id AS employee_id,
                r.raised_by AS raised_by,
                r.applied_date AS applied_date,
                t.financial_year AS financial_year,
                sam.percentage_scored AS assessment_score
            from
                kw_recommend_training r left join kw_training t on r.pip_id = t.pip_training_id
                LEFT JOIN
                kw_training_assessment ta ON ta.training_id = t.id
                LEFT JOIN
                kw_skill_answer_master sam ON sam.set_config_id = ta.assessment_id 
                AND sam.emp_rel = r.employee_id) """)



