# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ApprovalConfig(models.Model):
    _name = 'kw_eq_approval_configuration'
    _description = 'Approval configuration'

    approval_type = fields.Selection([('new', 'New'), ('extension', 'Extension'),('change', 'Change'),('revision','Revision')],string="Approval Type")
    level_1 = fields.Selection([('project_manager', 'PM'),('reviewer', 'Reviewer'),('ceo', 'CEO'),('csg_head', 'CSG Head'),('presales', 'Pre Sales'),('cso','Sales'),('cfo','CFO')],string="Authority 1",default="project_manager")
    level_2 = fields.Selection([('project_manager', 'PM'),('reviewer', 'Reviewer'),('ceo', 'CEO'),('csg_head', 'CSG Head'),('presales', 'Pre Sales'),('cso','Sales'),('cfo','CFO')],string="Authority 2")
    level_3 = fields.Selection([('project_manager', 'PM'),('reviewer', 'Reviewer'),('ceo', 'CEO'),('csg_head', 'CSG Head'),('presales', 'Pre Sales'),('cso','Sales'),('cfo','CFO')],string="Authority 3")
    level_4 = fields.Selection([('project_manager', 'PM'),('reviewer', 'Reviewer'),('ceo', 'CEO'),('csg_head', 'CSG Head'),('presales', 'Pre Sales'),('cso','Sales'),('cfo','CFO')],string="Authority 4")
    level_5 = fields.Selection([('project_manager', 'PM'),('reviewer', 'Reviewer'),('ceo', 'CEO'),('csg_head', 'CSG Head'),('presales', 'Pre Sales'),('cso','Sales'),('cfo','CFO')],string="Authority 5")
    
    level_6 = fields.Selection([('project_manager', 'PM'),('reviewer', 'Reviewer'),('ceo', 'CEO'),('csg_head', 'CSG Head'),('presales', 'Pre Sales'),('cso','Sales'),('cfo','CFO')],string="Authority 6")
    # level_6 = fields.Selection([('project_manager', 'PM'), ('sbu_head', 'SBU Head'),('reviewer', 'Reviewer'),('hod', 'HOD'),('ceo', 'CEO'),('csg_head', 'CSG Head'),('presales', 'Pre Sales'),('cso','CSO'),('cfo','CFO')],string="Authority 6")
    effective_date = fields.Date(string="Effective Date")





    






















    # @api.constrains('first_level', 'level_2_id', 'level_3_id', 'level_4_id','oppertunity_name','first_level_user','level_2_id_user','level_3_id_user','level_4_id_user')
    # def _check_selections(self):
    #     for record in self:
    #         duplicate_record = self.search([
    #             ('oppertunity_name', '=', record.oppertunity_name.id),('id', '!=', record.id)
    #         ])
    #         if duplicate_record:
    #             raise ValidationError("Duplicate Oppertunity Name detected!")
    #         if record.first_level == record.level_2_id or record.first_level == record.level_3_id or record.first_level == record.level_4_id:
    #             raise ValidationError("Level 1 must be unique.")
    #         elif record.level_2_id == record.first_level or record.level_2_id == record.level_3_id or record.level_2_id == record.level_4_id:
    #             raise ValidationError("Level 2 must be unique.")
    #         elif record.level_3_id == record.first_level or record.level_3_id == record.level_2_id or record.level_3_id == record.level_4_id:
    #             raise ValidationError("Level 3 must be unique.")
    #         elif record.level_4_id == record.first_level or record.level_4_id == record.level_2_id or record.level_4_id == record.level_3_id:
    #             raise ValidationError("Level 4 must be unique.")
            
            # if record.first_level_user == record.level_2_id_user or record.first_level_user == record.level_3_id_user or record.first_level_user == record.level_4_id_user:
            #     raise ValidationError("Level 1 user must be unique.")
            # elif record.level_2_id_user == record.first_level_user or record.level_2_id_user == record.level_3_id_user or record.level_2_id_user == record.level_4_id_user:
            #     raise ValidationError("Level 2 user must be unique.")
            # elif record.level_3_id_user == record.first_level_user or record.level_3_id_user == record.level_2_id_user or record.level_3_id_user == record.level_4_id_user:
            #     raise ValidationError("Level 3 user must be unique.")
            # elif record.level_4_id_user == record.first_level_user or record.level_4_id_user == record.level_2_id_user or record.level_4_id_user == record.level_3_id_user:
            #     raise ValidationError("Level 4 user must be unique.")
                
        


   
                


                        


