from datetime import date, datetime
from odoo import models,fields,api

class CloseFileApprove(models.TransientModel):
    _name = 'smart_office.close.file.approve'
    _description = "Close file Approve wizard"

    folder_id = fields.Many2one("folder.master","File")
    remark = fields.Text("Remark",required=1)

    @api.multi
    def action_submit_file_close_approve(self):
        current_employee = self.env.user.employee_ids and self.env.user.employee_ids[-1] or self.env['hr.employee']
        # self.env['file.tracker.report'].create({
        #     'name': self.folder_id.folder_name,
        #     'number': self.folder_id.number,
        #     'type': 'File',
        #     'closed_by': current_employee.user_id.name,
        #     'closed_by_dept': current_employee.department_id.name,
        #     'closed_by_jobpos': current_employee.job_id.name,
        #     'closed_by_branch': current_employee.branch_id.name,
        #     'close_date': date.today(),
        #     'action_taken': 'file_closed',
        #     'remarks': self.remark,
        #     'details': f"File Close Approved On : {date.today()}"
        # })
        self.folder_id.state = 'closed'
        self.folder_id.closed_by_uid = self.folder_id.reopen_request_user.id
        self.folder_id.closed_date = date.today()
        self.folder_id.closed_time = datetime.now()
        # start : Add tracking information of close_request_approved to new model 28-December-2021
        self.env['smart_office.file.tracking'].create({
            'file_id':self.folder_id.id,
            'action_stage_id':self.env.ref('smart_office.file_stage_close_request_approved').id,
            'remark':self.remark,
        })
        # end : Add tracking information of close_request_approved to new model 28-December-2021
        self.env.user.notify_success("File close request approved successfully.")
        return {
                'name'      : 'Pending For Close',
                'view_mode' : 'tree,form',
                'view_type' : 'form',
                'view_id'   : False,
                'res_model' : 'folder.master',
                'type'      : 'ir.actions.act_window',
                'target'    : 'main',
                'domain'    :[("state",'=',"pending_close")],
                'context'   : {"action_pending_close":True,"filter_department":1,"edit":True,"create":False,"delete":False}
                }

class CloseFileReject(models.TransientModel):
    _name = 'smart_office.close.file.reject'
    _description = "Close file Reject wizard"

    folder_id = fields.Many2one("folder.master","File")
    remark = fields.Text("Remark",required=1)

    @api.multi
    def action_submit_file_close_reject(self):
        current_employee = self.env.user.employee_ids[0:1]
        # self.env['file.tracker.report'].create({
        #     'name': self.folder_id.folder_name,
        #     'number': self.folder_id.number,
        #     'type': 'File',
        #     'rejected_by': current_employee.user_id.name,
        #     'rejected_by_dept': current_employee.department_id.name,
        #     'rejected_by_jobpos': current_employee.job_id.name,
        #     'rejected_by_branch': current_employee.branch_id.name,
        #     'rejected_date': date.today(),
        #     'action_taken': 'file_close_reject',
        #     'remarks': self.remark,
        #     'details': f"File Close Request Rejected on : {date.today()}"
        # })
        self.folder_id.state = 'in_progress'
        # start : Add tracking information of close_request_rejected to new model 28-December-2021
        self.env['smart_office.file.tracking'].create({
            'file_id':self.folder_id.id,
            'action_stage_id':self.env.ref('smart_office.file_stage_close_request_rejected').id,
            'remark':self.remark,
        })
        # end : Add tracking information of close_request_rejected to new model 28-December-2021
        self.env.user.notify_success("File close request rejected successfully.")
        return {
                'name'      : 'Pending For Close',
                'view_mode' : 'tree,form',
                'view_type' : 'form',
                'view_id'   : False,
                'res_model' : 'folder.master',
                'type'      : 'ir.actions.act_window',
                'target'    : 'main',
                'domain'    :[("state",'=',"pending_close")],
                'context'   : {"action_pending_close":True,"filter_department":1,"edit":True,"create":False,"delete":False}
                }