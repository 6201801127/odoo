from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = 'project.project'

    def open_quality_control(self):
        tree_view_id = self.env.ref("quality_control_oca.qc_inspection_tree_view").id
        form_view_id = self.env.ref("quality_control_oca.qc_inspection_form_view").id
        kanban_view_id = self.env.ref("quality_control_oca.qc_inspection_kanban_view").id
        pivot_view_id = self.env.ref("quality_control_oca.qc_inspection_pivot_view").id
        return {
            'name': _('Quality Control'),
            'view_type': 'form',
            'view_mode': 'kanban,tree,form,pivot',
            'views': [(kanban_view_id, 'kanban'), (tree_view_id, 'tree'), (form_view_id, 'form'),
                      (pivot_view_id, 'pivot')],
            'res_model': 'qc.inspection',
            'domain': [('project_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id, 'default_is_from_project': True}
        }

    def _get_quality_control_count(self):
        qc_inception_obj = self.env['qc.inspection']
        for record in self:
            record.quality_control_count = qc_inception_obj.search_count([('project_id', '=', record.id)])

    quality_control_count = fields.Integer(compute='_get_quality_control_count', tracking=True)
