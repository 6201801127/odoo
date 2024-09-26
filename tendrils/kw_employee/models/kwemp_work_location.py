from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kwemp_work_location(models.Model):
    _name = 'kwemp_work_location'
    _description = "A master model for the work location of employees."

    name = fields.Char(string=u'Location Name', required=True, size=100)
    kw_id = fields.Integer(string='Tendrils ID')
