from odoo import fields, models, _, api
from odoo import tools
from datetime import date, datetime, time


class BatchWiseBulkReport(models.Model):
    _name = 'batch_wise_bulk_report'
    _description = 'Batch Wise Bulk Report'
    _order = 'rule_sequence'
    _auto = False

    MONTH_LIST = [

        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]

    year_data = fields.Selection(string='Year', selection='_get_year_list', default=str(date.today().year))
    month_data = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    current_month = fields.Boolean(search="_search_current_month", compute='_compute_current_month')
    salary_rule_type = fields.Char( string=' ',compute='_rule_category')
    salary_rule = fields.Char( string='Salary Components')
    treasury_budget = fields.Float( string='Treasury Amount')
    project_amount = fields.Float( string='Project Amount')
    total = fields.Float( string='Total Amount',compute='_calculate_total_budget')
    rule_sequence = fields.Integer()
    
    @api.multi
    def _compute_current_month(self):
        for record in self:
            pass

    @api.multi
    def _search_current_month(self, operator, value):
        month = date.today().month
        year = date.today().year
        return ['&', ('month', '=', str(month)), ('year', '=', str(year))]
    
    
    @api.depends('salary_rule')
    def _rule_category(self):
    	for rec in self:
            if rec.salary_rule == 'Basic Salary':
                    rec.salary_rule_type = 'Earnings'
            if rec.salary_rule == 'LWOP':
                rec.salary_rule_type = 'Deduction'
    
    @api.onchange('treasury_budget','project_amount')
    def _calculate_total_budget(self):
        for rec in self:
            rec.total = rec.treasury_budget + rec.project_amount

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year + 7, 2010, -1)]


    @api.model_cr
    def init(self):
        year_data = self.env.context.get('year_data') 
        company = self.env.context.get('company') if self.env.context.get('company') else 1
        month_data = int(self.env.context.get('month_data')) if self.env.context.get('month_data') else 11
        payslip_run_id = int(self.env.context.get('payslip_run_id')) if self.env.context.get('payslip_run_id') else 1 
        
        tools.drop_view_if_exists(self.env.cr, self._table)

        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
     with a as (select row_number() over() as id,sum(l.amount) FILTER (WHERE e.budget_type ='treasury') 
							as treasury_budget,
	   		sum(l.amount) FILTER (WHERE e.budget_type ='project') 
							as project_amount,
			l.year as year_data,l.month as month_data,l.name as salary_rule,sequence as rule_sequence from hr_payslip_line l join hr_payslip h  on l.slip_id = h.id
	join hr_employee e on h.employee_id = e.id
	where l.year='{year_data}' and l.month={month_data} and l.code not in ('CTC') and h.company_id = {company} and  payslip_run_id = {payslip_run_id} group by l.year,l.month,l.name,sequence),
	
 b as (select (select 1000) as id,count(e.id) FILTER (WHERE e.budget_type ='treasury') 
							as treasury_budget,
	   	count(h.id) FILTER (WHERE e.budget_type ='project') 
							as project_amount,
		l.year as year_data,l.month as month_data,(select 'Total Employees Count') as salary_rule,(select 700) as rule_sequence 
		from hr_payslip_line l join hr_payslip h  on l.slip_id = h.id
		join hr_employee e on h.employee_id = e.id
		where l.year='{year_data}' and l.month={month_data} and l.code = 'CTC' and h.company_id = {company} and  payslip_run_id = {payslip_run_id} group by l.year,l.month,l.name,sequence),
		
	 c as (select 
	(select 600) as id,sum(l.amount) FILTER (WHERE e.budget_type ='treasury' 
							and l.code in ('LWOP','OD','EEPF','ESI','PTD','TDS','FC','SALADV','CMT','HID')) 
							as treasury_budget,			 
	sum(l.amount) FILTER (WHERE e.budget_type ='project'
							and l.code in ('LWOP','OD','EEPF','ESI','PTD','TDS','FC','SALADV','CMT','HID')) 
							as project_amount,
	l.year as year_data,l.month as month_data,(select 'Total Deduction') as salary_rule,(select 499) as rule_sequence from hr_payslip_line l join hr_payslip h  on l.slip_id = h.id
	join hr_employee e on h.employee_id = e.id
    where l.year='{year_data}' and l.month={month_data} and h.company_id = {company} and  payslip_run_id = {payslip_run_id}
	group by l.year,l.month),
	
   	e as (WITH d AS (select  case
	when sum(l.amount) FILTER (WHERE l.code = 'GROSS') = sum(l.amount) FILTER (WHERE l.code = 'CTC') or 
    sum(l.amount) FILTER (WHERE l.code = 'GROSS') + max(h.employer_pf) = sum(l.amount) FILTER (WHERE l.code = 'CTC') THEN 0
	else round((sum(l.amount) FILTER (WHERE l.code = 'BASIC') * 4.81/ 100))
	end as gratuity,l.year as year_data,l.month as month_data,l.employee_id 
	from hr_payslip_line l
    join hr_payslip h on h.id=l.slip_id  where l.year='{year_data}' and l.month={month_data} and h.company_id = {company} and  payslip_run_id = {payslip_run_id} group by l.year,l.month,l.employee_id)
	
	select (select 601) as id,sum(gratuity) FILTER (WHERE e.budget_type ='treasury') 
							as treasury_budget,
							sum(gratuity) FILTER (WHERE e.budget_type ='project') 
							as project_amount,d.year_data as year_data,d.month_data as month_data,(select 'Gratuity') as salary_rule,(select 500) as rule_sequence
							from d join hr_employee e on d.employee_id = e.id
							group by d.year_data,d.month_data)
							
