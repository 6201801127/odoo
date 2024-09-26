# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class ZoomEventLog(models.Model):
    _name = 'kw_zoom_event_log'
    _description = 'Zoom Event Log'
    _order = "create_date desc"

    payload = fields.Text(string='Payload')
    event = fields.Char(string='Event')
