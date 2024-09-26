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
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        previous_owner = []
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for file in self.env['muk_dms.file'].browse(active_ids):
            current_file_employee = self.env['hr.employee'].search([('user_id', '=', file.current_owner_id.id)], limit=1)
            transfer_to_emp = self.env['hr.employee'].search([('user_id', '=', file.current_owner_id.id)], limit=1)
            self.env['file.tracker.report'].create({
                'name': str(file.name),
                'number': str(file.letter_number),
                'type': 'Correspondence',
                'pulled_by': str(current_file_employee.user_id.name),
                'pulled_by_dept': str(current_file_employee.department_id.name),
                'pulled_by_jobpos': str(current_file_employee.job_id.name),
                'pulled_by_branch': str(current_file_employee.branch_id.name),
                'pulled_date': datetime.now().date(),
                'pulled_to_user': str(current_employee.user_id.name),
                'pulled_to_dept': str(current_employee.department_id.name),
                'pulled_to_job_pos': str(current_employee.job_id.name),
                'pulled_to_branch': str(current_employee.branch_id.name),
                'action_taken': 'correspondence_pulled',
                'remarks': self.remarks,
                'details': 'Correspondence pulled'
            })
            file.previous_owner_emp = [(4, transfer_to_emp.id)]
            file.last_owner_id = file.current_owner_id.id
            file.current_owner_id = self.env.user.id
            file.responsible_user_id = self.env.user.id
            # file.sec_owner = []
            # file.previous_owner = [(4,file.last_owner_id.id)]
            # file.previous_owner = [(4,file.current_owner_id.id)]
