from odoo import fields, models, api, tools
# import datetime
from datetime import date,datetime,timedelta
from odoo import fields, models, api,tools


class MealPriceReport(models.Model):
    _name = "meal_price_log"
    _description = "Total Meal And Beverages Price"
    _rec_name = "employee_id"
    _auto = False

  
    # code = fields.Char(string="Code")
    year = fields.Integer(string="Year")
    month = fields.Integer(string="Month")
    month_selection = fields.Char(string='Month', compute='compute_month')
    
    location_id = fields.Many2one('kw_res_branch','Location')
    employee_id = fields.Many2one('hr.employee', string="Employee Name")
    # designation_id = fields.Many2one('hr.job', string="Designation")
    # department_id = fields.Many2one('hr.department', string="Department")
    no_of_regular_meal = fields.Integer(string="No Of Regular Meal")
    no_of_guest_meal = fields.Integer(string="No Of Guest Meal")
    total_price_of_regular_meal = fields.Integer(string="Total Regular Meal Price")
    total_price_of_guest_meal = fields.Integer(string="Total Guest Meal Price")
    total_meal_price = fields.Float(string="Total Price", compute="total_price")
    # price_id = fields.Many2one('price_master_configuration')
    

    def total_price(self):
        for record in self:
            canteen_recs = self.env['kw_canteen_regular_meal'].sudo().search([('employee_id','=',record.employee_id.id), ('state', '=', 'approved')])
            if canteen_recs:
                for canteen_rec in canteen_recs:
                    if canteen_rec.is_special:
                        record.total_meal_price = (record.total_price_of_regular_meal + record.total_price_of_guest_meal)/2
                    else:
                        record.total_meal_price = record.total_price_of_regular_meal + record.total_price_of_guest_meal
            else:
                record.total_meal_price = record.total_price_of_regular_meal + record.total_price_of_guest_meal
            
            
    @api.depends('month')
    def compute_month(self):
        month_dict = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
        for rec in self:
            month = rec.month
            rec.month_selection = month_dict.get(month)
            
    @api.model_cr
    def init(self):
        # regular_price = self.env['price_master_configuration'].search([('meal_type', '=', 'Regular')])
        # guest_price = regular_price.search([('meal_type', '=', 'Guest')])
        # date_to = date.today().replace(day=25)
        # month_int =str(date_to.month)
        # datetime_object = datetime.strptime(month_int, "%m")
        # full_month_name = datetime_object.strftime("%B")
        # date_from = date_to - relativedelta(months=1) + relativedelta(days=1)
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (        
        select row_number() over() as id,EXTRACT(year from recorded_date + INTERVAL '1 MONTH - 25 DAY') as year,
        EXTRACT(month from recorded_date + INTERVAL '1 MONTH - 25 DAY') as month,
		 emp.base_branch_id as location_id,a.employee_id,
        SUM(COALESCE(no_of_veg,0) + COALESCE(no_of_non_veg,0)) FILTER (WHERE a.meal_type_id = (select id from price_master_configuration where meal_code='R')) as no_of_regular_meal,
        SUM(COALESCE(no_of_veg,0) + COALESCE(no_of_non_veg,0)) FILTER (WHERE a.meal_type_id = (select id from price_master_configuration where meal_code='G')) as no_of_guest_meal,
        SUM(COALESCE(no_of_veg,0) + COALESCE(no_of_non_veg,0)) FILTER (WHERE a.meal_type_id = (select id from price_master_configuration where meal_code='R')) * (select price from price_master_configuration where meal_code='R') as total_price_of_regular_meal,
        SUM(COALESCE(no_of_veg,0) + COALESCE(no_of_non_veg,0)) FILTER (WHERE a.meal_type_id = (select id from price_master_configuration where meal_code='G')) * (select price from price_master_configuration where meal_code='G') as total_price_of_guest_meal
        from meal_bio_log a 
            join hr_employee emp on a.employee_id = emp.id
		group by EXTRACT(year from recorded_date + INTERVAL '1 MONTH - 25 DAY'),
        EXTRACT(month from recorded_date + INTERVAL '1 MONTH - 25 DAY'),employee_id,emp.base_branch_id)
"""

        self.env.cr.execute(query)

    @api.multi
    def get_view_details(self):
        tree_view_id = self.env.ref('kw_canteen.view_meal_bio_log_tree').id
        for rec in self:
            previous_month = datetime(int(rec.year), int(rec.month)-1, 26) if int(rec.month) != 1 else datetime(int(rec.year)-1,12, 26)
            this_month = datetime(int(rec.year), int(rec.month), 25) 
            meal = self.env['meal_bio_log'].sudo().search([('recorded_date','>=',previous_month),('recorded_date','<=',this_month),('employee_id','=',rec.employee_id.id)])
            return {
                "name": "Daily Report View",
                'views': [(tree_view_id,'tree')],
                'view_mode': 'tree',
                'view_type': 'form',
                "res_model": 'meal_bio_log',
                "type": 'ir.actions.act_window',
                "target": "self",
                "domain": [('id', 'in', meal.ids)]
            }