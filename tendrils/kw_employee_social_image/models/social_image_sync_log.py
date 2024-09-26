from odoo import api, fields, models


class SocialImageSyncLog(models.Model):
    _name = 'log_sync_social_image'
    _description = 'Employee Candid Image Sync'

    name = fields.Char(string='Employee Name')
    status = fields.Char(string='Status')
    payload = fields.Char(string='payload')
