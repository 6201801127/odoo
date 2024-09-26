from datetime import timedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import IN_STATUS_LE_HALF_DAY, DAY_STATUS_WORKING, DAY_STATUS_RWORKING, \
    ATD_STATUS_ABSENT, ATD_STATUS_SHALF_ABSENT, EMP_STS_NORMAL, EMP_STS_NEW_JOINEE, EMP_STS_EXEMP

class AttendanceMode(models.TransientModel):
    _name = 'kw_daily_attendance_create'
    _description = 'Attendance Create Wizard For Date'

    date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    @api.multi
    def create_attendance_by_date(self):
        attendance_from_date = self.date
        attendance_to_date = self.to_date
        if attendance_to_date < attendance_from_date:
            raise ValidationError("To date can't be less than from date.")

        daily_attendance = self.env['kw_daily_employee_attendance']
        hr_wizard = self.env['kw_manual_attendance_hr_wizard']

        for day in range(int((attendance_to_date - attendance_from_date).days) + 1):
            attendance_date = attendance_from_date + timedelta(day)
            
            all_employees = self.env['hr.employee'].search([('date_of_joining', '<=', attendance_date)])
            not_created_employees = all_employees - daily_attendance.search([('attendance_recorded_date', '=', attendance_date),\
                                                                        ('employee_id', 'in', all_employees.ids)]).mapped('employee_id')
            # print("not created employees are---->",not_created_employees)
            for employee in not_created_employees:
                # if there is no attendance record and date of joining present and the date is greater than equal to DOJ
                try:
                    # create attendance with a new db cursor
                    hr_wizard.create_attendance_with_new_cr(employee, attendance_date)
                except Exception as e:
                    continue
                    # raise ValidationError(str(e))
        self.env.user.notify_success("Attendance(s) Created Successfully.")
    
    @api.multi
    def update_attendance_by_date(self):
        daily_attendance = self.env['kw_daily_employee_attendance']
        attendance_date = self.date
        attendance_to_date = self.to_date
        if attendance_to_date < attendance_date:
            raise ValidationError("To date can't be less than from date.")
        employee_attendance_data = daily_attendance.search([('attendance_recorded_date', '>=', attendance_date),('attendance_recorded_date', '<=', attendance_to_date)])

        for emp_attendance_rec in employee_attendance_data:

            employee_status = False
            try:
                if emp_attendance_rec.employee_id.date_of_joining and (emp_attendance_rec.attendance_recorded_date == emp_attendance_rec.employee_id.date_of_joining):
                    employee_status = EMP_STS_NEW_JOINEE

                if not emp_attendance_rec.employee_id.active and emp_attendance_rec.employee_id.last_working_day and emp_attendance_rec.attendance_recorded_date == emp_attendance_rec.employee_id.last_working_day:
                    employee_status = EMP_STS_EXEMP

                if not employee_status and emp_attendance_rec.attendance_recorded_date > emp_attendance_rec.employee_id.date_of_joining:
                    employee_status = EMP_STS_NORMAL

                if not emp_attendance_rec.employee_id.active and emp_attendance_rec.employee_id.last_working_day and emp_attendance_rec.attendance_recorded_date > emp_attendance_rec.employee_id.last_working_day:
                    employee_status = False

            except Exception:# as e
                continue
            shift_info = []

            try:
                shift_info = daily_attendance._compute_day_status(emp_attendance_rec.employee_id,emp_attendance_rec.attendance_recorded_date)
                if shift_info :
                    emp_shift_id = shift_info[2].id if shift_info[2] else False
                    shift_second_half_time = shift_info[5] if shift_info[5] else 0
                    emp_shift_name = shift_info[6] if shift_info[6] else shift_info[2].name
                    attendance_status = emp_attendance_rec.state
                    work_mode = daily_attendance.get_employee_work_mode(emp_attendance_rec.employee_id.id, emp_attendance_rec.attendance_recorded_date)
                    if (shift_info[0] in [DAY_STATUS_WORKING, DAY_STATUS_RWORKING]) and (emp_attendance_rec.check_in and not emp_attendance_rec.check_out):
                        attendance_status = ATD_STATUS_SHALF_ABSENT

                        if emp_attendance_rec.check_in_status in [IN_STATUS_LE_HALF_DAY]:
                            attendance_status = ATD_STATUS_ABSENT

                    if emp_attendance_rec.work_mode != work_mode or emp_attendance_rec.day_status != shift_info[0] \
                            or emp_attendance_rec.shift_id.id != emp_shift_id or emp_attendance_rec.shift_name != emp_shift_name \
                            or emp_attendance_rec.shift_rest_time != shift_info[1] or emp_attendance_rec.shift_in_time != shift_info[3] \
                            or emp_attendance_rec.shift_out_time != shift_info[4] or emp_attendance_rec.shift_second_half_time != shift_second_half_time \
                            or emp_attendance_rec.employee_status != employee_status or emp_attendance_rec.state != attendance_status:
                        emp_attendance_rec.write({'day_status': shift_info[0],
                                                  'shift_id': emp_shift_id,
                                                  'shift_name': emp_shift_name,
                                                  'work_mode': work_mode,
                                                  'shift_rest_time': shift_info[1],
                                                  'shift_in_time': shift_info[3],
                                                  'shift_out_time': shift_info[4],
                                                  'shift_second_half_time': shift_second_half_time,
                                                  'employee_status': employee_status})
            except Exception:# as e
                continue
        self.env.user.notify_success("Attendance(s) Updated Successfully.")