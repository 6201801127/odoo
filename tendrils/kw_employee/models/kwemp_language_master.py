from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class kwemp_language_master(models.Model):
    _name = 'kwemp_language_master'
    _description = "A master model to create different languages."

    name = fields.Char(string="Language Name", required=True, size=100)
    kw_id = fields.Integer(string='Tendrils ID')
    active = fields.Boolean('Active', default=True)

    @api.constrains('name', )
    def validate_language(self):
        if re.match("^[a-zA-Z0-9 ,./()_-]+$", self.name) == None:
            raise ValidationError("Invalid language! Please provide a valid language name.")
        record = self.env['kwemp_language_master'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("The language name \"" + self.name + "\" already exists.")

    @api.model
    def create(self, vals):
        record = super(kwemp_language_master, self).create(vals)
        if record:
            self.env.user.notify_success(message='New Language created successfully.')
        else:
            self.env.user.notify_danger(message='New Language creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kwemp_language_master, self).write(vals)
        if res:
            self.env.user.notify_success(message='Language updated successfully.')
        else:
            self.env.user.notify_danger(message='Language updation failed.')
        return res
    #    For course details