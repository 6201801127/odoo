# -*- coding: utf-8 -*-
from odoo import models, fields, api


class NewsletterLog(models.Model):
    _name = "kw_newsletter_log"
    _description = "Stores sync log of csm website newsletter."
    _order = "create_date desc"

    name = fields.Char(string="Name")
    date = fields.Date(string='Date', default=fields.Date.context_today, )
    status = fields.Char("Status")
