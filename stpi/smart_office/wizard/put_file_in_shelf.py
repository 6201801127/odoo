# -*- coding: utf-8 -*-
from datetime import datetime,date
from odoo import fields, models, api
from odoo.exceptions import ValidationError

class PutFileInShelf(models.TransientModel):
    _name = "put_file_in_shelf"
    _description = "Put File in Shelf"

    shelf_type = fields.Selection([('own','Own Shelf'),('department','Departmental Shelf')],string="Shelf Type",default="own",required=True)
    remarks = fields.Text('Remarks',required=True)

    @api.multi
    def put_file_in_shelf(self):
        current_employee = self.env.user.employee_ids[0:1]
        current_user = self.env.user
        if not current_employee.department_id:
            raise ValidationError("Your department information is not available.")
        if not current_user.default_branch_id:
            raise ValidationError("Your branch information is not available.")
        else:
            message = ""
            file_ids = self._context.get('active_ids', [])
            files = self.env['folder.master'].browse(file_ids)
            if self.shelf_type == 'department':
                other_department_files = files.filtered(lambda r:r.department_id not in [current_employee.department_id,current_employee.department_id.parent_id])
                other_branch_files = files.filtered(lambda r:r.branch_id != current_user.default_branch_id)
                if other_department_files or other_branch_files:
                    self.env.user.notify_warning("Some file(s) have not moved.")
                    message = "Some file(s) have not moved."
                #     raise ValidationError("You can't put other department file in shelf.Please select files from your department only.")
                # if other_branch_files:
                #     raise ValidationError("You can't put other branch file in shelf.Please select files from your branch only.")
                # tracker = self.env['file.tracker.report']
                emp_obj = self.env['hr.employee']

                current_user = self.env.user
                current_employee = current_user.employee_ids and current_user.employee_ids[-1] or emp_obj

                for file in files - other_department_files - other_branch_files:
                    # tracker.create({'name': file.folder_name,
                    #                 'number': file.number,
                    #                 'type': 'File',

                    #                 'put_in_shelf_user' : current_user.name,
                    #                 'put_in_shelf_dept': current_employee.department_id.name,
                    #                 'put_in_shelf_job_pos': current_employee.job_id.name,
                    #                 'put_in_shelf_branch': current_user.default_branch_id.name,
                    #                 'put_in_shelf_date': date.today(),

                    #                 'action_taken': 'put_in_shelf',
                    #                 'remarks': self.remarks,
                    #                 'details': 'Put File in shelf'})

                    file.write({"last_owner_id"      : current_user.id,
                                "previous_owner"     : [(4,current_user.id)],
                                "sec_owner"          : [(4,current_user.id)],
                                "is_on_shelf"        : True,
                                "state"              : 'shelf',
                                "current_owner_id"   : False,
                                "action_by_uid"      : self._uid,
                                "action_time"        : datetime.now(),
                                "action_date"        : datetime.now().date(),
                                "file_mode"          : 'inbox'})
                    # start : Add tracking information of file_put_in_shelf to new model 28-December-2021
                    not_forwarded_correspondences = file.file_ids.filtered(lambda r : r not in file.file_ids_m2m)
                    if not_forwarded_correspondences:
                        for corres in not_forwarded_correspondences:
                            file.file_ids_m2m = [[4,corres.id]]

                    self.env['smart_office.file.tracking'].create({
                        'file_id':file.id,
                        'action_stage_id':self.env.ref('smart_office.file_stage_file_put_in_shelf').id,
                        # 'action_to_user_id':rec.employee.user_id.id,
                        'remark':self.remarks,
                    })
                    # end : Add tracking information of file_put_in_shelf to new model 28-December-2021
            else:
                invalid_files = files.filtered(lambda r: r.current_owner_id != self.env.user or r.state != 'in_progress' or r.file_mode == 'own_shelf')
                if invalid_files:
                    self.env.user.notify_warning("Some file(s) have not moved.")
                    message = "Some file(s) have not moved."

                    # raise ValidationError("You can't put files of other in your shelf.Please select files where you are the current owner.")
                # tracker = self.env['file.tracker.report']
                emp_obj = self.env['hr.employee']

                current_user = self.env.user
                current_employee = current_user.employee_ids and current_user.employee_ids[-1] or emp_obj

                for file in files - invalid_files:
                    # tracker.create({
                    #     'name': file.folder_name,
                    #     'number': file.number,
                    #     'type': 'File',

                    #     'put_in_shelf_user' : current_user.name,
                    #     'put_in_shelf_dept': current_employee.department_id.name,
                    #     'put_in_shelf_job_pos': current_employee.job_id.name,
                    #     'put_in_shelf_branch': current_user.default_branch_id.name,
                    #     'put_in_shelf_date': date.today(),

                    #     'action_taken': 'put_in_own_shelf',
                    #     'remarks': self.remarks,
                    #     'details': 'Put File in shelf'
                    # })

                    file.write({'file_mode'          : 'own_shelf',
                                'put_in_own_shelf_date' :datetime.now(),
                                'put_in_own_shelf_time' :datetime.now().date()
                                # "action_by_uid"      : self._uid,
                                # "action_time"        : datetime.now(),
                                # "action_date"        : datetime.now().date()
                                })
                    # start : Add tracking information of file_put_in_own_shelf to new model 28-December-2021
                    # not_forwarded_correspondences = file.file_ids.filtered(lambda r : r not in file.file_ids_m2m)
                    # if not_forwarded_correspondences:
                    #     for corres in not_forwarded_correspondences:
                    #         file.file_ids_m2m = [[4,corres.id]]

                    self.env['smart_office.file.tracking'].create({
                        'file_id':file.id,
                        'action_stage_id':self.env.ref('smart_office.file_stage_file_put_in_own_shelf').id,
                        # 'action_to_user_id':rec.employee.user_id.id,
                        'remark':self.remarks,
                    })
                    # end : Add tracking information of file_put_in_shelf to new model 28-December-2021
            if not message:
                self.env.user.notify_success("File moved to shelf successfully.")