from odoo import fields, models, api
from datetime import datetime

class DispatchMode(models.TransientModel):
    _name = 'edit.doc.dispatch.mode'
    _description = 'Edit Dispatch Mode'


    dispatch_mode = fields.Selection(
        [('hand_to_hand', 'Hand to Hand'),('email', 'Email'), ('fax', 'Fax'), ('splmess', 'Spl. Messenger'), ('post', 'Post')
         ], string='Dispatch Mode')
    doc_dispatch = fields.Many2one('dispatch.document', string='Document Dispatch')



    def confirm_button(self):
        if self:
            self.doc_dispatch.write({
                'dispatch_mode': self.dispatch_mode,
            })
            form_view = self.env.ref('smart_office.foldermaster_form_view')
            tree_view = self.env.ref('smart_office.foldermaster_tree_view1')
            value = {
                'domain': str([('id', '=', self.doc_dispatch.folder_id.id)]),
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': 'folder.master',
                'view_id': False,
                'views': [(form_view and form_view.id or False, 'form'),
                          (tree_view and tree_view.id or False, 'tree')],
                'type': 'ir.actions.act_window',
                'res_id': self.doc_dispatch.folder_id.id,
                'target': 'current',
                'nodestroy': True
            }
            return value
