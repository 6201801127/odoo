from odoo import models, fields, api,_

class LeaveEmployeeType(models.Model):
    _name = 'leave.employee.type'
    _description = 'Leave Employee Type Changes For STPI'
    _rec_name = 'name'
    
    name = fields.Char(string="Name")
    tech_name = fields.Selection([
                                ('regular','Regular Employee'),
                                 ('contractual_with_agency','Contractual with Agency'),
                                 ('contractual_with_stpi','Contractual with STPI')
                                ],string="Tech Name")
