# -*- coding: utf-8 -*-
# © 2018-Today Aktiv Software (http://aktivsoftware.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields,api,_
from odoo.exceptions import UserError, ValidationError
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from pytz import timezone, UTC
from datetime import timedelta
from collections import defaultdict
from odoo.tools import float_utils
from datetime import datetime,date
from pytz import utc
import math


class HrHolidays(models.Model):
    _inherit = 'hr.leave'
    _name = 'hr.leave'
    _description = "Leave"

    sandwich_rule = fields.Boolean('Sandwich Rule')
    hr_consider_sandwich_rule= fields.Boolean('Apply Sandwich Rule',default=True)
    night_shift = fields.Boolean(default=False)
    count_no_of_leave = fields.Integer('Number Of Leave')
    report_note = fields.Text('Comments by Manager')



    @api.onchange('holiday_status_id', 'request_date_from', 'request_date_to', 'number_of_days_display',
                  'hr_consider_sandwich_rule', 'commuted_leave_selection')
    def compute_number_of_leave(self):
        days = 0.0
        list_age = []
        if self.holiday_status_id:
            if self.holiday_status_id:
                if self.holiday_status_id.sandwich_rule and self.request_unit_half == False and self.request_unit_half_2 == False:
                    print("????????????????????????????????////////////////123")
                    self.hr_consider_sandwich_rule = True
                    if self.date_to and self.date_from:
                        time_delta = self.date_to - self.date_from
                        days = math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
                    print("if number_of_days_display teuwwwww11111", days)
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>", self.hr_consider_sandwich_rule)
                else:
                    self.sandwich_rule = False
                    if self.holiday_status_id.leave_type.code == 'Restricted Holiday':
                        if self.date_to and self.date_from:
                            time_delta = self.date_to - self.date_from
                            days = math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
                            print(days, 'FLOAT')
                    else:
                        print(self.date_to,self.date_from, self.id, 'DEEpDate data')
                        if self.date_to and self.date_from and self.request_unit_half == False and self.request_unit_half_2 == False:
                            days = self._get_number_of_days(self.date_from, self.date_to, self.employee_id.id)
                            print(days, 'DDDDDDDDDDDD')
                        if self.date_to and self.date_from and self.request_unit_half == True or self.request_unit_half_2 == True:
                            days = self._get_number_of_days(self.date_from, self.date_to, self.employee_id.id)
                            print('duasssssssssssssssssssssssssss', days)
                            if isinstance(days, dict):
                                days = days['days']
                            if days == 1:
                                days = days - 0.5
                            else:
                                days = days
                            print(days, 'DDDDDDDDDDDD')
            elif self.hr_consider_sandwich_rule and self.employee_id and days:
                time_delta = self.date_to - self.date_from
                days = math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
                print("if sandwichrule teuwwwww", days)
            else:
                if self.employee_id and self.date_from and self.date_to:
                    self.sandwich_rule = False
                    days = self._get_number_of_days(self.date_from, self.date_to, self.employee_id.id)
                    print(days, 'yyyyyy')

            if self.commuted_leave_selection == 'Yes':
                self.commuted_leave = 'Commuted Leaves'
                days = days * 2
            else:
                self.commuted_leave = ''
            if isinstance(days, dict):
                days = days['days']
            self.number_of_days = days
            print("Actual Number of days in sandwich ", days)
            # if self.employee_id and self.employee_id.work_shifts:
            #     for holidays in self.employee_id.work_shifts.global_leave_ids:
            #         if holidays.holiday_type != 'rh':
            #             if holidays.date == self.request_date_to or holidays.date == self.request_date_from:
            #                 raise ValidationError(_('The selected dates are holidays itself'))

        if self.request_date_from and self.request_date_to:
            self.count_no_of_leave = (self.request_date_to - self.request_date_from).days + 1
        if self.holiday_status_id.leave_type.code != 'Half Pay Leave':
            self.commuted_leave_selection = 'No'
        if self.holiday_status_id.leave_type.code == 'Child Care Leave':
            today = date.today()
            relatives_ids = self.env['employee.relative'].search(
                [('employee_id', '=', self.employee_id.id), ('relate_type.name', 'in', ('Son', 'Daughter')),
                 ('status2', '!=', 'non_surviving')])
            print('relatives_ids-2154545454--------------', relatives_ids)
            for rec_child in relatives_ids:
                delta = today.year - rec_child.birthday.year - (
                            (today.month, today.day) < (rec_child.birthday.month, rec_child.birthday.day))
                print("???????????????????????????", delta)
                list_age.append(delta)
            number = min(list_age) if list_age else 0
            # print("list age", list_age, number)
            if number > 18:
                raise ValidationError(_('you are not allowed to take this leave as the age of childrens are above 18.'))
            if self.request_date_to and self.request_date_from:
                if self.request_date_from < today or self.request_date_to < today:
                    raise ValidationError(
                        _('you are not allowed to take this leave as the date selected are past date which are not allowed for CCL.'))

        if self.holiday_status_id.leave_type.code in ['Maternity Leave', 'Paternity Leave']:
            relatives_ids = self.env['employee.relative'].search(
                [('employee_id', '=', self.employee_id.id), ('relate_type.name', 'in', ('Son', 'Daughter')),
                 ('status2', '!=', 'non_surviving')])
            print('relatives_ids---------------', len(relatives_ids))
            if len(relatives_ids) >= 2:
                raise ValidationError(
                    _('You are not allowed to take this leave as you have already taken leaves for 2 childrens and for the 3rd child its not allowed according to rule.'))
        if self.holiday_status_id.leave_type.code == 'Paternity Leave':
            leaves_ids = self.env['hr.leave'].search(
                [('employee_id', '=', self.employee_id.id), ('holiday_status_id', '=', self.holiday_status_id.id), ('state', 'not in', ['cancel', 'refuse'])])
            print("Leaves////////////////////",(leaves_ids.ids), self.id)
            if self.id not in leaves_ids.ids:
                for leaves in leaves_ids:
                    if self.request_date_from:
                        days = (self.request_date_from - leaves.request_date_to).days
                        print("-0-0-0-0-0-0--0-0-00-0-", leaves.request_date_to, self.request_date_from, days)
                        if days < 300:
                            raise ValidationError(_('you are not allowed to take this leave according to paternity leave rule'))

    ## Nikunja - Aug 23 2021
    @api.constrains('holiday_status_id','commuted_leave_selection','request_date_from', 'request_date_to')
    # @api.onchange('holiday_status_id','request_date_from', 'request_date_to','number_of_days_display','hr_consider_sandwich_rule','commuted_leave_selection')
    def check_leave_type(self):
        days = 0.0
        if self.holiday_status_id and self.holiday_status_id.sandwich_rule:
            if self.holiday_status_id:
                if self.holiday_status_id.sandwich_rule and self.request_unit_half == False and self.request_unit_half_2 == False:
                    print("????????????????????????????????////////////////")
                    self.hr_consider_sandwich_rule = True
                    time_delta = self.date_to - self.date_from
                    days = math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
                    print("if number_of_days_display teuwwwww",days)
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>",self.hr_consider_sandwich_rule)
                else:
                    self.sandwich_rule = False
                    days = self._get_number_of_days(self.date_from, self.date_to,self.employee_id.id)
            elif self.hr_consider_sandwich_rule and self.employee_id and days:
                time_delta = self.date_to - self.date_from
                days = math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
                print("if sandwichrule teuwwwww",days)
            else:
                if self.employee_id and self.date_from and self.date_to:
                    self.sandwich_rule = False
                    days = self._get_number_of_days(self.date_from, self.date_to, self.employee_id.id)

            if self.commuted_leave_selection == 'Yes':
                self.commuted_leave = 'Commuted Leaves'
                days = days*2
            else:
                self.commuted_leave = ''
            print("Actual Number of days in sandwich ",days,self.holiday_status_id.leave_type.code)
            self.number_of_days = days
            if self.employee_id and self.employee_id.resource_calendar_id and self.holiday_status_id.leave_type.code != 'Half Pay Leave':
                for holidays in self.employee_id.resource_calendar_id.global_leave_ids:
                    if holidays.holiday_type != 'rh':
                        if holidays.date == self.request_date_to or holidays.date == self.request_date_from:
                            raise ValidationError(_('The selected dates are holidays itself'))

        # self.duration_display = days
        # self.no_of_days_display_half = days
    ## Nikunja - Aug 23 2021

    # @api.onchange('date_from','date_to')
    # def check_date_from_live(self):
    #     res = {}
    #     if self.employee_id:
    #         days=[]
    #         for each in self.employee_id.resource_calendar_id.attendance_ids:
    #             if int(each.dayofweek) not in days:
    #                 days.append(int(each.dayofweek))
    #         if self.date_from:
    #
    #             start_date=self.date_from
    #             date_number=start_date.weekday()
    #             if date_number not in days:
    #                 res.update({'value': {'date_to': '','date_from': '','number_of_days_display':0.00,'sandwich_rule':False}, 'warning': {
    #                            'title': 'Validation!', 'message': 'This day is already holiday.'}})
    #         if self.date_to:
    #             end_date=self.date_to
    #             date_number=end_date.weekday()
    #             if date_number not in days:
    #                 res.update({'value': {'date_to': '','number_of_days_display':0.00,'sandwich_rule':False}, 'warning': {
    #                            'title': 'Validation!', 'message': 'This day is already holiday.'}})
    #
    #     return res

    @api.onchange('request_date_from_period', 'request_hour_from', 'request_hour_to',
                  'request_date_from', 'request_date_to',
                  'employee_id')
    def _onchange_request_parameters(self):
        if not self.request_date_from:
            self.date_from = False
            return

        if self.request_unit_half or self.request_unit_hours:
            self.request_date_to = self.request_date_from

        if not self.request_date_to:
            self.date_to = False
            return

        # roster_id = self.env['hr.attendance.roster'].search([('employee_id','=',self.employee_id.id),('date','=',self.date_from.date())],limit=1)
        # print("-------------roster_id", roster_id)
        # if roster_id and roster_id.shift_id:
        #     if roster_id.shift_id.night_shift:
        #         self.night_shift = True
        #     else:
        #         self.night_shift = False
        #     domain =[('calendar_id', '=',roster_id.shift_id.id)]
        # else:
        #     if self.employee_id.resource_calendar_id.night_shift or self.env.user.company_id.resource_calendar_id.night_shift:
        #         self.night_shift = True
        #     else:
        #         self.night_shift = False

        domain = [('calendar_id', '=',self.employee_id.resource_calendar_id.id or self.env.user.company_id.resource_calendar_id.id)]
        attendances = self.env['resource.calendar.attendance'].search(domain, order='dayofweek, day_period DESC')

        # find first attendance coming after first_day
        attendance_from = next((att for att in attendances if int(att.dayofweek) >= self.request_date_from.weekday()),
                               attendances[0])
        # find last attendance coming before last_day
        attendance_to = next(
            (att for att in reversed(attendances) if int(att.dayofweek) <= self.request_date_to.weekday()),
            attendances[-1])

        if self.request_unit_half:
            if self.request_date_from_period == 'am':
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_from.hour_to)
            else:
                hour_from = float_to_time(attendance_to.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)
        elif self.request_unit_hours:
            # This hack is related to the definition of the field, basically we convert
            # the negative integer into .5 floats
            hour_from = float_to_time(
                abs(self.request_hour_from) - 0.5 if self.request_hour_from < 0 else self.request_hour_from)
            hour_to = float_to_time(
                abs(self.request_hour_to) - 0.5 if self.request_hour_to < 0 else self.request_hour_to)
        elif self.request_unit_custom:
            hour_from = self.date_from.time()
            hour_to = self.date_to.time()
        else:
            hour_from = float_to_time(attendance_from.hour_from)
            hour_to = float_to_time(attendance_to.hour_to)

        tz = self.env.user.tz if self.env.user.tz and not self.request_unit_custom else 'UTC'  # custom -> already in UTC
        self.date_from = timezone(tz).localize(datetime.combine(self.request_date_from, hour_from)).astimezone(
            UTC).replace(tzinfo=None)
        self.date_to = timezone(tz).localize(datetime.combine(self.request_date_to, hour_to)).astimezone(UTC).replace(
            tzinfo=None)

    # @api.multi
    # @api.depends('number_of_days')
    # def _compute_number_of_hours_display(self):
    #     for holiday in self:
    #         roster_id = self.env['hr.attendance.roster'].search([('employee_id', '=', holiday.employee_id.id), ('date', '=', holiday.date_from.date())], limit=1)
    #         # print("---------2----roster_id", roster_id)
    #         if roster_id and roster_id.shift_id:
    #             calendar = roster_id.shift_id
    #         else:
    #             calendar = holiday.employee_id.resource_calendar_id or self.env.user.company_id.resource_calendar_id
    #         if holiday.date_from and holiday.date_to:
    #             number_of_hours = calendar.get_work_hours_count(holiday.date_from, holiday.date_to)
    #             holiday.number_of_hours_display = number_of_hours or (holiday.number_of_days * HOURS_PER_DAY)
    #         else:
    #               holiday.number_of_hours_display = 0

    def write(self, values):
        print(values, self.id,'valuessss')
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            user_id = self.employee_id.user_id
            assigne_group = self.env.ref('hr_holidays.group_hr_holidays_user')
            assigne_group.sudo().write({'users': [(4, user_id.id)]})


            result = super(HrHolidays, self).write(values)
            assigne_group.sudo().write({'users': [(3, user_id.id)]})
        else:
            result = super(HrHolidays, self).write(values)
        return result


