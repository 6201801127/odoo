from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class HRLeaveAllocationInherit(models.Model):
    _inherit='hr.leave.allocation'


    @api.onchange('holiday_status_id')
    def hr_take_leave(self):
        for rec in self:
            check_casual = self.env['hr.leave.type'].search([('is_casual_lt', '=', True)], limit=1)
            if rec.holiday_status_id == check_casual.id:
                if rec.number_of_days > 5.00:
                    raise ValidationError(_('You are not able to take more than 5 days casual leave'))



    def hr_leave_casual_cron(self):
        first_day = datetime.now().date().replace(month=1, day=1)
        last_day = first_day + relativedelta(months=12) - relativedelta(days=1)
        name = 'Casual Leave ' + str(first_day.year)
        c_leave_type_name = self.env['leave.type.master'].create({
            'name': name,
            'code' : name,
            })
        c_leave_type = self.env['hr.leave.type'].create({
            'name': c_leave_type_name.id,
            'color_name': 'lightgreen',
            'request_unit': 'day',
            'time_type': 'leave',
            'allocation_type': 'fixed',
            'validity_start': first_day,
            'validity_stop': last_day,
            'is_casual_lt': True,
        })
        n_name = str(self.env.user.company_id.name) + ' - ' + str(name)
        allocate_leave = self.env['hr.leave.allocation'].create({
                    'name': n_name,
                    'holiday_status_id': c_leave_type.id,
                    'holiday_type': 'company',
                    'mode_company_id': self.env.user.company_id.id,
                    'number_of_days': 8.00,
                }
            )
        allocate_leave.sudo().action_approve()



    def hr_leave_half_pay_cron(self):
        first_day = datetime.now().date().replace(day=1)
        last_day = first_day + relativedelta(months=7) - relativedelta(days=1)
        name = 'Half Pay Leave ' + str(first_day.year)
        c_leave_type_name = self.env['leave.type.master'].create({
            'name': name,
            'code' : name,
            })
        c_leave_type = self.env['hr.leave.type'].create({
            'name': c_leave_type_name.id,
            'color_name': 'lightgreen',
            'request_unit': 'day',
            'time_type': 'leave',
            'allocation_type': 'fixed',
            'validity_start': first_day,
            'validity_stop': last_day,
            'is_half_pay': True,
        })
        n_name = str(self.env.user.company_id.name) + ' - ' + str(name)
        allocate_leave = self.env['hr.leave.allocation'].create({
                    'name': n_name,
                    'holiday_status_id': c_leave_type.id,
                    'holiday_type': 'company',
                    'mode_company_id': self.env.user.company_id.id,
                    'number_of_days': 10.00,
                }
            )
        allocate_leave.sudo().action_approve()

    def hr_leave_earned_cron(self):
        name = 'Earned Leave'
        c_leave_type_name = self.env['leave.type.master'].create({
            'name': name,
            'code' : name,
            })
        c_leave_type = self.env['hr.leave.type'].create({
            'name': c_leave_type_name,
            'color_name': 'lightgreen',
            'request_unit': 'day',
            'time_type': 'leave',
            'allocation_type': 'fixed',
            'hr_consider_sandwich_rule': True,
        })
        n_name = str(self.env.user.company_id.name) + ' - ' + str(name)
        allocate_leave = self.env['hr.leave.allocation'].create({
                    'name': n_name,
                    'holiday_status_id': c_leave_type.id,
                    'holiday_type': 'company',
                    'mode_company_id': self.env.user.company_id.id,
                    'number_of_days': 15.00,
                }
            )
        allocate_leave.sudo().action_approve()






class HRLeaveTypeInherit(models.Model):
    _inherit='hr.leave.type'

    is_casual_lt = fields.Boolean('Is casual')
    is_half_pay = fields.Boolean('Is Half-pay')
    hr_consider_sandwich_rule = fields.Boolean('Apply Sandwich Rule')
    is_maternity = fields.Boolean('Is Maternity')




class HRLeaveInherit(models.Model):
    _inherit='hr.leave'

    is_commuted = fields.Boolean('Is Commuted')
    medical_certificate = fields.Binary("Medical Certificate")
    is_half_pay = fields.Boolean('Is Half-pay')

    @api.onchange('holiday_status_id')
    def onchange_is_holiday_status_id(self):
        for rec in self:
            rec.is_half_pay = rec.holiday_status_id.is_half_pay
            rec.hr_consider_sandwich_rule = rec.holiday_status_id.hr_consider_sandwich_rule
            if rec.holiday_status_id and rec.holiday_status_id.is_maternity == True:
                if rec.employee_id.gender == 'female':
                    if rec.number_of_days > 180.00:
                        raise ValidationError(_('You are not able to take more than 1800 days Maternity leave'))
                else:
                    raise ValidationError(_('You are not able to take Maternity leave'))

    @api.onchange('is_commuted')
    def onchange_is_commuted(self):
        for rec in self:
            if rec.is_commuted == True:
                if rec.holiday_status_id:
                    pass



    @api.onchange('number_of_days')
    def onchange_number_od(self):
        for rec in self:
            if rec.holiday_status_id and rec.holiday_status_id.is_half_pay == True:
                if rec.number_of_days:
                    rec.number_of_days = 2*rec.number_of_days



class HRPrlInherit(models.Model):
    _inherit='hr.payslip'

    half_pay = fields.Float('Half Pay', compute='_compute_half_pay')


    @api.depends('employee_id','date_from','date_to')
    def _compute_half_pay(self):
        for line in self:
            sum = 0
            check_leave = self.env['hr.leave'].search([('employee_id', '=', line.employee_id.id)])
            for leave in check_leave:
                if leave.holiday_status_id.is_half_pay == True:
                    sum += leave.number_of_days
            line.half_pay = sum