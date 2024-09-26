from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _convert_prepared_anglosaxon_line(self, line, partner):
        return {
            'date_maturity': line.get('date_maturity', False),
            'partner_id': partner,
            'name': line['name'],
            'debit': line['price'] > 0 and line['price'],
            'credit': line['price'] < 0 and -line['price'],
            'account_id': line['account_id'],
            'employee_id': line.get('employee_id'),
            'department_id': line.get('department_id'),
            'budget_type': line.get('budget_type'),
            'budget_update': line.get('budget_update'),
            'project_id': line.get('project_id'),
            'analytic_line_ids': line.get('analytic_line_ids', []),
            'amount_currency': line['price'] > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
            'currency_id': line.get('currency_id', False),
            'quantity': line.get('quantity', 1.00),
            'product_id': line.get('product_id', False),
            'product_uom_id': line.get('uom_id', False),
            'analytic_account_id': line.get('account_analytic_id', False),
            'invoice_id': line.get('invoice_id', False),
            'project_wo_id' : line.get('project_wo_id',False),
            'division_id': line.get('division_id',False),
            'section_id': line.get('section_id',False),
            'budget_line': line.get('budget_line',False),
            'capital_line': line.get('capital_line',False),
            'project_line': line.get('project_line',False),
            # 'tax_ids': line.get('tax_ids', False),
            # 'tax_line_id': line.get('tax_line_id', False),
            # 'analytic_tag_ids': line.get('analytic_tag_ids', False),
        }