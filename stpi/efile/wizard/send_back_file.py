# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta


class PullInto(models.TransientModel):
    _name = "send.back.file.custom"
    _description = "HR Employee Cheque Action"

    mis_sent = fields.Boolean(string='Mis sent?')
    remarks = fields.Text('Remarks')



    @api.multi
    def pull_into_files_action_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        previous_owner = []
        if self.mis_sent == True:
            details = 'File sent mistakenly'
        else:
            details = 'File sending back'
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for file in self.env['folder.master'].browse(active_ids):
            current_file_employee = self.env['hr.employee'].search([('user_id', '=', file.current_owner_id.id)], limit=1)
            previous_file_employee = self.env['hr.employee'].search([('user_id', '=', file.last_owner_id.id)], limit=1)
            self.env['file.tracker.report'].create({
                'name': str(file.folder_name),
                'number': str(file.number),
                'type': 'File',
                'send_bank_from': str(current_file_employee.user_id.name),
                'send_bank_from_dept': str(current_file_employee.department_id.name),
                'send_bank_from_jobpos': str(current_file_employee.job_id.name),
                'send_bank_from_branch': str(current_file_employee.branch_id.name),
                'send_bank_date': datetime.now().date(),
                'send_bank_to_user': str(previous_file_employee.user_id.name),
                'send_bank_to_dept': str(previous_file_employee.department_id.name),
                'send_bank_to_job_pos': str(previous_file_employee.job_id.name),
                'send_bank_to_branch': str(previous_file_employee.branch_id.name),
                'action_taken': 'correspondence_send_bank',
                'remarks': self.remarks,
                'details': details
            })
            file.last_owner_id, file.current_owner_id = file.current_owner_id.id, file.last_owner_id.id







    #     context = dict(self._context or {})
    #     active_ids = context.get('active_ids', []) or []
    #     for employee in self.env['cheque.requests'].browse(active_ids):
    #         if employee.state == 'to_approve':
    #             employee.sudo().button_approved()
    #
    #
    # @api.multi
    # def pull_intos_action_reject_button(self):
    #     context = dict(self._context or {})
    #     active_ids = context.get('active_ids', []) or []
    #     for employee in self.env['cheque.requests'].browse(active_ids):
    #         if employee.state == 'to_approve':
    #             employee.sudo().button_reject()