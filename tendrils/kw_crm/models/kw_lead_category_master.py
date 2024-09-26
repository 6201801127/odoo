# -*- coding: utf-8 -*-

from odoo import models, fields, api


class kw_lead_category_master(models.Model):
    _name = 'kw_lead_category_master'
    _description = 'Lead category Master'

    name = fields.Char(string='Name', )
    project_id = fields.Many2one('crm.lead', string='Parent Product', )
    active = fields.Boolean('Status', default=True)
