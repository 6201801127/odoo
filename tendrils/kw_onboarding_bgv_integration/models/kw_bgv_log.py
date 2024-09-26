from odoo import models, fields, api


class BgvLogRecord(models.Model):
    _name = "kwonboard_enrollment_bgv_log"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = "enrollment_id"

    enrollment_id = fields.Many2one("kwonboard_enrollment")
    access_token = fields.Char(string="Access Token")

    bgv_request_payload = fields.Text(string="Bgv Request")
    bgv_response_payload = fields.Text(string="Bgv Response")
    bgv_id = fields.Char(string="Bgv Id")

    candidate_request_payload = fields.Text(string="Candidate Request")
    candidate_response_payload = fields.Text(string="Candidate Response")
    candidate_id = fields.Char(string="Candidate Id")

    company_request_payload = fields.Text(string="Company Request")
    company_response_payload = fields.Text(string="Company Response")
    company_id = fields.Char(string="Company Id")

    experience_request_payload = fields.Text(string="Experience Request")
    experience_response_payload = fields.Text(string="Experience Response")
    experience_id = fields.Char(string="Experience Id")
