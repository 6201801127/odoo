# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class KwAppraisalPageWiseReport(models.Model):
    _name           = "kw_appraisal_page_wise_report"
    _description    = "Appraisal page wise report"
    _auto           = False

    name            = fields.Char(string='Employee',) 
    emp_code        = fields.Char(string='Employee Code')
    job_title       = fields.Char(string='Designation')
    page_name       = fields.Char(string='Page Name')
    avg_mark        = fields.Char(string='Average Mark')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (
            select row_number() over(order by j.id, e.name, p.id) as id,emp_code as emp_code, e.name as name, j.name as job_title, p.title as page_name, avgmark as avg_mark from 
                (
                    select emp_id, page_id, avg(quizz_mark) as avgmark
                    from hr_appraisal a
                    join survey_user_input i on i.appraisal_id=a.id and i.id=a.lm_input_id and i.state='done'
                    join survey_user_input_line il on il.user_input_id=i.id
                    join survey_question q on q.id=il.question_id
                    group by emp_id, page_id
                ) m
                join hr_employee e on e.id=m.emp_id
                join hr_job j on j.id=e.job_id
                join survey_page p on p.id=m.page_id
                order by id

        )""" % (self._table))


   