from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = "project.project"


    def open_analytics(self):
        xml_id = 'analytic.view_account_analytic_line_pivot'
        pivot_view_id = self.env.ref(xml_id).id
        # xml_id = 'om_account_budget.crossovered_budget_view_form'
        # form_view_id = self.env.ref(xml_id).id
        print(self.analytic_account_id.id, '------')
        return {
            'name': _('Analytic Account'),
            'view_type': 'pivot',
            'view_mode': 'pivot',
            'views': [(pivot_view_id, 'pivot')],
            'res_model': 'account.analytic.line',
            'domain': [('account_id', '=', self.analytic_account_id.id)],
            'type': 'ir.actions.act_window',
            # 'context': {'default_analytic_account_id': self.analytic_account_id.id}
        }

    def _get_analytic_amount_count(self):
        analytic_obj = self.env['account.analytic.line']
        analytics_account_line = analytic_obj.search([('account_id', '=', self.analytic_account_id.id)])
        print(analytics_account_line, 'analytics_account_line')

        if analytics_account_line:
            self.cost_analysis = sum(analytics_account_line.mapped('amount'))
            print(self.cost_analysis, '==========')
        else:
            self.cost_analysis = 0
            print('hello')

    cost_analysis = fields.Integer(compute='_get_analytic_amount_count')
