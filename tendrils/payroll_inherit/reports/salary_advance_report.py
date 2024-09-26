from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError
from datetime import date, datetime, time
from odoo.addons import decimal_precision as dp
import math
from math import floor,ceil

class EmployeesSalaryAdvanceReport(models.Model):
    _name = 'payroll_salary_advance_report'
    _description = 'Payroll Salary Advance Report'
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
    name = fields.Char(string="Employee's Name",related='employee_id.name')
    date_to = fields.Date(string="To Date")
    employee_id = fields.Many2one("hr.employee")
    emp_code = fields.Char(string="Emp ID",related='employee_id.emp_code')
    interest = fields.Float(string='Interest Amount',digits=dp.get_precision('Payroll'))
    principal_amount = fields.Float(string='EMI Amount',digits=dp.get_precision('Payroll'))
    total_amount = fields.Float(string='Total',digits=dp.get_precision('Payroll'),compute='compute_amount')
    purpose = fields.Char(string="Purpose",compute='compute_amount')
    
    def calculate_round_amount(self,amount):
        if amount - int (amount) >= 0.5:
            return  ceil(amount)
        else:
            return round(amount)
   
                
    @api.depends('interest','principal_amount')
    def compute_amount(self):
        for rec in self:
            rec.total_amount = rec.calculate_round_amount(rec.principal_amount + rec.interest)
            if rec.total_amount > 0 :
                salary_adv_lines = self.env['kw_advance_deduction_line'].sudo().search([('year','=',int(rec.year)),('month','=',int(rec.month)),('employee_id','=',rec.employee_id.id)]).mapped('deduction_id').ids
                if salary_adv_lines:
                    salary_adv = self.env['kw_advance_apply_salary_advance'].sudo().search([('id','in',salary_adv_lines)])
                    purpose_lst = []
                    for record in salary_adv:
                        purpose_lst.append(record.adv_purpose.purpose)
                    rec.purpose = ', '.join(purpose_lst)


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as(
        select row_number() over() as id,	
		date_part('year',a.date_to) as year,
        CAST(date_part('month',a.date_to) as varchar(10)) as month,
        a.date_to as date_to,
 		q.employee_id as employee_id,
 		case
		when q.code = 'SALADV'  then  (select sum(n.monthly_interest) from kw_advance_deduction_line n join kw_advance_apply_salary_advance s on n.deduction_id = s.id 
										join hr_employee e on e.id = s.employee_id  and n.year = date_part('year', a.date_to)
										and n.month = date_part('month', a.date_to) and s.state in ('release','paid') and s.employee_id = q.employee_id and  (n.is_preclosure is null or n.is_preclosure is false))
		end as interest,
		case
		when q.code = 'SALADV'  then  (select sum(n.principal_amt) from kw_advance_deduction_line n join kw_advance_apply_salary_advance s on n.deduction_id = s.id 
										join hr_employee e on e.id = s.employee_id  and n.year = date_part('year', a.date_to)
										and n.month = date_part('month', a.date_to)  and s.state in ('release','paid')  and  s.employee_id = q.employee_id and  (n.is_preclosure is null or n.is_preclosure is false))
		end as principal_amount
	    from hr_payslip a join hr_payslip_line as q on a.id = q.slip_id
        join hr_employee e on e.id = a.employee_id
		where q.code = 'SALADV' and q.amount >0 and a.state='done'
		group by a.date_to,q.code,q.employee_id
        )""" % (self._table))



class EmployeeVerifiedSalaryAdvanceReport(models.Model):
    _name = 'payroll_salary_advance_verified_report'
    _description = 'Payroll Salary Advance Verified Report'
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
    name = fields.Char(string="Employee's Name",related='employee_id.name')
    date_to = fields.Date(string="To Date")
    employee_id = fields.Many2one("hr.employee")
    emp_code = fields.Char(string="Emp ID",related='employee_id.emp_code')
    interest = fields.Float(string='Interest Amount',digits=dp.get_precision('Payroll'))
    principal_amount = fields.Float(string='EMI Amount',digits=dp.get_precision('Payroll'))
    total_amount = fields.Float(string='Total',digits=dp.get_precision('Payroll'),compute='compute_amount')
    purpose = fields.Char(string="Purpose",compute='compute_amount')
    
    def calculate_round_amount(self,amount):
        if amount - int (amount) >= 0.5:
            return  ceil(amount)
        else:
            return round(amount)
   
                
    @api.depends('interest','principal_amount')
    def compute_amount(self):
        for rec in self:
            rec.total_amount = rec.calculate_round_amount(rec.principal_amount + rec.interest)
            if rec.total_amount > 0 :
                salary_adv_lines = self.env['kw_advance_deduction_line'].sudo().search([('year','=',int(rec.year)),('month','=',int(rec.month)),('employee_id','=',rec.employee_id.id)]).mapped('deduction_id').ids
                if salary_adv_lines:
                    salary_adv = self.env['kw_advance_apply_salary_advance'].sudo().search([('id','in',salary_adv_lines)])
                    purpose_lst = []
                    for record in salary_adv:
                        purpose_lst.append(record.adv_purpose.purpose)
                    rec.purpose = ', '.join(purpose_lst)


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as(
        select row_number() over() as id,	
		date_part('year',a.date_to) as year,
        CAST(date_part('month',a.date_to) as varchar(10)) as month,
        a.date_to as date_to,
 		q.employee_id as employee_id,
 		case
		when q.code = 'SALADV'  then  (select sum(n.monthly_interest) from kw_advance_deduction_line n join kw_advance_apply_salary_advance s on n.deduction_id = s.id 
										join hr_employee e on e.id = s.employee_id  and n.year = date_part('year', a.date_to)
										and n.month = date_part('month', a.date_to) and s.state in ('release','paid') and s.employee_id = q.employee_id  and  (n.is_preclosure is null or n.is_preclosure is false))
		end as interest,
		case
		when q.code = 'SALADV'  then  (select sum(n.principal_amt) from kw_advance_deduction_line n join kw_advance_apply_salary_advance s on n.deduction_id = s.id 
										join hr_employee e on e.id = s.employee_id  and n.year = date_part('year', a.date_to)
										and n.month = date_part('month', a.date_to)  and s.state in ('release','paid')  and  s.employee_id = q.employee_id  and  (n.is_preclosure is null or n.is_preclosure is false))
		end as principal_amount
	    from hr_payslip a join hr_payslip_line as q on a.id = q.slip_id
        join hr_employee e on e.id = a.employee_id
		where q.code = 'SALADV' and q.amount >0 
		group by a.date_to,q.code,q.employee_id
        )""" % (self._table))
