from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class kwemp_reference_mode_master(models.Model):
    _name = 'kwemp_reference_mode_master'
    _description = "A master model to save the reference modes."

    name = fields.Char(string="Reference Mode", required=True, size=100)
    kw_id = fields.Integer(string='Tendrils ID')
    active = fields.Boolean('Active', default=True)

    @api.constrains('name', )
    def validate_reference_mode(self):
        if re.match("^[a-zA-Z/\s\+-.()]+$", self.name) == None:
            raise ValidationError("Invalid reference mode! Please provide a valid reference mode.")
        record = self.env['kwemp_reference_mode_master'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("This reference mode \"" + self.name + "\" already exists.")

    @api.model
    def create(self, vals):
        record = super(kwemp_reference_mode_master, self).create(vals)
        if record:
            self.env.user.notify_success(message='New Reference modes created successfully.')
        else:
            self.env.user.notify_danger(message='New Reference modes creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kwemp_reference_mode_master, self).write(vals)
        if res:
            self.env.user.notify_success(message='Reference modes updated successfully.')
        else:
            self.env.user.notify_danger(message='Reference modes updation failed.')
        return res
