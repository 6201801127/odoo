# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from odoo import models, fields, api


class kw_appraisal(models.Model):
    _name = 'kw_assessment_period_master'
    _description = 'Employee Appraisal'
    _rec_name = 'assessment_period'

    def _default_financial_yr(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        return current_fiscal

    assessment_period = fields.Char(string="Assessment Period", required=True)
    fiscal_year_id = fields.Many2one('account.fiscalyear', 'Financial Year',default=_default_financial_yr,required=True, track_visibility='always')


    @api.constrains('assessment_period')
    def check_period(self):
        exists_name = self.env['kw_assessment_period_master'].search(
            [('assessment_period', '=', self.assessment_period), ('id', '!=', self.id)])
        if exists_name:
            raise ValueError("The Appraisal period" + '"'+self.assessment_period + '"' + " already exists.")