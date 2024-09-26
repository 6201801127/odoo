# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime

class SendBackFile(models.TransientModel):
    _name = "send.back.file.custom"
    _description = "File(s) send back."

    mis_sent = fields.Boolean('Mistakenly Sent?')
    remarks = fields.Text('Remarks')

    @api.multi
    def action_send_back_files(self):
        files = self.env['folder.master'].browse(self._context.get('active_ids', []))
        previous_owner = []

        if self.mis_sent:
            details = 'File sent mistakenly'
        else:
            details = 'File sending back'
        
        message = False
        invalid_files = files.filtered(lambda r:r.current_owner_id != self.env.user or r.state != 'in_progress' or r.incoming_source != 'forward')
        if invalid_files:
            message = 'Some file(s) have not been sent back.'

        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for file in files - invalid_files:
            current_file_employee = self.env['hr.employee'].search([('user_id', '=', file.current_owner_id.id)], limit=1)
            previous_file_employee = self.env['hr.employee'].search([('user_id', '=', file.last_owner_id.id)], limit=1)
            # self.env['file.tracker.report'].create({
            #     'name': str(file.folder_name),
            #     'number': str(file.number),
            #     'type': 'File',
            #     'send_bank_from': str(current_file_employee.user_id.name),
            #     'send_bank_from_dept': str(current_file_employee.department_id.name),
            #     'send_bank_from_jobpos': str(current_file_employee.job_id.name),
            #     'send_bank_from_branch': str(current_file_employee.branch_id.name),
            #     'send_bank_date': datetime.now().date(),
            #     'send_bank_to_user': str(previous_file_employee.user_id.name),
            #     'send_bank_to_dept': str(previous_file_employee.department_id.name),
            #     'send_bank_to_job_pos': str(previous_file_employee.job_id.name),
            #     'send_bank_to_branch': str(previous_file_employee.branch_id.name),
            #     'action_taken': 'file_send_bank',
            #     'remarks': self.remarks,
            #     'details': details
            # })
            # file.last_owner_id, file.current_owner_id = file.current_owner_id.id, file.last_owner_id.id
            notings = file.noting_ids.search([('folder_id','=',file.id)])
            if notings:
                notings.write({'secondary_employee_ids':[[4,previous_file_employee.id]]})
                draft_noting = notings.filtered(lambda r:r.state == 'draft' and r.employee_id == current_employee)
                if draft_noting:
                    draft_noting.write({'state':'submitted','forward_date':datetime.now().date(),'forward_time':datetime.now()})

                comments = self.env['smart_office.comment'].search([('noting_id','in',notings.ids)])
                draft_comment = comments.filtered(lambda r: r.employee_id == current_employee and  r.state=='draft')
                if comments:
                    comments.write({'secondary_employee_ids':[[4,previous_file_employee.id]]})
                if draft_comment:
                    draft_comment.write({'state':'submitted','forward_date':datetime.now().date(),'forward_time':datetime.now()})

                if not draft_noting and not draft_comment:
                    latest_note = notings.filtered(lambda r:r.is_last_sequence == True)[-1:]
                    new_comment = latest_note.comment_ids.create({'noting_id':latest_note.id,'state':'submitted','forward_date':datetime.now().date(),'forward_time':datetime.now()})
                    new_comment.secondary_employee_ids = [[4,previous_file_employee.id]]

            file.write({'file_mode':'inbox',
                        'last_owner_id':file.current_owner_id.id,
                        'current_owner_id':file.last_owner_id.id,
                        'incoming_source':'forward',
                        'action_by_uid':self._uid,
                        'action_time':datetime.now(),
                        'action_date':datetime.now().date(),
                        'file_mode': 'inbox',
                        })
            # start : Add tracking information of file_sent_back to new model 28-December-2021
            self.env['smart_office.file.tracking'].create({
                'file_id':file.id,
                'action_stage_id':self.env.ref('smart_office.file_stage_file_forwarded').id,
                'action_by_user_id':self._uid,
                'action_to_user_id':file.current_owner_id.id,
                'remark':self.remarks,
            })
            # end : Add tracking information of file_sent_back to new model 28-December-2021
        if message:
            self.env.user.notify_info(message)
        elif (files - invalid_files):
            self.env.user.notify_success("File(s) sent back successfully.")