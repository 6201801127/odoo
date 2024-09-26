# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
import datetime
from datetime import date, datetime

import re
import time

import os, base64
# import mimetypes
# from odoo.tools.mimetypes import guess_mimetype



class kwonboard_work_experience(models.Model):
    _name = 'kwonboard_work_experience'
    _description = "Work experience of on-boardings."

    country_id = fields.Many2one('res.country', string="Country Name", required=True)
    name = fields.Char(string="Previous Organization Name", required=True, size=100)
    designation_name = fields.Char(string="Job Profile ", required=True, size=100)
    organization_type = fields.Char(string="Organization Type", required=True)
    industry_type = fields.Char(string="Industry Type", )

    effective_from = fields.Date(string="Effective From")
    effective_to = fields.Date(string="Effective To")
    uploaded_doc = fields.Binary(string="Document Upload", attachment=True,)
    filename = fields.Char("file name", )

    enrole_id = fields.Many2one('kwonboard_enrollment', ondelete='cascade', string="Enrollment ID", )
