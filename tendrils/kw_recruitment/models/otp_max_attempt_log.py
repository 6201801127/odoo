from odoo import api, fields, models

class OtpMaxAttemptLog(models.Model):
    _name = 'otp_max_attempt_log'
    _description = 'OTP Max Attempt Log'

    applicant_id = fields.Many2one('hr.applicant')
    mobile = fields.Char(
        string='Mobile',
    )
    max_attempts = fields.Integer(
        string='Max_attempts',
    )
    date = fields.Date(
        string='Date',
    )
    is_passed = fields.Boolean(
        string='Is_passed',
        default=False,
    )
    
    
    
    
