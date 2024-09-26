# -*- coding: utf-8 -*-
from odoo import models, fields, api


class kw_generated_otp_in(models.Model):
    _inherit = "kw_generate_otp"

    user = fields.Char(string="User Name")
