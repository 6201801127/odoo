from odoo import models, fields, api


class kw_project_inherit(models.Model):
    _inherit = "project.project"

    prject_category_id = fields.Many2many('kw_project_category_master', string='Category Name')
