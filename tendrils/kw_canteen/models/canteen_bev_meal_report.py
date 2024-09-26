from odoo import fields, models, api, tools
from datetime import date,datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api,tools


class MealPriceReport(models.Model):
    _name = "employee_canteen_expense_report"
    _description = "Employee Canteen Expense Report"
    _rec_name = "employee_id"
    _order="recorded_date desc"
    _auto = False
    
    recorded_date = fields.Date(string="Date")
    employee_id = fields.Many2one('hr.employee',string="Employee")
    department=fields.Char("Department",related='employee_id.department_id.name')
    designation=fields.Char("Designation",related='employee_id.job_id.name')
    tea_coffee_count = fields.Integer(string="Tea/Coffee")
    b2c_count = fields.Integer(string="Bean Coffee")
    regular_meal_count = fields.Integer(string="Regular Meal")
    guest_meal_count = fields.Integer(string="Guest Meal")
    tea_coffee_price = fields.Float(string='Price',compute='calculate_price')
    b2c_price = fields.Float(string='Price',compute='calculate_price')
    regular_meal_price = fields.Float(string="Price")
    guest_meal_price = fields.Float(string="Price")

    @api.depends('tea_coffee_count','b2c_count')
    def calculate_price(self):
        beverage = self.env['kw_canteen_beverage_type'].sudo().search([])
        for rec in self:
            tea_coffee_price = rec.tea_coffee_count * beverage.filtered(lambda x:x.beverage_code == 'TC').mapped('beverage_price')

            rec.tea_coffee_price += sum(tea_coffee_price)
            b2c_price = rec.b2c_count * beverage.filtered(lambda x:x.beverage_code == 'B2C').mapped('beverage_price')
            rec.b2c_price += sum(b2c_price)
        
    @api.model_cr
    def init(self):
       
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (     
           select row_number() over() as id,RES.DATE as recorded_date,E.id as employee_id,
            (
                SELECT count(BE.beverage_type_id)
                FILTER (WHERE BE.beverage_type_id = (select id from kw_canteen_beverage_type where beverage_code ='TC'))
                FROM baverage_bio_log AS BE
                WHERE BE.employee_id=E.ID
                AND date(BE.recorded_date)=RES.DATE   

            ) AS tea_coffee_count,
            (
                SELECT count(BE.beverage_type_id)
                FILTER (WHERE BE.beverage_type_id = (select id from kw_canteen_beverage_type where beverage_code ='B2C'))
                FROM baverage_bio_log AS BE
                WHERE BE.employee_id=E.ID
                AND date(BE.recorded_date)=RES.DATE
            ) b2c_count,
            (
                SELECT coalesce(no_of_veg,0) + coalesce(no_of_non_veg,0)  as veg_meal_count FROM meal_bio_log V
                WHERE V.employee_id=E.ID 
				AND  V.meal_type_id =  (select id from price_master_configuration where meal_code = 'R')
                AND  date(V.recorded_date)=RES.DATE  
            ) AS regular_meal_count,
			 (
                SELECT coalesce(no_of_veg,0) + coalesce(no_of_non_veg,0)  as veg_meal_count FROM meal_bio_log V
                WHERE V.employee_id=E.ID and V.company_guest = false
				AND  V.meal_type_id =  (select id from price_master_configuration where meal_code = 'G')
                AND  date(V.recorded_date)=RES.DATE  
            ) 
			AS guest_meal_count,

			(
                SELECT
				 sum(total_price) FROM meal_bio_log V
                WHERE V.employee_id=E.ID 
				AND V.meal_type_id =  (select id from price_master_configuration where meal_code = 'R')
                AND  date(V.recorded_date)=RES.DATE  
            ) AS regular_meal_price,
			
			(
                SELECT
				sum(total_price) FROM meal_bio_log V
                WHERE V.employee_id=E.ID  and V.company_guest = false
				And V.meal_type_id =  (select id from price_master_configuration where meal_code = 'G')
                AND  date(V.recorded_date)=RES.DATE  
            ) AS guest_meal_price
            
            
            FROM hr_employee e
            LEFT JOIN
            (
            select date(recorded_date) AS DATE,employee_id from meal_bio_log
            union  
            select date(recorded_date) AS DATE,employee_id from baverage_bio_log
            ) AS RES
            ON E.ID=RES.employee_id
            WHERE RES.DATE IS NOT NULL
        )
        """
        self.env.cr.execute(query)