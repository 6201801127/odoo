from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    upload_doc_dir_id = fields.Many2one('kw_dms.directory', ondelete='restrict', string="Uploaded Document ID", )
    upload_doc_dir_access_group = fields.Many2one('kw_dms_security.access_groups', ondelete='restrict',
                                                  string="Uploaded Document Access Group", )

    issue_doc_dir_id = fields.Many2one('kw_dms.directory', ondelete='restrict', string="Issued Document ID", )
    issue_doc_dir_access_group = fields.Many2one('kw_dms_security.access_groups', ondelete='restrict',
                                                 string="Issued Document Access Group", )

    dms_user_doc_dir_id = fields.Many2one('kw_dms.directory', ondelete='restrict', string="DMS User Document ID", )
    dms_user_doc_dir_access_group = fields.Many2one('kw_dms_security.access_groups', ondelete='restrict',
                                                    string="DMS User Document Access Group", )

    @api.multi
    def _create_digilock_folder(self):

        config_params = self.env['ir.config_parameter'].sudo()
        dir_model = self.env['kw_dms.directory'].sudo()
        access_group_model = self.env['kw_dms_security.access_groups'].sudo()

        dir_records = dir_model.search([])
        access_group_records = access_group_model.search([])

        digilock_upload_folder = int(config_params.get_param('kw_dms.digilock_hr_employee_folder', False))

        for record in self:

            dms_user_doc_dir_access_group_id = record.dms_user_doc_dir_access_group.id
            dms_user_doc_dir_id = record.dms_user_doc_dir_id.id

            upload_doc_dir_access_group_id = record.upload_doc_dir_access_group.id
            upload_doc_dir_id = record.upload_doc_dir_id.id

            issue_doc_dir_access_group_id = record.issue_doc_dir_access_group.id
            issue_doc_dir_id = record.issue_doc_dir_id.id

            updatests = 0

            if record.user_id:

                # folder_name                 = '%s_%s'%(record.user_id.login,record.id)
                folder_name = '%s' % (record.user_id.login)

                upload_access_group_name = '%s_upload_access_group' % (record.user_id.login)
                issue_access_group_name = '%s_issued_access_group' % (record.user_id.login)
                dms_user_access_group_name = '%s_user_access_group' % (record.user_id.login)

                if upload_doc_dir_id and issue_doc_dir_id and dms_user_doc_dir_id and record.dms_user_doc_dir_id.name != folder_name:
                    record.dms_user_doc_dir_id.write({'name': folder_name})

                """##create main user directory"""
                if not dms_user_doc_dir_id:

                    updatests = 1

                    existing_dms_user_doc_dir = dir_records.filtered(lambda r: r.name == folder_name)
                    existing_dms_user_access_group = access_group_records.filtered(
                        lambda r: r.name == dms_user_access_group_name)

                    if existing_dms_user_access_group:
                        dms_user_doc_dir_access_group_id = existing_dms_user_access_group.id
                    else:
                        dms_user_doc_dir_access_group_id = access_group_model.create(
                            {'name': dms_user_access_group_name,
                             'perm_read': True,
                             'explicit_users': [[4, record.user_id.id, 0]]}).id

                    if existing_dms_user_doc_dir:
                        dms_user_doc_dir_id = existing_dms_user_doc_dir.id
                    else:
                        dms_user_doc_dir_id = dir_model.create(
                            {'name': folder_name,
                             'parent_directory': digilock_upload_folder,
                             'groups': [[4, dms_user_doc_dir_access_group_id, 0]]}).id

                """##create user upload documents directory"""
                if not upload_doc_dir_access_group_id or upload_doc_dir_id:
                    updatests = 1

                    existing_upload_doc_dir = dir_records.filtered(
                        lambda r: r.name == 'Uploaded Documents' and r.parent_directory.id == dms_user_doc_dir_id)
                    existing_upload_doc_dir_access_group = access_group_records.filtered(
                        lambda r: r.name == upload_access_group_name)

                    if existing_upload_doc_dir_access_group:
                        upload_doc_dir_access_group_id = existing_upload_doc_dir_access_group.id
                    else:
                        upload_doc_dir_access_group_id = access_group_model.create(
                            {'name': upload_access_group_name,
                             'perm_read': True,
                             'perm_create': True,
                             'perm_write': True, 'explicit_users': [[4, record.user_id.id, 0]]}).id

                    if existing_upload_doc_dir:
                        upload_doc_dir_id = existing_upload_doc_dir.id
                    else:
                        upload_doc_dir_id = dir_model.create(
                            {'name': 'Uploaded Documents',
                             'parent_directory': dms_user_doc_dir_id,
                             'groups': [[4, upload_doc_dir_access_group_id, 0]]}).id

                """##create user Issued documents directory"""
                if not issue_doc_dir_access_group_id or not issue_doc_dir_id:

                    updatests = 1

                    existing_issued_doc_dir = dir_records.filtered(lambda r: r.name == 'Issued Documents' and r.parent_directory.id == dms_user_doc_dir_id)
                    existing_issued_doc_dir_access_group = access_group_records.filtered(lambda r: r.name == issue_access_group_name)

                    if existing_issued_doc_dir_access_group:
                        issue_doc_dir_access_group_id = existing_issued_doc_dir_access_group.id
                    else:
                        issue_doc_dir_access_group_id = access_group_model.create(
                            {'name': issue_access_group_name,
                             'perm_read': True,
                             'explicit_users': [[4, record.user_id.id, 0]]}).id

                    if existing_issued_doc_dir:
                        issue_doc_dir_id = existing_issued_doc_dir.id
                    else:
                        issue_doc_dir_id = dir_model.create(
                            {'name': 'Issued Documents',
                             'parent_directory': dms_user_doc_dir_id,
                             'groups': [[4, issue_doc_dir_access_group_id, 0]]}).id

                if updatests == 1:
                    record.write({'dms_user_doc_dir_access_group': dms_user_doc_dir_access_group_id,
                                  'dms_user_doc_dir_id': dms_user_doc_dir_id,
                                  'upload_doc_dir_access_group': upload_doc_dir_access_group_id,
                                  'upload_doc_dir_id': upload_doc_dir_id,
                                  'issue_doc_dir_access_group': issue_doc_dir_access_group_id,
                                  'issue_doc_dir_id': issue_doc_dir_id})
            else:
                raise ValidationError("Please configure the related user setting for the selected employee, \
                before uploading any document.")

    # @api.model
    # def create(self, vals):
    #     record = super(hr_employee, self).create(vals)
    #     record._create_digilock_folder()
    #     return record

    # @api.multi
    # def write(self, vals):
    #     record = super(hr_employee, self).write(vals)
    #     if 'user_id' in vals:
    #         self._create_digilock_folder()
    #     return record
