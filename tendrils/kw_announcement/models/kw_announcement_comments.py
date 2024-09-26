# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class kw_announcement_comments(models.Model):
    _name = 'kw_announcement_comments'
    _description = 'Announcement Comments'
    _rec_name = 'comments'

    announcement_id = fields.Many2one(string=u'Announcement', comodel_name='kw_announcement', ondelete='cascade',
                                      required=True)
    comments = fields.Text(string="Write a comment", required=True)
