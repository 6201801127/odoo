"""
Model: kw_cr_management

Description: This module contains a model for managing change requests in Kwantify.

"""
from odoo import models, fields, api 
from odoo.exceptions import ValidationError
from datetime import date,datetime


class kw_cr_management(models.Model):
    """
    Model class for Change Request Management in Kwantify.
    """
    _name = "kw_cr_management"
    _description = "CR Management"
    _rec_name = "reference_no"

    def get_project_data(self):
        emp_ids = self.env.user.employee_ids.ids
        project_ids = self.env['kw_project_environment_management'].sudo().search([('employee_ids', 'in', emp_ids)]).mapped(
            'project_id')
        return [('id', 'in', project_ids.ids)]

    project_id = fields.Many2one('project.project', string='Project Name', domain=get_project_data)
    project_code = fields.Char(string='Project Code', compute='_compute_project_code')
    project_manager_id = fields.Many2one('hr.employee', string='Project Code', related='project_id.emp_id')
    cr_type = fields.Selection(string='Type', selection=[('CR', 'CR'), ('Service', 'Service')], required=True)
    module_id = fields.Many2one('kw_project.module', string='Module Name', domain="[('project_id', '=', project_id)]")
    environment_id = fields.Many2one('kw_environment_master')
    url_or_service_name = fields.Char('URL or Service Name')
    description = fields.Text('Description')
    change_type = fields.Selection(string='Change Type',
                                   selection=[('New', 'New'), ('Cosmetic', 'Cosmetic'), ('Normal', 'Normal'),
                                              ('Major', 'Major')], default='New')
    activity = fields.Many2one('kw_cr_activity_master','Activity')
    estimate_activity_hour = fields.Float(string='Estimate Activity Hour',compute="_check_estimate_time_activity" ,store=True)
    sub_activity = fields.Many2one('kw_cr_sub_activity_master','Sub Activity')
    audit = fields.Text('Audit')
    change_impact = fields.Text('Change Impact')
    priority = fields.Selection(string='Priority', selection=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')],
                                default='Low')
    attachment_name = fields.Text('File Location')
    backup_required = fields.Selection(string='Backup Required', selection=[('Yes', 'Yes'), ('No', 'No')],
                                       default='No')
    reference_no = fields.Char(string='Reference')
    stage = fields.Selection([('Draft', 'Draft'), ('Applied', 'Applied'),('Test Lead Approved','Test Lead Approved'), ('Approve', 'Approve'),
                              ('Rollbacked', 'Rollbacked'), ('Cancel', 'Cancel'), ('Request', 'Request For Rollback'),
                              ('Reject', 'Reject'), ('Hold', 'Hold'), ('Uploaded', 'Uploaded'),('In Progress', 'In Progress')], default='Draft')
    is_manager = fields.Boolean(string="Is Manager?", default=False, compute="_check_manager")
    is_officer_user = fields.Boolean(string="Is Officer User?", default=False, compute='_check_manager')
    is_user = fields.Boolean(string="Is User?", default=False, compute='_check_manager')
    is_uploaded = fields.Boolean(string="Is Uploaded", default=False)
    is_cancel = fields.Boolean(string="Is Cancelled", default=False)
    cr_raised_by = fields.Many2one('hr.employee', 'CR Raised By')
    cr_cancelled_by = fields.Many2one('hr.employee', 'Cancelled By')
    cancel_cmt = fields.Text('Cancelled Comment')

    cr_raised_on = fields.Datetime('Raised')
    cr_uploaded_on = fields.Datetime('Uploaded')
    cr_rollbacked_on = fields.Datetime('Rollback')
    cr_cancelled_on = fields.Datetime('Cancelled')
    requesr_rollbacked_on = fields.Datetime('Request Rollback')
    cr_rejected_on = fields.Datetime('Rejected')
    cr_holded_on = fields.Datetime('Holded')
    cr_approved_on = fields.Datetime('Approved')

    uploaded_by = fields.Many2one('hr.employee', 'Uploaded By')
    uploaded_cmt = fields.Text('Uploaded Comment')

    rollbacked_by = fields.Many2one('hr.employee', 'Rollback By')
    rollbacked_cmt = fields.Text('Rollback Comment')

    request_for_rollback_id = fields.Many2one('hr.employee', 'Request Rollback By')
    request_for_rollback_cmt = fields.Text('Request Rollback Comment')

    cr_rejected_by = fields.Many2one('hr.employee', 'Rejected By')
    reject_cmt = fields.Text('Rejected Comment')

    cr_holded_by = fields.Many2one('hr.employee', 'Holded By')
    hold_cmt = fields.Text('Holded Comment')

    cr_approved_by = fields.Many2one('hr.employee', 'Approved By')
    approved_cmt = fields.Text('Approved Comment')
    platform_id = fields.Many2one('kw_cr_platform_master', 'Platform')
    notify_emp_ids = fields.Many2many('hr.employee', string='Notify To', domain=[('employement_type', '!=', 5)])
    pending_at = fields.Many2many('hr.employee', string='Pending At', compute='_check_pending_at')
    is_pm_approval_required = fields.Boolean(string="PM Approval Required?", default=False)

    prject_category_id = fields.Many2one('kw_project_category_master', string='Category Name',
                                         domain=[('code', '=', 'PW')], index=True)
    parent_task_id = fields.Many2one('project.task', string="Activity", index=True)
    task_id = fields.Many2one('project.task', string="Task", index=True)
    time_spent = fields.Float(string="Time Spent", default=0.0)
    # project_data_id = fields.Many2one('project.project', 'Project', domain=[('allow_timesheets', '=', True)],index=True)
    # is_project_activity = fields.Boolean("Project Work ?",compute="_compute_if_project_activity")
    date_of = fields.Date(string="Date",default=date.today())
    pm_approved_ids = fields.Many2many('hr.employee','approve_pm_rel','cr_approver_id','emp_id',string="Pm approved")
    is_pm = fields.Boolean(string="Is PM?", default=False, compute='_check_manager')
    inprogress_log_ids = fields.One2many('activity_inprogress_log','cr_sr_inprogress_id',string="Inprogress Log")
    # cr_in_progress_by = fields.Many2one('hr.employee', 'In Progress By')
    # in_progress_comment = fields.Text('In Progress Comment')
    # cr_in_progress_on = fields.Datetime('In Progress')

    is_testing_lead = fields.Boolean(string="Is Testing Lead?",store=True)

    @api.constrains('description')
    def _check_description_length(self):
        for record in self:
            if record.description and len(record.description) > 250:
                raise ValidationError("Description must be under 250 characters.")
    @api.depends('activity')
    def _check_estimate_time_activity(self):
        for record in self:
            if record.cr_type == 'CR':
                record.estimate_activity_hour = record.activity.estimate_time
            elif record.cr_type == 'Service':
                record_sub_activity = self.env['kw_cr_sub_activity_master'].sudo().search([('cr_activity_id','=',record.activity.id),('id','=',record.sub_activity.id)])
                record.estimate_activity_hour = record_sub_activity.estimate_time_sr
            
    @api.onchange('project_id')
    def _changes_in_environment(self):
        self.environment_id = False
        environment_data = self.env['kw_environment_sequence'].sudo().search(
            [('project_id', '=', self.project_id.id)]).mapped('environment_id').ids
        return {'domain': {'environment_id': [('id', 'in', environment_data)], }}

    @api.onchange('activity')
    def _onchange_activity(self):
        if self.activity:
            self.sub_activity = False
            return {'domain': {'sub_activity': [('cr_activity_id', '=', self.activity.id)]}}

    @api.depends('project_id','stage')
    def _check_pending_at(self):
        for record in self:
            # project_env = record.project_id

            project_env_records = self.env['kw_project_environment_management'].sudo().search([('project_id', '=', record.project_id.id)])
            pending = []
            pending_at_data = self.env['kw_project_environment_management'].sudo().search([('project_id', '=', record.project_id.id)])
            if record.stage == 'Uploaded':
                record.pending_at = [(5, 0, 0)] 
            elif (record.environment_id.is_approval_required == True
                  and record.stage in ['Applied']
                  and record.cr_type == 'CR'
                  and record.project_id.emp_id.id == record.cr_raised_by.id and record.is_pm_approval_required == False):
                if pending_at_data.server_admin :
                    record.pending_at = [(4, rec) for rec in pending_at_data.server_admin.ids]
                else:
                    manager_group = self.env.ref('change_request_management.group_cr_manager').users
                    officer_group = self.env.ref('change_request_management.group_cr_officer').users
                    all_server_admin = manager_group + officer_group
                    record.pending_at = [(4, user.employee_ids.id, False) for user in all_server_admin]
            elif (record.environment_id.is_approval_required == True
                and record.stage in ['Applied']
                and record.cr_type == 'CR'
                and record.is_pm_approval_required == True 
                and record.project_id.emp_id.id != record.cr_raised_by.id):
                pending = []
                for project_env in project_env_records:
                    if project_env.testing_lead_id:
                        pending.extend(project_env.testing_lead_id.ids)
                    else:
                        pending=[project_env.project_manager_id.id,project_env.project_id.sbu_id.representative_id.id]

                record.pending_at = [(6, 0, pending)]

            elif (record.environment_id.is_approval_required == True
                  and record.stage in ['Test Lead Approved']
                  and record.cr_type == 'CR'
                  and record.is_pm_approval_required == True and record.project_id.emp_id.id != record.cr_raised_by.id):

                pending = [record.project_manager_id.id, record.project_id.sbu_id.representative_id.id]

                record.pending_at = [(4, rec) for rec in pending]
            elif record.stage in ['Applied'] and record.cr_type != 'CR':
                if (record.environment_id.is_approval_required == True
                    and record.is_pm_approval_required == True and record.project_id.emp_id.id != record.cr_raised_by.id):
                    pending = [record.project_manager_id.id,record.project_id.sbu_id.representative_id.id]
                    record.pending_at = [(4, rec) for rec in pending]
                elif pending_at_data.server_admin:
                    record.pending_at = [(4, rec.id, False) for rec in pending_at_data.server_admin]
                else:
                    manager_group = self.env.ref('change_request_management.group_cr_manager').users
                    officer_group = self.env.ref('change_request_management.group_cr_officer').users
                    all_server_admin = manager_group + officer_group
                    record.pending_at = [(4, user.employee_ids.id, False) for user in all_server_admin]
            elif record.stage in ['Applied', 'Approve'] and record.cr_type == 'CR':
                if pending_at_data.server_admin:
                    record.pending_at = [(6, 0, pending_at_data.server_admin.ids)]
                else:
                    manager_group = self.env.ref('change_request_management.group_cr_manager').users
                    officer_group = self.env.ref('change_request_management.group_cr_officer').users
                    all_server_admin = manager_group + officer_group
                    record.pending_at = [(4, user.employee_ids.id, False) for user in all_server_admin]

            elif record.stage in ['Applied', 'Approve'] and record.cr_type != 'CR':
                if pending_at_data.server_admin:
                    record.pending_at = [(6, 0, pending_at_data.server_admin.ids)]
                else:
                    manager_group = self.env.ref('change_request_management.group_cr_manager').users
                    officer_group = self.env.ref('change_request_management.group_cr_officer').users
                    all_server_admin = manager_group + officer_group
                    record.pending_at = [(4, user.employee_ids.id, False) for user in all_server_admin]
            else:
                record.pending_at = []

    @api.model
    def check_project_tagged_employees(self):
        tree_view_id = self.env.ref('change_request_management.change_request_management_list').id
        form_view_id = self.env.ref('change_request_management.change_request_management_form').id

        # selected_project_ids = self.env['kw_cr_management'].sudo().search([])

        # emp_data = []

        # for rec in selected_project_ids:
        #     cr_raised_by = rec.cr_raised_by
        #     project_id = rec.project_id
        #     print(cr_raised_by, "------------------------------cr raised by")
        #     print(project_id, "------------------------------project_id")

        tagged_projects = self.env['kw_project_environment_management'].sudo().search([
            ('employee_ids', 'in', [self.env.user.employee_ids.id])
        ]).mapped('project_id')
        project_ids = []
        if tagged_projects:
            project_ids = tagged_projects.ids
            
        # print( "------------------------------tagged_projects", tagged_projects, project_ids)

        # emp_data.extend(tagged_employees.ids)

        action = {
            'type': 'ir.actions.act_window',
            'name': 'Apply CR',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'kw_cr_management',
            'target': 'main',
            'context': {'default_cr_type': 'CR'}
        }

        # if self.env.user.has_group('change_request_management.group_cr_user') \
        #         and not self.env.user.has_group('change_request_management.group_cr_officer') \
        #         and not self.env.user.has_group('change_request_management.group_cr_manager') \
        #         and not self.env.user.has_group('change_request_management.group_cr_mis_user'):
        action['domain'] = [('project_id.id', 'in', project_ids),
                            ('cr_type', '=', 'CR'),
                            '|', ('stage', 'in', ['Applied','Test Lead Approved', 'Request', 'Approve', 'Uploaded']),
                            '&', ('create_uid', '=', self.env.user.id), ('stage', 'in', ['Draft'])]
        # , 'Uploaded'
        # print("action['domain'] >>>> ", action['domain'])
        return action
    
    @api.model
    def check_take_action_project_employees(self):
        tree_view_id = self.env.ref('change_request_management.change_request_take_action_management_list').id
        form_view_id = self.env.ref('change_request_management.change_request_take_action_management_form').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Take Action',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'kw_cr_management',
            'target': 'main',
            "domain":[('cr_type','=','CR'),
            '|',('stage','in',['Request','Hold']),
             '|',
             '&',('stage','in',['Approve','In Progress']),('is_pm_approval_required','=',True),
            '&',('stage','in',['Applied','In Progress']),('is_pm_approval_required','=',False),],
            'context': {'default_cr_type': 'CR','create':False,'edit':False}
        }
        if self.env.user.has_group('change_request_management.group_cr_manager'):
            return action
        elif self.env.user.has_group('change_request_management.group_cr_officer'):
            tagged_projects = self.env['kw_project_environment_management'].sudo().search([
            ('server_admin', 'in', [self.env.user.employee_ids.id])])
            project_ids=tagged_projects.mapped('project_id.id')
            action['domain'] = [('cr_type','=','CR'),
                        '|',('stage','in',['Request','Hold']),
                        '|',
                        '&',('stage','in',['Approve','In Progress']),('is_pm_approval_required','=',True),
                        '&',('stage','in',['Applied','In Progress']),('is_pm_approval_required','=',False),
                        '&',('project_id.id','in',project_ids),('pending_at.id','in',self.env.user.employee_ids.id)]
            return action
            
    @api.model
    def project_tagged_employees_sr(self):
        tree_view_id = self.env.ref('change_request_management.service_request_management_list_view').id
        form_view_id = self.env.ref('change_request_management.service_request_management_form_view').id
         # Get the current user
        user_id = self.env.user.id
        
        # Fetch all the project environment records where the user is the testing lead
        project_env_records = self.env['kw_project_environment_management'].sudo().search([('testing_lead_id.user_id', '=', user_id)])
        
        # Extract the project IDs from these records
        project_ids = project_env_records.mapped('project_id.id')

        tagged_projects = self.env['kw_project_environment_management'].sudo().search([
            ('employee_ids', 'in', [self.env.user.employee_ids.id])
        ]).mapped('project_id')
        project_ids = []
        if tagged_projects:
            project_ids = tagged_projects.ids

        action = {
            'type': 'ir.actions.act_window',
            'name': 'Apply SR',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'kw_cr_management',
            'target': 'main',
            'context': {'default_cr_type': 'Service'}
        }

        action['domain'] = [('project_id.id', 'in', project_ids),
                            ('cr_type', '=', 'Service'),
                            '|', ('stage', 'in', ['Applied', 'Approve','Request', 'Uploaded']),
                            '&', ('create_uid', '=', self.env.user.id), ('stage', 'in', ['Draft'])]
                            
        # , 'Uploaded'
        # print("action['domain'] >>>> ", action['domain'])
        return action
    @api.model
    def test_lead_take_action(self):
        current_user_emp_ids = self.env.user.employee_ids.ids
        
        project_ids = self.env['kw_project_environment_management'].sudo().search([
            ('testing_lead_id', 'in', current_user_emp_ids)
        ]).mapped('project_id.id')
        # print("in test lead   ===========================",project_ids)
        tree_view_id = self.env.ref('change_request_management.change_request_test_lead_take_action_list').id
        form_view_id = self.env.ref('change_request_management.change_request_test_lead_take_action_form').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Take Action',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'kw_cr_management',
            'target': 'main',
            'context': {'default_cr_type': 'CR', 'search_default_state_applied': 1,'create': False, 'edit': False},
            'domain': [ ('cr_type', 'in', ['CR']),
                    ('stage', 'in', ['Applied']),
                    ('is_pm_approval_required', '=', True),
                    ('project_id', 'in', project_ids) 

                    ]
            }
        return action

    @api.model
    def pm_take_action(self):
        tree_view_id = self.env.ref('change_request_management.change_request_pm_take_action_management_list').id
        form_view_id = self.env.ref('change_request_management.change_request_pm_take_action_management_form').id

        # tagged_projects = self.env['kw_project_environment_management'].sudo().search([
        #     ('project_manager_id', '=', self.env.user.employee_ids.id)
        # ]).mapped('project_id')
        # # print(tagged_projects,"tagged--------------------------------------")
        #
        # project_ids = []
        # if tagged_projects:
        #     project_ids = tagged_projects.ids

        # PM Take action
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Take Action',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'kw_cr_management',
            'target': 'main',
            'context': {'default_cr_type': 'CR', 'search_default_state_test_lead_approved': 1,'search_default_state_applied': 1,'create': False, 'edit': False},
            'domain': [ '|',  
                    ('project_manager_id', '=', self.env.user.employee_ids.id),
                    '&',  
                    ('project_manager_id.sbu_type', '=', 'sbu'), 
                    '|', 
                    ('project_id.sbu_id.representative_id', '=', self.env.user.employee_ids.id),
                    ('project_id.sbu_id.representative_id', '=', False),  
                    ('cr_type', 'in', ['CR','Service']),
                    '&',
                    ('stage', 'in', ['Test Lead Approved', 'Approve', 'Reject','Applied']),
                    ('is_pm_approval_required', '=', True),
                    ('is_testing_lead', '=', False)]
            }
        # print("action['domain'] >>>> ", action['domain'])
        return action

    def _check_manager(self):
        for record in self:
            pm_id = record.project_id.emp_id.id
            record.write({'pm_approved_ids': [(4, pm_id)]})
            user_employee_id = self.env.user.employee_ids.id
            is_user_approved = any(user_employee_id == pm.id for pm in record.pm_approved_ids)
            if is_user_approved:
                record.is_pm = True
                
            if self.env.user.has_group('change_request_management.group_cr_manager'):
                record.is_manager = True
                # print("manager called------------------------")
            if self.env.user.has_group('change_request_management.group_cr_officer'):
                record.is_officer_user = True
                # print("officer called===========================")
            if self.env.user.has_group('change_request_management.group_cr_user'):
                record.is_user = True

    @api.depends('project_id')
    def _compute_project_code(self):
        for rec in self:
            if rec.project_id and rec.project_id.crm_id:
                project_code_record = self.env['crm.lead'].sudo().browse(rec.project_id.crm_id.id)
                if project_code_record.stage_id.code == 'workorder' and project_code_record.code is not False:
                    rec.project_code = project_code_record.code
                elif project_code_record.stage_id.code == 'opportunity' and  project_code_record.code is not False:
                    rec.project_code = project_code_record.code
                else:
                    rec.project_code = rec.project_id.code
            else:
                rec.project_code = False

    # @api.onchange('project_id')
    # def _onchange_project_id(self):
    #     self.module_id = False
    #     if self.project_id:
    #         project = self.project_id.sudo()
    #         module_ids = self.env['kw_project.module'].sudo().search([('project_id', '=', project.id)]).ids
    #         return {'domain': {'module_id': [('id', 'in', module_ids)]}}
    #     else:
    #         return {'domain': {'module_id': []}}

    @api.onchange('cr_type')
    def _cr_type_onchange(self):
        if self.cr_type == 'Service':
            self.activity = False
            self.audit = False
            self.change_impact = False
            # self.priority = False
            self.attachment_name = False
            self.backup_required = False
            sr_data = self.env['kw_cr_activity_master'].sudo().search([('cr_type', '=', 'SR')]).ids
            return {'domain': {'activity': [('id', 'in', sr_data)]}}
        else:
            cr_data = self.env['kw_cr_activity_master'].sudo().search([('cr_type', '=', 'CR')]).ids
            return {'domain': {'activity': [('id', 'in', cr_data)]}}

    def btn_apply(self):
        project_id = self.project_id.id
        environment_id = self.environment_id.id
        cr_type = self.cr_type

        if project_id:
            environment_sequence = self.env['kw_environment_sequence'].sudo().search(
                [('project_id', '=', project_id), ('environment_id', '=', environment_id)], order='id desc', limit=1)
            if environment_sequence and cr_type == 'CR':
                cr_sequence = environment_sequence.cr_sequence + 1
                environment_sequence.write({'cr_sequence': cr_sequence})
                self.reference_no = 'CR-{}'.format(cr_sequence)
            elif environment_sequence and cr_type == 'Service':
                service_sequence = environment_sequence.service_sequence + 1
                environment_sequence.write({'service_sequence': service_sequence})
                self.reference_no = 'SR-{}'.format(service_sequence)
            # mai faired to officer while apply cr
            # template = self.env.ref('change_request_management.kw_cr_management_email_template')
            # users = self.env['res.users'].sudo().search([])
            # officers = users.filtered(lambda user: user.has_group('change_request_management.group_cr_officer'))
            # officer_emails = ",".join(officers.mapped('email'))
            user_name = self.env.user.employee_ids.display_name
            # user_code = self.env.user.employee_ids.emp_code
            # user_data = user_name + '(' + user_code + ')'

            project_env = self.env['kw_project_environment_management'].sudo().search([('project_id', '=', self.project_id.id)])
            # proj_env = self.env['kw_environment_master'].search([('name','=',self.environment_id.name)])
            proj_env = self.env['kw_environment_master'].browse(self.environment_id.id)
            # print("proj_env >>>>>>>>>>>>>> ", proj_env, project_env, self.environment_id.name)

            if self.cr_type == 'CR':
                # print("in cr>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",self.cr_type,self.environment_id.is_approval_required)

                if (self.project_id.emp_id.id
                        and self.project_id.emp_id.id == self.env.user.employee_ids.id
                        and project_env.project_manager_id.id == self.env.user.employee_ids.id
                        and self.environment_id.is_approval_required == True) :
                    # CR applied by PM
                    # if self.project_id.emp_id.id and self.project_id.emp_id.id == self.env.user.employee_ids.id or project_env.project_manager_id.id == self.env.user.employee_ids.id:
                        # print(self.project_id.emp_id.id, self.env.user.employee_ids.id, "project_env.project_manager_id.id == self.env.user.employee_ids.id===================")
                    self.write({
                        'stage': 'Applied',
                        'cr_raised_on': datetime.now(),
                        'cr_raised_by': self.env.user.employee_ids.id,
                        'is_pm_approval_required': False,
                        })
                    template = self.env.ref('change_request_management.kw_cr_management_cancel_email_template')

                    if project_env:
                        # print("project env===================================,",project_env)
                        cc_emp = project_env.mapped('employee_ids.work_email')
                        notifyemp = self.notify_emp_ids.mapped('work_email')
                        pltform = self.platform_id.mapped('name')
                        cc_emp.extend(notifyemp)
                        cc_emails = ",".join(set(cc_emp))
                        if project_env.server_admin:
                            email_to = ','.join(project_env.mapped('server_admin.work_email'))
                            cc_emails += ',' + 'kwcr@csm.tech'
                        else:
                            email_to = 'kwcr@csm.tech'
                        # print(cc_emails,email_to,"=============================================>>>>>>>>.email")
                        user_name = self.env.user.employee_ids.display_name
                        email_from = self.env.user.employee_ids.work_email
                        template.with_context(cc_mail=cc_emails, email_to=email_to, email_from=email_from,
                                              mail_for="Approve", name="CR | Approve Request Email", subject="Approved",
                                              user_name=user_name, pltform=pltform).sudo().send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                    self.env.user.notify_success("CR Applied and Approved Successfully.")
                
                # elif self.project_id.emp_id.id != self.env.user.employee_ids.id:
                elif proj_env.is_approval_required == True:
                    # CR raised by project members for PM approval required
                    # self.is_pm_approval_required = True
                    self.write({
                        'stage': 'Applied',
                        'is_pm_approval_required': True,
                        'cr_raised_on': datetime.now(),
                        'cr_raised_by': self.env.user.employee_ids.id
                    })

                    if project_env.testing_lead_id:
                        self.is_testing_lead = True

                        mail_to_list = project_env.testing_lead_id.mapped('work_email')
                    if not project_env.testing_lead_id and project_env.project_manager_id:
                        self.is_testing_lead = False
                    
                        mail_to_list = project_env.project_manager_id.mapped('work_email')
                        if isinstance(mail_to_list, str):
                            mail_to_list = [mail_to_list]
                        if project_env.project_id.sbu_id.representative_id:
                            representative_email = project_env.project_id.sbu_id.representative_id.work_email
                            if representative_email:  
                                mail_to_list.append(representative_email)
                    cc_emp = project_env.mapped('employee_ids.work_email')
                    notify_emp = self.notify_emp_ids.mapped('work_email') if self.notify_emp_ids else []
                    cc_emp.extend(notify_emp)
                    cc_emails = ",".join(set(cc_emp)) 
                                
                    template = self.env.ref('change_request_management.kw_cr_management_email_template')
                    if template:
                        template.with_context(user_name=user_name, cc_mail=cc_emails, mail_to=",".join(mail_to_list)).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                                
                    self.env.user.notify_info("CR Applied and sent to Testing Lead for approval.")

                    # mail_to_list = project_env.project_manager_id.mapped('work_email')
                    # if self.project_id.sbu_id.representative_id:
                    #     mail_to_list.extend([self.project_id.sbu_id.representative_id.work_email])
                    # email_to = ','.join(list(set(mail_to_list)))

                    # cc_emp = project_env.mapped('employee_ids.work_email')
                    # notify_emp = self.notify_emp_ids.mapped('work_email') if self.notify_emp_ids else []
                    # cc_emp.extend(notify_emp)
                    # cc_emp.extend(project_env.testing_lead_id.mapped('work_email')) if project_env.testing_lead_id else []
                    # cc_emp.extend(project_env.database_admin_id.mapped('work_email')) if project_env.database_admin_id else []
                    # cc_emails = ",".join(set(cc_emp)) 
                    # template = self.env.ref('change_request_management.kw_cr_management_email_template')
                    # if template:
                    #     template.with_context(user_name=user_name, cc_mail=cc_emails, mail_to=email_to).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

                else:
                    # CR raised by project members for non approval required
                    self.write({
                        'stage': 'Applied',
                        'is_pm_approval_required': False,
                        'cr_raised_on': datetime.now(),
                        'cr_raised_by': self.env.user.employee_ids.id
                    })

                    cc_emp = project_env.mapped('employee_ids.work_email')
                    cc_emp.extend(self.notify_emp_ids.mapped('work_email') if self.notify_emp_ids else [])
                    cc_emp.extend(project_env.project_manager_id.mapped('work_email') if project_env.project_manager_id else [])
                    cc_emp.extend(project_env.testing_lead_id.mapped('work_email') if project_env.testing_lead_id else [])
                    cc_emp.extend(project_env.database_admin_id.mapped('work_email') if project_env.database_admin_id else [])
                    cc_emails = ",".join(set(cc_emp))
                    if project_env.server_admin:
                        email_to = ','.join( project_env.server_admin.mapped('work_email'))
                        cc_emails += ',' + 'kwcr@csm.tech'
                    else:
                        email_to = 'kwcr@csm.tech'
                    template = self.env.ref('change_request_management.kw_cr_management_email_template')
                    if template:
                        template.with_context(user_name=user_name, cc_mail=cc_emails, mail_to=email_to).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            

            elif self.cr_type == 'Service':
                if (self.project_id.emp_id.id
                        and self.project_id.emp_id.id == self.env.user.employee_ids.id
                        and project_env.project_manager_id.id == self.env.user.employee_ids.id
                        and self.environment_id.is_approval_required == True) :
                    self.write({
                        'stage': 'Applied',
                        'cr_raised_on': datetime.now(),
                        'cr_raised_by': self.env.user.employee_ids.id,
                        'is_pm_approval_required': False,
                    })
                    template = self.env.ref('change_request_management.kw_cr_management_cancel_email_template')

                    if project_env:
                        # print("project env===================================,",project_env)
                        cc_emp = project_env.mapped('employee_ids.work_email')
                        notifyemp = self.notify_emp_ids.mapped('work_email')
                        pltform = self.platform_id.mapped('name')
                        cc_emp.extend(notifyemp)
                        cc_emails = ",".join(set(cc_emp))
                        if project_env.server_admin:
                            email_to = ','.join(project_env.mapped('server_admin.work_email'))
                            cc_emails += ',' + 'kwcr@csm.tech'
                        else:
                            email_to = 'kwcr@csm.tech'
                        # print(cc_emails,email_to,"=============================================>>>>>>>>.email")
                        user_name = self.env.user.employee_ids.display_name
                        email_from = self.env.user.employee_ids.work_email
                        template.with_context(cc_mail=cc_emails, email_to=email_to, email_from=email_from,
                                              mail_for="Approve", name="CR | Approve Request Email", subject="Approved",
                                              user_name=user_name, pltform=pltform).sudo().send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                    self.env.user.notify_success("CR Applied and Approved Successfully.")
                
                elif proj_env.is_approval_required == True:
                    self.write({
                        'stage': 'Applied',
                        'is_pm_approval_required': True,
                        'cr_raised_on': datetime.now(),
                        'cr_raised_by': self.env.user.employee_ids.id
                    })
                    mail_to_list = project_env.project_manager_id.mapped('work_email')
                    if self.project_id.sbu_id.representative_id:
                        mail_to_list.extend([self.project_id.sbu_id.representative_id.work_email])
                    email_to = ','.join(list(set(mail_to_list)))

                    cc_emp = project_env.mapped('employee_ids.work_email')
                    notify_emp = self.notify_emp_ids.mapped('work_email') if self.notify_emp_ids else []
                    cc_emp.extend(notify_emp)
                    cc_emp.extend(project_env.testing_lead_id.mapped('work_email')) if project_env.testing_lead_id else []
                    cc_emp.extend(project_env.database_admin_id.mapped('work_email')) if project_env.database_admin_id else []
                    cc_emails = ",".join(set(cc_emp)) 
                    cc_emails += ',' + 'kwcr@csm.tech'
                    template = self.env.ref('change_request_management.kw_cr_management_email_template')
                    if template:
                        template.with_context(user_name=user_name, cc_mail=cc_emails, mail_to=email_to).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
               

                # cr_manager_group = self.env.ref('change_request_management.group_cr_manager')
                # # Retrieve users who are in the 'group_cr_manager' group
                # cr_managers = cr_manager_group.users

                # # Retrieve users associated with the project
                # project_users = project_env.mapped('employee_ids.user_id')
                # # Find the intersection of cr_managers and project_users to get managers tagged with the project
                # managers_tagged_with_project = cr_managers & project_users
                # cr_manager_emails = []
                # for manager in managers_tagged_with_project:
                #     if manager.employee_ids:
                #         cr_manager_emails.extend([employee.work_email for employee in manager.employee_ids])
                # cr_manager_email = ",".join(cr_manager_emails)
                # Check the cr_type value
                    # cr_type is 'CR', use the manager's emails

                # cr_type is not 'CR', use the static email address
                # Add the project managers' emails to the cc_emails list
                    # cc_emp = project_env.mapped('employee_ids.work_email')
                    # cc_emp.extend(self.notify_emp_ids.mapped('work_email') if self.notify_emp_ids else [])
                    # cc_emp.extend(project_env.project_manager_id.mapped('work_email') if self.project_manager_id else [])
                    # cc_emails = ",".join(set(cc_emp))

                    # if project_env.server_admin.exists():
                    #     email_to = ','.join( project_env.server_admin.mapped('work_email'))
                    #     cc_emails += ',' + 'kwcr@csm.tech'
                    # else:
                    #     # manager_group = self.env.ref('change_request_management.group_cr_manager').users
                    #     # officer_group = self.env.ref('change_request_management.group_cr_officer').users
                    #     # both_group = manager_group + officer_group
                    #     # user_mails = both_group.mapped('employee_ids.work_email')
                    #     # email_to = ",".join(set(user_mails))
                    #     email_to = 'kwcr@csm.tech'

                    # template = self.env.ref('change_request_management.kw_cr_management_email_template')
                    # template.with_context(user_name=user_name, cc_mail=cc_emails, mail_to=email_to).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

                    # self.env.user.notify_success("SR Applied Successfully.")
                else:
                    self.write({
                        'stage': 'Applied',
                        'is_pm_approval_required': False,
                        'cr_raised_on': datetime.now(),
                        'cr_raised_by': self.env.user.employee_ids.id
                    })
    @api.model            
    def check_take_action_sr_project_employees(self):
        tree_view_id = self.env.ref('change_request_management.service_request_take_action_management_list').id
        form_view_id = self.env.ref('change_request_management.service_request_take_action_management_form').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Take Action',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'kw_cr_management',
            'target': 'main',
            "domain":[('cr_type','=','Service'), ('stage','in',['Applied','In Progress','Request','Hold','Approve'])],
            'context': {'edit': False, 'create': False,}
        }
        if self.env.user.has_group('change_request_management.group_cr_manager'):
            return action
        elif self.env.user.has_group('change_request_management.group_cr_officer'):

            tagged_projects = self.env['kw_project_environment_management'].sudo().search([
            ('server_admin', 'in', [self.env.user.employee_ids.id])])
            project_ids=tagged_projects.mapped('project_id.id')

            action['domain'] = ['&',('cr_type','=','Service'),('pending_at.ids','in',self.env.user.employee_ids.id),
                                 '&',('project_id.id','in',project_ids),('stage','in',['Applied','In Progress','Request','Hold','Approve'])]
            return action

    def btn_upload(self):
        view_id = self.env.ref("change_request_management.cr_uploaded_wizard_view").id
        action = {
            'name': 'Upload',
            'type': 'ir.actions.act_window',
            'res_model': 'cr_uploaded_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'current_id': self.id}
        }
        return action

    def btn_rollback(self):
        view_id = self.env.ref("change_request_management.cr_rollbacked_wizard_view").id
        action = {
            'name': 'Rollback',
            'type': 'ir.actions.act_window',
            'res_model': 'cr_rollbacked_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'current_id':self.id}
        }
        return action

    def btn_cancel(self):
        view_id = self.env.ref("change_request_management.cr_cancel_wizard_view").id
        action = {
            'name': 'Cancel',
            'type': 'ir.actions.act_window',
            'res_model': 'cr_cancel_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'current_id':self.id}
        }
        return action

    def btn_request_rollback(self):
        view_id = self.env.ref("change_request_management.cr_request_rollback_wizard_view").id
        action = {
            'name': 'Request For Rollback',
            'type': 'ir.actions.act_window',
            'res_model': 'cr_request_rollback_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'current_id': self.id}
        }
        return action

    def btn_reject(self):
        view_id = self.env.ref("change_request_management.cr_reject_wizard_view").id
        action = {
            'name': 'Reject',
            'type': 'ir.actions.act_window',
            'res_model': 'cr_cancel_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'current_id': self.id}
        }
        return action

    def btn_hold(self):
        view_id = self.env.ref("change_request_management.cr_hold_wizard_view").id
        action = {
            'name': 'Hold',
            'type': 'ir.actions.act_window',
            'res_model': 'cr_cancel_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'current_id': self.id}
        }
        return action

    def btn_approved(self):
        view_id = self.env.ref("change_request_management.cr_approve_wizard_view").id
        action = {
            'name': 'PM Approve',
            'type': 'ir.actions.act_window',
            'res_model': 'cr_cancel_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'current_id': self.id}
        }
        return action
    def btn_tl_approved(self):
        view_id = self.env.ref("change_request_management.cr_approve_test_lead_wizard_view").id
        action = {
            'name': 'TL Approve',
            'type': 'ir.actions.act_window',
            'res_model': 'cr_cancel_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'current_id': self.id}
        }
        return action

    def btn_pm_reject(self):
        view_id = self.env.ref("change_request_management.cr_pm_reject_wizard_view").id
        action = {
            'name': 'Reject',
            'type': 'ir.actions.act_window',
            'res_model': 'cr_cancel_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'current_id': self.id}
        }
        return action

    def btn_test_lead_reject(self):
        view_id = self.env.ref("change_request_management.cr_test_lead_reject_wizard_view").id
        action = {
            'name': 'Reject',
            'type': 'ir.actions.act_window',
            'res_model': 'cr_cancel_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'current_id': self.id,'button':'TL_Rejected'}
        }
        return action
        
    def btn_in_progress(self):
        view_id = self.env.ref("change_request_management.in_progress_wizard_view").id
        return {
            'name': 'In Progress',
            'type': 'ir.actions.act_window',
            'res_model': 'in_progress_wizard_model',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {
                'default_cr_id': self.id,
            },
        }


