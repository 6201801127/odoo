from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError
from datetime import date, datetime, time


class NetCtcReport(models.Model):
    _name = 'net_ctc_report'
    _description = 'NET/CTC Report'
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
    division = fields.Many2one('hr.department', string="Division")
    employement_type = fields.Many2one('kwemp_employment_type', string="Type of Employment")
    emp_count = fields.Integer(string='Total No. Of Employee')
    net = fields.Float(string='NET Amount (In Rs.)')
    ctc = fields.Float(string='CTC Amount (In Rs.)')
    month_int = fields.Integer(string="Month Int")
    
   
    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year + 7, 2010, -1)]

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (

        WITH    cte1 AS
        (
        select a.id,date_part('year',a.date_to) as year,date_part('month',a.date_to) as month,c.department_id,
        c.division,c.employement_type,b.amount 
        from hr_payslip a 
        join hr_payslip_line b 
        on a.id = b.slip_id join hr_employee c on b.employee_id = c.id where b.code = 'NET' and state='done' and 
        a.company_id = (select id from res_company where 
        currency_id =(select id from res_currency where name='INR'))
        ),
        cte2 AS
        (
        select a.id,date_part('year',a.date_to) as year,date_part('month',a.date_to) as month,c.department_id,
        c.division,c.employement_type,b.amount 
        from hr_payslip a 
        join hr_payslip_line b 
        on a.id = b.slip_id join hr_employee c on b.employee_id = c.id where b.code = 'CTC' and state='done'
        and 
        a.company_id = (select id from res_company where 
        currency_id =(select id from res_currency where name='INR'))
        )
        select row_number() over(order by a.department_id,a.division,a.employement_type) as id, cast(a.year as varchar(10)) as year, CAST(a.month as varchar(10)) as month,
        a.department_id as department_id,a.division as division,a.employement_type as employement_type,
        count(a.id) as emp_count,sum(a.amount) as net,sum(b.amount) as ctc ,CAST (a.month AS INTEGER) as month_int
        from cte1 a 
        join cte2 b on a.id = b.id 
        group by a.month,a.year,a.department_id,a.division,a.employement_type
    
            )""" % (self._table))
