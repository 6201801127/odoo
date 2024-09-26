from odoo import fields, models,api,tools
from datetime import date


class BeveragePriceReport(models.Model):
    _name = "beverage_price_log"
    _description = "Monthly Beverage Price Report"
    _auto = False

    year = fields.Integer(string="Year")
    month = fields.Integer(string="Month")
    location_id = fields.Many2one('kw_res_branch', string="Location")
    employee_id = fields.Many2one('hr.employee', string="Employee Name")
    no_of_beverages = fields.Integer(string="No Of Beverages")
    total_price = fields.Float(string="Total Price")
    month_selection = fields.Char(string='Month', compute='compute_month')

    @api.depends('month')
    def compute_month(self):
        month_dict = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                      9: 'September', 10: 'October', 11: 'November', 12: 'December'}
        for rec in self:
            month = rec.month
            rec.month_selection = month_dict.get(month)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            select row_number() over() as id,
            EXTRACT(year from recorded_date + INTERVAL '1 MONTH - 25 DAY') as year,
            EXTRACT(month from recorded_date + INTERVAL '1 MONTH - 25 DAY') as month,
            emp.base_branch_id as location_id,a.employee_id,
            count(*) FILTER (WHERE a.beverage_type_id = (select id from kw_canteen_beverage_type where beverage_code ='TC')) as no_of_beverages,
            (count(*) FILTER (WHERE a.beverage_type_id = (select id from kw_canteen_beverage_type where beverage_code ='TC')) * (select beverage_price from kw_canteen_beverage_type where beverage_code ='TC')) as total_price
            from baverage_bio_log a
            join hr_employee emp on a.employee_id = emp.id
            group by EXTRACT(year from recorded_date + INTERVAL '1 MONTH - 25 DAY'),
            EXTRACT(month from recorded_date + INTERVAL '1 MONTH - 25 DAY'),employee_id,emp.base_branch_id
            
            )"""

        self.env.cr.execute(query)


