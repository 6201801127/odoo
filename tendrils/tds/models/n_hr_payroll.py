# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime, date, timedelta


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    tds_amount = fields.Integer(string='TDS', compute='_compute_tds')

    @api.depends('line_ids')
    def _compute_tds(self):
        for rec in self:
            for record in rec.line_ids:
                if record.code == 'TDS':
                    rec.tds_amount = record.total



