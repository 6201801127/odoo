"""

This module defines the KwProjectServerConfiguration model for managing project server configurations in Odoo.

Imports:
    - date: For working with date objects.
    - models: For defining Odoo models.
    - fields: For defining fields in Odoo models.
    - api: For defining Odoo API methods.

"""
from datetime import date
from odoo import models, fields, api


class KwProjectServerConfiguration(models.Model):
    """
    This class represents project server configurations in Odoo.

    Attributes:
        _name (str): The technical name of the model.
        _description (str): The description of the model.
        _rec_name (str): The field to be used as the record's display name.
        _order (str): The default sorting order for records.
    """
    _name = "kw_cr_server_configuration"
    _description = "Project CR Configuration"
    _rec_name = "server_name"
    _order = "id DESC"

    serial_no = fields.Integer(string='SL No.', force_save=True)
    server_name = fields.Char(string="Server Name")
    server_type = fields.Selection(string="Server Type", selection=[('Physical', 'Physical'), ('Virtual', 'Virtual')])
    dedicated_shared = fields.Selection(string="Hosting Type",
                                        selection=[('Dedicated', 'Dedicated'), ('Shared', 'Shared')])
    date_of_installation = fields.Date(string="Date Of Installation")
    location = fields.Many2one('kw_data_center_master', string="Data Center")
    # project = fields.Many2one('project.project', string="Project")
    visit_for = fields.Selection(string='Visit For', selection=[('opp', 'Opportunity'), ('work_order', 'Work Order')],
                                 default='opp')
    project = fields.Many2one(comodel_name='crm.lead', string='Project')
    # instance = fields.Selection(string="Instance",
    #                             selection=[('Production', 'Production'), ('Testing', 'Testing'), ('Stage', 'Stage')])
    instance = fields.Many2one('kw_environment_master', string='Instance')
    owner = fields.Many2one('kw_cr_owner_master', string="Owner")
    purpose = fields.Text(string="Purpose")
    department_id = fields.Many2one('hr.department', string="Department",
                                    domain=[('dept_type.code', '=', 'department')])
    adminstrator_id = fields.Many2one('hr.employee', string="Administrator")
    make_by = fields.Char(string="Make")
    model_name = fields.Char(string="Model")
    sn_name = fields.Char(string="SN")
    cpu_frequency = fields.Char(string="CPU Frequency")
    cpu_nos = fields.Integer(string="CPU Nos")
    ram_processor = fields.Integer(string="RAM")
    hdd_in = fields.Integer(string="HDD in")
    lan_data = fields.Char(string="LAN")
    date_of_process = fields.Date(string="DOP")
    warranty_num = fields.Char(string="Warranty")
    cost_of = fields.Char(string="Cost")
    fa_code = fields.Char(string="FA Code")
    rack = fields.Char(string="Rack")
    san_volume = fields.Char(string="SAN Volume in GB")
    os_type = fields.Many2one('kw_cr_os_type_master', string="OS Type")
    os_type_in = fields.Many2one('kw_cr_os_master', string="OS")
    database_name = fields.Many2one('kw_cr_database_master', string="Database")
    platform1 = fields.Many2one('kw_cr_platform1_master', string="Application")
    platform2 = fields.Many2one('kw_cr_platform2_master', string="Analytics")
    infra_details = fields.Many2one('kw_infra_details_master', string="Infra Details")
    project_cr_env_id = fields.Many2one('kw_cr_project_configuration')
    # server_id = fields.Many2one('kw_cr_server_configuration',string = 'Server Name')
    # ram_p = fields.Integer(related='server_id.ram_processor')
    # cpu = fields.Char(related='server_id.cpu_nos')
    # dedicate_share =  fields.Selection(string="Hosting Type", selection=[('Dedicated', 'Dedicated'), ('Shared', 'Shared')],related='server_id.dedicated_shared')
    active = fields.Boolean(string="Active", default=True)
    valid_till_date = fields.Date(string='Valid Till')
    remark = fields.Text(string="Remark")
    environment_id = fields.Many2one('kw_environment_master', string='Environment')
    server_create_date = fields.Date(string="Create Date", default=date.today())

    _sql_constraints = [
        ('name_uniq', 'unique(server_name)', 'Name already exist.'),
    ]

    @api.model
    def create(self, vals):
        # existing_sequences = self.env['ir.sequence'].search([('code', '=', 'self.kw_cr_server_configuration')])
        # if existing_sequences:
        #     seq = existing_sequences.next_by_id() or '/'
        #     vals['serial_no'] = seq
        existing_record = self.env['kw_cr_server_configuration'].search([], order='id desc', limit=1)
        if existing_record.exists():
            vals['serial_no'] = int(existing_record.serial_no) + 1
        else:
            vals['serial_no'] = 1

        if vals['os_type_in']:
            os_type_sequence = self.env['kw_cr_os_master'].sudo().search(
                [('id', '=', vals['os_type_in'])], limit=1)
            if os_type_sequence:
                os_sequence = os_type_sequence.server_sequence + 1
                os_type_sequence.write({'server_sequence': os_sequence})

        record = super(KwProjectServerConfiguration, self).create(vals)
        if record:
            self.env.user.notify_success(message='Server created successfully.')
        return record

    @api.onchange('visit_for')
    def _onchange_in_visit_for(self):
        self.project = False
        if self.visit_for == 'opp':
            return {'domain': {'project': [('stage_id.code', '=', 'opportunity')]}}
        elif self.visit_for == 'work_order':
            return {'domain': {'project': [('stage_id.code', '=', 'workorder')]}}

    @api.onchange('os_type')
    def _onchange_os_type_for(self):
        self.os_type_in = False
        os_type_rec = self.env['kw_cr_os_master'].search([('os_type_id', '=', self.os_type.id)]).mapped('id')
        if os_type_rec:
            return {'domain': {'os_type_in': [('id', 'in', os_type_rec)]}}

    def sequence_num_update_server_management(self):
        server_management_data = self.env['kw_cr_server_configuration'].sudo().search([], order='id ASC')
        counter = 1
        for rec in server_management_data:
            # if rec.serial_no:
            #     rec.write({'serial_no': int(rec.serial_no)})
            # elif not rec.serial_no:
            rec.write({'serial_no': counter})
            counter += 1

        # sequence_record = self.env['ir.sequence'].search([('code', '=', 'self.kw_cr_server_configuration')])
        # sequence_record.write({'number_next': counter})


