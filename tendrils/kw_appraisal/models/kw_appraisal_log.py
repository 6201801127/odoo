# -*- coding: utf-8 -*-
from odoo import models, fields, api


class kw_appraisal_log(models.Model):
    _name = "kw_appraisal_log"
    _description = "Stores Appraisal Log"
    # _order = "create_date desc"

    name = fields.Char(string="Name")
    date = fields.Date(string='Date', default=fields.Date.context_today, )
    payload = fields.Char(string="Payload")
    status = fields.Char("Status")
