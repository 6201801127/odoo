from datetime import date , datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.http import request


class kwAddRequisitionItems(models.Model):
    _name = 'kw_add_requisition_items'
    _description = "A master model to add Requisition Items"
    _rec_name = 'sequence'
    _order = 'id desc'
    
    
    def default_employee(self):
        return self.env.user.employee_ids.id
    
    def get_alternate_requisition_item_domain(self):
        if self._context.get('alternate_requisition_item'):
            domain = [('id', 'in', self._context.get('alternate_requisition_item'))]
            return domain
    
    sequence = fields.Char(string="Sequence", default='New', readonly=1, track_visibility='always')
    item_code = fields.Many2one('product.product', string="Item Code", required=True)
    item_description = fields.Char(string="Item Description")
    uom = fields.Char(string="Unit Of Measurement", required=True)
    quantity_required = fields.Float(string="Quantity Required", default=1)
    expected_days = fields.Date(string="Required Date")
    quotation_id = fields.Many2one('kw_quotation')
    quotation_consolidation_id = fields.Many2one('kw_quotation_consolidation')
    requisition_rel_id = fields.Many2one('kw_purchase_requisition', required=True, ondelete='cascade')
    status = fields.Selection(string='Status',selection=[ ('Draft', 'Draft'),
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Cancelled', 'Cancelled'),
        ('Rejected', 'Rejected'),
        ],default='Draft')
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
    employee_id = fields.Many2one('hr.employee',default=default_employee)
    requisition_remark= fields.Text(string="Requisition Remark")
    action_on = fields.Date("Action On")
    action_taken_on = fields.Date("Released On")
    requisition_action_by = fields.Char(string='Requisition action by')
    quant_required = fields.Float("Quantity Required")
    quant_available= fields.Float("Quantity Available")
    alternate_requisition_item=fields.Many2one('product.product', string="Alternate Requisition Item", domain=get_alternate_requisition_item_domain)


    # @api.model
    # def create(self,vals):
    #     vals['quant_required'] = int(vals['quantity_required']) if 'quantity_required' in vals else 0
    #     res = super(kwAddRequisitionItems, self).create(vals)
    #     res.quant_available = res.item_code.qty_available
    #     res.sequence = res.requisition_rel_id.requisition_number
    #     return res
    
