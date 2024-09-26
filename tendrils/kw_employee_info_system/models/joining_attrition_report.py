# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools


class fiscalyearjoiningreport(models.Model):
    _name = 'fiscal_year_wise_joining_report'
    _description = 'Joining Report'
    _auto = False
    _order = 'id desc'

    MONTH_LIST = [
        (1, 'January'), (2, 'February'),
        (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'),
        (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'),
        (11, 'November'), (12, 'December')
    ]
    year = fields.Integer(string='Year',size=4)
    month = fields.Selection(MONTH_LIST, string='Month')
    date_of_joining = fields.Date()
    fiscal_year = fields.Many2one('account.fiscalyear',string='Fiscal Year')
    month_year  = fields.Char()
    # quarterly2 = fields. ([
    #     ('1', 'Q1'),
    #     ('2', 'Q2'),
    #     ('3', 'Q3'),
    #     ('4', 'Q4'),
    # ], string="Quaterly")
    quarterly = fields.Char()
    department = fields.Char()
    total_employees = fields.Integer()
    male_count = fields.Integer()
    female_count = fields.Integer()
    this_year_count = fields.Integer()
    this_quarter_count = fields.Integer()
    this_month_count = fields.Integer()
    male_ratio = fields.Integer()
    female_ratio = fields.Integer()
    monthly_growth = fields.Integer()
    quarterly_growth = fields.Integer()
    yearly_growth = fields.Integer()

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s AS (
            SELECT row_number() over(
              order by DATE_TRUNC('month', hr.date_of_joining), 
              DATE_TRUNC('quarter', hr.date_of_joining)
          ) AS id,
          (
              SELECT
                  MAX(id)
              FROM
                  account_fiscalyear
              WHERE
                  hr.date_of_joining >= date_start AND hr.date_of_joining <= date_stop
          ) AS fiscal_year,
          case
          when date_part('quarter', date_of_joining) = 1 then 'Q1'  || ' ' || date_part('year', date_of_joining)
          when  date_part('quarter', date_of_joining) = 2 then 'Q2'  || ' ' || date_part('year', date_of_joining)
          when date_part('quarter', date_of_joining) = 3 then 'Q3'  || ' ' || date_part('year', date_of_joining)
          when  date_part('quarter', date_of_joining) = 4 then 'Q4'  || ' ' || date_part('year', date_of_joining)
          end as quarterly,
          TO_CHAR(date_of_joining, 'Mon YYYY') AS month_year,
          date_part('quarter', date_of_joining) as quarter,
          date_part('month', date_of_joining) as month,
          date_part('year', date_of_joining) as year,
          dept.name AS department,
          DATE(DATE_TRUNC('month', date_of_joining)) AS date_of_joining,
          count(hr.id) as total_employees,
          count(hr.id) FILTER (WHERE hr.gender = 'male') as male_count,
          count(hr.id) FILTER (WHERE hr.gender = 'female') as female_count,
          100 * count(hr.id) FILTER (WHERE hr.gender = 'male') / nullif(count(hr.id), 0) as male_ratio,
          100 * count(hr.id) FILTER (WHERE hr.gender = 'female') / nullif(count(hr.id), 0) as female_ratio,
          100 * (
              count(hr.id) - (
                  LAG(count(hr.id)) OVER (
                      ORDER BY DATE_TRUNC('month', hr.date_of_joining), 
                      DATE_TRUNC('quarter', hr.date_of_joining)
                  )
              )
          ) / nullif(
              (
                  LAG(count(hr.id)) OVER (
                      ORDER BY DATE_TRUNC('month', hr.date_of_joining), 
                      DATE_TRUNC('quarter', hr.date_of_joining)
                  )
              ), 
              0
          ) as monthly_growth,
          100 * (
              count(hr.id) - (
                  LAG(count(hr.id)) OVER (
                      ORDER BY DATE_TRUNC('quarter', hr.date_of_joining)
                  )
              )
          ) / nullif(
              (
                  LAG(count(hr.id)) OVER (
                      ORDER BY DATE_TRUNC('quarter', hr.date_of_joining)
                  )
              ), 
              0
          ) as quarterly_growth,
          100 * (
              count(hr.id) - (
                  LAG(count(hr.id)) OVER (
                      ORDER BY date_part('year', date_of_joining)
                  )
              )
          ) / nullif(
              (
                  LAG(count(hr.id)) OVER (
                      ORDER BY date_part('year', date_of_joining)
                  )
              ), 
              0
          ) as yearly_growth
      FROM
          hr_department as dept
          join hr_employee as hr on dept.id=hr.department_id
          join kw_hr_department_type as type on type.id = dept.dept_type
      WHERE
          type.code='department' AND employement_type NOT IN (5)
      GROUP BY
          fiscal_year,
          quarter,
          month_year,
          dept.name,
          date_of_joining
          
      ORDER BY
          date_of_joining DESC,
          dept.name ASC

            )""" % (self._table))
        

class FiscalYearAttritionReport(models.Model):
    _name = 'fiscal_year_wise_attrition_report'
    _description = 'Attrition Report'
    _auto = False
    _order = 'id desc'

    MONTH_LIST = [
        (1, 'January'), (2, 'February'),
        (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'),
        (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'),
        (11, 'November'), (12, 'December')
    ]
    year = fields.Integer(string='Year',size=4)
    month = fields.Selection(MONTH_LIST, string='Month')

    last_working_day = fields.Date()
    fiscal_year = fields.Many2one('account.fiscalyear', string='Fiscal Year')
    month_year = fields.Char()
    quarterly = fields.Char()
    quarter = fields.Char()
    department = fields.Char()
    total_employees = fields.Integer()
    male_count = fields.Integer()
    female_count = fields.Integer()
    this_year_count = fields.Integer()
    this_quarter_count = fields.Integer()
    this_month_count = fields.Integer()
    male_ratio = fields.Integer()
    female_ratio = fields.Integer()
    monthly_growth = fields.Integer()
    quarterly_growth = fields.Integer()
    yearly_growth = fields.Integer()
            
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s AS (

        SELECT row_number() over(
        order by DATE_TRUNC('month', hr.last_working_day), 
        DATE_TRUNC('quarter', hr.last_working_day)
    ) AS id,
    (
        SELECT
            MAX(id)
        FROM
            account_fiscalyear
        WHERE
            hr.last_working_day >= date_start AND hr.last_working_day <= date_stop
    ) AS fiscal_year,
    
    TO_CHAR(last_working_day, 'Mon YYYY') AS month_year,
    date_part('quarter',last_working_day) as quarter,
    case
      when date_part('quarter', last_working_day) = 1 then 'Q1'  || ' ' || date_part('year', last_working_day)
      when  date_part('quarter', last_working_day) = 2 then 'Q2'  || ' ' || date_part('year', last_working_day)
      when date_part('quarter', last_working_day) = 3 then 'Q3'  || ' ' || date_part('year', last_working_day)
      when  date_part('quarter', last_working_day) = 4 then 'Q4'  || ' ' || date_part('year', last_working_day)
      end as quarterly,
    date_part('month',last_working_day) as month,
    date_part('year',last_working_day) as year,
    
    dept.name as department,
    DATE(DATE_TRUNC('month', last_working_day)) AS last_working_day,
    count(hr.id) as total_employees,
    count(hr.id) FILTER (WHERE hr.gender = 'male') as male_count,
    count(hr.id) FILTER (WHERE hr.gender = 'female') as female_count,
    100 * count(hr.id) FILTER (WHERE hr.gender = 'male') / nullif(count(hr.id), 0) as male_ratio,
    100 * count(hr.id) FILTER (WHERE hr.gender = 'female') / nullif(count(hr.id), 0) as female_ratio,
    100 * (
        count(hr.id) - (
            LAG(count(hr.id)) OVER (
                ORDER BY DATE_TRUNC('month', hr.last_working_day), 
                DATE_TRUNC('quarter', hr.last_working_day)
            )
        )
    ) / nullif(
        (
            LAG(count(hr.id)) OVER (
                ORDER BY DATE_TRUNC('month', hr.last_working_day), 
                DATE_TRUNC('quarter', hr.last_working_day)
            )
        ), 
        0
    ) as monthly_growth,
    100 * (
        count(hr.id) - (
            LAG(count(hr.id)) OVER (
                ORDER BY DATE_TRUNC('quarter', hr.last_working_day)
            )
        )
    ) / nullif(
        (
            LAG(count(hr.id)) OVER (
                ORDER BY DATE_TRUNC('quarter', hr.last_working_day)
            )
        ), 
        0
    ) as quarterly_growth,
    100 * (
        count(hr.id) - (
            LAG(count(hr.id)) OVER (
                ORDER BY date_part('year', last_working_day)
            )
        )
    ) / nullif(
        (
            LAG(count(hr.id)) OVER (
                ORDER BY date_part('year', last_working_day)
            )
        ), 
        0
    ) as yearly_growth
FROM
    hr_department as dept
    join hr_employee as hr on dept.id=hr.department_id
    join kw_hr_department_type as type on type.id = dept.dept_type
WHERE
    type.code='department' AND employement_type NOT IN (5)
GROUP BY
    fiscal_year,
    quarter,
    month_year,
    dept.name,
    last_working_day
    
ORDER BY
    last_working_day DESC,
    dept.name ASC

            )""" % (self._table))
