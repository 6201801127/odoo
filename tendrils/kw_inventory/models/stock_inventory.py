from odoo import api, models, fields
from odoo.addons import decimal_precision as dp


# class InventoryLine(models.Model):
#     _inherit = "stock.inventory"

#     opening_balance = fields.Float(string="Opening Balance")
#     closing_balance = fields.Float(string="Closing Balance")
#     quantity_inorder = fields.Text(string='Quantity In Order')
#     quantity_indented = fields.Text(string='Quantity Indented')
class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    opening_balance = fields.Float(string="Opening Balance",
                                   digits=dp.get_precision('Product Unit of Measure'), default=0,
                                   help="Opening Balance Quantity")
    closing_balance = fields.Float(string="Closing Balance",
                                   digits=dp.get_precision('Product Unit of Measure'), default=0,
                                   help="Closing Balance Quantity")
    quantity_inorder = fields.Float(string='Quantity In Order',
                                    digits=dp.get_precision('Product Unit of Measure'), default=0,
                                    help="Quantity In Order")
    quantity_indented = fields.Float(string='Quantity Indented',
                                     digits=dp.get_precision('Product Unit of Measure'), default=0,
                                     help="Quantity Indented")
