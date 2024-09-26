from odoo import fields, models, _, api
from odoo import tools
from datetime import date, datetime, time
from odoo.addons import decimal_precision as dp




class PayrollTDSReport(models.Model):
    _name = 'payroll_tds_report'
    _description = 'TDS Report'
    _auto = False

    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]

    date_to=fields.Date(string="To Date")
    year = fields.Char(string="Year", size=4)
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    name = fields.Char(string="Employee's Name",related='employee_id.name')
    emp_code = fields.Char(string='Emp ID',related='employee_id.emp_code')
    employee_id = fields.Many2one('hr.employee',string='Employee Name')
    tds_amount = fields.Float(string='TAX Deducted Amt.',digits=dp.get_precision('Payroll'))
    month_name = fields.Char(compute='compute_month')
    pan_number = fields.Char(string='PAN', compute='_compute_pan_num')
    final_gross = fields.Float(string='Final Gross Salary',digits=dp.get_precision('Payroll'))


    @api.depends('employee_id')
    def _compute_pan_num(self):
        for rec in self:
            for record in rec.employee_id.identification_ids:
                if record.name == '1':
                    rec.pan_number = record.doc_number



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
            sum(b.amount) FILTER (WHERE b.code = 'TDS') as tds_amount,
            sum(b.amount) FILTER (WHERE b.code = 'GROSS') as final_gross,
            a.employee_id as employee_id
            from hr_payslip a 
            join hr_payslip_line b
            on a.id = b.slip_id join hr_employee c on a.employee_id = c.id
            where b.code in ('TDS','GROSS') and a.state='done'
            group by a.date_to,a.employee_id)""" % (self._table))

class PayrollTDSVerifyReport(models.Model):
    _name = 'payroll_tds_verify_report'
    _description = 'TDS Report'
    _auto = False

    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]

    date_to=fields.Date(string="To Date")
    year = fields.Char(string="Year", size=4)
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    name = fields.Char(string="Employee's Name",related='employee_id.name')
    emp_code = fields.Char(string='Emp ID',related='employee_id.emp_code')
    employee_id = fields.Many2one('hr.employee',string='Employee Name')
    tds_amount = fields.Float(string='TAX Deducted Amt.',digits=dp.get_precision('Payroll'))
    month_name = fields.Char(compute='compute_month')
    pan_number = fields.Char(string='PAN', compute='_compute_pan_num')
    final_gross = fields.Float(string='Final Gross Salary',digits=dp.get_precision('Payroll'))



    @api.depends('employee_id')
    def _compute_pan_num(self):
        for rec in self:
            for record in rec.employee_id.identification_ids:
                if record.name == '1':
                    rec.pan_number = record.doc_number



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
            sum(b.amount) FILTER (WHERE b.code = 'TDS') as tds_amount,
            sum(b.amount) FILTER (WHERE b.code = 'GROSS') as final_gross,
            a.employee_id as employee_id
            from hr_payslip a 
            join hr_payslip_line b
            on a.id = b.slip_id join hr_employee c on a.employee_id = c.id
            where b.code in ('TDS','GROSS') and a.state='done'
            group by a.date_to,a.employee_id)""" % (self._table))

