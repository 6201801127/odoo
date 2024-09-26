# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError
import pdb

class kw_noc(models.Model):
    _name = "kw_noc"
    _description = "No Objection Master"
    _rec_name = 'applicant_id'
    _order = 'id'

    applicant_id = fields.Many2one('hr.applicant', string="Applicant Name")
    department_id = fields.Many2one('hr.department', string="Department")
    division = fields.Many2one('hr.department', string="Division")
    section = fields.Many2one('hr.department', string="Practice")
    practise = fields.Many2one('hr.department', string="Section")
    date_joining = fields.Date('Date of Joining')
    date_resignation = fields.Date('Resignation Date')
    date_last = fields.Date('Last Date')
    remark = fields.Text('Remarks')