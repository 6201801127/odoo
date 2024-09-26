from odoo import models, fields, api

class SBUProjectCategoryMaster(models.Model):
    _name = 'kw_sbu_project_category_master'
    _description = "SBU Project Category Master"
    _rec_name = "name"
    
    name = fields.Char('Category Name',required=True)
    code = fields.Char('Code')
    active = fields.Boolean(string='Active', default=True)
    
    @api.constrains('name')
    def check_name(self):
        exists_name = self.env['kw_sbu_project_category_master'].search([('name', '=', self.name), ('id', '!=', self.id)])
        if exists_name:
            raise ValueError("This Category Name \"" + self.name + "\" already exists.")