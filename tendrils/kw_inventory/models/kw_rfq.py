from odoo import api, fields, models,_
from odoo.addons import decimal_precision as dp
from datetime import date, datetime
from odoo.exceptions import ValidationError,UserError
import re
from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from ast import literal_eval
# import decimal
# from num2words import num2words
from odoo.addons.kw_utility_tools import kw_helpers
from odoo.tools.float_utils import float_compare


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def _compute_amount_in_word(self):
        for rec in self:
            rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'

    num_word = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')

    boolean_create_po = fields.Boolean(string="Po create boolean", default=False)
    qc_ids = fields.Many2many('kw_quotation_consolidation', 'kw_qc_purchase_rel', string="Quotation Consolidation No")
    partner_id = fields.Many2one('res.partner', string='Vendor',
                                 help="You can find a vendor by its Name, TIN, Email or Internal Reference.",
                                 required=False)
    child_ids = fields.Many2one('res.partner', string='Contact & Address')
    address=fields.Text(string='Address')
    # qc_items_record_id = fields.Integer(string='Quotation Consolidation Items Record Id')
    state = fields.Selection([('draft', 'Draft PO'), ('sent', 'PO for Approval'), ('to approve', 'To Approve'),('approved', 'Approved'),
                              ('purchase', 'Confirm PO'),
                              ('done', 'Locked'), ('cancel', 'Cancelled'), ('reject', 'Rejected')
                              ], string='Status', readonly=True, index=True, copy=False, default='draft',
                             track_visibility='onchange',
                             group_expand='_expand_groups')
    req_id_rel = fields.Many2many('kw_purchase_requisition', 'kw_rfq_po_rel', string='Purchase Requisition Rel Id')
    requisition_ids = fields.Many2many('kw_requisition_requested', string="Requisitions")

    # req_id = fields.Many2one('kw_purchase_requisition',string='Purchase Requision Id',domain="[('id','in',req_id_rel)]")
    cc_code = fields.Char('Cost Center Code')
    budget_code = fields.Char("Budget Code")
    estimated_value = fields.Integer("Estimated Value")
    budgeted_value = fields.Integer("Budget Value")

    contact_prsn_name = fields.Char('Contact Person Name')
    contact_prsn_number = fields.Char('Contact Person Number')
    sign_autority = fields.Many2one('hr.employee', string='Signature Authority')
    branch_id = fields.Many2one('kw_res_branch', string='Location/Ship To')
    purchase_no = fields.Char(string='Purchase No')
    project_code = fields.Char(related='req_id_rel.project_code', string="Project Code",store=True)
    check_service = fields.Boolean(string='Check servive', compute='compute_check_service')
    status = fields.Selection([('sent', 'PO for Approval'),('approved', 'Approved'),('purchase', 'Confirm PO'),('reject', 'Rejected')], string='Status', readonly=True)
    po_created_by=fields.Many2one('hr.employee',string="Employee")
    pending_at=fields.Char(string="Pending at")


    @api.multi
    def action_ceo_approve(self):
        emp_data = self.env['res.users'].sudo().search([])
        ceo_user = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_chief_executive') == True)
        ceo_user_mail =','.join(ceo_user.mapped('employee_ids.work_email')) if ceo_user else ''
        ceo_user_name =','.join(ceo_user.mapped('employee_ids.name')) if ceo_user else ''
        ceo_user_emp_code =','.join(ceo_user.mapped('employee_ids.emp_code')) if ceo_user else ''
        po_approver_user = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_po_approver') == True)
        po_approver_mail =','.join(po_approver_user.mapped('employee_ids.work_email')) if po_approver_user else ''
        po_approver_name =','.join(po_approver_user.mapped('employee_ids.name')) if po_approver_user else ''
        po_approver_emp_code =','.join(po_approver_user.mapped('employee_ids.emp_code')) if po_approver_user else ''
        self.write({'state': "approved",'pending_at':po_approver_name})
        template_id = self.env.ref('kw_inventory.purchase_order_approved') 
        for recs in self.order_line:
            template_id.with_context(ceo_user_mail=ceo_user_mail,
            ceo_user_name=ceo_user_name,
            ceo_user_emp_code=ceo_user_emp_code,
            po_approver_emp_code=po_approver_emp_code,
            pr_user_mail=po_approver_mail,
            po_approver_name=po_approver_name,
            po_no=self.name,
            product=recs.product_id.name,
            product_code=recs.product_id.default_code,
            qty=recs.product_qty,
            price=recs.price_unit).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")  
        self.env.user.notify_success("Purchase Order Approved successfully.")    


    @api.multi
    def render_purchase_orders(self):
        tree_view_id = self.env.ref('purchase.purchase_order_tree').id
        form_view_id = self.env.ref('purchase.purchase_order_form').id
        search_view_id = self.env.ref('kw_inventory.view_purchase_order_filter_inh').id

        action = {
                'type': 'ir.actions.act_window',
                'name' : 'Purchase Order',
                'views': [(tree_view_id, 'tree'),(search_view_id, 'search'),(form_view_id,'form')],
                'view_mode': 'tree,form',
                'res_model': 'purchase.order',
                'context': {'search_default_group_status': 1,"create": False,"import": False},
                }
        if self.env.user.has_group('kw_inventory.group_chief_executive'):
            action['domain'] = [('state','=','sent')]
        elif self.env.user.has_group('kw_inventory.group_po_approver'):
            action['domain'] = [('state','in',['approved','purchase','reject'])]
        # print("action==========================",action)
        return action
    @api.multi
    def write(self, vals):
        # print("values=======",vals)
        if 'state' in vals:
            if vals['state'] == 'sent':
                vals['status'] = 'sent'
            elif vals['state'] == 'purchase':
                vals['status'] = 'purchase'
            elif vals['state'] == 'reject':
                vals['status'] = 'reject'
            else:
                pass
        res = super(PurchaseOrder, self).write(vals)
        return res
    
    @api.multi
    def compute_check_service(self):
        for rec in self:
            if rec.order_line:
                p_type = rec.order_line.mapped('product_id.type')
                # print("p_type======",p_type)
                if 'service' in p_type and rec.state in ['purchase','done']:
                    rec.check_service = True
                else:
                    rec.check_service = False
                    
            
    @api.multi
    def action_view_service(self):
        self.ensure_one()
        tree_view_id = self.env.ref("kw_inventory.purchase_order_line_inherited_tree").id
        return {
            'name': 'Service Entry Sheet',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'purchase.order.line',
            'res_id': self.id,
            'views': [(tree_view_id, 'tree')],
            'domain':[('product_id.type','=','service'),('order_id','=',self.id)],
            'context': {'search_default_groupby_supplier':1},
            'target': 'current'
        }
   
    @api.onchange('partner_id')
    def partner_id_onchange(self):
        for rec in self:
            child_list = []
            if rec.partner_id:
                # partner = self.env['res.partner'].sudo().search([('name', '=', rec.partner_id.name)])
                partner = self.env['res.partner'].sudo().browse(rec.partner_id.id)
                for record in partner.child_ids:
                    child_list.append(record.id) 
                return {'domain': {'child_ids': [('id', 'in', child_list)]}}

    @api.model
    def _expand_groups(self, states, domain, order):
        return ['draft', 'sent', 'to approve', 'purchase', 'done', 'cancel', 'reject']

    @api.model
    def get_year(self):
        chk_date = self.date_order or datetime.today()
        year = chk_date.year
        if chk_date.month >= 4:
            return f"{str(year)[-2:]}-{str(year + 1)[-2:]}"
        return f"{str(year - 1)[-2:]}-{str(year)[-2:]}"

    @api.onchange('branch_id')
    def _get_sign_auth(self):
        for rec in self:
            employees_list = []
            Parameters = self.env['ir.config_parameter'].sudo()
            signature_authority_ids = Parameters.get_param('kw_inventory.signature_authority_ids')
            if signature_authority_ids:
                auth_list = signature_authority_ids.strip('][').split(', ')

                if auth_list:
                    employees_list = [emp for emp in auth_list]

            return {'domain': {'sign_autority': [('id', 'in', employees_list)]}, }

    @api.onchange('partner_id')
    def get_data(self):
        data = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
        aaddress = []
        if data.street:
            aaddress.append(data.street)
        if data.street2:
            aaddress.append(data.street2)
        if data.city:
            aaddress.append(data.city)
        if data.state_id.name:
            aaddress.append(data.state_id.name)
        if data.zip:
            aaddress.append(data.zip)
        if data.country_id.name:
            aaddress.append(data.country_id.name)
        if data.phone:
            aaddress.append(data.phone)
        aaddress = ', \n'.join(aaddress)
        self.address = aaddress
        
    # @api.onchange("req_id")
    # def _change_req(self):
    #     # req = self.env['purchase.order'].sudo().search([('req_id','=','self.id')])
    #     for record in self:
    #         print(record.req_id,"Record=====")
    #         print(self.cc_code,"CC code====")
    #         record.cc_code = str(record.req_id.cost_center_code.code) + ' ' + str(record.req_id.cost_center_code.name)
    #         record.budget_code = record.req_id.budget_code
    #         record.estimated_value = record.req_id.estimated_value
    #         record.budgeted_value = record.req_id.budgeted_value

    @api.multi
    def move_qc(self):
        self.state = 'reject'
        for items in self.order_line:
            qc_item = self.env['kw_quotation_consolidation_items'].sudo().search(
                [('id', '=', items.quotation_items_ids.id)])
            if qc_item:
                qc_item.po_create = False

    # @api.onchange("indent")
    # def _set_items(self):
    #     for record in self:
    #         record.order_line = False
    #         for rec in record.indent:
    #             if rec.add_product_consolidation_rel:
    #                 vals = []
    #                 for items in rec.add_product_consolidation_rel:
    #                     product = self.env['product.product'].sudo().search([('id','=',items.item_code.id)])
    #                     unit = product.uom_id.id
    #                     vals.append([0,0,{
    #                         'product_id':items.item_code.id if items.item_code else False,
    #                         'name':items.item_description if items.item_description else False,
    #                         'product_qty': items.quantity_required if items.quantity_required else False,
    #                         'date_planned':datetime.now(),
    #                         'product_uom': unit,
    #                         'price_unit':0,
    #                     }])
    #                 record.order_line = vals
    #             else:
    #                 record.order_line=False

    # @api.multi
    # def get_taxes_list(self):
    #     dict_tax = {}
    #     for res in self:
    #         for line in self.order_line:
    #             for tax in line.taxes_id:

    #                 dict_tax['name'] = tax.name
    #                 dict_tax['price'] = tax.

    # @api.multi
    # def button_receipt(self):
    #     rec = self.picking_ids
    #     print("record=========",rec)
    #     if rec:
    #         done_picking = rec.filtered(lambda x: x.state == 'done')
    #         print("done picking=============",done_picking)
    #         if done_picking:
    #             print("inside if================")
    #             raise ValidationError("You can't reset to draft because some of the picking already processed.") 
    #         else:
    #             print("inside else===================")
    #             self.write({'state': 'draft'})
    #             rec.write({'state': 'cancel'})

    @api.multi
    def print_quotation(self):
        self.write({'state': "sent"})
        return self.env.ref('kw_inventory.purchase_order_rfq').report_action(self)

    @api.model
    def create(self, values):
        if 'qc_ids' in values:
            for qc in values.get('qc_ids'):
                quotation_conso = self.env['kw_quotation_consolidation'].browse([qc[1]])
                if quotation_conso.quotation and quotation_conso.quotation[0].notes:
                    values['notes'] = quotation_conso.quotation[0].notes
        if values.get('name', 'New') == 'New':
            # values['name'] = self.env['ir.sequence'].next_by_code('new.order') or '/'
            values['name'] = self.env['ir.sequence'].next_by_code('po_seq_generate') or '/'
            # print(values['name'],"*********>>>>>>>>>>>>>>>>>******")
            # values['name'] = 'New'
        return super(PurchaseOrder, self).create(values)


    # def button_confirm(self):
    #     code_generation = self.env['ir.sequence'].next_by_code('purchase.order') or '/'
    #     # print('code generation is ================',code_generation)
    #     self.write({'name' : code_generation,
    #                 'state':'purchase'})


    def button_confirm(self):
        for order in self:
            code_generation = self.env['ir.sequence'].next_by_code('purchase.order') or '/'
            if order.state not in ['draft','approved','sent']:
                continue
            order.write({'name' : code_generation, 'state':'purchase','date_order':date.today()})
            order._add_supplier_to_product()
            # self.env.context['code'] = code_generation
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.user.company_id.currency_id._convert(
                            order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
                    or order.user_has_groups('purchase.group_purchase_manager'):

                order.button_approve()
            # else:
            #     order.write({'state': 'to approve'})
            # print('code generation is ================',code_generation)
        
        """ Create a gatepass in the method and send notification to storemanageron po confirmation """
        # data = {
        #     'vendor_ref':self.partner_ref,
        #     'partner_id':self.partner_id.id,
        #     'order_date':self.date_order,
        #     'po_id':self.id,
        #     'state':'draft',
        #     'branch_id':self.branch_id.id,
        #     'company_id':self.company_id.id,
        #     'raised_by_id':self.env.user.employee_ids.id,
        #     'operation_type':'po',
        # }
        # pass_id = self.env['kw_product_gatepass'].sudo().create(data)
        # print("pass_id---------------------",pass_id)
        # pass_id.gatepass_line_ids = [(0,0, {'product_id':rec.product_id.id,'gatepass_line':pass_id.id,'description':rec.name,'uom':rec.product_uom.id,'quantity':rec.product_qty,'expected_date':rec.date_planned}) for rec in self.order_line]
        
        # print("pass_id.gatepass_line_ids=================",pass_id.gatepass_line_ids)
        # query = f"update kw_add_product_items set status='Hold' where id in ({str(non_rejected_data.ids)[1:-1]})"
        # self._cr.execute(query)
        template_id = self.env.ref('kw_inventory.purchase_order_confirm_mailto_vendor')
        emp_data = self.env['res.users'].sudo().search([])
        store_manager = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_store_manager') == True)
        email_to = ','.join(store_manager.mapped('email'))if store_manager else False
        
        store_manager_name = ','.join(store_manager.mapped('name'))if store_manager else False
        mail_res = template_id.sudo().with_context(email_to=email_to,store_manager_name=store_manager_name).send_mail(self.id,
                                                                             notif_layout="kwantify_theme.csm_mail_notification_light")
        # self.env.user.notify_success("Gate pass sent successfully.")    
        return True

    def amount_to_word(self, amt, curr):
        amount_in_word = kw_helpers.num_to_words(amt)
        currency_unit_label = ''
        currency_subunit_label = ''
        if curr:
            currency_unit_label = curr.currency_unit_label
            currency_subunit_label = curr.currency_subunit_label
        return f"{currency_unit_label} {amount_in_word} {currency_subunit_label if ' and ' in amount_in_word else ''}"

    # def number_to_word(self, number):
    #     def get_word(n):
    #         words={ 0:"", 1:"One", 2:"Two", 3:"Three", 4:"Four", 5:"Five", 6:"Six", 7:"Seven", 8:"Eight", 9:"Nine", 10:"Ten", 11:"Eleven", 12:"Twelve", 13:"Thirteen", 14:"Fourteen", 15:"Fifteen", 16:"Sixteen", 17:"Seventeen", 18:"Eighteen", 19:"Nineteen", 20:"Twenty", 30:"Thirty", 40:"Forty", 50:"Fifty", 60:"Sixty", 70:"Seventy", 80:"Eighty", 90:"Ninty" }
    #         if n<=20:
    #             return words[n]
    #         else:
    #             ones=n%10
    #             tens=n-ones
    #             return words[tens]+" "+words[ones]

    #     def get_all_word(n):
    #         d=[100,10,100,100]
    #         v=["","Hundred And","Thousand","Lakh"]
    #         w=[]
    #         for i,x in zip(d,v):
    #             t=get_word(n%i)
    #             if t!="":
    #                 t+=" "+x
    #             w.append(t.rstrip(" "))
    #             n=n//i
    #         w.reverse()
    #         w=' '.join(w).strip()
    #         if w.endswith("And"):
    #             w=w[:-3]
    #         return w

    #     arr=str(number).split(".")
    #     number=int(arr[0])
    #     crore=number//10000000
    #     number=number%10000000
    #     word=""
    #     if crore>0:
    #         word+=get_all_word(crore)
    #         word+=" Crore "
    #     word+=get_all_word(number).strip()+" Rupees"
    #     if len(arr)>1:
    #         if len(arr[1])==1:
    #             arr[1]+="0"

    #         if int(arr[1]) != 0:
    #          word+=" and "+get_all_word(int(arr[1]))+" paisa"
    #     return word
    
    #overiding addons method as per our new product type i.e - 'IT', 'Non-IT'
    @api.multi
    def button_cancel(self):
        # print("new method caledd==========================")
        for order in self:
            for inv in order.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(_("Unable to cancel this purchase order. You must first cancel the related vendor bills."))

        self.write({'state': 'cancel'})
        self.qc_ids.write({'state':'invalid'})
        self.requisition_ids.write({'status':'Rejected'})
        emp_data = self.env['res.users'].sudo().search([])
        ceo_user = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_chief_executive') == True)
        ceo_user_mail =','.join(ceo_user.mapped('employee_ids.work_email')) if ceo_user else ''
        ceo_user_name =','.join(ceo_user.mapped('employee_ids.name')) if ceo_user else ''
        ceo_user_emp_code =','.join(ceo_user.mapped('employee_ids.emp_code')) if ceo_user else ''
        po_approver = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_po_approver')==True)
        to_mail = ','.join(po_approver.mapped('employee_ids.work_email')) if po_approver else '' 
        user_name = ','.join(po_approver.mapped('employee_ids.name')) if po_approver else ''
        template_id = self.env.ref('kw_inventory.po_cancelled_notification_to_store_manager')
        template_id.with_context(email_to=to_mail,
                                user_name=user_name,
                                ceo_user_mail=ceo_user_mail,
                                ceo_user_name=ceo_user_name,
                                ceo_user_emp_code=ceo_user_emp_code,
                                po_name=self.name,
                                records=self.order_line,
                                ).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success(message='PO Rejected successfully.')
        
    @api.multi
    def _create_picking(self):
        # import pdb
        # pdb.set_trace()
        StockPicking = self.env['stock.picking']
        for order in self:
            # changed ptype in ['product', 'consu'] to ptype in ['nonit', 'it']
            if any([ptype in ['nonit', 'it'] for ptype in order.order_line.mapped('product_id.type')]):
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                if not pickings:
                    res = order._prepare_picking()
                    # print("res=========================",res)
                    picking = StockPicking.create(res)
                else:
                    picking = pickings[0]
                # print("order.order_line=====",order.order_line,picking)
                moves = order.order_line._create_stock_moves(picking)
                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date_expected):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
                picking.message_post_with_view('mail.message_origin_link',
                    values={'self': picking, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return True

class kw_purchase_order_line(models.Model):
    _inherit = "purchase.order.line"

    product_id = fields.Many2one('product.product', string='Item Code', domain=[('purchase_ok', '=', True)],
                                 change_default=True, required=True)
    quotation_items_ids = fields.Many2one('kw_quotation_consolidation_items', string='Quotation items')
    boolean_create = fields.Boolean(string='Po boolean', default=False)
    # price_subtotal = fields.Float(compute='_compute_amount', string='Subtotal',store=True, digits=dp.get_precision('Price Subtotal'))

    # @api.depends('product_qty', 'price_unit', 'taxes_id')
    # def _compute_amount(self):
    #     for line in self:
    #         vals = line._prepare_compute_all_values()
    #         taxes = line.taxes_id.compute_all(
    #             vals['price_unit'],
    #             vals['currency_id'],
    #             vals['product_qty'],
    #             vals['product'],
    #             vals['partner'])
    #         line.update({
    #             'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
    #             'price_total': taxes['total_included'],
    #             'price_subtotal': taxes['total_excluded'],
    #         })

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context(
            lang=self.partner_id.lang,
            partner_id=self.partner_id.id,
        )

        self.name = self.product_id.varient_description
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase

        self._compute_tax_id()

        self._suggest_quantity()
        self._onchange_quantity()

        return result
    