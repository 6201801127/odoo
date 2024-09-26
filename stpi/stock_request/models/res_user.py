from odoo import fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    
    warehouse_id=fields.Many2one("stock.warehouse", string="Warehouse")
    location_id = fields.Many2one("stock.location",string="Location")