# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json


class kw_sync_hr_jobs(models.Model):
    _inherit = 'hr.job'

    # @api.model
    # def create(self, vals):
    #     val_department_id = vals['department_id'] if 'department_id' in vals else ''
    #     val_description = vals['description'] if 'description' in vals else ''        
    #     val_no_of_recruitment = vals['no_of_recruitment'] if 'no_of_recruitment' in vals else ''     
    #     record = super(kw_sync_hr_jobs, self).create(vals)
    #     json_data = { "name":vals['name'],"department_id":val_department_id,"no_of_recruitment":val_no_of_recruitment,'description':val_description,'record_id':record.id,'kw_id':self.kw_id,'user id':self.env.uid}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"hr.job","query":'Inserted new row'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals or 'department_id' in vals or 'no_of_recruitment' in vals:
    #         val_name = vals['name'] if 'name' in vals else self.name
    #         val_department_id = vals['department_id'] if 'department_id' in vals else self.department_id.id
    #         val_no_of_recruitment = vals['no_of_recruitment'] if 'no_of_recruitment' in vals else self.no_of_recruitment
    #         val_description = vals['description'] if 'description' in vals else ''                                
    #         json_data = { "name":val_name,"department_id":val_department_id,"no_of_recruitment":val_no_of_recruitment,'description':val_description}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name,"department_id":self.department_id.id,"no_of_recruitment":self.no_of_recruitment,'description':val_description,'record_id':self.id,'kw_id':self.kw_id,'user id':self.env.uid}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_hr_jobs, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"hr.job",'old_data':old_serialized_data,"query":'Updated existing record'})
    #         return record

    # @api.multi
    # def unlink(self,**vals):
    #     for deg_rec in self:
    #         json_data = {"name":deg_rec.name,"department_id":deg_rec.department_id.id,"no_of_recruitment":deg_rec.no_of_recruitment,'record_id':deg_rec.id,'kw_id':deg_rec.kw_id,'user id':self.env.uid}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         record = super(kw_sync_hr_jobs, self).unlink()
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"hr.job"})
    #         return record
