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

class kw_lv_business_report(models.Model):
    _name = "kw_lv_business_report"
    _description = "Local visit business report"
    _auto = False

    employee_name = fields.Char(string='Employee Name')
    visit_date = fields.Date(string='Visit Date')
    activity_name = fields.Char(string='Activity Name')
    sub_category_name = fields.Char(string='Sub Category Name')
    work_opportunity = fields.Char(string="Work/Opportunity")
    order_type = fields.Char(string="Order Type")
    price = fields.Integer(string='Price', compute='get_price')
    current_financial_year = fields.Boolean("current Financial Year",compute='_compute_current_financial_year',search="_lv_search_current_financial_year")
    branch_location = fields.Many2one('kw_res_branch')
    branch_country = fields.Many2one('res.country')
    @api.multi
    def _lv_search_current_financial_year(self, operator, value):
        return ['&', ('visit_date', '>=', start_date), ('visit_date', '<=', end_date)]
    

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (
		SELECT 
                kw_lv_business.id AS id, 
				hr_employee.base_branch_id AS branch_location,
				kw_res_branch.country AS branch_country,
                hr_employee.name AS employee_name, 
                kw_lv_apply.visit_date AS visit_date, 
                kw_lv_activity_master.name AS activity_name, 
                kw_lv_sub_category_master.sub_category_name AS sub_category_name, 
                crm_lead.name AS work_opportunity, 
                CASE crm_stage.sequence
                    WHEN 3 THEN 'Opportunity'
                    WHEN 70 THEN 'Work Order'
                END AS order_type
                FROM hr_employee
                INNER JOIN kw_lv_apply ON
                    hr_employee.id = kw_lv_apply.emp_name
                INNER JOIN kw_lv_business ON
                    kw_lv_apply.id = kw_lv_business.lv_id
                INNER JOIN kw_lv_activity_master ON
                    kw_lv_business.activity_name = kw_lv_activity_master.id
                INNER JOIN kw_lv_sub_category_master ON
                    kw_lv_business.sub_category = kw_lv_sub_category_master.id
                INNER JOIN crm_lead ON
                    kw_lv_business.crm_id = crm_lead.id
                INNER JOIN crm_stage ON
                    crm_lead.stage_id = crm_stage.id
				INNER JOIN kw_res_branch ON 
					hr_employee.base_branch_id = kw_res_branch.id
                ORDER BY id DESC		
        )""" % (self._table))

    @api.multi
    def get_price(self):
        lv_apply = self.env['kw_lv_apply'].search([])
        for record in self:
            for applied_record in lv_apply:
                if applied_record.visit_category.visit_details == 'yes' and len(applied_record.business_ids) > 0 and record.id in applied_record.business_ids.ids:
                    record.price = applied_record.price / len(applied_record.business_ids) if applied_record.price > 0 else 0