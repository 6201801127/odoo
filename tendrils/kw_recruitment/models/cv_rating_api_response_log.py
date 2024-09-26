from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CvRatingApiResponseLog(models.Model):
    _name = 'cv_rating_api_response_log'
    _description = 'CV Rating API Response Log'
    _rec_name = 'status'
    _order = 'id desc'

    applicant_id = fields.Many2one('hr.applicant', string="Applicant")
    payload = fields.Text(string="Payload")
    response = fields.Text(string='Response')
    status = fields.Char(string='Status')
    rating = fields.Char(string="Rating")
    status_code = fields.Char(string='Status Code')