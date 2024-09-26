# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import IN_STATUS_LE, IN_STATUS_EXTRA_LE, \
    IN_STATUS_LE_HALF_DAY, IN_STATUS_LE_FULL_DAY, DAY_STATUS_WORKING, DAY_STATUS_RWORKING, LATE_WPC, LATE_WOPC, \
    ATD_STATUS_PRESENT, ATD_STATUS_FHALF_ABSENT, ATD_STATUS_SHALF_ABSENT, DAY_STATUS_WEEKOFF, DAY_STATUS_RHOLIDAY, \
    DAY_STATUS_HOLIDAY, EMP_STS_NORMAL, EMP_STS_NEW_JOINEE, EMP_STS_EXEMP
from calendar import monthrange, month_abbr
import datetime
from datetime import datetime, date


class EmployeeMonthlyAttendanceReport(models.Model):
    _name = "kw_attendance_monthly_report"
    _description = "Employee Monthly Attendance Report"
    _auto = False
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee', )
    name = fields.Char(string='Name')
    emp_code = fields.Char(string='Emp Code')
    designation = fields.Char(string='Designation')
    job_id = fields.Many2one('hr.job', string="Designation")
    attendance_date = fields.Date(string="Attendance Date")
    check_in = fields.Char(string='Check In')
    check_out = fields.Char(string='Check Out')
    worked_hours = fields.Float(string='Worked Hours')
    day_status = fields.Char(string='Day Status')
    ws_branch_unit_id = fields.Many2one('kw_res_branch_unit', string='WS Unit')
    month_date = fields.Integer(string='Month')
    year_date = fields.Integer(string='Year')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # AND ws.ws_branch_unit_id=3
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            with ws AS (SELECT ws.name AS ws_name,
                ws.branch_id AS ws_branch_id,
                ws.branch_unit_id AS ws_branch_unit_id,
                ws.infrastructure AS infrastructure,
                ws.workstation_type AS ws_workstation_type,
                ws_rel.eid AS emp_id
                FROM kw_workstation_master AS ws
                JOIN kw_workstation_hr_employee_rel AS ws_rel ON ws.id=ws_rel.wid)

                SELECT row_number() over(ORDER BY emp.name ASC, da.attendance_recorded_date ASC) as id, 
                emp.id AS employee_id, emp.name, emp.emp_code, emp.job_id,
                (select name from hr_job where id=emp.job_id) as designation,
                da.attendance_recorded_date AS attendance_date, 
                CASE WHEN check_in is not null THEN
                    CONCAT(LPAD(DATE_PART('hour',da.check_in + interval '5.5 hour')::text, 2, '0'),':',LPAD(DATE_PART('minute',da.check_in + interval '5.5 hour')::text, 2, '0'))
                ELSE '' END AS check_in, 
                CASE WHEN check_out is not null THEN
                    concat(LPAD(DATE_PART('hour',da.check_out + interval '5.5 hour')::text, 2, '0'),':',LPAD(DATE_PART('minute',da.check_out + interval '5.5 hour')::text, 2, '0')) 
                ELSE '' END AS check_out,
                da.worked_hours, 
                CASE WHEN da.payroll_day_value = 0 THEN 'Absent'
                WHEN da.day_status in ('{DAY_STATUS_RHOLIDAY}','{DAY_STATUS_WEEKOFF}') THEN 'Week Off'
                WHEN da.day_status in ('{DAY_STATUS_HOLIDAY}') THEN 'Holiday'
                WHEN da.is_on_tour is not null AND da.is_on_tour is true THEN 'On Tour'
                WHEN da.leave_status is not null THEN 'On Leave'
                WHEN da.day_status not in ('{DAY_STATUS_RHOLIDAY}','{DAY_STATUS_WEEKOFF}','{DAY_STATUS_HOLIDAY}') 
                    AND da.check_in is not null THEN 'Present'
                END AS day_status,
                ws.ws_branch_unit_id,
                DATE_PART('month', da.attendance_recorded_date) AS month_date,
                DATE_PART('year', da.attendance_recorded_date) AS year_date
                FROM hr_employee AS emp
                LEFT JOIN kw_daily_employee_attendance AS da ON da.employee_id=emp.id
                LEFT JOIN ws ON emp.id=ws.emp_id
                WHERE emp.employement_type!=5 
                ORDER BY emp.name, da.attendance_recorded_date
               
            )""" % (
            self._table))
        # DATE_PART('month', da.attendance_recorded_date) = 1
        # AND DATE_PART('year', da.attendance_recorded_date) = 2021
        # AND

    @api.model
    def get_employee_data(self, **kwargs):
        month = kwargs.get('month', False)
        year = kwargs.get('year', False)
        data = self.env['kw_attendance_monthly_report'].search(
            [('month_date', '=', month), ('year_date', '=', year)])
        # print("data >>> ",  kwargs, data)

        response = {}

        days_in_month = monthrange(year, month)[1]
        month_name_abbr = month_abbr[month]
        # print("days_in_month >>> ",  days_in_month, month_name_abbr)
        headers = {"row1": [{"string": "Name", "style": ["rowspan", 2], "class": "text-left wordbreak align-middle"},
                            {"string": "Code", "style": ["rowspan", 2], "class": "text-left wordbreak align-middle"},
                            {"string": "Designation", "style": ["rowspan", 2], "class": "text-left wordbreak align-middle"}],
                   "row2": [{"string": "Check In"}, {"string": "Check Out"}, {"string": "Worked Hours"}, {"string": "Day Status"}],
                   "days_in_month": days_in_month, "day_range": [str(x) for x in range(0, days_in_month)]}
        for i in range(1, days_in_month+1):
            headers['row1'].append({"string": f"{str(i).zfill(2)}-{month_name_abbr}-{year}",
                                    "style": ["colspan", 4],
                                    "class": "text-center wordbreak align-middle"})
        # print("headers >>> ", headers)
        response.update({'headers': headers})

        records = {}
        prev = ''
        temp = []
        temp_records = {}
        for rec in data:
            # print(rec.name, rec.attendance_date, " ---------------- ")
            if rec.name != prev:
                temp.append(rec.name)
                temp.append(rec.emp_code)
                temp.append(rec.designation)
                prev = rec.name
                records.update({rec.emp_code: temp})
                temp = []
            attendance_date = rec.attendance_date.strftime('%Y-%m-%d')
            if attendance_date in temp_records:
                temp_records[attendance_date].update({rec.emp_code: rec})
            else:
                temp_records.update({attendance_date: {rec.emp_code: rec}})
        # print("temp_records >>>> ", temp_records)
        for i in range(1, days_in_month + 1):  # month loop
            temp = []
            dt = datetime.strptime(f"{i}-{month}-{year}", '%d-%m-%Y').strftime('%Y-%m-%d')
            for x in records:  # employee loop
                temp = []
                # print('rec.attendance_date >> ', rec.attendance_date, dt, ' ----------------- ')
                # print('rec.name, rec.emp_code >>>>>>>>>>>>>> ', rec.name, rec.emp_code)
                # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>",x, dt, temp_records.keys())
                if dt in temp_records.keys() and x in temp_records[dt].keys():
                    rec = temp_records[dt][x]
                    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>",rec)
                    records[rec.emp_code] += [rec.check_in, rec.check_out, rec.worked_hours, rec.day_status]
                else:
                    records[x] += ['', '', '', '']

        # for rec in data:
        #     # print(rec.name, rec.attendance_date, " ---------------- ")
        #     if rec.name != prev:
        #         records.append(temp)
        #         temp = []
        #         temp.append(rec.name)
        #         temp.append(rec.emp_code)
        #         temp.append(rec.designation)
        #         temp.append(rec.check_in)
        #         temp.append(rec.check_out)
        #         temp.append(rec.worked_hours)
        #         temp.append(rec.day_status)
        #         prev = rec.name
        #         # records.append(temp)
        #     else:
        #         temp.append(rec.check_in)
        #         temp.append(rec.check_out)
        #         temp.append(rec.worked_hours)
        #         temp.append(rec.day_status)

        # print("records >>> ", records)
        final_records = [records[x] for x in records]
        # print("final_records >>> ", final_records)
        response.update({'records': final_records})
        return response
