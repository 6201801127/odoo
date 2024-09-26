# import re
from datetime import date , datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.http import request
import re
import uuid

class ProductAttributeValueInherit(models.Model):
    _inherit = 'product.attribute.value'
    _order = 'id desc'
    
    code = fields.Char(string='Code')

    @api.model
    def create(self, vals):
        last_code = self.env['product.attribute.value'].search([], order='id desc', limit=1).mapped('code')
        last_code = last_code[0] if last_code else 'false'
        
        generated_code = self.generate_next_code(last_code)
        vals['code'] = generated_code
        res = super(ProductAttributeValueInherit, self).create(vals)
        res.name =res.name.upper()
        return res
    
    @api.multi
    def write(self, vals):
        if 'name' in vals:
            vals['name'] = vals['name'].upper()
        res = super(ProductAttributeValueInherit, self).write(vals)
        return res

    def generate_next_code(self, last_code):
        code_options = []

        for i in range(100):
            code_options.append(f'{i:02d}')

        for i in range(10):
            for j in range(26):
                code_options.append(f'{i}{chr(ord("A") + j)}')

        for i in range(26):
            for j in range(26):
                code_options.append(f'{chr(ord("A") + i)}{chr(ord("A") + j)}')

        for i in range(26):
            for j in range(10):
                code_options.append(f'{chr(ord("A") + i)}{j}')

        if last_code not in code_options:
            return '00'  # Return '00' if last_code is not in code_options

        last_code_index = code_options.index(last_code)
        next_code_index = (last_code_index + 1) % len(code_options)

        next_code = code_options[next_code_index]
        return next_code




    
class ProductProductInheritInventory(models.Model):
    _inherit = "product.product"
    
    
    varient_description = fields.Text(string='Description')
    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking')], string="Tracking", help="Ensure the traceability of a storable product in your warehouse.", default='serial', required=True)
   
    @api.multi
    def generate_code(self):
        category_id = self.env['kw_product_category'].search([('base_code', '=', self.product_tmpl_id.type)], limit=1).name
        product_tmpl_data = self.product_tmpl_id.code
        spec_data = self.env['product.attribute.value'].browse(self.attribute_value_ids.ids).mapped('code')
        
        # Checking the specification values length which should be 3
        list_data = spec_data[:3] + ['00'] * (3 - len(spec_data))
        
        spec_data_name = self.env['product.attribute.value'].browse(self.attribute_value_ids.ids).mapped('name')
        consolidated_data = f"{product_tmpl_data}{''.join(list_data)}"
        consolidated_name = f"{self.product_tmpl_id.name} {' '.join(spec_data_name)} "

        
        if consolidated_data:
            self.default_code = consolidated_data
        if consolidated_name:
            self.varient_description =consolidated_name
            
    @api.constrains('type')
    def check_product_type(self):
        if self.type == 'consu' or self.type == 'product':
            raise ValidationError('This product type is not in use,please choose another.')


            
            
    @api.multi
    def write(self, vals):
        # print("values",vals)
        if 'tracking' in vals and vals['tracking'] == 'lot':
                raise ValidationError('Tracking with Lot No is disabled.Please select Tacking by unique serial no.')
        return super(ProductProductInheritInventory, self).write(vals)
    
    def action_open_quants(self):
        self.env['stock.quant']._merge_quants()
        self.env['stock.quant']._unlink_zero_quants()
        action = self.env.ref('stock.product_open_quants').read()[0]
        action['domain'] = [('product_id', '=', self.id),('is_issued','=',False),('process_location','=','store')]
        action['context'] = {'search_default_internal_loc': 1}
        return action


