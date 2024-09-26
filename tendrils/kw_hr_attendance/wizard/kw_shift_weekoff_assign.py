# -*- coding: utf-8 -*-
import re
from datetime import datetime, time
from dateutil import rrule as rrule_module

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class KwShiftWeekoffAssign(models.TransientModel):
    _name           = 'kw_shift_weekoff_assign_wizard'
    _description    = 'Kwantify Shift Weekoff Manage Wizard'

    DAY_LIST = [
        ('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'),
        ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')
    ]

    branch_id       = fields.Many2many(string="Branch/SBU",comodel_name='kw_res_branch',relation='kw_shift_weekoff_assign_kw_res_branch_rel',column1='branch_sbu_id',column2='weekoff_branch_wizard_id')
    shift_ids       = fields.Many2many(string='Shifts',comodel_name='resource.calendar',relation='kw_shift_weekoff_assign_resource_calendar_rel',column1='resource_calendar_id',column2='weekoff_shift_wizard_id', domain="[('employee_id','=',False)]")
    start_date      = fields.Date(string='Start Date')
    end_date        = fields.Date( string='End Date')
    # week_off_day    =  fields.Selection(string="Week Off/Weekend" ,selection=DAY_LIST)  

    rrule_type = fields.Selection([
        ('weekly', 'Week(s)'), ('monthly', 'Month(s)'),
    ], string='Recurrence', help="Let the event automatically repeat at that interval")

    mo              = fields.Boolean('Mon')
    tu              = fields.Boolean('Tue')
    we              = fields.Boolean('Wed')
    th              = fields.Boolean('Thu')
    fr              = fields.Boolean('Fri')
    sa              = fields.Boolean('Sat')
    su              = fields.Boolean('Sun')

    month_by = fields.Selection([
        ('date', 'Date of month'), ('day', 'Day of month')
    ], string='Option', default='date')
    day = fields.Integer('Date of month', default=1)
    week_list = fields.Selection([
        ('MO', 'Monday'), ('TU', 'Tuesday'), ('WE', 'Wednesday'), ('TH', 'Thursday'),
        ('FR', 'Friday'), ('SA', 'Saturday'), ('SU', 'Sunday')], string='Weekday')
    byday = fields.Selection([
        ('1', 'First'), ('2', 'Second'), ('3', 'Third'),
        ('4', 'Fourth'), ('5', 'Fifth'), ('-1', 'Last')
    ], string='By day')
    rrule = fields.Char('Recurrent Rule', compute='_compute_rrule', store=True)

    @api.constrains('shift_ids')
    def validate_shift_ids(self):
        for record in self:
            if not record.shift_ids:
                raise ValidationError("Please select at least one shift to include from list")

    @api.onchange('branch_id')
    def _get_shift_ids(self):
        domain = {'domain': {'shift_ids': []}}
        for record in self:
            if record.branch_id:
                record.shift_ids = False
                domain['domain']['shift_ids'] = [('branch_id','in',record.branch_id.ids),('employee_id','=',False)]
                # record.shift_ids = self.env['resource.calendar'].search([('branch_id','in',record.branch_id.ids),('employee_id','=',False)])
        return domain

    @api.depends('byday', 'start_date', 'end_date', 'rrule_type', 'month_by', 'mo',
                 'tu', 'we', 'th', 'fr', 'sa', 'su', 'day', 'week_list')
    def _compute_rrule(self):
        """ Gets Recurrence rule string according to value type RECUR of iCalendar from the values given.
            :return dictionary of rrule value.
        """
        for record in self:
            record.rrule = record._rrule_serialize()
           
    @api.model
    def create(self, vals):
        new_record = super(KwShiftWeekoffAssign, self).create(vals)
        self.action_assign_week_offs(new_record)
        return new_record
    
    @api.multi
    def write(self,vals):
        update_record = super(KwShiftWeekoffAssign, self).write(vals)
        self.action_assign_week_offs(self)
        return update_record

    def action_assign_week_offs(self,new_record):
        resource_rec = self.env['resource.calendar'].browse(new_record.shift_ids.ids)
        date_set = list(rrule_module.rrulestr(str(new_record.rrule), dtstart=new_record.start_date, forceset=True, ignoretz=True))

        for record in resource_rec:
            week_off_holidays = []
            for week_off_date in date_set:
                week_off_date = week_off_date.date()
                existing_week_offs  = record.global_leave_ids.filtered(lambda rec : rec.start_date == week_off_date and rec.holiday_type == '1')
                reason = 'Week Off'  # 'Weekend' if week_off_date.weekday() == 6 else 'Weekoff'
                if not existing_week_offs:
                    week_off_holidays.append((0, 0, {'date_from': datetime.combine(week_off_date, time.min),
                                                     'date_to': datetime.combine(week_off_date, time(23, 59, 59)),
                                                     'name': reason,
                                                     'start_date': week_off_date,
                                                     'holiday_type': '1'}))
            if week_off_holidays:
                record.global_leave_ids = week_off_holidays
               
        self.env.user.notify_success(message='Shift Week Off Assigned Successfully.')
        return 

    @api.multi
    def _rrule_serialize(self):
        """ Compute rule string according to value type RECUR of iCalendar
            :return: string containing recurring rule (empty if no rule)
        """
        if self.end_date and self.end_date < self.start_date:
            raise UserError('End date can not be less than start date.')       

        def get_week_string(freq):
            weekdays = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
            if freq == 'weekly':
                byday = [field.upper() for field in weekdays if self[field]]
                if byday:
                    return ';BYDAY=' + ','.join(byday)
            return ''

        def get_month_string(freq):
            if freq == 'monthly':
                if self.month_by == 'date' and (self.day < 1 or self.day > 31):
                    raise UserError("Please select a proper day of the month.")

                if self.month_by == 'day' and self.byday and self.week_list:  # Eg : Second Monday of the month
                    return ';BYDAY=' + self.byday + self.week_list
                elif self.month_by == 'date':  # Eg : 16th of the month
                    return ';BYMONTHDAY=' + str(self.day)
            return ''

        def get_end_date():
            final_date = fields.Date.to_string(self.end_date)
            end_date_new = ''.join((re.compile('\d')).findall(final_date)) + 'T235959Z' if final_date else False
            return ((end_date_new and (';UNTIL=' + end_date_new)) or '')

        freq = self.rrule_type  # day/week/month/year
        result = ''
        if freq:
            result = 'FREQ=' + freq.upper() + get_week_string(
                freq) + get_end_date() + get_month_string(freq)
        return result
