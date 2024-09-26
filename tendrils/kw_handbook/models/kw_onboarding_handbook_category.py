# -*- coding: utf-8 -*-
from odoo import models, fields, api


class kw_onboarding_handbook_category(models.Model):
    _name = "kw_onboarding_handbook_category"
    _description = "A model to manage employee handbook categories"
    _rec_name = "name"

    name = fields.Char(string="Name", required=True)
    # handbook     = fields.One2many('kw_onboarding_handbook','category')

    @api.constrains('name')
    def check_name(self):
        exists_name = self.env['kw_onboarding_handbook_category'].search(
            [('name', '=', self.name), ('id', '!=', self.id)])
        if exists_name:
            raise ValueError("The category name" + '"' + self.name + '"' + " already exists.")

    @api.model
    def create(self, vals):
        record = super(kw_onboarding_handbook_category, self).create(vals)
        if record:
            self.env.user.notify_success(message='Handbook category created successfully.')
        else:
            self.env.user.notify_danger(message='Handbook category creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kw_onboarding_handbook_category, self).write(vals)
        if res:
            self.env.user.notify_success(message='Handbook category updated successfully.')
        else:
            self.env.user.notify_danger(message='Handbook category updation failed.')
        return res
