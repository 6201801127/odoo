from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kwemp_blood_group_master(models.Model):
    _name = 'kwemp_blood_group_master'
    _description = "Blood Groups"

    name = fields.Char(string="Blood group", required=True,size=3)
    kw_id = fields.Integer(string='Tendrils ID')
    active = fields.Boolean('Active', default=True)

    @api.constrains('name', )
    def validate_bloodgroup(self):
        record = self.env['kwemp_blood_group_master'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("This blood group " + self.name + " already exists.")
    @api.model
    def create(self,vals):
        record = super(kwemp_blood_group_master, self).create(vals)
        if record:
            self.env.user.notify_success(message='Blood group created successfully.')
        else:
            self.env.user.notify_danger(message='Blood group creation failed.')
        return record
    
    @api.multi
    def write(self, vals):
        res = super(kwemp_blood_group_master, self).write(vals)
        if res:
            self.env.user.notify_success(message='Blood group updated successfully.')
        else:
            self.env.user.notify_danger(message='Blood group updation failed.')
        return res
