from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError
from datetime import date, datetime, time
from odoo.addons import decimal_precision as dp


class EmployeePFOthetAdvanceReport(models.Model):
    _name = 'payroll_other_advance_report'
    _description = 'Payroll Other Advance Report'
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
    name = fields.Char(string='Name',related='employee_id.name')
    date_to = fields.Date(string="To Date")
    employee_id = fields.Many2one("hr.employee")
    emp_code = fields.Char(string="Code",related='employee_id.emp_code')
    other_adv = fields.Float(string='Amount',digits=dp.get_precision('Payroll'))
    month_name = fields.Char(compute='compute_month')
    purpose = fields.Char(string="Purpose")

    @api.depends('month')
    def compute_month(self):
        month_dict = {'1': 'January', '2': 'February', '3': 'March', '4': 'April', '5': 'May', '6': 'June', '7': 'July', '8': 'August',
                      '9': 'September', '10': 'October', '11': 'November', '12': 'December'}
        for rec in self:
            if rec.month:
                rec.month_name = month_dict.get(rec.month)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as(
        select row_number() over() as id,
        date_part('year',a.date_to) as year,
        CAST(date_part('month',a.date_to) as varchar(10)) as month,
        a.date_to as date_to,
        b.amount  as  other_adv,
        c.purpose,
        a.employee_id
        from hr_payslip as a
        join hr_payslip_line as b
        on a.id = b.slip_id
        join lunch_expenses as c
        on c.employee_id = b.employee_id and CAST(c.year as VARCHAR) = b.year and CAST(c.month as INTEGER)=b.month and b.code ='OD' and b.amount >0
        
        )""" % (self._table))
