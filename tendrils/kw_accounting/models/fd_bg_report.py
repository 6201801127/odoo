from odoo import models, fields, api
from odoo import tools
from datetime import date, datetime


class FD_Report(models.Model):
    _name = 'fd_reports'
    _description = 'FD Report'
    _auto = False

    acc_number = fields.Char('A/C No')
    start_date = fields.Date('Start Dt.')
    maturity_date = fields.Date('Maturity Dt.')
    principal_amt = fields.Float('Principal')
    rate_of_interest = fields.Float('RoI')
    fd_type = fields.Selection([('cumulative','Cumulative'),('fixed','Fixed')],string="Type")
    ageing = fields.Selection([('<0','< 0'),('0-3','0-3'),('3-12','3-12'),('>12','> 12')],string="Ageing")
    maturity_amt = fields.Float('Maturity Amt.')
    recovered_or_renewed_dt = fields.Date('Maturity recd/Renewal Date')
    recovered_or_renewed_amt = fields.Float('Maturity recd/Renewal Amt')
    maturity_interest_net = fields.Float('Maturity Interest (Net)')
    tds = fields.Float('TDS')
    maturity_interest_gross = fields.Float('Maturity Interest (Gross)')
    interest_till = fields.Float('Interest')  
    interest_till_date = fields.Date('Interest Till Date')  
    lien_amount = fields.Float(string="Lien Amount")
    free_amount = fields.Float(string="Free Amount")

    @api.model_cr
    def init(self):
        report_date = self.env.context.get('report_date',False)
        date_format = report_date.strftime("%Y-%m-%d") if report_date else date.today().strftime("%Y-%m-%d")
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            SELECT row_number() over(order by start_date asc) as id,
            case 
                when (maturity_date < '{date_format}' and recovered_or_renewed_dt is null) THEN '<0'
                when (maturity_date - '{date_format}' + 1) <= 90 THEN '0-3'
                when (maturity_date - '{date_format}' + 1) >= 91 and (maturity_date - '{date_format}' + 1) <= 366 THEN '3-12'
                when (maturity_date - '{date_format}' + 1) > 366 THEN '>12'
            end as ageing,
            acc_number,start_date,maturity_date,principal_amt,rate_of_interest,fd_type,maturity_amt,recovered_or_renewed_dt,
            recovered_or_renewed_amt,maturity_interest_net,tds,maturity_interest_gross,interest_till,interest_till_date,lien_amount,free_amount
            from fd_tracker where ((recovered_or_renewed_dt is null or recovered_or_renewed_dt > '{date_format}') and start_date < '{date_format}') or  (maturity_date < '{date_format}' and recovered_or_renewed_dt is null)
        )"""
        self.env.cr.execute(query)

class BG_Report(models.Model):
    _name = 'bg_reports'
    _description = 'Bg Report'
    _auto = False

    bank_id = fields.Many2one('res.bank', string="Bank Name")
    bg_number = fields.Char(string="BG Number")
    bg_date = fields.Date(string="BG Date")
    bg_amount = fields.Float(string="BG Amount")
    bg_expiry_date = fields.Date(string="BG Expiry")
    ageing = fields.Selection([('0-3','0-3'),('3-6','3-6'),('>6','>6')],string="Ageing")
    claim_date = fields.Date(string="Claim Date")
    bg_purpose = fields.Selection([('workorder', 'Workorder'), ('others', 'Others'), ('tender', 'Tender'), ('empanelment', 'Empanelment')], string="BG Purpose")
    wo_id = fields.Many2one('crm.lead', string="Workorder")
    wo_number = fields.Char(string="WO/OPP Number", related="wo_id.code")
    wo_name = fields.Char(string="WO/Opportunity Name", related="wo_id.name")
    client_name = fields.Char(string="Client")
    project_amount = fields.Float(string="Project Amount")
    csg_head_id = fields.Many2one('hr.employee', string="CSG Head")
    account_holder_id = fields.Many2one('hr.employee', string="Account Holder")
    fd_amount = fields.Float(string="FD Amount")
    transaction_expiry = fields.Date(string="Transaction Expiry")
    bg_closure_date = fields.Date(string="BG Closure Date")
    bg_expenses = fields.Float(string="BG Expenses")

    @api.model_cr
    def init(self):
        report_date = self.env.context.get('report_date',False)
        date_format = report_date.strftime("%Y-%m-%d") if report_date else date.today().strftime("%Y-%m-%d")
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            SELECT row_number() over(order by bg_number asc) as id,
            case 
                when ('{date_format}' - bg_date + 1) <= 90 THEN '0-3'
                when ('{date_format}' - bg_date + 1) >= 91 and ('{date_format}' - bg_date + 1) <= 180 THEN '3-6'
                when ('{date_format}' - bg_date + 1) > 180 THEN '>6'
            end as ageing, 
            bank_id, bg_number, bg_date, bg_amount, bg_expenses, bg_expiry_date, claim_date, 
            bg_purpose, wo_id, client_name, project_amount, csg_head_id, account_holder_id, fd_amount, transaction_expiry, bg_closure_date 
            from bg_tracker where bg_date <= '{date_format}'
        )"""
        self.env.cr.execute(query)
