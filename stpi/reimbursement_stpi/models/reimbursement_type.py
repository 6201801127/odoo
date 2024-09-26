from odoo import api, fields, models
# from odoo.exceptions import ValidationError,UserError

class ReimbursementType(models.Model):

    _name = "reimbursement.type"
    _description = "Reimbursement Type"
    
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    name = fields.Char("Reimbursement Type",required=True,track_visibility='always')
    code = fields.Char("Code",required=True,track_visibility='always')
    active = fields.Boolean("Active",default=True)