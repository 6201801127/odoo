from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError
from datetime import date, datetime, time


class KwCtcReport(models.Model):
    _name = 'kw_ctc_report'
    _description = 'CTC Report'
    _auto = False
    # _rec_name = "display_name"

    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]
    year = fields.Selection(string='Year', selection='_get_year_list', default=str(date.today().year))
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    department_id = fields.Many2one('hr.department', string="Department")
    # division = fields.Many2one('hr.department', string="Division")
    # employement_type = fields.Many2one('kwemp_employment_type',  string="Type of Employment")
    # emp_count = fields.Integer()
    # ctc = fields.Float(string='CTC')
    location = fields.Many2one('kw_res_branch', string="location")
    fte_count = fields.Integer(string='Regular Employees')
    fte_amount = fields.Float(string='Amount')
    ret_project_count = fields.Integer(string='RET Project Employees')
    ret_project_amount = fields.Float(string='Amount')
    ret_overhead_count = fields.Integer(string='RET Overhead Employees')
    ret_overhead_amount = fields.Float(string='Amount')
    outsourced_count = fields.Integer(string='Outsourced Employees')
    outsourced_amount = fields.Float(string='Amount')
    contractual_count = fields.Integer(string='Contractual Employees')
    contractual_amount = fields.Float(string='Amount')
    total = fields.Float(string='Total')
    month_int = fields.Integer(string="Month Int")
    

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year + 7, 2010, -1)]

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (

       
	select row_number() over() as id,e.job_branch_id as location,e.department_id as department_id,cast(max(date_part('year',
	a.date_to)) as varchar(10)) as year,cast(max(date_part('month',a.date_to)) as varchar(10)) as month,
    CAST (max(date_part('month',a.date_to) ) AS INTEGER)
	as month_int,
	
    COUNT(*) FILTER (WHERE c.code = 'P' ) AS fte_count,
    sum(q.amount) FILTER (WHERE c.code = 'P' ) as fte_amount,
        
	COUNT(*) FILTER (WHERE c.code = 'C' ) AS ret_project_count,
    sum(q.amount) FILTER (WHERE c.code = 'C' ) as ret_project_amount,

    COUNT(*) FILTER (WHERE c.code = 'S') AS ret_overhead_count,
    sum(q.amount) FILTER (WHERE c.code = 'S') as ret_overhead_amount,
        
    COUNT(*) FILTER (WHERE c.code = 'O' ) AS outsourced_count,
    sum(q.amount) FILTER (WHERE c.code = 'O' ) as outsourced_amount,
        
	COUNT(*) FILTER (WHERE c.code = 'CE') AS contractual_count,
    sum(q.amount) FILTER (WHERE c.code = 'CE') as contractual_amount,

    sum (q.amount) as total
    
    from hr_employee e join hr_payslip as a on a.employee_id = e.id
    join  hr_payslip_line as q on a.id = q.slip_id
    join  kwemp_employment_type c on e.employement_type = c.id 
    where q.code = 'CTC' and a.state='done' and 
    a.company_id = (select id from res_company where 
    currency_id =(select id from res_currency where name='INR'))
    group by e.department_id,e.job_branch_id,a.date_to
    
            )""" % (self._table))


""" Don't Delete without asking , It can be used for future reference """

#  select row_number() over() as id,a.branch_id as location,a.department_id as department_id,cast(max(date_part('year',a.date_to)) as varchar(10)) as year,cast(max(date_part('month',a.date_to)) as varchar(10)) as month,
#         COUNT(*) FILTER (WHERE c.code = 'P' ) AS fte_count,
#         sum(q.amount) FILTER (WHERE c.code = 'P' ) as fte_amount,

#         COUNT(*) FILTER (WHERE c.code = 'C' ) AS ret_project_count,
#         sum(q.amount) FILTER (WHERE c.code = 'C' ) as ret_project_amount,

#         COUNT(*) FILTER (WHERE c.code = 'S') AS ret_overhead_count,
#         sum(q.amount) FILTER (WHERE c.code = 'S') as ret_overhead_amount,

#         COUNT(*) FILTER (WHERE c.code = 'O' ) AS outsourced_count,
#         sum(q.amount) FILTER (WHERE c.code = 'O' ) as outsourced_amount,

#         COUNT(*) FILTER (WHERE c.code = 'CE') AS contractual_count,
#         sum(q.amount) FILTER (WHERE c.code = 'CE') as contractual_amount,

#         sum (q.amount) as total

#         from hr_payslip as a
#         join  hr_payslip_line as q on a.id = q.slip_id join kwemp_employment_type c on a.employement_type = c.id where q.code = 'CTC' and state='done'
#         group by a.department_id,a.branch_id
