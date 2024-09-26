from odoo import fields, models, api, _
from datetime import datetime

class PartFile(models.TransientModel):
    _name = 'smart_office.part.file'
    _description = 'Wizard For Part File Creation'

    remark = fields.Text("Remark",required=True)
    folder_id = fields.Many2one("folder.master","File")

    @api.multi
    def create_part_file(self):
        query = f'select count(*) from folder_master where version = {self.folder_id.id}'
        self._cr.execute(query)
        data = self._cr.fetchall()
        no_of_part_file = data[0][0] + 1
        # no_of_part_file = self.folder_id.sudo().search_count([('version', '=', self.folder_id.id)]) + 1
        
        file = self.folder_id.create({
            'folder_name': f"{self.folder_id.folder_name}(Part {no_of_part_file})",
            'number': f"{self.folder_id.number}/Part {no_of_part_file}",
            'version': self.folder_id.id,
            'basic_version': no_of_part_file,
            'subject': self.folder_id.subject.id,
            'date': self.folder_id.date,
            'department_id':self.folder_id.department_id.id,
            'division_id':self.folder_id.division_id and self.folder_id.division_id.id or False,
            'tags': [[6,0,self.folder_id.tags.ids]],
            'old_file_number': self.folder_id.old_file_number,
            'status': self.folder_id.status,
            'type': self.folder_id.type,
            'description': self.folder_id.description,
            'first_doc_id': self.folder_id.first_doc_id,
            'state':'in_progress',
            'part_created_by':self._uid,
            'part_created_on':datetime.now(),
        })
        
        file.write({
            'incoming_source':'self',
            'action_by_uid':self._uid,
            'action_time':datetime.now(),
            'action_date':datetime.now().date(),
        })
        # start : Add tracking information of pulled_from_others_inbox to new model 28-December-2021
        # self.env['smart_office.file.tracking'].create({
        #     'file_id':self.folder_id.id,
        #     'action_stage_id':self.env.ref('smart_office.file_stage_part_file_created').id,
        #     # 'action_to_user_id':self.env.user.id,
        #     # 'previous_owner_user_id':file.current_owner_id.id,
        #     'remark':self.remark,
        # })
        # end : Add tracking information of pulled_from_others_inbox to new model 28-December-2021
        self.env.user.notify_success("Part file created successfully.")
        print("executing")
        
        return {
                'name'      : 'My Inbox',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref("smart_office.foldermaster_form_view").id,
                'res_model' : 'folder.master',
                'type'      : 'ir.actions.act_window',
                'target'    : 'main',
                'res_id':file.id,
                'domain'    : [('current_owner_id','=', self._uid),('is_on_shelf','=',False),('state','not in',['draft','closed','closed_part'])],
                'context'   : {"create":False,"delete":False},
                }