class CrEnviromentServerConfig(models.Model):
    """
    This class represents environment project servers in Odoo.

    Attributes:
        _name (str): The technical name of the model.
        _description (str): The description of the model.
        _order (str): The default sorting order for records.
    """
    _name = "cr_environment_project_server"
    _description = "Environ Project Server"
    _order = "environment_id ASC"

    environment_id = fields.Many2one('kw_environment_master', string='Environment')
    infra_details = fields.Many2one('kw_infra_details_master', string="Infra Details")
    server_id = fields.Many2one('kw_cr_server_configuration', string='Server Name')
    cpu = fields.Integer(related='server_id.cpu_nos')
    remark = fields.Text(string="Remark")
    purpose = fields.Text(string="Purpose")
    ram_p = fields.Integer(related='server_id.ram_processor')
    dedicate_share = fields.Selection(string="Hosting Type",
                                      selection=[('Dedicated', 'Dedicated'), ('Shared', 'Shared')],
                                      related='server_id.dedicated_shared')
    project_env_cr_id = fields.Many2one('kw_cr_project_configuration', string="Environment")
    # sequence = fields.Integer(string='Sequence', readonly=True, compute='compute_sequence')
    # total_ram_p = fields.Integer(string="Total RAM P", compute='_compute_total_ram_p')
    # total_cpu = fields.Integer(string="Total CPU", compute="_compute_total_cpu")
    application_id = fields.Many2one(related='server_id.platform1', string="Application")
    database_id = fields.Many2one(related='server_id.database_name', string="Database")
    datacenter_id = fields.Many2one(related='server_id.location', string="Data Center")

    # @api.depends('ram_p')
    # def _compute_total_ram_p(self):
    #     for rec in self:
    #         records = self.env["cr_environment_project_server"].search([
    #             ('ram_p', '=', rec.ram_p)])
    #     total_ram_p = sum(record.ram_p for record in records)
    #     rec.total_ram_p = total_ram_p

    # @api.depends('cpu')
    # def _compute_total_cpu(self):
    #     # print('yes')
    #     for rec in self:
    #         records = self.env["cr_environment_project_server"].search([
    #             ('cpu', '=', rec.cpu)])
    #     total_cpu = sum(record.cpu for record in records)
    #     rec.total_cpu = total_cpu

    # @api.depends('project_env_cr_id')
    # def compute_sequence(self):
    #     for rec in self:
    #         records = self.env["cr_environment_project_server"].search([
    #             ('project_env_cr_id', '=', rec.project_env_cr_id.id)
    #         ], order='id asc')
    #         for index, record in enumerate(records, start=1):
    #             record.sequence = index
