from datetime import date, datetime
from odoo import models,fields,api

class ReopenFile(models.TransientModel):
    _name = 'smart_office.reopen.file'
    _description = "Reopen file wizard"

    folder_id = fields.Many2one("folder.master","File")
    remark = fields.Text("Remark",required=1)

    @api.multi
    def action_submit_file_reopen(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        # self.env['file.tracker.report'].create({
        #     'name': self.folder_id.folder_name,
        #     'number': self.folder_id.number,
        #     'type': 'File',
        #     'repoen_by': current_employee.user_id.name,
        #     'repoen_by_dept': current_employee.department_id.name,
        #     'repoen_by_jobpos': current_employee.job_id.name,
        #     'repoen_by_branch': current_employee.branch_id.name,
        #     'repoen_date': date.today(),
        #     'action_taken': 'submit_file_repoen',
        #     'remarks': self.remark,
        #     'details': f"File Repoen Submitted on {date.today()}"
        # })
        self.folder_id.write({'state' : 'pending_reopen',
                              'reopen_request_user' : self._uid,
                              'close_reopen_date' : date.today(),
                              'close_reopen_time' : datetime.now()})
        # self.folder_id.state = 'pending_reopen'
        # self.folder_id.reopen_request_user = self._uid
        # self.folder_id.close_reopen_date = date.today()
        # self.folder_id.close_reopen_time = datetime.now()
        # start : Add tracking information of reopen_request_submitted to new model 28-December-2021
        self.env['smart_office.file.tracking'].create({
            'file_id':self.folder_id.id,
            'action_stage_id':self.env.ref('smart_office.file_stage_reopen_request_submitted').id,
            'remark':self.remark,
        })
        # end : Add tracking information of reopen_request_submitted to new model 28-December-2021
        self.env.user.notify_success("File reopen request submitted successfully.")