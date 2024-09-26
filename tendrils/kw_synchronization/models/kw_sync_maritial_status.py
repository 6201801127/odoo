from odoo import models, fields, api
import json


class kw_sync_maritial(models.Model):
    _inherit = 'kwemp_maritial_master'

    # @api.model
    # def create(self, vals):         
    #     record = super(kw_sync_maritial, self).create(vals)
    #     json_data = { "name":vals['name'],'code':vals['code']}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_maritial_master","query":'Inserted new row'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals or 'code' in vals :
    #         val_name = vals['name'] if 'name' in vals else self.name
    #         val_code_ids = vals['code'] if 'code' in vals else self.code
    #         json_data = { "name":val_name,'code':val_code_ids}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name,"code":self.code}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_maritial, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_maritial_master",'old_data':old_serialized_data,"query":'Updated existing record'})            
    #     return record

    # @api.multi
    # def unlink(self,**vals):
    #     json_data = {"name":self.name,"code":self.code}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     record = super(kw_sync_maritial, self).unlink()
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_maritial_master","query":'Row Deleted'})
    #     return record
