# -*- coding: utf-8 -*-

import json
import logging
import operator
import functools
import collections

from odoo import models, api, fields

_logger = logging.getLogger(__name__)

class Directory(models.Model):
    
    _name = 'kw_dms.directory'

    _inherit = [
        'kw_dms_security.mixins.access_groups',
        'kw_dms.directory',
    ]
    
    _access_groups_strict = False
    _access_groups_mode = True
    
    _access_groups_sudo = True
    _access_groups_fields = False
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    inherit_groups = fields.Boolean(
        string="Inherit Groups",
        default=True)
    
    #----------------------------------------------------------
    # Groups
    #----------------------------------------------------------
    
    @api.depends('inherit_groups', 'parent_path')
    def _compute_groups(self):
        records = self.filtered(lambda record: record.parent_path)
        paths = [list(map(int, rec.parent_path.split('/')[:-1])) for rec in records]
        ids = paths and set(functools.reduce(operator.concat, paths)) or []
        read = self.browse(ids).read(['inherit_groups', 'groups'])
        data = {entry.pop("id"): entry for entry in read} 
        for record in records:
            complete_group_ids = set()
            for id in reversed(list(map(int, record.parent_path.split('/')[:-1]))):
                if id in data:
                    complete_group_ids |= set(data[id].get('groups', []))
                    if not data[id].get('inherit_groups'):
                        break
            record.update({'complete_groups': [(6, 0, list(complete_group_ids))]})
        for record in self - records:
            if record.parent_directory and record.inherit_groups:
                complete_groups = record.parent_directory.complete_groups
                record.complete_groups = record.groups | complete_groups
            else:
                record.complete_groups = record.groups

    #----------------------------------------------------------
    # Create, Update, Delete
    #----------------------------------------------------------
    
    @api.multi
    def write(self, vals):
        if any(key in vals for key in ['groups', 'inherit_groups']):
            with self.env.norecompute():
                res = super(Directory, self).write(vals)
                domain = [('id', 'child_of', self.ids)]
                records = self.sudo().search(domain)
                records.modified(['groups'])
            if self.env.recompute and self.env.context.get('recompute', True):
                records.recompute()
            return res  
        return super(Directory, self).write(vals)
        