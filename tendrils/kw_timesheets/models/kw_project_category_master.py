from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError


class kw_project_category_master(models.Model):
    _name = 'kw_project_category_master'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Category master for project'
    
    name = fields.Char(string="Category Name", required=True, track_visibility='always')
    mapped_to = fields.Selection(
        [('Project', 'Project'), ('Opportunity', 'Opportunity/Work Order'), ('Support', 'Administrative Activities')],
        string='Mapped to', default='Opportunity', track_visibility='always')
    kw_id = fields.Integer(string="KW ID")
    active = fields.Boolean('Status', default=True, track_visibility='always')
    code = fields.Char(string="Code")

    @api.model
    def onchangeProjectCategory(self, **args):
        category_id = args.get('category_id', False)

        project_ids = []
        category = self.sudo().browse(int(category_id))
        if category.mapped_to == 'Project':
            project_ids = self.env['project.project'].sudo().search_read(
                [('prject_category_id', '=', int(category_id))], ['id', 'name'])

        elif category.mapped_to == 'Opportunity':
            project_ids = self.env['crm.lead'].sudo().search_read([], ['id', 'name'])

        return [project_ids]

    @api.model
    def onchangeProject(self, **args):
        project_id = args.get('project_id', False)
        project_task_ids = self.env['project.task'].sudo().search_read([('project_id', '=', int(project_id))], ['id', 'name'])

        return [project_task_ids]
