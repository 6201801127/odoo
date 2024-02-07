from odoo import models, fields

class KsDashboardNinjaTemplate(models.Model):
    _name = 'ks_dashboard_ninja.board_template'
    _description = 'Dashboard Ninja Template'
    
    name = fields.Char()
    ks_gridstack_config = fields.Char()
    ks_item_count = fields.Integer()