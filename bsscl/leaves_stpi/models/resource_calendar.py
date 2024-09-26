import pytz
from odoo import models, fields, api, _
from datetime import time, datetime,timedelta
from datetime import date, datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'
    _description= ' Resource Calendar Branch'
    
    branch_id = fields.Many2one('res.branch',string="Center",required=True)
    max_allowed_rh = fields.Float(string='Max RH')
    # max_allowed_gh = fields.Float(string='Max Allowed Gestured Holiday')
    from_date = fields.Date(string='From Date',autocomplete="off")
    to_date = fields.Date(string='To Date',autocomplete="off")
    week_list = fields.Selection([
        ('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
        ('6', 'Saturday'),
        ('7', 'Sunday')
    ], string='Weekday')

    rh_leave_type=fields.Many2one('hr.leave.type', string='RH Leave Type')

    assign_holiday_action_perform = fields.Selection([('assign_weekends', 'Assign to existing list'),
                                                 ('delete_all_existing_list', 'Delete the existing list'),
                                                 ('delete_all_existing_list_and_assign_weekends', 'Delete existing and assign'),
                                                 ], string='Action performed', default='delete_all_existing_list_and_assign_weekends',
                                                )
    holiday_type = fields.Selection([('rh', 'RH'),
                                      ('gh', 'GH'),('week_off', 'Week Off')], string='Holiday Type',
                                     )
    is_default_shift = fields.Boolean(string="Default Shift?",help="Default shift assignment for new created employees.")
    # @api.onchange('name','date')
    # def check_unquie_holiday(self):
    #     for rec in self:
    #         count = 0
    #         emp_id = self.env['resource.calendar.leaves'].search(
    #             [('date', '=', a.date),('name', '=', a.name), ('calendar_id', '=', rec.calendar_id.id)])
    #         for e in emp_id:
    #             count += 1
    #         if count > 1:
    #             raise ValidationError("Holiday must be unique")
    #
    #         for dup in rec.global_leave_ids:
    #             if dup.date
    @api.constrains('is_default_shift')
    def validate_default_shift(self):
        for shift in self:
            if shift.is_default_shift:
                duplicate_sift = self.search([('is_default_shift','=',True)]) - shift
                if duplicate_sift:
                    raise ValidationError("Only one shift can be default shift.")

    
    def check_unique_aholidays(self):
        for rec in self:
            for line in rec.global_leave_ids:
                for inter in rec.global_leave_ids:
                    if (line.date == inter.date) and (line.id != inter.id) and (line.name == inter.name) and (line.calendar_id == inter.calendar_id):
                        inter.sudo().unlink()



    
    def assign_weekends(self):
        for rec in self:
            if not (rec.from_date and rec.to_date and rec.week_list):
                raise ValidationError(
                    _("Please enter all the required fields, from date, to date and Weekday"))
            else:
                excluded = [int(rec.week_list)]
                global_leave_ids = []
                if int(rec.week_list) == 1:
                    week_day = 'Monday'
                elif int(rec.week_list) == 2:
                    week_day = 'Tuesday'
                elif int(rec.week_list) == 3:
                    week_day = 'Wednesday'
                elif int(rec.week_list) == 4:
                    week_day = 'Thursday'
                elif int(rec.week_list) == 5:
                    week_day = 'Friday'
                elif int(rec.week_list) == 6:
                    week_day = 'Saturday'
                elif int(rec.week_list) == 7:
                    week_day = 'Sunday'
                else:
                    week_day = ''
                a = time()
                b = time(23, 56, 56)
                fdate = rec.from_date
                while fdate <= rec.to_date:
                    if fdate.isoweekday() in excluded:
                        entered_date = datetime.strptime(str(fdate), '%Y-%m-%d')
                        date_from = entered_date - timedelta(hours=5, minutes=30, seconds=00)
                        date_to = entered_date + timedelta(hours=18, minutes=28, seconds=58)
                        global_leave_ids.append((0, 0, {
                            'calendar_id': rec.id,
                            'name': week_day,
                            'date': fdate,
                            'date_from': date_from,
                            'date_to': date_to,
                            'holiday_type':rec.holiday_type,
                        }))
                    fdate += relativedelta(days=1)
                rec.global_leave_ids = a = global_leave_ids
            # rec.sudo().check_unique_aholidays()

            # for line in rec.global_leave_ids:
            #     for inter in rec.global_leave_ids:
            #         if (line.date == inter.date) and (line.id != inter.id):
            #             inter.sudo().unlink()
            #

    
    def perform_ah_action(self):
        for rec in self:
            if rec.assign_holiday_action_perform == 'assign_weekends':
                rec.assign_weekends()
            elif rec.assign_holiday_action_perform == 'delete_all_existing_list':
                rec.delete_all_existing_list()
            elif rec.assign_holiday_action_perform == 'delete_all_existing_list_and_assign_weekends':
                rec.delete_all_existing_list_and_assign_weekends()
            else:
                pass



    
    def delete_all_existing_list(self):
        for rec in self:
            rec.global_leave_ids.unlink()

    
    def delete_all_existing_list_and_assign_weekends(self):
        for rec in self:
            rec.global_leave_ids.unlink()
            if not (rec.from_date and rec.to_date and rec.week_list):
                raise ValidationError(
                    _("Please enter all the required fields, from date, to date and Weekday"))
            else:
                excluded = [int(rec.week_list)]
                global_leave_ids = []
                if int(rec.week_list) == 1:
                    week_day = 'Monday'
                elif int(rec.week_list) == 2:
                    week_day = 'Tuesday'
                elif int(rec.week_list) == 3:
                    week_day = 'Wednesday'
                elif int(rec.week_list) == 4:
                    week_day = 'Thursday'
                elif int(rec.week_list) == 5:
                    week_day = 'Friday'
                elif int(rec.week_list) == 6:
                    week_day = 'Saturday'
                elif int(rec.week_list) == 7:
                    week_day = 'Sunday'
                else:
                    week_day = ''
                a = time()
                b = time(23, 56, 56)
                fdate = rec.from_date
                while fdate <= rec.to_date:
                    if fdate.isoweekday() in excluded:
                        entered_date = datetime.strptime(str(fdate), '%Y-%m-%d')
                        date_from = datetime.combine(entered_date, time.min)
                        date_to = datetime.combine(entered_date, time(23, 59, 59))
                        global_leave_ids.append((0, 0, {
                            'calendar_id': rec.id,
                            'name': week_day,
                            'date': fdate,
                            'date_from': date_from,
                            'date_to': date_to,
                            'holiday_type':rec.holiday_type,
                        }))
                    fdate += relativedelta(days=1)
                rec.global_leave_ids = a = global_leave_ids


    
    def allow_public_holiday_on_caledar(self):
        for resource in self:
            employee_ids = self.env['hr.employee'].search([('branch_id','=',resource.branch_id.id)])
            for employee in employee_ids:
                employee.resource_calendar_id = self.id
                
                
class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'
    _description= ' Resource Calendar Leaves'
    
    date = fields.Date(string="Date",required=True)
    holiday_type = fields.Selection([('rh', 'RH'),
                                      ('gh', 'GH'),('week_off', 'Week Off')], string='Holiday Type',
                                     )
    restricted_holiday = fields.Boolean(string='Restricted Holiday')
    gestured_holiday = fields.Boolean(string='Gestured Holiday')
    rh_leave_type=fields.Many2one('hr.leave.type', string='RH Leave Type')

    @api.onchange('holiday_type')
    @api.constrains('holiday_type')
    def onchange_h_type(self):
        for rec in self:
            if rec.holiday_type == 'rh':
                rec.restricted_holiday = True
                rec.gestured_holiday = False
            elif rec.holiday_type == 'gh':
                rec.restricted_holiday = False
                rec.gestured_holiday = True
            else:
                rec.restricted_holiday = False
                rec.gestured_holiday = False



    @api.onchange('date')
    def onchange_date(self):
        a = time()
        b = time(23, 56, 56)
        for line in self:
            if line.date:
                entered_date = datetime.strptime(str(line.date), '%Y-%m-%d')
#                 print("??????????????????????",entered_date)
                line.date_from = entered_date - timedelta(hours=5,minutes=30,seconds=00)
                line.date_to = entered_date + timedelta(hours=18,minutes=28,seconds=58)

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

        branch_id = branch_id or self.env.user.branch_id.id
        shift_id = shift_id or self.env.user.employee_ids.resource_calendar_id.id
        employee_id = employee_id or self.env.user.employee_ids.id

        calendar,rh_list,gh_list,week_off_list, shift_leaves = [],[],[],[], self.env['resource.calendar.leaves']
        if personal_calendar == 1:
            if employee_id:
                calendar, shift_leaves = self.get_personalized_calendar(employee_id, cal_start, cal_end)
        else:
            shift_master_record = self.env['resource.calendar'].browse(shift_id)
            shift_leaves = shift_master_record.global_leave_ids

        for record in shift_leaves:
            # exist_shift_holiday = shift_leaves.filtered(lambda r: r.date_from == record.date_from)

            # prime_color = '#00A09D' if record.holiday_type == 'rh' else '#d83d2b' if record.holiday_type== 'gh' else '#F5BB00'
            # bg_color = '#00A09D' if record.holiday_type == 'rh' else '#d83d2b' if record.holiday_type== 'gh' else '#F5BB00'
            if record.holiday_type == 'rh':
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
                    'priority': 1
                })
            elif record.holiday_type == 'gh':
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
                    'priority': 2
                })
            elif record.holiday_type == 'week_off':
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
                    'priority':3
                })
            calendar = rh_list + gh_list + week_off_list
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
            calendar = []
            shift_leaves = emplyee_shift.global_leave_ids.filtered(lambda r: cal_start_date <= r.date_to.date() <= cal_end_date)
            return [calendar, shift_leaves]

