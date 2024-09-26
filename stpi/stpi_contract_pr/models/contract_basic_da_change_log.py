# -*- coding: utf-8 -*-
from odoo import fields, models, api

class ContractBasicDaChangeLog(models.Model):
    _name = 'contract_basic_da_change_log'
    _description = 'BASIC,DA change log by effective from'

    date = fields.Date("Effective From")
    wage = fields.Float('Basic/Consolidated', digits=(16, 2), required=True)
    contract_id = fields.Many2one("hr.contract","Contract")
    da = fields.Float("DA Percentage")
    basic_da = fields.Float("Basic + DA")

    related_month_str = fields.Char("Related Month",compute="calculate_month_year",store=True)
    related_month_int = fields.Char("Related Month(Integer)",compute="calculate_month_year",store=True)

    related_year_int = fields.Char("Related Year",compute="calculate_month_year",store=True)

    @api.depends("date")
    def calculate_month_year(self):
        for log in self:
            if log.date:
                log.related_month_str = log.date.strftime("%B")
                log.related_month_int = log.date.month 
                log.related_year_int = log.date.year
            else:
                log.related_month_str = False
                log.related_month_int = False
                log.related_year_int = False