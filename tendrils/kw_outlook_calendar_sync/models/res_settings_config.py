# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime

from odoo import api, fields, models
from odoo.http import request
import json, requests
from base64 import b64encode
from odoo.exceptions import UserError, ValidationError, Warning


class OutlookIntegration(models.TransientModel):
    _inherit = 'res.config.settings'

    outlook_client_id = fields.Char('Client ID')
    outlook_client_secret = fields.Char('Client Secret')
    outlook_redirect_url = fields.Char('Redirect URL')
    
