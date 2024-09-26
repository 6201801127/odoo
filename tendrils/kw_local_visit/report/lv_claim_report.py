# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, tools, _,SUPERUSER_ID
from odoo.exceptions import ValidationError,UserError
from lxml import etree
import psycopg2


class KWLVClaimReport(models.Model):
    _name           = "kw_lv_claim_report"
    _description    = "Local visit Claim report"
    _auto           = False
    
   

    emp_name = fields.Many2one('hr.employee',string='Employee Name') 
    visit_id = fields.Many2one('kw_lv_Apply')
    date_of_travel = fields.Date()
    wo_name = fields.Char("WO Name")
    ra_approval = fields.Char(string='RA Approval')
    wo_code = fields.Char("WO Code")
    branch_location = fields.Many2one('kw_res_branch')
    branch_country = fields.Many2one('res.country')
    visit_location = fields.Char("Location")
    visit_purpose = fields.Char("Purpose")

    @api.model_cr
    def _fetch_claim_reports(self):
        fy_date_start = self.env.context.get('fy_date_start')  
        fy_date_stop = self.env.context.get('fy_date_stop')
        quater = self.env.context.get('quater')
        if quater:
            if quater == 1:
                fy_date_stop = fy_date_start + relativedelta(months=3) - relativedelta(days=1)
            elif quater == 2:
                fy_date_start = fy_date_start + relativedelta(months=3)
                fy_date_stop = fy_date_start + relativedelta(months=3) - relativedelta(days=1)
            elif quater == 3:
                fy_date_start = fy_date_start + relativedelta(months=6)
                fy_date_stop = fy_date_start + relativedelta(months=3) - relativedelta(days=1)
            elif quater == 4:
                fy_date_start = fy_date_start + relativedelta(months=9)
        
        current_date = date.today()
        tools.drop_view_if_exists(self.env.cr, self._table)
        query=""" CREATE or REPLACE VIEW %s as (
                    with local_visit as (
                            	
                    select lva.id as visit_id, 
                    COALESCE((SELECT string_agg(name::TEXT, ', ') FROM crm_lead cl WHERE cl.id in (select crm_id from kw_lv_business where lv_id = lva.id) ),'NA' ) AS wo_name,
                    COALESCE(( SELECT string_agg(code::TEXT, ', ')FROM crm_lead cl WHERE cl.id in (select crm_id from kw_lv_business where lv_id = lva.id) ),'NA') AS wo_code,
                    string_agg(lvb.location::TEXT, ', ') as location,
                    string_agg(lvb.purpose::TEXT, ', ') as purpose

                    from kw_lv_apply lva left join kw_lv_business lvb on lva.id = lvb.lv_id where lva.state = 'approved'
                    AND lva.visit_category NOT IN (SELECT id FROM kw_lv_category_master WHERE category_name = 'Personal')    group by lva.id)



                    SELECT row_number() OVER (
                            ---order by lva.emp_name,emp.department_id,emp.division,emp.sbu_master_id,local_visit.wo_name,local_visit.wo_code
                            ) AS id,
                    lva.id as visit_id,
                    lva.emp_name,
                    lva.visit_date as date_of_travel,
                    emp.base_branch_id AS branch_location,
                    (select country from kw_res_branch where id = emp.base_branch_id) as branch_country,
                    local_visit.wo_name,
                    local_visit.wo_code,
                    COALESCE( lva.location, local_visit.location, '') AS visit_location,
                    COALESCE(lva.purpose, local_visit.purpose, '') AS visit_purpose,
                    CASE
                    WHEN lva.action_remark IS NULL THEN 'No'
                    WHEN lva.action_remark = 'Auto Approved.' THEN 'Auto Approved'
                    ELSE 'Yes'
                    END AS ra_approval
                
                FROM local_visit
                join kw_lv_apply lva on local_visit.visit_id = lva.id
                            	
                JOIN 
                     hr_employee emp ON lva.emp_name = emp.id 
                where lva.visit_date >= %s and lva.visit_date <= %s
                    --- and  date_part('quarter', date_of_travel) from kw_lv_claim_report

        )""" % (self._table, '%s', '%s')

        self.env.cr.execute(query, (fy_date_start if fy_date_start else current_date, fy_date_stop if fy_date_stop else current_date))
        self.env.cr.execute("SELECT * FROM %s" % (self._table,))
        results = self.env.cr.dictfetchall()

        return results




    
    

class GetFilteredLocalVisitClaimReport(models.TransientModel):
    _name = "filter_local_visit_claim_report"
    _description = "Get Filtered Local Visit Claim Report FY Wise"

    financial_year_id = fields.Many2one('account.fiscalyear',string='Financial Year', required=True)
    quater = fields.Selection([(1,'Quater 1'),(2,'Quater 2'),(3,'Quater 3'),(4,'Quater 4')],string='Quater')
    
    def get_filtered_lv_claim_report(self):
        physical_ids = self.env['kw_lv_claim_physical'].search([]).mapped('visit_id.id')
        results = self.env['kw_lv_claim_report'].with_context(fy_date_start=self.financial_year_id.date_start,fy_date_stop=self.financial_year_id.date_stop,quater=self.quater)._fetch_claim_reports()
        query = "INSERT INTO kw_lv_claim_physical(visit_id, emp_name,date_of_travel, wo_name, wo_code, ra_approval, visit_location, visit_purpose, branch_location, branch_country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        params = []
        
        if results:
            for rec in results:
                if rec['visit_id'] not in physical_ids:
                    params.append((rec['visit_id'], rec['emp_name'], rec['date_of_travel'], rec['wo_name'], rec['wo_code'], rec['ra_approval'], rec['visit_location'], rec['visit_purpose'], rec['branch_location'], rec['branch_country']))
        if params:
            self.env.cr.executemany(query, params)

        domain = []
        current_date = date.today()
        fy_date_start = self.financial_year_id.date_start if self.financial_year_id.date_start else current_date
        fy_date_stop = self.financial_year_id.date_stop if self.financial_year_id.date_stop else current_date
        if self.quater:
            if self.quater == 1:
                fy_date_stop = fy_date_start + relativedelta(months=3) - relativedelta(days=1)
            elif self.quater == 2:
                fy_date_start = fy_date_start + relativedelta(months=3)
                fy_date_stop = fy_date_start + relativedelta(months=3) - relativedelta(days=1)
            elif self.quater == 3:
                fy_date_start = fy_date_start + relativedelta(months=6)
                fy_date_stop = fy_date_start + relativedelta(months=3) - relativedelta(days=1)
            elif self.quater == 4:
                fy_date_start = fy_date_start + relativedelta(months=9)
            domain.append(('date_of_travel', '>=', fy_date_start))
            domain.append(('date_of_travel', '<=', fy_date_stop))
        if not self.quater:
            domain.append(('date_of_travel', '>=', fy_date_start))
            domain.append(('date_of_travel', '<=', fy_date_stop))
        
        view_id = self.env.ref('kw_local_visit.kw_lv_claim_physical_view_tree').id
        action = {
            'name': f'Local Visit Claim Report ',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_lv_claim_physical',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            'domain': domain,
        }
        return action
