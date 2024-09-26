from odoo import models, fields, api
from odoo import tools


class KwStarlightReport(models.Model):
    _name = "kw_starlight_report"
    _description = "Starlight Reprot"
    _auto = False

    employee_id = fields.Many2one('hr.employee', string="Employee")
    nominated_by = fields.Many2one('hr.employee', string="Nominated By")
    pending_at = fields.Many2one('hr.employee', string="Pending By")
    reviewed_by = fields.Many2one('hr.employee', string="Reviewed By")
    state = fields.Selection([('sbu', 'Draft'), ('nominate', 'Nominated'), ('review', 'Reviewed'), ('award', 'Awarded'),
                              ('finalise', 'Published'), ('reject', 'Rejected')])
    reason = fields.Char(string="Reason & Justification")
    rnr_id = fields.Many2one(comodel_name='reward_and_recognition')
    reason_type_id = fields.Many2one('starlight_reason_master', string='Reason Type')
    month = fields.Integer(string='Month')
    month_name = fields.Char(string='Month')
    year = fields.Integer(string='Year')
    job_id = fields.Many2one('hr.job',string='Designation')
    department_id = fields.Many2one('hr.department',string='Department')
    division_id = fields.Many2one('hr.department',string='Division')
    section_id = fields.Many2one('hr.department',string='Practise')
    practise_id = fields.Many2one('hr.department',string='Section')
    nominated_on = fields.Datetime(string="Nominated On")
    publish_on = fields.Date(string="Publish On")
    rnr_division_id = fields.Many2one('kw_division_config', string='Department')
    location = fields.Many2one('kw_res_branch', string="Work Location")



    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)

        query = f""" CREATE or REPLACE VIEW {self._table} as (
                SELECT row_number() over() AS id,
                a.employee_id as employee_id,
                a.state as state,
                b.rnr_id as rnr_id,
                b.reason as reason,
                b.reason_type_id as reason_type_id,
                a.month as month,
                a.year as year,
                h.job_id as job_id,
                h.department_id as department_id,
                h.division as division_id,
                h.section as section_id,
                h.practise as practise_id,
                a.nominated_by as nominated_by,
                a.create_date as nominated_on,
                a.publish_on as publish_on,
                a.reviewed_by as reviewed_by,
                a.pending_at as pending_at,
                a.rnr_division_id as rnr_division_id,
                h.job_branch_id as location,
                a.compute_month as month_name 
            from reward_and_recognition a 
            join starlight_reason_lines b on a.id=b.rnr_id 
            join hr_employee h on h.id=a.employee_id
        )"""
        self.env.cr.execute(query)
