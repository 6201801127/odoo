# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields, api

class TrainingAssessmentReport(models.Model):
    _name = "kw_training_assessment_result"
    _description = "Training Assessment Result"
    _auto = False

    name = fields.Char("Name")
    designation = fields.Char("Designation")
    question_set_id = fields.Many2one("kw_skill_question_set_config",string="Assessment")
    date = fields.Datetime(string='Test Start Time',)
    time_taken = fields.Char("Time Taken")
    status = fields.Char(string='Status')
    score = fields.Integer("Score")
    percentage = fields.Integer("Percentage")


    @api.multi
    def _compute_time(self):
        for rec in self:
            if rec.time_taken:
                rec.f_time_taken = self.convert(int(rec.time_taken))
    @api.multi
    def view_participant_result(self):
        emp_id = self.id
        question_set_id = self.question_set_id.id
        assessment_given = self.env['kw_skill_answer_master'].sudo().search(
            [('emp_rel', '=', emp_id), ('set_config_id', '=', question_set_id)], limit=1)
        view_id = self.env.ref(
            'kw_skill_assessment.kw_question_user_report_form_view').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_skill_answer_master',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'res_id': assessment_given.id,
            'target': 'self',
            'flags': {"toolbar": False}
        }

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        if 'set_config_id' and 'employee_ids' in self.env.context:
            employee_ids = tuple(self.env.context.get('employee_ids'))
            # if len(employee_ids) == 1:
            #     employee_ids_str = f"({employee_ids[0]})"
            # else:
            #     employee_ids_str = str(employee_ids)
            set_config_id = self.env.context.get('set_config_id')
            self.env.cr.execute(
                f""" CREATE or REPLACE VIEW {self._table} as (
                   select A.id as id,A.name as name, 
                    (select name from hr_job where id = A.job_id) as designation,
                    B.set_config_id as question_set_id,
                    coalesce(Cast(TO_CHAR((B.time_taken || 'second')::interval, 'HH24:MI:SS') as varchar), '00:00:00') as time_taken,
                    (select duration from kw_skill_question_set_config where id=B.set_config_id) as duration,
                    B.create_date as date,coalesce(B.status,'Not Given') as status,
                    B.total_mark_obtained as score,
                    Round(CAST(coalesce((cast(B.percentage_scored as float)), 0) as numeric)) as percentage
                    from hr_employee A 
                    left outer join kw_skill_answer_master B
                   on A.id = B.emp_rel and B.set_config_id = {set_config_id} where A.id in {employee_ids} )
                """
            )