# *******************************************************************************************************************
#  File Name             :   kw_emp_month_wise_report.py
#  Description           :   This model is used to filter employee status details month wise
#  Created by            :   Monalisha rout
#  Created On            :   02-11-2023
#  Modified by           :   Monalisha Rout
#  Modified On           :   
#  Modification History  :  
# *******************************************************************************************************************

from odoo import fields, models, api, tools
from datetime import date, datetime, time
import calendar

class ParentDetails(models.Model):
    _name = 'kw_employee_parent_details'
    _description = 'Parent Details'
    _auto = False

    emp_code = fields.Char()
    employee_id = fields.Many2one('hr.employee')
    name = fields.Char(related='employee_id.name')
    direct_reporting = fields.Integer()
    indirect_reporting = fields.Integer(compute='_compute_indirect_reporting_count')
    department_id = fields.Many2one('hr.department')
    grade_id = fields.Many2one('kwemp_grade_master', string='Grade')
    job_id = fields.Many2one('hr.job')
    total_repotees = fields.Integer(compute='_compute_indirect_reporting_count')
    grade_band = fields.Char(compute='_compute_grade_band')
    emp_band = fields.Many2one(string=u'Band', comodel_name='kwemp_band_master')

    
    @api.depends('employee_id','direct_reporting')
    def _compute_indirect_reporting_count(self):
        for rec in self:
            emp = self.env['hr.employee'].search([('id','child_of',rec.employee_id.child_ids.ids)])
            rec.indirect_reporting = len(emp) - rec.direct_reporting if len(emp) > 1 else 0
            rec.total_repotees = len(emp)
            
    @api.depends('grade_id','emp_band')
    def _compute_grade_band(self):
        for rec in self:
            if rec.grade_id:
                rec.grade_band = f"{rec.grade_id.name}{'-' if rec.emp_band else ''}{rec.emp_band.name[5:] if rec.emp_band and len(rec.emp_band.name) > 5 else ''}"


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f"""
            CREATE or REPLACE VIEW {self._table} as (
            select row_number() over(order by hr.name) as id,
            hr.id as employee_id,
            hr.emp_code,
            hr.department_id as department_id,
            hr.emp_band as emp_band,
            hr.grade as grade_id,
            hr.job_id as job_id,
            (select count(b.id) from hr_employee b where b.parent_id = hr.id and b.active=true) as direct_reporting from 
            hr_employee AS hr 
            where active=true
            )"""
        
        self.env.cr.execute(query)