class kwRequisitionRequested(models.Model):
    _name = 'kw_requisition_requested'
    _description = "A master model to store all Requisition from both ends"
    _rec_name = 'sequence'
    _order = 'id desc'
    
    def default_employee(self):
        return self.env.user.employee_ids.id
    
    @api.multi
    def get_alternate_requisition_item_domain(self):
        if self._context.get('alternate_requisition_item') and self._context.get('item_code'):
            alternate_requisition_items = self._context.get('alternate_requisition_item')
            item_code_id = self._context.get('item_code')

            domain = [('id', 'in', alternate_requisition_items), ('id', '!=', item_code_id)]
            return domain
        else:
            return []

    
    sequence = fields.Char(string="Sequence", default='New', readonly=1, track_visibility='always')
    item_code = fields.Many2one('product.product', string="Item Code", required=True)
    item_description = fields.Char(string="Item Description")
    uom = fields.Char(string="Unit Of Measurement", required=True)
    quantity_required = fields.Float(string="Quantity Required", default=1)
    expected_days = fields.Date(string="Required Date")
    quotation_id = fields.Many2one('kw_quotation')
    quotation_consolidation_id = fields.Many2one('kw_quotation_consolidation')
    requisition_rel_id = fields.Many2one('kw_purchase_requisition', ondelete='cascade')
    requisition_rel_line_id = fields.Many2one('kw_add_requisition_items', ondelete='cascade')
    material_id = fields.Many2one('kw_material_management', ondelete='cascade')
    material_line_id = fields.Many2one('kw_add_product_items', ondelete='cascade')
    status = fields.Selection(string='Status',selection=[ ('Draft', 'Draft'),
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Quotation', 'Quotation Created'),
        ('Cancelled', 'Cancelled'),
        ('Rejected', 'Rejected'),
        ],default='Draft')
    order_qty = fields.Float(string="Quantity Required",track_visibility='always')
    available_qty = fields.Float(string="Quantity Available", related='item_code.qty_available')
    remark = fields.Text(string="Remark")
    item_in_stock = fields.Float(string='Item in Stock',force_save=True,Store=True)
    check_availability = fields.Selection(string='Type',selection=[('available', 'Available'), ('not_available', 'Not Available'), ('alternate', 'Alternate')])
    product_type = fields.Selection([
        ('service', 'Service/Licence'),('it', 'IT'),('nonit', 'Non-IT')],required=True)
    product_template_id = fields.Many2one("product.template",readonly=False,required=True)
    is_rejected = fields.Boolean(string='Is Rejected', default=False)
    alternate_name = fields.Many2one('product.product', string="Alternate Name")
    stock_master_id = fields.Many2one('stock.quant', string="Alternate Stock Material")
    employee_id = fields.Many2one('hr.employee',default=default_employee)
    pending_at = fields.Many2one('hr.employee')
    requisition_remark= fields.Text(string="Requisition Remark")
    action_on = fields.Date("Action On")
    action_taken_on = fields.Date("Released On")
    requisition_action_by = fields.Char(string='Requisition action by')
    quant_required = fields.Float("Quantity Required")
    quant_available= fields.Float("Quantity Available")
    alternate_requisition_item=fields.Many2one('product.product', string="Alternate Requisition Item", domain=get_alternate_requisition_item_domain)
    requirement_type = fields.Selection([
            ('treasury', 'Treasury'),
            ('project', 'Project'),
        ], string='Requirement Type',track_visibility='onchange')
    project_code = fields.Char(string="Project Code")
    requisition_applied_by=fields.Many2one("hr.employee",string='Requisition raised by')

    @api.constrains('quantity_required')
    def validate_qty_required(self):
        for record in self:
            if record.quantity_required == 0:
                raise ValidationError("Quantity cannot be 0")
            
    @api.constrains('expected_days')
    def _check_past_date(self):
        today = date.today()
        for record in self:
            if record.expected_days and record.expected_days < today:
                raise ValidationError('You can not select past date.')

    @api.onchange("item_code")
    def _set_description(self):
        for record in self:
            if record.item_code:
                record.item_description = record.item_code.varient_description
                record.uom = record.item_code.uom_id.name
                
    @api.onchange("item_code")
    def type_count_on_variants_onchange(self):
        for record in self:
            if record.item_code and record.item_code.qty_available > 0:
                record.check_availability = 'available'
            if record.item_code and record.item_code.qty_available == 0:
                record.check_availability = 'not_available'
                
    @api.onchange("check_availability")
    def check_availability_onchange(self):
        for record in self:
            if record.check_availability == 'alternate':
                return {'domain': {'alternate_name': [('id', '=', self.product_template_id.product_variant_ids.ids),('id', '!=', self.item_code.id)]}} 
                       
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

    @api.multi
    def edit_approved_requisition(self):
        data = {
                'type': 'ir.actions.act_window',
                'res_model': 'kw_requisition_requested',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                'target': 'self',
                'context': {'alternate_requisition_item':self.product_template_id.product_variant_ids.ids,'item_code':self.item_code.id},
                'flags': {'mode': 'edit'},
            }
        if self._context.get('hod_action'):
            data['name']='Pending Actions'
            data['view_id']=self.env.ref("kw_inventory.kw_hod_requisition_view_form").id
        else:
            data['name']='Approved Requisitions'
            data['view_id']=self.env.ref("kw_inventory.kw_approved_requisition_view_form").id
        return data
    
    @api.multi
    def action_create_quotation(self):
        form_view_id = self.env.ref("kw_inventory.kw_material_request_quotation_wizard_view").id
        return{
            'name': 'Create Quotation',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_material_request_quotation_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            # 'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new',
            'context':{'active_ids':self._context.get('active_ids')},
        }

    @api.multi
    def requisition_hod_action(self):
        contxt = {'default_requisition_id':self.id}
        action = {
            'name': ' Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_requisition_hod_remark',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context':contxt
        }
        if self._context.get('submit_hod_approve'):
            action['context'] = {'submit_hod_approve':True,'default_requisition_id':self.id}
            approve_form_view_id = self.env.ref("kw_inventory.kw_requisition_hod_approve_remark_form_view").id
            action['view_id'] = approve_form_view_id
        elif self._context.get('submit_hod_reject'):
            action['context'] = {'submit_hod_reject':True,'default_requisition_id':self.id}
            reject_form_view_id = self.env.ref("kw_inventory.kw_requisition_hod_reject_remark_form_view").id
            action['view_id'] = reject_form_view_id
        return action
    
    @api.model
    def create(self, vals):
        res = super(kwRequisitionRequested, self).create(vals)
        res.quant_available = res.item_code.qty_available
        res.sequence = res.requisition_rel_id.requisition_number
        if res.requisition_rel_id:
            res.write({
                "requirement_type":res.requisition_rel_id.requirement_type,
                "project_code":res.requisition_rel_id.project_code,
            })
        return res