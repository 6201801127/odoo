from odoo import models, fields, api


class WebsiteVisitor(models.Model):
    _inherit = 'website.visitor'
    _description = 'Website Visitor'

    lat = fields.Char('Latitude')
    lng = fields.Char('Longitude')

   