# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json


class kw_sync_employee_tag(models.Model):
    _inherit = 'hr.employee.category'

    # @api.model
    # def create(self, vals):         
    #     record = super(kw_sync_employee_tag, self).create(vals)
    #     json_data = { "name":vals['name']}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"hr.employee.catagory","query":'Inserted new row'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals :
    #         json_data = { "name":vals['name']}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_employee_tag, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"hr.employee.catagory",'old_data':old_serialized_data,"query":'Updated existing record'})            
    #     return record

    # @api.multi
    # def unlink(self, **vals):         
    #     json_data = { "name":self.name}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     record = super(kw_sync_employee_tag, self).unlink()
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"hr.employee.catagory","query":'Row Deleted'})
    #     return record
