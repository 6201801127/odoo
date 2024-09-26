# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class hr_job(models.Model):
    _inherit = "hr.job"
    _order = "is_published desc, name asc"

    # ---------Additional fields-----------#
    expiration = fields.Date("Expires On")
    job_code = fields.Char("Job Code")
    applicant_feedback_form = fields.Many2one('survey.survey', 'Applicant Feedback Form', domain="[('survey_type.code', '=', 'recr')]")

    job_position_ids = fields.One2many(string='Job Position', comodel_name='kw_hr_job_positions', inverse_name='job_id', )
    job_position_count = fields.Integer('Job Count', compute='_compute_job_positions')

    # ---------Additional fields-----------#

    # ---------Modified fields-----------#
    is_published = fields.Boolean("Is Published", )
    survey_id = fields.Many2one('survey.survey', 'Interview Form', domain="[('survey_type.code', '=', 'recr')]")

    # ---------Modified fields-----------#
    no_of_recruitment = fields.Integer(string='Expected New Employees', copy=False,
        compute='_compute_job_positions', help='Number of new employees you expect to recruit.')

    @api.multi
    def action_print_recruitment_survey(self):
        return self.survey_id.action_print_recruitment_survey()

    @api.multi
    def _compute_job_positions(self):
        for record in self:
            if record.job_position_ids:
                count = 0
                for data in record.job_position_ids:
                    if data.website_published and data.no_of_recruitment and data.no_of_recruitment > 0:
                        count = count + data.no_of_recruitment
                record.job_position_count = count
                record.expected_employees = record.no_of_employee + count
                record.no_of_recruitment = count
                # record.write({'no_of_recruitment': count})
            else:
                record.job_position_count = 0
                record.expected_employees = record.no_of_employee
                record.no_of_recruitment = 0
                # record.write({'no_of_recruitment': 0})
