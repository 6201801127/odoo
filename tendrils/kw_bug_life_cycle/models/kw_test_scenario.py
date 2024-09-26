from odoo import fields, models, api
from odoo.tools.profiler import profile
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.http import request


class TestScenarioMaster(models.Model):
    _name = 'test_scenario_master'
    _description = 'Test Scenario Master'
    _rec_name = 'code'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    code = fields.Char(readonly=True, default='New',string="Test Id", track_visibility='always')
    prepared_by = fields.Many2one('hr.employee', string='Prepared By',default=lambda self: self.env.user.employee_ids.id, readonly=True, track_visibility='always')
    project_id = fields.Many2one('kw_bug_life_cycle_conf', string='Project', required=True,domain=lambda self: self._get_projects(), track_visibility='always')
    module_id = fields.Many2one('bug_module_master', string='Global Link', required=True,domain="[('project_id','=',project_id)]", track_visibility='always')
    prepared_on = fields.Date(string='Prepared On', default=lambda self: fields.Date.today(), readonly=True, track_visibility='always')
    expected_no_of_test_case = fields.Integer(string='Expected Number of Test Cases', required=True, track_visibility='always')
    scenario_description = fields.Text(string='Scenario Description', required=True, track_visibility='always')
    state = fields.Selection([('Draft', 'Draft'), ('Submitted', 'Submitted'), ('TL Approved', 'TL Approved'),('PM/BA Approved', 'PM/BA Approved')], default='Draft', track_visibility='always')
    action_log_ids = fields.One2many('kw_test_scenario_log', 'test_scenario_id', string='Action log', readonly=True)
    modified_by = fields.Many2one('res.users', string='Modified By', readonly=True)
    tl_remark = fields.Text(string='Remark(TL)')
    pm_remark = fields.Text(string='Remark(PM)')
    ba_remark = fields.Text(string='Remark(BA)')

    is_user_tl = fields.Boolean(default=False)
    is_user_pm = fields.Boolean(default=False)
    is_user_ba = fields.Boolean(default=False)

    pending_at_tl = fields.Boolean(default=False)
    pending_at_pm_ba = fields.Boolean(default=False)
    is_view_scenario = fields.Boolean(string='is view scenario', compute='_check_view_id')
    send_to_pm_ba = fields.Boolean(default=False)
    approve_pm = fields.Boolean(default=False)
    approve_ba = fields.Boolean(default=False)
    hide_aprove = fields.Boolean(default=False)
    is_tester = fields.Boolean(default=False)

    pm_ba_btn_hide_bool = fields.Boolean(string='PM/BA Button Hide Bool',default=False)
    pm_ba_approve_btn_hide_bool = fields.Boolean(default=False)
    pending_at_ids = fields.Many2many(
        string='Pending At',
        comodel_name='hr.employee',
        relation='employee_test_scenario_rel',
        column1='employee_id',
        column2='test_scenario_id',
    )
    revert_btn_hide_bool = fields.Boolean()
    field_readonly_bool = fields.Boolean()
    not_ok_remark = fields.Text(string="Query/Remark")
    comply = fields.Text(string="Comply")
    revert_status_boolean = fields.Boolean()
    status_compute = fields.Char('Status', compute="get_status", store=False)
    changes_done_date = fields.Date(string='Changes Done Date', readonly=True)
    test_lead_reject_boolean = fields.Boolean()

    @api.multi
    def write(self, vals):
        fields_to_check = ['project_id', 'module_id', 'expected_no_of_test_case', 'scenario_description']
        if any(field in vals for field in fields_to_check):
            employee_id = self.env.user.id or False
            vals.update({
                'modified_by': employee_id,
                'changes_done_date': fields.Date.today(),
            })
        return super(TestScenarioMaster, self).write(vals)


    def get_status(self):
        for rec in self:
            if rec.state == 'Draft' and rec.revert_status_boolean == True:
                rec.status_compute = "Reverted"
            else:
                rec.status_compute = rec.state


    @api.constrains('project_id', 'module_id', 'scenario_description')
    def check_same_valid(self):
        for record in self:
            duplicate = self.search([
                ('project_id', '=', record.project_id.id),
                ('module_id', '=', record.module_id.id),
                ('scenario_description', '=', record.scenario_description),
                ('id', '!=', record.id)
            ])
            if duplicate:
                raise ValidationError(
                    'This scenario with the same description already exists for this project and module.')


    @api.onchange('project_id')
    def _false_module(self):
        self.module_id = False
        if self.project_id:
            user_employee_ids = self.env.user.employee_ids.ids
            grp_tester = self.env.ref('kw_bug_life_cycle.group_tester_bug_life_cycle').users
            grp_test_lead = self.env.ref('kw_bug_life_cycle.group_Test_lead_bug_life_cycle').users

            for emp in self.project_id.user_ids.filtered(lambda x: x.employee_id.id in user_employee_ids):
                if emp.user_type == 'Tester' and emp.employee_id.user_id in grp_tester:
                    self.is_tester = True
                    self.is_user_tl = False
                elif emp.user_type == 'Test Lead' and emp.employee_id.user_id in grp_test_lead:
                    self.is_user_tl = True
                    self.is_tester = False


    @api.depends()
    def _get_projects(self):
        projects = self.env['kw_bug_life_cycle_conf'].search([]).filtered(lambda x: any(user.employee_id.user_id == self.env.user and user.user_type in ['Tester','Test Lead'] for user in x.user_ids))
        return [('id', 'in', projects.ids)]

    @api.depends('project_id')
    def _check_view_id(self):
        for rec in self:
            if self._context.get('act_permission'):
                request.session['act_permission'] = self._context.get('act_permission')
                rec.is_view_scenario = True
            else:
                rec.is_view_scenario = False
                request.session['act_permission'] = False
            rec.is_user_ba = True

    @api.model
    def create(self,vals):
        project = self.env['kw_bug_life_cycle_conf'].browse(vals.get('project_id'))
        module = self.env['bug_module_master'].browse(vals.get('module_id'))
        seq_prefix = project.project_id.name + '||' + module.module_name  # Get the project name as the prefix
        existing_sequences = self.env['ir.sequence'].search([('code', '=', 'self.kw_test_scenario')])
        existing_sequence = existing_sequences.filtered(lambda seq: seq.prefix == seq_prefix)
        if existing_sequence:
            seq = existing_sequence.next_by_id() or '/'
        else:
            new_sequence_vals = {
                'name': f'{seq_prefix} Sequence',
                'code': 'self.kw_test_scenario',
                'prefix': seq_prefix,
                'padding': 3,
            }
            new_sequence = self.env['ir.sequence'].sudo().create(new_sequence_vals)
            seq = new_sequence.next_by_id() or '/'
        formatted_sequence = f"{seq_prefix}||TS{seq.split(seq_prefix)[-1].strip('-')}"
        vals['code'] = formatted_sequence
        return super(TestScenarioMaster, self).create(vals)


    def button_submit_action(self):
        if self._context.get('button') == 'send_to_tl':
            test_lead_ids = []
            for recc in self.project_id.user_ids:
                if recc.user_type == 'Test Lead':
                    test_lead_ids.append(recc.employee_id.id)
            if test_lead_ids:
                self.pending_at_ids = [(6, 0, test_lead_ids)]
            self.write({'pending_at_tl': True,
                        # 'modified_by':self.env.user.id,
                        'state': 'Submitted',
                        'not_ok_remark': False,
                        'revert_btn_hide_bool':True,
                        'revert_status_boolean': False,
                        'pm_ba_btn_hide_bool':False,
                        'field_readonly_bool':True,
                        'is_tester':False})
            self.env['kw_test_scenario_log'].create({
                'test_scenario_id':self.id,
                'action_taken_by_id': self.env.user.employee_ids.id,
                'action_taken_on': datetime.now(),
                'action_state': self.state,
                'action_remark': self.comply
            })
            self.comply = False

    def button_send_pm_ba_action(self):
        if self.state == 'Draft':
            pm_ba_ids = []
            for recc in self.project_id.user_ids:
                if recc.user_type in ['BA','Manager']:
                    pm_ba_ids.append(recc.employee_id.id)

            if pm_ba_ids:
                self.pending_at_ids = [(6, 0, pm_ba_ids)]
            self.write({'pm_ba_btn_hide_bool':True,
                        'is_user_tl':False,
                        'tl_remark': 'Ok',
                        'not_ok_remark': False,
                        # 'modified_by': self.env.user.id,
                        'pm_ba_approve_btn_hide_bool':True,
                        'revert_btn_hide_bool':True,
                        'revert_status_boolean': False,
                        'field_readonly_bool':True,
                        'state':'TL Approved'})
            self.env['kw_test_scenario_log'].create({
                'test_scenario_id':self.id,
                'action_taken_by_id': self.env.user.employee_ids.id,
                'action_taken_on': datetime.now(),
                'action_state': self.state,
                'action_remark': self.comply
            })
            self.comply = False
        elif self.state == 'Submitted':
            form_view_id = self.env.ref('kw_bug_life_cycle.test_scenario_wizard_view').id
            action = {
                'type': 'ir.actions.act_window',
                'name': 'Approval Wizard',
                'view_mode': 'tree',
                'view_type': 'form',
                'res_model': 'scenario_submit_wizard',
                'views': [(form_view_id, 'form')],
                'target': 'new',
                'context':{'current_id':self.id,'default_pm_ba_btn_hide_boolean': True}
            }
            return action

    @api.model
    def get_reqd_project(self):
        tree_view_id = self.env.ref('kw_bug_life_cycle.test_scenario_master_take_action_tree').id
        form_view_id = self.env.ref('kw_bug_life_cycle.test_scenario_master_form').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Take Action',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': 'ref="kw_bug_life_cycle.test_scenario_master_take_action_tree"',
            'res_model': 'test_scenario_master',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'domain': [('pending_at_ids', 'in', self.env.user.employee_ids.id)],
            'context': {'group_by': 'project_id'}
        }
        return action

    def button_pm_ba_approved(self):
        form_view_id = self.env.ref('kw_bug_life_cycle.test_scenario_wizard_view').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Approve PM/BA',
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'scenario_submit_wizard',
            'views': [(form_view_id, 'form')],
            'target': 'new',
            'context':{'current_id':self.id,'default_approve_btn_hide_boolean':True}
        }
        return action

    def button_revert_back(self):
        form_view_id = self.env.ref('kw_bug_life_cycle.test_scenario_wizard_view').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Revert',
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'scenario_submit_wizard',
            'views': [(form_view_id, 'form')],
            'target': 'new',
            'context':{'current_id':self.id,'default_revert_back_btn_hide_boolean': True}
        }
        return action


    def scenario_pending_mail(self):
        all_pending_records = self.env['test_scenario_master'].sudo().search([])
        """Pending Brainstrome"""
        pass

    @api.model
    def get_download_test_scenario(self, selected_ids):
        selected_records = self.env['test_scenario_master'].browse(selected_ids)
        ids_str = ','.join(map(str, selected_records.ids))
        action_url = '/download-test-scenario/%s' % ids_str
        return {
            'type': 'ir.actions.act_url',
            'url': action_url,
            'target': 'self',
        }


