import re
from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError


class kw_negotiation(models.Model):
    _name = 'kw_negotiation'
    _description = "A master model to create negotiation"
    _order = 'product asc, id asc'

    # approved_status = fields.Boolean(string="Approved Status")
    consolidation_id = fields.Many2one('kw_quotation_consolidation', string='Consolidation id')
    product = fields.Many2one('product.product', string="Product", required=True)
    product_uom = fields.Char(related='product.uom_id.name')
    product_name = fields.Char(related='product.name', string="Name")
    consolidation_item_id = fields.Many2one('kw_quotation_consolidation_items', string='Consolidation items')
    unit_price = fields.Float(string="Unit Price")
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True)
    payment_terms = fields.Many2one('account.payment.term', string='Payment Terms',
                                    readonly=True,
                                    store=True,
                                    )
                                    # related='vendor_id.property_supplier_payment_term_id',
    description = fields.Char(string="Description")
    attachment = fields.Binary(string='Attachment')
    file_name = fields.Char("Attachment Name")
    final_price = fields.Boolean(string='Final Price', default=False)
    currency_id = fields.Many2one('res.currency', string='Currency')
    # negotiation_no = fields.Char(string="Negotiation Number")
    qo_no = fields.Many2many('kw_quotation', string="Quotation Number")
    schedule_date = fields.Date(string="Date", default=date.today())
    quantity = fields.Float(string="Quantity")
    total = fields.Monetary(string="Total", currency_field='currency_id')
    negotiation_mode = fields.Many2one('kw_negotiation_mode_master', string='Mode Of Negotiation')
    # last_procrument_price = fields.Char(string="Last Procurement Price")
    qc_approve_check = fields.Boolean(string='QC Approve check')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
        ('final', 'Final Price'),
    ], string='Status', readonly=True, index=True, copy=False, default="draft")
    # readonly_field = fields.Boolean(string='ReadOnly Field',default=False)
    invisible_boolean = fields.Boolean(string='Invisible Boolean')
    cs = fields.Text(string='Comparative Statement')
    price_tax = fields.Float(compute='_compute_price', string='Tax')
    price_total = fields.Monetary(compute='_compute_price', string='Total')
    price_subtotal = fields.Monetary(compute='_compute_price', string='Sub Total')
    
    
    @api.depends('product', 'vendor_id','unit_price','quantity')
    def _compute_price(self):
        for line in self:
            if line.consolidation_id:
                product = line.consolidation_id.order_line.filtered(lambda x: x.product_id.id==line.product.id and x.partner_id.id==line.vendor_id.id)
                # print("product====================",product)
                if product:
                    line.price_tax = product.price_tax
                    line.price_subtotal =line.unit_price * line.quantity
                    line.price_total = product.price_tax + (line.unit_price * line.quantity)
                else:
                    line.price_tax = 0
                    line.price_total = 0
            else:
                line.price_tax = 0
                line.price_total = 0

    @api.onchange('vendor_id')
    def onchange_payment_terms(self):
        for rec in self:
            if not rec.vendor_id :
                rec.payment_terms = rec.vendor_id.property_supplier_payment_term_id
    
    @api.multi
    def btn_delete(self):
        return super(kw_negotiation, self).unlink()

    @api.multi
    @api.constrains('unit_price')
    def _check_values(self):
        for rec in self:
            # if rec.quantity == 0.0:
            #     raise ValidationError('Quantity should not be zero.')
            if rec.unit_price == 0.0:
                raise ValidationError('Quoted Price should not be zero.')

    @api.onchange('consolidation_id')
    def _onchange_consolidation_id(self):
        lst = []
        vendor_list = []

        for consolidation_item_id in self.consolidation_id.order_line:
            if consolidation_item_id.product_id.id not in lst:
                lst.append(consolidation_item_id.product_id.id)
            if consolidation_item_id.partner_id.id not in vendor_list:
                vendor_list.append(consolidation_item_id.partner_id.id)
        for rec in self.consolidation_id.negotiation_ids:
            if rec.product.id in lst and rec.final_price == True:
                lst.remove(rec.product.id)

        return {'domain': {'product': [('id', 'in', lst)], 'vendor_id': [('id', 'in', vendor_list)]}}

    @api.onchange('product')
    def _onchange_product_id(self):
        qc_items = self.env['kw_quotation_consolidation_items'].sudo().search([('product_id', '=', self.product.id),('order_id','=',self.consolidation_id.id)],limit=1)
        qc_items = self.env['kw_negotiation'].sudo().search([('id', 'in', self.consolidation_id.negotiation_ids.ids),('product','=',self.product.id)],limit=1)
        # qc_items = self.env['kw_quotation_consolidation'].sudo().search([('id','=',self.consolidation_id.id)])
        self.quantity = qc_items.quantity
        # self.quantity = qc_items.negotiation_ids.filtered(lambda x: x.product.id == self.product.id).quanity
        

    @api.multi
    def create(self, vals):
        child_product = []
        true_vals = []
        res = super(kw_negotiation, self).create(vals)
        # print('the res value is',res.consolidation_id)
        # print('res product id is',res.product.id)
        # print('res vendor id is',res.vendor_id.id)

        for res_record in res:
            neg_rec = self.env['kw_negotiation'].sudo().search(['&', ('product.id', '=', res_record.product.id), (
                'consolidation_id.id', '=', res_record.consolidation_id.id)])
            if neg_rec:
                for n in neg_rec:
                    n.update({'invisible_boolean': True})

            neg_records = self.env['kw_negotiation'].sudo().search(['&', ('product.id', '=', res_record.product.id), (
                'consolidation_id.id', '=', res_record.consolidation_id.id)], order='id asc', limit=1)
            # print(neg_records, "neg records--------")
            neg_records.update({'invisible_boolean': False})

            qc_child = self.env['kw_quotation_consolidation_items'].sudo().search(
                ['&', '&', ('order_id.id', '=', res_record.consolidation_id.id),
                 ('product_id.id', '=', res_record.product.id), ('partner_id.id', '=', res_record.vendor_id.id)])
            if qc_child:
                qc_child.update({'price_unit': res_record.unit_price})
            cons_rec = self.env['kw_quotation_consolidation'].sudo().search(
                [('id', '=', res_record.consolidation_id.id)])
            if cons_rec:
                con = self.env['kw_quotation_consolidation_items'].sudo().search([('order_id.id', '=', cons_rec.id)])
                for rec in cons_rec.order_line:
                    if rec.product_id.id not in child_product:
                        child_product.append(rec.product_id.id)
                for c in child_product:
                    negotiation_records = self.env['kw_negotiation'].sudo().search(
                        [('product.id', '=', c), ('consolidation_id.id', '=', res_record.consolidation_id.id),
                         ('final_price', '=', True)])
                    if negotiation_records:
                        true_vals.append('T')
                    else:
                        true_vals.append('F')

                # print(true_vals)
                if true_vals[0] == 'T':
                    if all(x == true_vals[0] for x in true_vals):
                        cons_rec.write({'boolean_button': True})
                    else:
                        cons_rec.write({'boolean_button': False})
                else:
                    cons_rec.write({'boolean_button': False})

        return res

    @api.multi
    def write(self, vals):
        child_product = []
        true_vals = []
        res = super(kw_negotiation, self).write(vals)
        # print('the res value is',self.consolidation_id)
        cons_rec = self.env['kw_quotation_consolidation'].sudo().search([('id', '=', self.consolidation_id.id)])
        if cons_rec:
            for rec in cons_rec.order_line:
                if rec.product_id.id not in child_product:
                    child_product.append(rec.product_id.id)
            for c in child_product:
                negotiation_records = self.env['kw_negotiation'].sudo().search(
                    [('product.id', '=', c), ('consolidation_id.id', '=', self.consolidation_id.id),
                     ('final_price', '=', True)])
                if negotiation_records:
                    true_vals.append('T')
                else:
                    true_vals.append('F')

            if true_vals[0] == 'T':
                if all(x == true_vals[0] for x in true_vals):
                    cons_rec.write({'boolean_button': True})
                else:
                    cons_rec.write({'boolean_button': False})
            else:
                cons_rec.write({'boolean_button': False})

        return res


class kw_negotiation_mode_master(models.Model):
    _name = 'kw_negotiation_mode_master'
    _description = "A master model to create mode of negotiation"
    _rec_name = "mode"

    mode = fields.Char("Mode Of Negotiation", required=True)

    @api.constrains('mode')
    def check_mode(self):
        for mode_neg in self:
            duplicate = self.env['kw_negotiation_mode_master'].sudo().search([('mode', '=', mode_neg.mode)]) - self
            if duplicate:
                raise ValidationError('This mode of negotiation is already exists.')
