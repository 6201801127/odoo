# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError

class kw_termination_reason_master(models.Model):
    _name = "kw_termination_reason_master"
    _description = "Termination Master"
    _rec_name = 'name'

    name = fields.Char(string="Reason", required=True)
    active = fields.Boolean(string="Active", default=True)
    sequence = fields.Integer(string="Sequence")


    _sql_constraints = [('name_unique', 'unique (name)', 'Reason must be unique!')]