class ScenarioSubmitWizard(models.TransientModel):
    _name = 'scenario_submit_wizard'
    _description = "Scenario Submit Wizard"

    remark = fields.Text("Remark")
    remark_selection = fields.Selection(
        string='Remark',
        selection=[('ok', 'Ok'), ('notok', 'Not Ok')]
    )
    pm_ba_btn_hide_boolean = fields.Boolean(string='PM/BA Button Hide')
    revert_back_btn_hide_boolean = fields.Boolean(string='Revert Back Button Hide')
    approve_btn_hide_boolean = fields.Boolean(string='Approve Button Hide')



    def send_btn_pm_ba(self):
        if self.env.context.get('current_id'):
            pm_ba_ids = []
            scenarion_data = self.env['test_scenario_master'].sudo().search(
                [('id', '=', self.env.context.get('current_id'))]
            )
            if scenarion_data:
                for recc in scenarion_data.project_id.user_ids:
                    if recc.user_type in ['BA', 'Manager']:
                        pm_ba_ids.append(recc.employee_id.id)
            if pm_ba_ids:
                scenarion_data.write({
                    'pending_at_ids': [(6, 0, pm_ba_ids)],
                    'tl_remark':'Ok',
                    'not_ok_remark': False,
                    # 'modified_by': self.env.user.id,
                    'state': 'TL Approved',
                    'test_lead_reject_boolean': False,
                    'pm_ba_btn_hide_bool':True,
                    'pm_ba_approve_btn_hide_bool':True,
                    'revert_status_boolean': False,
                    'action_log_ids': [[0, 0, {
                        'test_scenario_id': scenarion_data.id,
                        'action_taken_by_id': self.env.user.employee_ids.id,
                        'action_taken_on': datetime.now(),
                        'action_state': 'TL Approved',
                        'action_remark': scenarion_data.comply
                    }]]
                })
            scenarion_data.comply = False

    def button_approved_pm_ba(self):
        if self.env.context.get('current_id'):
            scenarion_data = self.env['test_scenario_master'].sudo().search(
                [('id', '=', self.env.context.get('current_id'))]
            )
            pm_list = []
            ba_list = []
            if scenarion_data:
                for recc in scenarion_data.project_id.user_ids:
                    if recc.user_type == 'Manager':
                        pm_list.append(recc.employee_id.id)
                    if recc.user_type == 'BA':
                        ba_list.append(recc.employee_id.id)
            if self.env.user.employee_ids.id in pm_list:
                current_pending_at_ids = scenarion_data.pending_at_ids.ids
                updated_pending_at_ids = [id for id in current_pending_at_ids if id not in pm_list]
                if len(updated_pending_at_ids) == 0:
                    scenarion_data.write({
                        'pending_at_ids':[(6, 0, updated_pending_at_ids)],
                        'pm_remark':'Ok',
                        'not_ok_remark': False,
                        # 'modified_by': self.env.user.id,
                        'state': 'PM/BA Approved',
                        'pm_ba_approve_btn_hide_bool':False,
                        'action_log_ids': [[0, 0, {
                            'test_scenario_id': scenarion_data.id,
                            'action_taken_by_id': self.env.user.employee_ids.id,
                            'action_taken_on': datetime.now(),
                            'action_state': 'PM Approved',
                            'action_remark': self.remark
                        }]]
                    })
                else:
                    scenarion_data.write({
                        'pending_at_ids': [(6, 0, updated_pending_at_ids)],
                        'pm_remark': 'Ok',
                        'not_ok_remark': False,
                        # 'modified_by': self.env.user.id,
                        'state': 'PM/BA Approved',
                        'pm_ba_approve_btn_hide_bool': True,
                        'action_log_ids': [[0, 0, {
                            'test_scenario_id': scenarion_data.id,
                            'action_taken_by_id': self.env.user.employee_ids.id,
                            'action_taken_on': datetime.now(),
                            'action_state': 'PM Approved',
                            'action_remark': self.remark
                        }]]
                    })
            elif self.env.user.employee_ids.id in ba_list:
                current_pending_at_ids = scenarion_data.pending_at_ids.ids
                updated_pending_at_ids = [id for id in current_pending_at_ids if id not in ba_list]
                if len(updated_pending_at_ids) == 0:
                    scenarion_data.write({
                        'pending_at_ids': [(6, 0, updated_pending_at_ids)],
                        'ba_remark': 'Ok',
                        'not_ok_remark': False,
                        # 'modified_by': self.env.user.id,
                        'state': 'PM/BA Approved',
                        'pm_ba_approve_btn_hide_bool': False,
                        'action_log_ids': [[0, 0, {
                            'test_scenario_id': scenarion_data.id,
                            'action_taken_by_id': self.env.user.employee_ids.id,
                            'action_taken_on': datetime.now(),
                            'action_state': 'BA Approved',
                            'action_remark': self.remark
                        }]]
                    })
                else:
                    scenarion_data.write({
                        'pending_at_ids': [(6, 0, updated_pending_at_ids)],
                        'ba_remark': 'Ok',
                        'not_ok_remark': False,
                        # 'modified_by': self.env.user.id,
                        'state': 'PM/BA Approved',
                        'pm_ba_approve_btn_hide_bool': True,
                        'action_log_ids': [[0, 0, {
                            'test_scenario_id': scenarion_data.id,
                            'action_taken_by_id': self.env.user.employee_ids.id,
                            'action_taken_on': datetime.now(),
                            'action_state': 'BA Approved',
                            'action_remark': self.remark
                        }]]
                    })

    def btn_revert_back_to_author(self):
        if self.env.context.get('current_id'):
            scenarion_data = self.env['test_scenario_master'].sudo().search(
                [('id', '=', self.env.context.get('current_id'))]
            )
            pm_list = []
            ba_list = []
            tester_ids = []
            test_lead_list = []
            if scenarion_data:
                for recc in scenarion_data.project_id.user_ids:
                    if recc.user_type == 'Tester':
                        tester_ids.append(recc.employee_id.id)
                    if recc.user_type == 'Manager':
                        pm_list.append(recc.employee_id.id)
                    if recc.user_type == 'BA':
                        ba_list.append(recc.employee_id.id)
                    if recc.user_type == 'Test Lead':
                        test_lead_list.append(recc.employee_id.id)
            if  self.env.user.employee_ids.id in test_lead_list:
                if scenarion_data.create_uid.employee_ids.id in tester_ids:
                    scenarion_data.write({
                        'revert_status_boolean':True,
                        'revert_btn_hide_bool':False,
                        'pm_ba_btn_hide_bool': True,
                        'is_tester':True,
                        # 'modified_by': self.env.user.id,
                        'tl_remark':'Not Ok',
                        'not_ok_remark': self.remark,
                        'pending_at_ids':[(6, 0, [scenarion_data.create_uid.employee_ids.id])],
                        'state': 'Draft',
                        'test_lead_reject_boolean':True,
                        'pm_ba_approve_btn_hide_bool':False,
                        'action_log_ids': [[0, 0, {
                            'test_scenario_id': scenarion_data.id,
                            'action_taken_by_id': self.env.user.employee_ids.id,
                            'action_taken_on': datetime.now(),
                            'action_state': 'TL Reverted',
                            'action_remark': self.remark
                        }]]
                    })
                else:
                    scenarion_data.write({
                        'pending_at_ids':[(6, 0, [scenarion_data.create_uid.employee_ids.id])],
                        'state': 'Draft',
                        'test_lead_reject_boolean': True,
                        'pm_ba_approve_btn_hide_bool':False,
                        'is_user_tl':True,
                        # 'modified_by': self.env.user.id,
                        'revert_btn_hide_bool':False,
                        'revert_status_boolean': True,
                        'action_log_ids': [[0, 0, {
                            'test_scenario_id': scenarion_data.id,
                            'action_taken_by_id': self.env.user.employee_ids.id,
                            'action_taken_on': datetime.now(),
                            'action_state': 'Reverted',
                            'action_remark': self.remark
                        }]]
                    })
            elif self.env.user.employee_ids.id in pm_list:
                # current_pending_at_ids = scenarion_data.pending_at_ids.ids
                # updated_pending_at_ids = [id for id in current_pending_at_ids if id not in pm_list]
                if scenarion_data.create_uid.employee_ids.id in tester_ids:
                    scenarion_data.write({
                        'revert_btn_hide_bool':False,
                        'revert_status_boolean': True,
                        'pm_ba_btn_hide_bool': True,
                        'is_tester':True,
                        'pm_remark':'Not Ok',
                        'not_ok_remark': self.remark,
                        # 'modified_by': self.env.user.id,
                        'pending_at_ids':[(6, 0, [scenarion_data.create_uid.employee_ids.id])],
                        'state': 'Draft',
                        'pm_ba_approve_btn_hide_bool':False,
                        'action_log_ids': [[0, 0, {
                            'test_scenario_id': scenarion_data.id,
                            'action_taken_by_id': self.env.user.employee_ids.id,
                            'action_taken_on': datetime.now(),
                            'action_state': 'PM Reverted',
                            'action_remark': self.remark
                        }]]
                    })
                else:
                    scenarion_data.write({
                        'pending_at_ids':[(6, 0, [scenarion_data.create_uid.employee_ids.id])],
                        'state': 'Draft',
                        'pm_remark': 'Not Ok',
                        'not_ok_remark': self.remark,
                        # 'modified_by': self.env.user.id,
                        'pm_ba_approve_btn_hide_bool':False,
                        'is_user_tl':True,
                        'revert_btn_hide_bool':False,
                        'revert_status_boolean': True,
                        'action_log_ids': [[0, 0, {
                            'test_scenario_id': scenarion_data.id,
                            'action_taken_by_id': self.env.user.employee_ids.id,
                            'action_taken_on': datetime.now(),
                            'action_state': 'PM Reverted',
                            'action_remark': self.remark
                        }]]
                    })
            elif self.env.user.employee_ids.id in ba_list:
                if scenarion_data.create_uid.employee_ids.id in tester_ids:
                    scenarion_data.write({
                        'revert_btn_hide_bool': False,
                        'revert_status_boolean': True,
                        'pm_ba_btn_hide_bool': True,
                        'is_tester': True,
                        'ba_remark': 'Not Ok',
                        'not_ok_remark': self.remark,
                        # 'modified_by': self.env.user.id,
                        'pending_at_ids': [(6, 0, [scenarion_data.create_uid.employee_ids.id])],
                        'state': 'Draft',
                        'pm_ba_approve_btn_hide_bool': False,
                        'action_log_ids': [[0, 0, {
                            'test_scenario_id': scenarion_data.id,
                            'action_taken_by_id': self.env.user.employee_ids.id,
                            'action_taken_on': datetime.now(),
                            'action_state': 'BA Reverted',
                            'action_remark': self.remark
                        }]]
                    })
                else:
                    scenarion_data.write({
                        'pending_at_ids': [(6, 0, [scenarion_data.create_uid.employee_ids.id])],
                        'state': 'Draft',
                        'ba_remark': 'Not Ok',
                        'not_ok_remark': self.remark,
                        'pm_ba_approve_btn_hide_bool': False,
                        'is_user_tl': True,
                        # 'modified_by': self.env.user.id,
                        'revert_btn_hide_bool': False,
                        'revert_status_boolean': True,
                        'action_log_ids': [[0, 0, {
                            'test_scenario_id': scenarion_data.id,
                            'action_taken_by_id': self.env.user.employee_ids.id,
                            'action_taken_on': datetime.now(),
                            'action_state': 'BA Reverted',
                            'action_remark': self.remark
                        }]]
                    })

    def send_tl_act_btn(self):
        if request.session['act_permission'] == True:
            raise ValidationError("This page does not have access to take any actions.")
        else:
            selected_records = self.env['test_scenario_master'].browse(self._context.get('active_ids', []))
            for record in selected_records:
                tester_ids = []
                test_lead_ids = []
                for recordd in record.project_id.user_ids:
                    if recordd.user_type == 'Tester':
                        tester_ids.append(recordd.employee_id.id)
                    if recordd.user_type == 'Test Lead':
                        test_lead_ids.append(recordd.employee_id.id)
                if record.state == 'Draft' and self.env.user.employee_ids.id in tester_ids and record.create_uid.employee_ids.id in tester_ids:
                    record.write({'pending_at_ids': [(6, 0, test_lead_ids)],
                                  'pending_at_tl': True,
                                  'state': 'Submitted',
                                  'not_ok_remark': False,
                                #   'modified_by': self.env.user.id,
                                  'revert_btn_hide_bool': True,
                                  'revert_status_boolean': False,
                                  'pm_ba_btn_hide_bool': False,
                                  'field_readonly_bool': True,
                                  'is_tester': False})
                    self.env['kw_test_scenario_log'].create({
                        'test_scenario_id': record.id,
                        'action_taken_by_id': self.env.user.employee_ids.id,
                        'action_taken_on': datetime.now(),
                        'action_state': record.state,
                        'action_remark': 'Sent to TL'
                    })


    def send_pm_ba_act_btn(self):
        if request.session['act_permission'] == True:
            raise ValidationError("This page does not have access to take any actions.")
        else:
            selected_records = self.env['test_scenario_master'].browse(self._context.get('active_ids', []))
            for record in selected_records:
                test_lead_ids = []
                pm_ba_ids = []
                for recordd in record.project_id.user_ids:
                    if recordd.user_type in  ['BA', 'Manager']:
                        pm_ba_ids.append(recordd.employee_id.id)
                    if recordd.user_type == 'Test Lead':
                        test_lead_ids.append(recordd.employee_id.id)
                if self.env.user.employee_ids.id in test_lead_ids and record.state == 'Submitted' and self.env.user.employee_ids.id in record.pending_at_ids.ids:
                    record.write({
                        'pending_at_ids': [(6, 0, pm_ba_ids)],
                        'pm_ba_btn_hide_bool':True,
                        'is_user_tl':False,
                        # 'modified_by': self.env.user.id,
                        'pm_ba_approve_btn_hide_bool':True,
                        'revert_btn_hide_bool':True,
                        'revert_status_boolean': False,
                        'field_readonly_bool':True,
                        'tl_remark': 'Ok',
                        'not_ok_remark': False,
                        'state':'TL Approved'})
                    self.env['kw_test_scenario_log'].create({
                        'test_scenario_id':record.id,
                        'action_taken_by_id': self.env.user.employee_ids.id,
                        'action_taken_on': datetime.now(),
                        'action_state': record.state,
                        'tl_remark': 'Ok',
                        'action_remark': 'TL Approved'
                    })
                elif self.env.user.employee_ids.id in test_lead_ids and record.state == 'Draft' and self.env.user.employee_ids.id in record.pending_at_ids.ids and self.env.user.id == record.create_uid.id or \
                        self.env.user.employee_ids.id in test_lead_ids and record.state == 'Draft' and self.env.user.employee_ids.id not in record.pending_at_ids.ids and self.env.user.id == record.create_uid.id:
                    record.write({
                        'pending_at_ids': [(6, 0, pm_ba_ids)],
                        'pm_ba_btn_hide_bool':True,
                        'is_user_tl':False,
                        # 'modified_by': self.env.user.id,
                        'pm_ba_approve_btn_hide_bool':True,
                        'revert_btn_hide_bool':True,
                        'revert_status_boolean': False,
                        'field_readonly_bool':True,
                        'tl_remark': 'Ok',
                        'not_ok_remark': False,
                        'state':'TL Approved'})
                    self.env['kw_test_scenario_log'].create({
                        'test_scenario_id':record.id,
                        'action_taken_by_id': self.env.user.employee_ids.id,
                        'action_taken_on': datetime.now(),
                        'action_state': record.state,
                        'tl_remark': 'Ok',
                        'action_remark': 'TL Approved'
                    })
                else:
                    pass



