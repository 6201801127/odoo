from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
import base64
from _ast import Pass

class GrnNumber(models.Model):
    _name = 'grn.seqid'
    _description = "GRN Seqid"
    _order = 'id desc'

class EmployeeIndentAdvance(models.Model):
    _name = 'indent.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description='Indent Request'
    _order = 'id desc'

    def _default_employee(self):
        return self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
    
    def _compute_is_user_approved(self):
        users = self.item_ids.mapped('user_id')
        if (self.env.uid in users.ids and self.state in ('to_approve','inprogress','rejected','approved')) or self.state in  ('rejected','approved'):
            self.is_approve = True
        elif self.indent_type == 'grn':
            self.is_approve = True
        else:
            self.is_approve = False
    
    def _compute_is_user_act(self):
        users = self.create_uid
        if self.env.uid == users.id and self.state in ('to_approve','draft') and self.indent_type != 'grn':
            self.is_usr_activity = True
        else:
            self.is_usr_activity = False

    def _item_receive_user(self):
        for record in self:
            if record.employee_id.user_id.id == self.env.uid:
                record.item_receive_user = True
        

    indent_sequence = fields.Char('Number',track_visibility='always')

    vendor_info = fields.Many2one('grn.vendor', track_visibility='always')
    vendor_id = fields.Many2one('res.partner', domain="[('supplier','=',True)]")
    bill_no = fields.Char('Bill Number',track_visibility='always')
    bill_date = fields.Date('Bill Date', default=fields.Date.today())
    upload_invoice = fields.Binary('Upload Invoice',track_visibility='always')
    filename = fields.Char()
    received_by = fields.Many2one('hr.employee','Received By',track_visibility='always', domain="[('branch_id','=',branch_id)]")
    item_checked_by = fields.Char('Item Checked By',track_visibility='always')
    date_of_receive = fields.Date('Date of Receive',track_visibility='always')
    purchase_date = fields.Date('Purchase Date',track_visibility='always')
    employee_id = fields.Many2one('hr.employee', string='Employee', default=_default_employee ,track_visibility='always')
    company_id = fields.Many2one('res.company', related='employee_id.company_id', store=True, readonly=False)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True, store=True)
    amount = fields.Monetary('Amount',track_visibility='always')
    branch_id = fields.Many2one('res.branch', string='Center', store=True)
    job_id = fields.Many2one('hr.job', string='Functional Designation', store=True)
    department_id = fields.Many2one('hr.department', string='Department', store=True)
    requested_date = fields.Date('Date', default=fields.Date.today())
    item_ids = fields.One2many('indent.request.items','request_id', string='Items')
    issue_id = fields.One2many('issue.request','Indent_id', string='Items')
    indent_type = fields.Selection([('issue', 'Issue'), ('grn', 'GRN')
                               ],track_visibility='always', string='Type')

    state = fields.Selection([('draft', 'Draft'), ('to_approve', 'Pending for Approval'), 
                              ('inprogress', 'In Progress'), ('approved', 'Approved'),
                              ('cancel', 'Cancelled'), ('rejected', 'Rejected')
                               ], required=True, default='draft',track_visibility='always', string='Status')
    
    is_approve = fields.Boolean(compute='_compute_is_user_approved', string='Is the indent approved')
    is_usr_activity = fields.Boolean(compute='_compute_is_user_act')
    item_receive_user = fields.Boolean(compute='_item_receive_user')

    

    @api.multi
    def action_view_items(self):
        action = self.env.ref('indent_stpi.hremployeeIndent_request_action_issue').read()[0]
        if 1 == 1:
            form_view = [(self.env.ref('indent_stpi.employeeissue_request_form_view').id, 'form')]
            action['views'] = form_view
            action['res_id'] = self.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    # def action_show_details(self):
    #     """ Returns an action that will open a form view (in a popup) allowing to work on all the
    #     lines of a particular indent to assign quantity and serial. 
    #     """
    #     self.ensure_one()
    #
    #     view = self.env.ref('stock.view_stock_move_nosuggest_operations')
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
    #         # 'context': dict(
    #         #     self.env.context,
    #         #     show_lots_m2o=self.has_tracking != 'none' and (picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),  # able to create lots, whatever the value of ` use_create_lots`.
    #         #     show_lots_text=self.has_tracking != 'none' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
    #         #     show_source_location=self.location_id.child_ids and self.picking_type_id.code != 'incoming',
    #         #     show_destination_location=self.location_dest_id.child_ids and self.picking_type_id.code != 'outgoing',
    #         #     show_package=not self.location_id.usage == 'supplier',
    #         #     show_reserved_quantity=self.state != 'done'
    #         # ),
    #     }
    
    @api.onchange('employee_id')
    @api.constrains('employee_id')
    def onchange_emp_get_base(self):
        for rec in self:
            rec.job_id = rec.employee_id.job_id.id
            rec.department_id = rec.employee_id.department_id.id
            rec.branch_id = rec.employee_id.branch_id.id
            
    @api.multi
    @api.constrains('item_ids')
    def _check_amount(self):
        for sheet in self:
            expense_lines = sheet.mapped('item_ids')
            line_amounts = sum(expense_lines.mapped('amount'))
            if expense_lines and self.amount < line_amounts:
                raise ValidationError(_("Item's total amount must be equal or less then with GRN amount."))


    def onchange_indent_state(self):
        group_id = self.env.ref('indent_stpi.group_grn_manager')
        ### category wise approval request
        # users = self.item_ids.mapped('item_category_id').mapped('category_id').mapped('user_id')
        users = self.item_ids.mapped('item_category_id').mapped('user_id')
        resUsers = users.filtered(
            lambda r: group_id.id in r.groups_id.ids and self.branch_id.id in r.branch_ids.ids).mapped('partner_id')
        if resUsers:
            employee_partner = self.employee_id.user_id.partner_id
            if employee_partner:
                resUsers += employee_partner
            message = "%s is move to %s" % (self.indent_sequence, dict(self._fields['state'].selection).get(self.state))
            self.env['mail.message'].create({'message_type': "notification",
                                             "subtype_id": self.env.ref("mail.mt_comment").id,
                                             'body': message,
                                             'subject': "Invent request",
                                             'needaction_partner_ids': [(4, p.id, None) for p in resUsers],
                                             'model': self._name,
                                             'res_id': self.id,
                                             })
            self.env['mail.thread'].message_post(
                body=message,
                partner_ids=[(4, p.id, None) for p in resUsers],
                subtype='mail.mt_comment',
                notif_layout='mail.mail_notification_light',
            )


    @api.multi
    def button_to_approve(self):
        for res in self:
            if res.indent_type != 'grn':
                res.onchange_indent_state()
                # users = self.item_ids.mapped('item_category_id').mapped('category_id').mapped('user_id')
                users = self.item_ids.mapped('item_category_id').mapped('user_id')
                resUsers = users.filtered(
                    lambda r: self.branch_id.id in r.branch_ids.ids)
                # for user in resUsers:
                for item in res.item_ids:
                #
                #     categ_users = item.item_category_id.category_id.user_id
                #     if user in categ_users:
                    if not item.item_id.serial_bool:
                        pass
                        # res.issue_id = [(0,0,{
                        #         'Indent_id': res.id,
                        #         'employee_id': res.employee_id.id,
                        #         'branch_id': res.branch_id.id,
                        #         'Indent_item_id': item.id,
                        #         'item_category_id': item.item_category_id.id,
                        #         'item_id': item.item_id.id,
                        #         'serial_bool': item.item_id.serial_bool,
                        #         'asset': item.item_id.asset,
                        #         'specification': item.specification,
                        #         'requested_quantity': item.requested_quantity,
                        #         'approved_quantity': 0,
                        #         'requested_date': item.requested_date,
                        #         'indent_state': res.state,
                        #         'indent_type': res.indent_type,
                        #         'state': 'to_approve',
                        #     })]
                    else:
                        serial_number = False
                        if res.indent_type != 'grn':
                            search_id = self.env['indent.serialnumber'].sudo().search(
                                [('grn', '=', True), ('issue', '!=', True), ('branch_id', '=', res.branch_id.id),
                                 ('item_category_id', '=', item.item_category_id.id), ('item_id', '=', item.item_id.id),
                                 ('state', '=', 'approved')]
    
                            )
                            if search_id:
                                for sr in search_id:
                                    serial_number = sr.id
                            else:
                                serial_number = False
                        n = item.requested_quantity
                        for i in range(n):
                            res.item_ids = [(0,0,{
                                'Indent_id': res.id,
                                'employee_id': res.employee_id.id,
                                'branch_id': res.branch_id.id,
                                'Indent_item_id': item.id,
                                'item_category_id': item.item_category_id.id,
                                'item_category': item.item_category.id,
                                'item_sub_category_id': item.item_sub_category_id.id,
                                'item_id': item.item_id.id,
                                'serial_bool': item.item_id.serial_bool,
                                'asset': item.item_id.asset,
                                'specification': item.specification,
                                'requested_spec': item.requested_spec,
                                'requested_quantity': 1,
                                'approved_quantity':0 if res.indent_type == 'issue' else 1,
                                'requested_date': item.requested_date,
                                'indent_state': res.state,
                                'indent_type': res.indent_type,
                                'temporary_item_id' : item.item_id.id
                                # 'state': 'to_approve',
                            })]
                        item.unlink()
            res.write({'state': 'to_approve'})
            
    
            
    def button_grant(self):
        users = self.item_ids.mapped('item_category_id').mapped('category_id').mapped('user_id')
        resUsers = users.filtered(
            lambda r: self.branch_id.id in r.branch_ids.ids)
        if len(resUsers) == 1:
            for item in self.item_ids:
                issued_item = self.issue_id.filtered(
                        lambda r: r.item_id.id in item.item_id.ids)
                if issued_item:
                    issued_item.write({'state':'approved','issue_state':'approved'})
                    serial = issued_item.mapped('serial_number')
                    if serial: serial.write({'issue':True})
                    item.write({'issue_approved':True,
                                'state':'approved',
                                'issue_state':'approved',
                                'approved_quantity':sum(issued_item.mapped('approved_quantity')),
                                'approved_date':issued_item[0].approved_date,
                                'user_id':self.env.user.id
                    })
                    item.item_id.issue += sum(issued_item.mapped('approved_quantity'))
                    item.item_id.balance = item.item_id.received - item.item_id.issue
            
        else:
            for item in self.item_ids:
                issued_item = self.issue_id.filtered(
                        lambda r: r.item_id.id == item.item_id.id)
                if issued_item:
                    issued_item.write({'state':'approved','issue_state':'approved'})
                    serial = issued_item.mapped('serial_number')
                    if serial: serial.write({'issue':True})
                    item.write({'issue_approved':True,
                                'state':'approved',
                                'issue_state':'approved',
                                'approved_quantity':sum(issued_item.mapped('approved_quantity')),
                                'approved_date':issued_item[0].approved_date,
                                'user_id':self.env.user.id
                    })
                    item.item_id.issue += sum(issued_item.mapped('approved_quantity'))
                    item.item_id.balance = item.item_id.received - item.item_id.issue
        
        states = self.item_ids.mapped('state')
        if all(states): self.state = 'approved'
        elif all(x == 'rejected' for x in states): self.state = 'rejected'
        else: self.state = 'inprogress'
        return True
          
          
    @api.multi
    def button_approved(self):
        for res in self:
            res.onchange_indent_state()
            res.write({'state': 'approved'})
            state = 'to_approve'
            if res.indent_type == 'grn':
                state = 'to_approve_proceed'
                res.item_ids.write({'approved_date': fields.Date.today()})
            else:
                state = 'to_approve'
            for item in res.item_ids:
                if not item.item_id.serial_bool:
                    create_ledger_family = self.env['issue.request'].sudo().create(
                        {
                            'Indent_id': res.id,
                            'employee_id': res.employee_id.id,
                            'branch_id': res.branch_id.id,
                            'Indent_item_id': item.id,
                            'item_category_id': item.item_category_id.id,
                            'item_id': item.item_id.id,
                            'serial_bool': item.item_id.serial_bool,
                            'asset': item.item_id.asset,
                            'specification': item.specification,
                            'requested_quantity': item.requested_quantity,
                            'approved_quantity': item.approved_quantity if item.approved_quantity > 0 else item.requested_quantity,
                            'requested_date': item.requested_date,
                            'indent_state': res.state,
                            'indent_type': res.indent_type,
                            'state': state,
                        }
                    )
                else:
                    serial_number = False
                    if res.indent_type != 'grn':
                        search_id = self.env['indent.serialnumber'].sudo().search(
                            [('grn', '=', True), ('issue', '!=', True), ('branch_id', '=', res.branch_id.id),
                             ('item_category_id', '=', item.item_category_id.id), ('item_id', '=', item.item_id.id),
                             ('state', '=', 'approved')]

                        )
                        if search_id:
                            for sr in search_id:
                                serial_number = sr.id
                        else:
                            serial_number = False
                    n = item.approved_quantity if item.approved_quantity > 0 else item.requested_quantity
                    for i in range(n):
                        create_ledger_family = self.env['issue.request'].sudo().create(
                            {
                                'Indent_id': res.id,
                                'employee_id': res.employee_id.id,
                                'branch_id': res.branch_id.id,
                                'Indent_item_id' : item.id,
                                'item_category_id': item.item_category_id.id,
                                'item_id': item.item_id.id,
                                'serial_bool': item.item_id.serial_bool,
                                'serial_number': serial_number,
                                'asset': item.item_id.asset,
                                'specification': item.specification,
                                'requested_quantity': 1,
                                'approved_quantity': 0 if res.indent_type == 'issue' else 1,
                                'requested_date': item.requested_date,
                                'indent_state': res.state,
                                'indent_type': res.indent_type,
                                'state': state,
                            }
                        )



    @api.multi
    def button_reject(self):
        for record in self:
            if record.indent_type != 'grn':
                users = record.item_ids.mapped('item_category_id').mapped('category_id').mapped('user_id')
                resUsers = users.filtered(
                    lambda r: record.branch_id.id in r.branch_ids.ids)
                if len(resUsers) == 1:
                    for item in record.item_ids:
                        issued_item = record.issue_id.filtered(
                                lambda r: r.item_id.id in item.item_id.ids)
                        if issued_item:
                            issued_item.write({'state':'rejected'})
                            item.write({'issue_approved':False,
                                        'state':'rejected',
                                        'approved_quantity':sum(issued_item.mapped('approved_quantity')),
                                        'approved_date':issued_item[0].approved_date,
                                        'user_id':self.env.user.id
                            })
                    
                else:
                    for item in record.item_ids:
                        issued_item = record.issue_id.filtered(
                                lambda r: r.item_id.id == item.item_id.id)
                        if issued_item:
                            issued_item.write({'state':'rejected'})
                            item.write({'issue_approved':False,
                                        'state':'rejected',
                                        'approved_quantity':sum(issued_item.mapped('approved_quantity')),
                                        'approved_date':issued_item[0].approved_date,
                                        'user_id':self.env.user.id
                            })
                states = record.item_ids.mapped('state')
                if False not in states and 'approved' in states: 
                    record.state = 'approved'
                elif all(x == 'rejected' for x in states): 
                    record.state = 'rejected'
                else: 
                    record.state = 'inprogress'
                record.issue_id.write({'issue_state':'rejected'})
            else:
                record.write({'state':'rejected'})
        return True
            # rec.onchange_indent_state()
            # rec.write({'state': 'rejected'})
            
    @api.multi
    def button_cancel(self):
        for rec in self:
            if rec.indent_type != 'grn':
                rec.onchange_indent_state()
                issue_id = self.env['issue.request'].search([('Indent_id', '=', rec.id)])
                if issue_id: issue_id.unlink()
            rec.write({'state': 'cancel'})

    @api.multi
    def button_reset_to_draft(self):
        for rec in self:
            rec.onchange_indent_state()
            if rec.indent_type != 'grn':
                issue_id = self.env['issue.request'].search([('Indent_id', '=', rec.id)])
                if issue_id: issue_id.unlink()
            rec.write({'state': 'draft'})

    @api.model
    def create(self, vals):
        res =super(EmployeeIndentAdvance, self).create(vals)
        if res.indent_type == 'issue':
            seq = self.env['ir.sequence'].next_by_code('indent.request')
            sequence = 'IR' + str(seq)
        else:
            seq = self.env['ir.sequence'].next_by_code('grn.seqid')
            sequence = 'GRN' + str(seq)
        res.indent_sequence = sequence
        res.onchange_indent_state()
        # search_id = self.env['indent.request'].sudo().search(
        #     [('employee_id', '=', res.employee_id.id),
        #      ('state', 'not in', ['approved','rejected']), ('id', '!=', res.id)])
        # for emp in search_id:
        #     if emp:
        #         raise ValidationError(
        #             "One of the Indent Request is already in process.")
        return res

    @api.multi
    @api.depends('indent_sequence')
    def name_get(self):
        res = []
        for record in self:
            if record.indent_sequence:
                name = record.indent_sequence
            else:
                name = 'IR'
            res.append((record.id, name))
        return res


