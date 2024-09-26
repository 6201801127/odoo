# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime

class PullIntoMyInbox(models.TransientModel):
    _name = "pull.into.file.my.custom"
    _description = "Pull into my inbox"

    remarks = fields.Text('Remarks')

    @api.multi
    def pull_into_files_my_action_button(self):
        files = self.env['folder.master'].browse(self._context.get('active_ids', []))

        previous_owner = []
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        message = False
        own_shelf_files = files.filtered(lambda r:r.current_owner_id == self.env.user and r.state == 'in_progress' and r.file_mode=='own_shelf')
        
        other_files = files - own_shelf_files
        invalid_files = other_files.filtered(lambda r:r.current_owner_id == self.env.user or r.state != 'in_progress')

        extra_files = other_files - invalid_files
        if invalid_files:
            message = 'Some file(s) have not been pulled.'
        for file in extra_files:
            current_file_employee = self.env['hr.employee'].search([('user_id', '=', file.current_owner_id.id)], limit=1)
            # self.env['file.tracker.report'].create({
            #     'name': str(file.folder_name),
            #     'number': str(file.number),
            #     'type': 'File',
            #     'pulled_by': str(current_file_employee.user_id.name),
            #     'pulled_by_dept': str(current_file_employee.department_id.name),
            #     'pulled_by_jobpos': str(current_file_employee.job_id.name),
            #     'pulled_by_branch': str(current_file_employee.branch_id.name),
            #     'pulled_date': datetime.now().date(),
            #     'pulled_to_user': str(current_employee.user_id.name),
            #     'pulled_to_dept': str(current_employee.department_id.name),
            #     'pulled_to_job_pos': str(current_employee.job_id.name),
            #     'pulled_to_branch': str(current_employee.branch_id.name),
            #     'action_taken': 'file_pulled',
            #     'remarks': self.remarks,
            #     'details': 'File pulled'
            # })
            # start : Add tracking information of pulled_from_others_inbox to new model 28-December-2021
            self.env['smart_office.file.tracking'].create({
                'file_id':file.id,
                'action_stage_id':self.env.ref('smart_office.file_stage_pulled_from_others_inbox').id,
                'action_to_user_id':self.env.user.id,
                'previous_owner_user_id':file.current_owner_id.id,
                'remark':self.remarks,
            })
            # end : Add tracking information of pulled_from_others_inbox to new model 28-December-2021
            # file.last_owner_id = file.current_owner_id.id
            # file.current_owner_id = self.env.user.id
            # file.responsible_user_id = self.env.user.id
            # file.previous_owner = [(4, file.file.current_owner_id.id)]
            # file.previous_owner = [(4, file.current_owner_id.id)]
            # file.sec_owner = [(4, file.file.current_owner_id.id)]
            # file.sec_owner = [(4, file.current_owner_id.id)]
            file.write({
                'last_owner_id': file.current_owner_id.id,
                'current_owner_id': self.env.user.id,
                'responsible_user_id': self.env.user.id,
                # 'previous_owner': [(4, file.file.current_owner_id.id)],
                'previous_owner': [(4, file.current_owner_id.id)],
                'sec_owner': [(4, file.current_owner_id.id)],
                'incoming_source':'pull_inbox',
                'action_by_uid':self._uid,
                'action_time':datetime.now(),
                'action_date':datetime.now().date(),
                'file_mode': 'inbox'
            })
            for corres in file.file_ids.search([('folder_id','=',file.id)]):
                # file_count+=1
                corres.last_owner_id = corres.current_owner_id.id
                corres.responsible_user_id = self.env.user.id
                corres.current_owner_id = self.env.user.id
                # corres.previous_owner = [(4, rec.env.user.id)]
                corres.previous_owner_emp = [(4,corres.last_owner_id.employee_ids.ids[0])]
        # end : extra files loop
        # start : own_shelf files loop
        for file in own_shelf_files:
            current_file_employee = self.env['hr.employee'].search([('user_id', '=', file.current_owner_id.id)], limit=1)
            # self.env['file.tracker.report'].create({
            #     'name': str(file.folder_name),
            #     'number': str(file.number),
            #     'type': 'File',
            #     'pulled_by': str(current_file_employee.user_id.name),
            #     'pulled_by_dept': str(current_file_employee.department_id.name),
            #     'pulled_by_jobpos': str(current_file_employee.job_id.name),
            #     'pulled_by_branch': str(current_file_employee.branch_id.name),
            #     'pulled_date': datetime.now().date(),
            #     'pulled_to_user': str(current_employee.user_id.name),
            #     'pulled_to_dept': str(current_employee.department_id.name),
            #     'pulled_to_job_pos': str(current_employee.job_id.name),
            #     'pulled_to_branch': str(current_employee.branch_id.name),
            #     'action_taken': 'pulled_from_shelf',
            #     'remarks': self.remarks,
            #     'details': 'File pulled'
            # })
            # start : Add tracking information of pulled_from_others_inbox to new model 28-December-2021
            self.env['smart_office.file.tracking'].create({
                'file_id':file.id,
                'action_stage_id':self.env.ref('smart_office.file_stage_file_pulled_from_own_shelf').id,
                # 'action_to_user_id':self.env.user.id,
                # 'previous_owner_user_id':file.current_owner_id.id,
                'remark':self.remarks,
            })
            # end : Add tracking information of pulled_from_others_inbox to new model 28-December-2021
            # file.last_owner_id = file.current_owner_id.id
            # file.current_owner_id = self.env.user.id
            # file.responsible_user_id = self.env.user.id
            # file.previous_owner = [(4, file.last_owner_id.id)]
            # file.previous_owner = [(4, file.current_owner_id.id)]
            # file.sec_owner = [(4, file.last_owner_id.id)]
            # file.sec_owner = [(4, file.current_owner_id.id)]
            file.write({
                'incoming_source':'pull_own_shelf',
                'action_by_uid':self._uid,
                'action_time':datetime.now(),
                'action_date':datetime.now().date(),
                'file_mode': 'inbox'
            })
            # for corres in file.file_ids:
            #     # file_count+=1
            #     corres.last_owner_id = corres.current_owner_id.id
            #     corres.responsible_user_id = self.env.user.id
            #     corres.current_owner_id = self.env.user.id
            #     # corres.previous_owner = [(4, rec.env.user.id)]
            #     corres.previous_owner_emp = [(4,corres.last_owner_id.employee_ids.ids[0])]
        if message:
            self.env.user.notify_info(message)