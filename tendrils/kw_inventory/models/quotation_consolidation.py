from datetime import date
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons.kw_utility_tools import kw_helpers


class kw_quotation_consolidation(models.Model):
    _name = 'kw_quotation_consolidation'
    _description = "Quotation Consolidation"
    _rec_name = "qo_consolidation_no"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'id desc'

    boolean_button = fields.Boolean(string="Approve Button Boolean", default=False)
    negotiation_ids = fields.One2many('kw_negotiation', 'consolidation_id', string='Negotiation')
    date = fields.Date('Date', default=date.today())
    seq_no = fields.Char("")
    qo_consolidation_no = fields.Char('Quotation Consolidation no', required=True, default="New", readonly="1")
    quotation = fields.Many2many('kw_quotation', string="Quotation")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get('account.account'))
    state = fields.Selection([('draft', 'QC Created'),
                              ('approved', 'QC Updated'),
                              ('readyforpo', 'Ready For PO'),
                              ('invalid', 'Invalid')
                              ], string='Status', readonly=True, index=True, copy=False, default='draft',
                             track_visibility='onchange', group_expand='_expand_groups')
    order_line = fields.One2many('kw_quotation_consolidation_items', 'order_id', string='Order Lines')
    remark = fields.Text(string='Remark')
    pr_no = fields.Char(compute='_compute_quotation')
    requisition_ids = fields.Many2many('kw_requisition_requested',string='Requisition Ids')
    pr_date = fields.Char('Date', compute='_compute_quotation')
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')


    @api.depends('quotation')
    def _compute_quotation(self):
        for rec in self:
            # for quote in rec.requisition_ids:
            pr_val = map(str, rec.requisition_ids.mapped("sequence"))
            date_val = map(str, rec.requisition_ids.mapped("requisition_rel_id.date"))
            rec.pr_no=','.join(pr_val)
            rec.pr_date=','.join(date_val)
            # rec.pr_no = [
            #     (6, 0, [req.id for quote in rec.quotation for indt in quote.indent for req in indt.requisition_rel])]
            # rec.pr_date = ' '.join(
            #     [str(req.date) for quote in rec.quotation for indt in quote.indent for req in indt.requisition_rel])

    @api.model
    def create(self, vals):
        if vals.get('qo_consolidation_no', 'New') == 'New':
            vals['qo_consolidation_no'] = self.env['ir.sequence'].next_by_code('kw_quotation_consolidation') or '/'
        res = super(kw_quotation_consolidation, self).create(vals)
        if res:
            self.env.user.notify_success(message='Quotation Consolidation created successfully.')
        else:
            self.env.user.notify_danger(message='Quotation Consolidation creation failed.')
        return res

    @api.model
    def _expand_groups(self, states, domain, order):
        return ['draft', 'approved', 'readyforpo', 'invalid']

    # @api.multi
    # def write(self, vals):
    #     child_product = []
    #     true_vals = []
    #     res = super(kw_quotation_consolidation, self).write(vals)
    #     for rec in self.order_line:
    #         child_product.append(rec.product_id.id)
    #     for c in child_product:
    #         negotiation_records = self.env['kw_negotiation'].sudo().search([('product.id','=',c),('consolidation_id.id','=',self.id),('final_price','=',True)])
    #         if negotiation_records:
    #             true_vals.append('T')
    #         else:
    #             true_vals.append('F')
    #     print(true_vals)
    #     if true_vals[0] == 'T':
    #         if all(x == true_vals[0] for x in true_vals):
    #             print('hello')
    # self.write({'boolean_button': True})
    # self.boolean_button = True
    # else:
    #  self.boolean_button = False
    # self.write({'boolean_button': False})
    # else:
    #  self.boolean_button = False
    # self.write({'boolean_button': False})
    # return res

    @api.multi
    def btn_negotiation(self):
        view_id = self.env.ref('kw_inventory.kw_negotiation_view_form').id
        return {
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'form')],
            'res_model': 'kw_negotiation',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            # 'res_id':self.id,
            'target': 'new',
        }

    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })

    def amount_to_word(self, amt, curr):
        amount_in_word = kw_helpers.num_to_words(amt)
        currency_unit_label = ''
        currency_subunit_label = ''
        if curr:
            currency_unit_label = curr.currency_unit_label
            currency_subunit_label = curr.currency_subunit_label

        return f"{currency_unit_label} {amount_in_word} {currency_subunit_label if ' and ' in amount_in_word else ''}"

    @api.multi
    def btn_ready_for_po(self):
        self.write({'state': 'readyforpo'})

    @api.multi
    def move_to_quotation(self):
        wizard_form = self.env.ref('kw_inventory.kw_quotation_consolidation_wizard_view', False)
        return {
            'name': 'Remark',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': wizard_form.id,
            'res_model': 'kw_quotation_consolidation_wizard',
            'target': 'new',
            'context': {'default_ref_id': self.id}
        }

    @api.multi
    def approve(self):
        # self.write({'state': 'approved'})
        self.date=date.today()
        product_list = []
        n_ids = []
        for rec in self:
            for record in rec.negotiation_ids:
                if record.product.id not in product_list:
                    product_list.append(record.product.id)
        for product in product_list:
            negotiation_record = self.env['kw_negotiation'].sudo().search(
                ['&', '&', ('consolidation_id.id', '=', self.id), ('product.id', '=', product),
                 ('final_price', '=', True)])
            if len(negotiation_record) == 1:
                n_ids.append(negotiation_record.id)
            else:
                raise ValidationError('Final price for an item will be selected once')

        for n_id in n_ids:
            negotiation_rec = self.env['kw_negotiation'].sudo().search([('id', '=', n_id)])
            if negotiation_rec:
                negotiation_rec.write({'qc_approve_check': True})
                qc_child = self.env['kw_quotation_consolidation_items'].sudo().search(
                ['&', '&', ('order_id.id', '=', negotiation_rec.consolidation_id.id),
                 ('product_id.id', '=', negotiation_rec.product.id), ('partner_id.id', '=', negotiation_rec.vendor_id.id)])
                qc_child.write({'state':'pending','remark': '', 'approve_boolean': False})

        for record in self.negotiation_ids:
            record.write({'state': 'approve'})

        self.write({'state': 'approved'})

    @api.multi
    def reject(self):
        self.write({'state': 'rejected'})
        for record in self:
            for rec in record.quotation:
                rec.write({'state': 'negotiation'})

    @api.multi
    def unlink(self):
        for record in self:
            po_rec = self.env['purchase.order'].sudo().search([('state', 'not in', ['cancel', 'reject'])])
            if po_rec:
                for po in po_rec:
                    for rec in po.qc_ids:
                        if record.qo_consolidation_no == rec.qo_consolidation_no:
                            raise ValidationError(
                                f"Record cannot be Deleted. Quotation Consolidation No - {record.qo_consolidation_no} is referenced by Quotation No {po.name}")
        res = super(kw_quotation_consolidation, self).unlink()
        if res:
            self.env.user.notify_success(message='Quotation Consolidation deleted successfully.')
        else:
            self.env.user.notify_danger(message='Quotation Consolidation deletion failed.')
        return res
