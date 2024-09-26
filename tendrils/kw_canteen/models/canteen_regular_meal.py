from ast import literal_eval
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date,datetime,timedelta

class CanteenRegularMeal(models.Model):
    _name = 'kw_canteen_regular_meal'
    _description = 'Regular Meal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    # def get_current_logged_employee(self):
    #     emp = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
    #     return emp

    employee_id = fields.Many2one('hr.employee', string="Employee Name", required=True, tracking=False, readonly=True, default=lambda self : self.env.user.employee_ids[0:1])
    department_id = fields.Char(string='Department', related='employee_id.department_id.name')
    infra_unit_location_id = fields.Many2one('kw_res_branch_unit', string="Infra Unit Location", related="employee_id.branch_unit_id",store=True)
    desig_id = fields.Char(string='Designation', related='employee_id.job_id.name')

    # food_type = fields.Selection([('veg', 'Veg'),('non-veg', 'Non-Veg'),], required=True, string="Food Category")
    start_date = fields.Date(string="Start Date", required=True ,track_visibility='onchange')
    end_date = fields.Date(string="End Date",track_visibility='onchange')
    
    remarks = fields.Text(string="Remarks" , track_visibility='onchange')
    
    close_meal_ids = fields.One2many(comodel_name="exclusion_canteen_meal", inverse_name="regular_id",)
    apply_exclusion_boolean = fields.Boolean(string="Exclusion" , track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approved', 'Approved'), ('expired', 'Expired')], string="Status", default="draft" , track_visibility='onchange')

    opt_monday = fields.Boolean(string="Monday",track_visibility='onchange')
    opt_tuesday = fields.Boolean(string="Tuesday",track_visibility='onchange')
    opt_wedday = fields.Boolean(string="Wednesday",track_visibility='onchange')
    opt_thursday = fields.Boolean(string="Thrusday",track_visibility='onchange')
    opt_friday = fields.Boolean(string="Friday",track_visibility='onchange')
    opt_saturday = fields.Boolean(string="Saturday",track_visibility='onchange')
    opt_sunday = fields.Boolean(string="Sunday",track_visibility='onchange')
    is_special = fields.Boolean(string="Is Special",track_visibility='onchange')
    exclusion_applied_today = fields.Boolean(string="Today Exclusion", search="_search_today_exclusion",compute='chk_exclusion')
    no_meal_choice = fields.Boolean(string="No Meal", search="_search_no_meal_today",compute='chk_choice')

    @api.constrains('opt_monday', 'opt_tuesday','opt_wedday', 'opt_thursday','opt_friday','opt_saturday','opt_sunday')
    def must_select_weekday_meal(self):
        if  self.opt_monday==False and self.opt_tuesday==False and self.opt_wedday==False and self.opt_thursday==False and self.opt_friday==False and self.opt_saturday==False and self.opt_sunday==False:
            raise ValidationError(("You have to select weekday meal."))
                
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
    
    @api.constrains('close_meal_ids')
    def exclusion_end_date_valid(self):
        for record in self:
            for meal in record.close_meal_ids:
                overlapping = record.close_meal_ids.filtered(lambda r:(r.start_date <= meal.start_date <= r.end_date) or (r.start_date <= meal.end_date <= r.end_date) or (meal.start_date < r.start_date and meal.end_date > r.end_date)) - meal
                if overlapping:           
                    raise ValidationError(f'Meal exclusion already overlaps with exclusion having Start Date : {overlapping[0].start_date} End Date : {overlapping[0].end_date}')
                    
    @api.multi
    def chk_exclusion(self):
        for record in self:
            pass
    
    @api.multi
    def chk_choice(self):
        for record in self:
            pass
    @api.multi
    def _search_no_meal_today(self, operator, value):
        day = date.today().weekday()
        meal_ids = self.env['kw_canteen_regular_meal'].sudo().search([])
        if day == 6:
            sunday_meal = meal_ids.filtered(lambda x :x.opt_sunday == False)
            return [('id','in',sunday_meal.ids)]
        elif day == 0:
            monday_meal = meal_ids.filtered(lambda x :x.opt_monday == False)
            return [('id','in',monday_meal.ids)]
        elif day == 1:
            tuesday_meal = meal_ids.filtered(lambda x :x.opt_tuesday == False)
            return [('id','in',tuesday_meal.ids)]
        elif day == 2:
            wednesday_meal = meal_ids.filtered(lambda x :x.opt_wedday == False)
            return [('id','in',wednesday_meal.ids)]
        elif day == 3:
            thursday_meal = meal_ids.filtered(lambda x :x.opt_thursday == False)
            return [('id','in',thursday_meal.ids)]
        elif day == 4:
            friday_meal = meal_ids.filtered(lambda x :x.opt_friday == False)
            return [('id','in',friday_meal.ids)]
        elif day == 5:
            saturday_meal = meal_ids.filtered(lambda x :x.opt_saturday == False)
            return [('id','in',saturday_meal.ids)]


   
    @api.multi
    def _search_today_exclusion(self, operator, value):
        # day = date.today().weekday()
        current_date = date.today()
        exclusion_ids = self.env['exclusion_canteen_meal'].search([('start_date','<=',current_date),('end_date','>=',current_date),('exclusion_type','=','temporary')])
        return [('close_meal_ids','in',exclusion_ids.ids)]
    
    @api.onchange('opt_monday','opt_tuesday','opt_wedday','opt_thursday','opt_friday')
    def onchange_opt_for_meal(self):
        # if not self.opt_monday:
        #     self.monday_meal_id=False
        # if not self.opt_tuesday:
        #     self.tuesday_meal_id=False
        if not self.opt_wedday:
            self.wedday_meal_id=False
        # if not self.opt_thursday:
        #     self.thursday_meal_id=False
        if not self.opt_friday:
            self.friday_meal_id=False
  

    @api.constrains('start_date')
    def validate_meal_start_date(self):
        for meal in self:
            if meal.start_date and date.today() >= meal.start_date:
                    raise ValidationError('You must apply meal request after current date.')

    # @api.constrains('end_date')
    # def validate_meal_end_date(self):
    #     for meal in self:
    #         if meal.end_date and (meal.end_date - meal.start_date).days < 15:
    #             # if diff_date < 15:
    #             raise ValidationError('You should apply meal request for minimum of 15 Days.')





    @api.constrains('start_date','end_date')
    def validate_weekdays(self):
        for meal in self:
            # if meal.start_date and date.today() >= meal.start_date:
            #         raise ValidationError('You must apply meal request after current date.')
                
            if meal.end_date and (meal.end_date - meal.start_date).days < 15:
                raise ValidationError('You should apply meal request for minimum of 15 Days.')
                
            employee_regular_meals = meal.sudo().search([('employee_id', '=', self.employee_id.id),('id', '!=', self.id)])
            # if employee_regular_meals.filtered(lambda r: r.end_date == False):
            #     raise ValidationError(f'Regular meal request is already running for {meal.employee_id.name}')
            # else:
            for regular_meal in employee_regular_meals:
                if meal.end_date == False:
                    if regular_meal.end_date == False:
                        raise ValidationError(f'Regular meal request is already running for {meal.employee_id.name}')
                    elif regular_meal.end_date and regular_meal.start_date:
                        if meal.start_date <= regular_meal.end_date:
                            raise ValidationError(f'Regular meal request is already running for {meal.employee_id.name}')
                elif meal.start_date and meal.end_date:
                    if regular_meal.start_date and regular_meal.end_date:
                        if meal.start_date >= regular_meal.start_date and meal.start_date <= regular_meal.end_date:
                            raise ValidationError(f'Regular meal request is already running for {meal.employee_id.name}')
                        elif meal.end_date >= regular_meal.start_date and meal.end_date <= regular_meal.end_date:
                            raise ValidationError(f'Regular meal request is already running for {meal.employee_id.name}')
                    elif meal.start_date >= regular_meal.start_date and regular_meal.end_date == False:
                        raise ValidationError(f'Regular meal request is already running for {meal.employee_id.name}')

    def action_approve_regular_meal(self):
        self.state = 'approved'

    def action_apply_regular_meal(self):
        self.state = 'approved'
     

    # def regular_meal_expired(self):
    #     if self.start_date:
    #         today = date.today()
    #         end_date_ = self.end_date
    #         if today > end_date_:
    #             self.state = 'expired'


    @api.model
    def create(self, values):
        canteen_param = self.env['ir.config_parameter'].sudo().get_param('kw_canteen.canteen')
        # param = self.env['ir.config_parameter'].sudo()
        new_record = super(CanteenRegularMeal, self).create(values)
        if self.env.user.has_group('kw_canteen.canteen_manager_group'):
            new_record.state = 'approved'
        authorities = False
        if canteen_param:
            authorities = literal_eval(canteen_param)
        if authorities:
            empls = self.env['hr.employee'].search([('id', 'in', authorities), ('active', '=', True)])
            mail_template = self.env.ref('kw_canteen.canteen_regular_meal_apply_mail_template')
            email_to = ','.join(empls.mapped('work_email'))
            employee = new_record.employee_id.name
            employee_code = new_record.employee_id.emp_code
            email_from = new_record.employee_id.work_email
            mail_template.with_context(emails=email_to,regular_meal_start_date = new_record.start_date,employee=employee,email_from=email_from,employee_code=employee_code).send_mail(
                new_record.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        return new_record

    @api.model
    def end_date_expire_cron(self):
        data = self.search([('state', '!=', 'expired'), ('end_date', '<=', date.today())])
        data.write({'state': 'expired'})
        guest_rec = self.env['kw_canteen_guest_meal'].sudo().search([('state', '!=', 'expired'), ('end_date', '<=', date.today())])
        if guest_rec:
            guest_rec.write({'state': 'expired'})

    def open_wizard(self):
        for rec in self:
            view_id = self.env.ref('kw_canteen.kw_canteen_meal_exclusion_wizard_form').id
            return {
                'name':'Exclusion',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'kw_canteen_meal_exclusion_wizard',
                'view_id': view_id,
                'context': {'current_id':rec.id,},
                'target': 'new',
            }

    @api.multi
    def view_form(self):
        tree_view_id = self.env.ref('kw_canteen.view_kw_canteen_regular_meal_tree').id
        form_view_id = self.env.ref('kw_canteen.view_kw_canteen_regular_meal_form').id
        regular_rec = self.env['kw_canteen_regular_meal'].sudo().search([('state','!=','draft')])
        if self.env.user.has_group('kw_canteen.canteen_manager_group'):
            if regular_rec:
                action =  {
                    'name':'Regular Meal',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'kw_canteen_regular_meal',
                    'views':  [(tree_view_id, 'tree'),(form_view_id, 'form')],
                    'context': {'search_default_filter_self_record':1 ,'search_default_this_month_regular_meal':1},
                    'target': 'self',
                }
                return action
            else:
                regular_rec = self.env['kw_canteen_regular_meal'].sudo().search([('employee_id','=',self.env.user.employee_ids.id)])
                if regular_rec:
                    action =  {
                        'name':'Regular Meal',
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'kw_canteen_regular_meal',
                        'views':  [(tree_view_id, 'tree'),(form_view_id, 'form')],
                        'context': {'search_default_filter_self_record':1 ,'search_default_this_month_regular_meal':1},
                        'domain':[('id','in',regular_rec.ids)],
                        'target': 'self',
                    }
                    return action
                else:
                    action =  {
                        'name':'Regular Meal',
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'kw_canteen_regular_meal',
                        'views':  [(form_view_id, 'form')],
                        'context': {'search_default_filter_self_record':1 ,'search_default_this_month_regular_meal':1},
                        'target': 'self',
                    }
                    return action
        else:
            self_regular_rec = self.env['kw_canteen_regular_meal'].sudo().search([('employee_id','=',self.env.user.employee_ids.id)])
            if self_regular_rec:
                action =  {
                'name':'Regular Meal',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'kw_canteen_regular_meal',
                'views':  [(tree_view_id, 'tree'),(form_view_id, 'form')],
                'context': {'search_default_filter_self_record':1 ,'search_default_this_month_regular_meal':1},
                'target': 'self',
            }
                return action
            else:
                action =  {
                    'name':'Regular Meal',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'kw_canteen_regular_meal',
                    'views':  [(form_view_id, 'form')],
                    'context': {'search_default_filter_self_record':1 ,'search_default_this_month_regular_meal':1},
                    'target': 'self',
                }
                return action
        

