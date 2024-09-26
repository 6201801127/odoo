from odoo import fields, models, _, api
from odoo import tools
from datetime import date, datetime, time


class SalaryDisburseReport(models.Model):
    _name = 'kw_salary_disburse_report'
    _description = 'Salary Disburse Report'
    _auto = False

    """ view fields """
    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]
    emp_code = fields.Char(string='Employee Code',related='employee_id.emp_code')
    employee_id = fields.Many2one('hr.employee',string='Employee')
    name = fields.Char(string='Name',related='employee_id.name')
    department_id = fields.Many2one('hr.department',string='Department',related='employee_id.department_id')
    job_id = fields.Many2one('hr.job',string='Designation')
    base_branch_id = fields.Many2one('kw_res_branch', string="location")
    amount = fields.Float(string="Net Pay")
    year = fields.Char(string="Year", size=4)
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    month_int = fields.Integer(string="Month Int")
    state = fields.Char()
    bank = fields.Char("Bank")
    acc_number = fields.Integer("Account Number")
    ifsc = fields.Char("IFSC")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
        select  a.id,c.job_id,a.department_id,c.base_branch_id,date_part('year',a.date_to) as year,CAST(date_part('month',a.date_to)as varchar(10)) as month,
        b.amount as amount,a.state as state,a.employee_id as employee_id, CAST(date_part('month',a.date_to)as INTEGER) as month_int,
		case when a.bank is NULL then (select name from res_bank where id = d.bank_id)
			when a.bank is not Null then a.bank
		end as bank,
		case when a.acc_number is NULL then (select bank_account from hr_contract where id = a.contract_id)
			when a.acc_number is not Null then a.acc_number
		end as acc_number,
        case when a.ifsc is NULL then (select bic from res_bank where id = d.bank_id)
			when a.ifsc is not Null then a.ifsc
		end as ifsc
        from hr_payslip a 
        join hr_payslip_line b 
        on a.id = b.slip_id 
		join hr_employee c 
		on b.employee_id = c.id 
		join hr_contract d
		on d.id = a.contract_id
		where b.code = 'NET' and a.state='done'  and a.company_id = (select id from res_company where 
                currency_id =(select id from res_currency where name='INR'))
       )""" % (self._table))

class SalaryDisburseVerifyReport(models.Model):
    _name = 'kw_salary_disburse_verify_report'
    _description = 'Salary Disburse Report'
    _auto = False

    """ view fields """
    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]
    emp_code = fields.Char(string='Employee Code',related='employee_id.emp_code')
    employee_id = fields.Many2one('hr.employee',string='Employee')
    name = fields.Char(string='Name',related='employee_id.name')
    department_id = fields.Many2one('hr.department',string='Department',related='employee_id.department_id')
    job_id = fields.Many2one('hr.job',string='Designation')
    base_branch_id = fields.Many2one('kw_res_branch', string="location")
    amount = fields.Float(string="Net Pay")
    year = fields.Char(string="Year", size=4)
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    month_int = fields.Integer(string="Month Int")
    state = fields.Char()
    bank = fields.Char("Bank")
    acc_number = fields.Integer("Account Number")
    ifsc = fields.Char("IFSC")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
        select  a.id,c.job_id,a.department_id,c.base_branch_id,date_part('year',a.date_to) as year,CAST(date_part('month',a.date_to)as varchar(10)) as month,
        b.amount as amount,a.state as state,a.employee_id as employee_id, CAST(date_part('month',a.date_to)as INTEGER) as month_int,
		case when a.bank is NULL then (select name from res_bank where id = d.bank_id)
			when a.bank is not Null then a.bank
		end as bank,
		case when a.acc_number is NULL then (select bank_account from hr_contract where id = a.contract_id)
			when a.acc_number is not Null then a.acc_number
		end as acc_number,
        case when a.ifsc is NULL then (select bic from res_bank where id = d.bank_id)
			when a.ifsc is not Null then a.ifsc
		end as ifsc
        from hr_payslip a 
        join hr_payslip_line b 
        on a.id = b.slip_id 
		join hr_employee c 
		on b.employee_id = c.id 
		join hr_contract d
		on d.id = a.contract_id
		where b.code = 'NET' and a.company_id = (select id from res_company where 
                currency_id =(select id from res_currency where name='INR'))
       )""" % (self._table))


    
      
