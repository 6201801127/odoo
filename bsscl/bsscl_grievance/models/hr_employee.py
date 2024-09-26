from odoo import models, fields, api,_

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    
   
        
    current_office_id  = fields.Many2one('res.branch', string="Current Office")
   