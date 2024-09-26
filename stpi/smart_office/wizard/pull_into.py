# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta

class PullInto(models.TransientModel):
    _name = "pull.into.custom"
    _description = "HR Employee Cheque Action"

    department = fields.Many2one('hr.department', string = "Department")
    jobposition = fields.Many2one('hr.job', string = "Job position")
    job_post_id = fields.Many2one('stpi.job.post', 'Functional Designation')
    employee = fields.Many2one('hr.employee', string='Employee')
    user = fields.Many2one('res.users', related = 'employee.user_id', string='User')
    remarks = fields.Text('Remarks')

    # @api.onchange('department','job_post_id')
    # def _onchange_user(self):
    #     for rec in self:
    #         if rec.department.id and not rec.job_post_id.id:
    #             return {'domain': {'employee': [('department_id', '=', rec.department.id)]}}
    #         elif rec.job_post_id.id and not rec.department.id:
    #             return {'domain': {'employee': [('job_title', '=', rec.job_post_id.id)]}}
    #         elif rec.job_post_id.id and rec.department.id:
    #             return {'domain': {'employee': [('job_title', '=', rec.job_post_id.id),('department_id', '=', rec.department.id)]}}
    #         else:
    #             return {'domain': {'employee': ['|', ('job_title', '=', rec.job_post_id.id),('department_id', '=', rec.department.id)]}}

    @api.onchange('employee')
    def set_related_emp_data(self):
        self.department = self.mapped('employee.department_id')
        self.job_post_id = self.mapped('employee.job_title')
    
    @api.multi
    def pull_intos_action_button(self):
        message = False
        correspondences = self.env['muk_dms.file'].browse(self._context.get('active_ids',[]))
        previous_owner = []
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        invalid_correspondences = correspondences.filtered(lambda r:r.folder_id or self.employee.user_id == r.current_owner_id)
        if invalid_correspondences:
            message = 'Some correspondence(s) have not been transferred.'

        for file in correspondences - invalid_correspondences:
            current_file_employee = self.env['hr.employee'].search([('user_id', '=', file.current_owner_id.id)], limit=1)
            transfer_to_emp = self.env['hr.employee'].search([('user_id', '=', file.current_owner_id.id)], limit=1)
            # self.env['file.tracker.report'].create({
            #     'name': str(file.name),
            #     'number': str(file.letter_number),
            #     'type': 'Correspondence',
            #     'transferred_from': str(current_employee.user_id.name),
            #     'transferred_from_dept': str(current_employee.department_id.name),
            #     'transferred_from_jobpos': str(current_employee.job_id.name),
            #     'transferred_from_branch': str(current_employee.branch_id.name),
            #     'transferred_by': str(current_file_employee.user_id.name),
            #     'transferred_by_dept': str(current_file_employee.department_id.name),
            #     'transferred_by_jobpos': str(current_file_employee.job_id.name),
            #     'transferred_by_branch': str(current_file_employee.branch_id.name),
            #     'transferred_date': datetime.now().date(),
            #     'transferred_to_user': str(self.user.name),
            #     'transferred_to_dept': str(self.department.name),
            #     'transferred_to_job_pos': str(self.job_post_id.name),
            #     'transferred_to_branch': str(self.user.branch_id.name),
            #     'action_taken': 'correspondence_transferred',
            #     'remarks': self.remarks,
            #     'details': 'Correspondence transferred'
            # })
            file.write({'previous_owner_emp': [(4, transfer_to_emp.id)],
                        'last_owner_id': file.current_owner_id.id,
                        'current_owner_id': self.employee.user_id.id,
                        'responsible_user_id': self.employee.user_id.id,
                        'incoming_source': 'transfer',
                        'action_by_uid': self._uid,
                        'action_time': fields.Datetime.now(),
                        'action_date': fields.Date.today()})

            self.env['smart_office.correspondence.tracking'].create({
                'correspondence_id': file.id,
                'action_stage_id': self.env.ref('smart_office.corres_stage_transferred').id,
                'action_to_user_id': self.employee.user_id.id,
                'current_owner_id': file.current_owner_id.id,
                'remark': self.remarks
            })

            self.env['userwise.correspondence.tracking'].create({
                'correspondence_id': file.id,
                'action_stage_id': self.env.ref('smart_office.userwise_corres_transferred_by_someone').id,
                'user_id': self.employee.user_id.id,
                'remark': self.remarks
            })
            self.env['userwise.correspondence.tracking'].create({
                'correspondence_id': file.id,
                'action_stage_id': self.env.ref('smart_office.userwise_corres_transferred_to_someone').id,
                'action_to_user_id': self.employee.user_id.id,
                'remark': self.remarks
            })
        if message:
            self.env.user.notify_info(message)
            # file.sec_owner = []
            # file.previous_owner = [(4,file.last_owner_id.id)]
            # file.previous_owner = [(4,file.current_owner_id.id)]
