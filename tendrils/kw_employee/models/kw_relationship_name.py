from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

"""# For family"""


class kw_relationship_name(models.Model):
    _name = 'kwmaster_relationship_name'
    _description = "A master model to create family relationships."
    _order = "sequence"

    name = fields.Char(string="Name", required=True, size=100)
    relation_id = fields.One2many('kwemp_family_info', 'relationship_id')
    kw_id = fields.Integer(string='Tendrils ID')
    is_insure_covered = fields.Boolean('Is covered by Insurance ?')
    insurance_amount = fields.Integer(string="Premium Amount")
    gender = fields.Selection(string="Gender", selection=[('M', 'Male'), ('F', 'Female')], required=False)
    sequence = fields.Integer(required=True, index=True, default=5)
    active = fields.Boolean('Active', default=True)

    @api.constrains('name')
    def validate_relationship(self):
        if re.match("^[0-9a-zA-Z/\s\+-.()]+$", self.name) == None:
            raise ValidationError("Invalid relationship! Please provide a valid relationship.")
        record = self.env['kwmaster_relationship_name'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("The relationship \"" + self.name + "\" already exists.")

    @api.model
    def create(self, vals):
        record = super(kw_relationship_name, self).create(vals)
        if record:
            self.env.user.notify_success(message='New Relation created successfully.')
        else:
            self.env.user.notify_danger(message='New Relation creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kw_relationship_name, self).write(vals)
        if res:
            self.env.user.notify_success(message='Relation updated successfully.')
        else:
            self.env.user.notify_danger(message='Relation updation failed.')
        return res
