# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools
from datetime import date, datetime, time



class SBUResourceCostReport(models.Model):
    _name = 'sbu_resource_cost_report'
    _description = 'SBU ResourceCost Report'
    _auto = False

    
    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]
    year = fields.Selection(string='Year', selection='_get_year_list', default=str(date.today().year))
    month_name = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    emp_type = fields.Many2one('kwemp_employment_type', string='Employement Type')
    sbu_id = fields.Many2one('kw_sbu_master')
    sbu_name = fields.Char(string='SBU')
    ctc = fields.Float(string='Cost')
    
    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year + 7, 2010, -1)]
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            SELECT
                row_number() OVER () as id,
                date_part('year',a.date_to)::VARCHAR as year,
                date_part('month',a.date_to)::VARCHAR as month_name,
                hr.employement_type as emp_type,
                hr.sbu_master_id as sbu_id,
                (select name from kw_sbu_master where id = hr.sbu_master_id and type = 'sbu') as sbu_name,
                sum(b.amount) as ctc
                from hr_employee hr
                join hr_payslip a on a.employee_id=hr.id
                left join hr_payslip_line b 
                on a.id = b.slip_id  
                where b.code = 'CTC' 
                and a.state='done'
                and hr.active = true
                and hr.sbu_master_id in (select id from kw_sbu_master where type = 'sbu')
                and hr.employement_type not in (SELECT id FROM kwemp_employment_type where code in ('O','CE' ))
		        and hr.emp_role not in (SELECT id FROM kwmaster_role_name where code='O')
                group by
                a.date_to,
                hr.employement_type,sbu_name,hr.sbu_master_id
        )""" % (self._table))