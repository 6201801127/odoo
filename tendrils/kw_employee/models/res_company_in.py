# -*- coding: utf-8 -*-

from odoo import models, fields, api


class res_company_in(models.Model):
    _inherit = 'res.company'

    company_code = fields.Char(string=u'Company Code', help=u"Prefix for Employee Code")