class KwAddProductItems(models.Model):
    _name = 'kw_add_product_items'
    _description = "Purchase Requisition"
    _rec_name = 'sequence'
    _order = 'id desc'
    
    
    
    def default_employee(self):
        return self.env.user.employee_ids.id
    
    def get_child_employees(self):
        return [('id', 'child_of', self.env.user.employee_ids.ids)]
    
    def get_alternate_requisition_item_domain(self):
        if self._context.get('alternate_requisition_item'):
            domain = [('id', 'in', self._context.get('alternate_requisition_item'))]
            return domain
        
    def _default_access_token(self):
        return uuid.uuid4().hex
    
    access_token = fields.Char('Token', default=_default_access_token)
    sequence = fields.Char(string="Sequence", default='New', readonly=1, track_visibility='always')
    item_code = fields.Many2one('product.product', string="Item Code", required=True)
    item_description = fields.Char(string="Item Description")
    uom = fields.Char(string="Unit Of Measurement", required=True)
    quantity_required = fields.Float(string="Quantity", default=1)
    expected_days = fields.Date(string="Required Date" ,default=fields.Date.context_today)
    delivery_date = fields.Date(string="Delivery Date")
    material_rel_id = fields.Many2one('kw_material_management', required=True, ondelete='cascade')
    quotation_id = fields.Many2one('kw_quotation')
    quotation_consolidation_id = fields.Many2one('kw_quotation_consolidation')
    material_sequence = fields.Char(string="Requisition No", related='material_rel_id.item_sequence')
    status = fields.Selection(string='Status',selection=[ ('Draft', 'Draft'),
        ('Pending', 'Pending'),
        ('Hold', 'Hold'),
        ('Approved', 'Approved'),
        ('Cancelled', 'Cancelled'),
        ('Rejected', 'Rejected'),
        ('Issued', 'Issued'),
        ('Released', 'Released'),
        ],default='Draft',track_visibility='always')
    order_status = fields.Selection(string='Order Status',selection=[ 
        ('Draft', 'Draft'),
        ('Requisition_Approved', 'Requisition'),
        ('Approved', 'Requisition Approved'),
        ('Indent_Created', 'Indent'),
        ('Quotation_Created', 'Quotation'),
        ('Negotiation', 'Negotiation'),
        ('PO_Created', 'PO'),
        ])
    order_qty = fields.Float(string="Quantity Required",track_visibility='always')
    available_qty = fields.Float(string="Quantity Available", related='item_code.qty_available')
    remark = fields.Text(string="Remark")
    item_in_stock = fields.Integer(string='Item in Stock',force_save=True,Store=True)
    check_availability = fields.Selection(string='Type',selection=[('available', 'Available'), ('not_available', 'Not Available'), ('alternate', 'Alternate')])
    product_type = fields.Selection([
        ('service', 'Service/Licence'),('it', 'IT'),('nonit', 'Non-IT')],required=True)
    product_template_id = fields.Many2one("product.template",readonly=False,required=True)
    is_rejected = fields.Boolean(string='Is Rejected', default=False)
    alternate_name = fields.Many2one('product.product', string="Alternate Name")
    stock_master_id = fields.Many2one('stock.quant', string="Alternate Stock Material")
    service_master_id = fields.Many2one('kw_service_register', string="Service")
    employee_id = fields.Many2one('hr.employee',default=default_employee,domain = get_child_employees)
    requisition_remark= fields.Text(string="Requisition Remark")
    is_requisition_applied = fields.Boolean(string='Is Requisition Applied',default=False)
    action_on = fields.Date("Action On")
    action_taken_on = fields.Date("Released On")
    requisition_action_by = fields.Char(string='Requisition action by')
    quant_required = fields.Float("Quantity Required")
    quant_available= fields.Float("Quantity Available")
    alternate_requisition_item=fields.Many2one('product.product', string="Alternate Requisition Item", domain=get_alternate_requisition_item_domain)
    is_report_view = fields.Boolean(string='is report view', compute='_get_view_id')
    hold_time = fields.Datetime("Hold Time")
    duration = fields.Float(string='Hold Duration', compute='get_computed_time')
    user_request_qty = fields.Integer(string='User request Qty')
    project_code = fields.Char(string="Project Code")
    gatepass_type = fields.Selection([
        ('returnable', 'Returnable'),
        ('nonreturnable', 'Non-Returnable'),
    ], string='Gatepass Type',default='returnable',track_visibility='onchange')
    pending_at=fields.Char(string='Pending at')

    @api.multi
    @api.depends('hold_time')
    def get_computed_time(self):
        for record in self:
            if record.hold_time and record.status == 'Hold':
                record.duration = (datetime.now() - record.hold_time).total_seconds()/60/60
            else:
                record.duration = 0

    
    @api.depends('item_code')
    def _get_view_id(self):
        for rec in self:
            if self._context.get('hide_quotation'):
                request.session['hide_quotation'] = self._context.get('hide_quotation')
                rec.is_report_view = True
            else:
                rec.is_report_view = False
                request.session['hide_quotation'] = False


    @api.model
    def create(self,vals):
        vals['quant_required'] = int(vals['quantity_required']) if 'quantity_required' in vals else 0
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('add_product_item_sequence') or '/'
        if 'quantity_required' in vals:
            vals['user_request_qty'] = int(vals['quantity_required'])
        res = super(KwAddProductItems, self).create(vals)
        res.quant_available = res.item_code.qty_available
        return res
    
    @api.multi
    def write(self, vals): 
        if 'quantity_required' in vals:
            vals['user_request_qty'] = int(vals['quantity_required'])
        
        if 'user_request_qty' in vals and self.quantity_required < int(vals['user_request_qty']):
            raise ValidationError(f"Current quantity {int(vals['user_request_qty'])} can only be less or equal to the requested quantity {self.quantity_required}.")
        return super(KwAddProductItems, self).write(vals)
    
    
    @api.multi
    def action_create_quotation(self):
        if request.session['hide_quotation'] == True:
            raise ValidationError("Quotations are only created in approved requisition section")
        form_view_id = self.env.ref("kw_inventory.kw_material_request_quotation_wizard_view").id
        return{
            'name': 'Create Quotation',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_material_request_quotation_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new',
            'context':{'active_ids':self._context.get('active_ids')},
        }


    @api.constrains('quantity_required')
    def validate_qty_required(self):
        for record in self:
            if record.quantity_required <= 0:
                raise ValidationError("Quantity Required must be a positive number")
            
    @api.constrains('expected_days')
    def _check_past_date(self):
        today = date.today()
        for record in self:
            if record.expected_days and record.expected_days < today and not self._context.get('submit_hod_approve'):
                raise ValidationError('You can not select past date.')

    @api.onchange("item_code")
    def _set_description(self):
        for record in self:
            if record.item_code:
                record.item_description = record.item_code.varient_description
                record.uom = record.item_code.uom_id.name
                
                
    @api.onchange("check_availability")
    def check_availability_onchange(self):
        for record in self:
            record.stock_master_id = False
            record.alternate_name = False
            if record.check_availability == 'alternate':
                data = self.env['product.product'].sudo().search([('id', '=', self.product_template_id.product_variant_ids.ids),('id', '!=', self.item_code.id)])
                if data:
                    return {'domain': {'alternate_name': [('id','in',data.ids)]}}
                else: 
                    return {'domain': {'alternate_name': [('id','in',False)]}} 
               
                
        
    @api.onchange('product_type')
    def product_type_onchange(self):
        self.product_template_id = False
        self.item_code = False
        if self.product_type == 'service':
            return {'domain': {'product_template_id': [('type','=','service')]}}
        elif self.product_type == 'it':
            return {'domain': {'product_template_id': [('type','=','it')]}}
        elif self.product_type == 'nonit':
            return {'domain': {'product_template_id': [('type','=','nonit')]}}
        else:
            return {'domain': {'product_template_id': []}}

        
    @api.onchange('product_template_id')
    def product_template_id_onchange(self):
        self.item_code = False
        if self.product_template_id :
            return {'domain': {'item_code': [('id', '=', self.product_template_id.product_variant_ids.ids)]}}


    # @api.multi
    # def redirect_hold_item(self):
    #     form_view_id = self.env.ref("kw_inventory.kw_add_product_items_remark_hold_form_view").id
    #     self.hold_time = datetime.now()
    #     return {
    #         'name': ' Remark',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'kw_add_product_items',
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'res_id': self.id,
    #         'view_id': form_view_id,
    #         'target': 'new',
    #     }

    @api.multi
    def redirect_unhold_item(self):
        self.write({'status': 'Approved'})
        self.remark = ""
        if len(set(self.material_rel_id.add_product_items_ids.mapped('status'))) == 1:
            self.material_rel_id.write({'remark': self.remark, 'state': 'Approved'})

    # @api.multi
    # def give_hold_remark(self):
    #     self.write({'remark': self.remark, 'status': 'Hold'})
    #     if len(set(self.material_rel_id.add_product_items_ids.mapped('status'))) == 1:
    #         self.material_rel_id.write({'remark': self.remark, 'state': 'Hold'})
    #     emp_data = self.env['res.users'].sudo().search([])
    #     store_manager = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_store_manager') == True)
    #     store_manager_name = store_manager.mapped('name')[0]
    #     template_id = self.env.ref('kw_inventory.kw_material_management_hold_email_template')
    #     template_id.with_context(store_manager_name=store_manager_name).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")


    @api.multi
    def give_reject_remark(self):
        self.write({'remark':f'Remark by {self.env.user.employee_ids.name}-{self.remark}', 'status': 'Rejected','is_rejected':True,'item_in_stock':self.item_code.qty_available})
        self.material_rel_id.material_log.create({
                    "action_taken_by": self.env.user.employee_ids.id,
                    "material_id":self.material_rel_id.id ,
                    "product_id":self.item_code.name,
                    "action_remark": self.remark,
                    "status": 'Rejected',
                })
        emp_data = self.env['res.users'].sudo().search([])
        store_manager = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_store_manager') == True)
        store_manager_name = store_manager.mapped('name')[0]
        template_id = self.env.ref('kw_inventory.kw_material_management_reject_store_manager_template')
        template_id.with_context(store_manager_name=store_manager_name).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        # print("============================================",len(set(self.material_rel_id.add_product_items_ids.mapped('status'))))
        status_list = self.material_rel_id.add_product_items_ids.mapped('status')
        
        if len(set(status_list)) == 1:
            self.material_rel_id.write({'remark': self.remark, 'state': 'Rejected'})
        elif 'Issued' in list(set(status_list)) and 'Rejected' in list(set(status_list)) and len(set(status_list)) == 2:
            self.material_rel_id.write({'remark': self.remark, 'state': 'Issued'})


    @api.multi
    def give_approve_remark(self):
        self.write({'remark': self.remark, 'status': 'Issued'})
        self.material_rel_id.material_log.create({
                    "action_taken_by": self.env.user.employee_ids.id,
                    "material_id":self.material_rel_id.id ,
                    "product_id":self.item_code.name,
                    "action_remark": self.remark,
                    "status": 'Issued',
                })
        emp_data = self.env['res.users'].sudo().search([])
        store_manager = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_store_manager') == True)
        store_manager_name = store_manager.mapped('name')[0]
        template_id = self.env.ref('kw_inventory.kw_material_management_asigned_email_template')
        template_id.with_context(store_manager_name=store_manager_name).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        status_list = self.material_rel_id.add_product_items_ids.mapped('status')
        if len(set(status_list)) == 1:
            self.material_rel_id.write({'remark': self.remark, 'state': 'Issued'})
        elif 'Issued' in list(set(status_list)) and 'Rejected' in list(set(status_list)) and len(set(status_list)) == 2:
            self.material_rel_id.write({'remark': self.remark, 'state': 'Issued'})
        if self.product_type != 'service':
            query = f"update stock_quant set is_issued=True,status='Issued',material_ref_no='{self.material_rel_id.item_sequence}',department_id={self.employee_id.department_id.id},employee_id={self.employee_id.id},gatepass_type='{self.gatepass_type}',requirement_type='{self.material_rel_id.requirement_type}' where id = ({self.stock_master_id.id})"
            self._cr.execute(query)
        else:
            query = f"update kw_service_register set is_issued=True,status='Issued',material_ref_no={str(self.material_rel_id.item_sequence)},employee_id={self.employee_id.id} where id = ({self.service_master_id.id})"
            self._cr.execute(query)
        for rec in self:
            self.env['kw_product_assign_release_log'].create({
                "assigned_on":self.write_date,
                "products": rec.item_code.id,
                "quantity": rec.quantity_required,
                "assigned_to": rec.employee_id.id,
                "materil_id":rec.stock_master_id.id if rec.stock_master_id else False,
                "action_by": self.env.user.employee_ids.name,
                "status": 'Issued',
            })
        for rec in self:
            self.env['kw_stock_quant_log'].create({
                "assigned_on":self.write_date,
                "products": rec.item_code.id,
                "quantity": rec.quantity_required,
                "assigned_to": rec.employee_id.id,
                "material_id":rec.stock_master_id.id if rec.stock_master_id else False,
                "action_by": self.env.user.employee_ids.name,
                "status": 'Issued',
            })

    @api.multi
    def redirect_reject_item(self):
        form_view_id = self.env.ref("kw_inventory.kw_add_product_items_remark_reject_form_view").id
        return {
            'name': ' Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_add_product_items',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new',
        }

    @api.multi
    def redirect_approve_item(self):
        if not self.employee_id:
            raise ValidationError("Please Select Issue to")
        if self.product_type != 'service' and not self.stock_master_id:
            raise ValidationError("Please Select a Serial No")
        if self.product_type == 'service' and not self.service_master_id:
            raise ValidationError("Please Select a Service")
        form_view_id = self.env.ref("kw_inventory.kw_add_product_items_remark_approve_form_view").id
        return {
            'name': ' Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_add_product_items',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new',
        }

    
    @api.multi
    def create_material_requisition(self):
        self.status = 'Hold'
        self.hold_time = datetime.now()
        emp_data = self.env['res.users'].sudo().search([])
        store_manager = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_store_manager') == True)
        store_manager_name = store_manager.mapped('name')[0]
        template_id = self.env.ref('kw_inventory.kw_material_management_hold_email_template')
        template_id.with_context(store_manager_name=store_manager_name).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        self.write({'requisition_action_by':self.env.user.employee_ids.name,'is_requisition_applied':True,'action_on':self.write_date,'requisition_remark':f'Requisition Approved by {self.env.user.employee_ids.name}','order_qty':self.quantity_required})
        form_view_id = self.env.ref("kw_inventory.kw_add_product_items_create_requisition_form_view").id
        return {
            'name': ' Create Purchase Requisition',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_add_product_items',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new',
        }
    
    @api.multi
    def create_approve_requistion(self):
        emp_data = self.env['res.users'].sudo().search([])
        budget_head = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_dept_budget_head') == True)
        budget_head_id = budget_head.mapped('employee_ids')[0]
        budget_head_name = budget_head.mapped('name')[0]
        budget_head_email= budget_head.mapped('employee_ids.work_email')[0]
        budget_head_emp_code= budget_head.mapped('employee_ids.emp_code')[0]

        if self.quantity_required == 0:
            raise ValidationError("Order Quantity cannot be 0")
        
        """ Create Purchase requisition from store manager end """
        req_data = self.env['kw_purchase_requisition'].sudo().create({
                "department_name":self.employee_id.department_id.id if self.employee_id.department_id else False,
                "department_code":self.employee_id.department_id.code if self.employee_id.department_id else '',
                "indenting_department":self.employee_id.department_id.id if self.employee_id.department_id else False,
                "date":date.today(),
                "requirement_type":'treasury',
                "material_id":self.material_rel_id.id if self.material_rel_id else False,
                "state":"Pending",
                'pending_at':budget_head_name,
                'applied_by':self.env.user.employee_ids.id,
                "add_requisition_rel_ids":[(0,0,{
                                'requisition_applied_by':self.env.user.employee_ids.id,
                                'item_code':self.item_code.id if self.item_code else False,
                                'item_description':self.item_description if self.item_description else '',
                                'uom':self.uom if self.uom else '',
                                'quantity_required':self.order_qty if self.order_qty else self.quantity_required,
                                'expected_days':self.delivery_date if self.delivery_date else False,
                                'material_id':self.material_rel_id.id if self.material_rel_id else False,
                                'material_line_id':self.id,
                                'order_qty':self.order_qty if self.order_qty else 0,
                                'available_qty':self.available_qty if self.available_qty else 0,
                                'remark':self.remark if self.remark else '',
                                'item_in_stock':self.item_in_stock if self.item_in_stock else 0,
                                'check_availability':self.check_availability if self.check_availability else False,
                                'product_type':self.product_type if self.product_type else False,
                                'product_template_id':self.product_template_id.id if self.product_template_id else False,
                                'alternate_name':self.alternate_name.id if self.alternate_name else False,
                                'stock_master_id':self.stock_master_id.id if self.stock_master_id else False,
                                'employee_id':self.employee_id.id if self.employee_id else False,
                                'requisition_remark':self.requisition_remark if self.requisition_remark else '',
                                'action_on':self.action_on if self.action_on else False,
                                'action_taken_on':self.action_taken_on if self.action_taken_on else False,
                                'requisition_action_by':self.requisition_action_by if self.requisition_action_by else False,
                                'quant_available':self.quant_available if self.quant_available else 0,
                                'status':'Pending',
                                'pending_at':budget_head_id.id if budget_head_id else False,
                                'requirement_type':self.material_rel_id.requirement_type if self.material_rel_id.requirement_type else '',
                                'project_code':self.material_rel_id.project_code if self.material_rel_id.project_code else '',
                            })]
            })
        pending = budget_head_name + ': Req -' + req_data.requisition_number
        self.material_rel_id._get_status()
        self.write({"order_status":'Requisition_Approved','pending_at':pending,"remark":f'Requisition Created by {self.env.user.employee_ids.name}'})
        sequence_data =  self.env['kw_purchase_requisition'].sudo().search([('material_id','=',self.material_rel_id.id)],order='id desc',limit=1).mapped('requisition_number')
        materialview = self.env.ref('kw_inventory.kw_purchase_requisition_take_action_window')
        action_id = self.env['ir.actions.act_window'].search([('id', '=', materialview.id)], limit=1).id
        db_name = self._cr.dbname
        template_id = self.env.ref('kw_inventory.store_manager_purchase_requisition_email')
        template_id.with_context(active_id=self.env.context.get('active_id'),
                                 req_no= req_data.requisition_number,
                                dbname=db_name,
                                action_id=action_id,
                                token=self.access_token,
                                to_mail = budget_head_email,
                                user_name = budget_head_name,
                                user_code = budget_head_emp_code,
                                sequence_data=sequence_data[0]).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success(message='Purchase Requisition created successfully.')