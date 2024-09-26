# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class kw_release_notes(models.Model):
    _name           = 'kw_release_notes'
    _description    = "Kwantify Informations"
    _rec_name       = 'title'

    title           = fields.Char("Title")
    description     = fields.Text("Description")
    date            = fields.Date("Date",default=fields.Date.context_today)
    
    # attachment = fields.Binary(
    #     string=u'attachment',
    # )
    # filename=fields.Char("filename")