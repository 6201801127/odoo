# -*- coding: utf-8 -*-

from odoo import models,fields


class ProjectModule(models.Model):
    _name = "kw_project.module"
    _description = "Project Modules"
    
    name = fields.Char("Module Name",required=True)
    project_id = fields.Many2one("project.project","Project",required=True,ondelete="cascade")
    task_ids = fields.One2many('project.task', 'module_id', string='Tasks')
    last_sync_date = fields.Date("Last Sync Date", readonly=True)
    kw_id = fields.Integer("Tendrils ID")