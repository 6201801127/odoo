from calendar import monthrange
from datetime import date, datetime
from odoo import tools
from odoo import models, fields, api
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import DAY_STATUS_WORKING, DAY_STATUS_RWORKING


class ProductiveSummaryReport(models.Model):
    _name = "kw_productive_summary_report"
    _description = "Employee Monthly Productive Hours Summary"
    _auto = False
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee', )
    branch_id = fields.Many2one('kw_res_branch', string="Branch/SBU")

    department_id = fields.Many2one(string='Department', comodel_name='hr.department')
    attendance_year = fields.Integer(string="Year", )
    attendance_month = fields.Char(string="Month", compute="_compute_month_name")
    month_number = fields.Integer(string="Month Index")
    reporting_authority = fields.Many2one(string='Reporting Authority', comodel_name='hr.employee',
                                          related="employee_id.parent_id")
    working_days = fields.Integer(string="Working Days")
    total_effort = fields.Char(string="Actual Effort")
    required_effort = fields.Char(string="Required Effort", )
    extra_effort = fields.Char(string="Extra/Deficit Effort", )
    present_child_ids = fields.Many2many('kw_daily_employee_attendance', string="Child Ids",
                                         compute="get_no_of_present_days")

    @api.multi
    def _compute_month_name(self):
        for rec in self:
            rec.attendance_month = datetime.strptime(str(rec.attendance_year) + "-" + str(rec.month_number) + "-01", "%Y-%m-%d").strftime('%B')

    @api.multi
    def get_no_of_present_days(self):
        for rec in self:
            start_date, end_date = self.env['kw_late_attendance_summary_report']._get_month_range(rec.attendance_year, rec.month_number)

            daily_attendance_records = self.env['kw_daily_employee_attendance'].search(
                [('employee_id', '=', rec.employee_id.id), ('attendance_recorded_date', '>=', start_date),
                 ('attendance_recorded_date', '<=', end_date)], order="attendance_recorded_date asc", )

            self.present_child_ids = daily_attendance_records.ids

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
           select 
		        CAST(concat(employee_id,to_char(date_trunc('month', attendance_recorded_date), 'MM'),substring(CAST(extract(year from attendance_recorded_date) as text), 3, 2)) AS BIGINT) AS id, 
                employee_id,
                department_id, 
                branch_id,   
                extract(year from attendance_recorded_date)  AS attendance_year,                
                CAST(to_char(date_trunc('month', attendance_recorded_date), 'MM') AS INT) AS month_number,  
                sum(case when day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then 1 else 0 end) as working_days,
                coalesce(Cast(TO_CHAR((sum(worked_hours) || 'hour')::interval, 'HH24 "Hrs" : MI "Mins"') as varchar), '00 Hrs : 00 Mins') as total_effort,
                coalesce(Cast(TO_CHAR((sum(case when day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') and is_cross_shift=False then shift_out_time - shift_in_time - shift_rest_time  when day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') and is_cross_shift=True then shift_in_time - shift_out_time - shift_rest_time else 0 end) || 'hour')::interval, 'HH24 "Hrs" : MI "Mins"') as varchar), '00 Hrs : 00 Mins') as required_effort,
                coalesce(Cast(TO_CHAR((sum(abs(worked_hours)) - sum(case when day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') and is_cross_shift=False then shift_out_time - shift_in_time - shift_rest_time when day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') and is_cross_shift=True then shift_in_time - shift_out_time - shift_rest_time else 0 end)  || 'hour')::interval, 'HH24 "Hrs" : MI "Mins"') as varchar), '00 Hrs : 00 Mins') as extra_effort
                
                from kw_daily_employee_attendance
                group by employee_id,department_id,branch_id,5, date_trunc('month', attendance_recorded_date)
            )""" % (self._table))
