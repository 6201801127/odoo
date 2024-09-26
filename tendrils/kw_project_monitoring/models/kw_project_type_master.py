from odoo import models, fields, api
from datetime import date, datetime, time

class KWlifecyclemaster(models.Model):
    _name = 'kw_project_type_master'
    _rec_name = 'project_type'

    project_type = fields.Char(string="Project Type",required=True)
    
    
    
class ProjectTaskemaster(models.Model):
    _name = 'kw_project_module_master'
    _rec_name = 'name'

    name = fields.Char("Module Name",required=True)
    project_id = fields.Many2one("project.project","Project",required=True,ondelete="cascade")
    description = fields.Text("Description",required=True)
    existing_modules = fields.Text("Existing Modules", readonly=True, compute="_compute_existing_modules")
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Module Name already exist.'),
    ]

    
    @api.depends('project_id')
    def _compute_existing_modules(self):
        for record in self:
            if record.project_id:
                module_records = self.search([('project_id', '=', record.project_id.id)])
                module_names = module_records.mapped('name')
                record.existing_modules = ', '.join(module_names)
            else:
                record.existing_modules = ''
    
class ProjectRiskCategory(models.Model):
    _name = 'project_risk_category'

    name = fields.Char("Risk Name",required=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name already exist.'),
    ]

