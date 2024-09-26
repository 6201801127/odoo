from odoo import tools
from odoo import models, fields, api


class ReferredEmployeeApplicantReport(models.Model):
    _name = "hr_applicant_ceo_reference_report"
    _description = "Applicant Referred by CEO report"
    _auto = False
    _rec_name = 'name'

    applied_date = fields.Datetime(string="Applied Date")
    name = fields.Char(string="Name")
    contact = fields.Char(string="Contact")
    reference = fields.Char(string="Reference")
    emp_code = fields.Char(string="Emp. Code")
    date_of_joining = fields.Date(string="Date of Joining")
    last_working_day = fields.Date(string="Exit Date")
    job_position = fields.Many2one("kw_hr_job_positions", string="Job Position")
    source = fields.Many2one("utm.source", string="Source")
    referred_by = fields.Many2one('hr.employee', string="Referred By")
    referred_user = fields.Many2one('res.users', string="Referred By User")
    status = fields.Many2one('hr.recruitment.stage', string="Status")
    create_uid = fields.Many2one("res.users", string="User")
    applicant_id = fields.Many2one("hr.applicant", string="Applicant")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (     
                SELECT row_number() over() AS id,  
ha.id AS applicant_id,
ha.create_date AS applied_date,
ha.partner_name AS name,
ha.partner_mobile AS contact,
ha.job_position AS job_position,
ha.source_id AS source,
ha.reference AS reference,
us.code AS source_code,
ha.employee_referred AS referred_by,
ru.id AS referred_user,
ha.stage_id AS status,
ha.create_uid AS create_uid,
emp.date_of_joining AS date_of_joining,
emp.last_working_day AS last_working_day,
emp.emp_code AS emp_code
FROM hr_applicant AS ha
JOIN utm_source AS us ON us.id = ha.source_id
LEFT JOIN hr_employee AS he ON he.id = ha.employee_referred
LEFT JOIN res_users AS ru ON ru.id=he.user_id
LEFT JOIN kwonboard_enrollment AS enrol ON enrol.applicant_id=ha.id
LEFT JOIN hr_employee AS emp ON emp.onboarding_id = enrol.id
WHERE us.code = 'ceo_reference'
                )"""
        self.env.cr.execute(query)

    def action_download_feedback(self):
        return self.applicant_id.export_feedbacks()
