from odoo import api, fields, models
from datetime import datetime, timedelta


class SpecialMealCancellation(models.TransientModel):
    _name = 'manual_special_meal_cancellation'
    _description = 'Canteen Special meal Cancellation'
    # _rec_name = 'branch_id'

   

    from_date = fields.Date(string="From Date", required=True, autocomplete="off")
    to_date = fields.Date(string="To Date", required=True, autocomplete="off")
    # branch_id = fields.Many2one('kw_res_branch', string="Branch/SBU")
    emp_date_ids = fields.Many2many('kw_canteen_manual_emp_info', )
    
    @api.multi
    def generate_dates(self):
        for record in self:
            if record.from_date and record.to_date:
                # #Start :: create dates for the selected date range
                all_dates = self.env['kw_canteen_cancel_dates'].search([])
                date_list = []
                for day in range(int ((record.to_date - record.from_date).days)+1):
                    search_date = record.from_date + timedelta(day)
                    if not all_dates.filtered(lambda rec : rec.name == search_date):
                        date_list.append({'name':search_date})
                if date_list:
                    self.env['kw_canteen_cancel_dates'].create(date_list)
                # #End :: create dates for the selected date range

                # #Start :: create employee attendnace for the selected date-range
                attendance_dates = self.env['kw_canteen_cancel_dates'].search([('name', '>=', record.from_date), ('name', '<=', record.to_date)])
                emp_date_info = self.env['kw_canteen_manual_emp_info'].search([])
                employee_ids = self.env['kw_canteen_regular_meal'].search([('is_special','=',True),('state','=','approved')])  # ('user_id.branch_id', '=', self.branch_id.id),
                record.emp_date_ids = False
                record.emp_date_ids = [
                    (0, 0, {                        
                        'employee_id': employee.employee_id.id,
                        'attendance_date': rec.id,
                    })
                    # if there isn't a demo line record for the user, create a new one
                    if not emp_date_info.filtered(lambda x: x.employee_id == employee and x.attendance_date==rec) else
                    # otherwise, return the line
                    (4, emp_date_info.filtered(lambda x: x.employee_id == employee and x.attendance_date==rec)[0].id)
                    for rec in attendance_dates
                    for employee in employee_ids
                ]
               
            # else:
            #     raise ValidationError("Please enter all the required fields!\n (1) From Date\n (2) To Date\n ")
  
    
    
    @api.multi        
    def create_manual_cancellation(self):
        for rec in self:
            if rec.emp_date_ids:
                for emp_attendance in rec.emp_date_ids:
                    if emp_attendance.present_status == True:
                        day = emp_attendance.attendance_date.name.weekday()
                        employee_ids = self.env['kw_canteen_regular_meal'].sudo().search([('employee_id','=',emp_attendance.employee_id.id),('state','=','approved')],limit=1)
                        veg,nonveg =0,0
                        # if day == 2:
                        wednesday =employee_ids.filtered(lambda r:r.opt_wedday == True).mapped('wedday_meal_id.code')
                        if  wednesday == 'veg':                   
                            veg = 1
                        else:
                            nonveg = 1
                        friday =employee_ids.filtered(lambda r:r.opt_friday == True).mapped('friday_meal_id.code')
                        if  friday== 'veg':                   
                            veg = 1
                        else:
                            nonveg = 1
                        saturday_meal_id =employee_ids.filtered(lambda r:r.opt_saturday == True).mapped('saturday_meal_id.code')
                        if  saturday_meal_id == 'veg':                   
                            veg = 1
                        else:
                            nonveg = 1
                        sunday_meal_id =employee_ids.filtered(lambda r:r.opt_sunday == True).mapped('sunday_meal_id.code')
                        if  sunday_meal_id == 'veg':                   
                            veg = 1
                        else:
                            nonveg = 1
                        meal = self.env['meal_bio_log'].sudo().search([('employee_id','=',emp_attendance.employee_id.id),('meal_type_id.meal_code','=','R'),('recorded_date','=',emp_attendance.attendance_date.name)],limit=1)
                        if not meal:
                            self.env['meal_bio_log'].sudo().create({
                                'employee_id':emp_attendance.employee_id.id,
                                'emp_code':emp_attendance.employee_id.emp_code,
                                'infra_unit_location_id':emp_attendance.employee_id.infra_unit_loc_id.id,
                                'recorded_date':emp_attendance.attendance_date.name,
                                'meal_type':'regular',
                                'meal_type_id':self.env['price_master_configuration'].sudo().search([('meal_code','=','R')],limit=1).id,
                                'no_of_veg': 1 if day == 0 or day == 1 or day ==3 else veg,
                                'no_of_non_veg': 0 if day == 0 or day == 1 or day ==3 else nonveg,
                                'meal_price':self.env['price_master_configuration'].sudo().search([('meal_code','=','R')],limit=1).price,
                                'is_special':True,
                                'card_punch' :'no'
                            })
                        else:
                            meal_price = self.env['price_master_configuration'].sudo().search([('meal_code','=','R')],limit=1).price
                            meal.write({
                                'meal_price':meal_price,
                                'total_price': (meal.total_meal * meal_price)/2,
                                'is_special':True
                                })
                       

        self.env.user.notify_success(message='Manual deatails has been  updated for the selected employees.')
        # return new_record

        return {'type': 'ir.actions.act_window_close'}


class SpecialMealCancellationEmployeeInfo(models.TransientModel):
    _name = 'kw_canteen_manual_emp_info'
    _description = 'Canteen Employee Info'
    _order = "attendance_date"

    employee_id = fields.Many2one('hr.employee', string="Employees", required=True)
    attendance_date = fields.Many2one('kw_canteen_cancel_dates', string="Date")
    present_status = fields.Boolean(string='Present', default=True)
    
   

class CanteenCancellationDates(models.TransientModel):
    _name = 'kw_canteen_cancel_dates'
    _description = 'Canteen Meal Cancellation Date Info'
    _order = "name"

    name = fields.Date(string="Date", required=True)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.name.strftime("%d-%b-%Y")))
        return result