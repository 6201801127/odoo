from odoo import api, fields, models, _, tools
from dateutil.relativedelta import relativedelta
from datetime import datetime,date
import calendar

class AssessmentProgressReport(models.Model):
    _name = "kw_assessment_progress_report"
    _description = "Assessment Progress Report"
    _auto = False
    _rec_name = 'assessee'


    assessee            = fields.Char(string="Assessee")
    designation         = fields.Char(string="Designation")
    department          = fields.Char(string="Department")
    period              = fields.Char(string="Period")
    period_date         = fields.Date(string='Period Date')
    assessment          = fields.Char(string="Assessment Type")
    from_date           = fields.Date(string="From Date")
    to_date             = fields.Date(string="To Date")
    feedback_status     = fields.Selection(string='Status',selection=[('0', 'Not Scheduled'),('1', 'Scheduled'), ('2', 'Draft'), ('3', 'Completed'),('4', 'Sent for Approval'),('5', 'Approved'),('6', 'Published')], default='0')
    score               = fields.Char(string="Score (in %)")
    weightage           = fields.Char(string="Performance Grade")
    positive_area       = fields.Char(string="Positive Area")              
    weak_area           = fields.Char(string="Weak Area")  
    suggestion_remark   = fields.Char(string="Suggestion Remark")
    previous_grade      = fields.Char(string='Previous Grade 1',compute='_get_grade')
    last_grade          = fields.Char(string='Previous Grade 2',compute='_get_grade')
    assessors           = fields.Text(string='Assessors',compute='_get_assessors')

    @api.multi
    def _get_assessors(self):
        for record in self:
            details = self.env['kw_feedback_details'].browse(record.id)
            if details:
                for configs in details:
                    values = ', '.join(str(user_names.name + ' ('+ user_names.emp_code +')') if user_names and user_names.emp_code else user_names.name for user_names in configs.assessor_id)
                    record.assessors = values

    @api.multi
    def _get_grade(self):
        for record in self:
            details = self.env['kw_feedback_details'].browse(record.id)
            if details:
                for feedbacks in details:

                    month_name = calendar.month_name[feedbacks.period_id.period_date.month-1]
                    full_name = str(month_name+"-"+str(feedbacks.period_id.period_date.year))
                    periods = self.env['kw_feedback_details'].search(
                        [('period_id.name', '=', full_name),
                         ('period_id.map_resource_id', '=', feedbacks.period_id.map_resource_id.id),
                         ('feedback_status', 'in', ['3', '4', '5', '6'])],
                        limit=1)

                    if periods:
                        record.previous_grade = periods.weightage_id.value if periods.weightage_id.value else False

                        second_month_name = calendar.month_name[feedbacks.period_id.period_date.month-2]
                        second_full_name = str(second_month_name+"-"+str(feedbacks.period_id.period_date.year))
                        second_periods = self.env['kw_feedback_details'].search(
                            [('period_id.name', '=', second_full_name),
                             ('period_id.map_resource_id', '=', feedbacks.period_id.map_resource_id.id),
                             ('feedback_status', 'in', ['3', '4', '5', '6'])], limit=1)
                        if second_periods:
                            record.last_grade = second_periods.weightage_id.value if second_periods.weightage_id.value else False
                        else:
                            record.last_grade = 'Not Done'
                    else:
                        record.previous_grade = 'Not Done'
                        record.last_grade = 'Not Done'

    @api.multi
    def view_assessee_feedback_details(self):
        self.ensure_one()
        view_id = self.env.ref('kw_assessment_feedback.kw_feedback_publish_feedback_form_view1').id
        return {
            'name': 'Assessee Feedback Details',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_feedback_details',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': view_id,
            'target': 'new',
            'flags': {'mode': 'readonly', 'toolbar': False, 'action_buttons': False},
        }

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
            select fd.id as id, 
                CONCAT(he.name,' (',he.emp_code,')') as assessee,
                dept.name as department,
                job.name as designation,
                fap.name as period,
                fap.period_date as period_date,
                fa.name as assessment, 
                fd.assessment_from_date AS from_date,
                fd.assessment_to_date AS to_date,
                fd.feedback_status as feedback_status, 
                fd.total_score as score, 
                fd.positive_area as positive_area,
                fd.weak_area as weak_area,
                fd.suggestion_remark as suggestion_remark,
                fwm.value as weightage
                from kw_feedback_details fd
                left join hr_employee he on he.id = fd.assessee_id
                left join kw_feedback_assessment_period fap on fap.id = fd.period_id
                join kw_feedback_assessment fa on fa.id = fd.assessment_tagging_id and assessment_type = 'periodic'
                left join kw_feedback_weightage_master fwm on fwm.id = fd.weightage_id
                LEFT OUTER JOIN hr_department dept on dept.id = he.department_id
                LEFT OUTER JOIN hr_job job on job.id = he.job_id
            ORDER BY id DESC
        )""" % (self._table))   
