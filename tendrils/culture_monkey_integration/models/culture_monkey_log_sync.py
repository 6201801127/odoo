"""
Module for Culture Monkey Integration Sync.

This module provides functionality for synchronizing data with Culture Monkey.
"""
from odoo import tools
from odoo import models, fields, api


class CultureMonkeyIntegrationSync(models.Model):
    """
    Model for Culture Monkey Integration Sync.

    This model handles the synchronization of data with Culture Monkey.
    """
    _name = 'culture_monkey_sync_data'
    _description = 'Log'
    _rec_name = 'id'

    data_of_sync = fields.Datetime(string="Date")
    culture_monkey_id = fields.Integer(string="Culture Monkey Id")
    emp_id = fields.Many2one('employee_list_log', string="Employee")
    response_id = fields.Char(string="Response")
    request_id = fields.Char(string="Request")
    sync_required = fields.Boolean(string="Sync Required", default=False)
    ex_employee_sync = fields.Boolean(string="Ex-Employee Sync", default=False)
    type = fields.Integer('Type')

