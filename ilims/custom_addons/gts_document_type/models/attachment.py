# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    name = fields.Char(string='Document Name')
    document_type_id = fields.Many2one('document.type', string='Document Type')
    project_id = fields.Many2one('project.project', 'Project')

    # def write(self, vals):
    #     if self.env.context.get('params'):
    #         if self.env.context.get('params').get('model') == 'project.project':
    #             prev_document_name = self.name or ''
    #             prev_category = self.document_type_id.name
    #             prev_type = dict(self._fields['type'].selection).get(self.type)
    #             # prev_attachment = self.store_fname
    #             prev_url = self.url or ''
    #             rec = super(IrAttachment, self).write(vals)
    #             # • Attachment: {prev_attachment} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {attachment}<br/>
    #             message_body = """<b>Documents</b><br/>
    #                             • Document Name: {prev_document_name} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {document_name} <br/>
    #                             • Document Category: {prev_category} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {category}<br/>
    #                             • Type: {prev_type} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {type}<br/>
    #                             • URL: {prev_url} <i class="fa fa-long-arrow-right" aria-hidden="true"></i> {url}""" \
    #                 .format(prev_document_name=prev_document_name, document_name=self.name or '',
    #                         prev_category=prev_category, category=self.document_type_id.name,
    #                         prev_type=prev_type, type=dict(self._fields['type'].selection).get(self.type),
    #                         # prev_attachment=prev_attachment, attachment=self.store_fname,
    #                         prev_url=prev_url, url=self.url or '')
    #             self.project_id.message_post(body=message_body)
    #             return rec
    #         else:
    #             return super(IrAttachment, self).write(vals)
    #     else:
    #         return super(IrAttachment, self).write(vals)
