# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp


class kw_quotation(models.Model):
    _name = "kw_quotation"
    _description = "Quotation"
    _rec_name = "qo_no"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'id desc'

    @api.multi
    def _compute_amount_in_word(self):
        for rec in self:
            rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'

    num_word = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')
    narration = fields.Text(string="Narration")
    qo_no = fields.Char('Quotation Reference', required=True, default="New", readonly="1")
    partner_id = fields.Many2one('res.partner', string='Vendor', track_visibility='always')
    partner_ref = fields.Char('Vendor Reference')
    requisition_ids = fields.Many2many('kw_requisition_requested', string="Requisitions")
    indent = fields.Many2many('kw_consolidation', string="Indent")
    date_order = fields.Date('Order Date', required=True, default=date.today(), )
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.user.company_id.id)
    order_line = fields.One2many('kw_quotation_items', 'order_id', string='Order Lines')
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('approved', 'Approved'),
        ('sent', 'RFQ Sent'),
        ('response', 'Response Received'),
        ('negotiation', 'Negotiation'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    user_id = fields.Many2one('res.users', string='Quotation Representative', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user)
    dest_address_id = fields.Many2one('res.partner', string='Drop Ship Address')
    vendor_required = fields.Boolean(string="Vendor True", default=True)
    approve_status = fields.Boolean(string="Approval_status", default=False)
    quotation_item_state = fields.Boolean(string="State", compute='_compute_quotation_state')
    qo_attachment = fields.Binary(string="Attachment")
    file_name = fields.Char("Attachment Name")
    notes = fields.Text('Terms and Conditions')

    contact_prsn_name = fields.Char('Contact Person Name')
    contact_prsn_number = fields.Char('Contact Person Number')

    @api.multi
    def _compute_quotation_state(self):
        for record in self:
            if record.state == "negotiation":
                record.quotation_item_state = True
            else:
                record.quotation_item_state = False

    @api.model
    def create(self, vals):
        if vals.get('qo_no', 'New') == 'New':
            vals['qo_no'] = self.env['ir.sequence'].next_by_code('kw_quotation') or '/'
        return super(kw_quotation, self).create(vals)

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

    @api.onchange("indent")
    def _change_items(self):
        for record in self:
            record.order_line = False
            for rec in record.indent:
                if rec.add_product_consolidation_rel:
                    vals = []
                    val = []
                    for items in rec.add_product_consolidation_rel:
                        product = self.env['product.product'].sudo().search([('id', '=', items.item_code.id)])
                        # print(items.id)
                        val.append(items.id)
                        unit = product.uom_id.id
                        vals.append([0, 0, {
                            'product_id': items.item_code.id,
                            'name': items.item_description,
                            'product_qty': items.quantity_required,
                            'date_planned': date.today(),
                            'product_uom': unit,
                            'indent_record_id': [[6, False, [items.id]]],
                            'price_unit': 0,
                        }])
                    record.order_line = vals
                else:
                    record.order_line = False

    @api.multi
    def action_rfq_send(self):
        """
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        """
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        template_id = self.env.ref('kw_inventory.kw_inventory_send_mail_rfq').id
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'kw_quotation',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'mark_rfq_as_sent': True,
        })

        # In the case of a RFQ or a PO, we want the "View..." button in line with the state of the
        # object. Therefore, we pass the model description in the context, in the language in which
        # the template is rendered.
        lang = self.env.context.get('lang')
        if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
            template = self.env['mail.template'].browse(ctx['default_template_id'])
            if template and template.lang:
                lang = template._render_template(template.lang, ctx['default_model'], ctx['default_res_id'])

        self = self.with_context(lang=lang)
        if self.state in ['draft', 'sent']:
            ctx['model_description'] = _('Request for Quotation')
        else:
            ctx['model_description'] = _('Purchase Order')
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_rfq_as_sent'):
            self.filtered(lambda o: o.state == 'approved').write({'state': 'sent'})
        return super(kw_quotation, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    @api.multi
    def kw_print_quotation(self):
        return self.env.ref('kw_inventory.kw_print_quotation').report_action(self)

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def btn_response(self):
        self.write({'state': 'response'})
    @api.multi
    def send_by_post(self):
        self.write({'state': 'sent'})

    @api.multi
    def approve(self):
        self.write({'state': 'approved', 'date_order': date.today()})
       
    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})
        return {}

    @api.multi
    def button_confirm(self):
        self.write({'state': 'purchase'})

    @api.multi
    def unlink(self):
        for record in self:
            qo_c_no_rec = self.env['kw_quotation_consolidation'].sudo().search([])
            if qo_c_no_rec:
                for qc in qo_c_no_rec:
                    for rec in qc.quotation:
                        if record.qo_no == rec.qo_no:
                            raise ValidationError(
                                f"Record cannot be Deleted.Quotation No - {record.qo_no} is referenced by Quotation Consolidation No {qc.qo_consolidation_no}")

        return super(kw_quotation, self).unlink()
