# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AvgRateCalculation(models.Model):
    _name = 'kw_eq_avg_rate_calculation'
    _description = 'Averasge Rate configuration'

    percentage = fields.Integer('Percentage')
    effective_from = fields.Date(string="Effective Date")

    # @api.depends('write_date')
    # def compute_effective_date(self):
    #     for rec in self:
    #         rec.effective_from = rec.write_date.date()