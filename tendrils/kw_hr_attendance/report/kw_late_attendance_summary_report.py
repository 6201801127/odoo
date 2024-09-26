from calendar import monthrange
from datetime import date, datetime
from odoo import tools
from odoo import models, fields, api
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import ATD_STATUS_PRESENT, ATD_STATUS_ABSENT, \
    ATD_STATUS_FHALF_ABSENT, DAY_STATUS_WORKING, DAY_STATUS_RWORKING, ATD_STATUS_SHALF_ABSENT, IN_STATUS_LE, \
    IN_STATUS_EXTRA_LE, IN_STATUS_LE_HALF_DAY, IN_STATUS_LE_FULL_DAY


class EmployeeLateAttendanceSummary(models.Model):
    _name = "kw_late_attendance_summary_report"
    _description = "Employee Late Attendance Summary Report"
    _auto = False
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee', )
    branch_id = fields.Many2one('kw_res_branch', string="Branch/SBU")
    department_id = fields.Many2one(string='Department', comodel_name='hr.department')
    attendance_year = fields.Integer(string="Attendance Year", )
    attendance_month = fields.Char(string="Attendance Month", compute="_compute_month_name")
    month_number = fields.Integer(string="Month Index")
    working_days = fields.Integer(string="Working Days")
    total_late_entries = fields.Integer(string="Total Late Entry")
    lwpc_state = fields.Integer(string="Late With Pay Cut")
    lwopc_state = fields.Integer(string="Late Without Pay Cut")
    pending_at_ra = fields.Integer(string="Pending At RA")
    reporting_authority = fields.Many2one(string='Reporting Authority', comodel_name='hr.employee',
                                          related="employee_id.parent_id")
    total_late_entries_ids = fields.Many2many('kw_daily_employee_attendance', compute="get_total_late_entries")
    lwpc_state_ids = fields.Many2many('kw_daily_employee_attendance', compute="get_total_late_entries")
    lwopc_state_ids = fields.Many2many('kw_daily_employee_attendance', compute="get_total_late_entries")
    pending_at_ra_ids = fields.Many2many('kw_daily_employee_attendance', compute="get_total_late_entries")

    @api.multi
    def _compute_month_name(self):
        for rec in self:
            rec.attendance_month = datetime.strptime(str(rec.attendance_year)+"-"+str(rec.month_number)+"-01", "%Y-%m-%d").strftime('%B')

    # @api.model
    def _get_month_range(self, attendance_year=False, month_number=False):
        attendance_year = attendance_year or self.attendance_year
        month_number = month_number or self.month_number
        _, num_days = monthrange(int(attendance_year), int(month_number))
        start_date = date(int(attendance_year), int(month_number), 1)
        end_date = date(int(attendance_year), int(month_number), num_days)
        return start_date, end_date

    @api.multi
    def get_total_late_entries(self):
        for rec in self:
            start_date, end_date = rec._get_month_range()
            late_entries_records = self.env['kw_daily_employee_attendance'].search(
                [('employee_id', '=', rec.employee_id.id),
                 ('state', 'in', [ATD_STATUS_PRESENT, ATD_STATUS_FHALF_ABSENT, ATD_STATUS_SHALF_ABSENT]),
                 ('day_status', 'in', [DAY_STATUS_WORKING, DAY_STATUS_RWORKING]),
                 ('check_in_status', 'in', [IN_STATUS_LE, IN_STATUS_EXTRA_LE]),
                 ('attendance_recorded_date', '>=', start_date), ('attendance_recorded_date', '<=', end_date)],
                order="attendance_recorded_date asc", )

            rec.total_late_entries_ids = late_entries_records.ids

            lwpc_state_ids = late_entries_records.filtered(lambda rec: rec.le_action_status == '1')
            rec.lwpc_state_ids = lwpc_state_ids.ids

            lwopc_state_ids = late_entries_records.filtered(lambda rec: rec.le_action_status == '2')
            rec.lwopc_state_ids = lwopc_state_ids.ids

            pending_at_ra_ids = late_entries_records.filtered(lambda rec: rec.le_state == '1')
            rec.pending_at_ra_ids = pending_at_ra_ids.ids

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            SELECT 

                CAST(concat(employee_id,to_char(date_trunc('month', attendance_recorded_date), 'MM'),substring(CAST(extract(year from attendance_recorded_date) as text), 3, 2)) AS BIGINT) AS id, 
                 	
                employee_id, 
                extract(year from attendance_recorded_date)  AS attendance_year,                
                CAST(to_char(date_trunc('month', attendance_recorded_date), 'MM') AS INT) AS month_number,  
                department_id, 
                branch_id,                
                sum(case when day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') then 1 else 0 end) as working_days,
                sum(case when state in ('{ATD_STATUS_PRESENT}','{ATD_STATUS_FHALF_ABSENT}','{ATD_STATUS_SHALF_ABSENT}') and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') and check_in_status in ('{IN_STATUS_LE}','{IN_STATUS_EXTRA_LE}') then 1 else 0 end) as total_late_entries,
                sum(case when state in ('{ATD_STATUS_PRESENT}','{ATD_STATUS_FHALF_ABSENT}','{ATD_STATUS_SHALF_ABSENT}') and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') and le_action_status ='1' then 1 else 0 end) as lwpc_state,
                sum(case when state in ('{ATD_STATUS_PRESENT}','{ATD_STATUS_FHALF_ABSENT}','{ATD_STATUS_SHALF_ABSENT}') and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') and le_action_status ='2' then 1 else 0 end) as lwopc_state,
                sum(case when state in ('{ATD_STATUS_PRESENT}','{ATD_STATUS_FHALF_ABSENT}','{ATD_STATUS_SHALF_ABSENT}') and day_status in ('{DAY_STATUS_WORKING}','{DAY_STATUS_RWORKING}') and le_state = '1' then 1 else 0 end) as pending_at_ra
                from kw_daily_employee_attendance
                group by employee_id,department_id,branch_id,3, date_trunc('month', attendance_recorded_date)

            )""" % (self._table))

