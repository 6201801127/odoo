# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError
import pdb

class GroupMaster(models.Model):
    _name = "kw_emp_group_master"
    _description = "Employee Group Master"
    _order = 'id'

    code = fields.Char('Code')
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order of qualification.")
    active = fields.Boolean(string="Active", default=True)
    name = fields.Char('Name')


    _sql_constraints = [('name_unique', 'unique (name)', 'Name must be unique!'),('code_unique', 'unique (code)', 'Code must be unique!')]