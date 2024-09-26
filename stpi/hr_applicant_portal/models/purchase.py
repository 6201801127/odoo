# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.http import request


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _compute_access_url(self):
        for purchase in self:
            purchase.access_url = '/my/purchase/qoute/%s' % (purchase.id)

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s' % (self.name)

    access_url = fields.Char('Portal Access URL', compute='_compute_access_url', help='Purchase Order Portal URL')
