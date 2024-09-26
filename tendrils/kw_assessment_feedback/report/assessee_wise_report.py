from odoo import api, fields, models, _, tools

class AssessorWiseReport(models.Model):
    _name = "kw_assessee_wise_report"
    _description = "Assessee Wise Assessment Report"
    _auto = False

    assessee = fields.Char(string="Assessee")
    designation = fields.Char(string="Designation")
    period = fields.Char(string="Period")
    period_date = fields.Date(string="Period Date")
    period_month = fields.Char(string="Period Month")
    assessment_type = fields.Char(string="Assessment Type")
    date_of_joining = fields.Date(string="Date of Joining")
    probation_complete_date = fields.Date(string="Final Assessment Complete Date")
    status = fields.Selection(string='Status',selection=[('0', 'Not Scheduled'),('1', 'Scheduled'), ('2', 'Draft'), ('3', 'Completed'),('4', 'Published')])

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
            select ROW_NUMBER () OVER (ORDER BY he.id) as id,
            CONCAT(he.name,' (',he.emp_code,')') as assessee,  
            hj.name as designation,
            fap.name as period,
            fap.period_date as period_date,
            Cast(TRIM(to_char(period_date,'Month')) as varchar) as period_month,
            fa.name as assessment_type,
            he.date_of_joining as date_of_joining,
            he.date_of_completed_probation as probation_complete_date,
            coalesce(fd.feedback_status,'0') as status
            from hr_employee he
            join hr_job hj on hj.id = he.job_id
            left outer join kw_feedback_period_assessee_rel fpar on fpar.emp_id = he.id 
            left outer join kw_feedback_assessment_period fap on fap.id = fpar.period_id
            left outer join kw_feedback_map_resources fmr on fmr.id = fap.map_resource_id
            left outer join kw_feedback_details fd on fd.period_id = fap.id and fd.assessee_id = fpar.emp_id
            left outer join kw_feedback_assessment fa on fa.id = coalesce(fd.assessment_tagging_id,fmr.assessment_tagging_id)
            where he.on_probation = 't'
        )""" % (self._table))   