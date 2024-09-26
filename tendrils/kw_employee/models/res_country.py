from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResCountry(models.Model):
    _inherit = 'res.country'

    kw_id = fields.Integer(string='Kw Id')
    active = fields.Boolean('Active', default=True)

    @api.constrains('name', )
    def validate_country(self):
        record = self.env['res.country'].search([]) - self
        for info in record:
            if info.name.lower() == str(self.name).lower():
                raise ValidationError("This Country \"" + self.name + "\" already exists.")