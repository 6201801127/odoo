from odoo import tools
from odoo import models, fields, api
from datetime import datetime,date
from odoo.addons import decimal_precision as dp


class ResourceServingNoticePeriodReport(models.Model):
    _name           = "notice_period_resource_report"
    _description  = "Resource serving notice period report"
    _order="apply_date desc"
    _auto             = False

    # def get_row(self):
    #     count=0
    #     for record in self:
    #         record.sl_no = count + 1
    #         count = count + 1
    @api.depends('grade','band')
    def _compute_grade_band(self):
        for rec in self:
            if rec.band and rec.grade:
                rec.grade_band =rec.grade.name +','+' '+ rec.band.name

    name= fields.Char(string='Employee Name')
    job_id=fields.Many2one('hr.job',string='Position')
    base_branch_id=fields.Many2one('kw_res_branch',string='Base Location')
    date_of_joining=fields.Date("Date of Joining")
    emp_role= fields.Many2one('kwmaster_role_name',string="Employee Role")
    emp_category= fields.Many2one('kwmaster_category_name',string="Employee Category")
    apply_date=fields.Date("Apply Date")
    last_working_date=fields.Date("Last Working Date")
    grade= fields.Many2one('kwemp_grade_master',string="Employee Grade")
    band= fields.Many2one('kwemp_band_master',string="Employee Band")
    grade_band=fields.Char("Grade/Band",compute='_compute_grade_band')
    # sl_no=fields.Integer("SL#",compute="get_row")
    lm = fields.Many2one('hr.employee')
    lm_name = fields.Char(string="LM",related="lm.name")
    emp_ulm = fields.Char(string="ULM",related="lm.parent_id.name")


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (
         select row_number() over() as id,
            hr.name as name,
			hr.grade as grade,
			hr.emp_band as band,
            hr.job_id as job_id,
			hr.base_branch_id as base_branch_id,
            hr.date_of_joining as date_of_joining,
            hr.emp_role as emp_role,
            hr.emp_category as emp_category,
			rl.effective_form as apply_date,
			rl.last_working_date as last_working_date,
            hr.parent_id as lm
            from hr_employee as hr
            join kw_resignation as rl on hr.id=rl.applicant_id
            where rl.state not in ('reject','cancel') and hr.active=true
          
        )""" % (self._table))



    
  
   