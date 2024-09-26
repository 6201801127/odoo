# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError
from odoo import tools, _
from odoo import models, fields, api

class kw_training_material_dms_integration(models.Model):
    _name = 'kw_training_material'
    # integration with DMS
    _inherit = [
        'kw_training_material',
        'kw_dms.kw_training.integration',
        ]

    content_file = fields.Binary(required=True, string="Upload Document")

class kw_training_material_dms(models.Model):
    _inherit = 'kw_training'

    dms_user_doc_dir_id = fields.Many2one('kw_dms.directory', ondelete='restrict',
                                          string="DMS User Document ID",)
    dms_user_doc_dir_access_group = fields.Many2one('kw_dms_security.access_groups', ondelete='restrict',
                                                    string="DMS User Document Access Group",)
    @api.multi
    def _create_training_material_folder(self):

        config_params = self.env['ir.config_parameter'].sudo()
        dir_model = self.env['kw_dms.directory'].sudo()
        access_group_model = self.env['kw_dms_security.access_groups'].sudo()

        dir_records = dir_model.search([])
        access_group_records = access_group_model.search([])

        training_upload_folder = int(config_params.get_param(
            'kw_dms.training_material_folder', False))

        for record in self:
            dms_user_doc_dir_access_group_id = record.dms_user_doc_dir_access_group.id
            dms_user_doc_dir_id = record.dms_user_doc_dir_id.id
            updatests = 0

            if record.start_date:
                folder_name = f"{record.name}-{record.start_date.strftime('%d-%b-%Y')}"

                dms_user_access_group_name = '%s_user_access_group' % (
                    folder_name)

                if dms_user_doc_dir_id and record.dms_user_doc_dir_id.name != folder_name:
                    record.dms_user_doc_dir_id.write({'name': folder_name})

                ##create main content directory
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
                            {'name': dms_user_access_group_name, 'perm_read': True, 'explicit_users': [[4, self.env.user.id, 0]]}).id

                    if existing_dms_user_doc_dir:
                        dms_user_doc_dir_id = existing_dms_user_doc_dir.id
                    else:
                        dms_user_doc_dir_id = dir_model.create({'name': folder_name, 'parent_directory': training_upload_folder, 'groups': [
                                                               [4, dms_user_doc_dir_access_group_id, 0]]}).id

                if updatests == 1:
                   record.write({'dms_user_doc_dir_access_group': dms_user_doc_dir_access_group_id,
                                 'dms_user_doc_dir_id': dms_user_doc_dir_id, })
            else:
                raise ValidationError(
                    "Please select training before uploading any document.")
