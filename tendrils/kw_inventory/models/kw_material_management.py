# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp


class KwMaterialManagement(models.Model):
    _name = "kw_material_management"
    _description = "Material Management"
    _rec_name = "item_sequence"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'id desc'


    date = fields.Date(string='Date', default=fields.Date.context_today, required=True, track_visibility='always')
    add_product_items_ids = fields.One2many("kw_add_product_items", 'material_rel_id', string="Item Details", track_visibility='onchange')
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Pending', 'Pending'),
        ('Hold', 'Hold'),
        ('Approved', 'Approved'),
        ('Issued', 'Issued'),
        ('Cancelled', 'Cancelled'),
        ('Rejected', 'Rejected'),
        ('Released', 'Released')
    ], string='Status', readonly=True, index=True, copy=False, default='Draft', track_visibility='always')
    # pr_rel = fields.Many2one('kw_purchase_requisition', required=True, ondelete='cascade')
    # pr_req_no = fields.Char(string="Requisition No", related='pr_rel.requisition_number')
    # indnt_no = fields.Char(string="Indent Number", compute="show_indent")
    # indent_created = fields.Boolean(string='field_name', default=False)
    item_sequence = fields.Char(string="Sequence", default='New', readonly=1, track_visibility='always')
    dept_code = fields.Char(string="Department Code", default=lambda self: self.env.user.employee_ids.department_id.name)
    employee_id  = fields.Many2one('hr.employee',string='Employee',track_visibility='always', default=lambda self: self.env.user.employee_ids.id)
    department_id = fields.Many2one('hr.department', string="Department",track_visibility='always',default=lambda self: self.env.user.employee_ids.department_id.id)
    division_id  = fields.Many2one('hr.department',string='Division',track_visibility='always', default=lambda self: self.env.user.employee_ids.division.id)
    section_id  = fields.Many2one('hr.department',string='Section',track_visibility='always', default=lambda self: self.env.user.employee_ids.section.id)
    practice_id  = fields.Many2one('hr.department',string='Practice',track_visibility='always', default=lambda self: self.env.user.employee_ids.practise.id)
    branch_id  = fields.Many2one('kw_res_branch',string='Branch',track_visibility='always', default=lambda self: self.env.user.employee_ids.job_branch_id.id)
    pending_at  = fields.Many2one('hr.employee',string='Pending At',track_visibility='always')
    remark = fields.Text(string="Remark",track_visibility='always')
    is_available = fields.Boolean(string='Is available',compute='get_availablity_status')
    # requition_id  = fields.Many2one('kw_purchase_requisition',string='Requisition id', compute='get_requisition_id')
    pending_at_users    = fields.Char(string="Pending At",compute='_compute_pending_at')
    requirement_type = fields.Selection([
        ('treasury', 'Treasury'),
        ('project', 'Project'),
    ], string='Requirement Type',default='treasury',track_visibility='onchange')
    project_code    = fields.Char(string="Project Code")
    material_log = fields.One2many('kw_material_management_log','material_id')
    
    
    @api.depends('pending_at')
    def _compute_pending_at_users(self):
        for rec in self:
            if rec.state =='Pending':
                rec.pending_at_users = rec.pending_at_users.name if rec.pending_at_users else False
            elif rec.state == 'Approved':
                emp_data = rec.env['res.users'].sudo().search([])
                store_manager = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_store_manager') == True)
                # print("store manager=====================",store_manager)
        
                rec.pending_at_users = ','.join(store_manager.mapped('name'))if store_manager else False

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(KwMaterialManagement, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,submenu=submenu)
    #     if toolbar:
    #         print("toolbar-------",toolbar)
    #         for action in res['toolbar'].get('action'):
    #             print("action======",action)
    #             if action.get('xml_id'):
    #                 hide_id = self.env.ref("kw_inventory.requisition_report_view_tree").id
    #                 print("hide_id====",hide_id)
    #                 if action['xml_id'] == hide_id and self._context.get('hide_quotation') == True:
    #                     res['toolbar']['action'].remove(action)
    #     return res

    @api.depends('add_product_items_ids')
    def get_availablity_status(self):
        data = self.add_product_items_ids.filtered(lambda x:x.status in ['Requisition_Approved','Indent_Created','Quotation_Created','PO_Created'])
        if data:
            self.is_available = True
        else:
            self.is_available = False
    
    # @api.depends('add_product_items_ids')
    # def get_requisition_id(self):
    #     for rec in self:
    #         data = self.env['kw_purchase_requisition'].sudo().search([('material_id','=',rec.id)], order='id desc', limit=1)
    #         rec.requition_id = data.id

    @api.model
    def create(self, vals):
        if vals.get('item_sequence', 'New') == 'New':
            vals['item_sequence'] = self.env['ir.sequence'].next_by_code('kw_product_item_sequence') or '/'
        self.env.user.notify_success(message='Material Request created successfully.')
        return super(KwMaterialManagement, self).create(vals)
    
    @api.multi
    @api.depends('item_sequence','add_product_items_ids')
    def _get_status(self):
        for record in self:
            # print("method called of get status==========================")
            approv = []
            reject = []
            draf = []
            on_hold = []
            released=[]
            if record.add_product_items_ids:
                for rec in record.add_product_items_ids:
                    if rec.status == 'Draft':
                        draf.append(rec.status)
                    if rec.status == 'Approved':
                        approv.append(rec.status)
                    if rec.status == 'Rejected':
                        reject.append(rec.status)
                    if rec.status == 'Hold':
                        on_hold.append(rec.status)
                    if rec.status == 'Released':
                        released.append(rec.status)
                        # print("inside first if of hold=====================",on_hold)
                if len(record.add_product_items_ids) == len(draf):
                    # print(len(draf))
                    record.status = 'Pending'
                    record.state = 'Pending'
                if len(record.add_product_items_ids) == len(reject):
                    # print(len(reject))
                    record.status = 'Cancelled'
                    record.state = 'Cancelled'
                if len(record.add_product_items_ids) == len(approv):
                    # print(len(approv))
                    record.status = 'Issued'
                    record.state = 'Issued'
                if len(record.add_product_items_ids) == len(on_hold):
                    record.status = 'Hold'
                    record.state = 'Hold'
                if len(record.add_product_items_ids) == len(released):
                    record.status = 'Released'
                    record.state = 'Released'
                
                if len(draf) == 0 and len(on_hold) == 0 and len(approv) > 0 and len(reject) > 0:
                    record.status = 'Issued'
                    record.state = 'Issued'
    @api.multi
    def redirect_user_action(self):
        if not self.add_product_items_ids:
            raise ValidationError('Please add Items Details.')
        contxt = {'default_material_id':self.id}
        action = {
            'name': ' Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_material_management_user_remark',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context':contxt
        }
        if self._context.get('submit_material_request'):
            action['context'] = {'submit_material_request':True,'default_material_id':self.id}
            approve_form_view_id = self.env.ref("kw_inventory.kw_material_management_request_remark_form").id
            action['view_id'] = approve_form_view_id
        elif self._context.get('send_back_request'):
            action['context'] = {'send_back_request':True,'default_material_id':self.id}
            sendback_form_view_id = self.env.ref("kw_inventory.kw_material_management_sendback_remark_form_view").id
            action['view_id'] = sendback_form_view_id
        elif self._context.get('cancel_item_request'):
            action['context'] = {'cancel_item_request':True,'default_material_id':self.id}
            cancel_form_view_id = self.env.ref("kw_inventory.kw_material_management_cancel_remark_form_view").id
            action['view_id'] = cancel_form_view_id
        # print("action===",action)
        return action

    @api.multi
    def render_material_pending_actions(self):

        if self.env.user.has_group('kw_inventory.group_store_manager'):
            # print("--------inside iffffffffffffffff 1---------")
            tree_view_id = self.env.ref('kw_inventory.kw_materail_request_store_manager_view_tree').id
            form_view_id = self.env.ref('kw_inventory.kw_materail_request_store_manager_manager_form').id

            action = {
                    'type': 'ir.actions.act_window',
                    'name' : 'Pending Actions',
                    'views': [(tree_view_id, 'tree'),(form_view_id,'form')],
                    'view_mode': 'tree,form,search',
                    'res_model': 'kw_material_management',
                    'domain':[('state','not in',['Pending','Draft','Cancelled','Rejected'])],
                    'search_view_id': (self.env.ref('kw_inventory.kw_materail_request_store_manager_view_search').id,)
                    }
        else:
            # print("--------inside else 1---------")
            tree_view_id = self.env.ref('kw_inventory.kw_materail_request_take_action_view_tree').id
            form_view_id = self.env.ref('kw_inventory.kw_materail_request_take_action_manager_form').id
            action = {
                    'type': 'ir.actions.act_window',
                    'name' : 'Pending Action',
                    'views': [(tree_view_id, 'tree'),(form_view_id,'form')],
                    'view_mode': 'tree,form,search',
                    'res_model': 'kw_material_management',
                    'domain':[('pending_at.user_id','=',self.env.user.id),('state','in',['Pending'])],
                    'search_view_id': (self.env.ref('kw_inventory.kw_materail_request_sbu_view_search').id,)
                    }
        return action
    
    @api.multi
    def assign_pending_at(self):
        # print('=====================assign pending att called---------------======',self.employee_id.sbu_master_id,self.employee_id.division.manager_id,self.employee_id.department_id.manager_id)
        for rec in self:
        # check SBU
            if rec.state == 'Pending':
                if self.employee_id.sbu_master_id.representative_id:
                    # print("--------compute 1---------")
                    self.pending_at = self.employee_id.sbu_master_id.representative_id.id
                # check Division head
                elif self.employee_id.division.manager_id:
                    # print("--------compute 2---------")
                    self.pending_at = self.employee_id.division.manager_id.id
                # check HOD
                else:
                    # print("--------compute 3---------")
                    self.pending_at = self.employee_id.department_id.manager_id.id
            elif rec.state == 'Approved':
                    emp_data = rec.env['res.users'].sudo().search([])
                    store_manager = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_store_manager') == True)
                    # print("store manager=====================",store_manager)
                    rec.pending_at = (store_manager.mapped('employee_ids.id'))[0] if store_manager else False
            
        
    
    @api.multi
    def redirect_hod_action(self):
        contxt = {'default_material_id':self.id}
        action = {
            'name': ' Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_material_management_hod_remark',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context':contxt
        }
        if self._context.get('submit_hod_approve'):
            action['context'] = {'submit_hod_approve':True,'default_material_id':self.id}
            approve_form_view_id = self.env.ref("kw_inventory.kw_material_management_hod_approve_remark_form_view").id
            action['view_id'] = approve_form_view_id
        elif self._context.get('submit_hod_reject'):
            action['context'] = {'submit_hod_reject':True,'default_material_id':self.id}
            reject_form_view_id = self.env.ref("kw_inventory.kw_material_management_hod_reject_remark_form_view").id
            action['view_id'] = reject_form_view_id
        return action



    @api.multi
    def s_manager_action_item(self):
        if self._context.get('store_manager_assign') or self._context.get('store_manager_reject'):
            query = False
            contxt = {'default_material_id':self.id}
            action = {
                    'name': ' Remark',
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_material_management_store_management_remark',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'new',
                    'context':contxt,
                }
            # restrict assign if any item is in hold
            hold_data = self.add_product_items_ids.filtered(lambda x: x.status == 'Hold')
            if hold_data:
                raise ValidationError("Some line items are on hold. Please unhold to Approve/Reject.")
            if self._context.get('store_manager_assign'):
                item_data = self.add_product_items_ids.filtered(lambda x: not x.stock_master_id and x.status == 'Approved' and x.check_availability != 'not_available')
                if item_data:
                    raise ValidationError("Please select items.")
                notavailble_items = self.add_product_items_ids.filtered(lambda x: not x.stock_master_id and x.status == 'Approved' and x.check_availability == 'not_available')
                if notavailble_items:
                    raise ValidationError("You cannot assign, as the items are not-available.Either reject the line items or create requisition.")
                item_issued_data = self.add_product_items_ids.filtered(lambda r:r.stock_master_id.is_issued ==True)
                if item_issued_data:
                    message = ""
                    message_new = "The Following Items : " + "\n"
                    message += "Item Code - " + str(', '.join(item_issued_data.mapped('stock_master_id.serial_key'))) + " has already asigned," + "\n" + "Please select a different item."
                    self.message = message_new + message
                    # print("inside item_issued_data==============================")   
                    store_manager_validation_view_id = self.env.ref("kw_inventory.kw_material_management_store_manager_dynamic_validation_view").id
                    
                    action = {
                            'name': ' Remark',
                            'type': 'ir.actions.act_window',
                            'res_model': 'kw_material_management_store_management_remark',
                            'view_mode': 'form',
                            'view_type': 'form',
                            'target': 'new',
                            'view_id':store_manager_validation_view_id,
                            'context':{'default_message': self.message}
                            
                        }
                    # print("action==================",action)
                    return action
                # self.write({"state":'Issued'})
                # non_rejected_data = self.add_product_items_ids.filtered(lambda x: x.status =='Approved')
                # query = f"update kw_add_product_items set status='Issued' where id in ({str(non_rejected_data.ids)[1:-1]})"
                action['context'] = {'store_manager_assign':True,'default_material_id':self.id}
                store_manager_approve_form_view_id = self.env.ref("kw_inventory.kw_material_management_store_manager_assign_remark_form_view").id
                action['view_id'] = store_manager_approve_form_view_id
            if self._context.get('store_manager_reject'):
                action['context'] = {'store_manager_reject':True,'default_material_id':self.id}
                store_manager_reject_form_view_id = self.env.ref("kw_inventory.kw_material_management_store_manager_reject_remark_form_view").id
                action['view_id'] = store_manager_reject_form_view_id
            if query:
                self._cr.execute(query)
            return action
        non_rejected_data = self.add_product_items_ids.filtered(lambda x: x.is_rejected ==False and x.status not in ['PO_Created','Requisition_Approved','Quotation_Created','Indent_Created'])
        if self._context.get('store_manager_hold'):
            self.write({"remark":f'On Hold by {self.env.user.employee_ids.name}',"state":'Hold'})
            query = f"update kw_add_product_items set status='Hold' where id in ({str(non_rejected_data.ids)[1:-1]})"
            self._cr.execute(query)
        elif self._context.get('store_manager_unhold'):
            self.write({"remark":f'Un Hold by {self.env.user.employee_ids.name}',"state":'Approved'})
            query = f"update kw_add_product_items set status='Approved' where id in ({str(non_rejected_data.ids)[1:-1]})"
            self._cr.execute(query)
        else:
            pass
    
    @api.multi
    def s_manager_take_action(self):
        available_count_dict = {} 
        
        for rec in self.add_product_items_ids:
            product_id = rec.item_code.id 

            if rec.product_type!='service':
                store_data_count = self.env['stock.quant'].search_count([
                ('product_id', '=', product_id),
                ('is_issued', '=', False),
                ('process_location', '=', 'store')])
                
            
                # print("inside serice===================",store_data_count)
                if store_data_count > 0:
                    if product_id not in available_count_dict:
                        # print("inside 1st if of store===================")
                        
                        available_count_dict[product_id] = 0
                    
                    if available_count_dict[product_id] < store_data_count:
                        # print("inside 2nd if of store===================")
                        
                        rec.write({'check_availability': 'available'})
                        available_count_dict[product_id] += 1
                    else:
                        # print("inside else===================")
                        rec.write({'check_availability': 'not_available'})
                else:
                    rec.write({'check_availability': 'not_available'})
            else:
                service_data_count = self.env['kw_service_register'].search_count([
                ('product_code', '=', product_id),
                ('is_issued', '=', False)])
                if service_data_count > 0:
                    if product_id not in available_count_dict:
                        available_count_dict[product_id] = 0
                    
                    if available_count_dict[product_id] < service_data_count:
                        rec.write({'check_availability': 'available'})
                        available_count_dict[product_id] += 1
                    else:
                        rec.write({'check_availability': 'not_available'})
                else:
                    rec.write({'check_availability': 'not_available'})
           

        store_manager_form = self.env.ref("kw_inventory.kw_materail_request_store_manager_manager_form").id
        action = {
                    'name': ' Take Action',
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_material_management',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'view_id':store_manager_form,
                    'target': self,
                    'res_id':self.id,
                    'flags':{'mode':'edit'},
                }
        return action

    @api.constrains('add_product_items_ids')
    def check_duplicate_items(self):
        query = f"select stock_master_id from  kw_add_product_items where material_rel_id = {self.id} AND stock_master_id is not null and status != 'Released' "
        self._cr.execute(query)
        row = self._cr.fetchall()
        for rec in list(set(row)):
            if row.count((rec)) >=2:
                raise ValidationError("You cannot assign same item multiple times")
    
    @api.multi
    def redirect_request_requisition(self):
        # print("redirected------")
        req_form = self.env.ref("kw_inventory.kw_purchase_requisition_view_form").id
        data = []
        unique_product = self.add_product_items_ids.mapped('item_code')
        for rec in unique_product:
            query = f"select a.item_code,b.name,a.uom,a.quantity_required,a.expected_days,a.remark from kw_add_product_items a join product_template b on a.product_template_id=b.id where a.item_code = {rec.id} and a.material_rel_id = {self.id} limit 1"
            self._cr.execute(query)
            row = self._cr.fetchall()
            # print("row==========================",row)
            data.append((0,0, {'item_code':row[0][0],'item_description':row[0][1],
                        'uom':row[0][2],'quantity_required':row[0][3],
                        'expected_days':row[0][4],'status':'Draft',
                        'remark':''}))
        # for rec in self.add_product_items_ids[0]:
        #     data = {'item_code':rec.item_code.id,'item_description':rec.item_code.name,
        #     'uom':rec.uom,'quantity_required':rec.quantity_required,
        #     'expected_days':rec.expected_days,'status':'Draft',
        #     'remark':rec.remark}                              
        # print("dat====",data)
        action = {
                    'name': 'Purchase Requisition',
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_purchase_requisition',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'view_id':req_form,
                    'target': self,
                    'flags':{'mode':'edit'},
                    'context':{'default_material_id':self.id,'default_add_product_rel':data},
                }
                # 'context':{'default_material_id':self.id,'default_add_product_items_ids':[[(6,0,{'item_code':rec.item_code.id,'item_description':rec.item_code.name,
                #                                                                                      'uom':rec.uom,'quantity_required':rec.quantity_required,
                #                                                                                      'expected_days':rec.expected_days,'status':'Draft',
                #                                                                                      'remark':rec.remark})] for rec in self.add_product_items_ids]},
        res_id = self.env['kw_purchase_requisition'].sudo().search([('material_id','=',self.id)],order='id desc',limit=1)
        # print("res_id===",res_id)
        if res_id:
            action['res_id'] = res_id.id
        return action

    @api.multi
    def view_purchase_requisition(self):
        req_tree = self.env.ref("kw_inventory.kw_approved_requisition_view_tree").id
        req_form = self.env.ref("kw_inventory.kw_approved_requisition_view_form").id
        filtered_data = self.add_product_items_ids.filtered(lambda x: x.status == 'Requisition_Approved' and x.material_rel_id.id == self.id)
        action = {
                    'name': 'Approved Requisition',
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_requisition_requested',
                    'view_mode': 'form',
                    'view_type': 'form',
                     'views': [(req_tree, 'tree'), (req_form, 'form')],
                    'target': self,
                    'domain':[('id','in',filtered_data.ids if filtered_data else [])]
                }
        return action
    
    # @api.multi
    # def check_hod_manager(self):
    #     # import pdb
    #     # pdb.set_trace()
    #     # contxt = {'default_material_id':self.id}
    #     action = {
    #         'name': 'Pending Actions',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'kw_material_management',
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'target': self,
    #         # 'context':contxt
    #     }  
    #     if self.env.user.has_group('kw_wfh.group_hr_hod'):
    #         hod_tree_view_id = self.env.ref("kw_inventory.kw_materail_request_take_action_view_tree").id
    #         action['view_id'] = hod_tree_view_id
    #     elif self.env.user.has_group('stock.group_stock_manager'):
    #         manager_tree_view_id = self.env.ref("kw_inventory.kw_materail_request_store_manager_view_tree").id
    #         action['view_id'] = manager_tree_view_id
    #     return action
    
    
    

