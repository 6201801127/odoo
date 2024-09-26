# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class DocumentType(models.Model):
    _name = 'document.type'
    _description = 'Document Type'
    _rec_name = 'name'

    name = fields.Char('Name', track_visibility='always')
