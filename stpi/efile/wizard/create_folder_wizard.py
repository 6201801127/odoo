from odoo import fields, models, api
from datetime import datetime

class CreateFolder(models.TransientModel):
    _name = 'assignfolder.wizard'
    _description = 'Wizard of Create folder'


    folder = fields.Many2one('folder.master', string = 'Folder')
    dg_id = fields.Many2one('green.sheets')
    deffolderid = fields.Many2one('muk_dms.file')
    datas = fields.Binary(related='deffolderid.pdf_file')

    old_file_number = fields.Char(string='Old File Number')

    previous_reference = fields.Text('Previous Reference')
    later_reference = fields.Text('Later Reference')

    folder_name = fields.Char(string = 'File Name')
    subject = fields.Many2one('code.subject', string='Subject')
    date = fields.Date(string='Date', default = fields.Date.today())
    tags = fields.Many2many('muk_dms.tag', string='Tags')
    status = fields.Selection([('normal', 'Normal'),
                               ('important', 'Important'),
                               ('urgent', 'Urgent')
                               ], string='Status')
    type = fields.Many2many('folder.type', string = "Type")
    description = fields.Text(string = 'Description')




    def confirm_button(self):
        if self:
            letter_id = []
            letter_id.append(self.deffolderid.id)
            string = str(self.deffolderid.php_letter_id)
            print('===============string================', string)
            file_id = self.env['folder.master'].create({
                'folder_name': self.folder_name,
                'subject': self.subject.id,
                'date': self.date,
                'tags': self.tags,
                'old_file_number': self.old_file_number,
                'status': self.status,
                'type': self.type,
                'description': self.description,
                'first_doc_id': int(self.deffolderid.php_letter_id),
                'document_ids': string,
                'file_ids' : [(6, 0, letter_id)]
            })
            self.deffolderid.folder_id = file_id.id
            current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['file.tracker.report'].create({
                'name': str(self.deffolderid.name),
                'type': 'File',
                'assigned_by': str(current_employee.user_id.name),
                'assigned_by_dept': str(current_employee.department_id.name),
                'assigned_by_jobpos': str(current_employee.job_id.name),
                'assigned_by_branch': str(current_employee.branch_id.name),
                'assigned_date': datetime.now().date(),
                'action_taken': 'assigned_to_file',
                'remarks': self.description,
                'details': "Correspondence attached to file {}".format(file_id.folder_name)
            })
            form_view = self.env.ref('smart_office.foldermaster_form_view')
            tree_view = self.env.ref('smart_office.foldermaster_tree_view1')
            value = {
                'domain': str([('id', '=', file_id.id)]),
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': 'folder.master',
                'view_id': False,
                'views': [(form_view and form_view.id or False, 'form'),
                          (tree_view and tree_view.id or False, 'tree')],
                'type': 'ir.actions.act_window',
                'res_id': file_id.id,
                'target': 'current',
                'nodestroy': True
            }
            return value