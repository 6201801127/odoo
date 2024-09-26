# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime

from odoo import api, fields, models
from odoo.http import request
import json, requests
from base64 import b64encode
from odoo.exceptions import UserError, ValidationError, Warning


class Company(models.Model):
    _inherit = 'res.company'

    google_client_id = fields.Char('Client ID')
    google_client_secret = fields.Char('Client Secret')
    google_redirect_url = fields.Char('Redirect URL')
    
