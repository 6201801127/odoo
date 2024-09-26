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


class kw_lv_apply_report(models.Model):
    _name           = "kw_lv_apply_report"
    _description    = "Local visit apply report"
    _auto           = False
    _order          = 'id desc'    

    @api.model
    def _get_time_list(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=7, minute=45, second=0, microsecond=0)
        end_loop = dt.replace(hour=22, minute=0, second=0, microsecond=0)
        time_list = []
        while start_loop < end_loop:
            start_loop = (start_loop+relativedelta(minutes=+15))
            time_list.append((start_loop.strftime('%H:%M'),
                              start_loop.strftime('%I:%M %p')))
        return time_list
    
    @api.model
    def _get_time_list_without_relativedelta(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=7, minute=0, second=0, microsecond=0)
        end_loop = dt.replace(hour=23, minute=0, second=0, microsecond=0)
        time_list = []
        while start_loop < end_loop:
            start_loop = (start_loop+relativedelta(minutes=+1))
            time_list.append((start_loop.strftime('%H:%M'),
                              start_loop.strftime('%I:%M %p')))
        return time_list

    emp_name = fields.Char(string='Employee Name') 
    category_name = fields.Char(string='Category Name')
    vehicle_type = fields.Char(string='Vehicle Type')
    visit_date = fields.Date(string='Visit Date')
    expected_in_time = fields.Selection(string='Expected In Time',selection='_get_time_list')
    out_time = fields.Selection(string='Out Time',selection='_get_time_list_without_relativedelta')
    in_time = fields.Selection(string='In Time',selection='_get_time_list_without_relativedelta')
    total_km = fields.Integer(string='Total KM')
    price = fields.Float(string='Price')
    lv_status = fields.Char(string='Status')
    current_financial_year = fields.Boolean("current Financial Year",compute='_compute_current_financial_year',search="_lv_search_current_financial_year")
    branch_location = fields.Many2one('kw_res_branch')
    branch_country = fields.Many2one('res.country')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (
            select a.id as id, e.name as emp_name,e.base_branch_id AS branch_location, c.category_name as category_name, CASE
                WHEN vehicle_category_name IS NULL AND a.parent_lv_id IS NULL THEN 'Own'
                WHEN a.parent_lv_id IS NOT NULL THEN (
                    SELECT kw_lv_vehicle_category_master.vehicle_category_name
                    FROM kw_lv_apply
                            LEFT JOIN kw_lv_vehicle_category_master ON
                        kw_lv_vehicle_category_master.id = kw_lv_apply.vehicle_type
                    WHERE kw_lv_apply.id = a.parent_lv_id
                )
                ELSE vehicle_category_name END AS vehicle_type, 
           visit_date as visit_date, expected_in_time as expected_in_time, out_time as out_time, actual_in_time as in_time, a.total_km as total_km, a.price as price,
                status, a.state, settlement_state, payment_state,
                kw_lv_stage_master.name AS lv_status,
				kw_res_branch.country AS branch_country
                from kw_lv_apply a
                join hr_employee e on e.id=a.emp_name
                join kw_lv_category_master c on c.id=a.visit_category
                left join kw_lv_vehicle_category_master vcm on vcm.id=a.vehicle_type
                left join kw_lv_apply_and_lv_settlement lvs on lvs.kw_lv_apply_id=a.id
                left join kw_lv_settlement s on s.id=lvs.kw_lv_settlement_id
                LEFT OUTER JOIN kw_lv_stage_master ON
                    a.stage_id = kw_lv_stage_master.id
				LEFT JOIN kw_res_branch ON 
					e.base_branch_id = kw_res_branch.id
                where status is not null
                order by id desc
        )""" % (self._table))
    
    def view_lv_details(self):
        result_id = self.env['kw_lv_apply'].browse(self.id)
        view_id = self.env.ref('kw_local_visit.kw_lv_view_form').id
        if len(result_id):
            return {
                    'name':'Local Visit Details',
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_lv_apply',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id':result_id.id,
                    'view_id': view_id,
                    'target': 'same',
                    'flags': {'mode': 'readonly'},
                    }
        else:
            pass

    
    @api.multi
    def _lv_search_current_financial_year(self, operator, value):
        return ['&', ('visit_date', '>=', start_date), ('visit_date', '<=', end_date)]



   