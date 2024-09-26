# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta

class PullIntoMyInbox(models.TransientModel):
    _name = "pull.into.my.custom"
    _description = "Pull into My Inbox"

    remarks = fields.Text('Remarks')

    @api.multi
    def pull_intos_my_action_button(self):
        
        message = False
        correspondences = self.env['muk_dms.file'].browse(self._context.get('active_ids',[]))

        previous_owner = []
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        invalid_correspondences = correspondences.filtered(lambda r:r.folder_id or self.env.user == r.current_owner_id)

        if invalid_correspondences:
            message = 'Some correspondence(s) have not been transferred.'

        for file in correspondences - invalid_correspondences:
            current_file_employee = self.env['hr.employee'].search([('user_id', '=', file.current_owner_id.id)], limit=1)
            transfer_to_emp = self.env['hr.employee'].search([('user_id', '=', file.current_owner_id.id)], limit=1)
            # self.env['file.tracker.report'].create({
            #     'name': str(file.name),
            #     'number': str(file.letter_number),
            #     'type': 'Correspondence',
            #     'pulled_by': str(current_file_employee.user_id.name),
            #     'pulled_by_dept': str(current_file_employee.department_id.name),
            #     'pulled_by_jobpos': str(current_file_employee.job_id.name),
            #     'pulled_by_branch': str(current_file_employee.branch_id.name),
            #     'pulled_date': datetime.now().date(),
            #     'pulled_to_user': str(current_employee.user_id.name),
            #     'pulled_to_dept': str(current_employee.department_id.name),
            #     'pulled_to_job_pos': str(current_employee.job_id.name),
            #     'pulled_to_branch': str(current_employee.branch_id.name),
            #     'action_taken': 'correspondence_pulled',
            #     'remarks': self.remarks,
            #     'details': 'Correspondence pulled'
            # })
            file.write({'previous_owner_emp': [(4, transfer_to_emp.id)],
                        'last_owner_id': file.current_owner_id.id,
                        'current_owner_id': self.env.user.id,
                        'responsible_user_id': self.env.user.id,
                        'incoming_source': 'pull_inbox',
                        'action_by_uid': self._uid,
                        'action_time': fields.Datetime.now(),
                        'action_date': fields.Date.today()})

            self.env['smart_office.correspondence.tracking'].create({
                'correspondence_id': file.id,
                'action_stage_id': self.env.ref('smart_office.corres_stage_pull_inbox').id,
                'action_to_user_id': self.env.user.id,
                'remark': self.remarks
            })

            self.env['userwise.correspondence.tracking'].create({
                'correspondence_id': file.id,
                'action_stage_id': self.env.ref('smart_office.userwise_corres_pulled_from_someone').id,
                'user_id': self.env.user.id,
                'remark': self.remarks
            })
            self.env['userwise.correspondence.tracking'].create({
                'correspondence_id': file.id,
                'action_stage_id': self.env.ref('smart_office.userwise_corres_pulled_to_someone').id,
                'action_to_user_id': self.env.user.id,
                'remark': self.remarks
            })
        if message:
            self.env.user.notify_info(message)
            # file.sec_owner = []
            # file.previous_owner = [(4,file.last_owner_id.id)]
            # file.previous_owner = [(4,file.current_owner_id.id)]
