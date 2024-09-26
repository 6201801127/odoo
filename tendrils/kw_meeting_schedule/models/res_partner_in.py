from odoo import models, fields, api
import re
from odoo.exceptions import ValidationError


class ResPartnerIn(models.Model):
    _inherit = "res.partner"

    is_meeting_participant = fields.Boolean('Added to Meeting', default=False)
