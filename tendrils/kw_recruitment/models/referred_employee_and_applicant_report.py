from odoo import tools
from odoo import models, fields, api


class RefeeredEmployeeApplicantReport(models.Model):
    _name = "kw_referred_employee_and_applicant_report"
    _description = "Referred employee and applicant status report"
    _auto = False
    _rec_name = 'name'

    applied_date = fields.Datetime(string="Applied Date")
    name = fields.Char(string="Name")
    contact = fields.Char(string="Contact")
    job_position = fields.Many2one("kw_hr_job_positions", string="Job Position")
    source = fields.Many2one("utm.source", string="Source")
    referred_by = fields.Many2one('hr.employee', string="Referred By")
    referred_user = fields.Many2one('res.users', string="Referred By User")
    status = fields.Many2one('hr.recruitment.stage', string="Status")
    referred_amount = fields.Float(string="Referred Amount")
    create_uid = fields.Many2one("res.users", string="User")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (     
                SELECT row_number() over() AS id,  
ha.create_date AS applied_date,
ha.partner_name AS name,
ha.partner_mobile AS contact,
ha.job_position AS job_position,
ha.source_id AS source,
us.code AS source_code,
ha.employee_referred AS referred_by,
ru.id AS referred_user,
ha.stage_id AS status,
ha.create_uid AS create_uid,
k.referred_amount AS referred_amount
FROM hr_applicant AS ha
JOIN kw_hr_job_positions AS k ON ha.job_position = k.id
JOIN utm_source AS us ON us.id = ha.source_id
LEFT JOIN hr_employee AS he ON he.id = ha.employee_referred
LEFT JOIN res_users AS ru ON ru.id=he.user_id
WHERE us.code = 'employee'
                )"""
        self.env.cr.execute(query)
