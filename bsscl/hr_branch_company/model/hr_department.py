from odoo import _, api, fields, models

class HRDepartment(models.Model):
    _inherit = 'hr.department'

    branch_id = fields.Many2one('res.branch', 'Branch')