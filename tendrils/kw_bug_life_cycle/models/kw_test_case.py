import datetime
from odoo import fields, models, api,_
from odoo.exceptions import ValidationError,UserError
import csv
import base64
from io import StringIO
import os
import mimetypes
import re
from markupsafe import Markup


class TestCaseUpload(models.Model):
    _name = 'kw_test_case_upload'
    _description = 'Test Case Upload'
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
                ('test_case_update_perm', '=', True)
            ]).mapped('module_id.id')
            return [('id', 'in', permitted_modules)]
        else:
            return [('id', '=', False)]

    test_suite = fields.Char('Test Suite Suffix', required=True)
    test_suite_name = fields.Char('Test Suite Name', readonly=True, compute="get_test_suite_name", store=False)
    testing_level = fields.Many2one('testing_level_config_master', string='Testing Level', domain="[('name','in',['SIT', 'Component', 'Functional'])]")
    project_id = fields.Many2one('kw_bug_life_cycle_conf', string='Project', required=True, domain=_get_project)
    p_id = fields.Integer(related='project_id.project_id.id')
    module_id = fields.Many2one('bug_module_master', string='Global Link', required=True,
                                domain=_get_module_domain)
    file = fields.Binary(string='File', attachment=True)
    file_name = fields.Char("File Name")
    data_line_ids = fields.One2many('kw_test_case_data_line', 'case_upload_id', string='Data Lines')
    generate_id_add_line_visible_boolean = fields.Boolean()
    file_import_boolean = fields.Boolean()
    tc_id_generated = fields.Char(store=False, compute='get_is_tc_gen')

    def get_test_suite_name(self):
        for rec in self:
            if rec.test_suite:
                project_name = rec.project_id.project_id.name
                module_name = rec.module_id.module_name.replace(' ', '_')
                prefix = ''
                if rec.testing_level.name == 'Component':
                    prefix = f"{project_name}_05_01_{module_name}_CTC"
                elif rec.testing_level.name == 'Functional':
                    prefix = f"{project_name}_05_01_{module_name}_FTC"
                elif rec.testing_level.name == 'SIT':
                    prefix = f"{project_name}_05_02_SITC"
                rec.test_suite_name = f'{prefix}_{rec.test_suite}'

    def get_is_tc_gen(self):
        for rec in self:
            if rec.data_line_ids:
                for recc in rec.data_line_ids:
                    if recc.restrict_delete_bool == True:
                        rec.tc_id_generated = 'Yes'
                    else:
                        rec.tc_id_generated = 'No'
            else:
                rec.tc_id_generated = 'No TC.'


    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.module_id = False
        return {'domain': {'module_id': self._get_module_domain()}}

    @api.constrains('file')
    def _check_file_extension(self):
        for record in self:
            if record.file:
                file_name = record.file_name or ''
                file_extension = mimetypes.guess_extension(mimetypes.guess_type(file_name)[0])
                if file_extension != '.csv':
                    raise ValidationError("Please upload only CSV files.")

    def button_import_data(self):
        for rec in self:
            if not rec.file:
                raise UserError('Please upload a CSV file.')
            csv_data = base64.b64decode(rec.file).decode('utf-8')
            csv_file = StringIO(csv_data)
            csv_reader = csv.DictReader(csv_file)
            csv_columns = set(csv_reader.fieldnames)
            o2m_columns = {'expectation', 'tc_id', 'pos_neg', 'scenario_id', 'scenario_description', 'test_case_description', 'sl_no', 'test_data_action', 'sub_reference'}
            missing_elements = o2m_columns - csv_columns
            if missing_elements:
                raise UserError(f'The following columns are missing in the CSV file: {", ".join(missing_elements)}')
            existing_data = rec.data_line_ids.filtered(
                lambda x: x.scenario_id or x.tc_id or x.pos_neg or x.scenario or x.test_data_action or x.expectation
            )
            existing_data_rows = {
                (line.scenario_id, line.tc_id, line.pos_neg, line.scenario, line.test_data_action, line.expectation)
                for line in existing_data
            }
            new_data = []
            for row in csv_reader:
                data_tuple = (
                    row.get('sl_no'), row.get('sub_reference'), row.get('scenario_id'), row.get('tc_id'),
                    row.get('pos_neg'),
                    row.get('scenario_description'), row.get('test_case_description'), row.get('test_data_action'),
                    row.get('expectation')
                )

                if data_tuple in existing_data_rows:
                    raise UserError('Data already exists in the One2many field.')

                scenario_id = row.get('scenario_id')
                ps = row.get('pos_neg')
                tcd = row.get('test_case_description')
                tda = row.get('test_data_action')
                exp = row.get('expectation')
                if not scenario_id:
                    raise ValidationError('Missing Test Scenario ID.')
                if not ps:
                    raise ValidationError('Missing Pos/Neg field.')
                if not tcd:
                    raise ValidationError('Missing Test Case Description.')
                if not tda:
                    raise ValidationError('Missing Test Data Action.')
                if not exp:
                    raise ValidationError('Missing Expectation.')

                sc_id = self.env['test_scenario_master'].sudo().search([('code', '=', scenario_id), ('test_lead_reject_boolean', '=', False)])
                if sc_id:
                    if rec.testing_level.name != 'SIT':
                        if sc_id.project_id.id == rec.project_id.id and sc_id.module_id.id == rec.module_id.id:
                            new_data.append((0, 0, {
                                'sl_no': row.get('sl_no'),
                                'sub_reference': row.get('sub_reference'),
                                'scenario_id': sc_id.id,
                                'tc_id': row.get('tc_id'),
                                'pos_neg': row.get('pos_neg'),
                                'scenario': row.get('scenario_description'),
                                'test_case_description': row.get('test_case_description'),
                                'test_data_action': row.get('test_data_action'),
                                'expectation': row.get('expectation'),
                            }))
                        else:
                            raise ValidationError('You Can\'t Import Multiple Project/Global Link Scenario data.' )
                    elif rec.testing_level.name == 'SIT':
                        if sc_id.project_id.id == rec.project_id.id:
                            new_data.append((0, 0, {
                                'sl_no': row.get('sl_no'),
                                'sub_reference': row.get('sub_reference'),
                                'scenario_id': sc_id.id,
                                'tc_id': row.get('tc_id'),
                                'pos_neg': row.get('pos_neg'),
                                'scenario': row.get('scenario_description'),
                                'test_case_description': row.get('test_case_description'),
                                'test_data_action': row.get('test_data_action'),
                                'expectation': row.get('expectation'),
                            }))
                        else:
                            raise ValidationError('You Can\'t Import Multiple Project Scenario data.' )
                else:
                    raise ValidationError(f'Invalid Scenario ID: {scenario_id}.')
            rec.data_line_ids = False
            rec.data_line_ids = new_data
            if rec.data_line_ids:
                rec.generate_id_add_line_visible_boolean = True


    def button_generate_id(self):
        project_name = self.project_id.project_id.name
        module_name = self.module_id.module_name.replace(' ', '_')

        if self.testing_level.name == 'Component':
            prefix = f"{project_name}_05_01_{module_name}_CTC"
        elif self.testing_level.name == 'Functional':
            prefix = f"{project_name}_05_01_{module_name}_FTC"
        elif self.testing_level.name == 'SIT':
            prefix = f"{project_name}_05_02_SITC"
        else:
            raise UserError('Invalid Testing Level. Please select a valid testing level.')

        regex = re.compile(rf'{re.escape(prefix)}(\d{{3}})')
        highest_existing_id = 0
        existing_records = self.env['kw_test_case_data_line'].search([
            ('case_upload_id.project_id', '=', self.project_id.id),
            ('case_upload_id.module_id', '=', self.module_id.id),
            ('case_upload_id.testing_level', '=', self.testing_level.id),
        ])

        for line in existing_records:
            match = regex.match(line.tc_id)
            if match:
                highest_existing_id = max(highest_existing_id, int(match.group(1)))

        sequence_number = highest_existing_id + 1
        for rec in self.data_line_ids:
            if not rec.tc_id or rec.tc_id == "New":
                rec.tc_id = f"{prefix}{sequence_number:03d}"
                rec.restrict_delete_bool = True
                sequence_number += 1

        self.file_import_boolean = True
        self.generate_id_add_line_visible_boolean = False

    def action_open_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Test Case Line',
            'view_mode': 'form',
            'res_model': 'kw_test_case_line_wizard',
            'target': 'new',
            'context': {
                'default_testing_level': self.testing_level.id,
                'default_project_id': self.project_id.id,
                'default_module_id': self.module_id.id,
            }
        }


