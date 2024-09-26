from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = "project.project"

    def open_project_issues(self):
        tree_view_id = self.env.ref('project.view_task_tree2').id
        form_view_id = self.env.ref('project.view_task_form2').id
        kanban_view_id = self.env.ref('project.view_task_kanban').id
        pivot_view_id = self.env.ref('project.view_project_task_pivot').id
        return {
            'name': _('Project Issue'),
            'view_type': 'form',
            'view_mode': 'tree,form,kanban,pivot',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form'), (kanban_view_id, 'kanban'),
                      (pivot_view_id, 'pivot')],
            'res_model': 'project.task',
            'domain': [('project_id', '=', self.id), ('is_issue', '=', True)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id, 'default_is_issue': True, 'default_is_from_project': True}
        }

    def compute_issue_count(self):
        for record in self:
            record.issue_count = self.env['project.task'].search_count(
                [('project_id', '=', self.id), ('is_issue', '=', True)])

    issue_count = fields.Integer(compute='compute_issue_count')
