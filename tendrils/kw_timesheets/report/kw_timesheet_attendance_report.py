# from calendar import monthrange
# from datetime import date ,datetime
from odoo import tools
from odoo import models, fields, api
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import DAY_STATUS_WORKING,DAY_STATUS_RWORKING

class TimesheetProductiveReport(models.Model):
    _name           = "kw_timesheet_attendance_report"
    _description    = "Timesheet Monthly Productive Hours Summary"
    _auto           = False
    _rec_name       = 'employee_id'

    employee_id                 = fields.Many2one(string='Employee',comodel_name='hr.employee',)
    parent_id                   = fields.Many2one('hr.employee','Reporting Authority') 
    branch_id                   = fields.Many2one('kw_res_branch', string="Branch/SBU")
    job_id                      = fields.Many2one('hr.job',string="Designation",related="employee_id.job_id")
    department_id               = fields.Many2one(string='Department',comodel_name='hr.department') 
    attendance_year             = fields.Integer(string="Year",)
    attendance_month            = fields.Char(string="Month")    
    month_number                = fields.Integer(string="Month Index")
    working_days                = fields.Integer(string="Working Days")

    required_effort             = fields.Char(string="Required Effort",help="Data extracted from attendance.")
    timesheet_effort            = fields.Char(string="Actual Effort",help="Calculated from timesheet.")
    total_effort                = fields.Char(string="Extra/Deficit Effort",help="Data i.e Required Effort - Actual Effort")   

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f"""CREATE or REPLACE VIEW {self._table} AS (
            SELECT 
            CAST(concat(employee_id,to_char(date_trunc('month', attendance_recorded_date), 'MM'),substring(CAST(extract(year from attendance_recorded_date) AS text), 3, 2)) AS BIGINT) AS id, 
            employee_id,
            parent_id, 
            branch_id,   
            department_id, 
            extract(year from attendance_recorded_date)  AS attendance_year, 
            to_char(attendance_recorded_date, 'Month') AS attendance_month,     
            CAST(to_char(date_trunc('month', attendance_recorded_date), 'MM') AS INT) AS month_number,  
            sum(case when day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then 1 else 0 end) AS working_days,
            coalesce(Cast(TO_CHAR((sum(case 
                when day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') and is_cross_shift=False then shift_out_time - shift_in_time - shift_rest_time  
                when day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') and is_cross_shift=True then shift_in_time - shift_out_time - shift_rest_time else 0 end) || 'hour')::interval, 'HH24 "Hrs" : MI "Mins"') as varchar), '00 Hrs : 00 Mins') AS required_effort,
            coalesce(Cast(TO_CHAR((sum(timesheet_effort) || 'hour')::interval, 'HH24 "Hrs" : MI "Mins"') as varchar), '00 Hrs : 00 Mins') as timesheet_effort,
            coalesce(Cast(TO_CHAR((sum(abs(timesheet_effort)) - sum(case 
                when day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') AND is_cross_shift=False then shift_out_time - shift_in_time - shift_rest_time 
                when day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') AND is_cross_shift=True then shift_in_time - shift_out_time - shift_rest_time else 0 end)  || 'hour')::interval, 'HH24 "Hrs" : MI "Mins"') as varchar), '00 Hrs : 00 Mins') as total_effort
            FROM (SELECT a.employee_id, parent_id, attendance_recorded_date, a.department_id, a.branch_id, day_status, is_cross_shift, shift_out_time, shift_in_time, shift_rest_time, timesheet_effort
            FROM kw_daily_employee_attendance a
            JOIN hr_employee e on e.id=a.employee_id
            LEFT JOIN (SELECT employee_id, date, sum(unit_amount) AS timesheet_effort 
            FROM account_analytic_line GROUP BY employee_id, date) t ON t.employee_id=a.employee_id AND t.date=a.attendance_recorded_date) attendance
            GROUP BY employee_id,department_id,branch_id,6, date_trunc('month', attendance_recorded_date), parent_id, 7
          
            )"""
        # print("query is",query)
        self.env.cr.execute(query)

    @api.multi
    def view_details_action_button(self):
        view_id = self.env.ref('kw_timesheets.view_kw_report_calendar').id
        return {
            'name': 'Tasks',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_timesheet_calendar_report',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'tree,form,calendar',
            'views': [(view_id, 'calendar')],
            'target': 'self',
            'view_id': view_id,
            'domain': [('employee_id', '=', self.employee_id.id)]
        }
