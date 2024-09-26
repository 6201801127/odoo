from calendar import monthrange
from datetime import date 
from odoo import tools
from odoo import models, fields, api
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import DAY_STATUS_WORKING,DAY_STATUS_RWORKING


class EffortEstimationReport(models.Model):
    _name = "kw_effort_estimation_report"
    _description = "Employee Effort Estimation Report"
    _auto = False
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee', )
    attendance_year = fields.Char(string="Attendance Year", )
    attendance_month = fields.Char(string="Attendance Month")
    month_number = fields.Integer(string="Month Index")
    reporting_authority = fields.Many2one(string='Reporting Authority', comodel_name='hr.employee', )
    total_effort = fields.Char(string="Total Effort")
    required_effort = fields.Char(string="Required Effort", )
    extra_effort = fields.Char(string="Extra Effort", )
    present_child_ids = fields.Many2many('kw_daily_employee_attendance', string="Child Ids",
                                         compute="get_no_of_present_days")

    def get_no_of_present_days(self):
        start_date, end_date = self.env['kw_late_attendance_summary_report']._get_month_range(self.attendance_year,
                                                                                              self.month_number)
        daily_attendance_records = self.env['kw_daily_employee_attendance'].search(
            [('employee_id', '=', self.employee_id.id), ('attendance_recorded_date', '>=', start_date),
             ('attendance_recorded_date', '<=', end_date)], order="attendance_recorded_date asc", )

        self.present_child_ids = daily_attendance_records.ids

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
           with attendance as
            (
                select employee_id,
                to_char(attendance_recorded_date,'MM') as month_number,
                Cast(TRIM(to_char(attendance_recorded_date,'Month')) as varchar) as attendance_month,
                cast(extract(year from attendance_recorded_date) as varchar) as attendance_year,
                coalesce(Cast(TO_CHAR((sum(worked_hours + shift_rest_time) || 'hour')::interval, 'HH24 "Hrs" : MI "Mins"') as varchar), '00 Hrs : 00 Mins') as total_effort,
                coalesce(Cast(TO_CHAR((sum(case when day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then shift_out_time - shift_in_time else 0 end) || 'hour')::interval, 'HH24 "Hrs" : MI "Mins"') as varchar), '00 Hrs : 00 Mins') as required_effort,
                coalesce(Cast(TO_CHAR((sum(abs(worked_hours + shift_rest_time)) - sum(case when day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then shift_out_time - shift_in_time else 0 end)  || 'hour')::interval, 'HH24 "Hrs" : MI "Mins"') as varchar), '00 Hrs : 00 Mins') as extra_effort
                from kw_daily_employee_attendance
                group by employee_id, extract(year from attendance_recorded_date), to_char(attendance_recorded_date,'Month'),  to_char(attendance_recorded_date,'MM')
    )
                select ROW_NUMBER () OVER (ORDER BY e.id) as id, e.id as employee_id, e.parent_id as reporting_authority,
                month_number, attendance_month, attendance_year, total_effort, required_effort, extra_effort from hr_employee e
                left join attendance a on a.employee_id = e.id 
                order by e.name
            )""" % (self._table))