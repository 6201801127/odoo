from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductReceiveRemark(models.TransientModel):
    _name = 'product_receive_remark'
    _description = "Product Receive Remark"

    order_linel_id = fields.Many2one('purchase.order.line', string="Order Line")
    remark = fields.Text(string='Location')

    @api.multi
    def recieve_all_products(self):
        if self.order_linel_id:
            # Existing code to update order_linel_id
            self.order_linel_id.sudo().write({
                'receive_remark': self.remark,
                'status': 'received',
            })

            product_items = self.env['kw_service_register']
            data_list = []
            record_set = self.order_linel_id

            # Obtain the sequence

            for record in record_set:
                count = 0
                for range_data in range(int(record.product_qty)):
                    sequence = self.env['ir.sequence'].next_by_code('kw.service.register.sequence')
                    data = {
                        "po_reference": self.order_linel_id.order_id.name,
                        'product_type': record.product_id.type,
                        "product_code": record.product_id.id,
                        "partner_id": self.order_linel_id.order_id.partner_id.id,
                        "product_uom": record.product_uom.id,
                        "quantity": 1,
                        'price':record.price_unit,
                        # Use the obtained sequence
                        "sequence_number": sequence,
                    }
                    count += 1
                    data_list.append(data)

            # Create records with the updated data list
            product_items.sudo().create(data_list)

    @api.multi
    def reject_all_products(self):
        if self.order_linel_id:
            self.order_linel_id.sudo().write({
                'receive_remark':self.remark,
                'status':'returned',
            })