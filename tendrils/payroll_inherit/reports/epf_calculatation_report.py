from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError
from datetime import date, datetime, time
import math
from math import ceil,floor


class EPFCalcReport(models.Model):
    _name = 'payroll_epf_calculation_report'
    _description = 'EPF Calculation Report'
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
    employee_id = fields.Many2one("hr.employee")
    name = fields.Char(string="Name",related='employee_id.name')
    emp_code = fields.Char(string="Code",related='employee_id.emp_code')
    gross_wages = fields.Integer()
    eepf = fields.Integer()
    uan = fields.Char(string="EPF UAN",related='employee_id.uan_id')
    edli_charges  = fields.Integer(compute='compute_pf_1800_slab')
    pf_1800_slab = fields.Char(compute='compute_pf_1800_slab',string='PF 1800 Slab')
    eps_wages = fields.Integer(compute='compute_pf_1800_slab',string="EPS Wages")
    employee_pf  = fields.Integer(compute='compute_pf_1800_slab',string="Employee PF")
    pension_fund  = fields.Integer(compute='compute_pf_1800_slab',string="Pension Fund")
    employer_pf  = fields.Integer(compute='compute_pf_1800_slab',string="Employer PF")
    eps_enable = fields.Boolean("Under EPS Scheme")
    contract_id = fields.Many2one("hr.contract")
    edli_wages = fields.Integer(compute='compute_pf_1800_slab',string="EDLI Wages")
    epf_wages = fields.Integer(compute='compute_pf_1800_slab',string='EPF Wages')

    def calculate_round_amount(self,amount):
        if amount - int (amount) >= 0.5:
            return  ceil(amount)
        else:
            return round(amount)

    @api.depends('gross_wages')
    def compute_pf_1800_slab(self):
        for rec in self:
            rec.employee_pf = rec.eepf
            if rec.contract_id.enable_epf == 'yes':
                rec.employee_pf = rec.eepf
                if rec.eepf == 1800 and rec.gross_wages >= 15000 and rec.contract_id.pf_deduction =='avail1800':
                    rec.pf_1800_slab = 'Yes'
                else:
                    rec.pf_1800_slab = 'No'
                rec.epf_wages = rec.gross_wages if rec.contract_id.pf_deduction in ('basicper','other') else 15000 if rec.contract_id.pf_deduction =='avail1800' and rec.gross_wages >=15000 else rec.gross_wages
                rec.edli_wages = rec.epf_wages if rec.epf_wages < 15000 else  15000
                rec.edli_charges = rec.calculate_round_amount(rec.epf_wages * 0.5/100) if rec.epf_wages < 15000 else  rec.calculate_round_amount(15000 * 0.5/100)

                if rec.eps_enable == True:
                    if rec.epf_wages < 15000:
                        rec.eps_wages = rec.epf_wages
                    else:
                        rec.eps_wages = 15000
                else:
                    rec.eps_wages = 0
                rec.pension_fund = rec.calculate_round_amount(rec.eps_wages * 8.33/100)
                rec.employer_pf = rec.employee_pf - rec.pension_fund if rec.contract_id.pf_deduction !='other' else rec.calculate_round_amount(rec.gross_wages * 12/100) - rec.pension_fund if rec.pension_fund > 0 else rec.calculate_round_amount(rec.gross_wages * 12/100)


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
       select  row_number() over() as id,date_part('year',a.date_to) as year,
		CAST(date_part('month',a.date_to) as varchar(10)) as month,
		a.date_to as date_to,
		a.employee_id as employee_id,
		sum(b.amount) FILTER (WHERE b.code = 'BASIC' ) as gross_wages,
		sum(b.amount) FILTER (WHERE b.code = 'EEPF' ) as eepf,
		con.eps_enable as eps_enable,
        a.contract_id as contract_id
		from hr_payslip a 
        join hr_payslip_line b 
		on a.id = b.slip_id
        join hr_contract con 
		on a.contract_id = con.id
		join hr_employee c on con.employee_id = c.id 
		where a.state='done' and
        a.company_id = 1
		group by a.employee_id,a.date_to,con.eps_enable,a.contract_id
		having sum(b.amount) FILTER (WHERE b.code = 'EEPF' )>0
        )""" % (self._table))
