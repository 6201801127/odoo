from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class AccessMaster(models.Model):
    _name = 'kw_eq_master_data'
    _description = 'Access Master'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")