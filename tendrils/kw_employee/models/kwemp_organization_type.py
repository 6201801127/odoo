from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kwemp_organization(models.Model):
    _name = 'kwemp_organization'
    _description = "Organization Types"
    _order = "name"

    name = fields.Char(string="Organization Type", required=True, size=100)
    kw_id = fields.Integer(string='Tendrils ID')
    active = fields.Boolean('Active', default=True)

    @api.constrains('name', )
    def validate_organization_type(self):
        record = self.env['kwemp_organization'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("The organization type " + self.name + " already exists.")

    @api.model
    def create(self,vals):
        record = super(kwemp_organization, self).create(vals)
        if record:
            self.env.user.notify_success(message='Organization Types created successfully.')
        else:
            self.env.user.notify_danger(message='Organization Types creation failed.')
        return record
    
    @api.multi
    def write(self, vals):
        res = super(kwemp_organization, self).write(vals)
        if res:
            self.env.user.notify_success(message='Organization Types updated successfully.')
        else:
            self.env.user.notify_danger(message='Organization Types updation failed.')
        return res