class TestCaseDataLine(models.Model):
    _name = 'kw_test_case_data_line'
    _description = 'Test Case Data Line'
    _rec_name = 'tc_id'

    @api.model
    def get_default_result(self):
        result_record = self.env['kw_tc_execution_type'].sudo().search([('code', '=', 'NOTEXC')], limit=1)
        return result_record.id

    sl_no = fields.Integer(string = 'SL No')
    sub_reference = fields.Char(string = 'Sub Reference')
    project_id = fields.Many2one()
    scenario_id = fields.Many2one('test_scenario_master', string='Test Scenario ID')
    tc_id = fields.Char(string='TC ID', default="New")
    pos_neg = fields.Char(string='Positive/Negative')
    scenario = fields.Text(related="scenario_id.scenario_description", string="Test Scenario Description")
    test_case_description = fields.Char(string="Test Case Description")
    test_data_action = fields.Char(string="Test Data/Action")
    expectation = fields.Char(string="Expected Result")
    case_upload_id = fields.Many2one('kw_test_case_upload')
    case_execute_id = fields.Many2one('kw_test_case_exec')
    case_review_id = fields.Many2one('kw_test_case_review')
    restrict_delete_bool = fields.Boolean(string='Locked', default=False)
    actual = fields.Text(string="Actual")
    result = fields.Many2one('kw_tc_execution_type', string="Result", default=get_default_result, domain=[('code', '!=', 'NOTEXC')])
    code = fields.Char(related='result.code', string='Result Code')
    bug_ids = fields.Many2many(
        comodel_name='kw_raise_defect',
        relation='bug_case_rel',
        column1='bug_id',
        column2='case_id', string="Bug ID")
    bug_id_status = fields.Char(string='Bug Status', compute='_compute_bug_id_status')
    mark_for_reg = fields.Boolean(string='Mark For Regression?')
    copy_for_uat = fields.Boolean(string='Copy For UAT?')
    tl_review = fields.Char(string="Test Lead Review")
    is_invalid = fields.Boolean(string='Is Invalid?')
    automatable = fields.Boolean(string='Automatable?')
    automated = fields.Boolean(string='Automated?')
    automation_review = fields.Char(string="Automation Review")
    iteration = fields.Integer(default='0', readonly=1, store=True)
    iter_comp_boolean = fields.Boolean()
    result_readonly_boolean = fields.Boolean()

    @api.model
    def get_default_result(self):
        result_record = self.env['kw_tc_execution_type'].sudo().search([('code', '=', 'NOTEXC')], limit=1)
        return result_record.id

    @api.onchange('result')
    def get_result_readonly_boolean(self):
        for rec in self:
            all_bugs_closed = (not rec.bug_ids) or all(bug.state == 'Closed' for bug in rec.bug_ids)

            if rec.result.code == 'PASS' and rec.iter_comp_boolean != True:
                rec.result_readonly_boolean = True
            elif rec.result.code == 'FAIL' and rec.iter_comp_boolean != True and not all_bugs_closed:
                rec.result_readonly_boolean = True
            else:
                rec.result_readonly_boolean = False

    @api.multi
    def write(self, vals):
        old_result = None
        for record in self:
            old_result = record.result.id
        result = super(TestCaseDataLine, self).write(vals)
        for record in self:
            if 'result' in vals and vals.get('result') != old_result:
                if record.case_execute_id:
                    record.case_execute_id.iteration_log_ids.create({
                        'tc_id': record.tc_id,
                        'ts_id': record.scenario_id.id,
                        'result': record.result.name,
                        'iter_num': record.iteration,
                        'iter_date': datetime.datetime.now(),
                        'tc_execution_id': record.case_execute_id.id,
                        'bug_ids': [(6, 0, record.bug_ids.ids)]
                    })
        return result


    @api.onchange('result')
    def get_iteration_value(self):
        for rec in self:
            if rec.result and rec.iter_comp_boolean:
                dataa = self.env['kw_test_case_exec'].sudo().search([
                    ('testing_level', '=', rec.case_execute_id.testing_level.id),
                    ('project_id', '=', rec.case_execute_id.project_id.id),
                    ('module_id', '=', rec.case_execute_id.module_id.id)
                ])
                max_iteration = 0
                max_iteration_record = None
                for data in dataa:
                    for line in data.data_line_ids:
                        if line.iteration and line.iteration > max_iteration:
                            max_iteration = line.iteration
                            max_iteration_record = line
                if max_iteration_record and max_iteration_record.iter_comp_boolean:
                    rec.iteration = max_iteration + 1
                else:
                    rec.iteration = max_iteration
                rec.iter_comp_boolean = False
            else:
                dataa = self.env['kw_test_case_exec'].sudo().search([
                    ('testing_level', '=', rec.case_execute_id.testing_level.id),
                    ('project_id', '=', rec.case_execute_id.project_id.id),
                    ('module_id', '=', rec.case_execute_id.module_id.id)
                ])
                max_iteration = 0
                max_iteration_record = None
                for data in dataa:
                    for line in data.data_line_ids:
                        if line.iteration and line.iteration > max_iteration:
                            max_iteration = line.iteration
                            max_iteration_record = line
                if max_iteration_record and max_iteration_record.iter_comp_boolean:
                    rec.iteration = max_iteration + 1
                elif  max_iteration == 0:
                    rec.iteration = 1
                else:
                    rec.iteration = max_iteration

    @api.depends('bug_ids')
    def _compute_bug_id_status(self):
        for record in self:
            if record.bug_ids:
                bug_status_list = []
                for bug in record.bug_ids:
                    if bug.state in ['Draft', 'New']:
                        color = 'red'
                    elif bug.state in ['Progressive', 'Hold', 'Done', 'Rejected']:
                        color = '#dcaa00'
                    elif bug.state == 'Closed':
                        color = 'green'
                    bug_url = f'/web#id={bug.id}&model=kw_raise_defect&view_type=form'
                    bug_status = f'<a href="{bug_url}" style="color: {color}; text-decoration: underline;" onclick="window.location.href=\'{bug_url}\'">\
                                        {bug.number} - {bug.state}</a>'
                    bug_status_list.append(bug_status)
                record.bug_id_status = Markup(', '.join(bug_status_list))
            else:
                record.bug_id_status = ''

    @api.onchange('scenario_id')
    def get_default_result(self):
        for rec in self:
            data = self.env['kw_tc_execution_type'].sudo().search([('code', '=', 'NOTEXC')], limit=1)
            rec.result = data

    def button_raises(self):
        view_id = self.env.ref("kw_bug_life_cycle.kw_raise_form").id
        action = {
            'name': 'Raise Defect',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_raise_defect',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            'context': {'default_project_id':self.case_execute_id.project_id.project_id.id,
                        'default_step_to_reproduce_bug':self.test_data_action,
                        'default_description':self.actual,
                        'default_module_id':self.case_execute_id.module_id.id,
                        'default_ts_id':self.scenario_id.id,
                        'default_tc_id':self.id,
                        'default_scenario_description':self.scenario,
                        'default_tc_description':self.test_case_description,
                        'record_id':self.id,
                        'raised_by_tc_exe':1}
        }
        return action

    def unlink(self):
        for record in self:
            if record.restrict_delete_bool:
                raise ValidationError('You cannot delete this record as TC ID has already been generated.')
        return super(TestCaseDataLine, self).unlink()






