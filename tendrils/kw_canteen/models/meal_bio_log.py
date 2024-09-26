from datetime import date,datetime
from odoo import models, fields, api
# from odoo.exceptions import ValidationError, AccessError

class MealBioLog(models.Model):
    _name="meal_bio_log"
    _description = "Meal Bio Log"
    _rec_name="employee_id"
    _order="recorded_date asc"

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
    # food_type = fields.Selection([('veg', 'Veg'),('non-veg', 'Non-Veg'),],  string="Food Category")
    
    no_of_veg = fields.Integer(string="No Of Veg")
    no_of_non_veg = fields.Integer(string="No Of Non-Veg")
    total_meal = fields.Integer(string="Total Meal", compute="calculate_total_meal")
    month = fields.Integer(string='Month')
    
    is_special = fields.Boolean(string="Is Special ?")
    total_price = fields.Float(string="Total Price",compute='calculate_total_price',store=True)
    
    unit_price = fields.Float(string="Unit Price",compute='calculate_total_price')
    company_guest = fields.Boolean(string="Company Guest")
    card_punch = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Card Punch")

    '''
    alter table meal_bio_log drop constraint meal_bio_log_meal_bio_log_unique;
    ALTER TABLE meal_bio_log ADD CONSTRAINT meal_bio_log_meal_bio_log_unique UNIQUE (employee_id,recorded_date,meal_type);
    '''

    # _sql_constraints = [
    #     ('meal_bio_log_unique', 'unique (employee_id,recorded_date,meal_type)', 'The recorded date with combination of employee exists for the selected date.'),
    # ]
    
    @api.depends('meal_type_id','no_of_non_veg')
    def calculate_total_price(self):
        for record in self:
            if record.is_special == True:
                record.unit_price = (record.meal_price)/2
            # if record.meal_type_id.meal_code == 'R':
                record.total_price = (record.total_meal * record.meal_price)/2
            else:
                record.unit_price = record.meal_price
                record.total_price = record.total_meal * record.meal_price
            # else:
                # record.total_price = record.total_meal * record.meal_type_id.price
    @api.onchange('no_of_veg','no_of_non_veg')
    def calculate_total_meal(self):
        for record in self:
            record.total_meal = record.no_of_veg + record.no_of_non_veg
        
    @api.model
    def create_daily_meal_log(self):
        # create meal log for employees on daily morning
        current_date = date.today()
        current_day_value = current_date.weekday()
        regular_meal_id=self.env.ref('kw_canteen.regular_id')
        guest_meal_id=self.env.ref('kw_canteen.guest_id')
        
        # start : process scheduler for regular meal employees
        regular_meal = self.env['kw_canteen_regular_meal']

        regular_employees = regular_meal.search(['&','&',('state','=','approved'),('is_special','=',False),
                '|','&', '&', '&', ('start_date', '!=', False), ('end_date','!=',False), ('start_date','<=',current_date), ('end_date','>=',current_date),
                '&', '&', ('start_date','!=', False), ('end_date', '=', False), ('start_date','<=',current_date)]).mapped('employee_id')

        exclusion_employees = regular_meal.search([('state','=','approved'),('close_meal_ids.start_date', '<=', current_date), ('close_meal_ids.end_date','>=',current_date)]).mapped('employee_id')
        
        log_created_employees = self.search([('recorded_date', '=', current_date),('meal_type_id','=',regular_meal_id.id)]).mapped('employee_id')
        not_created_employees = regular_employees - exclusion_employees - log_created_employees
        shifts = not_created_employees.mapped('resource_calendar_id')
        
        # not_to_be_created_shifts =  shifts.search([('id','in',shifts.ids),('global_leave_ids.date_from','<=',current_date),('global_leave_ids.date_to','>=',current_date)])#.filtered(lambda r:current_date not in r.public_holidays.mapped('date'))
        not_to_be_created_shifts =  shifts.filtered(lambda r:r.global_leave_ids.filtered(lambda r:r.date_from.date() <= current_date and r.date_from.date() >= current_date) or r.public_holidays.filtered(lambda r:current_date == r.date))
        if not_created_employees.filtered(lambda r:r.resource_calendar_id not in not_to_be_created_shifts):
            employee_meals = regular_meal.search([('employee_id', 'in', not_created_employees.ids),('state','=','approved')])
            for employee in not_created_employees.filtered(lambda r:r.resource_calendar_id not in not_to_be_created_shifts):
                employee_meal = employee_meals.filtered(lambda r:r.employee_id == employee)[0:1]
                emp_veg_meal = 0
                emp_non_veg_meal = 0
                
                if employee_meal.opt_monday and current_day_value == 0:#valid
                    if employee_meal.monday_meal_id.code == 'veg':
                        emp_veg_meal = 1
                    else:
                        emp_non_veg_meal = 1
                        
                elif employee_meal.opt_tuesday and current_day_value == 1:#valid
                    if employee_meal.tuesday_meal_id.code == 'veg':
                        emp_veg_meal = 1
                    else:
                        emp_non_veg_meal = 1
                        
                elif employee_meal.opt_wedday and current_day_value == 2:#valid
                    if employee_meal.wedday_meal_id.code == 'veg':
                        emp_veg_meal = 1
                    else:
                        emp_non_veg_meal = 1
                        
                elif employee_meal.opt_thursday and current_day_value == 3:#valid
                    if employee_meal.thursday_meal_id.code == 'veg':
                        emp_veg_meal = 1
                    else:
                        emp_non_veg_meal = 1
                        
                elif employee_meal.opt_friday and current_day_value == 4:#valid
                    if employee_meal.friday_meal_id.code == 'veg':
                        emp_veg_meal = 1
                    else:
                        emp_non_veg_meal = 1
                
                elif employee_meal.opt_saturday  and current_day_value == 5:#valid
                    if employee_meal.saturday_meal_id.code == 'veg':
                        emp_veg_meal = 1
                    else:
                        emp_non_veg_meal = 1
                
                elif employee_meal.opt_sunday and current_day_value == 6:#valid
                    if employee_meal.sunday_meal_id.code == 'veg':
                        emp_veg_meal = 1
                    else:
                        emp_non_veg_meal = 1
                if emp_veg_meal or emp_non_veg_meal:   
                    unit_location_id = regular_meal.search(['|','&','&',('state','=','approved'),('is_special','=',False),
                '&', '&', '&', '&', ('start_date', '!=', False), ('end_date','!=',False), ('start_date','<=',current_date), ('end_date','>=',current_date), ('employee_id','=',employee.id),
                '&', '&', '&', ('start_date','!=', False), ('end_date', '=', False), ('start_date','<=',current_date),('employee_id','=',employee.id)],limit=1)
                    self.create({
                        'meal_type':'regular',
                        'meal_type_id':regular_meal_id.id,
                        'meal_price': regular_meal_id.price,
                        'employee_id':employee.id,
                        'emp_code': employee.emp_code,
                        'recorded_date':current_date,
                        'infra_unit_location_id': unit_location_id.infra_unit_location_id.id,
                        'is_special':unit_location_id.is_special,
                        'no_of_veg':emp_veg_meal,
                        'no_of_non_veg':emp_non_veg_meal,
                        'card_punch' :'no'
                    })
        # end : process scheduler for regular meal employees
        
        # start : process scheduler for guest meal employees
        guest_meal = self.env['kw_canteen_guest_meal']
        guest_employees = guest_meal.search([('state','=','approved'),('start_date','<=',current_date), ('end_date','>=',current_date)]).mapped('employee_id')
        guest_log_created_employees = self.search([('recorded_date', '=', current_date),('meal_type_id','=',guest_meal_id.id)]).mapped('employee_id')
        
        guest_log_not_created_employees = guest_employees - guest_log_created_employees
        
        guest_employee_shifts = guest_log_not_created_employees.mapped('resource_calendar_id')
        
        not_to_be_created_log_shifts =  guest_employee_shifts.filtered(lambda r:r.global_leave_ids.filtered(lambda r:r.date_from.date() <= current_date and r.date_from.date() >= current_date))
        
        if guest_log_not_created_employees.filtered(lambda r:r.resource_calendar_id not in not_to_be_created_log_shifts):
            
            employee_guest_meals = guest_meal.search([('employee_id', 'in', guest_log_not_created_employees.ids),('state','=','approved')])
            
            for employee in guest_log_not_created_employees.filtered(lambda r:r.resource_calendar_id not in not_to_be_created_log_shifts):
                employee_meal = employee_guest_meals.filtered(lambda r:r.employee_id == employee)[0:1]
                emp_veg_meal = 0
                emp_non_veg_meal = 0
                
                if employee_meal.opt_monday and current_day_value == 0:#valid
                    if employee_meal.meal_for == 'self':
                        if  employee_meal.monday_meal_id.code == 'veg':
                            emp_veg_meal = 1
                        else:
                            emp_non_veg_meal = 1
                    else:
                        emp_veg_meal = employee_meal.monday_vg_count
                        emp_non_veg_meal = employee_meal.monday_nvg_count
                        
                elif employee_meal.opt_tuesday and current_day_value == 1:#valid
                    if employee_meal.meal_for == 'self':
                        if  employee_meal.tuesday_meal_id.code == 'veg':
                            emp_veg_meal = 1
                        else:
                            emp_non_veg_meal = 1
                    else:
                        emp_veg_meal = employee_meal.tuesday_vg_count
                        emp_non_veg_meal = employee_meal.tuesday_nvg_count
                            
                elif employee_meal.opt_wedday and current_day_value == 2:#valid
                    if employee_meal.meal_for == 'self':
                        if  employee_meal.wedday_meal_id.code == 'veg':
                            emp_veg_meal = 1
                        else:
                            emp_non_veg_meal = 1
                    else:
                        emp_veg_meal = employee_meal.wednesday_vg_count
                        emp_non_veg_meal = employee_meal.wednesday_nvg_count
                        
                elif employee_meal.opt_thursday and current_day_value == 3:#valid
                    if employee_meal.meal_for == 'self':
                        if employee_meal.thursday_meal_id.code == 'veg':
                            emp_veg_meal = 1
                        else:
                            emp_non_veg_meal = 1
                    else:
                        emp_veg_meal = employee_meal.thursday_vg_count
                        emp_non_veg_meal = employee_meal.thursday_nvg_count
                            
                elif employee_meal.opt_friday and current_day_value == 4:#valid
                    if employee_meal.meal_for == 'self':
                        if  employee_meal.friday_meal_id.code == 'veg':
                            emp_veg_meal = 1
                        else:
                            emp_non_veg_meal = 1
                    else:
                        emp_veg_meal = employee_meal.friday_vg_count
                        emp_non_veg_meal = employee_meal.friday_nvg_count
                elif employee_meal.opt_saturday and current_day_value == 5:#valid
                    if employee_meal.meal_for == 'self':
                        if  employee_meal.saturday_meal_id.code == 'veg':
                            emp_veg_meal = 1
                        else:
                            emp_non_veg_meal = 1
                    else:
                        emp_veg_meal = employee_meal.saturday_vg_count
                        emp_non_veg_meal = employee_meal.saturday_nvg_count

                elif employee_meal.opt_sunday and current_day_value == 6:#valid
                    if employee_meal.meal_for == 'self':
                        if  employee_meal.sunday_meal_id.code == 'veg':
                            emp_veg_meal = 1
                        else:
                            emp_non_veg_meal = 1
                    else:
                        emp_veg_meal = employee_meal.sunday_vg_count
                        emp_non_veg_meal = employee_meal.sunday_nvg_count
                if emp_veg_meal or emp_non_veg_meal:  
                    unit_location_id = guest_meal.search([('state','=','approved'),('start_date','<=',current_date), ('end_date','>=',current_date),('employee_id','=',employee.id)],limit=1).infra_unit_location_id                       
                    self.create({
                        'meal_type':'guest',
                        'meal_type_id':guest_meal_id.id,
                        'company_guest': True if employee_meal.is_company_guest == True else False,
                        'meal_price':guest_meal_id.price,
                        'employee_id':employee.id,
                        'emp_code': employee.emp_code,
                        'recorded_date':current_date,
                        'infra_unit_location_id': unit_location_id.id,
                        # 'food_type':employee_meal.food_type,
                        'no_of_veg':emp_veg_meal,
                        'no_of_non_veg':emp_non_veg_meal,
                        'card_punch' :'no'
                    })
        # end : process scheduler for guest meal employees


    @api.model
    def total_food_price_mail_cron(self):
        date = datetime.now()
        domain = [('month', '=', date.month), ('year', '=', date.year)]
        records = self.env['meal_price_log'].sudo().search(domain)
        month_name = date.strftime("%B")
        if date.day in (26, 27, 28):
            for record in records:
                dom = [('employee_id', '=', record.employee_id.id), ('month', '=', date.month),
                       ('year', '=', date.year)]
                beverages = self.env['beverage_price_log'].sudo().search(dom)
                beverage_price = beverages.total_price
                total_price = beverage_price + record.total_meal_price
                email_from = self.env.user.company_id.email
                mail_template = self.env.ref('kw_canteen.kw_canteen_total_food_price_mail_temp')
                # canteen_users = self.env.ref('kw_canteen.canteen_emp_user_group').users
                # canteen_users = record.employee_id.user_id
                # email_to = ','.join(canteen_users.mapped('employee_ids.work_email'))
                email_to = record.employee_id.work_email
                mail_template.with_context(email_to=email_to, email_from=email_from, beverage_price=beverage_price,
                                           month=month_name, total_price=total_price).send_mail(
                    record.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                                           
