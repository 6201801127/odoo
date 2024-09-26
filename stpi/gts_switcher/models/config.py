# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, tools, _

from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class ServerConnection(models.Model):
    _name = 'server.connection'
    _description = 'Server Instance Connection'

    name = fields.Char(string='Name', required=True)
    url = fields.Char(string='Url', required=True)
    active = fields.Boolean('Active', default=True)
    db_name = fields.Char("Database Name")
    user_name = fields.Char("Username")
    password = fields.Char(string='Password', default='')
    instance_type = fields.Selection([('coe', 'COE'),
                                      ('hrms', 'HRMS'),
                                      ], default='coe', required="1", string='Allowed Instance Type')
