# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class Resolve_Issue(models.Model):
    _name = 'resolve.issue'
    _description = 'Resolve Issue'
    _rec_name = "issue_names"


    issue_names = fields.Many2one(comodel_name="manage.issue", string="Issue Name")
    comment = fields.Text(string="Comment")
    user_email = fields.Char('Login')
    comment_date =fields.Datetime('Authentication Date', default=datetime.today())

    @api.model
    def default_get(self, fields):
        res = super(Resolve_Issue, self).default_get(fields)
        res['user_email'] = self.env.user.login
        print("res------>", res)
        print("fields------>", fields)
        return res

    
class ResUser(models.Model):
    _inherit ='res.users'
    _rec_name ='login'

    

