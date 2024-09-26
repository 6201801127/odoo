from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError
from datetime import date, datetime, time


class EmployeeESICalcReport(models.Model):
    _name = 'employee_esi_calc_report'
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
    employee_id = fields.Many2one("hr.employee")
    name = fields.Char(string="Name",related='employee_id.name')
    emp_code = fields.Char(string="Code",related='employee_id.emp_code')
    department_id = fields.Many2one("hr.department",string="Department",related='employee_id.department_id')
    job_id = fields.Many2one("hr.job",string="Designation",related='employee_id.job_id')
    basic = fields.Integer(string="Total Monthly Wages")
    ip_contribution = fields.Integer(string="IP Contribution(0.75%)")
    # empr_contribution  = fields.Integer(string="Employer Contribution(3.25%)",compute='calculate_total')
    # total  = fields.Integer(compute='calculate_total',string="Total" )
    contract_id = fields.Many2one('hr.contract')
    date_to = fields.Date()
   
    
    # @api.depends('ip_contribution','employee_id')
    # def calculate_total(self):
    #     for rec in self:
    #         # rec.empr_contribution = rec.basic*3.25/100 if rec.ip_contribution > 0 else 0
    #         rec.total = rec.ip_contribution + rec.empr_contribution         
            
    



    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            SELECT ROW_NUMBER() OVER() AS id,
            CAST(MAX(date_part('year', a.date_to)) AS VARCHAR(10)) AS year,
            CAST(MAX(date_part('month', a.date_to)) AS VARCHAR(10)) AS month,
            a.employee_id AS employee_id,
            a.contract_id AS contract_id,
            a.date_to AS date_to,
            SUM(q.amount) FILTER (WHERE q.code IN ('BASIC','HRAMN','TCA','PBONUS','CBONUS','LTC','PP')) AS basic,
            SUM(q.amount) FILTER (WHERE q.code = 'ESI') AS ip_contribution
            FROM hr_payslip a
            JOIN hr_payslip_line AS q ON a.id = q.slip_id
            JOIN hr_contract e ON e.id = a.contract_id
            WHERE a.company_id = 1
            GROUP BY a.date_to, a.employee_id, a.contract_id,a.state
            HAVING a.state = 'done' AND SUM(q.amount) FILTER (WHERE q.code = 'ESI') > 0
        )""" % (self._table))