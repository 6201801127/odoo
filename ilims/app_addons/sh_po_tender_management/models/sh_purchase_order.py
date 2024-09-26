# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _


class ShPurchase(models.Model):
    _inherit = 'purchase.order'

    agreement_id = fields.Many2one('purchase.agreement', 'Purchase Tender')
    cancel_lines = fields.Boolean(
        "Cancel Lines", compute='_compute_cancel_lines', store=True)
    selected_order = fields.Boolean("Selected Orders")
    sh_msg = fields.Char("Message", compute='_compute_sh_msg')
    technical_marks = fields.Integer('Technical Marks', tracking=True)
    financial_marks = fields.Integer('Financial Marks', tracking=True)
    total_marks = fields.Integer('Total Marks', tracking=True)
    sh_technical_attachment = fields.Binary(string='Technical Document', attachment=True)
    sh_technical_attachment_name = fields.Char(string="Technical Document Name")
    sh_financial_attachment = fields.Binary(string='Financial Document', attachment=True)
    sh_financial_attachment_name = fields.Char(string="Financial Document Name")
    technical_visible = fields.Boolean('Technical Visible', compute='_compute_technical_visible')
    financial_visible = fields.Boolean('Financial Visible', compute='_compute_technical_visible')

    @api.depends('agreement_id', 'agreement_id.state')
    def _compute_technical_visible(self):
        for record in self:
            record.technical_visible = False
            record.financial_visible = False
            if record.agreement_id:
                if record.agreement_id.state not in ('draft', 'confirm', 'bid_selection'):
                    record.technical_visible = True
                if record.agreement_id.state in ('financial_bid', 'financial_bid_published', 'closed', 'cancel'):
                    record.financial_visible = True

    @api.depends('partner_id')
    def _compute_sh_msg(self):
        if self:
            for rec in self:
                rec.sh_msg = ''
                if rec.agreement_id and rec.partner_id.id not in rec.agreement_id.partner_ids.ids:
                    rec.sh_msg = 'Vendor you have selected not exist in selected tender. You can still create quotation for that.'

    def _compute_cancel_lines(self):
        if self:
            for rec in self:
                if rec.state == 'cancel':
                    rec.cancel_lines = True
                else:
                    rec.cancel_lines = False


class ShPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    status = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                               ('cancel', 'Cancel')], string="State", default='draft')
    agreement_id = fields.Many2one(
        'purchase.agreement', 'Purchase Tender', related='order_id.agreement_id', store=True)
    cancel_lines = fields.Boolean(
        "Cancel Lines", related='order_id.cancel_lines', store=True)

    def action_confirm(self):
        if self:
            for rec in self:
                rec.status = 'confirm'

    def action_cancel(self):
        if self:
            for rec in self:
                rec.status = 'cancel'

    def action_update_qty(self):
        if self:
            return {
                'name': _('Change Quantity'),
                'type': 'ir.actions.act_window',
                'res_model': 'update.qty',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new'
            }
