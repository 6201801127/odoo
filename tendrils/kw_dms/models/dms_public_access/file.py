# -*- coding: utf-8 -*-

from odoo import models, api, fields


class FilePublicAccess(models.Model):
    _inherit = 'kw_dms.file'

    file_public_url = fields.Char(string='Public URL', store=True)

    @api.multi
    def create_public_url(self):
        for record in self:
            name = "Access Attachment: %s" % record.name
            attachment = self.env['ir.attachment'].create({
                'name': "%s (Temporary)" % name or name,
                'datas': record.content,
                'datas_fname': record.name,
                'type': 'binary',
                'public': False,
            })
            attachment.generate_access_token()
            if record.mimetype and record.mimetype != 'application/octet-stream':
                attachment.sudo().write({
                    'mimetype': record.mimetype,
                })
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            record.file_public_url = '%s/web/content/%s?access_token=%s' % (
            base_url, attachment.id, attachment.access_token)

        return True
