
from odoo import _, api, models, fields
from odoo.exceptions import ValidationError

class IrModelField(models.Model):
    
    _inherit = 'ir.model.fields'

    ttype = fields.Selection(selection_add=[('file', 'file')])