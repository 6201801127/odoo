from odoo import models, fields, api, _
from datetime import time, datetime, timedelta
from datetime import date, datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import pytz

class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'
    _description = ' Resource Calendar Leaves'

    @api.model
    def get_calendar_master_data(self,branch_id=None,shift_id=None,employee_id=None):
        branch_id = int(branch_id) if branch_id else False
        shift_id = int(shift_id) if shift_id else False
        employee_id = int(employee_id) if employee_id else False

        shift_id = shift_id or self.env.user.employee_ids.resource_calendar_id.id

        branch_id = branch_id or self.env.user.branch_id.id

        employee_id = employee_id or self.env.user.employee_ids.id

        branches = self.env['res.branch'].search([('active', '=', 'TRUE')])
        shift_master = self.env['resource.calendar'].search([('branch_id', '=', branch_id)])

        employee = self.env.user.employee_ids
        emp_domain = ['|', ('user_id', '=', self.env.user.id), ('id', 'in', employee.child_ids.ids)]
        employee_data = self.env['hr.employee'].search(emp_domain)
        # #ENd : employee master

        data = {'branches': branches.read(['name']),
                'shift_master': shift_master.read(['name']),
                'employee_master': employee_data.read(['name']),
                'default_branch': branch_id,
                'default_shift': shift_id,
                'default_employee': employee_id}
        return data

    @api.model
    def get_calendar_global_leaves(self, branch_id=None, shift_id=None, personal_calendar=1, employee_id=None,
                                   cal_start=False, cal_end=False):
        emp_timezone = pytz.timezone('UTC')
        branch_id = int(branch_id) if branch_id else False
        shift_id = int(shift_id) if shift_id else False
        employee_id = int(employee_id) if employee_id else False
        hr_employee = self.env['hr.employee'].sudo().search([])
        branch_id = branch_id or self.env.user.branch_id.id
        # print('branch_id++++++++++++1++++++++++',branch_id)
        shift_id = shift_id or self.env.user.employee_ids.calendar_id.id
        # print('shift_id++++++++++++2++++++++++',shift_id)
        employee_id = employee_id or self.env.user.employee_ids.id
        # print('employee_id++++++++++++2++++++++++',employee_id)


        calendar,rh_list,gh_list,week_off_list,holiday_list,public_holidays, shift_leaves = [],[],[],[],[],self.env['hr.holidays.public.line'], self.env['resource.calendar.leaves']
        if personal_calendar == 1:
            if employee_id:
                calendar, public_holidays, shift_leaves = self.get_personalized_calendar(employee_id, cal_start, cal_end)
        else:
            shift_master_record = self.env['resource.calendar'].browse(shift_id)
            # print("Shift_id---------------------------------",shift_master_record)
            shift_leaves = shift_master_record.global_leave_ids
            # print("Shift_id------------------2---------------",shift_leaves)

        for line in public_holidays:
            holiday_list.append({'id': line.id,
                             'name': line.name,
                             'year': line.date.year,
                             'week_off': '2',
                             'optional_holiday': False,
                             'color': '#d83d2b',
                             'date_from': line.date,
                             'date_to': line.date,
                             'formatted_holiday_date': line.date.strftime("%d %b"),
                             'overlap_public_holiday': 0,
                             'prime_color': '#d83d2b',
                             'priority': 1
                             })
        # print("================calendar===================",calendar)
            
        for record in shift_leaves:
            # exist_shift_holiday = shift_leaves.filtered(lambda r: r.date_from == record.date_from)

            # prime_color = '#00A09D' if record.holiday_type == 'rh' else '#d83d2b' if record.holiday_type== 'gh' else '#F5BB00'
            # bg_color = '#00A09D' if record.holiday_type == 'rh' else '#d83d2b' if record.holiday_type== 'gh' else '#F5BB00'
            if record.holiday_type == '3':
                rh_list.append({
                    'name': record.name,
                    'year': record.date_to.year,
                    'week_off': record.holiday_type,
                    'optional_holiday': False,
                    'color': '#00A09D',
                    'date_from': record.date_to.date(),
                    'date_to': record.date_to.date(),
                    'formatted_holiday_date': record.date_to.strftime("%d %b"),
                    'overlap_public_holiday': 0,
                    'prime_color': '#00A09D',
                    'priority': 2
                })
            elif record.holiday_type == '2':
                rh_list.append({
                    'name': record.name,
                    'year': record.date_to.year,
                    'week_off': record.holiday_type,
                    'optional_holiday': False,
                    'color': '#d83d2b',
                    'date_from': record.date_to.date(),
                    'date_to': record.date_to.date(),
                    'formatted_holiday_date': record.date_to.strftime("%d %b"),
                    'overlap_public_holiday': 0,
                    'prime_color': '#d83d2b',
                    'priority': 3
                })
            elif record.holiday_type == '1':
                rh_list.append({
                    'name': record.name,
                    'year': record.date_to.year,
                    'week_off': record.holiday_type,
                    'optional_holiday': False,
                    'color': '#F5BB00',
                    'date_from': record.date_to.date(),
                    'date_to': record.date_to.date(),
                    'formatted_holiday_date': record.date_to.strftime("%d %b"),
                    'overlap_public_holiday': 0,
                    'prime_color': '#F5BB00',
                    'priority':4
                })
            calendar = rh_list + gh_list + week_off_list + holiday_list
            # print("Calendar 2======================",calendar)
        sorted_calendar = sorted(calendar, key=lambda r: r['priority']) if calendar else []
        infodict = dict(holiday_calendar=sorted_calendar) if calendar else dict()
        sorted_date = sorted(calendar, key=lambda r: r['date_from']) if calendar else []
        infodict_name = dict(holiday_calendar=sorted_date) if calendar else dict()
        return [infodict,infodict_name]
    
    def get_personalized_calendar(self, employee_id, cal_start=False, cal_end=False):
        if employee_id:
            employee_id = self.env['hr.employee'].browse(employee_id)
            if cal_start and cal_end:
                cal_start_date = cal_start
                cal_end_date = cal_end
            else:
                cal_start_date = datetime.now().date().replace(month=1, day=1)
                cal_end_date = datetime.now().date().replace(month=12, day=31)

            branch_id = employee_id.user_id.branch_id.id
            emplyee_shift = employee_id.resource_calendar_id
            branch_filter = [('branch_ids', '=', branch_id)]  # ,('date','not in',roaster_shift_dates)
            calendar = []
            public_holidays = self.env['hr.holidays.public.line'].search(branch_filter)
            shift_leaves = emplyee_shift.global_leave_ids.filtered(lambda r: cal_start_date <= r.date_to.date() <= cal_end_date)
            return [calendar,public_holidays, shift_leaves]