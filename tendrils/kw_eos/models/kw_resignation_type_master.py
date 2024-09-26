# -*- coding: utf-8 -*-
from odoo import models, fields, api


class kw_resignation_master(models.Model):
    _name = "kw_resignation_master" 
    _description = "Resignation Type Master"
    _rec_name = 'name'

    name = fields.Char("Name")
    code = fields.Char("Code")
    sequence = fields.Integer("Sequence", default=0, help="Gives the sequence order of qualification.")
    active = fields.Boolean(string="Active", default=True)
    is_visible_emp = fields.Boolean(string="Visible to Employee")


    _sql_constraints = [('name_unique', 'unique (name)', 'Name must be unique!'),('code_unique', 'unique (code)', 'Code must be unique!')]