ROUNDING_FACTOR = 16

class ResourceMixin(models.AbstractModel):
    _inherit = "resource.mixin"

    def get_work_days_data(self, from_datetime, to_datetime, compute_leaves=True, calendar=None, domain=None):
        """
            By default the resource calendar is used, but it can be
            changed using the `calendar` argument.

            `domain` is used in order to recognise the leaves to take,
            None means default value ('time_type', '=', 'leave')

            Returns a dict {'days': n, 'hours': h} containing the
            quantity of working time expressed as days and as hours.
        """
        # roster_id = self.env['hr.attendance.roster'].search([('employee_id', '=', self.id), ('date', '=', from_datetime.date())], limit=1)
        # print("---------3----roster_id", roster_id)
        # if roster_id and roster_id.shift_id:
        #     calendar = roster_id.shift_id
        # else:
        calendar = calendar or self.resource_calendar_id
        resource = self.resource_id

        # naive datetimes are made explicit in UTC
        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=utc)

        # total hours per day: retrieve attendances with one extra day margin,
        # in order to compute the total hours on the first and last days
        from_full = from_datetime - timedelta(days=1)
        to_full = to_datetime + timedelta(days=1)
        intervals = calendar._attendance_intervals(from_full, to_full, resource)
        day_total = defaultdict(float)
        for start, stop, meta in intervals:
            day_total[start.date()] += (stop - start).total_seconds() / 3600

        # actual hours per day
        if compute_leaves:
            intervals = calendar._work_intervals(from_datetime, to_datetime, resource, domain)
            print("printprintprintprintprintprintprintprint",compute_leaves,intervals)
        else:
            intervals = calendar._attendance_intervals(from_datetime, to_datetime, resource)
        day_hours = defaultdict(float)
        for start, stop, meta in intervals:
            day_hours[start.date()] += (stop - start).total_seconds() / 3600

        # compute number of days as quarters
        days = sum(
            float_utils.round(ROUNDING_FACTOR * day_hours[day] / day_total[day]) / ROUNDING_FACTOR
            for day in day_hours
        )
        return {
            'days': days,
            'hours': sum(day_hours.values()),
        }
