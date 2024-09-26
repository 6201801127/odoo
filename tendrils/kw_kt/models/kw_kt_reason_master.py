# -*- coding: utf-8 -*-
from odoo import models, fields, api


class kw_kt_reason_master(models.Model):
    _name = "kw_kt_reason_master"
    _description = "KT Reason Master Model"
    # _rec_name = 'category_name'

    reason = fields.Char(string="Reason")
