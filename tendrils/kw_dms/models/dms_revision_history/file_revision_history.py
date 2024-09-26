# -*- coding: utf-8 -*-
import logging

from odoo import models, api, fields

from odoo.addons.kw_dms_utils.fields import file

_logger = logging.getLogger(__name__)


class Revision_file(models.Model):

    _name           = 'kw_dms.file_revision_history'
    _description    = "DMS revision files"
    
    file_id         = fields.Many2one(comodel_name='kw_dms.file', string="File",)

    name            = fields.Char(string="File Name", index=True)
    directory       = fields.Many2one(comodel_name='kw_dms.directory', string="Directory",)
    storage         = fields.Many2one(comodel_name='kw_dms.storage', string="Storage",)
    path_names      = fields.Char()
   
    content         = fields.Binary(string="File Content",attachment=True)
    

    extension       = fields.Char()
    mimetype        = fields.Char()
    size            = fields.Integer()
    version         = fields.Float(digits=(12,1))
    checksum        = fields.Char(
        string="Checksum/SHA1",
        readonly=True, 
        size=40, 
        index=True)
   
  
