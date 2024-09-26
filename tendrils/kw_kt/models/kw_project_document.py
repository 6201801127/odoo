from odoo import models, fields, api
from kw_utility_tools import kw_validations


class kw_project_document(models.Model):
    _name = "kw_project_document"
    _description = " Upload Project Documents"
    # _rec_name = 'project_id'

    document_attach = fields.Binary(string="Document", required=True, attachment=True)
    doc_file_name = fields.Char(string="Document Name")
    # project_id = fields.Many2one('project.project',string="For Project")
    # description = fields.Char(string='Description', required=True, size=198)
    time_line_plan_id = fields.Many2one('kw_time_line_plan', string="Time Line Plan Id", required=True)

    @api.multi
    def btn_document_submit(self):
        view_id = self.env.ref('kw_kt.kw_kt_activity_form').id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_time_line_plan',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            'res_id': self.time_line_plan_id.id,
        }
        return action

    @api.constrains('document_attach')
    def validate_document_attach(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
        for record in self:
            kw_validations.validate_file_mimetype(record.document_attach, allowed_file_list)
            kw_validations.validate_file_size(record.document_attach, 4)
