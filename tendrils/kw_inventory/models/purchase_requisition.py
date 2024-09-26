# import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_purchase_requisition(models.Model):
    _name = 'kw_purchase_requisition'
    _description = "Purchase Requisition"
    _rec_name = "requisition_number"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'id desc'

    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    requisition_number = fields.Char(string="Requisition Number", required=True, default="New", readonly="1")

    project_code = fields.Char(string="Project Code")
    add_product_rel = fields.One2many("kw_add_product", 'pr_rel', string="Item Details")
    add_requisition_rel_ids = fields.One2many("kw_requisition_requested", 'requisition_rel_id', string="Item Details", track_visibility='onchange')
    cost_center_code = fields.Many2one('account.account', string="Cost Center Code", track_visibility='always')
    budget_code = fields.Char(string="Budget code")
    estimated_value = fields.Integer(string="Estimated Value")
    budgeted_value = fields.Integer(string="Budget Value")
    can_edit_remark = fields.Boolean(compute='compute_can_edit_remark')
    status = fields.Char(string="PR Status", compute="_get_status", store=True, default="Draft")
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Pending', 'Pending'),
        ('Hold', 'Hold'),
        ('In progress', 'In progress'),
        ('Approved', 'Approved'),
        ('Cancelled', 'Cancelled'),
        ('Rejected', 'Rejected'),
    ], string='Status', readonly=True, index=True, copy=False, default='Draft', track_visibility='onchange')
    remark = fields.Char(string='Remark',track_visibility='always')
    # get_department = fields.Boolean(compute="_get_department", string="Get Department", default=False)
    department_name = fields.Many2one('hr.department', string="Department Name", required=True,
                                      track_visibility='always',
                                      default=lambda self: self.get_department()
                                      )
    department_code = fields.Char(string="Department Code", default=lambda self: self.env.user.employee_ids.department_id.code)
    indenting_department = fields.Many2one('hr.department', string="Indenting Department", required=True,
                                           track_visibility='always', default=lambda self: self.get_department())
    type_of_po  = fields.Many2one('purchase_order_type',string='Purchase Order Type')
    material_id = fields.Many2one('kw_material_management', ondelete='cascade')
    pending_at    = fields.Char(string="Pending At")
    applied_by = fields.Many2one('hr.employee')
    requirement_type = fields.Selection([
        ('treasury', 'Treasury'),
        ('project', 'Project'),
    ], string='Requirement Type',default='treasury',track_visibility='onchange')
    
    # @api.multi
    # def _compute_pending_at(self):
    #     for rec in self:
    #         if rec.state =='Pending':
    #             rec.pending_at = rec.department_name.manager_id.id if rec.department_name.manager_id else False
            

    @api.multi
    def redirect_request_action(self):
        contxt = {'default_requisition_id':self.id}
        action = {
            'name': ' Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_requisition_user_remark',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context':contxt
        }
        if self._context.get('apply_requisition_request'):
            action['context'] = {'apply_requisition_request':True,'default_requisition_id':self.id}
            apply_form_view_id = self.env.ref("kw_inventory.kw_requisition_request_apply_remark_form").id
            action['view_id'] = apply_form_view_id
        elif self._context.get('approve_requisition_request'):
            action['context'] = {'approve_requisition_request':True,'default_requisition_id':self.id}
            approve_form_view_id = self.env.ref("kw_inventory.kw_requisition_request_remark_form").id
            action['view_id'] = approve_form_view_id
        elif self._context.get('send_back_requisition'):
            action['context'] = {'send_back_requisition':True,'default_requisition_id':self.id}
            sendback_form_view_id = self.env.ref("kw_inventory.kw_requisition_sendback_remark_form_view").id
            action['view_id'] = sendback_form_view_id
        elif self._context.get('cancel_requisition'):
            action['context'] = {'cancel_requisition':True,'default_requisition_id':self.id}
            cancel_form_view_id = self.env.ref("kw_inventory.kw_requisition_cancel_remark_form_view").id
            action['view_id'] = cancel_form_view_id
        elif self._context.get('reject_requisition'):
            action['context'] = {'reject_requisition':True,'default_requisition_id':self.id}
            cancel_form_view_id = self.env.ref("kw_inventory.kw_requisition_reject_remark_form_view").id
            action['view_id'] = cancel_form_view_id
        # print("action===",action)
        return action


    # pr sequence
    @api.model
    def create(self, vals):
        if vals.get('requisition_number', 'New') == 'New':
            vals['requisition_number'] = self.env['ir.sequence'].next_by_code('kw_requisition') or '/'
        self.env.user.notify_success(message='Requisition created successfully.')
        return super(kw_purchase_requisition, self).create(vals)

    @api.constrains('requisition_number','add_requisition_rel_ids')
    def check_child_record(self):
        if len(self.add_requisition_rel_ids) == 0:
            # print(len(record.add_product_rel))
            raise ValidationError("Please fill item details.")
        for record in self.add_requisition_rel_ids:
            if record.quantity_required <=0:
                raise ValidationError("Quantity required should be a positive value")

    # @api.onchange("department_name")
    # def _set_department_code(self):
    #     for record in self:
    #         if record.department_name:
    #             record.department_code = record.department_name.id

    @api.model
    def get_department(self):
        # print("get dept called")
        # print(self._uid)
        uid = self.env.user.id
        dept = self.env['hr.employee'].sudo().search([('user_id', '=', self._uid)])
        # print("Department is",dept.department_id)
        return dept.department_id.id

    @api.model
    def compute_can_edit_remark(self):
        for record in self:
            record.can_edit_remark = record.env.user.has_group('stock.group_stock_manager')

    @api.multi
    @api.depends('add_product_rel')
    def _get_status(self):
        # print('get status method called')
        for record in self:
            approv = []
            reject = []
            draf = []
            on_hold = []
            if record.add_product_rel:
                for rec in record.add_product_rel:
                    if rec.status == 'Draft':
                        draf.append(rec.status)
                    if rec.status == 'Approved':
                        approv.append(rec.status)
                    if rec.status == 'Rejected':
                        reject.append(rec.status)
                    if rec.status == 'Hold':
                        on_hold.append(rec.status)
                if len(record.add_product_rel) == len(draf):
                    # print(len(draf))
                    record.status = 'Pending'
                    record.state = 'Pending'
                if len(record.add_product_rel) == len(reject):
                    # print(len(reject))
                    record.status = 'Cancelled'
                    record.state = 'Cancelled'
                if len(record.add_product_rel) == len(approv):
                    # print(len(approv))
                    record.status = 'Approved'
                    record.state = 'Approved'
                if len(record.add_product_rel) == len(on_hold):
                    record.status = 'Hold'
                    record.state = 'Hold'
                if len(draf) > 0 and len(approv) > 0 or len(reject) > 0 and len(approv) > 0 or len(reject) > 0 and len(
                        draf) > 0 or len(draf) > 0 and len(on_hold) > 0 or len(on_hold) > 0 and len(approv) > 0 or len(
                    on_hold) > 0 and len(reject) > 0:
                    record.status = 'In progress'
                    record.state = 'In progress'
                if len(draf) == 0 and len(on_hold) == 0 and len(approv) > 0 and len(reject) > 0:
                    record.status = 'Approved'
                    record.state = 'Approved'

    # @api.model
    # def create(self, vals):
    #     new_record = super(kw_purchase_requisition, self).create(vals)
    #     self.env.user.notify_success(message='Requisition Created Successfully.')
    #     return new_record

    @api.multi
    def write(self, vals):
        res = super(kw_purchase_requisition, self).write(vals)
        self.env.user.notify_success(message='Requisition updated successfully.')
        return res

    @api.onchange('add_product_rel')
    def validate_item(self):
        for record in self:
            lst = []
            for rec in record.add_product_rel:
                if rec.item_code.id in lst:
                    raise ValidationError("Same item cannot be added twice")
                else:
                    lst.append(rec.item_code.id)

    @api.multi
    def unlink(self):
        for record in self:
            indent_rec = self.env['kw_consolidation'].sudo().search([])
            if indent_rec:
                for indent in indent_rec:
                    for req in indent.requisition_rel:
                        if record.requisition_number == req.requisition_number:
                            raise ValidationError(
                                f"Record cannot be Deleted. Requisition No - {record.requisition_number} is referenced by Indent No - {indent.indent_number}")

        res = super(kw_purchase_requisition, self).unlink()
        if res:
            self.env.user.notify_success(message='Requisition deleted successfully.')
        else:
            self.env.user.notify_danger(message='Requisition deletion failed.')
        return res
