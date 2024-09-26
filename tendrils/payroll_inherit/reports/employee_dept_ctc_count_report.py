from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError
from datetime import date, datetime, time


class DepratmentWiseCTCCountReport(models.Model):
    _name = 'depratment_wise_ctc_count_report'
    _description = 'Depratment Wise CTC Count Report'
    _auto = False

    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]
    year = fields.Selection(string='Year', selection='_get_year_list')
    month = fields.Selection(MONTH_LIST, string='Month')
    department = fields.Many2one('hr.department', string="Dept")
    division = fields.Many2one('hr.department', string="Division")
    practise = fields.Many2one('hr.department', string="Practice")
    emp_count = fields.Integer(string='Count')
    ctc = fields.Float(string='Value Rs.')
    month_int = fields.Integer(string="Month Int")

    
    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year + 7, 2010, -1)]

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            select 
                row_number() over(order by p.date_to desc) as id,
                cast(max(date_part('year',p.date_to)) as varchar(10)) as year,
                cast(max(date_part('month',p.date_to)) as varchar(10)) as month,
                CAST (max(date_part('month',p.date_to) ) AS INTEGER) as month_int,
				hr.department_id as department,
				hr.division as division,
				hr.section as practise,
				count(p.id) FILTER (WHERE p.id=line.slip_id and line.code ='CTC') as emp_count,
				sum(line.amount)  FILTER (WHERE line.code ='CTC' and p.id=line.slip_id) as ctc
                
                FROM hr_payslip p
				join hr_employee hr on p.employee_id=hr.id
 				join hr_payslip_line line on p.id=line.slip_id 
				where   p.state='done'
                GROUP BY hr.department_id, hr.division, hr.section,p.date_to
            )""" % (self._table))
