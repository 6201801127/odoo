# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-2014 CodUP (<http://codup.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _
# from openerp.osv import fields, osv
from datetime import datetime
from odoo import tools
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_asset = fields.Boolean('Is Asset', default=True)
    asset_type = fields.Many2one('asset.type', string='Asset Type')
    brands = fields.Many2one('asset.brand', 'Make/Brand')
    model_no = fields.Many2one('asset.model', 'Model No')
    brand = fields.Boolean('Brand')
    model = fields.Boolean('Model')
    partners = fields.Char('partners')
    trigger = fields.Char('trigger')
    test = fields.Char('trigger')
    sale_ok = fields.Boolean(
        'Can be Sold', default=False,
        help="Specify if the product can be selected in a sales order line.")

    # 
    # @api.onchange("is_asset")
    # def onchange_is_asset(self):
    #     res = {}
    #     if self.is_asset:
    #         product_category = self.env['product.category'].search_read([('name', '=', 'Capital Expenditures')],['id'])
    #         res = {
    #             'categ_id': product_category[0]['id']
    #         }
    #     return {'value': res}

    
    @api.onchange("asset_type")
    def onchange_asset_type(self):
        res = {}
        if self.asset_type:
            asset_type = self.env['asset.type'].browse(self.asset_type)
            res = {
                'brand': self.asset_type.brand,
                'model': self.asset_type.model,
            }
        return {'value': res}


class Product(models.Model):
    _inherit = 'product.product'

    # 
    # @api.onchange("is_asset")
    # def onchange_is_asset(self):
    #     res = {}
    #     if self.is_asset:
    #         product_category = self.env['product.category'].search_read([('name', '=', 'Capital Expenditures')],['id'])
    #         res = {
    #             'categ_id': product_category[0]['id']
    #         }
    #     return {'value': res}

    
    @api.onchange("asset_type")
    def onchange_asset_type(self):
        res = {}
        if self.asset_type:
            asset_type = self.env['asset.type'].browse(self.asset_type)
            res = {
                'brand': self.asset_type.brand,
                'model': self.asset_type.model,
            }
        return {'value': res}


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    
    def button_validate(self):
        self.ensure_one()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some lines to move'))

        # If no lots when needed, raise error
        picking_type = self.picking_type_id
        no_quantities_done = all(
            line.qty_done == 0.0 for line in self.move_line_ids)
        no_initial_demand = all(move.product_uom_qty ==
                                0.0 for move in self.move_lines)
        if no_initial_demand and no_quantities_done:
            raise UserError(
                _('You cannot validate a transfer if you have not processed any quantity.'))

        if picking_type.use_create_lots or picking_type.use_existing_lots:
            lines_to_check = self.move_line_ids
            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(
                    lambda line: float_compare(line.qty_done, 0,
                                               precision_rounding=line.product_uom_id.rounding)
                )
                qty = sum(line.quantity_done for line in self.move_lines)
                self.create_assets()
            for line in lines_to_check:
                product = line.product_id
                if product and product.tracking != 'none':
                    if not line.lot_name and not line.lot_id:
                        raise UserError(
                            _('You need to supply a lot/serial number for %s.') % product.display_name)
                    elif line.qty_done == 0:
                        raise UserError(
                            _('You cannot validate a transfer if you have not processed any quantity for %s.') % product.display_name)
        return super(StockPicking, self).button_validate()
        if no_quantities_done:
            view = self.env.ref('stock.view_immediate_transfer')
            wiz = self.env['stock.immediate.transfer'].create(
                {'pick_ids': [(4, self.id)]})
            return {
                'name': _('Immediate Transfer?'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.immediate.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
            view = self.env.ref('stock.view_overprocessed_transfer')
            wiz = self.env['stock.overprocessed.transfer'].create(
                {'picking_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.overprocessed.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        # Check backorder should check for other barcodes
        if self._check_backorder():
            return self.action_generate_backorder_wizard()

        self.action_done()
        return

    # 
    # def button_validate(self):
    #     print "button_validate"
    #     res = super(StockPicking, self).button_validate()
    #     self.create_assets()
    #     return res

    
    def create_assets(self):
        for move_line in [self.mapped('move_lines')]:
            for prod in move_line:
                if prod.quantity_done == 0.0:
                    qty = prod.product_uom_qty
                if not prod.quantity_done == 0.0:
                    qty = prod.quantity_done
                purchase_id = self.env['purchase.order'].search_read(
                    [('name', '=', self.origin)],
                    ['date_order', 'partner_id'])
                if prod.product_id.is_asset:
                    for quantity in range(0, int(qty)):
                        asset_datas = {
                            'asset_type': prod.product_id.asset_type.id,
                            'brand': prod.product_id.brand,
                            'model': prod.product_id.model,
                            'mobile': prod.product_id.asset_type.mobile,
                            'state': 'draft',
                            'picking_id': self.id,
                            'model_no': prod.product_id.model_no.id,
                            'brands': prod.product_id.brands.id,
                            'purchase_date': purchase_id and purchase_id[0]['date_order'],
                            'partner_id': self.partner_id.id,
                            'property_stock_asset': self.location_dest_id.id,
                            'creation_date': datetime.now(),
                            'active': True,
                            'product_id': prod.product_id.id,
                            'name': prod.product_id.name
                        }
                        asset = self.env['asset.asset'].create(asset_datas)
        return True


class StockImmediateTransfers(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    def process(self):

        for picking in self.pick_ids:
            picking.create_assets()
        return super(StockImmediateTransfers, self).process()


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    def action_validate(self):
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        available_qty = sum(self.env['stock.quant']._gather(self.product_id,
                                                            self.location_id,
                                                            self.lot_id,
                                                            self.package_id,
                                                            self.owner_id,
                                                            strict=True).mapped('quantity'))
        if float_compare(available_qty, self.scrap_qty, precision_digits=precision) >= 0:
            assets = self.env['asset.asset'].search([('picking_id', '=', self.picking_id.id),
                                                     ('product_id', '=',
                                                      self.product_id.id),
                                                     ('stock_scrap', '=', False)])
            for asset in assets:
                for qty in range(0, int(self.scrap_qty)):
                    if qty != int(self.scrap_qty):
                        asset.write({'state': 'scrapped', 'stock_scrap': True})
            return self.do_scrap()
        else:
            return {
                'name': _('Insufficient Quantity'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.warn.insufficient.qty.scrap',
                'view_id': self.env.ref('stock.stock_warn_insufficient_qty_scrap_form_view').id,
                'type': 'ir.actions.act_window',
                'context': {
                    'default_product_id': self.product_id.id,
                    'default_location_id': self.location_id.id,
                    'default_scrap_id': self.id
                },
                'target': 'new'
            }
