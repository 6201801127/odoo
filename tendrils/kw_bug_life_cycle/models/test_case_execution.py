from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class TestCaseExecution(models.Model):
    _name = 'kw_test_case_exec'
    _description = 'Test Case Execution'
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
    data_line_ids = fields.One2many('kw_test_case_data_line', 'case_execute_id', string='Data Lines')
    iteration_log_ids = fields.One2many('kw_tc_exec_iteration_log', 'tc_execution_id', string='Iteration Log')
    fetch_bool = fields.Boolean()
    complete_bool = fields.Boolean(compute="_check_project_tl", store=False)
    iteration = fields.Char(default='0', compute="get_iteration", store=False)
    complete_msg = fields.Char(compute='get_msg_data', store=False)
    complete_msg1 = fields.Char(compute='get_msg_data', store=False)

    def get_iteration(self):
        for rec in self:
            iterations = [line.iteration for line in rec.data_line_ids if line.iteration]
            max_iteration = max(iterations, default=0)
            rec.iteration = max_iteration


    def _check_project_tl(self):
        emp_list = []
        if self.project_id:
            data = self.env['kw_bug_life_cycle_conf'].search([('project_id', '=', self.project_id.project_id.id)])
            for user in data.user_ids:
                if user.user_type in ['Test Lead']:
                    emp_list.append(user.employee_id.id)
        if self.env.user.employee_ids.id in emp_list:
            self.complete_bool = True
        else:
            self.complete_bool = False

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.module_id = False
        return {'domain': {'module_id': self._get_module_domain()}}

    def button_fetch(self):
        if self.project_id and self.module_id and self.fetch_from == 'mine':
            existing_case_ids = self.data_line_ids.mapped('id')
            data = self.env['kw_test_case_upload'].sudo().search([
                ('testing_level', '=', self.testing_level.id),
                ('project_id', '=', self.project_id.id),
                ('module_id', '=', self.module_id.id),
                ('create_uid', '=', self.env.user.id)
            ])
            all_data = self.env['kw_test_case_data_line'].sudo().search([
                ('case_upload_id', 'in', data.ids), ('case_execute_id', '=', False)
            ])
            if all_data:
                for rec in all_data:
                    if rec.id not in existing_case_ids:
                        rec.case_execute_id = self.id
                self.fetch_bool = True
            else:
                raise ValidationError('No Data Found.')

        elif self.project_id and self.module_id and self.fetch_from == 'colleagues':
            existing_case_ids = self.data_line_ids.mapped('id')
            data = self.env['kw_test_case_upload'].sudo().search([('testing_level', '=', self.testing_level.id),
                                                                  ('project_id', '=', self.project_id.id),
                                                                  ('module_id', '=', self.module_id.id),
                                                                  ('create_uid', '!=', self.env.user.id)])
            all_data = self.env['kw_test_case_data_line'].sudo().search([('case_upload_id', 'in', data.ids), ('case_execute_id', '=', False)])
            if all_data:
                for rec in all_data:
                    if not rec.case_execute_id and rec.scenario_id.id not in existing_case_ids:
                        rec.case_execute_id = self.id
                self.fetch_bool = True
            else:
                raise ValidationError('No Data Found.')

    def button_success(self):
        total_line = 0
        total_executed = 0
        records = self.env['kw_test_case_exec'].sudo().search([
            ('testing_level', '=', self.testing_level.id),
            ('project_id', '=', self.project_id.id),
            ('module_id', '=', self.module_id.id)
        ])
        for linee in records:
            for line in linee.data_line_ids:
                total_line += 1
                if line.result.code in ['PASS', 'FAIL']:
                    total_executed += 1
        if total_line > 0:
            perc = round(total_executed / total_line * 100)
        else:
            perc = 0
        if perc < 50:
            view_id = self.env.ref('kw_bug_life_cycle.tc_exc_complete_wizard_form').id
            return {
                'name': 'Complete Execution Msg',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'tc_exc_complete_wizard',
                'context':{'default_test_case_exec_id': self.id,
                           'default_complete_msg':self.complete_msg,
                           'default_complete_msg1':self.complete_msg1,
                           'default_ok_btn_bool':True},
                'target': 'new',
            }
        else:
            view_id = self.env.ref('kw_bug_life_cycle.tc_exc_complete_wizard_form').id
            return {
                'name': 'Complete Execution Msg',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'tc_exc_complete_wizard',
                'context': {'default_test_case_exec_id': self.id,
                            'default_complete_msg': self.complete_msg},

                'target': 'new',
            }

    def get_msg_data(self):
        for rec in self:
            total_line = 0
            total_executed = 0
            total_regress = 0
            records = self.env['kw_test_case_exec'].sudo().search([
                ('testing_level', '=', rec.testing_level.id),
                ('project_id', '=', rec.project_id.id),
                ('module_id', '=', rec.module_id.id)
            ])
            highest_iteration_records = {}
            for record in records:
                key = (record.testing_level.id, record.project_id.id, record.module_id.id)
                current_iteration = record.iteration
                if key not in highest_iteration_records or current_iteration > highest_iteration_records[key].iteration:
                    highest_iteration_records[key] = record
            final_records = list(highest_iteration_records.values())
            total_iter = final_records[0].iteration
            for linee in records:
                for line in linee.data_line_ids:
                    total_line += 1
                    if line.result.code in ['PASS', 'FAIL']:
                        total_executed += 1
                    if line.mark_for_reg == True:
                        total_regress += 1
            if total_line > 0:
                perc = round(total_executed / total_line * 100)
            else:
                perc = 0
            if int(total_iter) > 1:
                rec.complete_msg = (
                    f'WRT the selected Testing Level, Project & Global link.<br>'
                    f'You have executed <span style="color:black; font-weight:bold;">{total_executed}</span> test cases out of '
                    f'<span style="color:black; font-weight:bold;">{total_line}</span>. <br>'
                    f'Your Execution percentage is <span style="color:black; font-weight:bold;">{perc}%</span>.<br>'
                    f'You have chosen <span style="color:black; font-weight:bold;">{total_regress}</span> out of <span style="color:black; font-weight:bold;">{total_line}</span> TC for regression.'
                                )
                rec.complete_msg1 = (
                    f'You have to execute at least <span style="color:black; font-weight:bold;">50%</span> of the total test cases to complete the execution.'
                )
            else:
                rec.complete_msg = (
                    f'WRT the selected Testing Level, Project & Global link.<br>'
                    f'You have executed <span style="color:black; font-weight:bold;">{total_executed}</span> test cases out of '
                    f'<span style="color:black; font-weight:bold;">{total_line}</span>. <br>'
                    f'Your Execution percentage is <span style="color:black; font-weight:bold;">{perc}%</span>.<br>'
                )
                rec.complete_msg1 = (
                    f'You have to execute at least <span style="color:black; font-weight:bold;">50%</span> of the total test cases to complete the execution.'
                )



class TestCaseExecIterationLog(models.Model):
    _name = 'kw_tc_exec_iteration_log'
    _description = 'Test Case Execution Iteration Log'

    tc_id = fields.Char(string='TC ID')
    result = fields.Char(string="Status")
    iter_num = fields.Integer(string = 'Iteration No')
    iter_date = fields.Datetime(string='Date Time')
    ts_id = fields.Many2one('test_scenario_master')
    tc_execution_id = fields.Many2one('kw_test_case_exec')
    bug_ids = fields.Many2many('kw_raise_defect')
