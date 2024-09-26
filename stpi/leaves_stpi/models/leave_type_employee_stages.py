from odoo import models, fields, api,_

class LeaveTypeEmployeeStages(models.Model):
    _name = 'leave.type.employee.stage'
    _description = 'Leave Type employee stage Changes For STPI'
    _rec_name = 'name'
    
    name = fields.Char(string="Name")
    tech_name = fields.Selection([('test_period', 'Probation'),('contract', 'Contract'),('deputation', 'Deputation'),('employment', 'Regular')],string="Tech Name") 
