# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date,datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.http import request

class kw_purchase_order_line(models.Model):
    _inherit = "purchase.order.line"

    receive_remark = fields.Char('Remark')
    receive_date = fields.Date('Date')
    status = fields.Selection(string=' Status',selection=[('pending', 'Pending'), ('received', 'Received'), ('returned', 'Returned')],default='pending')

    @api.multi
    def receive_products(self):
        view = self.env.ref('kw_inventory.product_receive_remark_view')
        return {
            'name': _('Confirmation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product_receive_remark',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': {'default_order_linel_id':self.id},
        }
    
    @api.multi
    def return_products(self):
        view = self.env.ref('kw_inventory.product_reject_remark_view')
        return {
            'name': _('Confirmation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product_receive_remark',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': {'default_order_linel_id':self.id},
        }

class StockQuantInherited(models.Model):
    _inherit = "stock.quant"
    _description = "Stock"
    _rec_name = "lot_id"
    # _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'id desc'


    serial_key = fields.Char('Serial No', required=True, default="New", readonly="1")
    user_company_id = fields.Many2one('res.company', 'Company', required=False,
                                 default=lambda self: self.env.user.company_id.id)
    employee_id = fields.Many2one('hr.employee', string="Issued To")
    product_id = fields.Many2one('product.product', string="Product")
    product_name = fields.Char(string="Name", related='product_id.name',store=True)
    material_type = fields.Selection(string=' Product Type',selection=[('consu', 'Consumable'), ('service', 'Service'), ('product', 'Product')],related='product_id.type', store=True)
    is_grn = fields.Boolean(string="GRN",default=False)
    is_issued = fields.Boolean(string="Issued",default=False)
    is_asset = fields.Boolean(string="Asset")
    active = fields.Boolean(string="Active", default=True)
    process_location = fields.Selection(string=' Operation Type',selection=[('vendor', 'Vendor'),('grn', 'GRN'), ('qc', 'QC'), ('store', 'Store')],default='vendor')
    sequence = fields.Integer(string='Sequence' ,readonly=True)
    location_id = fields.Many2one('stock.location', 'Location',auto_join=True, ondelete='cascade', required=False)
    quantity = fields.Float('Quantity', required=False, oldname='qty')
    reserved_quantity = fields.Float('Reserved Quantity',required=False)
    # serial_type = fields.Selection(selection=[('lot_serial', 'Lot/Serial'), ('fa', 'FA Code')],string='Serial Type',default='lot_serial')
    fa_code = fields.Char(string="FA Code")
    is_verified = fields.Boolean(string="Verified")
    is_gift = fields.Boolean(string="Gift")
    
    dept_id = fields.Many2one('stock_dept_configuration',string='Store')
    branch_id  = fields.Many2one('kw_res_branch',related='dept_id.branch_id',string='Location',track_visibility='always')
    status = fields.Selection(string='Status',selection=[ ('Draft', 'In Stock'),
        ('Issued', 'Issued'),
        ('Released', 'Released'),
        ('gift','Gifted')
        ],default='Draft',)
    asset_id = fields.Many2one('account.asset.asset',string='Asset', compute='get_stock_asset_id')
    gatepass_type = fields.Selection([
        ('returnable', 'Returnable'),
        ('nonreturnable', 'Non-Returnable'),
    ], string='Gatepass Type',track_visibility='onchange')
    requirement_type = fields.Selection([
        ('treasury', 'Treasury'),
        ('project', 'Project'),
    ], string='Requirement Type',track_visibility='onchange')
    department_id = fields.Many2one('hr.department',string='Issued Department')
    repair_damage = fields.Selection([
        ('repair', 'Sent to Repair'),
        ('repaired', 'Repaired'),
        ('damage', 'Damage'),
        ('e_waste', 'E-Waste'),
        ('other', 'Other'),
    ], string='Repair/Damage',track_visibility='onchange')
    price = fields.Float(string='Price')
    remark = fields.Text(string='Remark')
    repair_date = fields.Date('Repair Date')
    project_code = fields.Char(string='Project Code')
    age = fields.Float(string='Age(Yrs)',compute='compute_age')
    material_ref_no = fields.Char('Material Ref No')
    
    @api.depends('create_date')
    def compute_age(self):
        for rec in self:
            if rec.create_date:
                datetime_obj = datetime.strptime(str(rec.create_date),"%Y-%m-%d %H:%M:%S.%f")
                days = (date.today()-datetime_obj.date()).days
                year = days/365
                rec.age = year
        
    @api.depends('is_asset')
    def get_stock_asset_id(self):
        for rec in self:
            asset_id = self.env['account.asset.asset'].search([('stock_quant_id','=',rec.id)])
            if asset_id:
                rec.asset_id = asset_id.id

            
    @api.onchange('department_id')
    def _changes_in_environment(self):
        if self.department_id:
            emp_data = self.env['hr.employee'].sudo().search(
                [('department_id', '=', self.department_id.id)])
            return {'domain': {'employee_id': [('id', 'in', emp_data.ids if emp_data else [])], }}
    
    @api.model
    def render_assign_gatepass(self):
        view_id = self.env.ref('kw_inventory.kw_gatepass_assign_form').id
        return {
            'name': 'Assign Nonreturnable/Returnable Gatepass',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_gatepass_assign',
            'view_type': 'form',
            'view_mode': 'form',
            # 'views': [(view_id, 'form')],
            'target': 'new',
            'view_id': view_id,
        }
    
    @api.multi
    def update_serial_no(self):
        view_id = self.env.ref('kw_inventory.stock_production_lot_serialno_form').id
        return {
            'name': 'Take Action',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.production.lot',
            'res_id': self.lot_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'new',
            'view_id': view_id,
        }
    
    @api.multi
    def redirect_release_items(self):
        form_view_id = self.env.ref("kw_inventory.kw_stock_quant_remark_release_form_view").id
        return {
            'name': ' Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.quant',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new',
        }
    
    @api.multi
    def redirect_issue_repair_damage_view(self):
        form_view_id = self.env.ref("kw_inventory.kw_issue_repair_damage_wiz_form").id
        return {
            'name': ' Issue Items',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_issue_repair_damage_wiz',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
            'context': {"default_stock_id":self.id},
        }
    
    @api.multi
    def return_to_store(self):
        form_view_id = self.env.ref("kw_inventory.kw_gatepass_return_to_store_form").id
        return {
            'name': 'Return to store',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_gatepass_assign',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
            'context': {"default_stock_id":self.id},
        }
    @api.multi
    def return_details(self):
        tree_view_id = self.env.ref("kw_inventory.kw_product_repair_log_view_tree").id
        return {
            'name': 'Repair Details',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_product_repair_log',
            'res_id': self.id,
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': tree_view_id,
            'target': 'self',
            'domain': [('repair_id', '=', self.id)],
        }
    
    @api.multi
    def release_items(self):
        emp_data = self.env['res.users'].sudo().search([])
        store_manager = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_store_manager') == True)
        store_manager_name = store_manager.mapped('name')[0]
        emp_code=store_manager.mapped('employee_ids.emp_code')[0]
        template_id = self.env.ref('kw_inventory.material_release_item_email_template')
        # print("employe===============================================",self.employee_id)
        template_id.with_context(emp_code=emp_code,store_manager_name=store_manager_name,date=date.today()).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        self.write({"status":'Released','gatepass_type':'',"project_code":'','department_id':False,'requirement_type':'','employee_id':False,'is_issued':False,"action_taken_on":self.write_date,"remark":f'Released by {self.env.user.employee_ids.name}'})
        # print(jkfddddddddddddddd)
        query = f"update kw_add_product_items set status='Released' where stock_master_id = ({self.id})"
        self._cr.execute(query)
        self.env['kw_product_assign_release_log'].create({
            "assigned_on":self.write_date,
            "products": self.product_id.id,
            "quantity": self.quantity,
            "assigned_to": self.employee_id.id,
            "materil_id":self.id ,
            "action_by": self.env.user.employee_ids.name,
            "status": 'Released',
        })
        self.env.user.notify_success(message='Product released successfully.')

    
    @api.multi
    def verify_serial_no(self):
        for rec in self:
            if rec.is_gift:
                rec.write({"status": 'gift'})

        # if not self.dept_id:
        #     raise ValidationError('Please give Department')
        self.is_verified = True
        
    # @api.depends('is_gift','product_id')   
    # def _compute_is_asset(self):
    #     for rec in self:
    #         if rec.product_id.is_asset and not rec.is_gift:
    #             rec.is_asset=True
    #         else:
    #             rec.is_asset= False
                
            # if rec.is_gift:
    
    # @api.multi
    # def update_fa_code(self):
    #     view_id = self.env.ref('kw_inventory.stock_quant_facode_form').id
    #     return {
    #         'name': 'Take Action',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'stock.quant',
    #         'res_id': self.id,
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'views': [(view_id, 'form')],
    #         'target': 'new',
    #         'view_id': view_id,
    #     }
        
    @api.multi
    def create_asset_entry(self):
        product = self.product_id.product_tmpl_id.alias_name
        location = self.branch_id.alias
        asset_data = self.env['account.asset.asset'].sudo().search([('template_id','=',self.product_id.product_tmpl_id.id),('asset_owner_branch_id','=',self.branch_id.id)],order='id desc',limit=1).mapped('name')
        if asset_data:
            last_part = asset_data[0].split('/')[-1]
            next_number = int(last_part) + 1
            formatted_next_number = f'{next_number:04d}'
            sequence = 'CSM' + '/' + str(location) + '/' + str(product) + '/' + formatted_next_number
        else:
            sequence = 'CSM' + '/' + str(location) + '/' + str(product) + '/' + '0001'
        datetime_obj = datetime.strptime(str(self.create_date),"%Y-%m-%d %H:%M:%S.%f")
        days = (date.today()-datetime_obj.date()).days if datetime_obj else 0
        age_value = days/365 if days > 0 else 0
        view_id = self.env.ref('kw_inventory.view_account_asset_asset_new_form').id
        return {
            'name': sequence,
            'type': 'ir.actions.act_window',
            'res_model': 'account.asset.asset',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'self',
            'view_id': view_id,
            'context':{'default_stock_quant_id':self.id,'default_name':sequence,'default_value':self.price,'default_residual_percentage':self.product_id.salvage_value,'default_age':age_value}
        }
    
    @api.multi
    def view_asset_entry(self):
        view_id = self.env.ref('kw_inventory.view_account_asset_asset_new_form').id
        if self.asset_id:
            return {
                'name': 'Take Action',
                'type': 'ir.actions.act_window',
                'res_model': 'account.asset.asset',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'target': 'self',
                'view_id': view_id,
                'res_id':self.asset_id.id,
            }
    
    @api.multi
    def update_facode(self):
        action_id = self.env.ref('kw_inventory.action_stock_quant_approval').id
        return {
                    'type': 'ir.actions.act_url',
                    'tag': 'reload',
                    'url': f'/web#action={action_id}&model=stock.quant&view_type=list',
                    'target': 'self',
                }
    
    @api.model
    def create(self, values):
        if request.session['process_location']:
            values['process_location']=request.session['process_location']
        result = super(StockQuantInherited, self).create(values)
        if result.product_id:
            exist_material = self.env['stock.quant'].sudo().search([('product_id','=',result.product_id.id),('active','=',True),('sequence','!=',0)], order='sequence desc', limit=1)
            result.sequence , result.serial_key = self._get_material_sequence(result,exist_material)
        if result.lot_id:
            move_line_rec = self.env['stock.move.line'].sudo().search([('lot_id','=',result.lot_id.id)])
            move_line_store = move_line_rec.filtered( lambda x: x.location_dest_id.stock_process_location=='store')
            move_line_grn = move_line_rec.filtered( lambda x: x.location_dest_id.stock_process_location=='grn')
            if move_line_store:
                result.dept_id = move_line_store.move_id.store_id.id if move_line_store.move_id.store_id else False
                get_price = self.call_get_price(result.product_id,move_line_store.move_id.picking_id)
                if get_price:
                    result.price = get_price
            

        return result
    
    def call_get_price(self,product_id=False,picking_id=False):
        if product_id and picking_id:
            po_data = self.env['purchase.order'].sudo().search([('name','=',picking_id.origin)], limit=1)
            if po_data:
                product_line_rec = po_data.order_line.filtered(lambda x:x.product_id.id == product_id.id)
                if product_line_rec:
                    return product_line_rec.price_unit
            else:
                return False
            
    
    @api.multi
    def write(self, vals):
        # if 'employee_id' in vals:
        #     if vals['employee_id']:
        #         vals['is_issued'] = True
        #         vals['status'] = 'Issued'
        #     else:
        #         vals['is_issued'] = False
        #         vals['status'] = 'Released'

        if 'is_issued' in vals and 'status' in vals:
            assigned_to = vals.get('employee_id', False)
            log_data = {
                "assigned_on": self.write_date,
                "products": self.product_id.id,
                "quantity": self.quantity,
                "assigned_to": assigned_to,
                "material_id": self.id,
                "action_by": self.env.user.employee_ids.name,
                "status": vals['status'],
            }
            self.env['kw_stock_quant_log'].create(log_data)
            if self.asset_id:
                transfer_data = {
                    "assigned_on": self.write_date,
                    "products": self.product_id.id,
                    "quantity": self.quantity,
                    "assigned_to": assigned_to if assigned_to else self.employee_id.id,
                    "material_id": self.id,
                    "action_by": self.env.user.employee_ids.name,
                    "status": vals['status'],
                }
                self.asset_id.write({
                    'transfer_history_ids': [(0, 0, transfer_data)]
                })
        res = super(StockQuantInherited, self).write(vals)
        return res



    @api.multi
    def _get_material_sequence(self,result,exist_material):
        sequence,serial_key = 0,'New'
        if exist_material:
            sequence = exist_material.sequence + 1
            serial_key = result.product_id.code if result.product_id.code else '' + '/' + f"{(exist_material.sequence+1):03}"
            pass
        else:
            sequence = 1
            serial_key = result.product_id.code if result.product_id.code else '' + '/' + '001'
        return  sequence,serial_key
    
    @api.model
    def send_email_for_uncreated_fa(self):
        # print("inside scheduler==================")
        quants_without_fa = self.search([('status', '=', 'Issued'),('asset_id', '=', False)])
        # print("records fa============================",quants_without_fa)
        # Send email for each record
        for quant in quants_without_fa:
            self.send_email(quant)

    @api.model
    def send_email(self, quant):
        # print("inside send mail scghedulesr===================")
        emp_data = self.env['res.users'].sudo().search([])
        store_manager = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_store_manager') == True)
        store_manager_email = store_manager.mapped('email')[0]
        store_manager_name = store_manager.mapped('name')[0]
        emp_code=store_manager.mapped('employee_ids.emp_code')[0]
        template_id = self.env.ref('kw_inventory.reminder_email_template_uncreated_fa')
        template_id.with_context(emp_code=emp_code,store_manager_name=store_manager_name,store_manager_email=store_manager_email).send_mail(quant.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            
class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"
    # _rec_name = "serial_key"

    @api.multi
    def update_serailno(self):
        # print("method called==============================================")
        action_id = self.env.ref('kw_inventory.view_stock_quant_approval_tree').id
        return {
                    'type': 'ir.actions.act_url',
                    'tag': 'reload',
                    'url': f'/web#action={action_id}&model=stock.quant&view_type=list',
                    'target': 'self',
                }
class StockQuantLog(models.Model):
    _name = "kw_stock_quant_log"
    _description = "Stock Quant Log"

    products = fields.Many2one('product.product',string="Products/Items")
    quantity = fields.Integer(string='Product Qty')
    assigned_to = fields.Many2one('hr.employee',string='Assigned To')
    asset_id = fields.Many2one('account.asset.asset',string='Asset Id')
    assigned_on = fields.Date(string='Assigned/Released On')
    action_by = fields.Char(string='Action Taken By')
    status = fields.Selection([
        ('Issued', 'Assigned'),
        ('Released', 'Released')
    ], string='Status')
    material_id = fields.Many2one('stock.quant',string='Material Id')
    
