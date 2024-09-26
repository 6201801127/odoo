from odoo import api, fields, models, _, tools

class InterviewSummaryReport(models.Model):
    _name = "interview_summary_report"
    _description = "Interview Summary Report"
    _auto = False

    job_position = fields.Many2one('kw_hr_job_positions', string="Job Position")
    name = fields.Char(string="Name")
    exp_year = fields.Integer(string="Year(s)")
    stage_id = fields.Many2one('hr.recruitment.stage', 'Stage')
    qualification_ids = fields.Many2many("kw_qualification_master", string="Qualification")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (       
    SELECT
    row_number() over() as id,
    a.job_position as job_position,
    a.partner_name as name,
    a.exp_year as exp_year,
    a.stage_id as stage_id,
    b.kw_qualification_master_id as qualification_ids
    FROM hr_applicant as a INNER JOIN hr_applicant_kw_qualification_master_rel as b 
    ON a.id = b.hr_applicant_id
            )""" % (self._table)) 