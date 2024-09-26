# -*- coding: utf-8 -*-
from datetime import date,datetime
from odoo import fields, models, api
from odoo.exceptions import ValidationError

class PullFileFromShelf(models.TransientModel):
    _name = "pull_file_from_shelf"
    _description = "Pull From Shelf To Inbox"

    remarks = fields.Text('Remarks',required=True)

    @api.multi
    def pull_file_to_inbox(self):
        file_ids = self._context.get('active_ids', [])
        files = self.env['folder.master'].browse(file_ids)
        not_in_shelf_files = files.filtered(lambda r:r.is_on_shelf == False)
        if not_in_shelf_files:
            raise ValidationError("Please select files which is in shelf to pull into your inbox.")
        # tracker = self.env['file.tracker.report']

        current_user = self.env.user
        current_employee = current_user.employee_ids[0:1]

        if not current_employee.department_id:
            raise ValidationError("Your department information is not available.")
        if not current_user.default_branch_id:
            raise ValidationError("Your branch information is not available.")
        else:
            if not current_user.has_group('smart_office.smart_office_pull_manager'):
                other_department_files = files.filtered(lambda r:r.department_id != current_employee.department_id)
                other_branch_files = files.filtered(lambda r:r.branch_id != current_user.default_branch_id)
                if other_department_files:
                    raise ValidationError("You can't pull other department files from shelf. Please select files from your department only.")
                if other_branch_files:
                    raise ValidationError("You can't pull other branch files from shelf. Please select files from your department only.")
            
            for file in files:
                # tracker.create({
                #     'name': file.folder_name,
                #     'number': file.number,
                #     'type': 'File',

                #     'pulled_by'     : current_user.name,
                #     'pulled_by_dept': current_employee.department_id.name,
                #     'pulled_by_jobpos': current_employee.job_id.name,
                #     'pulled_by_branch': current_user.default_branch_id.name,
                #     'pulled_date': date.today(),

                #     # 'pulled_to_user': str(current_employee.user_id.name),
                #     # 'pulled_to_dept': str(current_employee.department_id.name),
                #     # 'pulled_to_job_pos': str(current_employee.job_id.name),
                #     # 'pulled_to_branch': str(current_user.default_branch_id.name),

                #     'action_taken': 'pulled_from_shelf',
                #     'remarks': self.remarks,
                #     'details': 'Pulled file from shelf'
                # })
                file.write({
                            # "last_owner_id"      : file.current_owner_id.id,
                            "current_owner_id"   : current_user.id,
                            "responsible_user_id": current_user.id,
                            "previous_owner"     : [(4, file.last_owner_id.id),(4,current_user.id)],
                            "sec_owner"          : [(4, file.last_owner_id.id),(4,current_user.id)],
                            "is_on_shelf"        : False,
                            'state'              : 'in_progress',
                            'incoming_source'    : 'pull_shelf',
                            'action_by_uid'      :self._uid,
                            'action_time'        :datetime.now(),
                            'action_date'        :datetime.now().date(),
                            'file_mode'          :'inbox'
                })
                for corres in file.file_ids.search([('folder_id','=',file.id)]):
                    # file_count+=1
                    corres.last_owner_id = corres.current_owner_id.id
                    corres.responsible_user_id = self.env.user.id
                    corres.current_owner_id = self.env.user.id
                    # corres.previous_owner = [(4, rec.env.user.id)]
                    corres.previous_owner_emp = [(4,corres.last_owner_id.employee_ids.ids[0])]
                notings = file.noting_ids.search([('folder_id','=',file.id)])
                employee_not_in_notings = notings.filtered(lambda r:current_employee not in r.secondary_employee_ids)
                if employee_not_in_notings:
                    employee_not_in_notings.write({'secondary_employee_ids':[[4,current_employee.id]]})

                comments = self.env['smart_office.comment'].search([('noting_id.folder_id','=',file.id)])
                employee_not_in_comments = comments.filtered(lambda r:current_employee not in r.secondary_employee_ids)
                if employee_not_in_comments:
                    employee_not_in_comments.write({'secondary_employee_ids':[[4,current_employee.id]]})
                # start : Add tracking information of file_pulled_from_shelf to new model 28-December-2021
                self.env['smart_office.file.tracking'].create({
                    'file_id':file.id,
                    'action_stage_id':self.env.ref('smart_office.file_stage_file_pulled_from_shelf').id,
                    # 'action_to_user_id':rec.employee.user_id.id,
                    'remark':self.remarks,
                })
                # end : Add tracking information of file_pulled_from_shelf to new model 28-December-2021
            self.env.user.notify_success("File pulled to inbox successfully.")