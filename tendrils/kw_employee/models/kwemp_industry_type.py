from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kwemp_industry(models.Model):
    _name = 'kwemp_industry'
    _description = "Industry Types"
    _order = "name"

    name = fields.Char(string="Industry Type", required=True,size=100)
    kw_id = fields.Integer(string='Tendrils ID')
    active = fields.Boolean('Active', default=True)
    @api.constrains('name', )
    def validate_industry_type(self):
        record = self.env['kwemp_industry'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("The industry type " + self.name + " already exists.")
        
    @api.model
    def create(self,vals):
        record = super(kwemp_industry, self).create(vals)
        if record:
            self.env.user.notify_success(message='Industry Type created successfully.')
        else:
            self.env.user.notify_danger(message='Industry Type creation failed.')
        return record
    
    @api.multi
    def write(self, vals):
        res = super(kwemp_industry, self).write(vals)
        if res:
            self.env.user.notify_success(message='Industry Type updated successfully.')
        else:
            self.env.user.notify_danger(message='Industry Type updation failed.')
        return res