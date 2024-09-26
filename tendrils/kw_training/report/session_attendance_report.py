from odoo import models, fields, api
from odoo import tools
from datetime import datetime, date, timedelta


class SessionAttendanceReport(models.Model):
    _name = 'kw_session_attendance_report'
    _description = 'Session Attendance Report'
    _auto = False



    training_id = fields.Many2one('kw_training', "Training")
    session_id = fields.Many2one('kw_training_schedule', "Session")
    date = fields.Date(string="Date")
    participant_id = fields.Many2one("hr.employee","Employee")
    emp_code = fields.Char(string="Participant's Code")
    designation = fields.Many2one('hr.job' , string="") 
    department_id = fields.Many2one('hr.department',string="Department")
    attendance = fields.Char("Attendance")
    participant_detail = fields.Char("Participants")

    # @api.depends('participant_id')
    # def _participant_detail(self):
    #     for rec in self:
    #         rec.participant_detail = f"{rec.participant_id.name} '||' {rec.participant_id.emp_code} '||' {rec.designation.name} '||' {rec.participant_id.work_email} '||' {rec.participant_id.mobile_phone}"


    @api.model_cr
    def init(self):
        current_fiscal = self.env['account.fiscalyear'].search([('date_start', '<=', datetime.today().date()), 
                                                                ('date_stop', '>=', datetime.today().date())])
        year_data = self.env.context.get('year_data')  if self.env.context.get('year_data') else current_fiscal
        training = int(self.env.context.get('training_data')) if self.env.context.get('training_data') else 0
        tools.drop_view_if_exists(self.env.cr, self._table)

        self.env.cr.execute(f""" CREATE or REPLACE VIEW {self._table} as 
        SELECT
            row_number() over() AS id,
            a.training_id AS training_id,
            a.session_id AS session_id,
            s.date AS date,
            p.participant_id AS participant_id,
            h.emp_code AS emp_code,
            h.job_id AS designation,
            h.department_id AS department_id,
            CASE WHEN p.attended IS TRUE THEN 'P' ELSE 'A' END AS attendance,
            CONCAT_WS('||',
                h.name,
                h.emp_code,
                j.name,
                h.work_email,
                h.mobile_phone
            ) AS participant_detail
        FROM
            kw_training_attendance a
            JOIN kw_training_schedule s ON s.id = a.session_id
            JOIN kw_training_attendance_details p ON a.id = p.attendance_id
            JOIN hr_employee h ON h.id = p.participant_id
            LEFT JOIN hr_job j ON h.job_id = j.id
        WHERE
            a.training_id = {training}
            AND s.date BETWEEN '{year_data.date_start}' AND '{year_data.date_stop}'
    """)