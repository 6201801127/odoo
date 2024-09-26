import os
import base64

import logging

from collections import defaultdict

from odoo import models, api, fields, tools
from odoo.tools import human_size

from odoo.addons.kw_dms_utils.fields import file

_logger = logging.getLogger(__name__)

class File(models.Model):
    
    _inherit = 'kw_dms.file'      
             
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    content_file = file.File(
        string="Content File",
        prefetch=False,
        invisible=True)
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------

    @api.model
    def _get_content_inital_vals(self):
        res = super(File, self)._get_content_inital_vals()
        res.update({'content_file': False})
        return res

    #----------------------------------------------------------
    # Read, View 
    #---------------------------------------------------------- 

    @api.depends('content_file')     
    def _compute_content(self):
        bin_size = self._check_context_bin_size('content')
        bin_recs = self.with_context({'bin_size': True})
        records = bin_recs.filtered(lambda rec: bool(rec.content_file))
        for record in records.with_context(self.env.context):
            context = {'human_size': True} if bin_size else {'base64': True}
            record.content = record.with_context(context).content_file
        super(File, self - records)._compute_content()
    
    @api.depends('content_file')
    def _compute_save_type(self):
        bin_recs = self.with_context({'bin_size': True})
        records = bin_recs.filtered(lambda rec: bool(rec.content_file))
        for record in records.with_context(self.env.context):
            record.save_type = "file"
        super(File, self - records)._compute_save_type()
    
    #----------------------------------------------------------
    # Create, Update, Delete
    #----------------------------------------------------------
    
    @api.multi
    def _inverse_content(self):
        records = self.filtered(
            lambda rec: rec.storage.save_type == 'file'
        )
        updates = defaultdict(set)
        for record in records:
            values = self._get_content_inital_vals()
            binary = base64.b64decode(record.content or "")
            values = self._update_content_vals(record, values, binary)
            values.update({
                'content_file': record.content and binary,
            })
            updates[tools.frozendict(values)].add(record.id)
        with self.env.norecompute():
            for vals, ids in updates.items():
                self.browse(ids).write(dict(vals))
        super(File, self - records)._inverse_content()