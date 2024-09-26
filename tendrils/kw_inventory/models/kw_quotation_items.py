from datetime import datetime
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp


class kw_quotation_items(models.Model):
    _name = 'kw_quotation_items'
    _description = 'Quotation Items'

    # negotiation_id = fields.Many2one('kw_negotiation',string="Negotiation id")
    negotiation_mode = fields.Selection(string='Mode Of Negotiation',
                                        selection=[('phone', 'By Phone'), ('mail', 'By Mail')])
    description = fields.Char(string="Description")
    attachment = fields.Binary(string='Attachment')
    last_procrument_price = fields.Char(string="Last Procurement Price")
    final_price = fields.Boolean(string='Final Price')
    compute_stages = fields.Boolean(string="Stages compute", compute="_compute_stages")
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Text(string='Description')
    date_planned = fields.Date(string='Date', required=True)
    company_id = fields.Many2one('res.company', string='Company', related='order_id.company_id',
                                 readonly=True,
                                 store=True, )
    product_qty = fields.Float(string='Quantity')
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'))
    taxes_id = fields.Many2many('account.tax', string='Taxes')
    order_id = fields.Many2one('kw_quotation', string='Order Reference', required=True, ondelete='cascade')
    quotation_number = fields.Char(string="Quotation Number", related="order_id.qo_no")
    quotation_state = fields.Selection(related='order_id.state', readonly=True, store=True)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    last_pp = fields.Char(string="Last Procurement Price")
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, string='Currency', readonly=True)
    indent_record_id = fields.Many2many('kw_add_product_consolidation', string='Indent Id')
    items_record_ids = fields.Many2many('kw_requisition_requested', string='Items Id')
    # calculate_quantity = fields.Char(compute='compute_quantity',string='Calculate Quantity')
    status = fields.Selection([('approved', 'Approved'), ('rejected', 'Reject')], string="Status")
    vendor_id = fields.Many2one(string="Vendor", related='order_id.partner_id')
    remark = fields.Text(string="Remark")

    @api.multi
    def _compute_stages(self):
        for record in self:
            if record.order_id.state == "negotiation":
                record.compute_stages = True
            else:
                record.compute_stages = False

    def btn_approve(self):
        form_view_id = self.env.ref("kw_inventory.kw_quotation_design_approve_remark_form_view").id
        return {
            'name': 'Quotation Approve',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(form_view_id, 'form')],
            'res_model': 'kw_quotation_items',
            'view_id': form_view_id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }

    def btn_reject(self):
        form_view_id = self.env.ref("kw_inventory.kw_quotation_design_reject_remark_form_view").id
        return {
            'name': 'Quotation Reject',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(form_view_id, 'form')],
            'res_model': 'kw_quotation_items',
            'view_id': form_view_id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }

    def btn_quotation_remark_approve(self):
        for record in self:
            record.update({'remark': record.remark, 'status': 'approved'})

    def btn_quotation_remark_reject(self):
        for rec in self:
            rec.update({'remark': rec.remark, 'status': 'rejected', 'final_price': False})

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
            # print("taxes===",line,line.taxes_id,taxes)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.onchange("product_id")
    def _set_description(self):
        for record in self:
            if record.product_id:
                record.name = record.product_id.name
                record.date_planned = date.today()
                record.product_uom = record.product_id.uom_id

    def _prepare_compute_all_values(self):
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.order_id.currency_id,
            'product_qty': self.product_qty,
            'product': self.product_id,
            'partner': self.order_id.partner_id,
        }

    # @api.multi
    # @api.depends('product_qty')
    # def compute_quantity(self):
    #     for record in self:
    #         a = 0
    #         total_qty = 0
    #         quotation_rec = self.env['kw_quotation_items'].sudo().search([('indent_record_id','=',record.indent_record_id)])
    #         for rec in quotation_rec:
    #             a = a + rec.product_qty

    #         indent_rec = self.env['kw_add_product_consolidation'].sudo().search([('id','=',record.indent_record_id)])

    #         b = indent_rec.quantity_required - a
    #         indent_rec.write({'quantity_onorder': a,'quantity_balance':b})

    # @api.model
    # def create(self, vals):
    #     new_record =  super(kw_quotation_items, self).create(vals)

    #     for record in new_record:
    #         a = 0
    #         total_qty = 0
    #         quotation_rec = self.env['kw_quotation_items'].sudo().search([('indent_record_id','=',record.indent_record_id)])
    #         for rec in quotation_rec:
    #             a = a + rec.product_qty

    #         indent_rec = self.env['kw_add_product_consolidation'].sudo().search([('id','=',record.indent_record_id)])
    #         b = indent_rec.quantity_required - a
    #         indent_rec.write({'quantity_onorder': a,'quantity_balance':b})

    #     return new_record

    @api.constrains('product_qty')
    def validate_qty(self):
        for record in self:
            if record.product_qty == 0:
                raise ValidationError("Quantity cannot be 0")

    # @api.multi
    # def unlink(self):
    #     print('unlink method called')
    #     for rec in self:
    #         a = 0
    #         total_qty = 0
    #         indent_rec = rec.indent_record_id
    #         record = super(kw_quotation_items, rec).unlink()
    #         quotation_rec = self.env['kw_quotation_items'].sudo().search([('indent_record_id','=',indent_rec)])
    #         if quotation_rec:
    #             for r in quotation_rec:
    #                 a = a + r.product_qty
    #         else:
    #             a = 0

    #         indent = self.env['kw_add_product_consolidation'].sudo().search([('id','=',indent_rec)])
    #         b = indent.quantity_required - a
    #         indent.write({'quantity_onorder': a,'quantity_balance':b})
