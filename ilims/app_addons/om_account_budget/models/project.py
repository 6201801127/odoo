from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Project(models.Model):
    _inherit = "project.project"

    def open_budgets(self):
        xml_id = 'om_account_budget.crossovered_budget_view_tree'
        tree_view_id = self.env.ref(xml_id).id
        xml_id = 'om_account_budget.crossovered_budget_view_form'
        form_view_id = self.env.ref(xml_id).id
        return {
            'name': _('Budgets'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'res_model': 'crossovered.budget',
            'domain': [('analytic_account_id', '=', self.analytic_account_id.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_analytic_account_id': self.analytic_account_id.id, 'default_is_from_project': True}
        }

    def _budget_total(self):
        crossovered_obj = self.env['crossovered.budget']
        for project in self:
            budgets = crossovered_obj.search([('analytic_account_id', '=', project.analytic_account_id.id)])
            if budgets:
                project.budget_total = sum(budgets.mapped('crossovered_budget_line.planned_amount'))
            else:
                project.budget_total = 0.0

    budget_total = fields.Integer(compute='_budget_total', tracking=True)

    def open_budget_analysis(self):
        tree_view_id = self.env.ref('om_account_budget.view_crossovered_budget_line_tree').id
        kanban_view_id = self.env.ref('om_account_budget.view_crossovered_budget_line_kanban').id
        graph_view_id = self.env.ref('om_account_budget.view_crossovered_budget_line_graph').id
        return {
            'name': _('Budget Analysis'),
            'view_mode': 'tree,kanban,graph',
            'views': [(tree_view_id, 'tree'), (kanban_view_id, 'kanban'), (graph_view_id, 'graph')],
            'res_model': 'crossovered.budget.lines',
            'domain': [('analytic_account_id', '=', self.analytic_account_id.id)],
            'type': 'ir.actions.act_window',
        }
