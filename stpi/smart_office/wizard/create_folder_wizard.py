from odoo import fields, models, api
from datetime import datetime

class CreateFolder(models.TransientModel):
    _name = 'assignfolder.wizard'
    _description = 'Wizard of Create folder'

    @api.model
    def _get_emp_department_id(self):
        current_emp = self.env.user.employee_ids[0:1]
        if current_emp and current_emp.department_id:
            if current_emp.department_id.parent_id:
                return current_emp.department_id.parent_id.id
            else:
                return current_emp.department_id.id
    @api.model
    def _get_emp_division_id(self):
        current_emp = self.env.user.employee_ids[0:1]
        if current_emp and current_emp.department_id:
            if current_emp.department_id.parent_id:
                return current_emp.department_id.id
            else:
                return False

    folder = fields.Many2one('folder.master', string = 'Folder')
    deffolderid = fields.Many2one('muk_dms.file')
    # dg_id = fields.Many2one('green.sheets')
    # datas = fields.Binary(related='deffolderid.pdf_file')

    old_file_number = fields.Char(string='Old File Number')

    previous_reference = fields.Text('Previous Reference')
    later_reference = fields.Text('Later Reference')

    folder_name = fields.Char(string = 'File Name')
    subject = fields.Many2one('code.subject', string='Subject')
    date = fields.Date(string='Date', default = fields.Date.today())
    department_id = fields.Many2one('hr.department', 'Division',domain=[('parent_id','=',False)],required=True,default=_get_emp_department_id)
    division_id = fields.Many2one('hr.department', 'Sub Division',required=True,default=_get_emp_division_id)
    tags = fields.Many2many('muk_dms.tag', string='Tags')
    status = fields.Selection([('normal', 'Normal'),
                               ('important', 'Important'),
                               ('urgent', 'Urgent')
                               ], string='Status')
    type = fields.Many2many('folder.type', string = "Type")
    description = fields.Text(string = 'Description')

    @api.onchange('department_id')
    def set_division(self):
        if self.department_id:
            if self.division_id and self.division_id.parent_id != self.department_id:
                self.division_id = False
        else:
            self.division_id = False
            
    @api.onchange('division_id')
    def set_subject(self):
        self.subject = False

    @api.multi
    def confirm_button(self):
        letter_id = []
        letter_id.append(self.deffolderid.id)
        string = str(self.deffolderid.php_letter_id)
        file_id = self.env['folder.master'].with_context(no_log_record=True).create({
            'folder_name': self.folder_name,
            'subject': self.subject.id,
            'date': self.date,
            'department_id':self.department_id.id,
            'division_id':self.division_id.id,
            'tags': [[6,0,self.tags.ids]],
            'old_file_number': self.old_file_number,
            'status': self.status,
            'type': self.type,
            'description': self.description,
            'first_doc_id': int(self.deffolderid.php_letter_id),
            'document_ids': string,
            'file_ids' : [(6, 0, letter_id)],
            'state':'in_progress',
            'incoming_source':'self',
            'action_by_uid':self._uid,
            'action_time':datetime.now(),
            'action_date':datetime.now().date(),
        })

        self.deffolderid.write({'folder_id' : file_id.id,
                                'attach_to_file_date': datetime.now().date(),
                                'attach_to_file_time': datetime.now()})
        # start: added on 15 December 2021

        # current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        # self.env['file.tracker.report'].create({
        #     'name': str(self.deffolderid.name),
        #     'type': 'File',
        #     'assigned_by': str(current_employee.user_id.name),
        #     'assigned_by_dept': str(current_employee.department_id.name),
        #     'assigned_by_jobpos': str(current_employee.job_id.name),
        #     'assigned_by_branch': str(current_employee.branch_id.name),
        #     'assigned_date': datetime.now().date(),
        #     'action_taken': 'assigned_to_file',
        #     'remarks': self.description,
        #     'details': f"Correspondence attached to file {file_id.folder_name}"
        # })
        # start : Add tracking information of file_created to new model 28-December-2021
        self.env['smart_office.file.tracking'].create({
            'file_id':file_id.id,
            'action_stage_id':self.env.ref('smart_office.file_stage_file_created').id,
            'remark':self.description
        })
        # end : Add tracking information of file_created to new model 28-December-2021

        # start : Add tracking information of correspondence_attached to new model 28-December-2021
        # self.env['smart_office.file.tracking'].create({
        #     'file_id':file_id.id,
        #     'action_stage_id':self.env.ref('smart_office.file_stage_correspondence_attached').id,
        #     'remark':self.description
        # })
        # end : Add tracking information of correspondence_attached to new model 28-December-2021
        self.env['smart_office.correspondence.tracking'].create({
            'correspondence_id': self._context.get('active_id'),
            'action_stage_id': self.env.ref('smart_office.corres_stage_attach_file_from_create_file').id,
            'remark': self.description
        })
        self.env.user.notify_success("File created successfully.")
        form_view_id = self.env.ref('smart_office.foldermaster_form_view').id
        tree_view_id = self.env.ref('smart_office.foldermaster_tree_view1').id
        return {
            'domain': str([('id', '=', file_id.id)]),
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'folder.master',
            'view_id': False,
            'views': [(form_view_id, 'form'),(tree_view_id, 'tree')],
            'type': 'ir.actions.act_window',
            'res_id': file_id.id,
            'target': 'current',
            'nodestroy': True
        }