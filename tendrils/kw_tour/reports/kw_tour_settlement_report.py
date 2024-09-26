from odoo import models, fields, api
from odoo import tools

class TourSettlementReport(models.Model):
    _name = 'kw_tour_settlement_report'
    _description = 'Tour Settlement Report'
    _auto = False

    tour_type_new =  fields.Many2one('kw_tour_type_new', 'Tour Type')
    settlement_id   = fields.Many2one("kw_tour_settlement","Settlement")
    tour_id         = fields.Many2one("kw_tour","Tour")
    
    name            = fields.Char("Employee Name")
    department      = fields.Char("Department")
    division        = fields.Char("Division")
    section         = fields.Char("Section")
    fiscal_year_id  = fields.Many2one('account.fiscalyear', "Fiscal Year")
    date_of_travel  = fields.Date("Date Of Travel")
    date_of_return  = fields.Date("Date Of Return")
    origin_place    = fields.Char("Originating Place") 
    purpose         = fields.Char("Purpose")
    state           = fields.Char("Status")
    total_advance_domestic = fields.Float("Advance Amount(Domestic)")
    total_advance_international = fields.Float("Advance Amount(USD)")
    total_domestic_currency = fields.Many2one("res.currency","Domestic currency")
    usd_currency_id = fields.Many2one("res.currency","USD currency")
    total_domestic  = fields.Float("Total Expenditure(Domestic)")
    total_international  = fields.Float("Total Expenditure(USD)")
    action_taken_by = fields.Char("Action To Be Taken By")
    tour_type_id = fields.Many2one('kw_tour_type', string="Type Of Tour")
    branch_country = fields.Many2one('res.country')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        
        self.env.cr.execute(f""" CREATE or REPLACE VIEW {self._table} as (
                select b.id as id,b.id as settlement_id,b.tour_id,concat(a.name,' (',a.emp_code,')') as name, 
                d.name as department,
                (select name from hr_department where id = a.division) as division,
                (select name from hr_department where id = a.section) as section,
                t.date_travel as date_of_travel,
                t.tour_type_new as  tour_type_new,
	            e.name as origin_place, 
                t.date_return as date_of_return,
                t.purpose as purpose,
                rb.country AS branch_country,
                b.state as state,
                b.total_domestic as total_domestic,
                b.total_international as total_international,
                b.domestic_currency_id as total_domestic_currency,
                b.usd_currency_id as usd_currency_id,
                b.pending_at as action_taken_by,
                b.tour_type_id,
                t.disbursed_inr as total_advance_domestic,
                t.disbursed_usd as total_advance_international,
                af.id AS fiscal_year_id
                    
                from kw_tour_settlement b  
                join hr_employee a  on a.id = b.employee_id
                left join hr_department d on a.department_id = d.id
                LEFT JOIN kw_res_branch rb ON a.base_branch_id = rb.id
                left join hr_job c on a.job_id = c.id
                left join kw_tour t on b.tour_id = t.id
                left join kw_tour_city e on  t.city_id = e.id
                LEFT JOIN account_fiscalyear af ON t.date_travel BETWEEN af.date_start AND af.date_stop
                where b.state != 'Draft'
                    )""")	

    @api.multi
    def action_settlement_details(self):
        form_view_id = self.env.ref('kw_tour.view_kw_tour_settlement_form_only').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_tour_settlement',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'res_id': self.ids[0],
            'target': 'self',
        }

    @api.multi
    def action_view_settlement_details(self):
        # tree_view_id = self.env.ref('kw_tour.view_kw_tour_settlement_details_tree').id
        # form_view_id = self.env.ref('kw_tour.view_kw_tour_settlement_details_tree').id
        return {
                'name'      : 'Tour Settlement Details',
                'view_type' : 'form',
                'view_mode' : 'tree',
                'res_model' : 'kw_tour_settlement_total_expense',
                'type'      : 'ir.actions.act_window',
                'target'    : 'current',
                'domain'    : [('settlement_id','=',self.id)],
                'context'   : {'create':False,'edit':False,'delete':False,'duplicate':False,'show_employee':False}
            }
        
    @api.multi
    def print_settlement_feedback(self):
        return self.env.ref('kw_tour.kw_tour_settlement_claim_report').report_action(self)