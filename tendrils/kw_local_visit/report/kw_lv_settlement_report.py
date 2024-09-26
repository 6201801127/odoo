# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, tools, _,SUPERUSER_ID
from odoo.exceptions import ValidationError,UserError
from lxml import etree

def lv_get_current_financial_dates():
    current_date = date.today()
    current_year = date.today().year
    if current_date < date(current_year, 4, 1):
        start_date = date(current_year-1, 4, 1)
        end_date = date(current_year, 3, 31)
    else:
        start_date = date(current_year, 4, 1)
        end_date = date(current_year+1, 3, 31)
    return start_date,end_date

start_date, end_date = lv_get_current_financial_dates()

class kw_lv_settlement_report(models.Model):
    _name = "kw_lv_settlement_report"
    _description = "Local visit settlement report"
    _auto = False
    _order = 'id desc'

    name = fields.Char(string='Employee Name')
    applied_on = fields.Date(string='Applied On')
    total_km = fields.Integer(string='Total K.M')
    price = fields.Integer(string='Price')
    payment_status = fields.Char(string="Status")
    mode = fields.Char(string="Payment Mode")
    payment_date = fields.Date(string='Payment Date')
    current_financial_year = fields.Boolean("current Financial Year",compute='_compute_current_financial_year',search="_lv_search_current_financial_year")
    branch_location = fields.Many2one('kw_res_branch')
    branch_country = fields.Many2one('res.country')
    
    @api.multi
    def _lv_search_current_financial_year(self, operator, value):
        return ['&', ('applied_on', '>=', start_date), ('applied_on', '<=', end_date)]

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (
            SELECT 
                kw_lv_settlement.id AS id,
                hr_employee.name AS name,
				hr_employee.base_branch_id AS branch_location,
                kw_lv_settlement.applied_date AS applied_on,
                kw_lv_settlement.total_km AS total_km,
                kw_lv_settlement.price AS price,
                kw_lv_stage_master.name AS payment_status,
                CASE
                   WHEN kw_lv_settlement.payment_date IS NULL THEN ''
                   ELSE
                       CASE
                           WHEN kw_lv_settlement.payment_mode = 'cash' THEN 'Cash'
                           WHEN kw_lv_settlement.payment_mode = 'ac' THEN 'Account Transfer'
                           ELSE ''
                           END
                   END AS mode,
                kw_lv_settlement.payment_date AS payment_date,
				br.country AS branch_country
            FROM kw_lv_settlement
            LEFT OUTER JOIN hr_employee ON
                kw_lv_settlement.emp_name = hr_employee.id
            LEFT OUTER JOIN kw_lv_stage_master ON
                kw_lv_settlement.stage_id = kw_lv_stage_master.id
			LEFT OUTER JOIN kw_res_branch br on hr_employee.base_branch_id = br.id
            ORDER BY id DESC
        )""" % (self._table))

    @api.multi
    def open_settlement_detail(self):
        settlement_record = self.env['kw_lv_settlement'].browse(self.id)
        if len(settlement_record):
            view_id = self.env.ref('kw_local_visit.kw_lv_settlement_apply_form').id
            return {
                    'name':'Settlement Detail',
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_lv_settlement',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id':self.id,
                    'view_id': view_id,
                    'target': 'same',
                    'flags': {'mode': 'readonly'},
                    }
        else:
            pass
