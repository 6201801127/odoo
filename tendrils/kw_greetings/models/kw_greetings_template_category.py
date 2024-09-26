from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_greetings_category(models.Model):
    _name = 'kw_greetings_category'
    _description = "Greetings category."

    name = fields.Char(string="Category Name", required=True, size=100)

    @api.constrains('name')
    def _validate_name(self):
        record = self.env['kw_greetings_category'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("The category " + self.name + " already exists.")

    @api.model
    def create(self, vals):
        new_record = super(kw_greetings_category, self).create(vals)
        self.env.user.notify_success(message='Wish category created sucessfully')
        return new_record

    @api.multi
    def write(self, vals):
        res = super(kw_greetings_category, self).write(vals)
        self.env.user.notify_success(message='Wish category updated sucessfully')
        return res
