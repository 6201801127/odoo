"""
Module: cr_management_reports

This module provides models and tools for managing change request management reports in Odoo.

Imports:
    - models: For defining Odoo models.
    - fields: For defining fields in Odoo models.
    - api: For defining Odoo API methods.
    - tools: For various tools provided by Odoo.
    - date: For working with date objects.
    - datetime: For working with date and time objects.
    - time: For working with time objects.

"""
from odoo import models, fields, api, tools
from datetime import date, datetime, time


class CrManagementReport(models.Model):
    """
    This class represents change request management reports in Odoo.

    Attributes:
        _name (str): The technical name of the model.
        _rec_name (str): The field to be used as the record's display name.
        _description (str): The description of the model.
        _order (str): The default sorting order for records.
    """
    _name = "cr_management_report"
    _rec_name = "reference_no"
    _description = "CR Management Report"
    _order = "id desc"
    _auto = False

    @api.depends('cr_raised_on', 'cr_uploaded_on')
    def _compute_duration(self):
        for record in self:
            if record.cr_raised_on and record.cr_uploaded_on:
                delta = record.cr_uploaded_on - record.cr_raised_on
                if delta.total_seconds() > 3600:  # If delta is more than 1 hour
                    record.duration = delta.total_seconds() / 3600
                else:
                    record.duration = delta.total_seconds() / 6000
            else:
                record.duration = 0.0


    project_id = fields.Many2one('project.project', string='Project Name')
    project_code = fields.Char(string='Project Code', compute='compute_project_code')
    cr_type = fields.Selection(string='Type', selection=[('CR', 'CR'), ('Service', 'Service')])
    module_id = fields.Many2one('kw_project.module', string='Module Name')
    # environment_id = fields.Many2one('kw_environment_master', string='Server')
    environment_name = fields.Char(string='Server')
    url_or_service_name = fields.Text('Website/URL')
    description = fields.Text('Description')
    reference_no = fields.Char(string='Reference')
    # skill_id = fields.Many2one('kw_skill_master', string='Platform')
    date = fields.Date(string='Date')
    date_time = fields.Char(string='Time')
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    uploaded_by = fields.Many2one('hr.employee', string='Uploaded By')
    estimate_activity_hour = fields.Float(string='Estimate Activity Hour')
    duration = fields.Float(string='Duration',compute='_compute_duration')
    roll_back = fields.Char(string='Roll Back')
    cr_raised_on = fields.Datetime('CR Raised Date')
    cr_uploaded_on = fields.Datetime('CR Uploaded')
    cr_rollbacked_on = fields.Datetime('CR Rollbacked')
    cr_cancelled_on = fields.Datetime('Cancelled')
    request_rollbacked_on = fields.Datetime('Request Rollback')
    cr_rejected_on = fields.Datetime('Rejected')
    cr_holded_on = fields.Datetime('Holded')
    state = fields.Char('State')
    platform_id = fields.Many2one('kw_cr_platform_master', 'Platform')
    sr_activity = fields.Many2one('kw_cr_activity_master',string = 'Activity')
    change_impact = fields.Text('Change Impact')
    

    @api.depends('project_id')
    def compute_project_code(self):
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

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
           SELECT
            cr.id as id,   
            cr.project_id AS project_id,
            pj.code AS project_code,
            cr.url_or_service_name AS url_or_service_name,
            cr.module_id AS module_id,
            (SELECT name FROM kw_environment_master WHERE id = cr.environment_id) AS environment_name,
            cr.reference_no AS reference_no,
            cr.description AS description,
            cr.cr_type AS cr_type,
            emp.id AS employee_id,
            cr.change_impact as change_impact,
            
            DATE(cr.create_date) AS date,
            TO_CHAR(cr.create_date, 'HH:MI:SS') AS date_time,
            cr.uploaded_by AS uploaded_by, 
            cr.estimate_activity_hour as estimate_activity_hour,
            null AS duration, 
            null AS roll_back,
            cr.cr_raised_on AS cr_raised_on,
            cr.cr_uploaded_on AS cr_uploaded_on,
            cr.cr_rollbacked_on AS cr_rollbacked_on,
            cr.cr_cancelled_on AS cr_cancelled_on,
            cr.requesr_rollbacked_on AS request_rollbacked_on,
            cr.cr_rejected_on AS cr_rejected_on,
            cr.cr_holded_on AS cr_holded_on,
            cr.stage AS state,
            cr.platform_id as platform_id,
            cr.activity as sr_activity
        FROM kw_cr_management cr
        LEFT JOIN project_project AS pj on pj.id = cr.project_id
        LEFT JOIN res_users AS usr on usr.id = cr.create_uid
        LEFT JOIN hr_employee AS emp on emp.user_id = usr.id
        WHERE cr.stage != 'Draft'
        ORDER BY cr.create_date desc
        )"""
        self.env.cr.execute(query)
        # null::integer AS skill_id,

    @api.model
    def report_project_tagged_employees(self, c_type=''):
        # print('c_type >>>>', c_type)
        tree_view_id = self.env.ref('change_request_management.cr_management_report_tree').id
        search_view_id = self.env.ref('change_request_management.cr_management_report_search_view').id
        form_view_id = self.env.ref('change_request_management.cr_management_report_form').id
        pivot_view_id = self.env.ref('change_request_management.env_project_pivot').id

        if c_type == 'cr':
            cr_type = 'CR'
            page_name = 'CR Report'
        else:
            cr_type = 'Service'
            page_name = 'SR Report'

        action = {
            'type': 'ir.actions.act_window',
            'name': page_name,
            'views': [(tree_view_id, 'tree'), (search_view_id, 'search'), (form_view_id, 'form'),(pivot_view_id,'pivot')],
            'view_mode': 'tree,search,form,pivot',
            'view_type': 'form',
            'res_model': 'cr_management_report',
            'target': 'main',
            'context': {'cr_type': cr_type},
            'domain': [('cr_type', '=', cr_type)],
        }
        env_object = self.env['kw_project_environment_management'].sudo()
        if self.env.user.has_group('change_request_management.group_cr_user') \
                and not self.env.user.has_group('change_request_management.group_cr_officer') \
                and not self.env.user.has_group('change_request_management.group_cr_manager') \
                and not self.env.user.has_group('change_request_management.group_cr_mis_user'):
            tagged_projects = env_object.search([('employee_ids', 'in', [self.env.user.employee_ids.id])]).mapped('project_id')
            project_ids = []
            if tagged_projects:
                project_ids = tagged_projects.ids
            action['domain'] += [('project_id.id', 'in', project_ids)]
        elif self.env.user.has_group('change_request_management.group_cr_test_lead') \
                and not self.env.user.has_group('change_request_management.group_cr_user') \
                and not self.env.user.has_group('change_request_management.group_cr_officer') \
                and not self.env.user.has_group('change_request_management.group_cr_manager') \
                and not self.env.user.has_group('change_request_management.group_cr_mis_user'):
            tagged_projects = env_object.search([('testing_lead_id', 'in', [self.env.user.employee_ids.id])]).mapped('project_id')
            project_ids = []
            if tagged_projects:
                project_ids = tagged_projects.ids
            action['domain'] += [('project_id.id', 'in', project_ids)]
        # elif self.env.user.has_group('change_request_management.group_cr_officer') \
        #         and not self.env.user.has_group('change_request_management.group_cr_manager') \
        #         and not self.env.user.has_group('change_request_management.group_cr_mis_user'):
        #     tagged_projects = env_object.search([('server_admin', 'in', [self.env.user.employee_ids.id])]).mapped('project_id')
        #     project_ids = []
        #     if tagged_projects:
        #         project_ids = tagged_projects.ids
        #     action['domain'] += [('project_id.id', 'in', project_ids)]

        # print(action['domain'], "action['domain']-----------------------------------------")

        return action
