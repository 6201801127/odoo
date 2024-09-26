from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError
from datetime import date, datetime, time


class ProfessionalTaxReport(models.Model):
    _name = 'professional_tax_report'
    _description = 'Professional Tax Deduction Report'
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
    # epf = fields.Float(string="EPF")
    # esi = fields.Float(string="ESI")
    pt = fields.Float(string="Professional Tax")
    gross = fields.Float(string="Final Gross")
    date_to = fields.Date()
    employement_type = fields.Many2one('kwemp_employment_type', string="Type of Employment",related='employee_id.employement_type')
    

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
        select row_number() over() as id,date_part('year',a.date_to) as year,CAST(date_part('month',a.date_to) as varchar(10)) as month,a.date_to as date_to,sum(b.amount)   FILTER (WHERE b.code = 'PTD') as  pt,
        sum(b.amount)   FILTER (WHERE b.code = 'GROSS') as  gross,
        a.employee_id as employee_id
        from hr_payslip a 
        join hr_payslip_line b 
        on a.id = b.slip_id join hr_employee c on b.employee_id = c.id
        where 
        a.company_id = (select id from res_company where 
        currency_id =(select id from res_currency where name='INR'))
		group by a.date_to,a.employee_id
        )""" % (self._table))

# CAST(a.month as varchar(10)) as month
        #  WITH    cte1 AS
        # (
        # select a.id,date_part('year',a.date_to) as year,date_part('month',a.date_to) as month,a.date_to as date_to,b.amount,a.employee_id
        # from hr_payslip a 
        # join hr_payslip_line b 
        # on a.id = b.slip_id join hr_employee c on b.employee_id = c.id where b.code = 'PTD' and state='done'
        # ),
        # cte2 AS
        # (
        # select a.id,date_part('year',a.date_to) as year,date_part('month',a.date_to) as month,a.date_to as date_to,b.amount,a.employee_id
        # from hr_payslip a 
        # join hr_payslip_line b 
        # on a.id = b.slip_id join hr_employee c on b.employee_id = c.id where b.code = 'EEPF' and state='done'
        # ),
		#         cte3 AS
        # (
        # select a.id,date_part('year',a.date_to) as year,date_part('month',a.date_to) as month,a.date_to as date_to,b.amount,a.employee_id
        # from hr_payslip a 
        # join hr_payslip_line b 
        # on a.id = b.slip_id join hr_employee c on b.employee_id = c.id where b.code = 'ESI' and state='done'
        # )
        # select row_number() over() as id, cast(a.year as varchar(10)) as year, CAST(a.month as varchar(10)) as month,
        # a.date_to as date_to,

        # sum(a.amount) as pt,sum(b.amount) as epf ,sum(c.amount) as esi, a.employee_id as employee_id
        # from cte1 a 
        # join cte2 b on a.id = b.id 
        # join cte3 c on a.id = c.id 
		
        # group by a.month,a.year,a.employee_id,a.date_to
    
   
   