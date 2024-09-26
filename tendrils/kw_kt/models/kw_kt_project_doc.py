from odoo import models, fields, api
from odoo.exceptions import ValidationError
from ast import literal_eval
from kw_utility_tools import kw_validations


class kw_kt_project_doc(models.Model):
    _name = "kw_kt_project_doc"
    _description = "KT Document Upload"
    _rec_name = 'project_id'

    @api.model
    def _domain_get_ids(self):
        # print("_domain_get_ids called")
        # print("context",self._context)
        # kt_doc_rec = self.env['kw_time_line_plan'].sudo().search([('kt_view_id','=',self.kt_view_doc_id.id)])
        # project_list = kt_doc_rec.mapped('project_id')
        # print(project_list.ids)
        domain = [('id', 'in', literal_eval(self._context.get('default_project_strs', '[]')))]
        # print("domain is",domain)
        return domain

    kt_view_doc_id = fields.Many2one('kw_kt_view', string="KT view id", ondelete='cascade')
    project_id = fields.Many2one('project.project', string="Project", domain=_domain_get_ids)
    document_attach = fields.Binary(string="Document Attach", attachment=True)
    doc_file_name = fields.Char(string="Document Name")
    details = fields.Text(string="Description")

    @api.constrains('document_attach')
    def validate_document_attach(self):
        allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
        for record in self:
            kw_validations.validate_file_mimetype(record.document_attach, allowed_file_list)
            kw_validations.validate_file_size(record.document_attach, 4)
