from odoo import fields, models, api, _


class UseCaseMapping(models.Model):
    _name = 'kw_use_case_mapping'
    _description = 'Use Case Mapping'
    _rec_name = 'project_id'

    def _get_project(self):
        projects = self.env['kw_bug_life_cycle_conf_user_field'].search(
            [('employee_id', '=', self.env.user.employee_ids.id), ('user_type', 'in', ['Test Lead'])]).mapped(
            'cycle_bug_conf_id.project_id')
        return [('project_id.id', 'in', projects.ids)]

    project_id = fields.Many2one('kw_bug_life_cycle_conf', string='Project', required=True, domain=_get_project)
    p_id = fields.Integer(related='project_id.project_id.id')
    module_id = fields.Many2one('kw_project.module', string='Module', required=True,
                                domain="[('project_id.id', '=', p_id)]")
    uc_line_ids = fields.One2many('kw_use_case_lines', 'use_case_mapping_id', string="UCs")

    @api.onchange('project_id')
    def _onchange_(self):
        self.module_id = False


class MappedUseCase(models.Model):
    _name = 'kw_use_case_lines'
    _description = 'Mapped Use Case'
    _rec_name = 'use_case_id'

    use_case_id = fields.Many2one('kw_bug_life_cycle_conf', string='Use Case', required=True)
    module_id = fields.Many2many('bug_module_master', string='Module')
    use_case_mapping_id = fields.Many2one('kw_use_case_mapping')
