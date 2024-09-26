# -*- coding: utf-8 -*-
from odoo import models, fields, api

class HeadSubHeadConfig(models.Model):
    _name = 'kw_eq_acc_head_sub_head'
    _description = 'Account head and sub head configuration'
    _rec_name = 'account_subhead_id'

    account_head_id = fields.Many2one('account.head')
    account_subhead_id = fields.Many2one('account.sub.head')
    code = fields.Char(string="code")
    total_profit_percentage = fields.Float(string='Total Profit Percentage')
    effective_date = fields.Date(string="Effective Date")
    sort_no = fields.Integer()


    @api.onchange('account_head_id')
    def _get_sub_heads(self):
        self.account_subhead_id = False
        if self.account_head_id:
            return {'domain': {'account_subhead_id': [('account_head', '=', self.account_head_id.id)]}}
        
    
    # @api.depends('write_date')
    # def compute_effective_date(self):
    #     for rec in self:
    #         rec.effective_date = rec.write_date.date()