from odoo import _, api, fields, models

class HRJob(models.Model):
    _inherit = 'hr.job'

    branch_id = fields.Many2one('res.branch', 'Branch')