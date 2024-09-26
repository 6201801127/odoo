# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError

class kw_lv_vehicle_category_master(models.Model):
    _name = 'kw_lv_vehicle_category_master'
    _description = "Local Visit Vehicle Category Master Details"
    _rec_name = "vehicle_category_name"

    location = fields.Many2one('kw_res_branch',string='Branch',ondelete='restrict')
    vehicle_category_name = fields.Char(string = 'Vehicle Category Name', required=True)
    auto_calculation = fields.Boolean()
    rate_per_km = fields.Float(string = 'Rate Per K.M.')
    currency = fields.Many2one('res.currency', string = 'Currency',ondelete='restrict')
    settlement_required = fields.Boolean()
    expiry_date = fields.Date(string = 'Expiry Date')
    remarks = fields.Text(string = 'Remarks')

    @api.model
    def create(self, values):
        result = super(kw_lv_vehicle_category_master, self).create(values)
        self.env.user.notify_success("Local visit vehicle category master created successfully.")
        return result
    
    @api.multi
    def write(self, values):
        result = super(kw_lv_vehicle_category_master, self).write(values)
        self.env.user.notify_success("Local visit vehicle category master updated successfully.")
        return result

    @api.constrains('vehicle_category_name')
    def check_vehicle_category_name(self):
        record = self.env['kw_lv_vehicle_category_master'].search([]) - self
        for info in record:
            if info.location.id == self.location.id and info.vehicle_category_name.lower() == self.vehicle_category_name.lower():
                raise ValidationError(
                    f'Exist! Already a same vehicle category name exists for city {self.location.city}')
