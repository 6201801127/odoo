# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class PullInto(models.TransientModel):
    _name = "send.back.custom"
    _description = "Send back"

    mis_sent = fields.Boolean(string='Mistakenly Sent?')
    remarks = fields.Text('Remarks')

    @api.multi
    def send_banks_action_button(self):
        message = False
        if self.mis_sent == True:
            details = 'Correspondence sent mistakenly'
        else:
            details = 'Correspondence sending back'
        
        correspondences = self.env['muk_dms.file'].browse(self._context.get('active_ids', []))
        invalid_correspondences = correspondences.filtered(lambda r:r.action_by_uid.id == self._uid or r.current_owner_id.id != self._uid)
        if invalid_correspondences:
            message = 'Some correspondence(s) have not been transferred.'
        # current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

        for file in correspondences - invalid_correspondences:
            current_file_employee = self.env['hr.employee'].search([('user_id', '=', file.current_owner_id.id)], limit=1)
            previous_file_employee = self.env['hr.employee'].search([('user_id', '=', file.last_owner_id.id)], limit=1)
            # self.env['file.tracker.report'].create({
            #     'name': str(file.name),
            #     'number': str(file.letter_number),
            #     'type': 'Correspondence',
            #     'send_bank_from': str(current_file_employee.user_id.name),
            #     'send_bank_from_dept': str(current_file_employee.department_id.name),
            #     'send_bank_from_jobpos': str(current_file_employee.job_id.name),
            #     'send_bank_from_branch': str(current_file_employee.branch_id.name),
            #     'send_bank_date': datetime.now().date(),
            #     'send_bank_to_user': str(previous_file_employee.user_id.name),
            #     'send_bank_to_dept': str(previous_file_employee.department_id.name),
            #     'send_bank_to_job_pos': str(previous_file_employee.job_id.name),
            #     'send_bank_to_branch': str(previous_file_employee.branch_id.name),
            #     'action_taken': 'correspondence_send_bank',
            #     'remarks': self.remarks,
            #     'details': details
            # })

            file.write({'responsible_user_id': file.last_owner_id.id,
            'last_owner_id' : file.current_owner_id.id,
            'current_owner_id' : file.last_owner_id.id,
            'incoming_source' : 'forward',
            'action_by_uid':self._uid,
            'action_time' : fields.Datetime.now(),
            'action_date' : fields.Date.today()
            })

            self.env['smart_office.correspondence.tracking'].create({
                'correspondence_id': file.id,
                'action_stage_id': self.env.ref('smart_office.corres_stage_forwarded').id,
                'action_by_user_id': file.last_owner_id.id,
                'action_to_user_id': file.current_owner_id.id,
                'remark': self.remarks
            })

        if message:
            self.env.user.notify_info(message)