class KwCrSubActivityMaster(models.Model):
    _name = "kw_test_scenario_log"
    _description = "Kw Cr Sub Activity Master"

    test_scenario_id = fields.Many2one('test_scenario_master')
    action_taken_by_id = fields.Many2one('hr.employee', string='Action Taken By')
    action_taken_on = fields.Date(string='Taken On')
    action_state = fields.Char(string='State')
    action_remark = fields.Char(string='Remark')


class DelegateTsWizard(models.TransientModel):
    _name = 'delegate_ts_wizard'
    _description = "Delegate TS Wizard"

    tester_id = fields.Many2one('hr.employee', string='Tester', domain=lambda self: self._get_tester_domain())

    def _get_tester_domain(self):
        test_scenario = self.env['test_scenario_master'].browse(self.env.context.get('default_selected_record_ids', []))
        for rec in test_scenario:
            if rec and rec.project_id:
                bug_conf = rec.project_id
                tester_ids = self.env['kw_bug_life_cycle_conf_user_field'].search([
                    ('cycle_bug_conf_id', '=', bug_conf.id),
                    ('user_type', '=', 'Tester')
                ]).mapped('employee_id').ids
                return [('id', 'in', tester_ids)]
            return [('id', '=', False)]

    def delegate_act_btn(self):
        if self.env.context.get('delegate') == True:
            test_scenario = self.env['test_scenario_master'].browse(self.env.context.get('default_selected_record_ids', []))
            test_scenario_ids = test_scenario.mapped('project_id.id')
            if len(set(test_scenario_ids)) == 1:
                for record in test_scenario:
                    test_lead_list = []
                    for recc in record.project_id.user_ids:
                        if recc.user_type == 'Test Lead':
                            test_lead_list.append(recc.employee_id.id)
                    if self.env.user.employee_ids.id in test_lead_list:
                        if record.state == 'Draft' and record.revert_status_boolean != True:
                            self.env.cr.execute("""
                                UPDATE test_scenario_master
                                SET create_uid = %s, prepared_by = %s
                                WHERE id = %s
                            """, (self.tester_id.user_id.id, self.tester_id.id, record.id))
                        elif record.state == 'Draft' and record.revert_status_boolean == True:
                            self.env.cr.execute("""
                                                        UPDATE test_scenario_master
                                                        SET create_uid = %s, prepared_by = %s
                                                        WHERE id = %s
                                                    """, (self.tester_id.user_id.id, self.tester_id.id, record.id))
                            record.pending_at_ids = [(6, 0, [self.tester_id.id])]
                        else:
                            raise ValidationError("Selected records must belong to Draft and Reverted Status.")
                    else:
                        raise ValidationError('You have no access to delegate in another project.')
            else:
                raise ValidationError("Selected records must belong to the same project.")
        else:
            raise ValidationError("This page only have access in view scenario page.")
