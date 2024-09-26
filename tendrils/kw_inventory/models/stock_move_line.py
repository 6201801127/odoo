from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    remark = fields.Char(string="Remarks", )
    # challan_qty =  fields.Float(string="Challan Quantity",)
    challan_qty = fields.Float(string='Challan Quantity', digits=dp.get_precision('Product Unit of Measure'))
    excess_quantity = fields.Float(string='Excess Quantity', digits=dp.get_precision('Product Unit of Measure'))
    shortage_quantity = fields.Float(string='Shortage Quantity', digits=dp.get_precision('Product Unit of Measure'))
    check_boolean = fields.Boolean("Check process location",compute='compute_check_boolean')
    
    def compute_check_boolean(self):
        # print("method chek called====================")
        for record in self:
            # print("record============",record)
            if record.location_dest_id.stock_process_location == 'qc' or record.location_dest_id.stock_process_location == 'store':
                record.check_boolean = True
                # print("check boolean==========",record.check_boolean)

    @api.onchange('challan_qty')
    def _onchange_challan_qty(self):
        record_id = self._origin.id
        challan_qty = self.challan_qty
        rec = self.env['stock.move.line'].sudo().search([('id', '=', record_id)])
        if rec:
            rec.move_id.write({'challan_qty': challan_qty})
