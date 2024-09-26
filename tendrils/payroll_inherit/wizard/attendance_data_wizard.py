import string
from odoo import fields, models, api
import json
import requests
# from datetime import datetime, date
from dateutil import relativedelta

import calendar
import datetime
from math import ceil, floor


class AttendanceData(models.TransientModel):
    _name = "attendance_data"
    _description = "get attendance data from v5"

    employee_id = fields.Many2one('hr.employee', string="User Id")
    year = fields.Selection([('2020', '2020'),
                             ('2021', '2021'),
                             ('2022', '2022'),
                             ('2023', '2023'),
                             ('2024', '2024'),
                             ('2025', '2025')], string="Year", required=True)
    month = fields.Selection([('1', 'January'),
                              ('2', 'February'),
                              ('3', 'March'),
                              ('4', 'April'),
                              ('5', 'May'),
                              ('6', 'June'),
                              ('7', 'July'),
                              ('8', 'August'),
                              ('9', 'September'),
                              ('10', 'October'),
                              ('11', 'November'),
                              ('12', 'December')], string="Month", Required=True)
    page_no = fields.Integer(string="Page No")
    page_size = fields.Integer(string="Page Size")

    def get_data(self):
        # Fetch the url
        parameter_url = self.env['ir.config_parameter'].sudo().get_param('kwantify_attendance_data_url')
        # print(".......................", parameter_url)
        if parameter_url:
            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}

            user_id = self.employee_id.kw_id if self.employee_id else 0
            year = int(self.year) if self.year else 0
            month = int(self.month) if self.month else 0

            # parameters for url
            payroll_data_dict = {
                "UserID": user_id,
                "Year": year,
                "Month": month,
                "PageNo": self.page_no,
                "PageSize": self.page_size,
            }
            resp = requests.post(parameter_url, headers=header, data=json.dumps(payroll_data_dict))
            j_data = json.dumps(resp.json())
            json_record = json.loads(j_data)
            attendance_data = self.env['kw_payroll_monthly_attendance_report'].sudo().search([('attendance_year','=',year),('attendance_month','=',month)])
            if json_record:
                query = ""
                record_lst = list(map(lambda x : x['UserID'],json_record))
                # print(record_lst)
                employee_id = self.env['hr.employee'].sudo().search([('kw_id', 'in', record_lst)])
                for rec in json_record:
                    filtered_attendance = attendance_data.filtered(lambda x : x.employee_id.kw_id == int(rec['UserID']))
                    fil_employee_id = employee_id.filtered(lambda x : x.kw_id == int(rec['UserID']))
                    if fil_employee_id:
                        if filtered_attendance:
                            # update the attendance record
                            query += f"update kw_payroll_monthly_attendance_report set kw_payable_days={rec['PayDays']} where id = {filtered_attendance.id};"

                        # else:

                        #     query += f"insert into kw_payroll_monthly_attendance_report (attendance_year,attendance_month,employee_id,num_absent_days,num_leave_days,actual_working,num_tour_days,num_shift_working_days,emp_status) values({rec['Year']},{rec['Month']},{employee_id.id},{rec['Absent']},{rec['Leave']},{rec['PayDays']},{rec['Tour']},{rec['WorkingDay']},{rec['Status']});"


                if len(query) > 0:
                    self._cr.execute(query)

            self.env['kw_attendance_log'].sudo().create(
                    {'request_params': payroll_data_dict, 'response_result': json_record})




