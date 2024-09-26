# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError
from odoo import tools, _
from odoo import models, fields, api


class kw_meeting_doc_dms_integration(models.Model):
    _name = 'ir.attachment'
    _inherit = [
        'ir.attachment',
        'kw_dms.kw_meeting.integration',
    ]
    content_file = fields.Binary(required=False, string="Upload Document")
    datas = fields.Binary(required=True, string="Upload Document")
    # name = fields.Char('Name', required=True)

    @api.model
    def create(self, values):
        if 'name' not in values or values.get('name') is False and values.get('datas_fname'):
            values['name'] = values.get('datas_fname')
        return super(kw_meeting_doc_dms_integration, self.with_context(mail_create_nolog=True)).create(values)

    @api.multi
    def write(self, vals):
        if 'name' not in vals or vals.get('name') is False and vals.get('datas_fname'):
            vals['name'] = vals.get('datas_fname')
        if vals.get('name') == None :
            vals['name'] = 'None'
        return super(kw_meeting_doc_dms_integration, self.with_context(mail_create_nolog=True)).write(vals)

    def auto_document_migration(self):
        meetings = self.env['ir.attachment'].search([('res_model', '=', 'kw_meeting_events'), ('dms_file_id', '=', False)])
        if meetings:
            for meeting in meetings:
                if meeting.datas is not None:
                    res_id = self.env['kw_dms.file'].search([('res_id', '=', meeting.id)])
                    if not res_id:
                        dms_id = self.env['kw_dms.kw_meeting.integration'].create_dms_file_with_resid(meeting.datas, meeting.name, meeting)
        return True


class kw_meeting_events_doc_dms(models.Model):
    _inherit = "kw_meeting_events"

    dms_user_doc_dir_id = fields.Many2one('kw_dms.directory', ondelete='restrict',string="DMS User Document ID",)
    dms_user_doc_dir_access_group = fields.Many2one('kw_dms_security.access_groups', ondelete='restrict',
                                                    string="DMS User Document Access Group",)

    @api.multi
    def _create_meeting_docs_folder(self):
        config_params = self.env['ir.config_parameter'].sudo()
        dir_model = self.env['kw_dms.directory'].sudo()
        access_group_model = self.env['kw_dms_security.access_groups'].sudo()
        dir_records = dir_model.search([])
        access_group_records = access_group_model.search([])
        meeting_upload_folder = int(config_params.get_param('kw_dms.meeting_doc_folder', False))
        for record in self:
            dms_user_doc_dir_access_group_id = record.dms_user_doc_dir_access_group.id
            dms_user_doc_dir_id = record.dms_user_doc_dir_id.id
            updatests = 0
            if record.create_date:
                folder_name = f"{record.meeting_code}-{record.create_date.strftime('%d-%b-%Y')}"
                dms_user_access_group_name = '%s_user_access_group' % (folder_name)
                if dms_user_doc_dir_id and record.dms_user_doc_dir_id.name != folder_name:
                    record.dms_user_doc_dir_id.write({'name': folder_name})
                """ create main user directory"""
                if not dms_user_doc_dir_id:
                    updatests = 1
                    existing_dms_user_doc_dir = dir_records.filtered(lambda r: r.name == folder_name)
                    existing_dms_user_access_group = access_group_records.filtered(lambda r: r.name == dms_user_access_group_name)

                    if existing_dms_user_access_group:
                        dms_user_doc_dir_access_group_id = existing_dms_user_access_group.id
                    else:
                        dms_user_doc_dir_access_group_id = access_group_model.create(
                            {'name': dms_user_access_group_name,
                             'perm_read': True,
                             'explicit_users': [[4, self.env.user.id, 0]]}).id

                    if existing_dms_user_doc_dir:
                        dms_user_doc_dir_id = existing_dms_user_doc_dir.id
                    else:
                        dms_user_doc_dir_id = dir_model.create({
                            'name': folder_name, 
                            'parent_directory': meeting_upload_folder, 
                            'groups': [[4, dms_user_doc_dir_access_group_id, 0]]}).id
                if updatests == 1:
                    record.write({'dms_user_doc_dir_access_group': dms_user_doc_dir_access_group_id,
                                 'dms_user_doc_dir_id': dms_user_doc_dir_id, })
            else:
                raise ValidationError("Please select applicant before uploading any document.")

