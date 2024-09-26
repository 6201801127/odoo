from datetime import date,datetime
from odoo import models,fields,api

class CloseFile(models.TransientModel):
    _name = 'smart_office.close.file'
    _description = "Close file wizard"

    folder_id = fields.Many2one("folder.master","File")
    remark = fields.Text("Remark",required=1)

    @api.multi
    def action_submit_file_close(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        # self.env['file.tracker.report'].create({
        #     'name': self.folder_id.folder_name,
        #     'number': self.folder_id.number,
        #     'type': 'File',
        #     'closed_by': current_employee.user_id.name,
        #     'closed_by_dept': current_employee.department_id.name,
        #     'closed_by_jobpos': current_employee.job_id.name,
        #     'closed_by_branch': current_employee.branch_id.name,
        #     'close_date': date.today(),
        #     'action_taken': 'submit_file_close',
        #     'remarks':self.remark,
        #     'details': f"File Close Submitted on : {date.today()}"
        # })
        self.folder_id.write({'state' : 'pending_close',
                              'reopen_request_user': self._uid,
                              'close_reopen_date': date.today(),
                              'close_reopen_time': datetime.now()})
        # start : Add tracking information of close_request_submitted to new model 28-December-2021
        self.env['smart_office.file.tracking'].create({
            'file_id':self.folder_id.id,
            'action_stage_id':self.env.ref('smart_office.file_stage_close_request_submitted').id,
            'remark':self.remark,
        })
        # end : Add tracking information of close_request_submitted to new model 28-December-2021
        self.env.user.notify_success("File close request submitted successfully.")