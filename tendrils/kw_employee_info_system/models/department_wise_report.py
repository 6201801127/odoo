from odoo import fields, models, api, tools

class DepartmentWiseReport(models.Model):
    _name = 'department_wise_report'
    _description = 'Departmentwise Report'
    _auto = False

    male = fields.Integer()
    female = fields.Integer()
    
    department = fields.Char()
    date_of_joining = fields.Date()
    fiscal_year = fields.Many2one('account.fiscalyear',string='Fiscal Year')

    quarter = fields.Char()
    month = fields.Char()
    male_to_female_ratio = fields.Char()
    month_year  = fields.Char()
    quarterly = fields.Selection([
        ('1', 'Q1'),
        ('2', 'Q2'),
        ('3', 'Q3'),
        ('4', 'Q4'),
    ], string="Quaterly")
    year = fields.Char()
    
    
    
    
            
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s AS (
select 
row_number() over(order by DATE_TRUNC('month', hr.date_of_joining),DATE_TRUNC('quarter', hr.date_of_joining) ) AS id,
 (
    SELECT 
      id 
    FROM 
      account_fiscalyear 
    WHERE 
      hr.date_of_joining >= date_start AND hr.date_of_joining <= date_stop
  ) AS fiscal_year,
 DATE_TRUNC('quarter', hr.date_of_joining) AS quarter,
 DATE_TRUNC('month', hr.date_of_joining) AS month,
 date_part('year', date_of_joining) as year, 
 case
  when date_part('quarter', date_of_joining) = 1 then 'Q1'  || ',' || date_part('year', date_of_joining)
  when  date_part('quarter', date_of_joining) = 2 then 'Q2'  || ',' || date_part('year', date_of_joining)
  when date_part('quarter', date_of_joining) = 3 then 'Q3'  || ',' || date_part('year', date_of_joining)
  when  date_part('quarter', date_of_joining) = 4 then 'Q4'  || ',' || date_part('year', date_of_joining)
  end as quarterly,
  
   TO_CHAR(date_of_joining, 'Mon YYYY') AS month_year,
 dept.name as department,date_of_joining,count(*) FILTER (WHERE hr.gender = 'male' ) as male,count(*) FILTER (WHERE hr.gender = 'female' ) as female from hr_department as dept
 
join hr_employee as hr on dept.id=hr.department_id
join kw_hr_department_type as type on type.id = dept.dept_type
where type.code='department'
group by fiscal_year,department,date_of_joining

           



            )""" % (self._table))
        