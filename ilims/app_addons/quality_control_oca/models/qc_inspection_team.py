from odoo import _, api, exceptions, fields, models
from odoo.exceptions import ValidationError


class QcInspectionTeam(models.Model):
    _name = "qc.inspection.team"
    _description = "Quality control Inspection Team"

    name = fields.Char('Name')
    team_ids = fields.Many2many('res.partner', string='Team')
