from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class ITInfraMaster(models.Model):
    _name = 'kw_eq_it_infra_master'
    _description = 'IT Infra Master'

    name = fields.Char()
    type = fields.Selection(string="Type",selection=[('purchase','Purchase'),('both', 'Purchase & Maintenance')])