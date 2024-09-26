from odoo import models, fields,api
from odoo.exceptions import ValidationError

class kw_user_type_master(models.Model):
    _name='kw_user_type_master'
    _description="User Type Master"
    _rec_name='user_type'

    user_type = fields.Char(string='Type')