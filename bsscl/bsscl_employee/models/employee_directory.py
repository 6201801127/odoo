import base64, re
from datetime import datetime,date,timedelta
from odoo import models, fields, api, _
from odoo import tools
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource


class EmployeeAddress(models.Model):
    _inherit = 'hr.employee.public'
    _description = 'hr employee public'


    salutation = fields.Many2one('res.partner.title', track_visibility='always')
    # employee_type = fields.Many2one('employee.type', string='Employment Type',
    #                                  track_visibility='always', store=True)
    employee_type = fields.Selection([('regular', 'Regular Employee'),
                                      ('contractual_with_agency', 'Contractual with Agency'),
                                      ('contractual_with_bsscl', 'Contractual with BSSCL')], string='Employment Type',
                                      tracking=True, store=True)
    identify_id = fields.Char(string='Identification No.',copy=False, store=True, track_visibility='always')
    recruitment_type = fields.Selection([
        ('d_recruitment', 'Direct Recruitment(DR)'),
        ('transfer', 'Transfer(Absorption)'),
        ('i_absorption', 'Immediate Absorption'),
        ('deputation', 'Deputation'),
        ('c_appointment', 'Compassionate Appointment'),
        ('promotion', 'Promotion'),
    ], 'Recruitment Type', track_visibility='always', store=True)
    
    ex_serviceman =fields.Selection([('no','No'),
                                     ('yes','Yes')],string='Whether Ex Service Man',track_visibility='always')
    transfer_date = fields.Date('Joining Date')
    first_name = fields.Char(string="First Name / प्रथम नाम")
    middle_name = fields.Char(string="Middle Name / मध्य नाम")

    last_name  = fields.Char(string="Last Name / उपनाम")
    job_id = fields.Many2one('hr.job', track_visibility='onchange', string="Post")
