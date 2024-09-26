# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

from odoo.addons.web.controllers.main import Binary
from odoo.addons.web.controllers.main import serialize_exception, content_disposition


class BinaryInherit(Binary):

    @http.route(['/web/content',
        '/web/content/<string:xmlid>',
        '/web/content/<string:xmlid>/<string:filename>',
        '/web/content/<int:id>',
        '/web/content/<int:id>/<string:filename>',
        '/web/content/<int:id>-<string:unique>',
        '/web/content/<int:id>-<string:unique>/<string:filename>',
        '/web/content/<int:id>-<string:unique>/<path:extra>/<string:filename>',
        '/web/content/<string:model>/<int:id>/<string:field>',
        '/web/content/<string:model>/<int:id>/<string:field>/<string:filename>'], type='http', auth="public")
    def content_common(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       filename=None, filename_field='datas_fname', unique=None, mimetype=None,
                       download=None, data=None, token=None, access_token=None, related_id=None, access_mode=None,
                       **kw):
        res = super(BinaryInherit, self).content_common(xmlid, model, id, field,
                                                        filename, filename_field, unique, mimetype,
                                                        download, data, token, access_token, related_id, access_mode,
                                                        **kw)
        uid = request.env.user.id
        if model == 'kw_dms.file' and download and id and uid:
            emp_id = request.env['hr.employee'].sudo().search([('user_id', '=', uid)], limit=1).id or False
            request.env['kw_dms.file_download_log'].create({'user_id': uid, 'employee_id': emp_id, 'file_id': id})
            # print("Downloading ....")
        return res
