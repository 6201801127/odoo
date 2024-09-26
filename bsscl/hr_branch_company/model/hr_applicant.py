from odoo import _, api, fields, models

class HRApplicant(models.Model):
    _inherit = 'hr.applicant'

    branch_id = fields.Many2one('res.branch', 'Branch', 
                                default=lambda self: self.env['res.users']._get_default_branch())
#   