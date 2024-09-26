# -*- coding: utf-8 -*-
import base64
import logging
import mimetypes

from odoo import models
from odoo.exceptions import AccessError
from odoo.http import request, STATIC_CACHE
from odoo.tools.mimetypes import guess_mimetype

_logger = logging.getLogger(__name__)

class IrHttp(models.AbstractModel):
    
    _inherit = 'ir.http'
    
    @classmethod
    def binary_content(cls, xmlid=None, model='ir.attachment', id=None, field='datas', unique=False, filename=None,
        filename_field='datas_fname', download=False, mimetype=None, default_mimetype='application/octet-stream',
        access_token=None, related_id=None, access_mode=None, env=None):
        res_status, res_headers, res_content = super(IrHttp, cls).binary_content(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename, mimetype=mimetype,
            filename_field=filename_field, download=download, access_mode=access_mode, related_id=related_id,
            default_mimetype=default_mimetype, access_token=access_token, env=env)
        if res_status == 200:
            env = env or request.env
            if model == "kw_dms.file" and field != 'content':
                obj = cls._xmlid_to_obj(env, xmlid) if xmlid else env[model].browse(int(id))
                filename = obj[filename_field] if not filename and filename_field in obj else filename
                mimetype = filename and mimetypes.guess_type(filename)[0]
                if not mimetype:
                    mimetype = guess_mimetype(base64.b64decode(res_content), default=default_mimetype)
                headers = []
                for header in res_headers:
                    if header[0] == 'Content-Type':
                        headers.append(('Content-Type', mimetype))
                    else:
                        headers.append(header)
                return res_status, headers, res_content
        return res_status, res_headers, res_content
        