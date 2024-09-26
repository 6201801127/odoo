# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json


class kw_sync_grade(models.Model):
    _inherit = 'kwemp_grade'

    # @api.model
    # def create(self, vals):
    #     description = vals['description'] if 'description' in vals else ''
    #     record = super(kw_sync_grade, self).create(vals)
    #     json_data = { "name":vals['name'],"description":description,'record_id':record.id,'kw_id':self.kw_id,'user id':self.env.uid}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_grade","operation":'I'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals or 'description' in vals:
    #         val_name = vals['name'] if 'name' in vals else self.name
    #         val_description = vals['description'] if 'description' in vals else self.description
    #         kw_id=vals['kw_id'] if 'kw_id' in vals else self.kw_id
    #         record_id=self.id
    #         json_data = { "name":val_name,"description":val_description,'record_id':record_id,'kw_id':self.kw_id,'user id':self.env.uid}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name,"description":self.description,'kw_id':self.kw_id}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_grade, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_grade",'old_data':old_serialized_data,"operation":'U','record_id':record_id})          
    #         return record

    # @api.multi
    # def unlink(self, **vals): 
    #     record_id=self.id
    #     json_data = { "name":self.name,"description":self.description,'record_id':record_id,'kw_id':self.kw_id,'user id':self.env.uid}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     record = super(kw_sync_grade, self).unlink()
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_grade","operation":'D','record_id':record_id})
    # return record
