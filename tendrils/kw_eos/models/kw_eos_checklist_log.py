# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class EOSChecklistLog(models.Model):
    _name = "kw_eos_checklist_log"
    _description = "EOS Checklist"

    applicant_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    state = fields.Selection([('Draft', 'Draft'),
                              ('Applied', 'Applied'),
                              ('Approved', 'Approved'),
                              ('Granted', 'Granted'),
                              ('Rejected', 'Rejected')
                              ], default='Draft', readonly=True)
    date = fields.Date(readonly=True)
    last_working_date = fields.Date(readonly=True)
    remark = fields.Char(readonly=True)
    eos_id = fields.Many2one('kw_eos_checklist')
