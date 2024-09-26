from odoo import fields, models

class Project(models.Model):
    _inherit = "project.project"

    sbu_id = fields.Many2one('kw_sbu_master', related="emp_id.sbu_master_id",string="SBU",store=True)