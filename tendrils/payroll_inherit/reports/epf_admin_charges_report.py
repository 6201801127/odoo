import string
from odoo import fields, models, api, tools
from datetime import date, datetime, time


class EPFAdminChargesReport(models.Model):
    _name = 'epf_admin_charges_report'
    _description = 'EPF Admin Charges Report'
    _auto = False


   
    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]
    year = fields.Char(string='Year',size=4)
    month = fields.Selection(MONTH_LIST, string='Month')
    date_to = fields.Date(string="Confirm Date")
    gross_wages = fields.Integer(string="Total EPF Wages",compute='_compute_admin_charges')
    admin_charges  = fields.Integer(string="Admin Charges" ,compute='_compute_admin_charges')
    
    @api.depends('date_to')
    def _compute_admin_charges(self):
        for rec in self:
            epf = sum(self.env['payroll_epf_calculation_report'].sudo().search([('date_to','=',rec.date_to)]).mapped('epf_wages'))
            rec.gross_wages = epf
            rec.admin_charges = round(rec.gross_wages * 0.5/100)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
        SELECT 
        ROW_NUMBER() OVER() AS id,
        DATE_PART('year', h.date_to) AS year,
        CAST(DATE_PART('month', h.date_to) AS VARCHAR(10)) AS month,
        h.date_to
        FROM 
        hr_payslip h
        JOIN 
        hr_payslip_line l ON h.id = l.slip_id AND h.company_id = 1 AND h.state = 'done'
        JOIN 
        hr_contract c ON c.id = h.contract_id
        GROUP BY 
        h.date_to
        HAVING 
        SUM(CASE WHEN l.code = 'EEPF' THEN l.amount ELSE 0 END) > 0
        )""" % (self._table))
        
        
         


    #    select  row_number() over() as id,date_part('year',h.date_to) as year,
	# 	CAST(date_part('month',h.date_to) as varchar(10)) as month,
	# 	h.date_to,
    #     case when max(c.pf_deduction) in ('basicper','other')
    #         then sum(l.amount) filter(where l.code = 'BASIC') 
    #     when max(c.pf_deduction) = 'avail1800' and sum(l.amount) filter(where l.code = 'BASIC') >=15000
    #     then 15000 
    #     else sum (l.amount) filter(where l.code = 'BASIC') 
    #     end as basic
    #     from hr_payslip h
    #     join hr_payslip_line l on h.id = l.slip_id and h.company_id = 1 and h.state='done'
    #     join hr_contract c on c.id = h.contract_id
    #     group by h.date_to
    #     having SUM(l.amount) FILTER (WHERE l.code = 'EEPF') > 0   