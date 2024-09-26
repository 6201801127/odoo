from datetime import date, datetime, timedelta
from email.policy import default

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CanteenRegularMeal(models.Model):
    _name = 'kw_canteen_guest_meal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Guest Meal"
    _rec_name = 'employee_id'

    # def get_current_logged_employee(self):
        # emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        # return emp

    # employee_id = fields.Many2one('hr.employee', string="Employee Name", required=True, tracking=False, readonly=True, default=get_current_logged_employee)
    employee_id = fields.Many2one('hr.employee', string="Employee Name", required=True, tracking=False, readonly=True, default=lambda self : self.env.user.employee_ids[0:1])
    department_id = fields.Char(string='Department', related='employee_id.department_id.name')
    infra_unit_location_id = fields.Many2one('kw_res_branch_unit', string="Infra Unit Location",related="employee_id.branch_unit_id",store=True)
    desig_id = fields.Char(string='Designation', related='employee_id.job_id.name')
    meal_for = fields.Selection(string="Meal For",selection=[('self','Self'),('others','Others')],required=True,default="self",track_visibility='onchange')
    is_company_guest = fields.Boolean("Company Guest",track_visibility='onchange')

    start_date = fields.Date(string="Start Date", required=True,track_visibility='onchange')
    end_date = fields.Date(string="End Date",required=True,track_visibility='onchange')
    
    remarks = fields.Text(string="Remarks" , track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approved', 'Approved'), ('expired', 'Expired'), ('cancel', 'Canceled')], string="Status", default="draft" , track_visibility='onchange')

    opt_monday = fields.Boolean(string="Monday",track_visibility='onchange')
    opt_tuesday = fields.Boolean(string="Tuesday",track_visibility='onchange')
    opt_wedday = fields.Boolean(string="Wednesday",track_visibility='onchange')
    opt_thursday = fields.Boolean(string="Thrusday",track_visibility='onchange')
    opt_friday = fields.Boolean(string="Friday",track_visibility='onchange')
    opt_saturday = fields.Boolean(string="Saturday",track_visibility='onchange')
    opt_sunday = fields.Boolean(string="Sunday",track_visibility='onchange')

    is_monday_in_range = fields.Boolean(string="Is Monday In Range",compute="_compute_range_days")
    is_tuesday_in_range = fields.Boolean(string="Is Tuesday In Range",compute="_compute_range_days")
    is_wednesday_in_range = fields.Boolean(string="Is Wednesday In Range",compute="_compute_range_days")
    is_thursday_in_range = fields.Boolean(string="Is Thursday In Range",compute="_compute_range_days")
    is_friday_in_range = fields.Boolean(string="Is Friday In Range",compute="_compute_range_days")
    is_saturday_in_range = fields.Boolean(string="Is Saturday In Range",compute="_compute_range_days")
    is_sunday_in_range = fields.Boolean(string="Is Sunday In Range",compute="_compute_range_days")

    monday_meal_id = fields.Many2one('kw_canteen_meal_type',domain=[('code','=','veg')],
        readonly=True,default=lambda self:self.env['kw_canteen_meal_type'].search([('code','=','veg')]).id,track_visibility='onchange')
    tuesday_meal_id = fields.Many2one('kw_canteen_meal_type',domain=[('code','=','veg')], 
       readonly=True,default=lambda self:self.env['kw_canteen_meal_type'].search([('code','=','veg')]).id,track_visibility='onchange')
    wedday_meal_id = fields.Many2one('kw_canteen_meal_type',string="Wednesday Meal",track_visibility='onchange')
    thursday_meal_id = fields.Many2one('kw_canteen_meal_type',domain=[('code','=','veg')], 
       readonly=True,default=lambda self:self.env['kw_canteen_meal_type'].search([('code','=','veg')]).id,track_visibility='onchange')
    friday_meal_id = fields.Many2one('kw_canteen_meal_type',track_visibility='onchange')
    saturday_meal_id = fields.Many2one('kw_canteen_meal_type',track_visibility='onchange')
    sunday_meal_id = fields.Many2one('kw_canteen_meal_type',track_visibility='onchange')
    
    monday_vg_count=fields.Char(string="No of Veg")
    monday_nvg_count=fields.Char(string="No of Non-Veg")
    
    tuesday_vg_count=fields.Char(string="No of Veg")
    tuesday_nvg_count=fields.Char(string="No of Non-Veg")
    
    wednesday_vg_count=fields.Char(string="No of Veg")
    wednesday_nvg_count=fields.Char(string="No of Non-Veg")
    
    thursday_vg_count=fields.Char(string="No of Veg")
    thursday_nvg_count=fields.Char(string="No of Non-Veg")
    
    friday_vg_count=fields.Char(string="No of Veg")
    friday_nvg_count=fields.Char(string="No of Non-Veg")

    saturday_vg_count=fields.Char(string="No of Veg")
    saturday_nvg_count=fields.Char(string="No of Non-Veg")

    sunday_vg_count=fields.Char(string="No of Veg")
    sunday_nvg_count=fields.Char(string="No of Non-Veg")

    

    def prepare_day_names_from_date_range(self,start_date,end_date):
        day_list = []
        for day in range((end_date- start_date).days + 1):
            particular_date = start_date + timedelta(days=day)
            day_list.append(particular_date.weekday())
        return day_list

    @api.constrains('opt_monday', 'opt_tuesday','opt_wedday', 'opt_thursday','opt_friday','opt_saturday','opt_sunday')
    def must_select_weekday_meal(self):
        if  self.opt_monday==False and self.opt_tuesday==False and self.opt_wedday==False and self.opt_thursday==False and self.opt_friday==False and self.opt_saturday==False and self.opt_sunday==False:
            raise ValidationError(("You have to select weekday meal."))
    
    @api.onchange('meal_for')
    def set_menu_domain(self):
        if self.meal_for and self.meal_for == 'others':
            return {
                'domain':{
                    'monday_meal_id':[('code','in',['veg','nonveg'])],
                    'tuesday_meal_id':[('code','in',['veg','nonveg'])],
                    'thursday_meal_id':[('code','in',['veg','nonveg'])],
                    'saturday_meal_id':[('code','in',['veg','nonveg'])],
                }
            }
        
        if self.meal_for and self.meal_for == 'self':
            self.is_company_guest = False
            return {
                'domain':{
                    'monday_meal_id':[('code','=','veg')],
                    'tuesday_meal_id':[('code','=','veg')],
                    'thursday_meal_id':[('code','=','veg')],
                }
            }

    @api.depends('start_date','end_date')
    def _compute_range_days(self):
        for meal in self:
            if meal.start_date and meal.end_date:
                day_list = self.prepare_day_names_from_date_range(meal.start_date,meal.end_date)
                # 0 to 4 i.e monday to friday
                if 0 in day_list:
                    meal.is_monday_in_range = True
                if 1 in day_list:
                    meal.is_tuesday_in_range = True
                if 2 in day_list:
                    meal.is_wednesday_in_range = True
                if 3 in day_list:
                    meal.is_thursday_in_range = True
                if 4 in day_list:
                    meal.is_friday_in_range = True
                if 5 in day_list:
                    meal.is_saturday_in_range = True
                if 6 in day_list:
                    meal.is_sunday_in_range = True
                
    
    @api.constrains('start_date')
    def validate_start_date(self):
        for record in self:
            if record.is_company_guest == False:
                current_time = datetime.now().time()
                my_time = datetime.strptime('04:30:00','%H:%M:%S').time()
                if record.start_date and date.today() >= record.start_date and current_time > my_time :
                    raise ValidationError('You must apply meal request before 10 AM.')

    @api.onchange('start_date','end_date')
    def validate_start_end_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date: 
            raise ValidationError('End date must be greater than start darte.')

    @api.constrains('start_date','end_date')
    def validate_weekdays(self):
        for guest_meal in self:
            employee_guest_meals = self.sudo().search([('employee_id', '=', guest_meal.employee_id.id),('id', '!=', self.id)])
            # if employee_guest_meals.filtered(lambda r: not r.end_date):
            #     raise ValidationError(f'Guest meal request is already running for {guest_meal.employee_id.name}')
            # if is_end_date:
            # else:
            has_group_canteen_manager = self.env.user.has_group('kw_canteen.canteen_manager_group')
            for meal in employee_guest_meals:
                if  has_group_canteen_manager and meal.meal_for =="self" and guest_meal.meal_for =="self":
                    if guest_meal.start_date >= meal.start_date and guest_meal.start_date <= meal.end_date:
                        raise ValidationError(f'Guest meal request is already running for {guest_meal.employee_id.name}')
                    elif guest_meal.end_date >= meal.start_date and guest_meal.end_date <= meal.end_date:
                        raise ValidationError(f'Guest meal request is already running for {guest_meal.employee_id.name}')
                
    def action_approve_guest_meal(self):
        self.state = 'approved'

    def action_apply_guest_meal(self):
        self.state = 'approved'

    def action_cancel_guest_meal(self):
        if date.today() < self.start_date:
            self.state = 'cancel'
        else:
            raise ValidationError("Guest meal cann't be cancelled")
     
    # def guest_meal_expired(self):
    #     if self.start_date:
    #         today = date.today()
    #         end_date = self.end_date
    #         if today > end_date:
    #             self.state = 'expired'

    @api.multi
    def view_form(self):
        tree_view_id = self.env.ref('kw_canteen.view_kw_canteen_guest_meal_tree').id
        form_view_id = self.env.ref('kw_canteen.view_kw_canteen_guest_meal_form').id
        guest_rec = self.env['kw_canteen_guest_meal'].sudo().search([('state','!=','draft')])
        if self.env.user.has_group('kw_canteen.canteen_manager_group'):
            if guest_rec:
                action =  {
                    'name':'Guest Meal',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'kw_canteen_guest_meal',
                    'views':  [(tree_view_id, 'tree'),(form_view_id, 'form')],
                    'context':{'search_default_filter_self_record':1 , 'search_default_this_month_guest_meal':1},
                    'domain':['|',('id','in',guest_rec.ids),('employee_id','=',self.env.user.employee_ids.id)],
                    'target': 'self',
                }
                return action
            else:
                guest_rec = self.env['kw_canteen_guest_meal'].sudo().search([('employee_id','=',self.env.user.employee_ids.id)])
                if guest_rec:
                    action =  {
                        'name':'Guest Meal',
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'kw_canteen_guest_meal',
                        'views':  [(tree_view_id, 'tree'),(form_view_id, 'form')],
                        'context':{'search_default_filter_self_record':1 , 'search_default_this_month_guest_meal':1},
                        'domain':[('id','in',guest_rec.ids)],
                        'target': 'self',
                    }
                    return action
                else:
                    action =  {
                        'name':'Guest Meal',
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'kw_canteen_guest_meal',
                        'views':  [(form_view_id, 'form')],
                        'context':{'search_default_filter_self_record':1 , 'search_default_this_month_guest_meal':1},
                        'target': 'self',
                    }
                    return action
        else:
            self_guest_rec = self.env['kw_canteen_guest_meal'].sudo().search([('employee_id','=',self.env.user.employee_ids.id)])
            if self_guest_rec:
                action =  {
                'name':'Guest Meal',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'kw_canteen_guest_meal',
                'views':  [(tree_view_id, 'tree'),(form_view_id, 'form')],
                'context':{'search_default_filter_self_record':1 , 'search_default_this_month_guest_meal':1},
                'target': 'self',
            }
                return action
            else:
                action =  {
                    'name':'Guest Meal',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'kw_canteen_guest_meal',
                    'views':  [(form_view_id, 'form')],
                    'context':{'search_default_filter_self_record':1 , 'search_default_this_month_guest_meal':1},
                    'target': 'self',
                }
                return action
        