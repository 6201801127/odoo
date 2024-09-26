import re
from datetime import date, datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError

class kw_lv_sub_category_master(models.Model):
    _name = 'kw_lv_sub_category_master'
    _description = 'Local Visit Category'
    _rec_name = "sub_category_name"

    category_type = fields.Many2one('kw_lv_category_master',ondelete='restrict')
    sub_category_name = fields.Char(string='Sub Category Name', required=True)
    remark =  fields.Text(string='Remark')

    @api.model
    def create(self, values):
        result = super(kw_lv_sub_category_master, self).create(values)
        self.env.user.notify_success("Local visit sub category master created successfully.")
        return result
    
    @api.multi
    def write(self, values):
        result = super(kw_lv_sub_category_master, self).write(values)
        self.env.user.notify_success("Local visit sub category master updated successfully.")
        return result

    @api.constrains('sub_category_name')
    def check_sub_category_name(self):
        record = self.env['kw_lv_sub_category_master'].search([]) - self
        for info in record:
            if info.category_type.id == self.category_type.id and info.sub_category_name.lower() == self.sub_category_name.lower():
                raise ValidationError(
                    f'Exists! Already a same sub category name exist for category {self.category_type.category_name}.')
