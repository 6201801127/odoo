from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = 'project.project'

    def open_acceptance(self):
        tree_view_id = self.env.ref("gts_acceptance_management.acceptance_inspection_tree_view").id
        form_view_id = self.env.ref("gts_acceptance_management.acceptance_inspection_form_view").id
        kanban_view_id = self.env.ref("gts_acceptance_management.acceptance_inspection_kanban_view").id
        pivot_view_id = self.env.ref("gts_acceptance_management.acceptance_inspection_pivot_view").id
        return {
            'name': _('Acceptance'),
            'view_type': 'form',
            'view_mode': 'kanban,tree,form,pivot',
            'views': [(kanban_view_id, 'kanban'), (tree_view_id, 'tree'), (form_view_id, 'form'), (pivot_view_id, 'pivot')],
            'res_model': 'acceptance.inspection',
            'domain': [('project_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id, 'default_is_from_project': True}
        }

    def _get_acceptance_count(self):
        acceptance_inception_obj = self.env['acceptance.inspection']
        for record in self:
            record.acceptance_count = acceptance_inception_obj.search_count([('project_id', '=', record.id)])

    acceptance_count = fields.Integer(compute='_get_acceptance_count')
