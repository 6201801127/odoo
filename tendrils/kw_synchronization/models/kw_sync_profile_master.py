# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json


class kw_sync_language(models.Model):
    _inherit = 'kwemp_language_master'

    # @api.model
    # def create(self, vals):         
    #     record = super(kw_sync_language, self).create(vals)
    #     json_data = { "name":vals['name']}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_language_master","query":'Inserted new row'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals :
    #         json_data = { "name":vals['name']}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_language, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_language_master",'old_data':old_serialized_data,"query":'Updated existing record'})            
    #     return record

    # @api.multi
    # def unlink(self, **vals):         
    #     json_data = { "name":self.name}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     record = super(kw_sync_language, self).unlink()
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_language_master","query":'Row Deleted'})
    #     return record


class kw_sync_course(models.Model):
    _inherit = 'kwmaster_course_name'

    # @api.model
    # def create(self, vals):         
    #     record = super(kw_sync_course, self).create(vals)
    #     json_data = { "name":vals['name'],'course_type':vals['course_type']}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_course_name","query":'Inserted new row'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals or 'course_type' in vals:
    #         val_name = vals['name'] if 'name' in vals else self.name
    #         val_course_type = vals['course_type'] if 'course_type' in vals else self.course_type
    #         json_data = { "name":val_name,'course_type':val_course_type}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name,"course_type":self.course_type}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_course, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_course_name",'old_data':old_serialized_data,"query":'Updated existing record'})            
    #     return record

    # @api.multi
    # def unlink(self, **vals):         
    #     json_data = { "name":self.name,"course_type":self.course_type}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     record = super(kw_sync_course, self).unlink()
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_course_name","query":'Row Deleted'})
    #     return record


class kw_sync_stream(models.Model):
    _inherit = 'kwmaster_stream_name'

    # @api.model
    # def create(self, vals):         
    #     record = super(kw_sync_stream, self).create(vals)
    #     json_data = { "name":vals['name'],'course_id':vals['course_id']}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_stream_name","query":'Inserted new row'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals or 'course_id' in vals :
    #         val_name = vals['name'] if 'name' in vals else self.name
    #         val_course_id = vals['course_id'] if 'course_id' in vals else self.course_id.id
    #         json_data = { "name":val_name,'course_id':val_course_id}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name,"course_id":self.course_id.id}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_stream, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_stream_name",'old_data':old_serialized_data,"query":'Updated existing record'})            
    #     return record

    # @api.multi
    # def unlink(self, **vals):         
    #     json_data = { "name":self.name,"course_id":self.course_id.id}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     record = super(kw_sync_stream, self).unlink()
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_stream_name","query":'Row Deleted'})
    #     return record


class kw_sync_institute(models.Model):
    _inherit = 'kwmaster_institute_name'

    # @api.model
    # def create(self, vals):         
    #     record = super(kw_sync_institute, self).create(vals)
    #     json_data = { "name":vals['name'],'course_ids':vals['course_ids']}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_institute_name","query":'Inserted new row'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals or 'course_ids' in vals :
    #         val_name = vals['name'] if 'name' in vals else self.name
    #         val_course_ids = vals['course_ids'] if 'course_ids' in vals else self.course_ids.id
    #         json_data = { "name":val_name,'course_ids':val_course_ids}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name,"course_ids":self.course_ids.id}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_institute, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_institute_name",'old_data':old_serialized_data,"query":'Updated existing record'})            
    #     return record

    # @api.multi
    # def unlink(self, **vals):         
    #     json_data = { "name":self.name,"course_ids":self.course_ids.id}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     record = super(kw_sync_institute, self).unlink()
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_institute_name","query":'Row Deleted'})
    #     return record


class kw_sync_specialization(models.Model):
    _inherit = 'kwmaster_specializations'

    # @api.model
    # def create(self, vals):         
    #     record = super(kw_sync_specialization, self).create(vals)
    #     json_data = { "name":vals['name'],'stream_id':vals['stream_id']}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_specializations","query":'Inserted new row'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals or 'stream_id' in vals :
    #         val_name = vals['name'] if 'name' in vals else self.name
    #         val_stream_id = vals['stream_id'] if 'stream_id' in vals else self.stream_id.id
    #         json_data = { "name":val_name,'stream_id':val_stream_id}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name,"stream_id":self.stream_id.id}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_specialization, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_specializations",'old_data':old_serialized_data,"query":'Updated existing record'})            
    #     return record

    # @api.multi
    # def unlink(self, **vals):         
    #     json_data = { "name":self.name,"stream_id":self.stream_id.id}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     record = super(kw_sync_specialization, self).unlink()
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_specializations","query":'Row Deleted'})
    #     return record


