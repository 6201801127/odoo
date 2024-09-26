# -*- coding: utf-8 -*-
from odoo import models, fields #, api,_

class HrEmployee(models.Model):
    _name = 'stpi.job.post'
    _description = 'Job Post Master'

    name = fields.Char('Name')
    description = fields.Text('Description')