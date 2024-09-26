# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime

class BulkTransferFiles(models.TransientModel):
    _name = "pull.into.file.custom"
    _description = "File(s) bulk transfer"

    department = fields.Many2one('hr.department', string = "Department")
    jobposition = fields.Many2one('hr.job', string = "Job position")
    job_post_id = fields.Many2one('stpi.job.post', 'Functional Designation')
    employee = fields.Many2one('hr.employee', string='Employee')
    user = fields.Many2one('res.users', related = 'employee.user_id', string='User')
    remarks = fields.Text('Remarks')

    @api.onchange('employee')
    def set_job_department(self):
        if self.employee:
            self.job_post_id = self.employee.job_title.id
            self.department = self.employee.department_id.id
        else:
            self.job_post_id = False
            self.department = False

    @api.multi
    def action_bulk_transfer_files(self):
        files = self.env['folder.master'].browse(self._context.get('active_ids',[]))
        previous_owner = []
        message = False

        invalid_files = files.filtered(lambda r:r.current_owner_id == self.employee.user_id or r.state != 'in_progress')
        if invalid_files:
            message = 'Some file(s) have not been transferred.'

        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for file in files - invalid_files:
            current_file_employee = self.env['hr.employee'].search([('user_id', '=', file.current_owner_id.id)], limit=1)
            # self.env['file.tracker.report'].create({
            #     'name': str(file.folder_name),
            #     'number': str(file.number),
            #     'type': 'File',
            #     'transferred_from': str(current_employee.user_id.name),
            #     'transferred_from_dept': str(current_employee.department_id.name),
            #     'transferred_from_jobpos': str(current_employee.job_title.name),
            #     'transferred_from_branch': str(current_employee.branch_id.name),
            #     'transferred_by': str(current_file_employee.user_id.name),
            #     'transferred_by_dept': str(current_file_employee.department_id.name),
            #     'transferred_by_jobpos': str(current_file_employee.job_title.name),
            #     'transferred_by_branch': str(current_file_employee.branch_id.name),
            #     'transferred_date': datetime.now().date(),
            #     'transferred_to_user': str(self.user.name),
            #     'transferred_to_dept': str(self.department.name),
            #     'transferred_to_job_pos': str(self.job_post_id.name),
            #     'transferred_to_branch': str(self.user.branch_id.name),
            #     'action_taken': 'file_transferred',
            #     'remarks': self.remarks,
            #     'details': 'File transferred'
            # })
            # start : Add tracking information of transferred_to_another_user to new model 28-December-2021
            self.env['smart_office.file.tracking'].create({
                'file_id':file.id,
                'action_stage_id':self.env.ref('smart_office.file_stage_transferred_to_another_user').id,
                'action_to_user_id':self.employee.user_id.id,
                'previous_owner_user_id':file.current_owner_id.id,
                'remark':self.remarks,
            })
            # end : Add tracking information of transferred_to_another_user to new model 28-December-2021

            notings = file.noting_ids.search([('folder_id','=',file.id)])
            if notings:
                notings.write({'secondary_employee_ids':[[4,self.employee.id]]})
                draft_noting = notings.filtered(lambda r:r.state == 'draft' and r.employee_id == current_file_employee)
                if draft_noting:
                    draft_noting.write({'state':'submitted','forward_date':datetime.now().date(),'forward_time':datetime.now()})

                comments = self.env['smart_office.comment'].search([('noting_id','in',notings.ids)])
                draft_comment = comments.filtered(lambda r: r.employee_id == current_file_employee and  r.state=='draft')
                if comments:
                    comments.write({'secondary_employee_ids':[[4,self.employee.id]]})
                if draft_comment:
                    draft_comment.write({'state':'submitted','forward_date':datetime.now().date(),'forward_time':datetime.now()})

                if not draft_noting and not draft_comment:
                    latest_note = notings.filtered(lambda r:r.is_last_sequence == True)[-1:]
                    new_comment = latest_note.comment_ids.create({'noting_id':latest_note.id,'state':'submitted','forward_date':datetime.now().date(),'forward_time':datetime.now()})
                    new_comment.secondary_employee_ids = [[4,self.employee.id]]

                    new_comment.write({
                        'employee_id':current_file_employee and current_file_employee.id or False,
                        'secondary_employee_ids' : [[6,0,[self.employee.id,current_file_employee.id]]],
                        'job_id' : current_file_employee.job_id and current_file_employee.job_id.id or False,
                        'job_post_id' : current_file_employee.job_title and current_file_employee.job_title.id or False,
                        'branch_id' : current_file_employee.branch_id and current_file_employee.branch_id.id or False,
                        'department_id' : current_file_employee.department_id and current_file_employee.department_id.id or False,
                    })

            file.write({
                'incoming_source':'transfer',
                'action_by_uid':self._uid,
                'action_time':datetime.now(),
                'action_date':datetime.now().date(),
                'file_mode':'inbox',

                'last_owner_id':file.current_owner_id.id,
                'current_owner_id':self.employee.user_id.id,
                'responsible_user_id':self._uid,
                'previous_owner':[(4,file.current_owner_id.id),(4,self.employee.user_id.id)],
                'sec_owner':[(4,file.current_owner_id.id),(4,self.employee.user_id.id)],
            })

            for corres in file.file_ids:
                corres.last_owner_id = corres.current_owner_id.id
                corres.responsible_user_id = self.env.user.id
                corres.current_owner_id = self.employee.user_id.id
                corres.previous_owner_emp = [(4,corres.last_owner_id.employee_ids.ids[0])]

        if message:
            self.env.user.notify_info(message)