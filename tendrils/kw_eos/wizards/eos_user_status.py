# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class UserDetailsDetails(models.Model):
    _name = "kw_eos_user_status"
    _description = "User Status"

    user_details_id = fields.Many2one('kw_eos_user_details')
    applicant_id = fields.Many2one('hr.employee')
    state = fields.Selection(
        [('apply', 'Applied'),
         ('forward', 'Forwarded'),
         ('confirm', 'Approved'),
         ('grant', 'Granted'),
         ('hold', 'Hold'),
         ('reject', 'Rejected')], string='Status', default='apply')
    date = fields.Date()
    remark = fields.Text()
    last_working_date = fields.Date()
    reg_id = fields.Many2one('kw_resignation')

   




 