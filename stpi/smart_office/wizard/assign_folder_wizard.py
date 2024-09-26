from datetime import datetime
from odoo import fields, models, api
from odoo.exceptions import ValidationError
# import requests
# import json

class CreateFolder(models.TransientModel):
    _name = 'assign.folder.wizard'
    _description = 'Wizard of Create folder'

    deffolderid = fields.Many2one('muk_dms.file','Correspondence')
    # cooespondence_ids = fields.Many2many('muk_dms.file', string='Correspondence')
    folder_id = fields.Many2one('folder.master', string="File From Inbox",domain=lambda self: [('state','=','in_progress'),('current_owner_id','=', self._uid),('is_on_shelf', '=', False)])
    shelf_file_id = fields.Many2one('folder.master', 'File From Shelf',domain=[('is_on_shelf', '=', True),('state','=','in_progress')])
    description = fields.Text('Description')

    @api.multi
    def confirm_button(self):
        if self.folder_id and self.shelf_file_id:
            raise ValidationError("Please select either File from Inbox or File from Shelf.")
        
        current_user = self.env.user
        current_employee = current_user.employee_ids[0:1]

        if not current_employee.department_id:
                raise ValidationError("Your department information is not available.")

        if not current_employee.branch_id:
            raise ValidationError("Your branch information is not available.")

        # tracker = self.env['file.tracker.report']

        if self.folder_id:
            # normal flow
            self.deffolderid.folder_id = self.folder_id.id

        if self.shelf_file_id:
            # take to inbox then attach correspondence
            
            if self.shelf_file_id.is_on_shelf == False:
                raise ValidationError("Please select files which is in shelf to pull into your inbox.")

            file = self.shelf_file_id
            # start : move to inbox part with tracking 
            # tracker.create({
            #     'name': file.folder_name,
            #     'number': file.number,
            #     'type': 'File',

            #     'pulled_by'     : current_user.name,
            #     'pulled_by_dept': current_employee.department_id.name,
            #     'pulled_by_jobpos': current_employee.job_id.name,
            #     'pulled_by_branch': current_employee.branch_id.name,
            #     'pulled_date': datetime.now().date(),

            #     'action_taken': 'pulled_from_shelf',
            #     'remarks': self.description,
            #     'details': 'Pulled file from shelf'
            # })

            file.write({
                        # "last_owner_id"      : file.current_owner_id.id,
                        "current_owner_id"   : current_user.id,
                        "responsible_user_id": current_user.id,
                        "previous_owner"     : [(4, file.current_owner_id.id),(4,current_user.id)],
                        "sec_owner"          : [(4, file.current_owner_id.id),(4,current_user.id)],
                        "is_on_shelf"        : False,
                        'state'              : 'in_progress',
            })
            # end : move to inbox part with tracking 
            self.deffolderid.folder_id = self.shelf_file_id.id

        # start: added on 15 December 2021
        self.deffolderid.write({'attach_to_file_date': datetime.now().date(),
                                'attach_to_file_time': datetime.now()
                                })
        # start: added on 15 December 2021

        # start : tracking of correspondence attached to file
        # tracker.create({
        #     'name': str(self.deffolderid.name),
        #     'type': 'Correspondence',
        #     'number':self.deffolderid.letter_number,
        #     'assigned_by': str(current_employee.user_id.name),
        #     'assigned_by_dept': str(current_employee.department_id.name),
        #     'assigned_by_jobpos': str(current_employee.job_id.name),
        #     'assigned_by_branch': str(current_employee.branch_id.name),
        #     'assigned_date': datetime.now().date(),
        #     'action_taken': 'assigned_to_file',
        #     'remarks': self.description,
        #     'details': f"Correspondence attached to file {self.folder_id and self.folder_id.folder_name or self.shelf_file_id.folder_name}"
        # })
        # end : tracking of correspondence attached to file
        # start : Add tracking information of correspondence_attached to new model 28-December-2021
        # self.env['smart_office.file.tracking'].create({
        #     'file_id':self.folder_id and self.folder_id.id or self.shelf_file_id.id,
        #     'action_stage_id':self.env.ref('smart_office.file_stage_correspondence_attached').id,
        #     'remark':self.description
        # })
        # end : Add tracking information of correspondence_attached to new model 28-December-2021

        self.env['smart_office.correspondence.tracking'].create({
            'correspondence_id': self._context.get('active_id'),
            'action_stage_id': self.env.ref('smart_office.corres_stage_attach_file_from_create_file').id,
            'remark': self.description
        })

        form_view_id = self.env.ref('smart_office.foldermaster_form_view').id
        tree_view_id = self.env.ref('smart_office.foldermaster_tree_view1').id
        self.env.user.notify_success("Correspondence added to file successfully.")
        return {
            'domain': str([('id', '=', self.folder_id and self.folder_id.id or self.shelf_file_id.id)]),
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'folder.master',
            'view_id': False,
            'views': [(form_view_id, 'form'),(tree_view_id, 'tree')],
            'type': 'ir.actions.act_window',
            'res_id': self.folder_id and self.folder_id.id or self.shelf_file_id.id,
            'target': 'current',
            'nodestroy': True
        }