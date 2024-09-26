import datetime
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.addons.kw_utility_tools import kw_helpers
from odoo.exceptions import ValidationError

class StockReturnPickingInherit(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.multi
    def _create_returns(self):
        # Prevent copy of the carrier and carrier price when generating return picking
        # (we have no integration of returns for now)
        new_picking, pick_type_id = super(StockReturnPickingInherit, self)._create_returns()
        picking = self.env['stock.picking'].browse(new_picking)
        picking.write({'carrier_id': False,
                       'carrier_price': 0.0,
                       'is_return':True})
        return new_picking, pick_type_id

class StockLocationInherit(models.Model):
    _inherit = "stock.location"

    stock_process_location = fields.Selection([
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
        ('grn', 'GRN'),
        ('qc', 'QC'),('store', 'Store'),('scrap', 'Scrap')], string='Stock Process Location',
        track_visibility='onchange')

class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    _description = 'Stock'

    process_location = fields.Selection(string=' Operation Type',selection=[('vendor', 'Vendor'),('customer', 'Customer'),('grn', 'GRN'), ('qc', 'QC'), ('store', 'Store'),('scrap', 'Scrap')],default='vendor')
    is_return = fields.Boolean(string='Return check')
    hide_return_damage =fields.Boolean(string='Hide Return/Damange Buttons', compute='compute_return_and_damage')
    store_id = fields.Many2one('stock_dept_configuration', ondelete='cascade')
    
    
    def compute_return_and_damage(self):
        for rec in self:
            move_serial = rec.move_line_ids.mapped('lot_id.name')
            store_serial = self.env['stock.quant'].sudo().search([('lot_id.name','in',move_serial),('process_location','=','store')])
            if rec.process_location == 'store' and store_serial and not self._context.get('hide_process_buttons'):
                rec.hide_return_damage = False
                # print("11111111111")
            elif rec.process_location == 'grn' and not store_serial and not self._context.get('hide_process_buttons') and not rec.is_return:
                # print("22222222222")
                qc_ids = self.env['stock.picking'].sudo().search([('origin','=',rec.origin),('state','=','assigned'),('process_location','=','qc')],limit=1)
                if qc_ids:
                    # print("aaaaaaaaaaaaaa")
                    rec.hide_return_damage = False
                else:
                    # print("bbbbbbbbbbbbbbb")
                    rec.hide_return_damage = True
            elif rec.process_location == 'qc' and not store_serial and not self._context.get('hide_process_buttons'):
                # print("aaaaaaaaaa")
                rec.hide_return_damage = False
            elif rec.is_return and rec.process_location != 'vendor' and not self._context.get('hide_process_buttons'):
                # print("bbbbbbbbbb")
                rec.hide_return_damage = False
            elif self._context.get('hide_process_buttons'):
                rec.hide_return_damage = True
                # print("cccccccccc")
            else:
                # print("dddddddddd")
                rec.hide_return_damage = True


    
    @api.depends('location_dest_id')
    def _compute_btn_visibility(self):
        for rec in self:
            if rec.location_dest_id.stock_process_location == 'grn' and not self._context.get('hide_print_stock_buttons') and rec.state in ['assigned','done']:
                rec.btn_print = 1
            elif rec.location_dest_id.stock_process_location == 'qc' and not self._context.get('hide_print_stock_buttons'):
                rec.btn_print = 2
            elif not self._context.get('hide_print_stock_buttons'):
                rec.btn_print = 3

    @api.depends('move_ids_without_package.price_subtotal')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        # print("amount all called==============")
        for order in self:
            amount_total = amount_tax = 0.0
            for line in order.move_ids_without_package:
                price_subtotal = line.quantity_done * line.price_unit
                amount_total += line.price_subtotal
                amount_tax +=line.price_tax
                # print("line.price_subtotal======================",line.price_subtotal,line.quantity_done,line.price_unit)
                # print("price data===================",line.price_unit)
            order.update({
                'amount_total': amount_total,
                'amount_tax': order.currency_id.round(amount_tax),
                'full_amount_total': amount_total + amount_tax,
            })

    transporter_code = fields.Many2one('kw_inventory_transporter_master', string="Transporter",
                                       track_visibility='onchange')
    lr_rr_no = fields.Char(string="LR/RR Number", )
    lr_rr_date = fields.Date('LR/RR Date')
    mode_of_delivery = fields.Selection([
        ('Delivered by Hand', 'Delivered by Hand'),
        ('By Courier', 'By Courier'), ], string='Mode Of Delivery', default='Delivered by Hand',
        track_visibility='onchange')
    invoice_number = fields.Char(string="Invoice Number", )
    invoice_date = fields.Date('Invoice Date')
    challan_number = fields.Char(string="Challan Number", )
    challan_date = fields.Date('Challan Date')
    csm_price_conf = fields.Boolean('csm account conf', compute="_compute_price_config")
    po_date = fields.Datetime('PO Date')
    deliver_person_name = fields.Char(string="Delivery Personal Name")
    btn_print = fields.Integer(compute="_compute_btn_visibility")
    amount_total = fields.Float(string='Amount Total', store=True, readonly=True, compute='_amount_all', )
    amount_total_po = fields.Float(string='Amount Total in PO', store=True, readonly=True, )
    weight = fields.Float(string='Weight', digits=dp.get_precision('Stock Weight'), store=True, compute_sudo=True)
    shipping_weight = fields.Float("Weight for Shipping")
    amount_tax = fields.Float(string='Taxes', store=True, readonly=True, compute='_amount_all')
    full_amount_total = fields.Float(string='Total', store=True, readonly=True, compute='_amount_all')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    grn_remark = fields.Text("Remark")
    qc_remark = fields.Text("Remark")
    srv_remark = fields.Text("Remark")
 
    @api.model
    def grn_qc_srv_validation_reminder(self):
        today_date = fields.Date.today()
        purchase_orders = self.env['purchase.order'].sudo().search([])
        stock_pickings = self.env['stock.picking'].sudo().search([])

        for stock_picking in stock_pickings:
            if (stock_picking.process_location =='grn' or stock_picking.process_location =='qc' or stock_picking.process_location =='srv') and stock_picking.state in ['confirmed','waiting','assigned']:
                # print("inside iffffffffffffffff================",stock_picking.state,stock_picking.process_location,stock_picking.scheduled_date.date(),today_date)
                if stock_picking.scheduled_date and stock_picking.scheduled_date.date() <= today_date:
                    # print("inside 2nd if===================")
                    related_purchase_order = purchase_orders.filtered(lambda po: po.name == stock_picking.origin)

                    if related_purchase_order:
                        # print("inside 3rd if======================")
                        self.send_reminder_email(related_purchase_order, stock_picking)

    def send_reminder_email(self, purchase_order, stock_picking):
        # print("imail sent======================",stock_picking.process_location)
        emp_data = self.env['res.users'].sudo().search([])
        store_manager = emp_data.filtered(lambda user: user.has_group('kw_inventory.group_store_manager') == True)
        store_manager_email = store_manager.mapped('email')[0]
        store_manager_name = store_manager.mapped('name')[0]
        emp_code=store_manager.mapped('employee_ids.emp_code')[0]
        template_id = self.env.ref('kw_inventory.grn_qc_srv_validation_reminder')
        template_id.with_context(location=stock_picking.process_location.upper(),purchase_order=purchase_order.name,emp_code=emp_code,store_manager_name=store_manager_name,store_manager_email=store_manager_email).send_mail(stock_picking.id,notif_layout="kwantify_theme.csm_mail_notification_light")

        
    @api.depends('location_dest_id')
    def _compute_price_config(self):
        for rec in self:
            enable_unit_price = self.env['ir.config_parameter'].sudo().get_param('kw_inventory.enable_unit_price')
            rec.csm_price_conf = True if enable_unit_price else False


    def amount_to_word(self, amt, curr):
        amount_in_word = kw_helpers.num_to_words(amt)
        currency_unit_label = ''
        currency_subunit_label = ''
        if curr:
            currency_unit_label = curr.currency_unit_label
            currency_subunit_label = curr.currency_subunit_label

        return f"{currency_unit_label} {amount_in_word} {currency_subunit_label if ' and ' in amount_in_word else ''}"

    @api.model
    def create(self, values):
        indent_dept = False
        own_dept = False
        if values.get('origin'):
            po = self.env['purchase.order'].search([('name', '=', values.get('origin'))])
            if po:
                values['po_date'] = po.date_order
                values['amount_total_po'] = po.amount_total
                values['partner_id'] = po.partner_id.id if po.partner_id else False
            if po.req_id_rel:
                requisition = max(po.req_id_rel.ids)
                if requisition:
                    requisition_obj = self.env['kw_purchase_requisition'].browse(requisition)
                    if requisition_obj:
                        indent_dept = requisition_obj.indenting_department
                        own_dept = requisition_obj.department_name

        defaults = self.default_get(['name', 'picking_type_id'])
        picking_type_id = self.env['stock.picking.type'].browse(
            values.get('picking_type_id', defaults.get('picking_type_id')))

        year = str(datetime.datetime.today().year)[-2:]
        prefix = '2'
        seq = '/'
        if picking_type_id.name == 'GRN':
            seq = self.env['ir.sequence'].next_by_code('GRN') or '/'
        if picking_type_id.name == 'INSPECTION':
            seq = self.env['ir.sequence'].next_by_code('Inspection') or '/'
        if picking_type_id.name == 'SRV':
            seq = self.env['ir.sequence'].next_by_code('SRV') or '/'

        if picking_type_id.name in ['GRN', 'INSPECTION'] and own_dept:
            code = self.env['kw_sequence'].search(
                [('department_id', '=', own_dept.id), ('picking_type_id', '=', picking_type_id.id)]).code
        elif picking_type_id.name == 'SRV' and indent_dept:
            code = self.env['kw_sequence'].search(
                [('department_id', '=', indent_dept.id), ('picking_type_id', '=', picking_type_id.id)]).code
        else:
            code = self.env['kw_sequence'].search(
                [('department_id', '=', False), ('picking_type_id', '=', picking_type_id.id)]).code

        if not code:
            code = ''

        # values['name'] = prefix + year + code + seq

        result = super(StockPicking, self).create(values)
        if result.location_dest_id:
            result.process_location = result.location_dest_id.stock_process_location
        return result

    @api.multi
    def write(self, values):
        res = super(StockPicking, self).write(values)
        pickings = self.env['stock.picking'].search([('origin', '=', self.origin)]) - self
        if pickings:
            for pick in pickings:
                invoice_number = values.get('invoice_number') or self.invoice_number or ''
                invoice_date = f"'{values.get('invoice_date')}'" if values.get('invoice_date') and values.get(
                    'invoice_date') != False else ('null' if values.get('invoice_date') == False else (
                    'null' if self.invoice_date == False and 'invoice_date' not in values else f"'{self.invoice_date}'"))
                challan_number = values.get('challan_number') or self.challan_number or ''
                challan_date = f"'{values.get('challan_date')}'" if values.get('challan_date') and values.get(
                    'challan_date') != False else ('null' if values.get('challan_date') == False else (
                    'null' if self.challan_date == False and 'challan_date' not in values else f"'{self.challan_date}'"))
                deliver_person_name = values.get('deliver_person_name') or self.deliver_person_name or ''
                lr_rr_no = values.get('lr_rr_no') or self.lr_rr_no or ''
                lr_rr_date = f"'{values.get('lr_rr_date')}'" if values.get('lr_rr_date') and values.get(
                    'lr_rr_date') != False else ('null' if values.get('lr_rr_date') == False else (
                    'null' if self.lr_rr_date == False and 'lr_rr_date' not in values else f"'{self.lr_rr_date}'"))
                partner_id = f"'{values.get('partner_id')}'" if values.get('partner_id') and values.get(
                    'partner_id') != False else ('null' if values.get('partner_id') == False else (
                    'null' if self.partner_id.id == False and 'partner_id' not in values else f"'{self.partner_id.id}'"))
                mode_of_delivery = values.get('mode_of_delivery') or self.mode_of_delivery or ''
                transporter_code = f"'{values.get('transporter_code')}'" if values.get(
                    'transporter_code') and values.get('transporter_code') != False else (
                    'null' if values.get('transporter_code') == False else (
                        'null' if self.transporter_code.id == False and 'transporter_code' not in values else f"'{self.transporter_code.id}'"))

                query = f"""UPDATE stock_picking SET invoice_number = '{invoice_number}', 
                    invoice_date = {invoice_date},
                    challan_number = '{challan_number}',
                    challan_date = {challan_date},
                    deliver_person_name = '{deliver_person_name}',
                    lr_rr_no = '{lr_rr_no}',
                    lr_rr_date = {lr_rr_date},
                    partner_id = {partner_id},
                    mode_of_delivery = '{mode_of_delivery}',
                    transporter_code = {transporter_code} WHERE id = {pick.id};"""
                self.env.cr.execute(query)
        if 'store_id' in values:
            query = f"""UPDATE stock_move SET store_id = '{self.store_id.id}'
                     WHERE id in ({str(self.move_ids_without_package.ids)[1:-1]});"""
            self.env.cr.execute(query)
            
        return res

    @api.model
    def get_grn(self):
        po = self.env['purchase.order'].search([('name', '=', self.origin)])
        if po:
            return po.picking_ids.name

    @api.model
    def get_grn_date(self):
        po = self.env['purchase.order'].search([('name', '=', self.origin)])
        if po:
            return po.picking_ids.date_done.strftime("%d/%m/%Y")

    @api.model
    def get_tax(self, product_id):
        po = self.env['purchase.order'].search([('name', '=', self.origin)])
        if po and po.order_line:
            pol = self.env['purchase.order.line'].search([('product_id', '=', product_id.id), ('order_id', '=', po.id)])
            tax = pol.price_tax
            return tax

    @api.model
    def get_requisition(self):
        # print("method called=====================")
        number = []
        po = self.env['purchase.order'].search([('name', '=', self.origin)])
        # print("PO=====================",po)
        
        if po and po.requisition_ids:
            # print("inside first if============")
            if po.requisition_ids:
                # print("inside 2nd if============",po.requisition_ids,po.requisition_ids.sequence)
                
                for xx in po.requisition_ids:
                #     print("xxxxxxxxxxxxxx",xx)
                #     requisition_obj = self.env['kw_add_product_items'].browse(xx)
                #     print("obect===========================",requisition_obj)
                #     if requisition_obj:
                    number.append(xx.sequence)
                # print("number====================",number)
        return ','.join(number)

    @api.model
    def get_indent(self):
        indent = []
        po = self.env['purchase.order'].search([('name', '=', self.origin)])
        if po and po.qc_ids:
            if po.qc_ids.ids:
                for xx in po.qc_ids.ids:
                    quote_obj = self.env['kw_quotation_consolidation'].browse(xx).quotation
                    if quote_obj and quote_obj.indent:
                        # conso = max(quote_obj.indent.ids)
                        if quote_obj.indent.ids:
                            for xy in quote_obj.indent.ids:
                                conso_obj = self.env['kw_consolidation'].browse(xy)
                                if conso_obj:
                                    indent.append(conso_obj.indent_number)
        return ','.join(indent)

    # def _po_details_compute(self):
    #     for po_rec in self:
    #         po_record = self.env['purchase.order'].sudo().search([('name','=',po_rec.origin)])
    #         po_rec.vendor_bill_number = po_record.partner_ref
    #         po_rec.vendor_delivery_date_of_product = po_record.date_approve
    # po_rec.write({'vendor_bill_number': po_record.partner_ref, 'vendor_delivery_date_of_product': po_record.date_approve})

    # def button_scrap(self):
    #     self.ensure_one()
    #     view = self.env.ref('stock.stock_scrap_form_view2')
    #     products = self.env['product.product']
    #     for move in self.move_lines:
    #         if move.state not in ('draft', 'cancel') and move.product_id.type in ('product', 'consu'):
    #             products |= move.product_id
    #     return {
    #         'name': _('Damage'),
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'stock.scrap',
    #         'view_id': view.id,
    #         'views': [(view.id, 'form')],
    #         'type': 'ir.actions.act_window',
    #         'context': {'default_picking_id': self.id, 'product_ids': products.ids},
    #         'target': 'new',
    #     }
    # @api.multi
    # def send_gatepass_in_mail(self):
    #     template_id = self.env.ref('kw_inventory.send_gatepass_template')
    #     if self.id:
    #         # print("===================self",self.id)
    #         mail_res = template_id.sudo().with_context(email_from=self.env.user.employee_ids.work_email,
    #                                                    rec_id=self.id,).send_mail(self.id,
    #                                                                          notif_layout="kwantify_theme.csm_mail_notification_light")
            # self.env.user.notify_success("Gate pass sent successfully.")
       
            
    # @api.multi
    # def do_print_gatepass(self):
    #     self.write({'printed': True})
    #     return self.env.ref('kw_inventory.action_report_gate_pass').report_action(self)
    

    @api.multi
    def do_print_picking_Inspection(self):
        self.write({'printed': True})
        return self.env.ref('kw_inventory.action_report_picking_INSPECTION').report_action(self)

    @api.multi
    def do_print_picking_SRV(self):
        self.write({'printed': True})
        return self.env.ref('kw_inventory.action_report_picking_SRV').report_action(self)

    @api.multi
    def do_print_picking_GRN(self):
        self.write({'printed': True})
        return self.env.ref('kw_inventory.action_report_picking').report_action(self)

    @api.multi
    def sequence_update_from_sequence_master(self):
        indent_dept = False
        own_dept = False
        pickings = self.env['stock.picking'].search([])
        for picking in pickings:
            if picking.name.startswith('2') and len(picking.name) == 9:
                po = self.env['purchase.order'].search([('name', '=', picking.origin)])

                if po.req_id_rel:
                    requisition = max(po.req_id_rel.ids)
                    if requisition:
                        requisition_obj = self.env['kw_purchase_requisition'].browse(requisition)
                        if requisition_obj:
                            indent_dept = requisition_obj.indenting_department
                            own_dept = requisition_obj.department_name

                if picking.picking_type_id.name in ['GRN', 'INSPECTION'] and own_dept:
                    code = self.env['kw_sequence'].search([('department_id', '=', own_dept.id),
                                                           ('picking_type_id', '=', picking.picking_type_id.id)]).code
                elif picking.picking_type_id.name == 'SRV' and indent_dept:
                    code = self.env['kw_sequence'].search([('department_id', '=', indent_dept.id),
                                                           ('picking_type_id', '=', picking.picking_type_id.id)]).code
                else:
                    code = self.env['kw_sequence'].search(
                        [('department_id', '=', False), ('picking_type_id', '=', picking.picking_type_id.id)]).code

                picking.write({'name': picking.name[:3] + code + picking.name[5:]})
