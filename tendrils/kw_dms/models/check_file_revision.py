# -*- coding: utf-8 -*-

import os
import io
import json
import base64
import logging
import mimetypes
import itertools
import tempfile
import hashlib
import operator
import functools

from collections import defaultdict

from odoo import _, SUPERUSER_ID
from odoo import models, api, fields, tools
from odoo.tools.mimetypes import guess_mimetype
from odoo.exceptions import ValidationError
from odoo.exceptions import AccessError
from odoo.osv import expression

from odoo.addons.kw_dms_utils.tools import file
from odoo.addons.kw_dms.tools.security import NoSecurityUid


class check_file_revision(models.Model):
    
    _inherit = 'kw_dms.file'
    
    @api.multi
    def write(self,vals):
        # print(self.checksum,' Old checksum')
        if 'checksum' in vals:
            # print(vals['checksum'],' New checksum')
            new_name        = vals['name'] if 'name' in vals else self.name
            new_directory   = vals['directory'] if 'directory' in vals else self.directory.id
            new_storage     = vals['storage'] if 'storage' in vals else self.storage.id
            new_path_names  = vals['path_names'] if 'path_names' in vals else self.path_names
            new_path_json   = vals['path_json'] if 'path_json' in vals else self.path_json
            new_category    = vals['category'] if 'category' in vals else self.category.id
            new_content     = vals['content'] if 'content' in vals else self.content
            new_extension   = vals['extension'] if 'extension' in vals else self.extension
            new_mimetype    = vals['mimetype'] if 'mimetype' in vals else self.mimetype
            new_size        = vals['size'] if 'size' in vals else self.size
            new_checksum    = vals['checksum'] if 'checksum' in vals else self.checksum
            new_save_type   = vals['save_type'] if 'save_type' in vals else self.save_type
            if self.checksum :
                if not self.checksum == new_checksum:
                    # print('Not Same')
                    self.env['revision_file'].sudo().create({
                        'file_id':int(self.id),
                        'name':new_name,
                        'directory':new_directory,
                        'storage':new_storage,
                        'path_names':new_path_names,
                        'path_json':new_path_json,
                        'category':new_category,
                        'content':new_content,
                        'extension':new_extension,
                        'mimetype':new_mimetype,
                        'size':new_size,
                        'checksum':new_checksum,
                        'save_type':new_save_type,
                        })
        return super(check_file_revision,self).write(vals)
    
    @api.model
    def create(self,vals):
        return super(check_file_revision,self).create(vals)