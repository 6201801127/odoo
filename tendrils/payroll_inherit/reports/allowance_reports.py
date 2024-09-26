from odoo import fields, models, _, api
from odoo import tools
from datetime import date, datetime, time


class AllowanceAllocationReport(models.Model):
    _name = 'kw_allowance_allocation_report'
    _description = 'Allowance Allocation Report'
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
    year = fields.Selection(string='Year', selection='_get_year_list', default=str(date.today().year))
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    month_int = fields.Integer(string="Month Int")
    incentive = fields.Integer(string="Incentive")
    city_compensatory_allowance = fields.Integer(string="City Compensatory Allowance")
    leave_encashment = fields.Integer(string="Leave Encashment")
    employee_referral_bonus = fields.Integer(string="Employee Referral Bonus")
    equitable_allowance = fields.Integer(string="Equitable Allowance")
    training_incentive = fields.Integer(string="Training Incentive")
    special_allwance = fields.Integer(string="Special Allowance")
    variable = fields.Integer(string="Variable")
    arrear = fields.Integer(string="Arrears")
    total = fields.Integer(string="Total")
    department = fields.Many2one('hr.department', string="Department")
    employment_type = fields.Many2one('kwemp_employment_type', string='Employment Type')
    location = fields.Many2one('kw_res_branch', string="location")

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year + 7, 2010, -1)]
    

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            select row_number() over(order by month,year,b.department_id, b.employement_type) as id, a.month as month,a.year as year, b.department_id as department, b.job_branch_id as location, b.employement_type as employment_type,
            sum(a.amount)  FILTER (WHERE a.allowance = (select  id from hr_salary_rule where code = 'INC')) as incentive,
            sum(a.amount)  FILTER (WHERE a.allowance = (select  id from hr_salary_rule where code = 'CBDA')) as city_compensatory_allowance,
            sum(a.amount)  FILTER (WHERE a.allowance = (select  id from hr_salary_rule where code = 'LE')) as leave_encashment,
            sum(a.amount)  FILTER (WHERE a.allowance = (select  id from hr_salary_rule where code = 'ARRE')) as arrear,
            sum(a.amount)  FILTER (WHERE a.allowance = (select  id from hr_salary_rule where code = 'ERBONUS')) as employee_referral_bonus,
            sum(a.amount)  FILTER (WHERE a.allowance = (select  id from hr_salary_rule where code = 'VAR')) as variable,
            sum(a.amount)  FILTER (WHERE a.allowance = (select  id from hr_salary_rule where code = 'EALW')) as equitable_allowance,
            sum(a.amount)  FILTER (WHERE a.allowance = (select  id from hr_salary_rule where code = 'TINC')) as training_incentive,
            sum(a.amount)  FILTER (WHERE a.allowance = (select  id from hr_salary_rule where code = 'SALW')) as special_allwance,
            sum(a.amount) as total,CAST (a.month AS INTEGER) as month_int


            from allowance_allocation_master a join hr_employee b on a.employee = b.id 
            group by month,year,b.department_id,location,b.job_branch_id,b.employement_type
            order by month,year,b.department_id

            )""" % (self._table))

      
    # select row_number() over() as id, a.month as month,a.year as year, b.department_id as department, b.job_branch_id as location, b.employement_type as employment_type,
    # case when allowance = (select id from hr_salary_rule where name = 'Incentive') then a.amount else 0 end as incentive,
    # case when allowance = (select id from hr_salary_rule where name = 'City Compensatory Allowance') then a.amount else 0 end as city_compensatory_allowance,
    # case when allowance = (select id from hr_salary_rule where name = 'Leave Encashment') then a.amount else 0 end as leave_encashment,
    # case when allowance = (select id from hr_salary_rule where name = 'Employee Referral Bonus') then a.amount else 0 end as employee_referral_bonus,
    # case when allowance = (select id from hr_salary_rule where name = 'Equitable Allowance') then a.amount else 0 end as equitable_allowance,
    # case when allowance = (select id from hr_salary_rule where name = 'Training Incentive') then a.amount else 0 end as training_incentive,
    # case when allowance = (select id from hr_salary_rule where name = 'Special Allowance') then a.amount else 0 end as special_allwance,
    # case when allowance = (select id from hr_salary_rule where name = 'Arrears') then a.amount else 0 end as arrear,
    # case when allowance = (select id from hr_salary_rule where name = 'Variable') then a.amount else 0 end as variable,a.amount as total

    # from allowance_allocation_master a join hr_employee b on a.employee = b.id 