# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError


class Panelmembermaster(models.Model):
    _name        = "kw_panel_members_master"
    _description = "Panel Members for Interview in  job."
    _rec_name    = "grp_name"

    # #####------------------------Fields----------------------######

    members_name = fields.Many2many('hr.employee',string="Panel Members", required=True, domain=[('user_id','!=',False)])
    grp_name     = fields.Char(string="Group Name")
    active       = fields.Boolean('Active',default=True)
