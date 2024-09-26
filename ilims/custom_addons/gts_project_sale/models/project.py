from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = 'project.project'

    # Sale
    def open_quotation(self):
        tree_view_id = self.env.ref('sale.view_quotation_tree_with_onboarding').id
        form_view_id = self.env.ref('sale.view_order_form').id
        kanban_view_id = self.env.ref('sale.view_sale_order_kanban').id
        pivot_view_id = self.env.ref('sale.view_sale_order_pivot').id
        return {
            'name': _('Quotations'),
            'view_type': 'form',
            'view_mode': 'tree,form,kanban,pivot',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form'), (kanban_view_id, 'kanban'),
                      (pivot_view_id, 'pivot')],
            'res_model': 'sale.order',
            'domain': [('analytic_account_id', '=', self.analytic_account_id.id), ('state', 'in', ('draft', 'sent'))],
            'type': 'ir.actions.act_window',
            'context': {'default_analytic_account_id': self.analytic_account_id.id, 'default_is_from_project': True}
        }

    def open_sales(self):
        tree_view_id = self.env.ref('sale.view_order_tree').id
        form_view_id = self.env.ref('sale.view_order_form').id
        kanban_view_id = self.env.ref('sale.view_sale_order_kanban').id
        pivot_view_id = self.env.ref('sale.view_sale_order_pivot').id
        return {
            'name': _('Sales'),
            'view_type': 'form',
            'view_mode': 'tree,form,kanban,pivot',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form'), (kanban_view_id, 'kanban'),
                      (pivot_view_id, 'pivot')],
            'res_model': 'sale.order',
            'domain': [('analytic_account_id', '=', self.analytic_account_id.id), ('state', '=', 'sale')],
            'type': 'ir.actions.act_window',
            'context': {'default_analytic_account_id': self.analytic_account_id.id, 'default_is_from_project': True}
        }

    def open_invoices(self):
        sale_obj = self.env['sale.order']
        tree_view_id = self.env.ref('account.view_out_invoice_tree').id
        form_view_id = self.env.ref('account.view_move_form').id
        kanban_view_id = self.env.ref('account.view_account_move_kanban').id
        sales = sale_obj.search([('analytic_account_id', '=', self.analytic_account_id.id), ('state', '=', 'sale')])
        origin_list = []
        for sale in sales:
            origin_list.append(sale.name)
        return {
            'name': _('Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form,kanban',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form'), (kanban_view_id, 'kanban')],
            'res_model': 'account.move',
            'domain': [('state', '!=', 'cancel'),
                       ('analytic_account_id', '=', self.analytic_account_id.id), ('move_type', '=', 'out_invoice')],
            'type': 'ir.actions.act_window',
            'context': {'default_analytic_account_id': self.analytic_account_id.id, 'default_is_from_project': True,
                        'default_move_type': 'out_invoice'}
        }

    # Purchase
    def open_rfq(self):
        tree_view_id = self.env.ref('purchase.purchase_order_kpis_tree').id
        form_view_id = self.env.ref('purchase.purchase_order_form').id
        kanban_view_id = self.env.ref('purchase.view_purchase_order_kanban').id
        pivot_view_id = self.env.ref('purchase.purchase_order_pivot').id
        return {
            'name': _('Request for Quotation'),
            'view_type': 'form',
            'view_mode': 'tree,form,kanban,pivot',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form'), (kanban_view_id, 'kanban'), (pivot_view_id, 'pivot')],
            'res_model': 'purchase.order',
            'domain': [('analytic_account_id', '=', self.analytic_account_id.id),
                       ('state', 'in', ('draft', 'sent', 'to_approve'))],
            'type': 'ir.actions.act_window',
            'context': {'default_analytic_account_id': self.analytic_account_id.id, 'default_is_from_project': True}
        }

    def open_po(self):
        tree_view_id = self.env.ref('purchase.purchase_order_view_tree').id
        form_view_id = self.env.ref('purchase.purchase_order_form').id
        kanban_view_id = self.env.ref('purchase.view_purchase_order_kanban').id
        pivot_view_id = self.env.ref('purchase.purchase_order_pivot').id
        return {
            'name': _('Purchase Order'),
            'view_type': 'form',
            'view_mode': 'tree,form,kanban,pivot',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form'), (kanban_view_id, 'kanban'), (pivot_view_id, 'pivot')],
            'res_model': 'purchase.order',
            'domain': [('analytic_account_id', '=', self.analytic_account_id.id), ('state', '=', 'purchase')],
            'type': 'ir.actions.act_window',
            'context': {'default_analytic_account_id': self.analytic_account_id.id, 'default_is_from_project': True}
        }

    def open_bills(self):
        purchase_obj = self.env['purchase.order']
        tree_view_id = self.env.ref('account.view_out_invoice_tree').id
        form_view_id = self.env.ref('account.view_move_form').id
        kanban_view_id = self.env.ref('account.view_account_move_kanban').id
        purchases = purchase_obj.search([('analytic_account_id', '=', self.analytic_account_id.id),
                                         ('state', '=', 'purchase')])
        origin_list = []
        for purchase in purchases:
            origin_list.append(purchase.name)
        return {
            'name': _('Bills'),
            'view_type': 'form',
            'view_mode': 'tree,form,kanban',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form'), (kanban_view_id, 'kanban')],
            'res_model': 'account.move',
            'domain': [('state', '!=', 'cancel'),
                       ('analytic_account_id', '=', self.analytic_account_id.id), ('move_type', '=', 'in_invoice')],
            'type': 'ir.actions.act_window',
            'context': {'default_analytic_account_id': self.analytic_account_id.id, 'default_is_from_project': True,
                        'default_move_type': 'in_invoice'}
        }

    def _get_so_invoice_count(self):
        sale_obj = self.env['sale.order']
        invoice_obj = self.env['account.move']
        quotations = sale_obj.search([('analytic_account_id', '=', self.analytic_account_id.id),
                                      ('state', 'in', ('draft', 'sent'))])
        sales = sale_obj.search([('analytic_account_id', '=', self.analytic_account_id.id), ('state', '=', 'sale')])
        origin_list = []
        for sale in sales:
            origin_list.append(sale.name)
        invoices = invoice_obj.search([('state', '!=', 'cancel'),
                                       ('analytic_account_id', '=', self.analytic_account_id.id),
                                       ('move_type', '=', 'out_invoice')])
        if quotations:
            self.quotation_count = sum(quotations.mapped('amount_total'))
        else:
            self.quotation_count = 0
        if sales:
            self.sales_count = sum(sales.mapped('amount_total'))
        else:
            self.sales_count = 0
        if invoices:
            self.invoices_count = sum(invoices.mapped('amount_total'))
        else:
            self.invoices_count = 0

    def _get_po_bill_count(self):
        purchase_obj = self.env['purchase.order']
        invoice_obj = self.env['account.move']
        rfqs = purchase_obj.search([('analytic_account_id', '=', self.analytic_account_id.id),
                                    ('state', 'in', ('draft', 'sent', 'to_approve'))])
        purchase_orders = purchase_obj.search([('analytic_account_id', '=', self.analytic_account_id.id),
                                               ('state', '=', 'purchase')])
        origin_list = []
        for purchase in purchase_orders:
            origin_list.append(purchase.name)
        bills = invoice_obj.search([('state', '!=', 'cancel'),
                                    ('analytic_account_id', '=', self.analytic_account_id.id),
                                    ('move_type', '=', 'in_invoice')])
        if rfqs:
            self.rfq_count = sum(rfqs.mapped('amount_total'))
        else:
            self.rfq_count = 0
        if purchase_orders:
            self.po_count = sum(purchase_orders.mapped('amount_total'))
        else:
            self.po_count = 0
        if bills:
            self.bills_count = sum(bills.mapped('amount_total'))
        else:
            self.bills_count = 0

    quotation_count = fields.Integer(compute='_get_so_invoice_count')
    sales_count = fields.Integer(compute='_get_so_invoice_count')
    invoices_count = fields.Integer(compute='_get_so_invoice_count')
    rfq_count = fields.Integer(compute='_get_po_bill_count')
    po_count = fields.Integer(compute='_get_po_bill_count')
    bills_count = fields.Integer(compute='_get_po_bill_count')