class KwTestCaseLineWizard(models.TransientModel):
    _name = 'kw_test_case_line_wizard'
    _description = 'Add Test Case Lines Wizard'

    def get_test_scenario(self):
        record = self.env.context.get('current_record')
        data = self.env['kw_test_case_upload'].sudo().search([('id', '=', record)], limit=1)
        sce_li = []
        if data.testing_level.name != 'SIT':
            sce_li = self.env['test_scenario_master'].sudo().search([('project_id', '=', data.project_id.id),
                                                                     ('module_id', '=', data.module_id.id),
                                                                     ('test_lead_reject_boolean', '=', False)]).ids
        elif data.testing_level.name == 'SIT':
            sce_li = self.env['test_scenario_master'].sudo().search([('project_id', '=', data.project_id.id),
                                                                     ('test_lead_reject_boolean', '=', False)]).ids
        return [('id', 'in', sce_li)]

    testing_level = fields.Many2one('testing_level_config_master', string='Testing Level', readonly=True)
    project_id = fields.Many2one('kw_bug_life_cycle_conf', string='Project', readonly=True)
    module_id = fields.Many2one('bug_module_master', string='Global Link', readonly=True)

    sub_reference = fields.Char(string='Sub Reference')
    scenario_id = fields.Many2one('test_scenario_master', domain=get_test_scenario,  string='Test Scenario ID')
    pos_neg = fields.Char(string='Positive/Negative')
    test_data_action = fields.Char(string="Test Data/Action")
    expectation = fields.Char(string="Expected Result")
    test_case_description = fields.Char(string="Test Case Description")

    @api.model
    def default_get(self, fields):
        res = super(KwTestCaseLineWizard, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        if active_id:
            test_case = self.env['kw_test_case_upload'].browse(active_id)
            res.update({
                'testing_level': test_case.testing_level.id,
                'project_id': test_case.project_id.id,
                'module_id': test_case.module_id.id,
            })
        return res

    def action_add_line(self):
        """Add the line to the main model"""
        active_id = self.env.context.get('active_id')
        test_case = self.env['kw_test_case_upload'].browse(active_id)
        test_case.data_line_ids.create({
            'sub_reference': self.sub_reference,
            'scenario_id': self.scenario_id.id,
            'pos_neg': self.pos_neg,
            'test_data_action': self.test_data_action,
            'expectation': self.expectation,
            'case_upload_id': test_case.id,
            'test_case_description':self.test_case_description,
        })


class kw_tc_execution_types(models.Model):
    _name = "kw_tc_execution_type"
    _description = "Test Case Execution Type"
    _rec_name = "name"

    name = fields.Char('Name', required=True)
    code = fields.Char(string="Code", required=True)        
