from odoo import models, fields, api
import re
from odoo.exceptions import ValidationError


class ResPartnerIn(models.Model):
    _inherit = "res.partner"

    is_announcement = fields.Boolean('Is Announcement User?', default=False)
