# -*- coding: utf-8 -*-
from email.policy import default
from odoo import models, fields, api
from datetime import datetime


class ClearanceLog(models.Model):
    _name = "kw_clearance_log"
    _description = "EOS Clearance"

    applicant_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    remark = fields.Char(readonly=True)
    ra = fields.Boolean(readonly=True, default=False)
    it = fields.Boolean(readonly=True, default=False)
    admin = fields.Boolean(readonly=True, default=False)
    finance = fields.Boolean(readonly=True, default=False)
    eos_id = fields.Many2one('kw_eos_checklist',readonly=True)
    offboarding_id = fields.Many2one('kw_resignation',readonly=True)
