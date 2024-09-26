from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kwemp_religion_master(models.Model):
    _name = 'kwemp_religion_master'
    _description = "Religion Master"

    name = fields.Char(string="Religion", required=True,size=100)
    kw_id = fields.Integer(string='Tendrils ID')
    active = fields.Boolean('Active', default=True)
    @api.constrains('name', )
    def validate_religion(self):
        record = self.env['kwemp_religion_master'].search([]) - self
        for info in record:
            if info.name.lower() == str(self.name).lower():
                raise ValidationError("This Religion \"" + self.name + "\" already exists.")

    @api.model
    def create(self,vals):
        record = super(kwemp_religion_master, self).create(vals)
        if record:
            self.env.user.notify_success(message='New Religion created successfully.')
        else:
            self.env.user.notify_danger(message='New Religion creation failed.')
        return record
    
    @api.multi
    def write(self, vals):
        res = super(kwemp_religion_master, self).write(vals)
        if res:
            self.env.user.notify_success(message='Religion modes updated successfully.')
        else:
            self.env.user.notify_danger(message='Religion modes updation failed.')
        return res