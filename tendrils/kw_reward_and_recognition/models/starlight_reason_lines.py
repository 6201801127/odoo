from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StarlightReasonLines(models.Model):
    _name = 'starlight_reason_lines'
    _description = 'STARLIGHT REASONS & JUSTIFICATIONS'

    reason = fields.Char(string="Reason & Justification")
    rnr_id = fields.Many2one(comodel_name='reward_and_recognition')
    reason_type_id = fields.Many2one('starlight_reason_master', string='Reason Type')
