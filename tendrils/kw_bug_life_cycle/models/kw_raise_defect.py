import base64
from datetime import date, datetime,timedelta
import datetime
from odoo.tools.mimetypes import guess_mimetype
from kw_utility_tools import kw_validations
from odoo import fields, models, api,_
from odoo.exceptions import ValidationError,UserError
# import logging
# _logger = logging.getLogger(__name__)

# Define the mapping for next stages based on the current state
NEXT_STAGE_MAPPING = {
    'New': 'Acknowledge/Fix/Forward/Reject',
    'Progressive': 'Hold/Fixed',
    'Hold': 'Fixed',
    'Done': 'Closed/Reopen'
}


class RaiseDefect(models.Model):
    _name = 'kw_raise_defect'
    _description = "Bug Life Cycle"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'number'

    def _default_employee(self):
        return self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)

    def get_emp_project(self):
        project_data = []
        bug_life_cycle_confs = self.env['kw_bug_life_cycle_conf'].sudo().search([])
        for rec in bug_life_cycle_confs:
            for recc in rec.user_ids:
                if recc.user_type == 'Tester' or recc.user_type == 'Test Lead':
                    if self.env.user.id == recc.employee_id.user_id.id:
                        project_data.append(rec.project_id.id)
        return [('id', '=', project_data)]


    def get_developer_id(self):
        domain = [('id', '=', 0)]
        if self._context.get('developer_id'):
            domain = [('id', 'in', self._context.get('developer_id'))]
        return domain


    employee_id = fields.Many2one('hr.employee', default=_default_employee, string="Logged By",
                                  track_visibility='always')
    designation = fields.Many2one('hr.job', string="Designation", track_visibility='always')
    department_id = fields.Many2one('hr.department', store=True, track_visibility='always')
    division = fields.Many2one('hr.department', store=True, track_visibility='always')
    users_email = fields.Char(string='Employee Email', store=True, track_visibility='always')
    state = fields.Selection(string="Status",
                             selection=[('Draft', 'Draft'),
                                        ('New', 'New/Reopen'),
                                        ('Progressive', 'Progressive'),
                                        ('Hold', 'Hold'),
                                        ('Done', 'Fixed & Deployed In Test Server'),
                                        ('Rejected', 'Rejected'),
                                        ('Closed', 'Closed')
                                        ], default="Draft", track_visibility='onchange')
    number = fields.Char(string='Defect ID', default="New",
                         readonly=True, track_visibility='always')
    defect_create_ids = fields.One2many('defect_create_table','raise_defect_id',
                                        string="Defects", track_visibility='always')
    project_id = fields.Many2one('project.project', required=True ,  domain=get_emp_project, track_visibility='always')
    module_id = fields.Many2one('bug_module_master', track_visibility='always', required=True)
    sub_module_name_id = fields.Many2one('bug_sub_module_master',"Sub Module Name", track_visibility='always',
                                         required=True)
    screen_id = fields.Many2one("screen_master", 'Screen', track_visibility='always' , required=True)
    navigation = fields.Text('Navigation', required=True)
    developer_id = fields.Many2one('hr.employee', string="Pending At", track_visibility='always', domain=get_developer_id)
    module_lead_id = fields.Many2one('hr.employee', string="Module Lead Name",
                                     track_visibility='always')
    open_date = fields.Datetime(string="Open Date", readonly=True,
                                track_visibility='always')
    close_date = fields.Datetime(string="Closed Date", readonly=True,
                                 track_visibility='always')
    emp_location = fields.Many2one('kw_res_branch', string="Location", track_visibility='always')
    developer_assign_boolean = fields.Boolean()
    # description = fields.Text('Description')
    pending_at = fields.Many2many('hr.employee', string="Pending At")
    manager_id = fields.Many2one('hr.employee', readonly=True)
    test_lead_boolean = fields.Boolean(compute='get_all_compute_field_value', store=False)
    assigned_by = fields.Many2one('hr.employee', string="Last Action By")
    developer_button_boolean = fields.Boolean(compute='get_all_compute_field_value', store=False)
    developer_hold_button = fields.Boolean(compute='get_all_compute_field_value', store=False)
    developer_done_inp_button = fields.Boolean(compute='get_all_compute_field_value', store=False)
    developer_go_to_inp_button = fields.Boolean(compute='get_all_compute_field_value', store=False)
    raised_by_boolean_btn = fields.Boolean(compute='get_all_compute_field_value', store=False)
    dev_filed_boolean = fields.Boolean(default=True)
    forward_to = fields.Many2one('hr.employee')
    module_lead_boolean = fields.Boolean(compute='get_all_compute_field_value', store=False)
    application = fields.Selection(string="Application Type",
                                   selection=[('web', 'Web'), ('mobile', 'Mobile'), ('desktop', 'Desktop'), ('api', 'API'), ('embeded', 'Embeded'), ('database', 'Database')],
                                   track_visibility='onchange', default='web')
    year_of_experience=fields.Char(string="Year Of Experience",related='employee_id.total_experience_display')
    priority_id = fields.Many2one('priority_master',string="Priority",required=True)
    severity = fields.Many2one('severity_master' , string="Severity" , required=True)
    testing_level = fields.Many2one('testing_level_config_master', string="Testing Hierarchy", required=True, domain="[('name','not in',['SIT', 'Functional'])]")
    action_log_table_ids = fields.One2many('bug_log_table', 'bug_con_id' )
    snap_action_log_ids = fields.One2many('bug_snap_log_table', 'snap_bug_id')
    bug_con_id =fields.Many2one('kw_bug_life_cycle_conf')
    end_user = fields.Text('End User', required=True)
    ui_control_name = fields.Text('Associated Field', required=True)
    is_it_slipped_in_unit_testing = fields.Selection(string='Is It Skipped During UNIT TESTING.?', selection=[('Yes', 'Yes'),
                                                                                                              ('No', 'No'), ('Can\'t Say', 'Can\'t Say')])
    project_emp_ids = fields.Many2many('hr.employee','kw_employee_raise_bug_rel','employee_id','raise_id',string='Project', readonly=True)
    sla_question = fields.Selection(selection=[('yes', 'Yes'),
                                               ('no', 'No'),
                                               ('Unaware', 'Unaware')], string=" ")
    required_resolation_time =  fields.Float()
    required_resolation_time_given_on = fields.Datetime()
    current_datetime=fields.Datetime(string="Date Time")
    progressive_time=fields.Datetime(string="Date Time")
    remarks_defect = fields.Text(string="Remarks")
    issue_duplicate = fields.Boolean(string='Is it a Repeated issue?')
    test_lead_org_boolean = fields.Boolean(compute='get_all_compute_field_value', store=False)
    test_lead_close_boolean = fields.Boolean(compute='get_closed_sev_pri_value', store=False)
    submit_bug_date = fields.Datetime()
    assign_bug_date = fields.Datetime()
    accept_bug_date = fields.Datetime()
    reject_bug_date = fields.Datetime()
    hold_bug_date = fields.Datetime()
    go_to_inprogress_bug_date = fields.Datetime()
    fixed_bug_date = fields.Datetime()
    reopen_bug_date = fields.Datetime()
    closed_bug_date = fields.Datetime()
    forward_bug_date = fields.Datetime()
    step_to_reproduce_bug = fields.Html()
    assign_employee_ids = fields.Many2many('hr.employee','assign_employee_raise_defect_rel','employee_id','raise_defect_id',string='Assign Employee')
    my_project_employee_ids = fields.Many2many('hr.employee','my_project_employee_raise_defect_rel','employee_id','raise_defect_id', string='My Project Employee')
    confirm_bool = fields.Boolean(string="Confirm bool",default=False)
    my_project_boolean = fields.Boolean()
    status_of_bug = fields.Char(string="Status",compute="get_status_of_bug", store=False)
    bug_type = fields.Many2one('bug_type_master', string='Bug Type')
    description = fields.Text(string='Bug Description')
    snap_shot = fields.Binary("Upload Snap", attachment=True, help="", required=True)
    bug_cycle = fields.Integer(store=False, compute="get_bug_cycle", string="Cycle")
    reminder_count = fields.Integer(string='Reminder Count', default=1)
    ts_id = fields.Many2one('test_scenario_master', 'TS ID')
    scenario_description = fields.Char(string="Test Scenario Description")
    tc_id = fields.Many2one('kw_test_case_data_line', string="TC ID")
    tc_description = fields.Char(string='TC Description')
    
    @api.constrains('snap_shot')
    def validate_upload_file(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf', 'application/zip']
        for record in self:
            mimetype = guess_mimetype(base64.b64decode(record.snap_shot))
            if str(mimetype) not in allowed_file_list:
                raise ValidationError(_("Unsupported file format ! allowed file formats are .jpg , .jpeg , .png , .zip and .pdf "))
            elif  ((len(record.snap_shot)*3/4)/1024)/1024 > 5.0:
                raise ValidationError(_("Maximum file size should be less than 5 mb."))
            kw_validations.validate_file_mimetype(record.snap_shot, allowed_file_list)
            kw_validations.validate_file_size(record.snap_shot, 5)
    def get_bug_cycle(self):
        for rec in self:
            fixed_count = 0
            for action_log in rec.action_log_table_ids:
                if action_log.state == 'Fixed & Deployed In Test Server' or action_log.state =='Rejected':
                    fixed_count += 1
            rec.bug_cycle = fixed_count

    def get_all_compute_field_value(self):
        kw_bug_life_cycle_conf = self.env['kw_bug_life_cycle_conf'].sudo().search(
            [('project_id', '=', self.project_id.id)])
        module_leads = [recc.employee_id.user_id.id for recc in kw_bug_life_cycle_conf.user_ids if
                        recc.user_type == 'Module Lead']
        test_leads = [recc.employee_id.user_id.id for recc in kw_bug_life_cycle_conf.user_ids if
                      recc.user_type == 'Test Lead']
        dev_list = [recc.employee_id.id for recc in kw_bug_life_cycle_conf.user_ids if recc.user_type == 'Developer']
        user_id = self.env.user.id
        employee_ids_id = self.env.user.employee_ids.id
        self.module_lead_boolean = user_id in module_leads and self.forward_to.id == employee_ids_id
        self.test_lead_boolean = user_id in test_leads and employee_ids_id in self.pending_at.ids
        self.test_lead_org_boolean = user_id in test_leads
        self.developer_button_boolean = self.developer_id.id in dev_list and self.developer_id.id == employee_ids_id
        self.developer_hold_button = self.state == 'Progressive' and self.developer_id.id == employee_ids_id
        self.developer_go_to_inp_button = self.state == 'Hold' and self.developer_id.id == employee_ids_id
        self.developer_done_inp_button = self.state == 'Rejected' and self.developer_id.id == employee_ids_id
        self.raised_by_boolean_btn = self.employee_id.id == employee_ids_id

    def get_closed_sev_pri_value(self):
        kw_bug_life_cycle_conf = self.env['kw_bug_life_cycle_conf'].sudo().search(
            [('project_id', '=', self.project_id.id)])
        test_leads = [recc.employee_id.user_id.id for recc in kw_bug_life_cycle_conf.user_ids if
                      recc.user_type == 'Test Lead']
        user_id = self.env.user.id
        is_not_closed = self.state != 'closed'
        self.test_lead_close_boolean = is_not_closed and user_id in test_leads

    def get_status_of_bug(self):
        for recc in self:
            bug_rec = self.env['bug_log_table'].sudo().search([('bug_con_id', '=', recc.id)], order='create_date desc', limit=1)
            if bug_rec:
                bug_state = {
                    'Submitted': 'New',
                    'Assigned': 'New',
                    'New': 'New',
                    'Acknowledged': 'Progressive',
                    'Forwarded':'Forwarded',
                    'Hold': 'Hold',
                    'Fixed & Deployed In Test Server': 'Fixed & Deployed In Test Server',
                    'Closed': 'Closed',
                    'Rejected': 'Rejected',
                    'Reopened': 'Reopened'
                }.get(bug_rec.state, 'Draft')
                recc.status_of_bug = bug_state
            else:
                recc.status_of_bug = 'Draft'

    def edit_bug_rec(self):
        emp_list = []
        if self.project_id:
            data = self.env['kw_bug_life_cycle_conf'].search([('project_id', '=', self.project_id.id)])
            for user in data.user_ids:
                if user.user_type in ['Developer', 'Module Lead']:
                    emp_list.append(user.employee_id.id)
        bug_view_id = self.env.ref("kw_bug_life_cycle.kw_raise_form").id
        action = {
            'name': 'Raise Defect',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_raise_defect',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': bug_view_id,
            'target': 'current',
            'res_id': self.id,
            'context': {'developer_id': emp_list},
            'flags': {'mode': 'edit'},
        }
        return action

    def get_my_project(self):
        query = f'''SELECT kr.id FROM kw_raise_defect AS kr
                    JOIN kw_bug_life_cycle_conf AS kbc ON kbc.id = kr.bug_con_id
                    JOIN kw_bug_life_cycle_conf_user_field AS kbcu ON kbcu.cycle_bug_conf_id = kbc.id
                    WHERE kbcu.employee_id = {self.env.user.employee_ids.id}'''
        self.env.cr.execute(query)
        result = self.env.cr.fetchall()
        ids_list = [row[0] for row in result]
        tree_view_id = self.env.ref('kw_bug_life_cycle.kw_raise_list').id
        form_view_id = self.env.ref('kw_bug_life_cycle.kw_raise_form').id
        action = {'type': 'ir.actions.act_window',
                  'name': 'My Project',
                  'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                  'view_mode': 'tree,form',
                  'res_model': 'kw_raise_defect',
                  'domain': [('id', 'in', ids_list)],
                  'context': {'delete': True, 'my_project':True},
                  }
        return action

    @api.model
    def create(self,vals):
        record = super(RaiseDefect, self).create(vals)
        if record:
            self.env.user.notify_success(message='Raise defect created successfully.')
        return record
    @api.multi
    def unlink(self):
        for rec in self:
            emp_list =[]
            data = self.env['kw_bug_life_cycle_conf'].search([('project_id', '=', rec.project_id.id)])
            for user in data.user_ids:
                if user.user_type in ['Test Lead']:
                    emp_list.append(user.employee_id.id)
            if self.env.user.employee_ids.id in emp_list:
                self.env.user.notify_success(message='Assign Record deleted successfully.')
            else:
                raise UserError("You have no access to delete this record.")
        return super(RaiseDefect, self).unlink()
        

    @api.onchange('project_id')
    def get_p_id(self):
        for rec in self:
            emp_list = []
            my_project_list = []
            if rec.project_id:
                data = self.env['kw_bug_life_cycle_conf'].search([('project_id', '=', rec.project_id.id)])
                for user in data.user_ids:
                    my_project_list.append(user.employee_id.id)
                    if user.user_type in ['Developer', 'Module Lead']:
                        emp_list.append(user.employee_id.id)
                rec.assign_employee_ids = False
                rec.bug_con_id = data.id
                rec.assign_employee_ids = [(6, False, emp_list)]
                rec.my_project_employee_ids = False
                rec.my_project_employee_ids = [(6, False, my_project_list)]


    @api.onchange('sub_module_name_id')
    def get_sub_module(self):
        self.screen_id = False

    @api.constrains('step_to_reproduce_bug')
    def validation_defects(self):
        if  self.step_to_reproduce_bug == "<p><br></p>":
            raise ValidationError('Steps To Reproduce Details must not be empty! ')
        # if len(self.defect_create_ids.ids) > 1:
        #     raise ValidationError('Warning! You cannot add multiple lines.')
        # if not self.defect_create_ids.ids:
        #     raise ValidationError("Warning! Enter Bug Type, Bug Description and Upload Snap.")

    @api.onchange('project_id')
    def get_project_employee(self):
        for rec in self:
            emp_list = []
            if rec.project_id and rec.state in ['Draft']:
                data = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([])
                for recc in data:
                    emp_list.append(recc.employee_id.id)
            rec.project_emp_ids = [(4, id, False) for id in emp_list]

    @api.onchange('project_id')
    def get_module_id(self):
        if self.env.context.get('raised_by_tc_exe'):
            self.sub_module_name_id = False
            self.screen_id = False
            self.testing_level = False
            self.project_emp_ids = False
            if self.project_id:
                data = self.env['kw_bug_life_cycle_conf'].sudo().search([('project_id', '=', self.project_id.id)]).id
                dataa = self.env['bug_module_master'].sudo().search([('project_id', '=', data)]).mapped('id')
                return {'domain': {'module_id': [('id', 'in', dataa)]}}
            else:
                return {'domain': {'module_id': [('id', 'in', [])]}}
        else:
            self.module_id = False
            self.sub_module_name_id = False
            self.screen_id = False
            self.testing_level = False
            self.project_emp_ids = False
            if self.project_id:
                data = self.env['kw_bug_life_cycle_conf'].sudo().search([('project_id', '=', self.project_id.id)]).id
                dataa = self.env['bug_module_master'].sudo().search([('project_id', '=', data)]).mapped('id')
                return {'domain': {'module_id': [('id', 'in', dataa)]}}
            else:
                return {'domain': {'module_id': [('id', 'in', [])]}}

    @api.onchange('module_id')
    def get_sub_module_data(self):
        self.sub_module_name_id = False
        self.screen_id = False
        if self.module_id:
            module_dataa = self.env['bug_module_master'].sudo().search([('id', '=', self.module_id.id)]).mapped('id')
            sub_data = self.env['bug_sub_module_master'].sudo().search([('module_id', 'in', module_dataa)]).mapped('id')
            return {'domain': {'sub_module_name_id': [('id', 'in', sub_data)]}}
        else:
            return {'domain': {'sub_module_name_id': [('id', '=', False)]}}

    @api.onchange('sub_module_name_id')
    def get_navigation_data(self):
        if self.sub_module_name_id:
            sub_module_dataa = self.env['bug_sub_module_master'].sudo().search([('id', '=', self.sub_module_name_id.id)]).mapped('id')
            screen_data = self.env['screen_master'].sudo().search([('reg_sub_module_id', 'in', sub_module_dataa)]).mapped('id')
            return {'domain': {'screen_id': [('id', 'in', screen_data)]}}
        else:
            return {'domain': {'screen_id': [('id', '=', False)]}}

    @api.onchange('project_id', 'employee_id')
    def get_manager(self):
        if self.project_id:
            data = self.env['kw_bug_life_cycle_conf'].sudo().search([('project_id', '=', self.project_id.id)])
            for recc in data.user_ids:
                if recc.user_type == 'Manager':
                    self.manager_id = recc.employee_id.id

    @api.onchange('employee_id')
    def _change_employee(self):
        for rec in self:
            rec.department_id = rec.employee_id.department_id.id if rec.employee_id.department_id else False
            rec.division = rec.employee_id.division.id if rec.employee_id.division else False
            rec.users_email = rec.employee_id.work_email if rec.employee_id.work_email else False
            rec.emp_location = rec.employee_id.job_branch_id if rec.employee_id.job_branch_id else False
            rec.designation = rec.employee_id.job_id.id if rec.employee_id.job_id else False

    @api.onchange('project_id')
    def get_project_resource(self):
        emp_list = []
        if self.project_id:
            data = self.env['kw_bug_life_cycle_conf'].sudo().search([('project_id', '=', self.project_id.id)])
            for rec in data.user_ids:
                if rec.user_type in ['Developer', 'Module Lead']:
                    emp_list.append(rec.employee_id.id)
        return {'domain': {'developer_id': [('id', 'in', emp_list)]}}

    @api.multi
    def btn_submit(self):
        for rec in self:
            if rec.developer_id:
                dev_list = []
                data = self.env['kw_bug_life_cycle_conf'].sudo().search([('project_id', '=', rec.project_id.id)])
                for recc in data.user_ids:
                    if recc.user_type == 'Developer':
                        dev_list.append(recc.employee_id.id)
                if rec.developer_id.id in dev_list:
                    rec.dev_filed_boolean = False
                    rec.developer_assign_boolean = True
                    rec.assign_bug_date = datetime.datetime.now()
                    rec.pending_at = [(4, rec.developer_id.id, False)]
                    rec.assigned_by = self.env.user.employee_ids.id
                    user_designation = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([('employee_id', '=', self.env.user.employee_ids.id), ('cycle_bug_conf_id.project_id', '=', self.project_id.id)])
                    rec.write({'action_log_table_ids':[[0, 0, {'state':'Submitted',
                                                               'designation': user_designation.user_type,
                                                               'remark':'Assign to developer',
                                                               'action_taken_by': self.env.user.employee_ids.name,
                                                               }]]})
                else:
                    rec.dev_filed_boolean = False
                    rec.assigned_by = self.env.user.employee_ids.id
                    rec.developer_assign_boolean = False
                    rec.pending_at = [(4, rec.developer_id.id, False)]
                    rec.forward_to = rec.developer_id.id
                    rec.module_lead_boolean = True
                    user_designation = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search(
                        [('employee_id', '=', self.env.user.employee_ids.id),
                         ('cycle_bug_conf_id.project_id', '=', self.project_id.id)])
                    rec.write({'action_log_table_ids': [[0, 0, {'state': 'Submitted',
                                                                'designation': user_designation.user_type,
                                                                'remark': 'Assign to module lead',
                                                                'action_taken_by': self.env.user.employee_ids.name,
                                                                }]]})
            else:
                if not rec.confirm_bool:
                    view_id = self.env.ref("kw_bug_life_cycle.confirm_wizard_view1_form").id
                    return {
                        'name': 'Confirm',
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'views': [(view_id, 'form')],
                        'res_model': 'kw_bug_remark_wizards',
                        'view_id': view_id,
                        'target': 'new',
                    }
                rec.dev_filed_boolean = False
                rec.developer_assign_boolean = False
                data = self.env['kw_bug_life_cycle_conf'].sudo().search([('project_id', '=', rec.project_id.id)])
                test_lead_id=[]
                for recc in data.user_ids:
                    if recc.user_type == 'Test Lead':
                        test_lead_id.append(recc.employee_id.id)
                rec.pending_at = [(4, id, False) for id in test_lead_id]
                user_designation = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([('employee_id', '=', self.env.user.employee_ids.id), ('cycle_bug_conf_id.project_id', '=', self.project_id.id)])
                rec.write({'action_log_table_ids':[[0, 0, {'state':'Submitted',
                                                           'designation':user_designation.user_type,
                                                           'remark':'Assign to test lead',
                                                           'action_taken_by': self.env.user.employee_ids.name,
                                                           }]]})
            seq_prefix = rec.project_id.name
            existing_sequences = self.env['ir.sequence'].search([('code', '=', 'self.kw_raise_defect')])
            existing_sequence = existing_sequences.filtered(lambda seq: seq.prefix == seq_prefix)
            if existing_sequence:
                seq = existing_sequence.next_by_id() or '/'
            else:
                new_sequence_vals = {
                    'name': f'{seq_prefix} Sequence',
                    'code': 'self.kw_raise_defect',
                    'prefix': seq_prefix,
                    'padding': 3,
                }
                new_sequence = self.env['ir.sequence'].sudo().create(new_sequence_vals)
                seq = new_sequence.next_by_id() or '/'
            formatted_sequence = f"{seq_prefix}||{seq.split(seq_prefix)[-1].strip('-')}"
            rec.number = formatted_sequence

            template1 = self.env.ref('kw_bug_life_cycle.email_template_for_tester')
            data = self.env['kw_bug_life_cycle_conf'].sudo().search([('project_id', '=', rec.project_id.id)])
            test_module_id = []
            developer_id = []
            for recc in data.user_ids:
                if recc.user_type in ['Test Lead','Module Lead']:
                    test_module_id.append(recc.employee_id.work_email)
                if recc.user_type == 'Developer':
                    developer_id.append(recc.employee_id.id)
            if template1:
                test_module_id.append(rec.employee_id.work_email)
                if rec.developer_id.id in developer_id:
                    dev_name=rec.developer_id.name
                    email_to = rec.developer_id.work_email
                    email_cc = ','.join(set(test_module_id))
                    subject = f"Bug Repository || {rec.project_id.name} || New Ticket Creation"
                    template1.with_context(mail_for='Test',email_to = email_to,mail_cc=email_cc,subject = subject,tname=rec.employee_id.name, name = dev_name). \
                        send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                else:
                    for recc in rec.pending_at:
                        email_to=recc.work_email if recc.work_email else ''
                        name=recc.name
                        email_cc = ','.join(set(test_module_id))
                        subject = f"Bug Repository || {rec.project_id.name} || New Ticket Creation"

                        template1.with_context(mail_for='Test',email_to = email_to,subject = subject, mail_cc=email_cc,tname=rec.employee_id.name, name = name). \
                            send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            rec.current_datetime=datetime.datetime.now()
            rec.state = 'New'
            rec.submit_bug_date = datetime.datetime.now()
            rec.open_date = datetime.datetime.now()
            rec.write({'snap_action_log_ids': [[0, 0, {'state': 'Submitted',
                                                       'snap_shot':rec.snap_shot,
                                                       'snap_upload_by': self.env.user.employee_ids.name,
                                                       }]]})
            # if self._context.get('raised_by_tc_exe') and self._context.get('record_id'):
            if self.tc_id:
                test_case_data_line = self.env['kw_test_case_data_line'].sudo().search([('id', '=', self.tc_id.id)])
                test_case_data_line.write({
                    'bug_ids': [(4, rec.id)],
                    'result_readonly_boolean':True
                })
    def btn_assign_wizard(self):
        view_id = self.env.ref('kw_bug_life_cycle.developer_assign_wizards_form').id
        return {
            'name': 'Developer Assign Wizard',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'kw_developer_assign_wizards',
            'target': 'new',
        }

    def btn_accept_ticket(self):
        view_id = self.env.ref('kw_bug_life_cycle.kw_all_remark_wizards_form').id
        return {
            'name': 'Remarks Wizards',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'kw_bug_remark_wizards',
            'target': 'new',
            'context': {
                'button_name': 'Accept Ticket',
                'default_invisible_boolean': True
            }
        }

    def btn_hold(self):
        view_id = self.env.ref('kw_bug_life_cycle.kw_all_remark_wizards_form').id
        return {
            'name': 'Remarks Wizards',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'kw_bug_remark_wizards',
            'target': 'new',
            'context': {
                'button_name': 'Hold'
            }
        }

    def btn_done(self):
        view_id = self.env.ref('kw_bug_life_cycle.kw_all_remark_wizards_form').id
        return {
            'name': 'Remarks Wizards',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'kw_bug_remark_wizards',
            'target': 'new',
            'context': {
                'button_name': 'Done',
                'default_done_button_boolean': True
            }
        }

    def btn_close_stage(self):
        view_id = self.env.ref('kw_bug_life_cycle.kw_all_remark_wizards_form').id
        return {
            'name': 'Remarks Wizards',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'kw_bug_remark_wizards',
            'target': 'new',
            'context': {
                'button_name': 'Close',
                'default_close_button_boolean': True
            }
        }

    def btn_cancel(self):
        view_id = self.env.ref('kw_bug_life_cycle.kw_all_remark_wizards_form').id
        return {
            'name': 'Remarks Wizards',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'kw_bug_remark_wizards',
            'target': 'new',
            'context': {
                'button_name': 'Cancel'
            }
        }
    def btn_goto_inprogress_stage(self):
        self.state  = 'Progressive'
        self.go_to_inprogress_bug_date = datetime.datetime.now()

    def btn_reopen_stage(self):
        view_id = self.env.ref('kw_bug_life_cycle.kw_all_remark_wizards_form').id
        return {
            'name': 'Remarks Wizards',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'kw_bug_remark_wizards',
            'target': 'new',
            'context': {
                'button_name': 'Reopen',
                'default_assigned_boolean': True,
                'default_project_id': self.project_id.id
            }
        }

    def btn_forward_stage(self):
        for rec in self:
            view_id = self.env.ref('kw_bug_life_cycle.kw_forword_bug_wizards_form').id
            return {
                'name': 'Forword Module Lead',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'kw_forword_bug_wizards',
                'view_id': view_id,
                'target': 'new',
                'context': {'default_project_id': rec.project_id.id,
                            },
            }


    @api.multi
    def bug_form_view_action_button(self):
        for rec in self:
            form_view = self.env.ref("kw_bug_life_cycle.kw_raise_form").id
            bug_rec = self.env['kw_raise_defect'].sudo().search([('number', '=', rec.number),
                                                                 ('state', '=',rec.state ),
                                                                 ('project_id', '=',rec.project_id.id )])
            if bug_rec:
                bug_rec = bug_rec[0]
                return {
                    'name': 'Form View',
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_raise_defect',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': bug_rec.id,
                    'target': 'self',
                    'view_id':form_view,
                    'context': {'edit': False, 'create': False, 'delete': False},
                }

    def calculate_datetime(self,hour, holiday_dates, start_datetime):
        target_datetime = start_datetime
        for i in range(hour):
            target_datetime += datetime.timedelta(hours=1)
            while target_datetime.date() in holiday_dates or target_datetime.weekday() >= 5:
                target_datetime += datetime.timedelta(days=1)
        return target_datetime

    def calculate_office_time(self, current_datetime, target_hours, attendance_record, weekoff_dates, holidays_dates):
        assigned_date = current_datetime + timedelta(hours=5,minutes=30)
        remaining_hours = target_hours
        while remaining_hours > 0:
            if assigned_date.date() not in holidays_dates and assigned_date.date() not in weekoff_dates:
                compare_start_time = assigned_date.replace(hour=int(attendance_record.shift_in_time), minute=0, second=0, microsecond=0)
                compare_end_time = assigned_date.replace(hour=int(attendance_record.shift_out_time), minute=0, second=0, microsecond=0)
                if assigned_date <= compare_start_time :
                    assigned_date = assigned_date.replace(hour=int(attendance_record.shift_in_time), minute=0, second=0, microsecond=0)
                    temp_remaining_hours = remaining_hours - 9
                    if temp_remaining_hours > 0:
                        assigned_date = assigned_date.replace(hour=int(attendance_record.shift_in_time), minute=0, second=0, microsecond=0) + timedelta(days=1)
                        remaining_hours = temp_remaining_hours
                    else:
                        assigned_date = assigned_date + timedelta(hours=remaining_hours)
                        remaining_hours = 0
                elif assigned_date > compare_end_time:
                    assigned_date = assigned_date.replace(hour=int(attendance_record.shift_in_time), minute=0, second=0, microsecond=0) + timedelta(days=1)
                else:
                    time_difference = (compare_end_time - assigned_date)
                    time_difference_hours = time_difference.total_seconds() / 3600.0
                    temp_remaining_hours = remaining_hours - time_difference_hours
                    if temp_remaining_hours <= 0:
                        assigned_date = assigned_date + timedelta(hours=remaining_hours)
                        remaining_hours = 0
                    else:
                        assigned_date = assigned_date.replace(hour=int(attendance_record.shift_in_time), minute=0, second=0, microsecond=0) + timedelta(days=1)
                        remaining_hours = temp_remaining_hours
            else:
                assigned_date =  assigned_date.replace(hour=int(attendance_record.shift_in_time), minute=0, second=0, microsecond=0) + timedelta(days=1)
                continue
        return assigned_date - timedelta(hours=5,minutes=30)


    def sla_config_mail_cron(self):
        # print('-------------------------------scheduler run for SLA---------------------------------')
        current_time1 = datetime.datetime.now()
        time_deltaa = datetime.timedelta(hours=5, minutes=30)
        new_time = current_time1 + time_deltaa
        current_time = new_time.time()
        range1_start = datetime.time(10, 45)
        range1_end = datetime.time(10, 50)
        range2_start = datetime.time(16, 30)
        range2_end = datetime.time(16, 35)
        record = self.env['kw_raise_defect'].sudo().search([('state', '!=', 'Draft')])
        if (range1_start <= current_time <= range1_end) or (range2_start <= current_time <= range2_end):
            for rec in record:
                holiday_rec = self.env['hr.holidays.public.line'].search(
                    [('date', 'like', current_time1.strftime('%Y-%m-%'))])
                holidays_dates = [holiday.date for holiday in holiday_rec]
                weekoff_rec = self.env['resource.calendar.leaves'].search(
                    [('start_date', 'like', current_time1.strftime('%Y-%m-%'))])
                weekoff_dates = [woff.start_date for woff in weekoff_rec]
                attendance_record = self.env['kw_daily_employee_attendance'].search(
                    [('employee_id.user_id', '=', rec.employee_id.user_id.id)], limit=1)
                time1 = 0
                time2 = 0
                time3 = 0
                time4 = 0
                time5 = 0
                time6 = 0
                if rec.sla_question == 'yes':
                    sla_data = self.env['sla_config'].sudo().search([('project_id', '=', rec.project_id.id)])
                    for recc in sla_data.sla_config_time_ids:
                        if recc.from_state == 'New' and recc.to_state == 'Acknowledged/Reject':
                            time1 += recc.time

                if rec.submit_bug_date and not rec.accept_bug_date or not rec.reject_bug_date:
                    if rec.calculate_office_time(rec.submit_bug_date, 5,
                                                 attendance_record, holidays_dates, weekoff_dates)+time_deltaa <= new_time:
                        pass

                if rec.accept_bug_date and not rec.hold_bug_date and not rec.fixed_bug_date:
                    if rec.calculate_office_time(rec.accept_bug_date, 5,
                                                 attendance_record, holidays_dates,
                                                 weekoff_dates) + time_deltaa <= new_time:
                        pass

                if rec.accept_bug_date and rec.hold_bug_date and not rec.fixed_bug_date:
                    if rec.calculate_office_time(rec.hold_bug_date, 5,
                                                 attendance_record, holidays_dates,
                                                 weekoff_dates) + time_deltaa <= new_time:
                        pass

                if rec.reject_bug_date and not rec.reopen_bug_date or rec.closed_bug_date:
                    if rec.calculate_office_time(rec.reject_bug_date, 5,
                                                 attendance_record, holidays_dates,
                                                 weekoff_dates) + time_deltaa <= new_time:
                        pass


    def daily_mail_to_pm_mail_cron(self):
        bug_record = self.env['kw_raise_defect'].sudo().search([('state', '!=', 'Draft')])
        project_bug_counts = {}
        if bug_record.exists():
            for bug in bug_record:
                project = bug.project_id.name
                key = (project)
                if key in project_bug_counts:
                    project_bug_counts[key] += 1
                else:
                    project_bug_counts[key] = 1
            for project, bug_count in project_bug_counts.items():
                data = self.env['kw_bug_life_cycle_conf'].sudo().search([('project_id.name', '=', project)])
                pm_id = []
                test_module_id = []
                pm_name = ''
                for recc in data.user_ids:
                    if recc.user_type == 'Manager':
                        pm_id.append(recc.employee_id.work_email)
                        pm_name = recc.employee_id.name
                    if recc.user_type in ['Test Lead', 'Module Lead']:
                        test_module_id.append(recc.employee_id.work_email)
                bug_ontotal= self.env["kw_raise_defect"].sudo().search_count([('project_id.name','=',project),('state','!=','Draft')])
                bug_onclosed= self.env["kw_raise_defect"].sudo().search_count([('state','=','Closed'),('project_id.name','=',project)])
                if bug_ontotal:
                    alive_data = bug_ontotal - bug_onclosed

                if pm_id:
                    template = self.env.ref('kw_bug_life_cycle.email_template_for_tester')
                    if template:
                        mail_to = ','.join(pm_id)
                        mail_cc = ','.join(test_module_id)
                        proj_name = project
                        subject = f"Bug Repository || {proj_name} || Daily PM Report"
                        template.with_context(mail_for='PM', alive_data=alive_data,email_to=mail_to, mail_cc=mail_cc, bug_count=bug_count,subject = subject, proj_name=proj_name, name=pm_name). \
                            send_mail(bug.id, notif_layout="kwantify_theme.csm_mail_notification_light")

    def daily_mail_to_developer_escalation_mail_cron(self):
        current_time = datetime.datetime.now()
        time_difference = timedelta(hours=5, minutes=30)
        new_time = current_time + time_difference
        template_obj = self.env.ref('kw_bug_life_cycle.email_template_escalation_reminder_mail')

        bug_record = self.env['kw_raise_defect'].sudo().search([('state', 'not in', ['Draft', 'Closed'])])

        recipient_bugs = {}

        for bug in bug_record:

            date_fields = [
                bug.create_date, bug.submit_bug_date, bug.assign_bug_date, bug.accept_bug_date, bug.reject_bug_date, 
                bug.hold_bug_date, bug.go_to_inprogress_bug_date, bug.fixed_bug_date, bug.reopen_bug_date, 
                bug.closed_bug_date, bug.forward_bug_date
            ]
            latest_date = max([date for date in date_fields if date]) + time_difference
            bug_last_action_datetime = new_time - latest_date
            total_seconds = bug_last_action_datetime.total_seconds()
            total_hours, remainder = divmod(total_seconds, 3600)
            total_minutes, total_seconds = divmod(remainder, 60)

            if total_hours >= 48:
                time_passed_formatted = f"{int(total_hours):02}:{int(total_minutes):02}"
                
                next_stage = NEXT_STAGE_MAPPING.get(bug.state, '')

                pending_users = [(user.name, user.work_email) for user in bug.pending_at]
                for name, email in pending_users:
                    reminder_count = bug.reminder_count if bug.reminder_count else 0
                    bug_info = {
                        'bug_id': bug.id,
                        'project': bug.project_id.name,
                        'ticket_id': bug.number,
                        'stage_bug': bug.state,
                        'next_stage': next_stage,
                        'time_from_last': time_passed_formatted,
                        'reminder_count': reminder_count,
                    }

                    if email in recipient_bugs:
                        recipient_bugs[email]['bugs'].append(bug_info)
                    else:
                        recipient_bugs[email] = {
                            'name': name,
                            'bugs': [bug_info]
                        }

        for email, info in recipient_bugs.items():
            name = info['name']
            bugs = info['bugs']

            data = self.env['kw_bug_life_cycle_conf'].sudo().search([('project_id.name', '=', bugs[0]['project'])])
            test_module_id = set(recc.employee_id.work_email for recc in data.user_ids if recc.user_type in ['Test Lead', 'Module Lead'])

            mail_cc = ','.join(test_module_id) if test_module_id else []
            subject = f"Bug Repository || {bugs[0]['project']} || Reminder/Escalation."

            if template_obj:
                template_obj.with_context(
                    email_to=email,
                    ticket_id=', '.join([bug['ticket_id'] for bug in bugs]),
                    bug_stage=bugs,
                    mail_cc=mail_cc,
                    subject=subject,
                    name=name,
                ).send_mail(bugs[0]['bug_id'], notif_layout="kwantify_theme.csm_mail_notification_light")

                for bug in bugs:
                    bug_obj = self.env['kw_raise_defect'].sudo().browse(bug['bug_id'])
                    current_reminder_count = bug_obj.reminder_count if bug_obj.reminder_count else 0
                    new_reminder_count = current_reminder_count + 1
                    bug_obj.sudo().write({'reminder_count': new_reminder_count})
                    print(f"Updated reminder_count for bug_id {bug_obj.id}: {new_reminder_count}")


    def developer_remainder_mail_cron(self):
        pass

    # @api.model
    # def create(self, vals):
    #     print('------------------checkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
    #     _logger.info("Creating a new record with vals: %s", vals)
    #     # Modify context separately
    #     bug_con_id = vals.get('bug_con_id')
    #     print(bug_con_id, 'wcreate_bug_con')
    #     context = dict(self.env.context, test=True, bug_con_id = bug_con_id)
    #     # Create the new record with the modified context
    #     new_record = super(RaiseDefect, self.with_context(context)).create(vals)
    #     _logger.info("Created new record: %s", new_record)
    #     return new_record


    # def write(self, vals):
    #     print('=======writeeeeeeeeeeeeeeeeee')
    #     _logger.info("Writing to record(s) with vals: %s", vals)
    #     bug_con_id = self.bug_con_id.id
    #     print(bug_con_id, 'write_bug_con')
    #     context = dict(self.env.context, test=True, bug_con_id = bug_con_id)
    #     result = super(RaiseDefect, self.with_context(context)).write(vals)
    #     _logger.info("Written to record(s) result: %s", result)
    #     return result

class DefectCreateTable(models.Model):
    _name = 'defect_create_table'
    _description = 'defect_create_table'

    module_name = fields.Html(string='Step To Reproduce')
    description = fields.Text(string='Bug Description')
    bug_type = fields.Many2one('bug_type_master')
    raise_defect_id = fields.Many2one('kw_raise_defect')
    snap_shot = fields.Binary("Upload Snap", attachment=True, help="", required=True)

    @api.constrains('snap_shot')
    def validate_upload_file(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf', 'application/zip']
        for record in self:
            mimetype = guess_mimetype(base64.b64decode(record.snap_shot))
            if str(mimetype) not in allowed_file_list:
                raise ValidationError(_("Unsupported file format ! allowed file formats are .jpg , .jpeg , .png , .zip and .pdf "))
            elif  ((len(record.snap_shot)*3/4)/1024)/1024 > 5.0:
                raise ValidationError(_("Maximum file size should be less than 5 mb."))
            kw_validations.validate_file_mimetype(record.snap_shot, allowed_file_list)
            print("in size format===========================================")
            kw_validations.validate_file_size(record.snap_shot, 5)


class CreateBugLogTable(models.Model):
    _name = 'bug_log_table'
    _description = 'bug_log_table'

    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    action_taken_by = fields.Char(string='Action Taken By')
    designation = fields.Char(string="Designation")
    remark = fields.Text(string='Remark')
    state = fields.Char(string='State')
    bug_con_id = fields.Many2one('kw_raise_defect')


class BugHREmployee(models.Model):
    _inherit = 'hr.employee'

    # def name_get(self):
    #     res = super(BugHREmployee, self).name_get()
    #     if self._context.get('test', False):
    #         # print('================11111111111111111111111111111111111111111111111===')
    #         bug_con_id = self._context.get('bug_con_id', False)
    #         # print(bug_con_id, '================bug pring')
    #         if bug_con_id:
    #             # print('===========================bug con id-------------------------------')
    #             kw_bug_life_cycle_conf = self.env['kw_bug_life_cycle_conf'].sudo().search(
    #                 [('id', '=', bug_con_id)]
    #             )
    #             Testing = [recc.employee_id.user_id.id for recc in kw_bug_life_cycle_conf.user_ids if recc.user_type in
    #                        ('Test Lead', 'Tester')]
    #             Development = [recc.employee_id.user_id.id for recc in kw_bug_life_cycle_conf.user_ids if recc.user_type
    #                            in ('Developer', 'Module Lead')]
    #             result = []
    #             for employee in self:
    #                 if employee.user_id.id in Testing:
    #                     name = 'Testing'
    #                 elif employee.user_id.id in Development:
    #                     name = 'Development'
    #                 result.append((employee.id, f'{employee.name} ({employee.emp_code}) ({name})'))
    #             return result
    #     return res

class SnapLogTable(models.Model):
    _name = 'bug_snap_log_table'
    _description = 'bug_snap_log_table'

    date = fields.Datetime(string='Date', default=fields.Datetime.now, )
    snap_upload_by = fields.Char(string='Snap Upload By')
    state = fields.Char(string='State')
    snap_shot = fields.Binary("Upload Snap", attachment=True, help="", required=True)
    snap_bug_id = fields.Many2one('kw_raise_defect')
    
    
    def get_snap_download(self):
        action_url = '/download-snap-bug/%s' % self.id
        return {
            'type': 'ir.actions.act_url',
            'url': action_url,
            'target': 'self',
        }
