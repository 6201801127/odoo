from odoo import api, fields, models,_
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
import re

class StockMove(models.Model):
    _inherit = "stock.move"

    price_unit = fields.Float(string='Unit Price', store=True,digits=dp.get_precision('Product Price'))
    price_subtotal = fields.Float(string='Sub Total', readonly=True)
    challan_qty = fields.Float(string="Challan Quantity", digits=dp.get_precision('Product Unit of Measure'))
    l10n_in_hsn_code = fields.Char(related='product_id.product_tmpl_id.l10n_in_hsn_code', string="HSN/SAC Code",
                                   help="Harmonized System Nomenclature/Services Accounting Code")
    taxes_id = fields.Many2many('account.tax', string='Taxes')
    product_qty = fields.Float(string='Quantity')
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)
    product_id = fields.Many2one('product.product', string='Product')
    partner_id = fields.Many2one('res.partner', string='Vendor')
    currency_id = fields.Many2one('res.currency', string='Currency')
    # serial_type = fields.Selection(selection=[('lot_serial', 'Lot/Serial'), ('fa', 'FA Code')],string='Serial Type',default='lot_serial')
    # readonly_serial_type =fields.Boolean(string='Check Readonly status', compute='compute_serial_type')
    # last_fa_code = fields.Char(compute='compute_last_fa_code')
    prefix = fields.Char()
    store_id = fields.Many2one('stock_dept_configuration',string='Store')
    
    # @api.onchange('serial_type')
    # def onchnage_serial_type(self):
    #     if self.serial_type == 'fa':
    #         if self.move_line_ids:
    #             for rec in self.move_line_ids:
    #                 code = self.env['ir.sequence'].next_by_code('fa_code_sequence')
    #                 rec.lot_name = code
    
    # @api.depends('serial_type')
    # def compute_last_fa_code(self):
    #     for rec in self:
    #         last_rec = self.env['stock.quant'].sudo().search([('product_id','=',rec.product_id.id),('fa_code','!=',False)],order='id desc',limit=1)
    #         if last_rec:
    #             rec.last_fa_code = last_rec.fa_code
    
    # @api.multi
    # def update_fa_code(self):
    #     count = 1
    #     r = re.compile("([a-zA-Z]+)([0-9]+)")
    #     last_code = ''
    #     if self.last_fa_code:
    #         last_code = r.match(self.last_fa_code).group(2)
    #     else:
    #         last_code ='000'
    #     for rec in self.move_line_ids:
    #         # rec.lot_name =f"{self.prefix}{str(int(last_code) + count).rjust(3, '0')}"
    #         rec.write({
    #             'lot_name':f"{self.prefix}{str(int(last_code) + count).rjust(3, '0')}",
    #             'qty_done':1,
    #         })
    #         count = count+1
    #     # self.action_show_details()
    #     if self.picking_id.picking_type_id.show_reserved:
    #         view = self.env.ref('stock.view_stock_move_operations')
    #     else:
    #         view = self.env.ref('stock.view_stock_move_nosuggest_operations')

    #     picking_type_id = self.picking_type_id or self.picking_id.picking_type_id
    #     return {
    #         'name': _('Detailed Operations'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'stock.move',
    #         'views': [(view.id, 'form')],
    #         'view_id': view.id,
    #         'target': 'new',
    #         'res_id': self.id,
    #         'context': dict(
    #             self.env.context,
    #             show_lots_m2o=self.has_tracking != 'none' and (picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),  # able to create lots, whatever the value of ` use_create_lots`.
    #             show_lots_text=self.has_tracking != 'none' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
    #             show_source_location=self.location_id.child_ids and self.picking_type_id.code != 'incoming',
    #             show_destination_location=self.location_dest_id.child_ids and self.picking_type_id.code != 'outgoing',
    #             show_package=not self.location_id.usage == 'supplier',
    #             show_reserved_quantity=self.state != 'done'
    #         ),
    #     }
            
    
    # @api.multi
    # def compute_serial_type(self):
    #     for rec in self:
    #         if rec.picking_id.location_dest_id.stock_process_location != 'grn':
    #             rec.readonly_serial_type = True
    #         else:
    #             rec.readonly_serial_type = False
                
    
    # @api.constrains('serial_type')
    # def validate_serial_type(self):
    #     for record in self:
    #         if record.serial_type not in ['lot_serial','fa']:
    #             raise ValidationError("Please Select Serial Type.")
    
    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
            })

    def _prepare_compute_all_values(self):
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.currency_id,
            'product_qty': self.product_qty,
            'product': self.product_id,
            'partner': self.partner_id,
        }

    @api.model
    def create(self, values):
        purchase = self.env['purchase.order'].search([('name', '=', values.get('origin'))])
        product_id = values.get('product_id')
        order_line_ids = purchase.order_line.filtered(lambda o: o.product_id.id == product_id)
        if order_line_ids:
            values['price_unit'] = order_line_ids[0].price_unit
            values['taxes_id'] = [(6,0,order_line_ids[0].taxes_id.ids)]
        result = super(StockMove, self).create(values)
        return result

    @api.multi
    def write(self, values):
        if values.get('move_line_ids'):
            total=0
            for move_line in values.get('move_line_ids'):
                if move_line and move_line[2]:
                    if 'qty_done' in move_line[2] and 'price_unit' not in values:
                        total += move_line[2].get('qty_done') * self.price_unit
                    if 'qty_done' in move_line[2] and 'price_unit' in values:
                        values['price_subtotal'] = move_line[2].get('qty_done') * values.get('price_unit')
                self.price_subtotal= total

        res = super(StockMove, self).write(values)
        if values.get('price_unit') and 'remaining_value' not in values:
            # Update with Query
            picks = self.env['stock.picking'].search([('origin', '=', self.picking_id.origin)]) - self.picking_id
            for pick in picks:
                move = pick.move_ids_without_package.filtered(lambda o: o.product_id.id == self.product_id.id)
                if move:
                    # query = f"""UPDATE stock_move SET price_unit = {self.price_unit} WHERE id = {move.id};"""
                    ids = ','.join([str(id) for id in move.ids])
                    query = f"""UPDATE stock_move SET price_unit = {self.price_unit} WHERE id in ({ids});"""
                    self.env.cr.execute(query)
        
        # if 'serial_type' in values:
        #     moves = self.env['stock.move'].search([('origin', '=', self.origin),('serial_type','!=',self.serial_type)]) - self
        #     # print("moves======",moves)
        #     if moves:
        #         for rec in moves:
        #             # print("rec======",rec)
        #             rec.serial_type = self.serial_type

        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        product = self.product_id.with_context(lang=self.partner_id.lang or self.env.user.lang)
        self.name = product.name
        self.product_uom = product.uom_id.id
        return {'domain': {'product_uom': [('category_id', '=', product.uom_id.category_id.id)]}}