SELECT * FROM a
UNION 
SELECT * FROM b
UNION
SELECT * FROM c
UNION
SELECT * FROM e

		)""" % (self._table))


class BatchWiseBulkReport(models.Model):
    _name = 'batch_wise_bulk_verified_report'
    _description = 'Batch Compiled Salary Verified Report'
    _order = 'rule_sequence'
    _auto = False

    MONTH_LIST = [

        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]

    year_data = fields.Selection(string='Year', selection='_get_year_list', default=str(date.today().year))
    month_data = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    current_month = fields.Boolean(search="_search_current_month", compute='_compute_current_month')
    salary_rule_type = fields.Char( string=' ',compute='_rule_category')
    salary_rule = fields.Char( string='Salary Components')
    treasury_budget = fields.Float( string='Treasury Amount')
    project_amount = fields.Float( string='Project Amount')
    total = fields.Float( string='Total Amount',compute='_calculate_total_budget')
    rule_sequence = fields.Integer()
    
    @api.multi
    def _compute_current_month(self):
        for record in self:
            pass

    @api.multi
    def _search_current_month(self, operator, value):
        month = date.today().month
        year = date.today().year
        return ['&', ('month', '=', str(month)), ('year', '=', str(year))]
    
    
    @api.depends('salary_rule')
    def _rule_category(self):
    	for rec in self:
            if rec.salary_rule == 'Basic Salary':
                    rec.salary_rule_type = 'Earnings'
            if rec.salary_rule == 'LWOP':
                rec.salary_rule_type = 'Deduction'
    
    @api.onchange('treasury_budget','project_amount')
    def _calculate_total_budget(self):
        for rec in self:
            rec.total = rec.treasury_budget + rec.project_amount

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year + 7, 2010, -1)]


    @api.model_cr
    def init(self):
        year_data = self.env.context.get('year_data') 
        company = self.env.context.get('company') if self.env.context.get('company') else 1
        month_data = int(self.env.context.get('month_data')) if self.env.context.get('month_data') else 11
        tools.drop_view_if_exists(self.env.cr, self._table)
        payslip_run_id = int(self.env.context.get('payslip_run_id')) if self.env.context.get('payslip_run_id') else 1 
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
     with a as (select row_number() over() as id,sum(l.amount) FILTER (WHERE e.budget_type ='treasury') 
							as treasury_budget,
	   		sum(l.amount) FILTER (WHERE e.budget_type ='project' ) 
							as project_amount,
			l.year as year_data,l.month as month_data,l.name as salary_rule,sequence as rule_sequence from hr_payslip_line l join hr_payslip h  on l.slip_id = h.id
	join hr_employee e on h.employee_id = e.id
	where l.year='{year_data}' and l.month={month_data} and l.code not in ('CTC') and h.state='done' and h.company_id = {company} and  payslip_run_id = {payslip_run_id} group by l.year,l.month,l.name,sequence),
	
 b as (select (select 1000) as id,count(e.id) FILTER (WHERE e.budget_type ='treasury') 
							as treasury_budget,
	   	count(h.id) FILTER (WHERE e.budget_type ='project') 
							as project_amount,
		l.year as year_data,l.month as month_data,(select 'Total Employees Count') as salary_rule,(select 700) as rule_sequence 
		from hr_payslip_line l join hr_payslip h  on l.slip_id = h.id
		join hr_employee e on h.employee_id = e.id
		where l.year='{year_data}' and l.month={month_data} and l.code = 'CTC' and h.state='done' and h.company_id = {company} and  payslip_run_id = {payslip_run_id} group by l.year,l.month,l.name,sequence),
		
	 c as (select 
	(select 600) as id,sum(l.amount) FILTER (WHERE e.budget_type ='treasury'
							and l.code in ('LWOP','OD','EEPF','ESI','PTD','TDS','FC','SALADV','CMT','HID')) 
							as treasury_budget,			 
	sum(l.amount) FILTER (WHERE e.budget_type ='project'
							and l.code in ('LWOP','OD','EEPF','ESI','PTD','TDS','FC','SALADV','CMT','HID')) 
							as project_amount,
	l.year as year_data,l.month as month_data,(select 'Total Deduction') as salary_rule,(select 499) as rule_sequence from hr_payslip_line l join hr_payslip h  on l.slip_id = h.id
	join hr_employee e on h.employee_id = e.id
    where l.year='{year_data}' and l.month={month_data} and h.state='done' and h.company_id = {company} and  payslip_run_id = {payslip_run_id}
	group by l.year,l.month),
	
   	e as (WITH d AS (select  case
	when sum(l.amount) FILTER (WHERE l.code = 'GROSS') = sum(l.amount) FILTER (WHERE l.code = 'CTC') or 
    sum(l.amount) FILTER (WHERE l.code = 'GROSS') + max(h.employer_pf) = sum(l.amount) FILTER (WHERE l.code = 'CTC') THEN 0
	else round((sum(l.amount) FILTER (WHERE l.code = 'BASIC') * 4.81/ 100))
	end as gratuity,l.year as year_data,l.month as month_data,l.employee_id 
	from hr_payslip_line l
    join hr_payslip h on h.id=l.slip_id  where l.year='{year_data}' and l.month={month_data} and h.state='done' and h.company_id = {company} and  payslip_run_id = {payslip_run_id} group by l.year,l.month,l.employee_id)
	
	select (select 601) as id,sum(gratuity) FILTER (WHERE e.budget_type ='treasury' ) 
							as treasury_budget,
							sum(gratuity) FILTER (WHERE e.budget_type ='project') 
							as project_amount,d.year_data as year_data,d.month_data as month_data,(select 'Gratuity') as salary_rule,(select 500) as rule_sequence
							from d join hr_employee e on d.employee_id = e.id
							group by d.year_data,d.month_data)
SELECT * FROM a
UNION 
SELECT * FROM b
UNION
SELECT * FROM c
UNION
SELECT * FROM e

		)""" % (self._table))