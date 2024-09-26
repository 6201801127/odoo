from odoo import models, fields, api
from odoo import tools

class TourSettlementExpenseReport(models.Model):
    _name = 'kw_tour_settlement_expense_report'
    _description = 'Tour Settlement Expense Report'
    _auto = False

    # tour_id         = fields.Many2one("kw_tour","Tour")
    code           = fields.Char("Tour Reference No.")
    # settlement_id   = fields.Many2one("kw_tour_settlement","Setlement")
    employee_id     = fields.Many2one('hr.employee',string="Employee Name")
    date_of_travel  = fields.Date("Date Of Travel")
    date_of_return  = fields.Date("Date Of Return")
    state           = fields.Char("Status")
    ta_inr =      fields.Float("TA Amount(INR)")
    ta_usd =      fields.Float("TA Amount(USD)")
    da_inr =      fields.Float("DA Amount(INR)")
    da_usd =      fields.Float("DA Amount(USD)")
    hra_inr =      fields.Float("HRA Amount(INR)")
    hra_usd =      fields.Float("HRA Amount(USD)")
    misc_inr =      fields.Float("Misc. Amount(INR)")
    misc_usd =      fields.Float("Misc. Amount(USD)")
    hardship_inr =      fields.Float("Hardship Amount(INR)")
    hardship_usd =      fields.Float("Hardship Amount(USD)")
    visa_inr =      fields.Float("VISA Amount(INR)")
    visa_usd =      fields.Float("VISA Amount(USD)")
    vaccine_inr =      fields.Float("Vaccine Amount(INR)")
    vaccine_usd =      fields.Float("Vaccine Amount(USD)")
    rtpcr_inr =      fields.Float("RTPCR Amount(INR)")
    rtpcr_usd =      fields.Float("RTPCR Amount(USD)")
    ticket_inr =      fields.Float("Ticket Cost(INR)")
    ticket_usd =      fields.Float("Ticket Cost(USD)")
    action_taken_by = fields.Char("Action To Be Taken By")
    city_id       = fields.Many2one('kw_tour_city', string="Originating Place")
    purpose         = fields.Char("Purpose")
    department    = fields.Char(related='employee_id.department_id.name', string='Department Name')
    division        = fields.Char(related='employee_id.division.name', string='Division')
    section         = fields.Char(related='employee_id.section.name', string='Section')
    amount_total_inr = fields.Float("Total Amount(INR)",compute='_compute_total_inr')
    amount_total_usd = fields.Float("Total Amount(USD)",compute='_compute_total_usd')
    fiscal_year_id  = fields.Many2one('account.fiscalyear', "Fiscal Year")

    @api.multi
    def _compute_total_inr(self):
        for rec in self:
            rec.amount_total_inr= rec.ta_inr+rec.da_inr+ rec.hra_inr+rec.misc_inr+rec.hardship_inr+rec.visa_inr+rec.vaccine_inr+rec.rtpcr_inr+rec.ticket_inr

    @api.multi
    def _compute_total_usd(self):
        for rec in self:
            rec.amount_total_usd= rec.ta_usd+rec.da_usd+ rec.hra_usd+rec.misc_usd+rec.hardship_usd+rec.visa_usd+rec.rtpcr_usd+rec.vaccine_usd+rec.ticket_usd

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        
        self.env.cr.execute(f""" CREATE or REPLACE VIEW {self._table} as (
                select ROW_NUMBER() OVER () AS id,(select code from kw_tour where id = a.tour_id) as code,employee_id, (select date_travel from kw_tour where id = a.tour_id) as date_of_travel,
                (select date_return from kw_tour where id = a.tour_id) as date_of_return,
                (select city_id from kw_tour where id = a.tour_id) as city_id,
                (select purpose from kw_tour where id = a.tour_id) as purpose,
                (SELECT id FROM account_fiscalyear WHERE (SELECT date_travel FROM kw_tour WHERE id = a.tour_id) BETWEEN date_start AND date_stop) AS fiscal_year_id,
                state,
                case 
                when state = 'Draft'  then 'Self'
                when state = 'Applied'  then 'Settlement request pending with RA'
                when state = 'Approved'  then 'Settlement pending with Finance'
                when state = 'Granted'  then 'Payment pending with Finance'
                when state = 'Payment Done'  then 'Settled'
                else '--'
                end as action_taken_by,
                
                COALESCE((select sum(amount_inr) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and expense_id = (select id from kw_tour_expense_type where code = 'ta') ),0) as ta_inr,
                COALESCE((select sum(amount_usd) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and expense_id = (select id from kw_tour_expense_type where code = 'ta') ),0) as ta_usd,

                COALESCE((select sum(amount_inr) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and expense_id = (select id from kw_tour_expense_type where code = 'da') ),0) as da_inr,
                COALESCE((select sum(amount_usd) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and expense_id = (select id from kw_tour_expense_type where code = 'da') ),0) as da_usd,

                COALESCE((select sum(amount_inr) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and expense_id = (select id from kw_tour_expense_type where code = 'hra') ),0) as hra_inr,
                COALESCE((select sum(amount_usd) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and expense_id = (select id from kw_tour_expense_type where code = 'hra') ),0) as hra_usd,

                COALESCE((select sum(amount_inr) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and expense_id = (select id from kw_tour_expense_type where code = 'misc') ),0) as misc_inr,
                COALESCE((select sum(amount_usd) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and expense_id = (select id from kw_tour_expense_type where code = 'misc') ),0) as misc_usd,

                COALESCE((select sum(amount_inr) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and expense_id = (select id from kw_tour_expense_type where code = 'hardship allowance') ),0) as hardship_inr,
                COALESCE((select sum(amount_usd) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and expense_id = (select id from kw_tour_expense_type where code = 'hardship allowance') ),0) as hardship_usd,

                COALESCE((select sum(amount_inr) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and expense_id = (select id from kw_tour_expense_type where code = 'ticket cost') ),0) as ticket_inr,
                COALESCE((select sum(amount_usd) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and expense_id = (select id from kw_tour_expense_type where code = 'ticket cost') ),0) as ticket_usd,

                COALESCE((select sum(amount_inr) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and travel_prerequisite_id = (select id from kw_tour_travel_prerequisite where name = 'Visa') ),0) as visa_inr,
                COALESCE((select sum(amount_usd) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and travel_prerequisite_id = (select id from kw_tour_travel_prerequisite where name = 'Visa') ),0) as visa_usd,

                COALESCE((select sum(amount_inr) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and travel_prerequisite_id = (select id from kw_tour_travel_prerequisite where name = 'Vaccine') ),0) as vaccine_inr,
                COALESCE((select sum(amount_usd) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and travel_prerequisite_id = (select id from kw_tour_travel_prerequisite where name = 'Vaccine') ),0) as vaccine_usd,

                COALESCE((select sum(amount_inr) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and travel_prerequisite_id = (select id from kw_tour_travel_prerequisite where name = 'RTPCR Test') ),0) as rtpcr_inr,
                COALESCE((select sum(amount_usd) from 
                kw_tour_settlement_total_expense where settlement_id = a.id and travel_prerequisite_id = (select id from kw_tour_travel_prerequisite where name = 'RTPCR Test') ),0) as rtpcr_usd
                from kw_tour_settlement a 
                    )""")	


        
   