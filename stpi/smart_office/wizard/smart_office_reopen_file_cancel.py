from datetime import date
from odoo import models,fields,api

class ReopenFileCancel(models.TransientModel):
    _name = 'smart_office.reopen.file.cancel'
    _description = "Reopen file cancel wizard"

    folder_id = fields.Many2one("folder.master","File")
    remark = fields.Text("Remark",required=1)

    @api.multi
    def action_submit_file_reopen_cancel(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        # self.env['file.tracker.report'].create({
        #     'name': self.folder_id.folder_name,
        #     'number': self.folder_id.number,
        #     'type': 'File',
        #     'cancelled_by': current_employee.user_id.name,
        #     'cancelled_by_dept': current_employee.department_id.name,
        #     'cancelled_by_jobpos': current_employee.job_id.name,
        #     'cancelled_by_branch': current_employee.branch_id.name,
        #     'cancelled_date': date.today(),
        #     'action_taken': 'cancel_file_repoen',
        #     'remarks': self.remark,
        #     'details': f"File Repoen Cancelled on {date.today()}"
        # })

        self.folder_id.state = 'closed'
        # start : Add tracking information of reopen_request_cancelled to new model 28-December-2021
        self.env['smart_office.file.tracking'].create({
            'file_id':self.folder_id.id,
            'action_stage_id':self.env.ref('smart_office.file_stage_reopen_request_cancelled').id,
            'remark':self.remark,
        })
        # end : Add tracking information of reopen_request_cancelled to new model 28-December-2021
        self.env.user.notify_success("File reopen request cancelled successfully.")

        return {
                'name'      : 'View Status',
                'view_mode' : 'tree,form',
                'view_type' : 'form',
                'view_id'   : False,
                'views'     : [(self.env.ref("smart_office.foldermaster_tree_view1").id, 'tree'),(self.env.ref("smart_office.foldermaster_form_view").id, 'form')],
                'res_model' : 'folder.master',
                'type'      : 'ir.actions.act_window',
                'target'    : 'main',
                'domain'    : [('reopen_request_user','=',self._uid),("state",'in',["pending_close","pending_reopen"])],
                'context'   : {"group_by":"state","filter_department":1,"create":False,"delete":False,"edit":False},
                }