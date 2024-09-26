# -*- coding: utf-8 -*-
# from calendar import monthrange
from datetime import date
from odoo import tools
from odoo import models, fields, api
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import ATD_STATUS_PRESENT, ATD_STATUS_ABSENT, \
    ATD_STATUS_FHALF_ABSENT, ATD_STATUS_SHALF_ABSENT, DAY_STATUS_WORKING, DAY_STATUS_RWORKING, IN_STATUS_EARLY_ENTRY, \
    IN_STATUS_ON_TIME, ATD_STATUS_TOUR, ATD_STATUS_LEAVE, ATD_STATUS_FHALF_LEAVE, ATD_STATUS_SHALF_LEAVE


class EmployeeAttendanceSummary(models.Model):
    _name = "kw_employee_attendance_summary_report"
    _description = "Employee Attendance Summary Report"
    _auto = False
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee', )
    branch_id = fields.Many2one('kw_res_branch', string="Branch/SBU", )
    department_id = fields.Many2one(string='Department', comodel_name='hr.department')
    attendance_year = fields.Integer(string="Attendance Year", )
    month_number = fields.Date(string="Attendance Month")
    attendance_month = fields.Char(string="Attendance Month Name", compute="_compute_month_name")
    month_index = fields.Integer(string="Attendance Month Index")
    # month_number                = fields.Char(string="Month Index")    
    working_days = fields.Integer(string="Working Days")
    present_state = fields.Float(string='Present', )
    absent_state = fields.Float(string='Absent', )
    on_leave_state = fields.Float(string="On Leave")
    on_tour_state = fields.Integer(string="On Tour")
    normal_entry_state = fields.Integer(string='Normal Entry', )
    lwpc_state = fields.Integer(string='With Pay Cut', )
    lwopc_state = fields.Integer(string='With out Pay Cut', )
    reporting_authority = fields.Many2one(string='Reporting Authority', comodel_name='hr.employee',
                                          related="employee_id.parent_id")

    monthly_attendance_child_ids = fields.Many2many('kw_daily_employee_attendance',
                                                    string="Monthly Attendance Child Ids",
                                                    compute="get_no_of_monthly_attendance_days")
    present_child_ids = fields.Many2many('kw_daily_employee_attendance', string="Present Child Ids",
                                         compute="get_no_of_monthly_attendance_days")
    absent_child_ids = fields.Many2many('kw_daily_employee_attendance', string="Absent Child Ids",
                                        compute="get_no_of_monthly_attendance_days")
    on_leave_child_ids = fields.Many2many('kw_daily_employee_attendance', string="On Leave Child Ids",
                                          compute="get_no_of_monthly_attendance_days")
    on_tour_child_ids = fields.Many2many('kw_daily_employee_attendance', string="On Tour Child Ids",
                                         compute="get_no_of_monthly_attendance_days")

    @api.multi
    def _compute_month_name(self):
        for rec in self:
            rec.attendance_month = rec.month_number.strftime('%B')

    @api.multi
    def get_no_of_monthly_attendance_days(self):
        for rec in self:
            month_index = rec.month_number.strftime('%m')
            # print(rec.month_number,month_index)
            start_date, end_date = self.env['kw_late_attendance_summary_report']._get_month_range(rec.attendance_year, month_index)
            daily_attendance_records = self.env['kw_daily_employee_attendance'].search(
                [('employee_id', '=', rec.employee_id.id), ('attendance_recorded_date', '>=', start_date),
                 ('attendance_recorded_date', '<=', end_date),
                 ('day_status', 'in', [DAY_STATUS_WORKING, DAY_STATUS_RWORKING])],
                order="attendance_recorded_date asc", )

            rec.monthly_attendance_child_ids = daily_attendance_records.ids

            present_child_ids = daily_attendance_records.filtered(lambda rec: rec.state in [ATD_STATUS_PRESENT, ATD_STATUS_FHALF_ABSENT, ATD_STATUS_SHALF_ABSENT] and rec.is_valid_working_day == True)
            rec.present_child_ids = present_child_ids.ids

            absent_child_ids = daily_attendance_records.filtered(lambda rec: rec.payroll_day_value == 0 and rec.is_valid_working_day == True)
            rec.absent_child_ids = absent_child_ids.ids

            on_leave_child_ids = daily_attendance_records.filtered(lambda rec: rec.leave_day_value > 0)
            rec.on_leave_child_ids = on_leave_child_ids.ids

            on_tour_child_ids = daily_attendance_records.filtered(lambda rec: rec.is_on_tour == True)
            rec.on_tour_child_ids = on_tour_child_ids.ids

    #         rec.on_tour_child_ids = daily_attendance_records.ids   ::timestamp::date

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
           SELECT 
            CAST(concat(employee_id,to_char(date_trunc('month', attendance_recorded_date), 'MM'),substring(CAST(extract(year from attendance_recorded_date) as text), 3, 2)) AS BIGINT) AS id,                 	
            employee_id,                
            date_trunc('month', attendance_recorded_date) ::timestamp without time zone::date AS month_number, 
            extract(year from attendance_recorded_date)  AS attendance_year,                
            CAST(to_char(date_trunc('month', attendance_recorded_date), 'MM') AS INT) AS month_index,    
            department_id, 
            branch_id,           
            sum(case when is_valid_working_day = True and state in ('{ATD_STATUS_PRESENT}','{ATD_STATUS_FHALF_ABSENT}','{ATD_STATUS_SHALF_ABSENT}')and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then 1 else 0 end) as present_state,
            sum(leave_day_value) as on_leave_state,
            sum(case when is_on_tour = True then 1 else 0 end) as on_tour_state,
            sum(case when day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then 1 else 0 end) as working_days,
            sum(case when is_valid_working_day = True and payroll_day_value = 0 and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then 1  when is_valid_working_day = True and payroll_day_value = 0.5 and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then 0.5 else 0 end) as absent_state,
            sum(case when state in ('{ATD_STATUS_PRESENT}','{ATD_STATUS_FHALF_ABSENT}','{ATD_STATUS_SHALF_ABSENT}') and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') and (check_in_status ='{IN_STATUS_EARLY_ENTRY}' or check_in_status = '{IN_STATUS_ON_TIME}') then 1 else 0 end) as normal_entry_state,
            sum(case when state in ('{ATD_STATUS_PRESENT}','{ATD_STATUS_FHALF_ABSENT}','{ATD_STATUS_SHALF_ABSENT}') and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') and le_action_status ='1' then 1 else 0 end) as lwpc_state,
            sum(case when state in ('{ATD_STATUS_PRESENT}','{ATD_STATUS_FHALF_ABSENT}','{ATD_STATUS_SHALF_ABSENT}') and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') and le_action_status ='2' then 1 else 0 end) as lwopc_state 

            from kw_daily_employee_attendance 
            group by 2,department_id,branch_id, 4, date_trunc('month', attendance_recorded_date)
        )""" % (self._table))  ##ROW_NUMBER () OVER (ORDER BY e.id) as id, CAST(concat(e.id,month_index) AS INT) AS id,
