# -*- coding: utf-8 -*-
import base64
import logging
import mimetypes
from odoo.tools.mimetypes import guess_mimetype
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError

class kw_info(models.Model):
    _name = 'kw_info'
    _description = "Kwantify Informations"
    _rec_name = 'title'

    title = fields.Char("Title")
    description = fields.Text("Description")
    date = fields.Date("Date",default=fields.Date.context_today)
    
    attachment = fields.Binary(
        string=u'attachment',
    )
    filename=fields.Char("filename")


                