from odoo import models, fields, api

class bsap_grievance_master(models.Model):
    _name        = 'bsscl.grievance.type'
    _description = 'A model to manage grievance categories'
    _rec_name    = 'name'
    
    name = fields.Char(string="Name/(नाम)", required=True)
    code = fields.Char(string="Code(कोड)", required=True)
    # department_id = fields.Many2one('hr.department',string="Concerned Section(संबंधित अनुभाग)",domain="[('dept_type.code','=','section')]")