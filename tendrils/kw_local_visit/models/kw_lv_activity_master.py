# -*- coding: utf-8 -*-

import re
from datetime import date, datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError

class kw_lv_activity_master(models.Model):
    _name = 'kw_lv_activity_master'
    _description = 'Local Visit'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def create(self, values):
        result = super(kw_lv_activity_master, self).create(values)
        self.env.user.notify_success("Local visit activity master created successfully.")
        return result
    
    @api.multi
    def write(self, values):
        result = super(kw_lv_activity_master, self).write(values)
        self.env.user.notify_success("Local visit activity master updated successfully.")
        return result

    @api.constrains('name')
    def check_activity_name(self):
        record = self.env['kw_lv_activity_master'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError('Exists! Already a same activity name exist.')
