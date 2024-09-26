from odoo import tools
from odoo import models, fields, api
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import DAY_STATUS_WORKING,DAY_STATUS_RWORKING


class DailyTimesheetReport(models.Model):
    _name           = "kw_daily_timesheets_report"
    _description    = "Daily Timesheet Report"
    _auto           = False
    _rec_name       = 'employee_id'

    employee_id             = fields.Many2one(string='Employee',comodel_name='hr.employee',)
    parent_id               = fields.Char(string='Reporting Authority')
    date                    = fields.Date("Date") 
    month_number            = fields.Integer(string="Month Index")
    department_id           = fields.Many2one(string='Department',comodel_name='hr.department') 
    branch_id               = fields.Many2one('kw_res_branch', string="Branch/SBU")
    job_id                  = fields.Many2one('hr.job',string="Designation",related="employee_id.job_id")
    division                = fields.Many2one('hr.department',string="Division",related="employee_id.division")

    num_timesheet_effort    = fields.Float("Actual Effort")
    num_required_effort     = fields.Float("Required Effort")
    num_total_effort        = fields.Float("Extra/Deficit Effort")

    working_days            = fields.Integer(string="Working Days")

    on_leave_state          = fields.Float(string="On Leave")
    on_tour_state           = fields.Integer(string="On Tour")
    absent_state            = fields.Float(string='Absent',)

    str_timesheet_effort    = fields.Char(string="Actual Effort (HH:MM)",help="Calculated from timesheet.")
    str_required_effort     = fields.Char(string="Required Effort (HH:MM)",help="Data extracted from attendance.")
    str_total_effort        = fields.Char(string="Extra/Deficit Effort (HH:MM)",help="Data i.e Required Effort - Actual Effort") 

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f"""CREATE or REPLACE VIEW {self._table} AS (
            SELECT row_number() over() AS id,
            a.employee_id,
            (SELECT name  FROM hr_employee o WHERE  o.id=e.parent_id) AS parent_id,
            attendance_recorded_date AS date,
            CAST(to_char(date_trunc('month', attendance_recorded_date), 'MM') AS INT) AS month_number,  
            a.department_id,
            a.branch_id,
            coalesce(timesheet_effort,0) AS num_timesheet_effort,
            case    when day_status in ('0','3') AND is_cross_shift=False then shift_out_time - shift_in_time - shift_rest_time  
                    when day_status in ('0','3') AND is_cross_shift=True then shift_in_time - shift_out_time - shift_rest_time else 0 
                    end AS num_required_effort,
            coalesce(timesheet_effort,0) - case 
                when day_status in ('0','3') AND is_cross_shift=False then shift_out_time - shift_in_time - shift_rest_time  
                when day_status in ('0','3') AND is_cross_shift=True then shift_in_time - shift_out_time - shift_rest_time else 0 
            end AS num_total_effort,
            case when day_status in ('0','3') then 1 else 0 end AS working_days,
            leave_day_value AS on_leave_state,
            case when is_on_tour = True then 1 else 0 end AS on_tour_state,
            case 
                when is_valid_working_day = True AND payroll_day_value = 0 AND day_status in ('0','3') then 1
                when is_valid_working_day = True AND payroll_day_value = 0.5 AND day_status in ('0','3') then 0.5 
                else 0 
            end AS absent_state,
            coalesce(Cast(TO_CHAR((timesheet_effort || 'hour')::interval, 'HH24:MI') AS varchar), '00:00') AS str_timesheet_effort,
            coalesce(Cast(TO_CHAR(((case 
                when day_status in ('0','3') AND is_cross_shift=False then shift_out_time - shift_in_time - shift_rest_time  
                when day_status in ('0','3') AND is_cross_shift=True then shift_in_time - shift_out_time - shift_rest_time else 0 end) || 'hour')::interval, 'HH24:MI') AS varchar), '00:00') AS str_required_effort,
            coalesce(Cast(TO_CHAR(((coalesce(abs(timesheet_effort),0)) - (case 
                when day_status in ('0','3') AND is_cross_shift=False then shift_out_time - shift_in_time - shift_rest_time 
                when day_status in ('0','3') AND is_cross_shift=True then shift_in_time - shift_out_time - shift_rest_time else 0 end)  || 'hour')::interval, 'HH24:MI') AS varchar), '00:00') AS str_total_effort
            FROM kw_daily_employee_attendance a
            LEFT JOIN hr_employee e ON e.id = a.employee_id
            LEFT JOIN (
                SELECT employee_id, date, sum(unit_amount) AS timesheet_effort,active
                FROM account_analytic_line  
                GROUP BY employee_id, date,active
            ) t ON t.employee_id=a.employee_id AND t.date=a.attendance_recorded_date and t.active=True)
            """
        self.env.cr.execute(query)
