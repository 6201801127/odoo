# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class InfoSource(models.Model):
    _name = "kw_recruitment_info_source"
    _description = "Holds different information sources for an applicant"

    name = fields.Char("Source", required=True)
