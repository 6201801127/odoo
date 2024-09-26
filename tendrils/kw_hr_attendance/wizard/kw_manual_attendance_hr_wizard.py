# -*- coding: utf-8 -*-
# Get work mode of employee from WFH module while attendance creation 23-Feb-2021 (Gouranga)
import pytz
from datetime import datetime, timedelta

from odoo.addons.resource.models import resource

import psycopg2
from odoo import api, fields, models, registry, SUPERUSER_ID

from odoo.exceptions import ValidationError
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import DAY_STATUS_WORKING, DAY_STATUS_LEAVE, \
    DAY_STATUS_HOLIDAY, DAY_STATUS_RWORKING, DAY_STATUS_RHOLIDAY, ATD_MODE_MANUAL, ATD_STATUS_ABSENT, EMP_STS_NORMAL, \
    EMP_STS_NEW_JOINEE, EMP_STS_EXEMP


class ManualHrAttendanceWizard(models.TransientModel):
    _name = 'kw_manual_attendance_hr_wizard'
    _description = 'HR Manual Attendance Wizard'
    _rec_name = 'branch_id'

    @api.model
    def default_get(self, fields):
        res = super(ManualHrAttendanceWizard, self).default_get(fields)
        from_date, to_date, _ = self.env['kw_daily_employee_attendance']._get_recompute_date_range_configs(end_date=datetime.today().date())
        res['from_date'], res['to_date'] = from_date, to_date
        return res

    from_date = fields.Date(string="From Date", required=True, autocomplete="off")
    to_date = fields.Date(string="To Date", required=True, autocomplete="off")
    branch_id = fields.Many2one('kw_res_branch', string="Branch/SBU")
    emp_date_ids = fields.Many2many('kw_manual_atd_emp_info', )

    @api.multi
    def generate_attendance(self):
        for record in self:
            if record.from_date and record.to_date:
                # #Start :: create dates for the selected date range
                all_dates = self.env['kw_manual_attendance_dates'].search([])
                date_list = []
                for day in range(int ((record.to_date - record.from_date).days)+1):
                    search_date = record.from_date + timedelta(day)
                    if not all_dates.filtered(lambda rec : rec.name == search_date):
                        date_list.append({'name':search_date})
                if date_list:
                    self.env['kw_manual_attendance_dates'].create(date_list)
                # #End :: create dates for the selected date range

                # #Start :: create employee attendnace for the selected date-range
                attendance_dates = self.env['kw_manual_attendance_dates'].search([('name', '>=', record.from_date), ('name', '<=', record.to_date)])
                emp_date_info = self.env['kw_manual_atd_emp_info'].search([])
                manual_attendance_mode = self.env.ref('kw_hr_attendance.kw_attendance_mode_manual').alias or ATD_MODE_MANUAL

                employee_ids = self.env['hr.employee'].search([('attendance_mode_ids.alias', 'in', [manual_attendance_mode])])  # ('user_id.branch_id', '=', self.branch_id.id),
                record.emp_date_ids = False
                record.emp_date_ids = [
                    (0, 0, {                        
                        'employee_id': employee.id,
                        'attendance_date': rec.id,
                    })
                    # if there isn't a demo line record for the user, create a new one
                    if not emp_date_info.filtered(lambda x: x.employee_id == employee and x.attendance_date==rec) else
                    # otherwise, return the line
                    (4, emp_date_info.filtered(lambda x: x.employee_id == employee and x.attendance_date==rec)[0].id)
                    for rec in attendance_dates
                    for employee in employee_ids
                ]
                # print(record.line_ids)
               
            else:
                raise ValidationError("Please enter all the required fields!\n (1) From Date\n (2) To Date\n ")

    @api.multi        
    def create_manual_attendance(self):
        for rec in self:
            if rec.emp_date_ids:
                for emp_attendance in rec.emp_date_ids:
                    # #Start :: create manual attendance for the selected employee, for each date
                    joining_date = emp_attendance.employee_id.date_of_joining
                    exit_date = emp_attendance.employee_id.last_working_day if emp_attendance.employee_id.last_working_day else rec.to_date
                    if joining_date <= emp_attendance.attendance_date.name <= exit_date:
                        if emp_attendance.employee_id.resource_calendar_id:
                            remark = f"Manual Attendance Update of employees having manual attendance mode\n(Updated by {self.env.user.name}, on {datetime.now()})."
                            self.create_employee_manual_attendance(emp_attendance.employee_id,
                                                                emp_attendance.attendance_date.name,
                                                                emp_attendance.present_status, remark=remark)
                    else:
                        raise ValidationError(f'There is no shift assigned for "{emp_attendance.employee_id.name}". \n Please assign shift to the employee(s) before proceeding for manual attendance')
                    
            else:               
                raise ValidationError("Please enter all the required fields!")

        self.env.user.notify_success(message='Manual attendance updated for the selected employees successfully.')
        # return new_record

        return {'type': 'ir.actions.act_window_close'}

    # #method to create employee manual attendance ## enter record except the holidays.
    def create_employee_manual_attendance(self, employee, attendance_date, present_status=True, remark=False):
        daily_emp_attendance = self.env['kw_daily_employee_attendance']
        shift_info = daily_emp_attendance._compute_day_status(employee, attendance_date)

        # day_status,shift_rest_time,shift_id,shift_in_time,shift_out_time
        day_status = shift_info[0]
        emp_shift = shift_info[2]  # ofc_hours.mapped('calendar_id')[0]

        shift_in_time = shift_info[3]
        shift_out_time = shift_info[4]
        shift_second_half_time = shift_info[5] if shift_info[5] else 0
        emp_tz = employee.tz or emp_shift.tz or 'UTC'

        shift_name = shift_info[6]

        if day_status in [DAY_STATUS_WORKING,DAY_STATUS_RWORKING] and present_status:
            check_in_datetime = datetime.combine(attendance_date, resource.float_to_time(shift_in_time))
            check_out_datetime = datetime.combine(attendance_date if not emp_shift.cross_shift else attendance_date + timedelta(1), resource.float_to_time(shift_out_time))
            # print("----------------------------------------")
            # print(shift_in_time)
            in_datetime_emp_tz = pytz.timezone(emp_tz).localize(check_in_datetime)
            out_datetime_emp_tz = pytz.timezone(emp_tz).localize(check_out_datetime)

            # Convert to US/Pacific time zone
            utc_in_datetime = in_datetime_emp_tz.astimezone(pytz.timezone('UTC'))
            utc_out_datetime = out_datetime_emp_tz.astimezone(pytz.timezone('UTC'))

            attendance_data = {'employee_id': employee.id,
                               'shift_id': emp_shift.id if emp_shift else False,
                               'shift_name': shift_name,
                               'is_cross_shift': emp_shift.cross_shift if emp_shift else False,
                               'shift_in_time': shift_in_time,
                               'shift_out_time': shift_out_time,
                               'attendance_recorded_date': attendance_date,
                               'check_in': utc_in_datetime,
                               'check_in_mode': 2,
                               'check_out': utc_out_datetime,
                               'check_out_mode': 2,
                               'tz': emp_tz,
                               'shift_second_half_time': shift_second_half_time}
        else:

            attendance_data = {'employee_id': employee.id,
                               'shift_id': emp_shift.id if emp_shift else False,
                               'shift_name': shift_name,
                               'is_cross_shift': emp_shift.cross_shift if emp_shift else False,
                               'shift_in_time': shift_in_time,
                               'shift_out_time': shift_out_time,
                               'attendance_recorded_date': attendance_date,
                               'check_in': None,
                               'check_out': None,
                               'check_in_mode': 2,
                               'check_out_mode': 2,
                               'tz': emp_tz,
                               'shift_second_half_time': shift_second_half_time}

        day_rec = daily_emp_attendance.search([('employee_id', '=', employee.id), ('attendance_recorded_date', '=', attendance_date)])
        # print(day_rec)
        # body        = ("This record has been updated through manual attendance wizard.<br\> <b>Action Taken By :</b> %s")%(self.env.user.name)

        if day_rec:
            if remark:
                attendance_data['attendance_update_logs'] = day_rec.attendance_update_logs+'###'+remark if day_rec.attendance_update_logs else remark
            day_rec.write(attendance_data)
           
        else:
            # print("Shift nfo --")  
            if remark:
                attendance_data['attendance_update_logs'] = remark          
            daily_emp_attendance.create(attendance_data)   
           
    # #method to insert each day record for every employee/ monthly -- Everyday scheduler

    def auto_attendance_status_update(self, compute_future=False):
        daily_attendance = self.env['kw_daily_employee_attendance']
        all_employees = self.env['hr.employee'].search([('date_of_joining','!=',False)])
        # print("All employees -->",all_employees)

        end_date = datetime.today().date()
        if compute_future:
            _, end_date = self.env['kw_late_attendance_summary_report']._get_month_range(end_date.year, end_date.month)
        # end_date = end_date if not compute_future else month_end_date
        curr_month = end_date.month

        """start date should be previous month 25th day"""
        start_date = end_date.replace(day=25, month=end_date.month - 1) if curr_month > 1 else end_date.replace(day=25,
                                                                                                                month=12,
                                                                                                                year=end_date.year - 1)
        emp_data = []
        new_record_string = ''
        error_log = ''
        monthly_attendance_records = daily_attendance.search([('attendance_recorded_date', '>=', start_date),('attendance_recorded_date', '<=', end_date)])
        # print("Monthly datas are",start_date,end_date,monthly_attendance_records)
        for day in range(int((end_date - start_date).days) + 1):
            attendance_date = start_date + timedelta(day)
            # print(attendance_date) 
            # day_all_employee_rec = daily_attendance.search([('attendance_recorded_date', '=', attendance_date)])
            not_created_employees = all_employees.filtered(lambda r: attendance_date >= r.date_of_joining) - monthly_attendance_records.filtered(lambda r:r.attendance_recorded_date == attendance_date).mapped('employee_id')
            # print("Not emp --->",attendance_date,not_created_employees)
            # for employee in all_employees:
            for employee in not_created_employees:
                # emp_day_rec = day_all_employee_rec.filtered(lambda r: r.employee_id == employee)

                """if there is no attendance record and date of joining present and the date is greater than equal to DOJ"""
                try:
                    """ create a new db cursor"""
                    self.create_attendance_with_new_cr(employee, attendance_date)
                    # if not emp_day_rec and employee.date_of_joining and attendance_date >= employee.date_of_joining:
                    # if attendance_date >= employee.date_of_joining:
                        # print("inside if ..")
                        # """ create a new db cursor"""
                        # self.create_attendance_with_new_cr(employee, attendance_date)
                        # # emp_data.append({'employee_id':employee.id,'shift_id':day_shift.id if day_shift else False,'shift_name':day_shift.name if day_shift else '','is_cross_shift':day_shift.cross_shift if day_shift else False,'shift_in_time':shift_info[4],'shift_out_time':shift_info[5],'attendance_recorded_date':attendance_date,'tz':emp_tz,'state':ATD_STATUS_ABSENT,'shift_second_half_time':shift_info[6] if shift_info[6] else 0,'employee_status':employee_status})

                except Exception as e:
                    error_log += '## Error block ' + str(employee.name) + ' ' + str(attendance_date.strftime('%Y-%m-%d')) + ' ##' + str(e) + '## '
                    continue
                    # pass
        # print(emp_data)
        # if emp_data:
        #     daily_attendance.create(emp_data)

        """insert into log table --"""
        if (new_record_string and new_record_string != '') or (error_log and error_log != ''):
            try:
                self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Daily Attendance Creation',
                                                                       'error_log': error_log,
                                                                       'new_record_log': new_record_string})
            except Exception as e:
                # logging.exception("message")
                pass

    # #function to create attendance using new cursor
    def create_attendance_with_new_cr(self, employee, attendance_date):
        db_name = self._cr.dbname

        # Use a new cursor to avoid rollback that could be caused by an upper method
        try:
            db_registry = registry(db_name)
            with db_registry.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})

                kw_daily_attendance = env['kw_daily_employee_attendance']

                shift_info = kw_daily_attendance._get_employee_shift(employee, attendance_date)
                # ofc_hours               = shift_info[1]  
                emp_tz = employee.tz or employee.resource_calendar_id.tz or 'UTC'
                day_shift = shift_info[3]
                day_shift_name = shift_info[7] if shift_info[7] else day_shift.name
                # get work mode from WFH Module 23-Feb-2021 (Gouranga)
                emp_work_mode = kw_daily_attendance.get_employee_work_mode(employee.id, attendance_date)
                employee_status = EMP_STS_NORMAL
                if attendance_date == employee.date_of_joining:
                    employee_status = EMP_STS_NEW_JOINEE

                kw_daily_attendance.sudo().create({'employee_id': employee.id,
                                                   'shift_id': day_shift.id if day_shift else False,
                                                   'shift_name': day_shift_name,
                                                   'is_cross_shift': day_shift.cross_shift if day_shift else False,
                                                   'shift_in_time': shift_info[4],
                                                   'shift_out_time': shift_info[5],
                                                   'attendance_recorded_date': attendance_date,
                                                   'tz': emp_tz,
                                                   'state': ATD_STATUS_ABSENT,
                                                   'shift_second_half_time': shift_info[6] if shift_info[6] else 0,
                                                   'employee_status': employee_status,
                                                   'work_mode': emp_work_mode})
                # work mode added while attendance creation 23-Feb-2021 (Gouranga)
        except (psycopg2.Error):
            raise        
        except Exception as e:   
            raise


# ###### as per the change request#######

class ManualHrAttendanceEmployeeInfo(models.TransientModel):
    _name = 'kw_manual_atd_emp_info'
    _description = 'HR Manual Attendance Employee Info'
    _order = "attendance_date"

    employee_id = fields.Many2one('hr.employee', string="Employees", required=True)
    attendance_date = fields.Many2one('kw_manual_attendance_dates', string="Date")
    present_status = fields.Boolean(string='Present', default=True)


class ManualAttendanceDates(models.TransientModel):
    _name = 'kw_manual_attendance_dates'
    _description = 'HR Manual Attendance Date Info'
    _order = "name"

    name = fields.Date(string="Date", required=True)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            # record_name = record.name.strftime("%d-%b-%Y")
            result.append((record.id, record.name.strftime("%d-%b-%Y")))
        return result
