# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class CvMappingLog(models.Model):
    _name = "cv_mapping_log"
    _description = "CV Mapping Log"



    remark = fields.Text(readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'), 
        ('applied', 'Applied'), 
        ('tagged', 'Tagged'), 
        ('approve', 'Approved'), 
        ('reject', 'Rejected'),
        ('cancel', 'Cancelled'),], string='Status', default='draft')
    date = fields.Date()
    action_taken_by = fields.Char("Action Taken By")
    reg_id = fields.Many2one('hr.cv.mapping')
