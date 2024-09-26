from odoo import models, fields, api
from datetime import date


class CanteenMealReportUpdate(models.TransientModel):
    _name = 'kw_canteen_update_meal_report'
    _description = 'Update Meal Report'

    date_from = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")
    employee_id = fields.Many2one('hr.employee',string="Employee")
    meal_record_ids = fields.One2many(comodel_name="kw_canteen_employee_meal_log", inverse_name="update_id",string="Meal Records")
    


    @api.onchange("employee_id")
    def get_values(self):
        self.meal_record_ids = False
        # self.meal_record_ids = [(5, 0, 0)]
        if self.date_from and self.date_to and self.employee_id:
            meal_rec=self.env['meal_bio_log'].sudo().search([('recorded_date' , '>=' ,self.date_from),('recorded_date', '<=' , self.date_to),('employee_id', '=' , self.employee_id.id)])
            for data in meal_rec:
                self.meal_record_ids = [(0, 0, {
                                                'employee_id': data.employee_id.id,
                                                'emp_designation_id': data.employee_id.job_id.id,
                                                'infra_unit_location_id': data.infra_unit_location_id.id,
                                                'recorded_date': data.recorded_date,
                                                'meal_type_id': data.meal_type_id.id,
                                                'meal_type': data.meal_type,

                                                'is_special': data.is_special,
                                                })]
        
       
            
    def button_remove_duplicate_record(self):
        meal_rec=self.env['meal_bio_log'].sudo().search([('recorded_date' , '>=' ,self.date_from),('recorded_date', '<=' , self.date_to),('employee_id', '=' , self.employee_id.id)])
        if meal_rec:
            for record in meal_rec:
                self.env['removed_meal_report_log'].sudo().create({
                        'meal_type':record.meal_type,
                        'meal_type_id':record.meal_type_id.id,
                        'meal_price': record.meal_price,
                        'employee_id':record.employee_id.id,
                        'emp_code': record.employee_id.emp_code,
                        'recorded_date':record.recorded_date,
                        'infra_unit_location_id': record.infra_unit_location_id.id,
                        'no_of_veg':record.no_of_veg,
                        'no_of_non_veg':record.no_of_non_veg,
                        'is_special':record.is_special
                })
            meal_rec.unlink()
            self.env.user.notify_success("Record Removed Successfully.")


    
class MealReportLog(models.Model):

    _name ="removed_meal_report_log"
    _description="Removed Meal Report Log"


    employee_id = fields.Many2one('hr.employee','Employee')
    emp_code = fields.Char(string="Emp. Code")
    emp_name = fields.Char(related="employee_id.name",string="Employee")
    emp_designation_id = fields.Many2one(related="employee_id.job_id",string="Designation",store=True)
    infra_unit_location_id = fields.Many2one('kw_res_branch_unit', string="Infra Unit Location")
    essl_id = fields.Integer('ESSL ID')
    recorded_date = fields.Date('Date')
    meal_type = fields.Selection([('regular', 'Regular'),
                                ('guest', 'Guest')], default="guest",string="Meal Type")
    meal_type_id=fields.Many2one('price_master_configuration',string="Meal")       
    meal_price = fields.Float(string="Price")                     
    
    no_of_veg = fields.Integer(string="No Of Veg")
    no_of_non_veg = fields.Integer(string="No Of Non-Veg")
    total_meal = fields.Integer(string="Total Meal", compute="calculate_total_meal")
    month = fields.Integer(string='Month')
    
    is_special = fields.Boolean(string="Is Special ?")
    total_price = fields.Float(string="Total Price",compute='calculate_total_price',store=True)
    
    unit_price = fields.Float(string="Unit Price",compute='calculate_total_price')
    company_guest = fields.Boolean(string="Company Guest")


    @api.depends('meal_type_id','no_of_non_veg')
    def calculate_total_price(self):
        for record in self:
            if record.is_special == True:
                record.unit_price = (record.meal_price)/2
                record.total_price = (record.total_meal * record.meal_price)/2
            else:
                record.unit_price = record.meal_price
                record.total_price = record.total_meal * record.meal_price

    @api.onchange('no_of_veg','no_of_non_veg')
    def calculate_total_meal(self):
        for record in self:
            record.total_meal = record.no_of_veg + record.no_of_non_veg




class EmployeeMealLog(models.TransientModel):
    _name ="kw_canteen_employee_meal_log"
    _description="meal Log"


    employee_id = fields.Many2one('hr.employee','Employee')
    emp_code = fields.Char(string="Emp. Code",elated="employee_id.emp_code")
    emp_name = fields.Char(related="employee_id.name",string="Employee")
    emp_designation_id = fields.Many2one(related="employee_id.job_id",string="Designation",store=True)
    infra_unit_location_id = fields.Many2one('kw_res_branch_unit', string="Infra Unit Location")
    recorded_date = fields.Date('Date')
    meal_type = fields.Selection([('regular', 'Regular'),
                                ('guest', 'Guest')], default="guest",string="Meal Type")


    meal_type_id=fields.Many2one('price_master_configuration',string="Meal")       
    
    is_special = fields.Boolean(string="Is Special ?")

    update_id = fields.Many2one('kw_canteen_update_meal_report')