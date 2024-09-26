from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


# For Role
class kw_role_name(models.Model):
    _name = 'kwmaster_role_name'
    _description = "A master model to create different employee roles."
    _order = "name asc"

    name = fields.Char(string="Name", required=True, size=100)
    code = fields.Char(string="Code")
    category_ids = fields.One2many('kwmaster_category_name', 'role_ids')
    kw_id = fields.Integer(string='Tendrils ID')
    active = fields.Boolean('Active', default=True)
    budget_type = fields.Selection(string='Budget', selection=[('treasury', 'Treasury'), ('project', 'Project')],
                                    help="Set recruitment process is employee budget.")

    @api.constrains('name')
    def validate_details(self):
        if re.match("^[0-9a-zA-Z/\s\+-.()]+$", self.name) == None:
            raise ValidationError("Invalid role! Please provide a valid role.")
        record = self.env['kwmaster_role_name'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("The role \"" + self.name + "\" already exists.")

    @api.model
    def create(self, vals):
        record = super(kw_role_name, self).create(vals)
        if record:
            self.env.user.notify_success(message='New Employee role created successfully.')
        else:
            self.env.user.notify_danger(message='New Employee role creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kw_role_name, self).write(vals)
        if res:
            self.env.user.notify_success(message='Employee role updated successfully.')
        else:
            self.env.user.notify_danger(message='Employee role updation failed.')
        return res
