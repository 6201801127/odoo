from datetime import date,datetime
from odoo import models,fields,api

class ReopenFileApprove(models.TransientModel):
    _name = 'smart_office.reopen.file.approve'
    _description = "REopen File Approve wizard"

    folder_id = fields.Many2one("folder.master","File")
    remark = fields.Text("Remark",required=1)

    @api.multi
    def action_submit_file_reopen_approve(self):
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
        #     'action_taken': 'file_repoened',
        #     'remarks': self.remark,
        #     'details': f"File Repoen Approved on {date.today()}"
        # })
        self.folder_id.write({
            'state':'in_progress',
            'incoming_source':'file_reopen',
            'action_by_uid':self.folder_id.reopen_request_user.id,
            'action_time':datetime.now(),
            'action_date':datetime.now().date(),
        })
        # start : Add tracking information of reopen_request_approved to new model 28-December-2021
        self.env['smart_office.file.tracking'].create({
            'file_id':self.folder_id.id,
            'action_stage_id':self.env.ref('smart_office.file_stage_reopen_request_approved').id,
            'remark':self.remark,
        })
        # end : Add tracking information of reopen_request_approved to new model 28-December-2021
        self.env.user.notify_success("File reopen request approved successfully.")
        return {
                'name'      : 'Pending For Reopen',
                'view_mode' : 'tree,form',
                'view_type' : 'form',
                'view_id'   : False,
                'res_model' : 'folder.master',
                'type'      : 'ir.actions.act_window',
                'target'    : 'main',
                'domain'    :[("state",'=',"pending_reopen")],
                'context'   : {"action_pending_reopen":True,"filter_department":1,"edit":True,"create":False,"delete":False}
                }

class ReopenFileReject(models.TransientModel):
    _name = 'smart_office.reopen.file.reject'
    _description = "Reopen File Reject wizard"

    folder_id = fields.Many2one("folder.master","File")
    remark = fields.Text("Remark",required=1)

    @api.multi
    def action_submit_file_reopen_reject(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        # self.env['file.tracker.report'].create({
        #     'name': self.folder_id.folder_name,
        #     'number': self.folder_id.number,
        #     'type': 'File',
        #     'rejected_by': current_employee.user_id.name,
        #     'rejected_by_dept': current_employee.department_id.name,
        #     'rejected_by_jobpos': current_employee.job_id.name,
        #     'rejected_by_branch': current_employee.branch_id.name,
        #     'rejected_date': date.today(),
        #     'action_taken': 'file_repoen_reject',
        #     'remarks': self.remark,
        #     'details': f"File Repoen Rejected on {date.today()}"
        # })
        self.folder_id.state = 'closed'
        # start : Add tracking information of reopen_request_rejected to new model 28-December-2021
        self.env['smart_office.file.tracking'].create({
            'file_id':self.folder_id.id,
            'action_stage_id':self.env.ref('smart_office.file_stage_reopen_request_rejected').id,
            'remark':self.remark,
        })
        # end : Add tracking information of reopen_request_rejected to new model 28-December-2021
        self.env.user.notify_success("File reopen request rejected successfully.")
        return {
                'name'      : 'Pending For Reopen',
                'view_mode' : 'tree,form',
                'view_type' : 'form',
                'view_id'   : False,
                'res_model' : 'folder.master',
                'type'      : 'ir.actions.act_window',
                'target'    : 'main',
                'domain'    :[("state",'=',"pending_reopen")],
                'context'   : {"action_pending_reopen":True,"filter_department":1,"edit":True,"create":False,"delete":False}
                }