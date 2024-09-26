# -*- coding: utf-8 -*-
#########################
# Modification History :
# 02-Jul-2020 : Day of the week added, By : Nikunja
# 03-Jul-2020 : End Date removed from global leaves, By : T Ketaki Debadarshini
# 22-Jul-2020 : Personalized Calendar, By : T Ketaki Debadarshini
# 04-Nov-2020 : color modification for overlapping days,roster working days, By : T Ketaki Debadarshini
#########################
from datetime import datetime, time
from dateutil.rrule import rrule, WEEKLY
from pytz import timezone, utc

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons.resource.models.resource import datetime_to_string, float_to_time, string_to_datetime, Intervals


class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'

    # optional_holiday    = fields.Boolean('Optional Holiday', default=False, )
    start_date = fields.Date(string='Start Date', autocomplete="off")
    # end_date            = fields.Date(string='End Date',)

    holiday_type = fields.Selection(string="Holiday Type",
                                    selection=[('1', 'Week Off'), ('2', 'Fixed Holiday'), ('3', 'Restricted Holiday')],
                                    default='2')
    # Mod by Nikunja : start
    day = fields.Char(string='Day of Week', compute='_get_day_name', store=False)

    # branch_id           = fields.Many2one('kw_res_branch','Branch',related="calendar_id.branch_id")

    @api.depends('start_date')
    def _get_day_name(self):
        for record in self:
            record.day = record.start_date.strftime("%A") if record.start_date else False
    # Mod by Nikunja : End   

    @api.onchange('start_date')
    def change_datetime(self):
        for rec in self:
            # print(rec.calendar_id)
            if rec.calendar_id and not rec.resource_id:
                # tz              = timezone(rec.calendar_id.tz)
                rec.date_from = datetime.combine(rec.start_date, time.min) if rec.start_date else False
                rec.date_to = datetime.combine(rec.start_date, time(23, 59, 59)) if rec.start_date else False

    @api.model
    def get_calendar_master_data(self,branch_id=None,shift_id=None,employee_id=None):
        # print(branch_id)
        branch_id = int(branch_id) if branch_id else False
        shift_id = int(shift_id) if shift_id else False
        employee_id = int(employee_id) if employee_id else False

        shift_id = shift_id or self.env.user.employee_ids.resource_calendar_id.id or self.env.user.branch_id.default_shift_id.id

        branch_id = branch_id or self.env.user.employee_ids.resource_calendar_id.branch_id.id or self.env.user.branch_id.id or self.env.user.company_id.head_branch_id.id

        employee_id = employee_id or self.env.user.employee_ids.id

        branches = self.env['kw_res_branch'].search([('active', '=', 'TRUE')])
        # print(branch_id)
        shift_master = self.env['resource.calendar'].search([('employee_id', '=', False), ('branch_id', '=', branch_id)])

        # #Start : employee master
        employee = self.env.user.employee_ids
        emp_domain = ['|', ('user_id', '=', self.env.user.id), ('id', 'in', employee.child_ids.ids)]

        if self.env.user.has_group('hr_attendance.group_hr_attendance_manager'):
            emp_domain = []
        elif self.env.user.has_group('kw_hr_attendance.group_hr_attendance_roaster'):
            roaster_members =  self.env['kw_roaster_group_config'].search([('group_head_id', '=',employee.id)]).group_member_ids.ids
            emp_domain = ['|', ('user_id', '=', self.env.user.id), '|', ('id', 'in', employee.child_ids.ids),
                          ('id', 'in', roaster_members)]

        employee_data = self.env['hr.employee'].search(emp_domain)
        # #ENd : employee master

        data = {'branches': branches.read(['alias']),
                'shift_master': shift_master.read(['name']),
                'employee_master': employee_data.read(['name', 'emp_code']),
                'default_branch': branch_id,
                'default_shift': shift_id,
                'default_employee': employee_id}

        # print(data)
        return data

    # #method to get the global leaves , BY: T Ketaki Debadarshini, on : 27-April-2020
    @api.model
    def get_calendar_global_leaves(self, branch_id=None, shift_id=None, personal_calendar=1, employee_id=None,
                                   cal_start=False, cal_end=False):

        branch_id = int(branch_id) if branch_id else False
        shift_id = int(shift_id) if shift_id else False
        employee_id = int(employee_id) if employee_id else False

        branch_id = branch_id or self.env.user.employee_ids.resource_calendar_id.branch_id.id or self.env.user.branch_id.id or self.env.user.company_id.head_branch_id.id
        shift_id = shift_id or self.env.user.employee_ids.resource_calendar_id.id or self.env.user.branch_id.default_shift_id.id
        employee_id = employee_id or self.env.user.employee_ids.id

        calendar, public_holidays, shift_leaves = [], self.env['hr.holidays.public.line'], self.env['resource.calendar.leaves']
        hhplo = self.env['hr.holidays.public.line']
        
        # #for personalize calendar
        if personal_calendar == 1:
            if employee_id:
                calendar, public_holidays, shift_leaves = self.get_personalized_calendar(employee_id, cal_start, cal_end)
                # else:
            #     calendar,public_holidays,shift_leaves = [],self.env['hr.holidays.public.line'],self.env['resource.calendar.leaves']
        else:
            shift_master_record = self.env['resource.calendar'].sudo().browse(shift_id)
            shift_leaves = shift_master_record.global_leave_ids
            excluded_public_holidays = shift_master_record.excluded_public_holidays_ids.ids

            # #get data from public holidays
            if shift_master_record.onsite_shift:
                states_filter = [('shift_ids','=',shift_id),('year_id.holiday_assign_type', '=','onsite_holiday'),
                             ('id', 'not in', excluded_public_holidays)]  # #'|',('branch_ids', '=', False),

            else:
                states_filter = ['|',('shift_ids','=',shift_id),('branch_ids', '=', branch_id),
                             ('id', 'not in', excluded_public_holidays)]  # #'|',('branch_ids', '=', False),

            public_holidays = hhplo.search(states_filter)
            # print(public_holidays)
        for line in public_holidays:
            calendar.append({'id': line.id,
                             'name': line.name,
                             'year': line.date.year,
                             'week_off': '2',
                             'optional_holiday': False,
                             'color': '#d83d2b',
                             'date_from': line.date,
                             'date_to': line.date,
                             'formatted_holiday_date': line.date.strftime("%d %b"),
                             'overlap_public_holiday': 0,
                             'prime_color': '#d83d2b'})

        for record in shift_leaves:
            exist_public_holiday = public_holidays.filtered(lambda r: r.date == record.date_from.date())
            exist_shift_holiday = shift_leaves.filtered(lambda r: r.date_from == record.date_from and r.holiday_type == '2')

            prime_color = '#F5BB00' if record.holiday_type == '1' else '#d83d2b'
            bg_color = '#d83d2b' if exist_public_holiday or exist_shift_holiday else prime_color

            calendar.append({'id': record.id,
                             'name': record.name,
                             'year': record.date_from.year,
                             'week_off': record.holiday_type,
                             'optional_holiday': False,
                             'color': bg_color,
                             'date_from': record.date_from.date(),
                             'date_to': record.date_to.date(),
                             'formatted_holiday_date': record.date_from.strftime("%d %b"),
                             'overlap_public_holiday': 0,
                             'prime_color': prime_color})
        sorted_calendar = sorted(calendar, key=lambda r: r['date_from']) if calendar else []
        infodict = dict(holiday_calendar=sorted_calendar) if calendar else dict()
        return infodict

    # #get employee personalized calendar by : T Ketaki Debadarshini, On: 22-jul-2020
    def get_personalized_calendar(self, employee_id, cal_start=False, cal_end=False):
        if employee_id:
            employee_id = self.env['hr.employee'].browse(employee_id)
            if cal_start and cal_end:
                cal_start_date = cal_start
                cal_end_date = cal_end
            else:
                cal_start_date = datetime.now().date().replace(month=1, day=1)
                cal_end_date = datetime.now().date().replace(month=12, day=31)

            branch_id = employee_id.resource_calendar_id.branch_id.id or employee_id.user_id.branch_id.id or employee_id.user_id.company_id.head_branch_id.id
            emplyee_shift = employee_id.resource_calendar_id or employee_id.user_id.branch_id.default_shift_id
            # #get branch holidays
            if employee_id.resource_calendar_id.onsite_shift:
                branch_filter = [('shift_ids','=',employee_id.resource_calendar_id.id),('year_id.holiday_assign_type', '=','onsite_holiday'), (
                    'id', 'not in', emplyee_shift.excluded_public_holidays_ids.ids)]
            else:
                branch_filter = ['|',('shift_ids','=',employee_id.resource_calendar_id.id),('branch_ids', '=', branch_id), (
                    'id', 'not in', emplyee_shift.excluded_public_holidays_ids.ids)]  # ,('date','not in',roaster_shift_dates)
            public_holidays = self.env['hr.holidays.public.line'].search(branch_filter)

            calendar = []
            roster_shift_records = self.env['kw_employee_roaster_shift'].search(
                [('employee_id', '=', employee_id.id), ('date', '>=', cal_start_date), ('date', '<=', cal_end_date)],
                order="date asc")

            for roaster_info in roster_shift_records:
                exist_public_holiday = public_holidays.filtered(lambda r: r.date == roaster_info.date)
                prime_color = '#108bbb' if roaster_info.week_off_status else '#ffffff'
                color = '#d83d2b' if exist_public_holiday else prime_color

                calendar.append({
                    'name': 'Roster Week Off' if roaster_info.week_off_status else 'Roster Working Day <br/>' + str(roaster_info.shift_id.name),
                    'year': roaster_info.date.year,
                    'week_off': '1' if roaster_info.week_off_status else '0',
                    'optional_holiday': False,
                    'color': color,
                    'date_from': roaster_info.date,
                    'date_to': roaster_info.date,
                    'formatted_holiday_date': roaster_info.date.strftime("%d %b"),
                    'overlap_public_holiday': 1 if exist_public_holiday and not roaster_info.week_off_status else 0,
                    'prime_color': prime_color})

            roaster_shift_dates = roster_shift_records.mapped('date')
            # print(roaster_shift_dates)
            shift_leaves = emplyee_shift.global_leave_ids.filtered(lambda r: cal_start_date <= r.start_date <= cal_end_date and r.start_date not in roaster_shift_dates)
            return [calendar, public_holidays, shift_leaves]
