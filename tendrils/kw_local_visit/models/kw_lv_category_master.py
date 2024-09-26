import re
from datetime import date, datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError

class kw_lv_category_master(models.Model):
    _name = 'kw_lv_category_master'
    _description = 'Local Visit Category'
    _rec_name = "category_name"

    category_name = fields.Char(string=' Category Name', required=True)
    office_details = fields.Selection(string='Office In/Out Details',
                                    selection=[('yes', 'Yes'), ('no', 'No')], default='yes')
    visit_details = fields.Selection(string='Visit Details',
                                    selection=[('yes', 'Yes'), ('no', 'No')], default='yes')
    apply_future_date = fields.Selection(string='Future Date Details',
                                    selection=[('yes', 'Yes'), ('no', 'No')], default='yes')
    apply_back_date = fields.Selection(string='Back Date Details',
                                    selection=[('yes', 'Yes'), ('no', 'No')], default='yes')
    is_personal = fields.Selection(string='Is Personal ?',
                                    selection=[('yes', 'Yes'), ('no', 'No')], default='no')
    remark = fields.Text(string='Remarks')
    sequence = fields.Integer('Sequence')

    @api.constrains('category_name')
    def validate_name(self):
        record = self.env['kw_lv_category_master'].search([]) - self
        for info in record:
            if info.category_name.lower() == self.category_name.lower():
                raise ValidationError(f"The local visit category master {self.category_name} already exists.")

    @api.model
    def create(self, values):
        result = super(kw_lv_category_master, self).create(values)
        self.env.user.notify_success("Local visit category master created successfully.")
        return result
    
    @api.multi
    def write(self, values):
        result = super(kw_lv_category_master, self).write(values)
        self.env.user.notify_success("Local visit category master updated successfully.")
        return result