import datetime
from datetime import timedelta
from odoo import models, fields, api


class RecruitmentFeedback(models.TransientModel):
    _name = 'kw_recruitment_consolidated_feedback'
    _description = "Wizard: Download consolidated feedback for an applicant."

    def default_applicant(self):
        return self.env['hr.applicant'].browse(self._context.get('active_id'))

    binary_file = fields.Binary('File', readonly=True)
    file_name = fields.Char('File Name', readonly=True)
    applicant_id = fields.Many2one(comodel_name='hr.applicant', required=True,default=default_applicant)

