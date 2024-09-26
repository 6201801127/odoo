from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError
from datetime import date, datetime, time


class EmployeePFReport(models.Model):
    _name = 'employee_esi_report'
    _description = 'ESI Deduction Report'
    _auto = False


   
    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]
    year = fields.Char(string='Year')
    month = fields.Selection(MONTH_LIST, string='Month')
    employee_id = fields.Many2one("hr.employee")
    name = fields.Char(string="Name",related='employee_id.name')
    emp_code = fields.Char(string="Code",related='employee_id.emp_code')
    department_id = fields.Many2one("hr.department",string="Department",related='employee_id.department_id')
    job_id = fields.Many2one("hr.job",string="Designation",related='employee_id.job_id')
    emp_esi = fields.Float(string="Employee ESI")
    empr_esi = fields.Float(string="Employer ESI")
    date_to = fields.Date()

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
        select a.id,date_part('year',a.date_to) as year,CAST(date_part('month',a.date_to) as varchar(10)) as month,a.date_to as date_to,b.amount as emp_esi,b.amount as empr_esi,a.employee_id as employee_id
        from hr_payslip a 
        join hr_payslip_line b 
        on a.id = b.slip_id join hr_employee c on b.employee_id = c.id where b.code = 'ESI' and state='done'
        )""" % (self._table))

