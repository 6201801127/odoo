# -*- coding: utf-8 -*-
# ########################
# Modification History :
# 24-Jul-2020 : Extra column, Extra early entry field is added, By : T Ketaki Debadarshini

# ########################

import math, re
from datetime import datetime, time, timedelta, date
from pytz import timezone, utc
from dateutil.rrule import DAILY, rrule, MO, TU, WE, TH, FR, SA, SU

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round

from odoo.addons.resource.models.resource import datetime_to_string, float_to_time, string_to_datetime, Intervals, \
    HOURS_PER_DAY


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    kw_id = fields.Integer(string='Tendrils Id')
    branch_id = fields.Many2one(string='Branch', comodel_name='kw_res_branch', ondelete='restrict', )
    hours_per_day = fields.Float("Average hour per day", default=HOURS_PER_DAY, compute="_compute_work_hours_per_day",
                                 store=True,
                                 help="Average hours per day a resource is supposed to work with this calendar.")
    grace_time = fields.Float(string='Grace Time', default=0)
    late_exit_time = fields.Float(string='Late Exit Hour', )
    early_entry_time = fields.Float(string='Early Entry Hour', )
    extra_early_entry_time = fields.Float(string='Extra Early Entry Hour', )

    late_entry_time = fields.Float(string='Extra Late Entry Hour', )
    extra_late_exit_time = fields.Float(string='Extra Late Exit Hour', )
    cross_shift = fields.Boolean(string='Cross Shift', )

    late_entry_half_leave_time = fields.Float(string='Late Entry (Half Day Applicable)', default=3)
    late_entry_full_leave_time = fields.Float(string='Late Entry (Full Day Applicable)', default=5)
    early_exit_half_leave_time = fields.Float(string='Early Exit (Half Day Applicable)', default=2)

    start_date = fields.Date(string='Start Date', autocomplete="off")
    end_date = fields.Date(string='End Date', autocomplete="off")
    week_off_day = fields.Selection(string="Week Off/Weekend",
                                    selection=[('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'),
                                               ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')])
    # By Nikunja : Start
    public_holidays = fields.Many2many(string='Public Holidays', comodel_name='hr.holidays.public.line',
                                       compute='_get_public_holidays', store=False)
    onsite_shift = fields.Boolean(string="Onsite Shift")
   
    @api.depends('attendance_ids')
    def _compute_work_hours_per_day(self):
        if self.env.context.get('use_old_onchange_hours_per_day'):
            return super()._onchange_hours_per_day()
        for record in self:    
            attendances = record.attendance_ids.filtered(lambda att: not att.date_from and not att.date_to)
            hour_count = 0.0
            for att in attendances:
                hour_count += att.hour_to - att.hour_from - att.rest_time

            if attendances:
                record.hours_per_day = float_round(
                    hour_count / float(len(set(attendances.mapped('dayofweek')))),
                    precision_digits=2)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            record_name = record.name + ' (' + record.branch_id.city+')' if record.branch_id.city else record.name
            result.append((record.id, record_name))
        return result

    @api.constrains('name')
    def name_input_validation(self):
        for record in self:
            record._check_name()
            # if not (re.match('^[ a-zA-Z0-9:()-]+$',record.name)):
            #     raise ValidationError("Please remove special characters from shift name.")

    def _check_name(self):
        if self.search_count([('name', '=', self.name), ('employee_id', '=', False), ('id', '!=', self.id),
                              ('branch_id', '=', self.branch_id.id)]):
            raise ValidationError(
                f"Shift Name for '{self.branch_id.city}' branch is already exists. Please change the branch or shift name.")

    @api.depends('branch_id','excluded_public_holidays_ids')
    def _get_public_holidays(self):
        for record in self:
            if record.branch_id:
                record.public_holidays = self.env['hr.holidays.public.line'].search(
                    ['|',('shift_ids','=',record.id),('branch_ids', '=', record.branch_id.id),
                     ('id', 'not in', record.excluded_public_holidays_ids.ids)]).ids

    # By Nikunja : End
    @api.constrains('grace_time')
    def timing_validations(self):
        for record in self:
            if record.late_entry_time and record.grace_time:
                if record.late_entry_time < record.grace_time:
                    raise ValidationError("Late Entry time must be grater than grace time.")
    
    @api.constrains('late_entry_full_leave_time', 'late_entry_half_leave_time')
    def validate_late_entry_time(self):
        for record in self:
            if record.late_entry_full_leave_time and record.late_entry_half_leave_time:
                if record.late_entry_full_leave_time < record.late_entry_half_leave_time:
                    raise ValidationError("Late entry full day leave hours must be greater than late entry half day leave hours.")

    @api.constrains('late_exit_time', 'extra_late_exit_time')
    def validate_late_exit_time(self):
        for record in self:
            if record.extra_late_exit_time < record.late_exit_time:
                raise ValidationError("Extra late exit time must be greater than late exit time.")

    @api.constrains('early_entry_time', 'extra_late_exit_time', 'attendance_ids')
    def validate_early_entry_late_exit_time(self):
        for record in self:
            if not record.cross_shift:
                c_date = datetime.now().date()
                min_datetime = datetime.combine(c_date, time.min)
                max_datetime = datetime.combine(c_date, time.max)

                if record.early_entry_time and record.attendance_ids:
                    entry_time = float_to_time(record.early_entry_time)
                    entry_time_delta = timedelta(hours=entry_time.hour, minutes=entry_time.minute)
                    attendance_time_deltas = record.attendance_ids.mapped(lambda rec: datetime.combine(c_date, float_to_time(rec.hour_from)) - min_datetime)
                    min_shift_time = min(attendance_time_deltas)
                    if entry_time_delta >= min_shift_time:
                        raise ValidationError("Early entry time should be greater than previous day.")
                    
                if record.extra_late_exit_time and record.attendance_ids:
                    exit_time = float_to_time(record.extra_late_exit_time)
                    exit_time_delta = timedelta(hours=exit_time.hour, minutes=exit_time.minute)
                    exit_attendance_time_deltas = record.attendance_ids.mapped(lambda rec: max_datetime - datetime.combine(c_date, float_to_time(rec.hour_to)))
                    max_shift_time = min(exit_attendance_time_deltas)
                    if exit_time_delta >= max_shift_time:
                        if self.select_flexi_hrs and self.select_flexi_hrs in ('90min',):
                            pass
                        else:
                            raise ValidationError("Extra late exit time should be less than next day.")

    @api.constrains('attendance_ids')
    def validate_attendance(self):
        for record in self:
            if record.attendance_ids:
                # dayofweek [0,6] | hour_from , hour_to | date_from , date_to
                for attendance in record.attendance_ids:
                    except_attendance = record.attendance_ids - attendance
                    if not attendance.date_from and not attendance.date_to:
                        ex_att = except_attendance.filtered(lambda r: r.dayofweek == attendance.dayofweek and ((r.hour_from < attendance.hour_from < r.hour_to) or (r.hour_from < attendance.hour_to < r.hour_to)) and not (r.date_from and r.date_to))
                        if ex_att:
                            raise ValidationError(f"Working hour {attendance.name} overlaps with others. Please modify it.")
                    if attendance.date_from and attendance.date_to:
                        except_attendances = except_attendance.filtered(lambda rec: rec.date_from != False and rec.date_to != False)
                        ex_att = except_attendances.filtered(lambda r: r.dayofweek == attendance.dayofweek and ((r.hour_from < attendance.hour_from < r.hour_to) or (r.hour_from < attendance.hour_to < r.hour_to)) and ((r.date_from < attendance.date_from < r.date_to) or (r.date_from < attendance.date_to < r.date_to)))
                        if ex_att:
                            raise ValidationError(f"Working hour {attendance.name} overlaps with others. Please modify it.")

    @api.model
    def create(self, values):
        new_record = super(ResourceCalendar,self).create(values)
        self.env['kw_attendance_grace_time_log'].create({
            'shift_id': new_record.id,
            'grace_time': new_record.grace_time,
            'effective_from': new_record.create_date.date()
        })
        return new_record
    
    @api.multi
    def write(self, values):
        grace_time_log = self.env['kw_attendance_grace_time_log']
        for record in self:
            if 'grace_time' in values:
                if self.grace_time != values['grace_time']:
                    vals = {}
                    last_record = grace_time_log.search([('shift_id', '=', record.id)], order='id asc')
                    if not last_record:
                        grace_time_log.create({
                            'effective_from': record.create_date.date(),
                            'effective_to': date.today() - timedelta(days=1),
                            'shift_id': record.id,
                            'grace_time': record.grace_time
                        })
                    else:
                        last_record[-1].write({
                            'effective_to': date.today() - timedelta(days=1)
                        })
                    grace_time_log.create({
                        'effective_from': date.today(),
                        'shift_id': record.id,
                        'grace_time': values['grace_time']
                    })
        update_record = super(ResourceCalendar, self).write(values)
        return update_record

    # #action to assign week offs
    def action_assign_week_offs(self):
        if not self.start_date or not self.end_date or not self.week_off_day:
            raise ValidationError("Please enter all the fields required to assign holidays (Start Date, End Date, Week Off Day).")
        if self.end_date < self.start_date:
            raise ValidationError("End date should not be less than start date.")
        week_off_holidays = []
        resource_rec = self.env['resource.calendar'].browse(self.id)
        # print(resource_rec)
        # print(self.id)

        date_set = list(rrule(DAILY, dtstart=self.start_date, until=self.end_date, byweekday=[int(self.week_off_day)]))
        
        for week_off_date in  date_set:     
            # print(week_off_date)
            week_off_date = week_off_date.date()
            existing_week_offs = resource_rec.global_leave_ids.filtered(lambda rec: rec.start_date == week_off_date and rec.holiday_type == '1')  # and rec.end_date == week_off_date
            # print(existing_week_offs)
            reason = 'Week Off'  # if self.week_off_day and self.week_off_day == '6' else 'Weekoff' # By Nikunja

            if not existing_week_offs:
                week_off_holidays.append((0, 0, {'date_from': datetime.combine(week_off_date, time.min),
                                                 'date_to': datetime.combine(week_off_date, time(23, 59, 59)),
                                                 'name': reason,
                                                 'start_date': week_off_date,
                                                 'holiday_type': '1'}))  # ,'end_date':week_off_date

        if week_off_holidays:
            self.global_leave_ids = week_off_holidays

        return 

    # #method to return employee current shift as per the given date

    def _get_shift_grace_time(self, shift_id, search_date):
        # print(search_date,shift_id)
        if date.today() == search_date:
            return shift_id.grace_time
        else:
            shift_history_log = self.env['kw_attendance_grace_time_log'].search(
                [('shift_id', '=', shift_id.id), ('effective_from', '<=', search_date),
                 ('effective_to', '>=', search_date)], order='effective_from desc', limit=1)
           
            # print(shift_history_log)
            return shift_history_log.grace_time if shift_history_log else shift_id.grace_time

    # #action to assign working hours
    def action_assign_working_hours(self):
        if not any([self.first_half_hour_from, self.first_half_hour_to, self.second_half_hour_from, self.second_half_hour_to]):
            raise ValidationError("Please enter all the fields required to assign working hour details.")

        elif self.first_half_hour_from >= self.first_half_hour_to:
            raise ValidationError("First half start time should not be greater than end time.")

        elif self.second_half_hour_from >= self.second_half_hour_to and not self.cross_shift:
            raise ValidationError("Second half start time should not be greater than end time.")

        elif not self.cross_shift and (self.second_half_hour_from < self.first_half_hour_to or self.second_half_hour_from <= self.first_half_hour_from):
            raise ValidationError("Second half should start after first half time.")     
        
        existing_working_hours = self.attendance_ids.filtered(lambda rec: not rec.date_from and not rec.date_to) if self.attendance_ids else []

        working_hours = []
        invalid_data = self.env['resource.calendar.attendance']

        week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for week_day in range(7):
            first_half_rec = self.attendance_ids.filtered(lambda rec: rec.dayofweek == str(week_day) and rec.day_period == 'morning' and not (rec.date_from or rec.date_to))
            second_half_rec = self.attendance_ids.filtered(lambda rec: rec.dayofweek == str(week_day) and rec.day_period == 'afternoon' and not (rec.date_from or rec.date_to))

            first_half_data = {'name': week_days[week_day] + ' First Half',
                               'dayofweek': str(week_day),
                               'hour_from': self.first_half_hour_from,
                               'hour_to': self.first_half_hour_to,
                               'day_period': 'morning',
                               'rest_time': self.rest_hour}

            second_half_data = {'name': week_days[week_day] + ' Second Half',
                                'dayofweek': str(week_day),
                                'hour_from': self.second_half_hour_from,
                                'hour_to': self.second_half_hour_to,
                                'day_period': 'afternoon'}

            if first_half_rec:
                singletone = first_half_rec[0]
                invalid_data |= first_half_rec - singletone
                singletone.write(first_half_data)
            else:
                working_hours.append(first_half_data)

            if second_half_rec:
                one_record = second_half_rec[0]
                invalid_data |= second_half_rec - one_record
                one_record.write(second_half_data)
            else:
                working_hours.append(second_half_data)
        # print(flexi_working_hours)

        if working_hours:
            self.attendance_ids = working_hours
            
        if invalid_data:
            invalid_data.unlink()
        # self._compute_work_hours_per_day()
        return
    

class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    @api.constrains('name')
    def name_validation(self):
        for record in self:
            if not (re.match('^[ a-zA-Z0-9]+$',record.name)):
                raise ValidationError("Working Hour Name input accepts only alphanumeric values.")
