# -*- coding: utf-8 -*-

from odoo import models, fields, api
from openerp.exceptions import ValidationError


class Manage_Issue(models.Model):
    _name = 'manage.issue'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Manage Issue'
    _rec_name = 'issue_name'


    issue_name = fields.Char(string = "Issue Name")
    comment_count = fields.Integer(string='Comment Count',compute="_compute_comment_count") 
    comment_ids = fields.One2many(comodel_name="resolve.issue", inverse_name="issue_names", string="Comment", readonly=True)
    state = fields.Selection([('open', 'Open'), ('close', 'Close')], string="Status", default='open')


    _sql_constraints = [
        ('name_uniq', 'unique (issue_name)', " This type of issue already exist!"),
    ]


    def _compute_comment_count(self):
        comment_count = self.env['resolve.issue'].search_count([])
        self.comment_count = comment_count

    def close_issue(self):
        self.state = 'close'
        return True

    def reopen_issue(self):
        self.state = 'open'
        return True

    def total_comment(self):
        comt = self.env['resolve.issue'].search([])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Comment',
            'res_model': 'resolve.issue',
            'domain': [],
            'view_mode': 'tree,form',
            'target': 'current'
        }

    
   
        
       

      
    



