from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError
from datetime import date, datetime, time
import math

class ESICalcReport(models.Model):
    _name = 'payroll_bulk_esi_calculation_report'
    _description = 'ESI Calculation Report'
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
    date_to = fields.Date()
    esi_basic=fields.Integer(string="ESIC Monthly Wages")
    non_esi_basic=fields.Integer(string="Non ESIC Monthly Wages")
    non_esi_gross=fields.Integer(string="Non ESIC Monthly Wages",compute='calculate_contribution')
    
    empr_contribution  = fields.Float(string="Employer Contribution(3.25%)",compute='calculate_contribution')

    @api.depends('esi_basic','date_to')
    def calculate_contribution(self):
        for rec in self:
            rec.empr_contribution = math.ceil(rec.esi_basic *3.25/100)
            self.env.cr.execute(f"SELECT     SUM(q.amount) AS total_amount FROM     hr_payslip a JOIN     hr_payslip_line AS q ON a.id = q.slip_id LEFT JOIN (    SELECT slip_id, SUM(amount) AS esi_sum    FROM hr_payslip_line    WHERE code = 'ESI'  GROUP BY slip_id) AS esi ON a.id = esi.slip_id WHERE     a.company_id = 1     AND a.state = 'done'     AND a.date_to = '{rec.date_to}' AND q.code IN ('BASIC', 'HRAMN', 'TCA', 'PBONUS', 'CBONUS', 'LTC', 'PP')    AND COALESCE(esi.esi_sum, 0) = 0 GROUP BY     a.date_to HAVING     SUM(CASE WHEN q.code = 'HRAMN' THEN q.amount ELSE 0 END) > 0")
            query_result3 = self._cr.fetchall()
            print(query_result3)
            rec.non_esi_gross =query_result3[0][0]
                
            
    # total_esic_basic = fields.Integer(string="Total ESIC Wages")
    # total_non_esic_basic = fields.Integer(string="Total ESIC Wages")

    # ip_contribution = fields.Integer(string="IP Contribution(0.75%)")
    # total  = fields.Integer(compute='calculate_total',string="Total" )
    # date_to = fields.Date()
    # check_employees = fields.Char(compute='calculate_total')
   
    
    # @api.depends('ip_contribution','empr_contribution')
    # def calculate_total(self):
    #     for rec in self:
    #         rec.total = rec.ip_contribution + rec.empr_contribution      
            # if rec.ip_contribution > 0:
            #     rec.check_employees = 'ESIC members'
            # else:
            #     rec.check_employees = 'Non ESIC members'   
    
                
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
        

WITH cte4 AS (
    WITH cte1 AS (
        SELECT 
            ROW_NUMBER() OVER(ORDER BY a.date_to) AS id,
            a.date_to AS date_to,
            SUM(q.amount) FILTER (WHERE q.code IN ('BASIC','HRAMN','TCA','PBONUS','CBONUS','LTC','PP')) AS total_basic
        FROM 
            hr_payslip a
        JOIN 
            hr_payslip_line AS q ON a.id = q.slip_id
        WHERE 
            a.company_id = 1 
            AND a.state = 'done' 
        GROUP BY 
            a.date_to, a.employee_id
        HAVING 
            SUM(q.amount) FILTER (WHERE q.code = 'ESI') > 0
    )
    SELECT 
        sum(total_basic) as total_basic,
        date_to 
    FROM 
        cte1 
    GROUP BY 
        date_to
),
cte3 AS (
    WITH cte2 AS (
        SELECT 
            ROW_NUMBER() OVER() AS id,
            a.date_to AS date_to,
            SUM(q.amount) FILTER (WHERE q.code IN ('BASIC','HRAMN','TCA','PBONUS','CBONUS','LTC','PP')) AS basic
        FROM 
            hr_payslip a
        JOIN 
            hr_payslip_line AS q ON a.id = q.slip_id
        WHERE 
            a.company_id = 1 
            AND a.state = 'done' 
        GROUP BY 
            a.date_to, a.employee_id
        HAVING 
            SUM(q.amount) FILTER (WHERE q.code = 'HRAMN') > 0 
            AND SUM(q.amount) FILTER (WHERE q.code = 'ESI') = 0 
    )
    SELECT 
        date_to,
        sum(basic) as basic_sum
    FROM 
        cte2 
    GROUP BY 
        date_to
)
SELECT 
    ROW_NUMBER() OVER(ORDER BY a.date_to) AS id,
    a.total_basic AS esi_basic,
    b.basic_sum as non_esi_basic,
    a.date_to,
    EXTRACT(YEAR FROM a.date_to) AS year,
	CAST(date_part('month',a.date_to) as varchar(10)) as month
FROM 
    cte4 a 
JOIN 
    cte3 b ON a.date_to = b.date_to


        )""" % (self._table))