class IndentItemDetails(models.Model):
    _name = 'indent.request.items'
    _description = "Indent Item Details"
    _order = 'id desc'


    # @api.onchange('item_category_id')
    # def change_item_category_id(self):
    #     return {'domain': {'item_id': [('child_indent_stock', '=', self.item_category_id.id)
    #         ]}}
    
    def _compute_is_2nd_level_item(self):
        for rec in self:
            is_2nd_level =  rec.item_sub_category_id.level_2
            if is_2nd_level:
                rec.is_2nd_level_item = True
            else:
                rec.is_2nd_level_item = False


    @api.depends('item_id', 'alternative_item_id')
    def _get_stock_count(self):
        for record in self:
            if record.item_available == 'available':
                record.item_in_stock = record.item_id.balance
            elif record.item_available == 'alternate_available':
                record.item_in_stock = record.alternative_item_id.balance
            else:
                record.item_in_stock = 0
            

    request_id = fields.Many2one('indent.request', string='Item ID')
    user_id = fields.Many2one('res.users', string='Action Taken')
    item_category_id = fields.Many2one('product.category', string='Item Category')
    item_category = fields.Many2one('product.category', string='Item Category', domain="[('parent_id','=',False)]")
    item_sub_category_id = fields.Many2one('product.category', string='Item Sub Category')
    item_id = fields.Many2one('indent.stock', string='Item')
    item_details = fields.Text('Item Details')
    specification = fields.Text('Specifications')
    requested_quantity = fields.Integer('Qty.')
    approved_quantity = fields.Integer('Approved Qty.')
    company_id = fields.Many2one('res.company', related='user_id.company_id', store=True, readonly=False)
    currency_id = fields.Many2one('res.currency', readonly=True, store=True)
    amount = fields.Monetary('Amount')
    issue_approved = fields.Boolean('Issue approved')
    requested_date = fields.Date('Received Date', default=fields.Date.today())
    approved_date = fields.Date('Approved Date')
    indent_type = fields.Selection([('issue', 'Issue'), ('grn', 'GRN')
                               ],track_visibility='always', string='Type', related="request_id.indent_type")
    # state = fields.Selection(related="request_id.state")
    state = fields.Selection([('draft', 'Draft'),('approved', 'Approved'), ('rejected', 'Rejected'),
                               ('to_be_procure', 'To Be procured'),
                               ('waiting_for_another_level','Waiting for Another Level'),
                               ], default='draft')
    serial_number = fields.Many2one('indent.serialnumber',string='Serial Number')
    serial_bool = fields.Boolean(string='Serial Number')
    item_available = fields.Selection([('available', 'Available'), ('not_available', 'Not Available'), ('alternate_available', 'Alternate available')],default='available')
    is_2nd_level_item = fields.Boolean(compute='_compute_is_2nd_level_item')
    is_1st_level_done = fields.Boolean(default=False)
    is_2nd_level_done = fields.Boolean(default=False)
    requested_spec = fields.Text('Required Specification')
    alternative_item_id = fields.Many2one('indent.stock', string='Alternate Item')
    remark = fields.Text('Remark')
    show_item = fields.Boolean(default=False)
    temporary_item_id = fields.Many2one('indent.stock', string='Temporary Item')
    item_in_stock = fields.Integer(compute='_get_stock_count', string='Item in Stock')
    user_receive = fields.Boolean(string='Received By User')



    
    def button_received(self):
        for record in self:
            record.user_receive = True


    @api.onchange('item_sub_category_id')
    def clear_items(self):
        for record in self:
            record.item_id = False

    @api.onchange('alternative_item_id')
    def change_alternative_item_id(self):
        for record in self:
            record.serial_number = False

    @api.constrains('serial_number')
    def check_serial_number(self):
        for record in self:
            if record.serial_number:
                records = self.env['indent.request.items'].search([('serial_number', '=', record.serial_number.id)]) - self
                if records:
                    raise ValidationError("This Serial Number has already been Assigned")


    @api.multi
    def write(self, vals):
        for record in self:
            old_serial_no = record.serial_number if record.serial_number else False
            super(IndentItemDetails, self).write(vals)
            new_serial_no = record.serial_number if record.serial_number else False

            if old_serial_no == False and new_serial_no == False:
                pass
            elif old_serial_no == False and new_serial_no != False:
                new_serial_no.write({'issue': True})
            elif old_serial_no != False and new_serial_no == False:
                old_serial_no.write({'issue': False})
            elif old_serial_no != False and new_serial_no != False:
                if old_serial_no.id == new_serial_no.id:
                    if old_serial_no.issue == False:
                        old_serial_no.write({'issue': True})
                else:
                    old_serial_no.write({'issue': False})
                    new_serial_no.write({'issue': True})

        return True


    


    
            
       
            

    @api.onchange('item_available')
    def clear_serial_no(self):
        self.temporary_item_id = False
        self.serial_number = False
        self.alternative_item_id = False
        self.approved_quantity = 0
        if self.item_available == 'available':
            self.temporary_item_id = self.item_id.id

        return {'domain': {'serial_number': [('item_id', '=', self.item_id.id),('grn', '=', True),('issue', '=', False),('branch_id', '=', self.request_id.branch_id.id),('state', '=', 'approved')]}}

       

    @api.onchange('alternative_item_id')
    def serial_domain(self):
        if self.item_available == 'alternate_available':
            self.temporary_item_id = self.alternative_item_id.id
            return {'domain': {'serial_number': [('item_id', '=', self.alternative_item_id.id),('grn', '=', True),('issue', '=', False),('branch_id', '=', self.request_id.branch_id.id),('state', '=', 'approved')]}}
            

    

    
    
    @api.multi
    def button_confirm_apr(self):
        level = True if self.is_1st_level_done else False
        return {
            'name': 'Are you sure?',
            'type': 'ir.actions.act_window',
            'res_model': 'indent.confirm',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_item_line_id': self.id,'default_type':'apr','default_is_2nd_level':level}
        }
        
    @api.multi
    def button_confirm_reject(self):
        level = True if self.is_1st_level_done else False
        return {
            'name': 'Are you sure?',
            'type': 'ir.actions.act_window',
            'res_model': 'indent.confirm',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_item_line_id': self.id,'default_type':'reject','default_is_2nd_level':level}
        }
        
    @api.multi
    def button_confirm_procure(self):
        level = True if self.is_1st_level_done else False
        return {
            'name': 'Are you sure?',
            'type': 'ir.actions.act_window',
            'res_model': 'indent.confirm',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_item_line_id': self.id,'default_type':'procure','default_is_2nd_level':level}
        }
    
    # @api.multi
    # def write(self, vals):
    #     su = super(IndentItemDetails,self).sudo()
    #     res = su.write(vals)
    #     return res
    
    @api.multi
    @api.constrains('approved_quantity')
    def _check_amount(self):
        for sheet in self:
            if sheet.requested_quantity < sheet.approved_quantity:
                raise ValidationError(_("Approved Quantity cann't be greater than Requested Quantity!."))

    @api.multi
    @api.constrains('requested_quantity')
    def _check_requested_quantity(self):
        for record in self:
            if record.requested_quantity < 1:
                raise ValidationError('Requested Quantity should be greater than 0')
    
    def indent_item_procure_message(self, users):
        ### category wise approval request
        resUsers = users.mapped('partner_id')
        if resUsers:
            employee_partner = self.request_id.employee_id.user_id.partner_id
            if employee_partner:
                resUsers += employee_partner
            message = "%s --- This item need to be procure" % (self.item_id.name)
            self.env['mail.message'].create({'message_type': "notification",
                                             "subtype_id": self.env.ref("mail.mt_comment").id,
                                             'body': message,
                                             'subject': "Indent item to be procure",
                                             'needaction_partner_ids': [(4, p.id, None) for p in resUsers],
                                             'model': self._name,
                                             'res_id': self.id,
                                             })
            self.env['mail.thread'].message_post(
                body=message,
                partner_ids=[(4, p.id, None) for p in resUsers],
                subtype='mail.mt_comment',
                notif_layout='mail.mail_notification_light',
            )
            
    def level_approval_message(self, users):
        ### category wise approval request
        resUsers = users.mapped('partner_id')
        if resUsers:
            employee_partner = self.request_id.employee_id.user_id.partner_id
            if employee_partner:
                resUsers += employee_partner
            message = "%s ---  Item's Pending for Approval" % (self.request_id.indent_sequence)
            self.env['mail.message'].create({'message_type': "notification",
                                             "subtype_id": self.env.ref("mail.mt_comment").id,
                                             'body': message,
                                             'subject': "Pending for Approval",
                                             'needaction_partner_ids': [(4, p.id, None) for p in resUsers],
                                             'model': self._name,
                                             'res_id': self.id,
                                             })
            self.env['mail.thread'].message_post(
                body=message,
                partner_ids=[(4, p.id, None) for p in resUsers],
                subtype='mail.mt_comment',
                notif_layout='mail.mail_notification_light',
            )
    
    def get_parent_state(self):
        state = 'inprogress'
        states = self.request_id.sudo().item_ids.mapped('state')
        if 'draft' not in states and 'approved' in states and 'waiting_for_another_level' not in states: 
            state = 'approved'
        elif all(x == 'rejected' for x in states): 
            state = 'rejected'
        else: 
            state = 'inprogress'
        return state
    
    def get_branch_users(self, users):
        branch_users = users.filtered(lambda b: b.default_branch_id == self.request_id.branch_id)
        return branch_users


    
    
    @api.multi
    def button_item_approve(self):
        for record in self:
            sum = 0
            if record.item_available == 'available':
                if record.serial_bool:
                    if not record.serial_number:
                        raise ValidationError(f"Serial Number required for {record.item_id.name}")
                if record.approved_quantity < 1:
                    raise ValidationError(_("Approve Quantity must be greater then 0."))
                sum = record.item_id.balance
                if int(sum) < int(record.approved_quantity) and record.request_id.indent_type == 'issue':
                    raise ValidationError(_("Required quantity not in stock"))
                        
            elif record.item_available == 'alternate_available':
                if not record.alternative_item_id:
                     raise ValidationError(_("Please select Alternate item"))
                if record.alternative_item_id.serial_bool:
                    if not record.serial_number:
                        raise ValidationError(f"Serial Number required for {record.alternative_item_id.name}")
                if record.approved_quantity < 1:
                        raise ValidationError(_("Approve Quantity must be greater then 0."))
                sum = record.alternative_item_id.balance
                if int(sum) < int(record.approved_quantity) and record.request_id.indent_type == 'issue':
                    raise ValidationError(_("Required quantity not in stock"))

            
            # if record.serial_number:
            #     if record.serial_number.issue:
            #         raise ValidationError(_("Serial Number Already Issued!."))
            
            record.write({
                        'state':'approved',
                        'approved_date':fields.Date.today(),
                        'user_id':self.env.user.id,
                        'is_1st_level_done' : True
            })
            parent_state = record.get_parent_state()
            record.request_id.state = parent_state
            serial = record.serial_number
            if serial: serial.write({'issue':True})
            
            if record.item_available == 'available':
                record.item_id.issue += record.approved_quantity
                # record.item_id.balance = record.item_id.received - record.item_id.issue
                record.item_id.balance = record.item_id.balance - record.approved_quantity
            elif record.item_available == 'alternate_available':
                record.alternative_item_id.issue += record.approved_quantity
                record.alternative_item_id.balance = record.alternative_item_id.balance - record.approved_quantity
        
    @api.multi
    def button_item_reject(self):
        for record in self:
            record.state = 'rejected'
            record.approved_date = fields.Date.today()
            record.user_id = self.env.user.id
            parent_state = record.get_parent_state()
            record.request_id.state = parent_state
            record.is_1st_level_done = True
            serial = record.serial_number
            if serial: serial.write({'issue':False})
    
    @api.multi
    def button_send_approval(self):
        for record in self:
            sum = 0
            if record.item_available == 'available':
                if record.serial_bool:
                    if not record.serial_number:
                        raise ValidationError(f"Serial Number required for {record.item_id.name}")
                if record.approved_quantity < 1:
                    raise ValidationError(_("Approve Quantity must be greater then 0."))
                sum = record.item_id.balance
                if int(sum) < int(record.approved_quantity) and record.request_id.indent_type == 'issue':
                    raise ValidationError(_("Required quantity not in stock"))
                        
            elif record.item_available == 'alternate_available':
                if not record.alternative_item_id:
                     raise ValidationError(_("Please select Alternate item"))
                if record.alternative_item_id.serial_bool:
                    if not record.serial_number:
                        raise ValidationError(f"Serial Number required for {record.alternative_item_id.name}")
                if record.approved_quantity < 1:
                        raise ValidationError(_("Approve Quantity must be greater then 0."))
                sum = record.alternative_item_id.balance
                if int(sum) < int(record.approved_quantity) and record.request_id.indent_type == 'issue':
                    raise ValidationError(_("Required quantity not in stock"))
            
            record.state = 'waiting_for_another_level'
            record.is_1st_level_done = True
            parent_state = record.get_parent_state()
            record.request_id.state = parent_state
            users = record.item_sub_category_id.competent_authority
            branch_users = record.get_branch_users(users)
            record.level_approval_message(branch_users)
    
    @api.multi
    def button_level2_appove(self):
        for record in self:
            record.button_item_approve()
            record.is_2nd_level_done=True
        
    @api.multi
    def button_procure(self):
        for record in self:
            record.state = 'to_be_procure'
            parent_state = record.get_parent_state()
            record.approved_date = fields.Date.today()
            record.user_id = self.env.user.id
            record.request_id.state = parent_state
            record.is_2nd_level_done = True
            
            if record.item_sub_category_id.procur_group == 'technical':
                users = self.env.ref('indent_stpi.indent_procur_tech_group').users
                branch_users = record.get_branch_users(users)
                record.indent_item_procure_message(branch_users)
            if record.item_sub_category_id.procur_group == 'non-technical':
                users = self.env.ref('indent_stpi.indent_procur_non_tech_group').users
                branch_users = record.get_branch_users(users)
                record.indent_item_procure_message(branch_users)
            if record.item_sub_category_id.procur_group == 'admin':
                users = self.env.ref('indent_stpi.indent_procur_admin_group').users
                branch_users = record.get_branch_users(users)
                record.indent_item_procure_message(branch_users)
                
    @api.multi
    def button_level2_reject(self):
        for record in self:
            record.state = 'rejected'
            record.approved_date = fields.Date.today()
            record.user_id = self.env.user.id
            parent_state = record.get_parent_state()
            record.request_id.state = parent_state
            record.is_2nd_level_done = True
            serial = record.serial_number
            if serial: serial.write({'issue':False})
        
    
    
    @api.multi
    @api.constrains('approved_quantity')
    def _check_amount(self):
        for sheet in self:
            if sheet.requested_quantity < sheet.approved_quantity:
                raise ValidationError(_("Approved Quantity cann't be greater than Requested Quantity!."))


    @api.onchange('item_id')
    # @api.constrains('item_id')
    def change_item_category_id(self):
        for rec in self:
            rec.specification = rec.item_id.specification
            rec.temporary_item_id = rec.item_id.id
            if rec.item_id.name == 'Others':
                rec.show_item = True
            else:
                rec.show_item = False

    @api.multi
    def button_delete(self):
        for record in self:
            record.unlink()







    
            
            