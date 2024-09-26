from datetime import date
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AfterLoginConfiguration(models.Model):
    _name = 'login_activity_configuration'
    _description = "Login activity"

    view_name_id = fields.Char(string="View Name")
    view_name_code = fields.Char(string="Code")
    multi_company_ids = fields.Many2many('res.company', 'company_login_activity_rel', 'view_login_id',
                                         'company_login_id', string="Company Name")
