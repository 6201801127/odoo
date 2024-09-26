# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError
from odoo import tools, _
from odoo import models, fields, api


class kw_recruitment_documents_integration(models.Model):
    _name = 'kw_recruitment_documents'
    """##integration with DMS"""
    _inherit = [
        'kw_dms.kw_recruitment.integration',
    ]

    content_file = fields.Binary(required=True, string="Upload Document", store=True)
    applicant_id = fields.Many2one('hr.applicant', string="Ref")
    ir_attachment_id = fields.Many2one('ir.attachment')

    @api.model
    def create(self, values):
        # if not values.get('ir_attachment_id'):
        #     vals = {
        #         'res_model': values.get('res_model'),
        #         'res_id': values.get('applicant_id'),
        #         'datas': values.get('content_file'),
        #         'datas_fname': values.get('file_name')
        #     }
        #     attachment = self.env['ir.attachment'].create(vals)
        #     values['ir_attachment_id'] = attachment.id
        return super(kw_recruitment_documents_integration, self.with_context(mail_create_nolog=True)).create(values)
    
    def unlink(self):
        # self.ir_attachment_id.unlink()
        doc_ids = []
        for rec in self:
            doc_ids.append(rec.dms_file_id.id)
        record = super(kw_recruitment_documents_integration, self).unlink()
        for doc_id in doc_ids:
            self.env['kw_dms.file'].sudo().browse(doc_id).unlink()
        return record


class Attachments(models.Model):
    _inherit = 'ir.attachment'

    name = fields.Char(required=False)
  
    def auto_document_migration(self):
        applications = self.env['ir.attachment'].search([('res_model', '=', 'hr.applicant')])
        if applications:
            for application in applications:
                if application.datas is not None:
                    res_id = self.env['kw_recruitment_documents'].search([('ir_attachment_id', '=', application.id)])
                    file_id = self.env['kw_dms.file'].search([('res_id', '=', application.id)])
                    if not res_id:
                        self.env['kw_recruitment_documents'].create({
                            'applicant_id': application.res_id,
                            'content_file': application.datas,
                            'file_name': application.datas_fname,
                            'ir_attachment_id': application.id})
                    if not res_id and not file_id:
                        dms_id = self.env['kw_dms.kw_recruitment.integration'].create_dms_file_with_resid(
                            application.datas, application.name, application)
        return True


class kw_recruitment_cv_dms(models.Model):
    _inherit = 'hr.applicant'

    dms_user_doc_dir_id = fields.Many2one('kw_dms.directory', ondelete='restrict',
                                          string="DMS User Document ID", )
    dms_user_doc_dir_access_group = fields.Many2one('kw_dms_security.access_groups', ondelete='restrict',
                                                    string="DMS User Document Access Group", )
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'hr.applicant')],
                                     string='Attachments')

    document_ids = fields.One2many('kw_recruitment_documents', 'applicant_id', string='Documents')
    document_number = fields.Integer(compute='_compute_document_number', help='Document Count')

    @api.depends('document_ids')
    def _compute_document_number(self):
        # print("compute called")
        for applicant in self:
            # print("applicant",applicant)
            # print("length od document ids",len(applicant.document_ids))
            applicant.document_number = len(applicant.document_ids)

    @api.constrains('document_ids')
    def validate_document_ids(self):
        for record in self:
            if len(record.document_ids) == 0:
                raise ValidationError("Please add Documents.")

    @api.model
    def create(self, vals):
        if not vals.get('document_ids') or vals.get('document_ids') == []:
            raise ValidationError("Please Add Documents.")
        else:
            for attachment in vals.get('document_ids'):
                if isinstance(attachment[2], dict):
                    attachment[2]['res_model'] = 'hr.applicant'

        return super(kw_recruitment_cv_dms, self.with_context(mail_create_nolog=True)).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('document_ids'):
            for attachment in vals.get('document_ids'):
                if isinstance(attachment[2], dict):
                    attachment[2]['res_model'] = 'hr.applicant'
        return super(kw_recruitment_cv_dms, self.with_context(mail_create_nolog=True)).write(vals)

    @api.multi
    def _create_recruitment_cv_folder(self):

        config_params = self.env['ir.config_parameter'].sudo()
        dir_model = self.env['kw_dms.directory'].sudo()
        access_group_model = self.env['kw_dms_security.access_groups'].sudo()

        dir_records = dir_model.search([])
        access_group_records = access_group_model.search([])

        recruitment_upload_folder = int(config_params.get_param(
            'kw_dms.recruitment_cv_folder', False))

        for record in self:

            dms_user_doc_dir_access_group_id = record.dms_user_doc_dir_access_group.id
            dms_user_doc_dir_id = record.dms_user_doc_dir_id.id

            # upload_doc_dir_access_group_id = record.upload_doc_dir_access_group.id
            # upload_doc_dir_id = record.upload_doc_dir_id.id

            updatests = 0

            if record.create_date:

                folder_name = f"{record.partner_name}-{record.create_date.strftime('%d-%b-%Y')}"

                # upload_access_group_name = '%s_upload_access_group' % (
                #     folder_name)
                dms_user_access_group_name = '%s_user_access_group' % (
                    folder_name)

                if dms_user_doc_dir_id and record.dms_user_doc_dir_id.name != folder_name:
                    record.dms_user_doc_dir_id.write({'name': folder_name})

                """##create main user directory"""
                if not dms_user_doc_dir_id:

                    updatests = 1

                    existing_dms_user_doc_dir = dir_records.filtered(
                        lambda r: r.name == folder_name)
                    existing_dms_user_access_group = access_group_records.filtered(
                        lambda r: r.name == dms_user_access_group_name)

                    if existing_dms_user_access_group:
                        dms_user_doc_dir_access_group_id = existing_dms_user_access_group.id
                    else:
                        dms_user_doc_dir_access_group_id = access_group_model.create(
                            {'name': dms_user_access_group_name, 'perm_read': True,
                             'explicit_users': [[4, self.env.user.id, 0]]}).id

                    if existing_dms_user_doc_dir:
                        dms_user_doc_dir_id = existing_dms_user_doc_dir.id
                    else:
                        dms_user_doc_dir_id = dir_model.create(
                            {'name': folder_name, 'parent_directory': recruitment_upload_folder, 'groups': [
                                [4, dms_user_doc_dir_access_group_id, 0]]}).id

                if updatests == 1:
                    record.write({'dms_user_doc_dir_access_group': dms_user_doc_dir_access_group_id,
                                  'dms_user_doc_dir_id': dms_user_doc_dir_id, })

            else:
                raise ValidationError(
                    "Please select applicant before uploading any document.")

    @api.multi
    def action_get_documents(self):
        wizard_form = self.env.ref('kw_recruitment_dms_integration.doc_one2many_list_view', False)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': wizard_form.id,
            'res_model': 'kw_recruitment_documents',
            'target': 'new',
            'res_id': self.document_ids.id,
            'domain': [('applicant_id', '=', self.id)],
            'create': False,
            'edit': False
        }
