# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class Employee(models.Model):
    _inherit = 'hr.employee'

    zoom_email = fields.Char(string='Zoom Email')
