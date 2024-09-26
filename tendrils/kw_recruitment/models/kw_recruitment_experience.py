# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ApplicantExperience(models.Model):
    _name = "kw_recruitment_experience"
    _description = "Holds different experiences for an applicant"

    applicant_id = fields.Many2one('hr.applicant', 'Applicant', required=True, ondelete="cascade")
    job_role = fields.Char(string='Job Role', required=True)
    date_from = fields.Date("From")
    date_to = fields.Date("To")
    from_date = fields.Char("From")
    to_date = fields.Char("To")
