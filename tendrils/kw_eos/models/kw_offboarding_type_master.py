# -*- coding: utf-8 -*-
from odoo import models, fields, api


class kw_offboarding_type_master(models.Model):
    _name = "kw_offboarding_type_master" 
    _description = "Off-Boarding Type Master"
    _rec_name = 'name'

    name = fields.Char("Name", required=True)
    active = fields.Boolean(string="Active", default=True)
    code = fields.Char("Code", required=True)
    user_type_id = fields.Many2many('kw_user_type_master',string="Type", required=True)
    sequence = fields.Integer(string="Sequence")
    


    _sql_constraints = [('name_unique', 'unique (name)', 'Name must be unique!'),('code_unique', 'unique (code)', 'Code must be unique!')]