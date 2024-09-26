# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError

class kw_lv_vehicle_master(models.Model):
    _name = 'kw_lv_vehicle_master'
    _description =  "Local visit vehicle details"
    _rec_name = 'vehicle_name'

    location = fields.Many2one('kw_res_branch', string='Location',required=True)
    vehicle_category = fields.Many2one('kw_lv_vehicle_category_master', string='Vehicle Category', required=True)
    vehicle_name = fields.Char(string='Vehicle Name',required=True)
    vehicle_no = fields.Char(string='Vehicle no.')
    driver_name = fields.Char(string='Driver Name')
    driver_mobile = fields.Char(string='Driver Mob No')
    valid_from = fields.Char(string='Valid From.')
    total_valid_km = fields.Char(string='Total Valid K.M.')
    monthly_valid_km = fields.Integer(string='Monthly Valid K.M.')
    remarks = fields.Text(string='Remarks',required=True)

 
    @api.model
    def create(self, values):
        result = super(kw_lv_vehicle_master, self).create(values)
        self.env.user.notify_success("Local visit vehicle master created successfully.")
        return result
    
    @api.multi
    def write(self, values):
        result = super(kw_lv_vehicle_master, self).write(values)
        self.env.user.notify_success("Local visit vehicle master updated successfully.")
        return result