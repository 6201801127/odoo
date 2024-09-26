from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import email_send

class ResUsersPasswordExpiry(models.Model):
    _inherit = 'res.users'

    expiry_date = fields.Date(string='Password Expiry Date')
                
    def write(self, vals):
        if 'password' in vals:
            today = datetime.now().date()
            expiry_months = self.env['ir.config_parameter'].sudo().get_param('password_security.pass_expiry_time')
            expiry_date = today + timedelta(days=int(expiry_months) * 30)
            vals['expiry_date'] = expiry_date

        return super(ResUsersPasswordExpiry, self).write(vals)

        
    def send_password_expiry_notifications(self):
        # print("scheduler caledd=========================")
        today = datetime.now().date()
        expiry_limit = today + timedelta(days=10)
        
        users_to_notify = self.env['res.users'].search([
            ('expiry_date', '>=', today),
            ('expiry_date', '<=', expiry_limit),
        ])
        # print("users to notify-========================",users_to_notify)
        
        template = self.env.ref('password_security.password_expiration_reminder_email')
        
        for user in users_to_notify:
            days_remaining = (user.expiry_date - today).days
            # print('days remaining=========================',days_remaining)
            template.with_context({'days_remaining': days_remaining}).send_mail(user.id, force_send=True)

