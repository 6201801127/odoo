from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class TestCaseReview(models.Model):
    _name = 'kw_test_case_review'
    _description = 'Test Case Review'
    _rec_name = 'project_id'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    def _get_project(self):
        projects = self.env['kw_bug_life_cycle_conf_user_field'].search(
            [('employee_id', '=', self.env.user.employee_ids.id), ('user_type', 'in', ['Test Lead', 'Tester'])]).mapped(
            'cycle_bug_conf_id.project_id')
        return [('project_id.id', 'in', projects.ids)]

    def _get_module_domain(self):
        if self.project_id:
            permitted_modules = self.env['module_access'].search([
                ('module_access_id.project_id', '=', self.project_id.id),
                ('test_case_execution_perm', '=', True)
            ]).mapped('module_id.id')
            return [('id', 'in', permitted_modules)]
        else:
            return [('id', '=', False)]

    testing_level = fields.Many2one('testing_level_config_master', string='Testing Level',
                                    domain="[('name','in',['SIT', 'Component', 'Functional'])]")
    project_id = fields.Many2one('kw_bug_life_cycle_conf', string='Project', required=True, domain=_get_project)
    module_id = fields.Many2one('bug_module_master', string='Global Link', required=True,
                                domain=_get_module_domain)
    fetch_from = fields.Selection([('mine', 'Self'), ('colleagues', 'Colleagues')], string="Fetch From", default='mine')
    fetch_bool = fields.Boolean()
    review_data_line_ids = fields.One2many('kw_test_case_data_line', 'case_review_id', string='Data Lines')

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.module_id = False
        return {'domain': {'module_id': self._get_module_domain()}}
    
    def button_fetch_for_review(self):
        if self.project_id and self.module_id and self.fetch_from == 'mine':
            existing_case_ids = self.review_data_line_ids.mapped('id')
            data = self.env['kw_test_case_upload'].sudo().search([
                ('testing_level', '=', self.testing_level.id),
                ('project_id', '=', self.project_id.id),
                ('module_id', '=', self.module_id.id),
                ('create_uid', '=', self.env.user.id)
            ])
            all_data = self.env['kw_test_case_data_line'].sudo().search([
                ('case_upload_id', 'in', data.ids), ('case_review_id', '=', False)
            ])
            if all_data:
                for rec in all_data:
                    if rec.id not in existing_case_ids:
                        rec.case_review_id = self.id
                self.fetch_bool = True
            else:
                raise ValidationError('No Data Found.')

        elif self.project_id and self.module_id and self.fetch_from == 'colleagues':
            existing_case_ids = self.review_data_line_ids.mapped('id')
            data = self.env['kw_test_case_upload'].sudo().search([('testing_level', '=', self.testing_level.id),
                                                                  ('project_id', '=', self.project_id.id),
                                                                  ('module_id', '=', self.module_id.id),
                                                                  ('create_uid', '!=', self.env.user.id)])
            all_data = self.env['kw_test_case_data_line'].sudo().search([('case_upload_id', 'in', data.ids), ('case_review_id', '=', False)])
            if all_data:
                for rec in all_data:
                    if not rec.case_review_id and rec.scenario_id.id not in existing_case_ids:
                        rec.case_review_id = self.id
                self.fetch_bool = True
            else:
                raise ValidationError('No Data Found.')