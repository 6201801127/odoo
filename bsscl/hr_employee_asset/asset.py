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
from datetime import datetime, timedelta
from openerp import tools
from odoo.exceptions import UserError, AccessError,ValidationError
import re

class AssetAssetID(models.Model):
    _name = 'asset.asset.line'

    order_id = fields.Many2one(
        'asset.transfer', string='Asset Reference', index=True)
    serial = fields.Char('Serial #', size=64)
    receiving_status = fields.Selection(
        [('received', 'Received'),
         ('not_received', 'Not Received')], 'Receiving Status')
    check = fields.Boolean('Check')
    asset_id = fields.Many2one('asset.asset', 'Asset')
    remarks = fields.Char(string='Remarks')
    asset_type = fields.Many2one('asset.type', 'Type')


class AssetType(models.Model):
    """
        Assets Type
    """
    _name = 'asset.type'
    _rec_name = 'name'

    name = fields.Char(string='Asset Type')
    brand = fields.Boolean('Brand Mandatory')
    model = fields.Boolean('Model Mandatory')
    mobile = fields.Boolean('Mobile Number Mandatory')

    @api.constrains('name')
    @api.onchange('name')	
    def _onchange_name(self):
        for rec in self:
            if rec.name and not re.match(r'[A-Za-z]{1}[A-Za-z0-9\s]*$',str(rec.name)):

                raise ValidationError("Name should start from an alphabet")
            



class Model(models.Model):
    """
        Model Number
    """
    _name = 'asset.model'
    _rec_name = 'model_no'

    model_no = fields.Char(string='Name')
    asset_type = fields.Many2one('asset.type', 'Asset Type')
    asset_brand = fields.Many2one('asset.brand', 'Brand')


class Brand(models.Model):
    """
        Assets Brand
    """
    _name = 'asset.brand'
    _rec_name = 'brand'

    brand = fields.Char(string='Name')
    asset_type = fields.Many2one('asset.type', 'Asset Type')


class Tag(models.Model):
    """Assets Tag."""

    _name = 'asset.tag'

    name = fields.Char(string='Name')


