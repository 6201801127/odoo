# -*- coding: utf-8 -*-
# For Default branch/HO of company, Created By: T Ketaki Debadarshini

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    branch_ids          = fields.One2many('kw_res_branch', 'company_id', 'Branches')
    head_branch_id      = fields.Many2one('kw_res_branch', 'Default Branch', ondelete='restrict')

    
    