from odoo import fields, models, api
from datetime import datetime
import requests
import json
from odoo.exceptions import UserError

class AddReference(models.TransientModel):
    _name = 'add.reference.file'
    _description = 'Add Reference'


    cooespondence_ids = fields.Many2many('muk_dms.file', string='Correspondence')
    description = fields.Text()
    folder_id = fields.Many2one('folder.master', string="Select File")


    def confirm_button(self):
        if self:
            letter_id = []
            current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            for file in self.cooespondence_ids:
                file.folder_id = self.folder_id.id
                self.folder_id.file_ids = [(4, file.id)]
                letter_id.append(file.id)
                self.env['file.tracker.report'].create({
                    'name': str(file.name),
                    'type': 'Correspondence',
                    'assigned_by': str(current_employee.user_id.name),
                    'assigned_by_dept': str(current_employee.department_id.name),
                    'assigned_by_jobpos': str(current_employee.job_id.name),
                    'assigned_by_branch': str(current_employee.branch_id.name),
                    'assigned_date': datetime.now().date(),
                    'action_taken': 'assigned_to_file',
                    'remarks': self.description,
                    'details': "Correspondence attached to file {}".format(self.folder_id.folder_name)
                })
                self.folder_id.document_ids = str(self.folder_id.document_ids) + ',' + str(file.php_letter_id)
            print('============self.folder_id.document_ids=================', self.folder_id.document_ids)
            self.folder_id.folder_ids = [(6, 0, letter_id)]
            data = {
                'assign_name': self.folder_id.folder_name,
                'assign_no': self.folder_id.sequence,
                'assign_date': self.folder_id.date,
                'assign_subject': (self.folder_id.subject.subject),
                'remarks': self.folder_id.description,
                'created_by': self.folder_id.current_owner_id.id,
                'doc_flow_id': 0,
                'wing_id': self.folder_id.department_id.id,
                'section_id': 0,
                'designation_id': self.folder_id.job_id.id,
                'document_ids': self.folder_id.document_ids,
            }
            req = requests.post('http://206.189.129.190/STPI/www/web-service/add-assignment/', data=data,
                                json=None)
            try:
                pastebin_url = req.text
                print('============Patebin url=================', pastebin_url)
                dictionary = json.loads(pastebin_url)
            except Exception as e:
                print('=============Error==========',e)
            form_view = self.env.ref('smart_office.foldermaster_form_view')
            tree_view = self.env.ref('smart_office.foldermaster_tree_view1')
            value = {
                'domain': str([('id', '=', self.folder_id.id)]),
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': 'folder.master',
                'view_id': False,
                'views': [(form_view and form_view.id or False, 'form'),
                          (tree_view and tree_view.id or False, 'tree')],
                'type': 'ir.actions.act_window',
                'res_id': self.folder_id.id,
                'target': 'current',
                'nodestroy': True
            }
            return value