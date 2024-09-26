# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError


class kw_seleted_fis_yr(models.Model):
    _name = "kw_fiscal_selected_id"
    _description = "This Model helps to pass fiscal year id to report view"

    fiscal_year = fields.Many2one('account.fiscalyear', string='Financial Year')


class kw_fy_emp_report(models.Model):
    _name = "kw_fy_emp_reports"
    _description = "Kwantify FY Employee Report"
    _auto = False

    fiscal_year = fields.Many2one('account.fiscalyear', string='Financial Year')
    months = fields.Char(string=" Month")
    join_fte = fields.Integer(string='FTE Join')
    exit_fte = fields.Integer(string='FTE Exit')
    total_fte = fields.Integer(string='Current FTE')

    join_rte = fields.Integer(string='RTE Join')
    exit_rte = fields.Integer(string='RTE Exit')
    total_rte = fields.Integer(string='Current RTE')

    join_con = fields.Integer(string='Contractual Join')
    exit_con = fields.Integer(string='Contractual Exit')
    total_con = fields.Integer(string='Current Contractual')
    id = fields.Integer(string='Id')

    ret_contract = fields.Integer(string="RET  &  Contractual")

    @api.model_cr_context
    def init(self):
        fis_id = self.env['kw_fiscal_selected_id'].search([], limit=1)
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as ( 
    
            select row_number() over() AS id, (select fiscal_year from kw_fiscal_selected_id) AS fiscal_year, 
            month_name AS months,ext_t[1] AS exit_rte,ext_t[2] AS exit_con,ext_t[3] AS exit_fte
            ,ejt[1] AS join_rte,ejt[2] AS join_con,ejt[3] AS join_fte,et[1] AS total_rte,et[2] AS total_con,et[3] AS total_fte
            FROM (
            select month_name, ARRAY_AGG(emp_type) AS ety,
            ARRAY_AGG(emp_exit_total) AS ext_t,
            ARRAY_AGG(emp_join_total) AS ejt,
            ARRAY_AGG(emp_total) AS et
            FROM (select TO_CHAR(TO_DATE (x.current_month::text, 'MM'), 'Month') AS month_name ,
            case when x.emp_type in ('S','C') then 'RET' else 
            case when x.emp_type = 'P' then 'FTE' else 
            case when x.emp_type = 'O' then 'Contractual' else x.emp_type end
            end
            end AS emp_type,
            sum(x.exit_count) AS emp_exit_total,sum(x.join_count) AS emp_join_total,sum(y.total_count) AS emp_total from (select emp_exit_details_table.exit_count, emp_join_details_table.emp_type,emp_join_details_table.current_month,emp_join_details_table.join_count 
            from (select current_month,emp_type,count(emp_id) as exit_count from (select (select DATE_PART('month',date_stop ))
            AS current_month, et.code AS emp_type, et.id as emp_type_id from account_period AS ap
            cross join kwemp_employment_type AS et
            where ap.fiscalyear_id = (select fiscal_year from kw_fiscal_selected_id) and ap.special != true) AS emp_fiscal_month
            left join 
            (select DATE_PART('month',last_working_day) AS month, 
            case when id is null then 0 else id end AS emp_id,
            case when active is null then false else active end AS active,
            case when employement_type is null then 0 else employement_type end AS emp_type_emp
            from  hr_employee) AS emp_join_table 
            on emp_fiscal_month.current_month = emp_join_table.month and emp_fiscal_month.emp_type_id = emp_join_table.emp_type_emp
            group by current_month,emp_type order by current_month asc) AS emp_exit_details_table
            
            inner join 
            
            (select current_month,emp_type,count(emp_id) AS join_count from (select (select DATE_PART('month',date_stop ))
            AS current_month, et.code AS emp_type, et.id AS emp_type_id from account_period AS ap
            cross join kwemp_employment_type AS et
            where ap.fiscalyear_id = (select fiscal_year from kw_fiscal_selected_id) and ap.special != true) AS emp_fiscal_month
            left join 
            (select DATE_PART('month',date_of_joining ) AS month, 
            case when id is null then 0 else id end AS emp_id,
            case when active is null then false else active end AS active,
            case when employement_type is null then 0 else employement_type end AS emp_type_emp
            from  hr_employee) AS emp_join_table 
            on emp_fiscal_month.current_month = emp_join_table.month and emp_fiscal_month.emp_type_id = emp_join_table.emp_type_emp
            group by current_month,emp_type order by current_month asc) AS emp_join_details_table
            on emp_exit_details_table.current_month = emp_join_details_table.current_month 
            and emp_exit_details_table.emp_type = emp_join_details_table.emp_type) AS x
            
            inner join 
            
            (select * from (select current_month,emp_type,count(emp_id) AS total_count from (select (select DATE_PART('month',date_stop ))
            AS current_month, et.code AS emp_type,ap.date_stop AS last_day_month, et.id AS emp_type_id from account_period as ap
            cross join kwemp_employment_type AS et
            where ap.fiscalyear_id = (select fiscal_year from kw_fiscal_selected_id) and ap.special != true) AS emp_fiscal_month
            left join 
            (select DATE_PART('month',date_of_joining ) AS month, date_of_joining,
            case when id is null then 0 else id end AS emp_id,
            case when active is null then false else active end AS active,
            case when employement_type is null then 0 else employement_type end AS emp_type_emp
            from  hr_employee) AS emp_join_table 
            on emp_fiscal_month.emp_type_id = emp_join_table.emp_type_emp
            and emp_join_table.date_of_joining < emp_fiscal_month.last_day_month
            group by current_month,emp_type order by current_month asc) AS emp_total_details_table) AS y
            on x.current_month = y.current_month 
            and x.emp_type = y.emp_type group by month_name,x.emp_type) AS z group by month_name) AS final_t
    
        )""" % (self._table))


class kw_fy_emp_report(models.TransientModel):
    _name = "kw_fy_emp_reports_wizard"
    _description = "wizard fiscal year"

    fiscal_year = fields.Many2one('account.fiscalyear', string='Financial Year')

    def get_fy_resource_report(self):
        select_fis = self.env['kw_fiscal_selected_id'].search([])
        if select_fis:
            select_fis.fiscal_year = self.fiscal_year.id
        else:
            self.env['kw_fiscal_selected_id'].create({'fiscal_year': self.fiscal_year.id})

        tree_view_id = self.env.ref('kw_employee_info_system.kw_fy_emp_resources_tree_view').id
        fiscal_year_name = self.fiscal_year.name
        action = {
            'name': f'Employee MIS Report ({fiscal_year_name})',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_fy_emp_reports',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view_id, 'tree')],
            'target': 'main',
            'view_id': tree_view_id
        }
        return action
