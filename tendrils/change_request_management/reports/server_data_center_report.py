"""
This module provides models and tools for generating server data reports in Odoo.

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


class CrServerDataReport(models.Model):
    """
    This class represents server data reports in Odoo.

    Attributes:
        _name (str): The technical name of the model.
    """
    _name = 'cr_server_data_report'
    # _rec_name = 'reference_no'
    _description = 'CR Server Report'
    _auto = False
    
    
    
    server_name = fields.Char(string="Server Name")
    server_type = fields.Selection(string="Server Type", selection=[('Physical', 'Physical'), ('Virtual', 'Virtual')])
    dedicated_shared = fields.Selection(string="Hosting Type", selection=[('Dedicated', 'Dedicated'), ('Shared', 'Shared')])
    location = fields.Many2one('kw_data_center_master', string="Data Center")
    adminstrator_id = fields.Many2one('hr.employee', string="Administrator")
    os_type = fields.Many2one('kw_cr_os_type_master',string="OS Type")
    
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            SELECT   
                ROW_NUMBER() OVER () AS id,
                cr.server_name AS server_name,
                cr.server_type AS server_type,
                cr.dedicated_shared AS dedicated_shared,
                cr.location AS location,
                cr.adminstrator_id AS adminstrator_id,
                cr.os_type AS os_type
            FROM kw_cr_server_configuration cr
          )"""
        self.env.cr.execute(query)