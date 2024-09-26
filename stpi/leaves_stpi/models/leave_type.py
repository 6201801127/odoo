from odoo import models, fields, api,_

class LeaveType(models.Model):
    _name = 'leave.type'
    _description = 'Leave Type Changes For STPI'
    _rec_name = 'name'
    
    name = fields.Char(string="Name")
    
    
