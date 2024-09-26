from odoo import api, models,fields
from odoo.exceptions import UserError,ValidationError
from odoo import exceptions
from datetime import datetime

class PipAssessmentEmployee(models.Model):
    _name       ='assessment_pip_employee'
    _description= 'Performance Improvement Employee'


    emp_id = fields.Many2one('kw_feedback_assessment_pip')
    employee_name = fields.Many2one('hr.employee', 'Action Taken By', default=lambda self:  self.env.user.employee_ids)
    date = fields.Datetime('Date')
    comment = fields.Text('Comment')
    


   