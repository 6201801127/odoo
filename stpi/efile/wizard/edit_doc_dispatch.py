from odoo import fields, models, api
from datetime import datetime

class AddReference(models.TransientModel):
    _name = 'edit.doc.dispatch'
    _description = 'Add Reference'


    select_template = fields.Many2one('select.template.html')
    template_html = fields.Html('Template')
    doc_dispatch = fields.Many2one('dispatch.document', string='Document Dispatch')

    @api.onchange('select_template')
    def get_template(self):
        if self.select_template:
            self.template_html = self.select_template.template


    def confirm_button(self):
        if self:
            self.doc_dispatch.write({
                'select_template': self.select_template.id,
                'template_html': self.template_html,
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
