from odoo import api, fields, models

class OtpOnboardingMaxAttemptLog(models.Model):
    _name = 'otp_onboarding_max_attempt_log'
    _description = 'OTP Onboarding Max Attempt Log'

    enrollment_id = fields.Many2one('kwonboard_enrollment')
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
    
    
    
    
