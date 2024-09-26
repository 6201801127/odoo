from odoo import models, fields, api
# from odoo.exceptions import ValidationError


class KwProductAssignReleaseLog(models.Model):
    _name = "kw_product_assign_release_log"
    _description = "Product Assign Release Log"

    products = fields.Many2one('product.product',string="Products/Items")
    quantity = fields.Float(string='Product Qty')
    assigned_to = fields.Many2one('hr.employee',string='Assigned To')
    materil_id = fields.Many2one('stock.quant',string='Material Id')
    assigned_on = fields.Date(string='Assigned/Released On')
    action_by = fields.Char(string='Action Taken By')
    status = fields.Selection([
        ('Issued', 'Assigned'),
        ('Released', 'Released')
    ], string='Status')
    
class StockQuant(models.Model):
    _name = 'stock.quant'

    _inherit = ['stock.quant', 'mail.thread', 'mail.activity.mixin']
    
    @api.multi
    def action_view_product_tagging(self):
        tree_view_id = self.env.ref("kw_inventory.kw_product_assign_release_log_view_tree").id
        # print("====================",tree_view_id)
        return {
            'name': ' Product Assign Release Log',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_product_assign_release_log',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': tree_view_id,
            'target': 'self',
            'domain':[('products','=',self.product_id.id)]
        }
        
class ProductProductInherited(models.Model):
    _inherit = 'product.product'
    
    on_hand_quantity = fields.Float(string="On Hand Qty" ,compute='compute_on_hand_quantity')
    
    @api.multi
    def action_view_product_tagging(self):
        tree_view_id = self.env.ref("kw_inventory.kw_product_assign_release_log_view_tree").id
        # print("====================",tree_view_id)
        return {
            'name': ' Product Assign Release Log',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_product_assign_release_log',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': tree_view_id,
            'target': 'self',
            'domain':[('products','=',self.default_code)]
        }