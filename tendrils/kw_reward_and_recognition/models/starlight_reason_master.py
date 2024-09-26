from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StarlightReasonMaster(models.Model):
    _name = 'starlight_reason_master'
    _description = 'STARLIGHT REASONS MASTER'

    sequence = fields.Char(string="S.No")
    name = fields.Char(string="Reason")
    active = fields.Boolean(string="Active", default=True)
    mendatory = fields.Boolean(string="Mandatory", default=True)

    @api.model
    def create(self, vals):
        vals['sequence'] = self.env['ir.sequence'].next_by_code('reason_master') or '/'
        result = super(StarlightReasonMaster, self).create(vals)
        return result