class kw_sync_role_name(models.Model):
    _inherit = 'kwmaster_role_name'

    # @api.model
    # def create(self, vals):
    #     category_ids = vals['category_ids'] if 'category_ids' in vals else ''        
    #     record = super(kw_sync_role_name, self).create(vals)
    #     json_data = { "name":vals['name'],'category_ids':category_ids}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_role_name","query":'Inserted new row'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals or 'category_ids' in vals :
    #         val_name = vals['name'] if 'name' in vals else self.name
    #         val_category_ids = vals['category_ids'] if 'category_ids' in vals else self.category_ids.id
    #         json_data = { "name":val_name,'category_ids':val_category_ids}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name,"category_ids":self.category_ids.id}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_role_name, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_role_name",'old_data':old_serialized_data,"query":'Updated existing record'})            
    #     return record

    # @api.multi
    # def unlink(self, **vals):
    #     for record in self:
    #         record.category_ids.unlink()         
    #         json_data = { "name":self.name,"category_ids":self.category_ids.id}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         record = super(kw_sync_role_name, self).unlink()
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_role_name","query":'Row Deleted'})
    #     return record


class kw_sync_category_name(models.Model):
    _inherit = 'kwmaster_category_name'

    # @api.model
    # def create(self, vals):
    #     role_ids = vals['role_ids'] if 'role_ids' in vals else ''        
    #     record = super(kw_sync_category_name, self).create(vals)
    #     json_data = { "name":vals['name'],'role_ids':role_ids}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_category_name","query":'Inserted new row'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals or 'role_ids' in vals :
    #         val_name = vals['name'] if 'name' in vals else self.name
    #         val_role_ids = vals['role_ids'] if 'role_ids' in vals else self.role_ids.id
    #         json_data = { "name":val_name,'role_ids':val_role_ids}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name,"role_ids":self.role_ids.id}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_category_name, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_category_name",'old_data':old_serialized_data,"query":'Updated existing record'})            
    #     return record

    # @api.multi
    # def unlink(self, **vals):         
    #     json_data = { "name":self.name,"role_ids":self.role_ids.id}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     record = super(kw_sync_category_name, self).unlink()
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_category_name","query":'Row Deleted'})
    #     return record


class kw_sync_relationship_name(models.Model):
    _inherit = 'kwmaster_relationship_name'

    # @api.model
    # def create(self, vals):        
    #     record = super(kw_sync_relationship_name, self).create(vals)
    #     json_data = { "name":vals['name']}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_relationship_name","query":'Inserted new row'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals:
    #         val_name = vals['name'] if 'name' in vals else self.name
    #         json_data = { "name":val_name}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_relationship_name, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_relationship_name",'old_data':old_serialized_data,"query":'Updated existing record'})            
    #     return record

    # @api.multi
    # def unlink(self, **vals):         
    #     json_data = { "name":self.name}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     record = super(kw_sync_relationship_name, self).unlink()
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwmaster_relationship_name","query":'Row Deleted'})
    #     return record


class kw_sync_employement_type(models.Model):
    _inherit = 'kwemp_employment_type'

    # @api.model
    # def create(self, vals):        
    #     record = super(kw_sync_employement_type, self).create(vals)
    #     json_data = { "name":vals['name'],"code":vals['code']}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_employment_type","query":'Inserted new row'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals or 'code' in vals:
    #         val_name = vals['name'] if 'name' in vals else self.name
    #         val_code = vals['code'] if 'code' in vals else self.code
    #         json_data = { "name":val_name,"code":val_code}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name,"code":self.code}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_employement_type, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_employment_type",'old_data':old_serialized_data,"query":'Updated existing record'})            
    #     return record

    # @api.multi
    # def unlink(self, **vals):         
    #     json_data = { "name":self.name,"code":self.code}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     record = super(kw_sync_employement_type, self).unlink()
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_employment_type","query":'Row Deleted'})
    #     return record


class kw_sync_reference_mode_master(models.Model):
    _inherit = 'kwemp_reference_mode_master'

    # @api.model
    # def create(self, vals):         
    #     record = super(kw_sync_reference_mode_master, self).create(vals)
    #     json_data = { "name":vals['name']}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_reference_mode_master","query":'Inserted new row'})
    #     return record

    # @api.multi
    # def write(self, vals):
    #     if 'name' in vals :
    #         json_data = { "name":vals['name']}
    #         serialized_data = json.dumps(json_data, sort_keys=False)
    #         old_json_data = { "name":self.name}
    #         old_serialized_data = json.dumps(old_json_data, sort_keys=False)
    #         record = super(kw_sync_reference_mode_master, self).write(vals)
    #         new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_reference_mode_master",'old_data':old_serialized_data,"query":'Updated existing record'})            
    #     return record

    # @api.multi
    # def unlink(self, **vals):         
    #     json_data = { "name":self.name}
    #     serialized_data = json.dumps(json_data, sort_keys=False)
    #     record = super(kw_sync_reference_mode_master, self).unlink()
    #     new_data = self.env['kw_synchronization'].create({'new_data':serialized_data,'model_name':"kwemp_reference_mode_master","query":'Row Deleted'})
    #     return record
