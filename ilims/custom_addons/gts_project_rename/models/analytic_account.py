# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_account_id = fields.Many2one('account.analytic.account', string='Project Name',
                                          index=True, compute="_compute_analytic_account", store=True, readonly=False,
                                          check_company=True, copy=True)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Project Tags',
                                        compute="_compute_analytic_account", store=True, readonly=False,
                                        check_company=True, copy=True)



class SaleOrder(models.Model):
    _inherit = "sale.order"

    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Project Name',
        readonly=True, copy=False, check_company=True,  # Unrequired company
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="The analytic account related to a sales order.")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag', string='Project Tags',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    account_analytic_id = fields.Many2one('account.analytic.account', store=True, string='Project Name',
                                          compute='_compute_analytic_id_and_tag_ids', readonly=False)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', store=True, string='Project Tags',
                                        compute='_compute_analytic_id_and_tag_ids', readonly=False)
