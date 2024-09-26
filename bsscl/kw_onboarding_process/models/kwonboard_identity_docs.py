# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError

import datetime
from datetime import date, datetime
# from lxml import etree
import os, base64

# import mimetypes
# from odoo.tools.mimetypes import guess_mimetype


class kwonboard_identity_docs(models.Model):
    _name = 'kwonboard_identity_docs'
    _description = "A model to store different identity documents of on-boarding."
    _rec_name = 'name'

    name = fields.Selection(string="Identification Type",
                            selection=[('1', 'PAN'), ('2', 'Passport'), ('3', 'Driving Licence'), ('4', 'Voter ID'),
                                       ('5', 'AADHAAR')], required=True)
    doc_number = fields.Char(string="Document Number", required=True, size=100)
    date_of_issue = fields.Date(string="Date of Issue")
    date_of_expiry = fields.Date(string="Date of Expiry")
    renewal_sts = fields.Boolean("Renewal Applied", default=False)
    uploaded_doc = fields.Binary(string="Document Upload", attachment=True, )
    filename = fields.Char('File Name')
    enrole_id = fields.Many2one('kwonboard_enrollment', ondelete='cascade', string="Enrollment ID", )
