from odoo import models,fields,api
from odoo import tools


class FinancialYearWiseTrainingReport(models.Model):
    _name = "financial_year_wise_training_report"
    _description = "Training Plan"
    _auto = False
    _order="fiscal_year asc,training_id desc"
  


    fiscal_year = fields.Many2one('account.fiscalyear',"Financial Year")
    training_id = fields.Many2one('kw_training',"Training")
    participant_id = fields.Many2one('hr.employee',string="Participants")
    desgignation = fields.Many2one('hr.job',"Designation",related='participant_id.job_id')
    course_id = fields.Many2one('kw_skill_master',related='training_id.course_id',string="Course")



    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            select row_number() over() as id, a.financial_year as fiscal_year,
            a.training_id as training_id,
            b.hr_employee_id as participant_id 
            from kw_training_plan as a 
            join hr_employee_kw_training_plan_rel as b
            on a.id = b.kw_training_plan_id
            where a.state='approved'
           
        )"""
        self.env.cr.execute(query)