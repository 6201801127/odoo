from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kwemp_maritial_master(models.Model):
    _name = 'kwemp_maritial_master'
    _description = "Marital Status"

    kw_id = fields.Integer(string='Tendrils ID')
    name = fields.Char(string="Marital Status", required=True,size=100)
    code = fields.Char(string="Code", required=True,size=5)
    active = fields.Boolean('Active', default=True)

    @api.constrains('name', )
    def validate_maritial(self):
        record = self.env['kwemp_maritial_master'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("The Marital Status " + self.name + " already exists.")

    @api.model
    def create(self,vals):
        record = super(kwemp_maritial_master, self).create(vals)
        if record:
            self.env.user.notify_success(message='Marital Status created successfully.')
        else:
            self.env.user.notify_danger(message='Marital Status creation failed.')
        return record
    
    @api.multi
    def write(self, vals):
        res = super(kwemp_maritial_master, self).write(vals)
        if res:
            self.env.user.notify_success(message='Marital Status updated successfully.')
        else:
            self.env.user.notify_danger(message='Marital Status updation failed.')
        return res