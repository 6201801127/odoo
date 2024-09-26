# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json


class kw_sync_technical(models.Model):
    _inherit = 'kwemp_technical_category'

    # @api.model
    # def create(self, vals):         
    #     record = super(kw_sync_technical, self).create(vals)
    #     json_data = { "name":vals['name']}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_technical_category","query":'Inserted new row'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals :
    #         json_data = { "name":vals['name']}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_technical, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_technical_category",'old_data':old_serialized_data,"query":'Updated existing record'})            
    #     return record

    # @api.multi
    # def unlink(self, **vals):         
    #     json_data = { "name":self.name}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     record = super(kw_sync_technical, self).unlink()
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_technical_category","query":'Row Deleted'})
    #     return record


class kw_sync_technical_skills(models.Model):
    _inherit = 'kwemp_technical_skill'

    # @api.model
    # def create(self, vals):         
    #     record = super(kw_sync_technical_skills, self).create(vals)
    #     json_data = { "name":vals['name'],'category_id':vals['category_id']}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_technical_skill","query":'Inserted new row'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals or 'category_id' in vals :
    #         val_name = vals['name'] if 'name' in vals else self.name
    #         val_category_id = vals['category_id'] if 'category_id' in vals else self.category_id.id
    #         json_data = { "name":val_name,'category_id':val_category_id}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name,"category_id":self.category_id.id}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_technical_skills, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_technical_skill",'old_data':old_serialized_data,"query":'Updated existing record'})            
    #         return record

    # @api.multi
    # def unlink(self,**vals):
    #     for rec in self:
    #         json_data = {"name":rec.name,"category_id":rec.category_id.id}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         record = super(kw_sync_technical_skills, self).unlink()
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_technical_skill","query":'Row Deleted'})
    #         return record
