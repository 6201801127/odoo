import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp


class kw_quotation_consolidation_items(models.Model):
    _name = 'kw_quotation_consolidation_items'
    _description = "Quotation Consolidation"
    _order = 'product_id asc'

    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Text(string='Description')
    date_planned = fields.Date(string='Date', required=True)
    partner_id = fields.Many2one('res.partner', string='Vendor')
    product_qty = fields.Float(string='Quantity')
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')
    price_unit = fields.Float(string='Unit Price', required=True,digits=dp.get_precision('Product Price'))
    last_pp = fields.Char(string="Last Procurement Price")
    taxes_id = fields.Many2many('account.tax', string='Taxes')
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, string='Currency', readonly=True)
    order_id = fields.Many2one('kw_quotation_consolidation', string='Order Reference', required=True,
                               ondelete='cascade')
    quotation_record_id = fields.Integer(string='Quotation Record Id')
    remark = fields.Text(string="Remark")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
        ('pending', 'Pending for Approval'),
        ('reject', 'Rejected'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft',group_expand='_expand_groups')
    approve_boolean = fields.Boolean(string="Approve Boolean", default=False)
    invisible_boolean = fields.Boolean(string='Invisible Boolean')
    prd_attachment = fields.Binary(string="Attachment")
    file_name = fields.Char("Attachment Name")
    po_create = fields.Boolean("PO Create", default=False)


    def open_form_view(self):
        form_view_id = self.env.ref('kw_inventory.kw_quotation_consolidation_view_form').id
        return {
            'res_model': 'kw_quotation_consolidation',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.order_id.id,
            'view_id': form_view_id,
            'target': 'new',
            'context':{'create':False,'edit':False}
        }

    @api.model
    def _expand_groups(self, states, domain, order):
        return ['draft','pending','approve', 'reject']

    @api.multi
    def negotiation_approve(self):
        form_view_id = self.env.ref('kw_inventory.kw_approve_reason_form_view').id
        return {
            'name': ' Remark',
            'res_model': 'kw_quotation_consolidation_items',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new'
        }

    @api.multi
    def negotiation_reject(self):
        self.remark = ""
        form_view_id = self.env.ref('kw_inventory.kw_reject_reason_form_view').id
        return {
            'name': ' Remark',
            'res_model': 'kw_quotation_consolidation_items',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new'
        }

    @api.multi
    def give_approve_remark(self):
        self.write({'state': 'approve', 'remark': self.remark})
        cons_childids = self.env['kw_quotation_consolidation_items'].sudo().search(
            ['&', ('order_id.id', '=', self.order_id.id),
             ('product_id.id', '=', self.product_id.id)])
        for cons_rec in cons_childids:
            cons_rec.write({'approve_boolean': True})

    @api.multi
    def give_reject_remark(self):
        self.write({'remark': self.remark})
        # cons_childids = self.env['kw_quotation_consolidation_items'].sudo().search(
        #     ['&', ('order_id.id', '=', self.order_id.id),
        #      ('product_id.id', '=', self.product_id.id)])
        # for cons_rec in cons_childids:
        self.write({'state': 'reject'})

        negotiation_search = self.env['kw_negotiation'].sudo().search(
            ['&', ('product.id', '=', self.product_id.id), ('consolidation_id.id', '=', self.order_id.id)])
        if negotiation_search:
            for rec in negotiation_search:
                rec.write({'state': 'draft'})
                if rec.final_price == True:
                    rec.final_price = False

        self.order_id.state = 'draft'

        self.env['kw_negotiation_log'].create({'product_id': self.product_id.id,
                                               'name': self.name,
                                               'partner_id': self.partner_id.id,
                                               'product_qty': self.product_qty,
                                               'product_uom': self.product_uom.id,
                                               'price_unit': self.price_unit,
                                               'reject_remark': self.remark,
                                               'consolidation_id': self.order_id.id,
                                               })

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    def _prepare_compute_all_values(self):
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.order_id.currency_id,
            'product_qty': self.product_qty,
            'product': self.product_id,
            'partner': self.partner_id,
        }

    @api.multi
    def create(self, vals):
        res = super(kw_quotation_consolidation_items, self).create(vals)

        for res_record in res:
            qc_child = self.env['kw_quotation_consolidation_items'].sudo().search(
                ['&', ('product_id.id', '=', res_record.product_id.id), ('order_id.id', '=', res_record.order_id.id)])
            if qc_child:
                for child in qc_child:
                    child.update({'invisible_boolean': True})

            qc_child_record = self.env['kw_quotation_consolidation_items'].sudo().search(
                ['&', ('product_id.id', '=', res_record.product_id.id), ('order_id.id', '=', res_record.order_id.id)],
                order='id asc', limit=1)
            qc_child_record.update({'invisible_boolean': False})

        return res