class ProductMaterialInherit(models.Model):
    _inherit = "product.product"


    qty_available = fields.Float(
        'Quantity On Hand', compute='_compute_quantities', search='_search_qty_available',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Current quantity of products.\n"
             "In a context with a single Stock Location, this includes "
             "goods stored at this Location, or any of its children.\n"
             "In a context with a single Warehouse, this includes " 
             "goods stored in the Stock Location of this Warehouse, or any "
             "of its children.\n"
             "stored in the Stock Location of the Warehouse of this Shop, "
             "or any of its children.\n"
             "Otherwise, this includes goods stored in any Stock Location "
             "with 'internal' type.")
    product_code = fields.Char('Product Code')
    salvage_value = fields.Float(string="Residual Percentage(%)" )
    

    def _compute_quantities(self):
        for rec in self:
            product_record =self.env['stock.quant'].search_count([('product_id','=',rec.id),('is_issued','=',False),('process_location','=','store')])
            # print("product record========",product_record)
            if product_record:
                rec.qty_available = product_record
            else:
                rec.qty_available = 0
    
    @api.constrains('salvage_value')
    def check_salvage_value(self):
        if self.salvage_value and (self.salvage_value > 100 or self.salvage_value < 0):
            raise ValidationError("Please select Residual Percentage(%) between 1-100%.")

    

class InventoryResUsersInherited(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        user = super(InventoryResUsersInherited, self).create(vals)
        
        group_list = ['stock.group_stock_manager','stock.group_stock_user']
        for group in group_list:
            group_to_modify = self.env.ref(group)
            if user.id in group_to_modify.users.ids:
                group_to_modify.sudo().write({'users': [(3, user.id)]})
        
 
        return user
        
class MaterialManagementLog(models.Model):
    _name = "kw_material_management_log"
    _description = "Material Management Log"

    action_taken_on = fields.Date(string='Action Taken On',default=fields.Date.context_today)
    action_taken_by = fields.Many2one('hr.employee',string='Action Taken By')
    material_id = fields.Many2one('kw_material_management',string='Material Id')
    product_id = fields.Char(string="Product")
    action_remark = fields.Char(string='Remark')
    status = fields.Char(string='Status')

