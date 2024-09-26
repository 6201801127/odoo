# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json


class kw_sync_blood_group(models.Model):
    _inherit = 'kwemp_blood_group_master'

    # @api.model
    # def create(self, vals):         
    #     record = super(kw_sync_blood_group, self).create(vals)
    #     json_data = { "name":vals['name']}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_blood_group_master","operation":'I'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals :
    #         json_data = { "name":vals['name']}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_blood_group, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_blood_group_master",'old_data':old_serialized_data,"operation":'U'})            
    #     return record

    # @api.multi
    # def unlink(self, **vals):         
    #     json_data = { "name":self.name}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     record = super(kw_sync_blood_group, self).unlink()
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_blood_group_master","operation":'D'})
    #     return record
