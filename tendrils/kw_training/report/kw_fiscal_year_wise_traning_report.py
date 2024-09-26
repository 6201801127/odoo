from odoo import models, fields, api
from odoo import tools

class FiscalYearWiseReport(models.Model):
    _name = 'training_fiscalyear_wise_report'
    _description = 'Traning Fiscal year wise report'
    _auto = False
    _rec_name = 'fiscal_year'


    fiscal_year = fields.Char("Fiscal Year")
    training_id = fields.Char("Traning")
    duration = fields.Char(string="Duration in Hrs")
    participant_id = fields.Many2one('hr.employee',string="Participants")
    emp_name = fields.Char(string="Participants")
    emp_code = fields.Char(string="Participant's Code")
    department_id = fields.Many2one('hr.department',string="Department")
    designation = fields.Many2one('hr.job' , string="") 
    instructor = fields.Many2one("hr.employee",string="InstDesignationructor")
    session_id = fields.Many2one('kw_training_attendance_details' , string='Session')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE OR REPLACE VIEW %s AS 
                            (SELECT row_number() over() as id,
                                y.name AS fiscal_year,
                                c.emp_code AS emp_code,
                                c.department_id AS department_id,
                                c.name AS emp_name,
                                b.participant_id AS participant_id,
                                c.job_id AS designation,
                                array_to_string(array_agg(DISTINCT t.name), ', ') AS training_id,
                                array_to_string(array_agg(DISTINCT a.session_id), ', ') AS session_id,
                                SUM(DISTINCT CAST(d.duration as interval )) as duration
                                FROM kw_training t
                                JOIN account_fiscalyear y on y.id=t.financial_year
                                JOIN kw_training_attendance a on a.training_id=t.id
                                JOIN kw_training_attendance_details b on b.attendance_id= a.id
                                JOIN hr_employee c on c.id = b.participant_id
                                LEFT JOIN (
                                    SELECT training_id,
                                        coalesce(Cast(TO_CHAR((sum(to_timestamp(to_time,'HH24:MI:SS') - to_timestamp(from_time,'HH24:MI:SS')) || 'hour')::interval, 'HH24:MI') as varchar), '00:00') as duration
                                    FROM kw_training_schedule
                                    GROUP BY training_id
                                ) d ON d.training_id = t.id
                                GROUP BY y.name, y.id, b.participant_id , c.emp_code, c.job_id , c.name , c.department_id

                            )
                        """ % (self._table))
