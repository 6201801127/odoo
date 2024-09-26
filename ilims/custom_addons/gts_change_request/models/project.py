from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = 'project.project'

    def open_change_requests(self):
        tree_view_id = self.env.ref('gts_change_request.view_change_request_tree').id
        form_view_id = self.env.ref('gts_change_request.view_change_request_form').id
        kanban_view_id = self.env.ref('gts_change_request.view_change_request_kanban').id
        pivot_view_id = self.env.ref('gts_change_request.view_change_request_pivot').id
        return {
            'name': _('Change Requests'),
            'view_type': 'form',
            'view_mode': 'tree,form,kanban,pivot',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form'), (kanban_view_id, 'kanban'),
                      (pivot_view_id, 'pivot')],
            'res_model': 'change.request',
            'domain': [('project_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id, 'default_is_from_project': True}
        }

    def _get_change_request_count(self):
        change_request_obj = self.env['change.request']
        for record in self:
            record.change_request_count = change_request_obj.search_count([('project_id', '=', record.id)])

    change_request_count = fields.Integer(compute='_get_change_request_count')
