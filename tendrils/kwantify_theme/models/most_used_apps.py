from odoo import models, fields, api


class MostUsedApps(models.Model):
    _name = 'most_used_apps'
    _description = 'This model is used for storing employee wise most used apps'

    user_id = fields.Many2one('res.users', string="User ID")
    menu_id = fields.Many2one('ir.ui.menu', string="Menu")
