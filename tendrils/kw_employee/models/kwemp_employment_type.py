from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


# Class For employment type
class kwemp_employment_type(models.Model):
    _name = 'kwemp_employment_type'
    _description = "A master model to create different employment types."

    name = fields.Char(string="Employment Type", required=True, size=100)
    code = fields.Char(string="Employment Code", required=True, size=50)
    kw_id = fields.Integer(string='Tendrils ID')
    active = fields.Boolean('Active', default=True)

    @api.constrains('code', 'name')
    def validate_employment(self):
        if re.match("^[a-zA-Z/\s\+-.()]+$", self.name) == None:
            raise ValidationError("Invalid employment type! Please provide a valid employment type.")
        if re.match("^[a-zA-Z0-9-]+$", self.code) == None:
            raise ValidationError("Invalid employment code! Please provide a valid employment code.")

        record = self.env['kwemp_employment_type'].search([]) - self
        for info in record:
            if info.code == self.code:
                raise ValidationError("The employment code \"" + self.code + "\" already exists.")
            if info.name.lower() == self.name.lower():
                raise ValidationError("The employment type \"" + self.name + "\" already exists.")

    @api.model
    def create(self, vals):
        record = super(kwemp_employment_type, self).create(vals)
        if record:
            self.env.user.notify_success(message='New Employee Type created successfully.')
        else:
            self.env.user.notify_danger(message='New Employee Type creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kwemp_employment_type, self).write(vals)
        if res:
            self.env.user.notify_success(message='Employee Type updated successfully.')
        else:
            self.env.user.notify_danger(message='Employee Type updation failed.')
        return res
