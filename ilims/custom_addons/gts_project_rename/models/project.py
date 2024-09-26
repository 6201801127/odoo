from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Project(models.Model):
    _inherit = "project.project"

    # def open_sales(self):
    #     tree_view_id = self.env.ref('sale.view_order_tree').id
    #     form_view_id = self.env.ref('sale.view_order_form').id
    #     return {
    #         'name': _('Sales'),
    #         'view_type': 'form',
    #         'view_mode': 'tree,form',
    #         'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
    #         'res_model': 'sale.order',
    #         'domain': [('analytic_account_id', '=', self.analytic_account_id.id)],
    #         'type': 'ir.actions.act_window',
    #         'context': {'default_analytic_account_id': self.analytic_account_id.id}
    #     }

    def open_purchases(self):
        tree_view_id = self.env.ref('purchase.purchase_order_tree').id
        form_view_id = self.env.ref('purchase.purchase_order_form').id
        return {
            'name': _('Purchases'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'res_model': 'purchase.order',
            'domain': [('analytic_account_id', '=', self.analytic_account_id.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_analytic_account_id': self.analytic_account_id.id}
        }

    def _analysis_total(self):
        sale_obj = self.env['sale.order']
        purchase_obj = self.env['purchase.order']
        for project in self:
            sales = sale_obj.search_count([('analytic_account_id', '=', project.analytic_account_id.id)])
            if sales:
                project.sales_total = sum(sales.mapped('amount_total'))
            else:
                project.sales_total = 0.0
            # purchases = purchase_obj.search_count([('analytic_account_id', '=', project.analytic_account_id.id)])
            # if purchases:
            #     project.purchases_total = sum(purchases.mapped('amount_total'))
            # else:
            #     project.purchases_total = 0.0

    sales_total = fields.Integer(compute='_analysis_total')
    user_id = fields.Many2one('res.users', string='Project Manager', default=False, tracking=True)

    # purchases_total = fields.Integer(compute='_analysis_total')
