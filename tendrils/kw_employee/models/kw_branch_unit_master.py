# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import float_compare
from lxml import etree
from datetime import date


class KwBranchUnit(models.Model):
    _name = 'accounting.branch.unit'
    _description = 'accounting.branch.unit'

    name = fields.Char('Name')
    code = fields.Char('Code')
