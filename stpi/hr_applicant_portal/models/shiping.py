# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.http import request


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _compute_access_url(self):
        for move in self:
            move.access_url = '/my/shiping/%s' % (move.id)

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s' % (self.name)

    access_url = fields.Char('Portal Access URL', compute='_compute_access_url', help='Stock Order Portal URL')
