# -*- coding: utf-8 -*-
#start: commit history
# Model added 06 july 2021 (Gouranga kala)
#end: commit history
from odoo import models, fields #, api,_

class GroupMaster(models.Model):
    _name = 'stpi.group.master'
    _description = 'Group Master'

    name = fields.Char('Name',required=True)
    code = fields.Char('Code',required=True)
    description = fields.Text('Description')