class Inprogresslog(models.Model):
    _name = "activity_inprogress_log"


    inprogress_comment = fields.Text(string="Remark")
    inprogress_by_id = fields.Many2one('hr.employee',string="Take action By")
    inprogress_date = fields.Datetime(string="Action taken Datetime")
    cr_sr_inprogress_id = fields.Many2one('kw_cr_management')

class InprogressWizard(models.TransientModel):
    _name = 'in_progress_wizard_model'
    _description = 'Wizard for CR In Progress'

    in_progress_comment = fields.Text(string='Remarks',required=True)

    def action_move_to_in_progress(self):
        cr_id = self.env.context.get('default_cr_id')
        cr_record = self.env['kw_cr_management'].browse(cr_id)
        # 'stage': 'In Progress',cr_sr_inprogress_id
        cr_record.write({'stage': 'In Progress',})
        cr_record.inprogress_log_ids.create({'inprogress_comment':self.in_progress_comment,
            'inprogress_by_id': self.env.user.employee_ids.id,
            'inprogress_date': datetime.now(),
            'cr_sr_inprogress_id': cr_record.id
            }) 
        project_env = self.env['kw_project_environment_management'].sudo().search([('project_id', '=', cr_record.project_id.id)])
        template = self.env.ref('change_request_management.kw_cr_management_cancel_email_template')

        if project_env:
            cc_emp = project_env.mapped('employee_ids.work_email')
            
            notifyemp = cr_record.notify_emp_ids.mapped('work_email')
            pltform = cr_record.platform_id.mapped('name')
            cc_emp.extend(notifyemp)
            cc_emp.extend(['kwcr@csm.tech'])
            cc_emails = ",".join(set(cc_emp))
            user_name = self.env.user.employee_ids.display_name
            email_from = self.env.user.employee_ids.work_email
            email_to = cr_record.create_uid.email if cr_record.create_uid.email else False
            template.with_context(cc_mail=cc_emails, mail_for="in_progress", email_from=email_from,email_to=email_to,
                                    name="CR | In progress Request Email", subject="In-Progress", user_name=user_name,
                                    pltform=pltform).send_mail(cr_record.id,
                                                                notif_layout="kwantify_theme.csm_mail_notification_light")

            self.env.user.notify_success("CR In progress Successfully.")
        
        return {'type': 'ir.actions.act_window_close'}
