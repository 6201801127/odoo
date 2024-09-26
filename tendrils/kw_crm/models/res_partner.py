from odoo import models, fields, api


class Partner(models.Model):
    _inherit = "res.partner"

    competitor = fields.Boolean(string="Competitor", default=False)
    qc = fields.Char(string="Quality Certificate")
