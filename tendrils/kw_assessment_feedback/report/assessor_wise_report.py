from odoo import api, fields, models, _, tools

class AssessorWiseReport(models.Model):
    _name = "kw_assessor_wise_report"
    _description = "Assessor Wise Assessment Report"
    _auto = False

    assessor = fields.Char(string="Assessor")
    assessee = fields.Char(string="Assessee")
    assessment_type = fields.Char(string="Assessment Type")
    period = fields.Char(string="Period")
    period_date = fields.Date(string="Period Date")
    period_month = fields.Char(string="Period Month")
    from_date = fields.Date(string="Start Date")
    to_date = fields.Date(string="End Date")
    status = fields.Selection(string='Status',selection=[('0', 'Not Scheduled'),('1', 'Scheduled'), ('2', 'Draft'), ('3', 'Completed'),('4', 'Sent for Approval'),('5', 'Approved'),('6', 'Published')])
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
            select ROW_NUMBER () OVER (ORDER BY fap.id) as id,
            CONCAT(he.name,' (',he.emp_code,')') as assessor,
            CONCAT(her.name,' (',her.emp_code,')') as assessee,  
            fa.name as assessment_type, 
            fap.name as period, 
            fap.period_date as period_date,
            Cast(TRIM(to_char(period_date,'Month')) as varchar) as period_month,
            CASE fa.assessment_type
                    WHEN 'periodic' THEN fd.assessment_from_date
                    WHEN 'probationary' THEN fd.assessment_date
            END AS from_date,
            CASE fa.assessment_type
                WHEN 'periodic' THEN fd.assessment_to_date
                WHEN 'probationary' THEN fd.assessment_date
            END AS to_date,
            coalesce(fd.feedback_status,'0') as status
            from kw_feedback_assessment_period fap
            join kw_feedback_period_assessee_rel fpr on fpr.period_id = fap.id
            left join kw_feedback_map_resources fmr on fmr.id = fap.map_resource_id
            left join kw_feedback_details fd on fd.period_id = fap.id and fpr.emp_id = fd.assessee_id
            left join hr_employee her on her.id = coalesce(fd.assessee_id,fpr.emp_id)
            left join kw_feedback_period_assessor_rel fpar on fpar.period_id = fap.id
            left join kw_feedback_details_assessor_rel fdar on fdar.feedback_details_id = fd.id and fdar.employee_id = fpar.emp_id
            left join hr_employee he on he.id = coalesce(fdar.employee_id,fpar.emp_id)
            left join kw_feedback_assessment fa on fa.id = coalesce(fd.assessment_tagging_id,fmr.assessment_tagging_id)
        )""" % (self._table))   