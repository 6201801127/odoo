from datetime import date
from odoo import models,fields,api

class CloseFile(models.TransientModel):
    _name = 'smart_office.close.file.cancel'
    _description = "Close file wizard"

    folder_id = fields.Many2one("folder.master","File")
    remark = fields.Text("Remark",required=1)

    @api.multi
    def action_submit_file_close_cancel(self):
        current_employee = self.env.user.employee_ids[0:1]
        # self.env['file.tracker.report'].create({
        #     'name': self.folder_id.folder_name,
        #     'number': self.folder_id.number,
        #     'type': 'File',
        #     'cancelled_by': current_employee.user_id.name,
        #     'cancelled_by_dept': current_employee.department_id.name,
        #     'cancelled_by_jobpos': current_employee.job_id.name,
        #     'cancelled_by_branch': current_employee.branch_id.name,
        #     'cancelled_date': date.today(),
        #     'action_taken': 'cancel_file_close',
        #     'remarks': self.remark,
        #     'details': f"File Close Cancelled on : {date.today()}"
        # })
        self.folder_id.state = 'in_progress'
         # start : Add tracking information of close_request_cancelled to new model 28-December-2021
        self.env['smart_office.file.tracking'].create({
            'file_id':self.folder_id.id,
            'action_stage_id':self.env.ref('smart_office.file_stage_close_request_cancelled').id,
            'remark':self.remark,
        })
        # end : Add tracking information of close_request_cancelled to new model 28-December-2021
        self.env.user.notify_success("File close request cancelled successfully.")