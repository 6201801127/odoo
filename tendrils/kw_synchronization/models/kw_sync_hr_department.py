# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json


class kw_sync_hr_department(models.Model):
    _inherit = 'hr.department'

    # @api.model
    # def create(self, vals):
    #     val_parent_id = vals['parent_id'] if 'parent_id' in vals else ''
    #     val_manager_id = vals['manager_id'] if 'manager_id' in vals else ''     
    #     record = super(kw_sync_hr_department, self).create(vals)
    #     json_data = { "name":vals['name'],"parent_id":val_parent_id,"manager_id":val_manager_id,'kw_id':self.kw_id,'id':record.id,'user id':self.env.uid}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"hr.department","query":'Inserted new row'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals or 'parent_id' in vals or 'manager_id' in vals:
    #         val_name = vals['name'] if 'name' in vals else self.name
    #         val_parent_id = vals['parent_id'] if 'parent_id' in vals else self.parent_id.id
    #         val_manager_id = vals['manager_id'] if 'manager_id' in vals else self.manager_id.id            
    #         json_data = { "name":val_name,"parent_id":val_parent_id,"manager_id":val_manager_id,'kw_id':self.kw_id,'id':self.id,'user id':self.env.uid}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name,"parent_id":self.parent_id.id,"manager_id":self.manager_id.id}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_hr_department, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"hr.department",'old_data':old_serialized_data,"query":'Updated existing record'})
    #     return record

    # @api.multi
    # def unlink(self,**vals):
    #     json_data = {"name":self.name,"parent_id":self.parent_id.id,"manager_id":self.manager_id.id,'kw_id':self.kw_id,'id':self.id,'user id':self.env.uid}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     record = super(kw_sync_hr_department, self).unlink()
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"hr.department","query":'Row Deleted'})
    #     return record
