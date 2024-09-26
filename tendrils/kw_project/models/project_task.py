# -*- coding: utf-8 -*-

from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = "project.task"
    
    module_id = fields.Many2one("kw_project.module","Module")