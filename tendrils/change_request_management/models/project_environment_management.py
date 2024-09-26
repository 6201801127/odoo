"""
Model: kw_project_environment_management

This module defines the KwProjectEnvironmentManagement class for managing project environments in Odoo.

"""
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class KwProjectEnvironmentManagement(models.Model):
    """
    KwProjectEnvironmentManagement class

    This class represents project environment management in Odoo.

    """
    _name = 'kw_project_environment_management'
    _description = 'Project Environment Management'
    _rec_name = 'project_id'

    def get_server_employee(self):
        """
        Retrieve server employees associated with change request manager and officer groups.

        Returns:
            odoo.models.Model: The server employees associated with manager and officer groups.
        """
        manager_emp = self.env.ref('change_request_management.group_cr_manager').mapped('users.id')
        officer_emp = self.env.ref('change_request_management.group_cr_officer').mapped('users.id')
        user_ids = manager_emp + officer_emp
        emp_manger = self.env['hr.employee'].search([('user_id', 'in', user_ids)])
        return [('id', 'in', emp_manger.ids)]

    project_id = fields.Many2one('project.project', string='Project Name', )
    project_code = fields.Char(string='Project Code', compute='_compute_project_codes')
    # environment_ids = fields.Many2many('kw_environment_master', relation='env_master_rel', column1='env_id', column2='master_id')
    environment_sequence_ids = fields.One2many(comodel_name='kw_environment_sequence',
                                               inverse_name='environment_management_id', string='Environment Sequence')
    employee_ids = fields.Many2many(string='Employee Name', comodel_name='hr.employee', relation='project_env_emp_rel',
                                    column1='project_cr_id', column2='emp_id',
                                    domain="[('user_id', '!=', False), ('employement_type.code', '!=', 'O')]")
    server_admin = fields.Many2many('hr.employee', string="Server Admin", domain=get_server_employee)
    skip_pm_approval = fields.Boolean('Skip PM Approval')
    project_manager_id = fields.Many2one('hr.employee', string='PM')
    testing_lead_id = fields.Many2many('hr.employee','testing_lead_id_employee_rel', string="Test Lead")
    database_admin_id = fields.Many2one('hr.employee', string="Database Admin")
    active = fields.Boolean('Is Active', default=True)

    def _update_test_lead_group(self):
        # print("Updating Test Lead Group================")
        test_lead_group = self.env.ref('change_request_management.group_cr_test_lead')
        # print(test_lead_group, 'test_lead_group==================')
        for employee in self.testing_lead_id:
            # print(self.testing_lead_id, '=======================testing_lead_id')
            if employee.user_id and employee.user_id not in test_lead_group.users:
                test_lead_group.sudo().write({'users': [(4, employee.user_id.id)]})
                


    _sql_constraints = [
        ('project_id_uniq', 'unique(project_id)', 'Project already exist.')]

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            for rec in self.environment_sequence_ids:
                rec.project_id = self.project_id.id
            # self.environment_sequence_ids = [(5,)]
            # self.environment_sequence_ids = [(0, 0, {'project_id': self.project_id.id, })]
            self.project_manager_id = self.project_id.emp_id
            self.employee_ids = [(4,self.project_id.emp_id.id,False)] if self.project_id.emp_id.id not in self.employee_ids.ids else ''
            # print(self.project_manager_id,"--------------------------------")

    @api.depends('project_id')
    def _compute_project_codes(self):
        for rec in self:
            if rec.project_id and rec.project_id.crm_id:
                project_code_record = self.env['crm.lead'].sudo().browse(rec.project_id.crm_id.id)
                if project_code_record.stage_id.code == 'workorder' and project_code_record.code is not False:
                    rec.project_code = project_code_record.code
                elif project_code_record.stage_id.code == 'opportunity' and project_code_record.code is not False:
                    rec.project_code = project_code_record.code
                else:
                    rec.project_code = rec.project_id.code
            else:
                rec.project_code = False

    @api.multi
    def write(self, vals):
        old_test_lead_ids = set(self.testing_lead_id.ids)
        res = super(KwProjectEnvironmentManagement, self).write(vals)

        if 'employee_ids' in vals:
            self.add_to_specific_group()

        new_test_lead_ids = set(self.testing_lead_id.ids)
        removed_test_lead_ids = old_test_lead_ids - new_test_lead_ids

        if removed_test_lead_ids:
            test_lead_group = self.env.ref('change_request_management.group_cr_test_lead')
            for employee_id in removed_test_lead_ids:
                employee = self.env['hr.employee'].browse(employee_id)
                if employee.user_id:
                    # Check if the employee is a testing lead in any other project
                    other_projects_as_lead = self.env['kw_project_environment_management'].search([
                        ('id', '!=', self.id),  # Exclude current record
                        ('testing_lead_id', 'in', [employee_id])
                    ])
                    if not other_projects_as_lead:
                        # Remove the employee from the group only if they are not in other projects
                        if employee.user_id in test_lead_group.users:
                            test_lead_group.sudo().write({'users': [(3, employee.user_id.id)]})
                            
        if res:
            self.env.user.notify_success(message='Project Environment updated successfully.')
        else:
            self.env.user.notify_danger(message='Project Environment updation failed.')
        # Update test lead group
        self._update_test_lead_group()
        return res

    @api.model
    def create(self, vals):
        record = super(KwProjectEnvironmentManagement, self).create(vals)

        if 'employee_ids' in vals:
            record.add_to_specific_group()

        if record:
            self.env.user.notify_success(message='Project Environment created successfully.')
        else:
            self.env.user.notify_danger(message='Project Environment creation failed.')
        # Update test lead group
        record._update_test_lead_group()
        return record

    def add_to_specific_group(self):
        user_group = self.env.ref('change_request_management.group_cr_user')
        user_ids = self.employee_ids.mapped('user_id')
        for user in user_ids:
            if not user.has_group('change_request_management.group_cr_user'):
                user_group.sudo().write({'users': [(4, user.id)]})

    @api.multi
    def pm_tagging_to_project(self):
        # print("pm_tagging_to_project===================")
        project_env_data = self.env['kw_project_environment_management'].sudo().search([])
        for rec in project_env_data:
            if rec.project_id:
                rec.project_manager_id = rec.project_id.emp_id

    @api.multi
    def pm_tagging_in_employee(self):
        employee = []
        project_env_data = self.env['kw_project_environment_management'].sudo().search([])
        for rec in project_env_data:
            if rec.project_manager_id:
                employee.extend(rec.mapped('employee_ids.id'))
                if rec.project_manager_id not in employee:
                    rec.employee_ids = [(4, rec.project_manager_id.id, False)]

    @api.constrains('project_id')
    def _check_same_project(self):
        for rec in self:
            existing_project = self.env['kw_project_environment_management'].sudo().search([
                ('project_id', '=', rec.project_id.id)
            ])
            if existing_project and existing_project != rec:
                raise ValidationError("You can't create with the same project name.")
