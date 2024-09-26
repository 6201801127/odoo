from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_Skill_Date_Configuration(models.Model):
    _name = 'kw_skill_date_configuration'
    _description = "A model to create date Configuration."

    user_from_date = fields.Date(string="From Date", required=True,)
    user_to_date = fields.Date(string='To date',  required=True)
    ra_from_date = fields.Date(string='From Date', required=True)
    ra_to_date = fields.Date(string="To Date", required=True )

    @api.model
    def create(self, vals):
        existing_record = self.env['kw_skill_date_configuration'].search([])
        if existing_record:
            raise ValidationError("Only one Date Configuration is allowed at-a-time.")
        return super(kw_Skill_Date_Configuration, self).create(vals)
    
    @api.constrains('user_from_date','user_to_date','ra_from_date','ra_to_date')
    def check_dates(self):
        if self.user_from_date > self.user_to_date:
            raise ValidationError('To-date can not be less than From-date in Users Section')
        elif self.ra_from_date > self.ra_to_date:
            raise ValidationError('To-date can not be less than From-date in RA Section')
        
        
    def action_send_notification(self):
        return {
            'name': "Send Notification",
            'view_mode': 'form',
            'view_id': self.env.ref('kw_skill_assessment.notify_user_mail_wizard').id,
            'view_type': 'form',
            'res_model': 'skill_assessment_mail_notify_wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
