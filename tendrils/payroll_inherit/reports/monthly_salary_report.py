from odoo import fields, models, _, api
from odoo import tools
from datetime import date, datetime, time


class MonthlySalaryReport(models.Model):
    _name = 'kw_monthly_salary_report'
    _description = 'Monthly Salary Report'
    _auto = False

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
    month_int = fields.Integer(string="Month Int")
    basic = fields.Integer( string='Basic')
    hra = fields.Integer( string='HRA')
    conveyance = fields.Integer( string='Conveyance')
    pb = fields.Integer( string='Productivity Bonus')
    cb = fields.Integer( string='Commitment Bonus')
    incentive_allowances = fields.Integer( string='Incentive')
    variable = fields.Integer( string='Variable')
    spl_allowance = fields.Integer( string='Special Allowance')
    equitable_allowance = fields.Integer( string='Equitable Allowance')
    leave_encachment = fields.Integer( string='Leave Encashment')
    city_allowances = fields.Integer( string='City Allowance')
    traning_incentive = fields.Integer( string='Training Incentive')
    er_bonus = fields.Integer( string='Employee Referral Bonus')
    arrear = fields.Integer( string='Arrear')
    final_gross = fields.Integer( string='Final Gross')
    lwop = fields.Integer( string='LWOP')
    salary_adv = fields.Integer( string='Salary Advance')
    other_deduction = fields.Integer( string='Other Advance')
    eepf = fields.Integer( string='EPF Empe')
    epf = fields.Integer( string='EPF Empr')
    esi = fields.Integer( string='ESIE')
    ptd = fields.Integer( string='Prof. Tax')
    gratuity = fields.Integer( string='Gratuity')
    health_insurance_self = fields.Integer( string='Health Insurance Self')
    health_insurance_dependant = fields.Integer( string='Health Insurance for Dependant')
    lunch_expences = fields.Integer( string='Lunch Expenses')
    ctc = fields.Integer(string='CTC')
    net = fields.Integer(string='NET Amount (In Rs.)')
    ltc = fields.Integer(string='LTC')
    pp = fields.Integer(string='Prof Persuit')
    tds  = fields.Integer(string='TDS')
    employee_id = fields.Many2one('hr.employee')
    name = fields.Char(related='employee_id.name')
    emp_code = fields.Char(related='employee_id.emp_code')
    back_date_entry = fields.Boolean()
    transaction_date = fields.Date()
    date_to =  fields.Date()
    company_id = fields.Many2one('res.company')
    budget_type = fields.Selection([('project', 'Project Budget'), ('treasury', 'Treasury Budget')],string="Budget Type")
    nps = fields.Integer(string='NPS')

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year + 7, 2010, -1)]


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
           
      select row_number() over(order by year,month,a.employee_id) as id,a.employee_id as employee_id,
        cast(max(date_part('year',a.date_to)) as varchar(10)) as year,
        cast(max(date_part('month',a.date_to)) as varchar(10)) as month,
        CAST (max(date_part('month',a.date_to) ) AS INTEGER) as month_int,
        a.date_to as date_to,
        max(e.budget_type) as budget_type,
        a.back_date_entry,a.transaction_date,
        sum(q.amount) FILTER (WHERE q.code = 'BASIC' ) as basic,
        sum(q.amount) FILTER (WHERE q.code = 'HRAMN' ) as hra,
        sum(q.amount) FILTER (WHERE q.code = 'TCA' ) as conveyance,
        sum(q.amount) FILTER (WHERE q.code = 'PBONUS' ) as pb,
        sum(q.amount) FILTER (WHERE q.code = 'CBONUS' ) as cb,
        sum(q.amount) FILTER (WHERE q.code = 'LTC' ) as ltc,
        sum(q.amount) FILTER (WHERE q.code = 'PP' ) as pp,
        sum(q.amount) FILTER (WHERE q.code = 'INC' ) as incentive_allowances,
        sum(q.amount) FILTER (WHERE q.code = 'VAR' ) as variable,
        sum(q.amount) FILTER (WHERE q.code = 'SALW' ) as spl_allowance,
        sum(q.amount) FILTER (WHERE q.code = 'EALW' ) as equitable_allowance,
        sum(q.amount) FILTER (WHERE q.code = 'LE' ) as leave_encachment,
        sum(q.amount) FILTER (WHERE q.code = 'CBDA' ) as city_allowances,
        sum(q.amount) FILTER (WHERE q.code = 'TINC' ) as traning_incentive,
        sum(q.amount) FILTER (WHERE q.code = 'ERBONUS' ) as er_bonus,
        sum(q.amount) FILTER (WHERE q.code = 'ARRE' ) as arrear,
       - sum(q.amount) FILTER (WHERE q.code = 'LWOP' ) as lwop,
       (sum(q.amount) FILTER (WHERE q.code = 'GROSS' ) - sum(q.amount) FILTER (WHERE q.code = 'LWOP' )) as final_gross,
        sum(q.amount) FILTER (WHERE q.code = 'SALADV' ) as salary_adv,
        sum(q.amount) FILTER (WHERE q.code = 'OD' ) as other_deduction,
        sum(q.amount) FILTER (WHERE q.code = 'EEPF' ) as eepf,
        sum(a.employer_pf) FILTER (WHERE q.code = 'EEPF' ) as epf,
        sum(q.amount) FILTER (WHERE q.code = 'ESI' ) as esi,
        sum(q.amount) FILTER (WHERE q.code = 'PTD' ) as ptd,
        sum(q.amount) FILTER (WHERE q.code = 'TDS' ) as tds,
        sum(q.amount) FILTER (WHERE q.code = 'CMT' ) as health_insurance_self,
        sum(q.amount) FILTER (WHERE q.code = 'HID' ) as health_insurance_dependant,
        sum(q.amount) FILTER (WHERE q.code = 'FC' ) as lunch_expences,
        sum(q.amount) FILTER (WHERE q.code = 'NPS' ) as nps,
        sum(q.amount) FILTER (WHERE q.code = 'NET' ) as net,
        sum(q.amount) FILTER (WHERE q.code = 'CTC' ) as ctc,
        a.company_id as company_id,
        case when sum(q.amount) FILTER (WHERE q.code = 'GROSS') = sum(q.amount) FILTER (WHERE q.code = 'CTC') or
    sum(q.amount) FILTER (WHERE q.code = 'GROSS') +  sum(q.amount) FILTER (WHERE q.code = 'BASIC') *(12/100) = sum(q.amount) FILTER (WHERE q.code = 'CTC') THEN 0
	else round((sum(q.amount) FILTER (WHERE q.code = 'BASIC') * 4.81/ 100)) end as gratuity
        from hr_payslip a join hr_payslip_line as q on a.id = q.slip_id
        join hr_employee e on e.id = a.employee_id
        where a.state='done' and a.company_id = 1
        group by year,month,a.employee_id,a.back_date_entry,a.transaction_date,a.date_to,a.company_id
            )""" % (self._table))