class AssetAsset(models.Model):
    """
        Assets
    """
    _name = 'asset.asset'
    _rec_name = 'asset_number'
    _description = 'Asset'
    _inherit = ['mail.thread']
    _order = 'creation_date desc'

   
    def name_get(self):
        result = []
        for asset in self:
            asset_name = '[%s] %s' % (
                asset.serial, asset.brands.brand) if asset.serial else asset.brands
            result.append((asset.id, asset_name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        recs = self.search([('serial', operator, name), ('brand', operator, name)] + args, limit=limit)
        return recs.name_get()

    CRITICALITY_Selection = [
        ('0', 'General'),
        ('1', 'Important'),
        ('2', 'Very important'),
        ('3', 'Critical')
    ]

    STATE_Selection = [
        ('draft', 'Draft'),
        ('ready', 'Ready'),
        ('transfer', 'In Transfer'),
        ('available', 'Available'),
        ('hold', 'Hold'),
        ('allocated', 'Allocated'),
        ('lost', 'Lost'),
        ('sold', 'Sold'),
        ('repair', 'Repair'),
        ('scrapped', 'Scrapped'),
    ]

    name = fields.Char('Asset Name')
    property_stock_asset = fields.Many2one('stock.location', 'Asset Location')
    active = fields.Boolean('Active', default=True)
    asset_number = fields.Char('Asset #', size=64)
    serial = fields.Char('Serial #', size=64)
    partner_id = fields.Many2one('res.partner', 'Vendor')
    manufacturer_id = fields.Many2one('res.partner', 'Manufacturer')
    start_date = fields.Date('Start Date')
    picking_id = fields.Many2one('stock.picking')
    purchase_date = fields.Date('Purchase Date')
    warranty_start_date = fields.Date('Warranty Start')
    warranty_end_date = fields.Date('Warranty End')
    asset_move_id = fields.One2many('asset.move', 'asset_id', "Move")
    remarks = fields.Char(string='Remarks')
    asset_type = fields.Many2one('asset.type', 'Asset Type')
    brands = fields.Many2one('asset.brand', 'Make/Brand')
    employee_id = fields.Many2one('hr.employee', string='Assigned to')
    state = fields.Selection(
        STATE_Selection, 'Status', readonly=True, copy=False,
        index=True, track_visibility='onchange', default='draft')
    department_id = fields.Many2one(
        'hr.department', 'Department', readonly=True)
    specifications = fields.Text('Specifications')
    # service_area_id = fields.Many2one(
    #     'hr.employee.service.area', string="Service Area")
    mobile_no = fields.Char('Mobile Number', size=10)
    description = fields.Char('Asset Description', compute="add_description")
    model_no = fields.Many2one('asset.model', 'Model No')
    brand = fields.Boolean('Brand')
    model = fields.Boolean('Model')
    mobile = fields.Boolean('Mobile')
    creation_date = fields.Datetime(
        'Creation Date', default=fields.Datetime.now)
    product_id = fields.Many2one('product.product', 'Product')
    stock_scrap = fields.Boolean()
    
    #compute description
   
    def add_description(self):
        for val in self:
            if (val.serial and  val.brands.brand and val.model_no.model_no):
                val.description = str(val.model_no.model_no) + "<< " + str(val.brands.brand) + "<< " + str(val.serial)
            elif (val.serial and  val.brands.brand and not val.model_no.model_no):
                val.description = str(val.brands.brand) + "<< " + str(val.serial)
            elif (val.serial and  not val.brands.brand and val.model_no.model_no):
                val.description = str(val.model_no.model_no)+" << "+str(val.serial)
            else:
                val.description = str(val.serial)

   
    def unlink(self):
        """Allows to delete assets in draft,cancel states"""
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                raise UserError(
                    _("Invalid Action!\nCannot delete a Asset which is in state '%s'." % (rec.state)))
        return super(AssetAsset, self).unlink()

    @api.onchange('asset_type')
    def onchange_asset_type(self):
        if self.asset_type:
            self.update({
                'brand': self.asset_type.brand,
                'model': self.asset_type.model,
                'mobile': self.asset_type.mobile,
            })
            return

   
    def _get_asset_move_dic(self):
        """Return the generic asset move dictionary."""
        current_date = fields.Datetime.now()
        res = {
            'asset_id': self.id,
            'date': current_date,
            'executed_by': self.env.user.id,
            'asset_name': self.name,
            'asset_serial': self.serial,
            'asset_number': self.asset_number,
        }
        if 'asset_move_action' in self.env.context:
            res['action'] = self.env.context['asset_move_action']
        return res

    @api.model
    def create(self, vals):
        vals['asset_number'] = self.env['ir.sequence'].next_by_code(
            'asset.serial.num') or _('New')
        return super(AssetAsset, self).create(vals)

   
    def button_ready(self):
        self.ensure_one()
        self.env['asset.move'].create({
            'asset_id': self.id,
            'date': fields.Datetime.now(),
            'executed_by': self.env.user.id,
            'action': 'ready',
            'asset_name': self.name,
            'asset_serial': self.serial,
            'asset_number': self.asset_number,
        })
        return self.write({'state': 'ready'})

   
    def button_draft(self):
        self.ensure_one()
        self.env['asset.move'].create({
            'asset_id': self.id,
            'date': fields.Datetime.now(),
            'executed_by': self.env.user.id,
            'action': 'draft',
            'asset_name': self.name,
            'asset_serial': self.serial,
            'asset_number': self.asset_number,
        })
        return self.write({'state': 'available'})

   
    def button_scrapped(self):
        self.ensure_one()
        self.env['asset.move'].create({
            'asset_id': self.id,
            'date': fields.Datetime.now(),
            'executed_by': self.env.user.id,
            'action': 'scrapped',
            'asset_name': self.name,
            'asset_serial': self.serial,
            'asset_number': self.asset_number,
        })
        return self.write({'state': 'scrapped'})

   
    def button_hold(self):
        self.ensure_one()
        self.env['asset.move'].create({
            'asset_id': self.id,
            'date': fields.Datetime.now(),
            'executed_by': self.env.user.id,
            'action': 'hold',
            'asset_name': self.name,
            'asset_serial': self.serial,
            'asset_number': self.asset_number,
        })
        return self.write({'state': 'hold'})

   
    def button_lost(self):
        self.ensure_one()
        self.env['asset.move'].create({
            'asset_id': self.id,
            'date': fields.Datetime.now(),
            'executed_by': self.env.user.id,
            'action': 'lost',
            'asset_name': self.name,
            'asset_serial': self.serial,
            'asset_number': self.asset_number,
        })
        return self.write({'state': 'lost'})

   
    def button_sold(self):
        self.ensure_one()
        self.env['asset.move'].create({
            'asset_id': self.id,
            'date': fields.Datetime.now(),
            'executed_by': self.env.user.id,
            'action': 'sold',
            'asset_name': self.name,
            'asset_serial': self.serial,
            'asset_number': self.asset_number,
        })
        return self.write({'state': 'sold'})

   
    def button_repair(self):
        self.ensure_one()
        self.env['asset.move'].create({
            'asset_id': self.id,
            'date': fields.Datetime.now(),
            'executed_by': self.env.user.id,
            'action': 'repair',
            'asset_name': self.name,
            'asset_serial': self.serial,
            'asset_number': self.asset_number,
        })
        self.write({'state': 'repair'})
        return True

    def button_available(self):
        self.ensure_one()
        self.env['asset.move'].create({
            'asset_id': self.id,
            'date': fields.Datetime.now(),
            'executed_by': self.env.user.id,
            'action': 'available',
            'asset_name': self.name,
            'asset_serial': self.serial,
            'asset_number': self.asset_number,
        })
        return self.write({'state': 'available', 'employee_id': None})


class AssetTransfer(models.Model):
    """
        Assets Transfer
    """
    _name = 'asset.transfer'
    _rec_name = 'asset_number'
    _description = 'Asset Transfer'
    _inherit = ['mail.thread']
    _order = 'creation_date desc'

    STATE_Selection = [
        ('draft', 'Draft'),
        ('awaiting', 'Awaiting Receipt'),
        ('transferred', 'Transferred'),
        ('cancelled', 'Cancelled')
    ]

   
    def check_hrbp(self):
        """ Check HRBP """
        check = {}
        for rec in self:
            if rec.business_partner.id == self.env.uid and self.env.uid == 1:
                check[rec.id] = True
            else:
                check[rec.id] = False
        return check

   
    def check_admin(self):
        """ Check HRBP """
        check = {}
        for rec in self:
            if rec.business_partner.id == self.env.uid:
                check[rec.id] = True
            else:
                check[rec.id] = False
        return check

    asset_number = fields.Char('Transfer Asset #', size=64)
    transferred_by = fields.Many2one('res.users', 'Transferred By')
    received_by = fields.Many2one('res.users', 'Received By')
    transferred_date = fields.Datetime('Transfer Date')
    received_date = fields.Datetime('Received Date')
    # service_area_id = fields.Many2one(
    #     'hr.employee.service.area', string="Service Area")
    remarks = fields.Char(string='Remarks')
    business_partner = fields.Many2one(
        'res.users', 'Requesting User', default=lambda self: self.env.user)
    asset_transfer_ids = fields.One2many(
        'asset.asset.line', 'order_id', string='Asset Lines',
        states={'cancel': [('readonly', True)]}, copy=True)
    state = fields.Selection(
        STATE_Selection, 'Status', readonly=True, index=True, copy=False,
        track_visibility='onchange', default='draft')
    # 'check_hrbp': fields.function(check_hrbp, type="Boolean",
    #                               string="Check HRBP"),
    creation_date = fields.Datetime(
        'Creation Date', default=fields.Datetime.now())
    location_id = fields.Many2one('stock.location', 'Stock Location')
    # asset_transfer_id_hrbp = fields.One2many(
    #     'asset.asset.line', 'asset_transfer_id', string='Assets')
    # check_admin = fields.Boolean(_compute='check_admin', string="Check Admin")
    asset_ids = fields.Many2many(
        'asset.asset', 'asset_rel_id', 'transfer_relid',
        'asset_relid', 'Asset')

   
    def unlink(self):
        """Allows to delete assets in draft,cancel states"""
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                raise UserError(
                    _("Invalid Action!\nCannot delete a Asset which is in state '%s'." % (rec.state)))
        return super(AssetTransfer, self).unlink()

    # def onchange_service(self, cursor, user, ids, service_area_id, context=None):
    #     if not service_area_id:
    #         return True
    #     if service_area_id:
    #         stock_location = self.pool.get('stock.location')
    #         asset = self.pool.get('asset.asset')
    #         stock_location_id = stock_location.search(cursor, user, [
    #             ('service_area_id', '=', service_area_id),
    #             ('usage', '=', 'internal')],
    #             context=context)
    #         asset_id = asset.search(cursor, user, [
    #             ('state', '=', 'ready')],
    #             context=context)
    #     return {'value': {
    #         'location_id': stock_location_id[0] if stock_location_id else False,
    #         'asset_ids': [(6, 0, asset_id)]}
    #     }

   
    def button_available(self):
        move_id = self.env['asset.move']
        flag = 'available'
        self.env.context['asset_move_action'] = flag
        dic = self._get_asset_move_dic()
        move_id.create(dic)
        self.write({'state': 'available', 'employee_id': None})
        return True

   
    def button_confirm(self):
        current_date = fields.Datetime.now()
        sequence = self.env['ir.sequence'].next_by_code(
            'asset.transfer.number') or _('New')
        for asset in self.asset_transfer_ids:
            self.env['asset.move'].create({
                'asset_id': asset.asset_id.id,
                'date': current_date,
                'executed_by': self.env.user.id,
                'asset_serial': asset.asset_id.serial,
                'asset_number': asset.asset_id.asset_number,
                'action': 'transfer',
            })
            asset_id = asset.asset_id.write({'state': 'transfer'})
            asset.write({'check': True})
        self.write({'state': 'awaiting',
                    'transferred_by': self.env.user.id,
                    'transferred_date': current_date,
                    'asset_number': sequence})
        # ir_model_data = self.pool.get('ir.model.data')
        # template_obj = self.pool.get('email.template')
        # template_id = ir_model_data.get_object_reference('asset',
        #     'asset_transfer_process')[1]
        # if template_id:
        #     mail_id = template_obj.send_mail(
        #         cr, uid, template_id, record_id.id, force_send=True,
        #         context=context)
        return True

   
    def _create_stock_moves(self, order, asset_transfer_ids, picking_id=False):
        val = {}
        stock_move = self.env['stock.move']
        for asset in order.asset_transfer_ids:
            picking_obj = self.env['stock.picking.type'].search(
                [('code', '=', 'internal'),
                 ('default_location_src_id', '=', asset.asset_id.property_stock_asset.id)])
            
            val = {
                'product_uom_qty': 1,
                'state': 'done',
                'name': asset.asset_id.product_id.name,
                'product_id': asset.asset_id.product_id.id,
                'location_id': asset.asset_id.property_stock_asset.id,
                'location_dest_id': order.location_id.id,
                'product_uom': asset.asset_id.product_id.uom_id.id,
                'picking_type_id': picking_obj[0],
                'picking_id': picking_id
            }
            stock_id = self.env['stock.move'].create(val)

   
    def action_picking_create(self):
        record_id = self
        for order in record_id:
            for asset in order.asset_transfer_ids:
                picking_obj = self.env['stock.picking.type'].search(
                    [('code', '=', 'internal'),
                     ('default_location_src_id', '=', asset.asset_id.property_stock_asset.id)])
            picking_vals = {
                'picking_type_id': picking_obj[0],
                'service_area_id': order.service_area_id.id,
                'origin': order.asset_number,
                'usage': 'internal',
            }
            picking_id = self.env['stock.picking'].create(picking_vals)
            self._create_stock_moves(
                order, order.asset_transfer_ids, picking_id)

   
    def button_transfer(self):
        dic = {}
        current_date = datetime.now()
        record_id = self
        move_id = self.env['asset.move']
        # self.action_picking_create()
        for asset in record_id.asset_transfer_ids:
            dic = {
                'asset_id': asset.asset_id.id,
                'date': current_date,
                'executed_by': self.env.user.id,
                'asset_serial': asset.asset_id.serial,
                'asset_number': asset.asset_id.asset_number
            }
            if asset.receiving_status == 'received':
                asset_id = self.env['asset.asset'].write(
                    {'state': 'available'})
                dic['action'] = 'available'
            else:
                asset_id = self.env['asset.asset'].write({'state': 'ready'})
                dic['action'] = 'ready'
            move_id.create(dic)
        self.write(
            {'state': 'transferred',
             'received_by': record_id.business_partner.id,
             'received_date': current_date})
        return True

   
    def button_cancel(self):
        dic = {}
        current_date = datetime.now()
        record_id = self
        move_id = self.env['asset.move']
        for asset in record_id.asset_transfer_ids:
            dic = {
                'asset_id': asset.asset_id.id,
                'date': current_date,
                'executed_by': self.env.user.id,
                'asset_serial': asset.asset_id.serial,
                'asset_number': asset.asset_id.asset_number,
                'action': 'ready'
            }
            move_id.create(dic)
            asset_id = self.env['asset.asset'].write({'state': 'ready'})
        self.write(
            {'state': 'cancelled'})
        return True

   
    def button_draft(self):
        self.write(
            {'state': 'draft'})
        return True

    @api.onchange('asset_transfer_ids', 'asset_ids')
    def onchange_asset(self):
        res = {}
        data = []
        if self.asset_ids:
            for asset in self.asset_ids:
                data = list(asset)[-1]
        if self.asset_transfer_ids:
            for asset in self.asset_transfer_ids:
                rec = list(asset)
                if data and type(rec[-1]) != list:
                    list_rec = rec[-1].get('asset_id')
                    for data_list in data:
                        if data_list == list_rec:
                            if rec:
                                rec_id = rec[-1]
                                if rec_id:
                                    data.remove(rec_id.get('asset_id'))
                                    res['asset_ids'] = [(6, 0, data)]
        return {'value': res}


class AssetMove(models.Model):
    """
    Assets Move
    """
    _name = 'asset.move'
    _description = 'Asset Move'
    _order = 'date desc'
    _inherit = ['mail.thread']
    _rec_name = 'asset_name'

    ACTION_SELECTION = [
        ('ready', 'Ready'),
        ('transfer', 'In Transfer'),
        ('available', 'Available'),
        ('allocation', 'Allocation'),
        ('hold', 'Hold'),
        ('change', 'Changed'),
        ('exit', 'Exit'),
        ('scrapped', 'Scrapped'),
        ('sold', 'Sold'),
        ('repair', 'Under Repair'),
        ('lost', 'Lost')
    ]

    asset_id = fields.Many2one('asset.asset', 'Asset')
    date = fields.Datetime('Date')
    employee_id = fields.Many2one('hr.employee', 'Employee Name')
    action = fields.Selection(ACTION_SELECTION, 'Action')
    executed_by = fields.Many2one('res.users', 'Executed By')
    department_id = fields.Many2one('hr.department', 'Department')
    asset_name = fields.Char('Asset Name')
    asset_serial = fields.Char('Serial/Identification no.')
    asset_number = fields.Char('Asset #')

   
    def unlink(self):
        """Allows to delete assets in draft,cancel states"""
        for rec in self:
            raise UserError(
                _("Invalid Action!\nCannot delete a Asset in any state"))
        return super(AssetMove, self).unlink()
