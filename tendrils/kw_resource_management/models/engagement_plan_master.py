
from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError


class EngagementPlan(models.Model):
    _name = 'kw_engagement_master'
    _description = 'Engagement Master'
    

    name = fields.Char()
    active = fields.Boolean(string="Active") 
    code = fields.Char('Code')


    
    @api.constrains('name')
    def _check_name_duplicate_validation(self):
        for rec in self:
            Engagement_master_data = self.env['kw_engagement_master'].search([('name','ilike',rec.name),('id', '!=', rec.id)])
            if Engagement_master_data:
                raise ValidationError('This name is alredy Exist for Engagement Plan') 
        