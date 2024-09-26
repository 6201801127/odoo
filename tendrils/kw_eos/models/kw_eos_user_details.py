# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class UserDetails(models.Model):
    _name = "kw_eos_user_details"
    _description = "User Details"
    _rec_name = 'employee_id'

    department_id = fields.Many2one('hr.department', string='Department')
    division = fields.Many2one('hr.department', string="Division")
    section = fields.Many2one('hr.department', string="Practice")
    practise = fields.Many2one('hr.department', string="Section")
    employee_id = fields.Many2one('hr.employee', string='Name')
    job_id = fields.Many2one('hr.job', string="Job Position")
    apply_date = fields.Date(string='Apply Date')
    offboarding_type = fields.Many2one('kw_offboarding_type_master', string='Resignation Type')
    reason = fields.Text(string="Reason For Resignation")
    effective_from = fields.Date(string='Effective From Date')
    last_working_date = fields.Date(string='Last Working Date')

    resignation_ids = fields.One2many('kw_eos_user_status', 'user_details_id', string='Approval Details')


class KwResignationLog(models.Model):
    _name = "kw_resignation_log"
    _description = "Offboarding"

    applicant_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    state = fields.Selection(
        [('apply', 'Applied'),
         ('forward', 'Forwarded'),
         ('confirm', 'Approved'),
         ('grant', 'Granted'),
         ('hold', 'Hold'),
         ('reject', 'Rejected'),
         ('cancel', 'Cancelled'),
         ('cancelreject', 'Cancellation Request Rejected'),
         ('rlcancel_approve', 'RL Cancellation Approve'),
         ('waiting_for_rl_cancellation', 'Applied for RL Cancellation'),
         ('pending_at_finance', 'Pending At Finance'),
         ('submit_by_finance', 'Submitted by Finance'),
         ('close','Closed')], string='Status', default='apply', readonly=True)
    date = fields.Date(readonly=True)
    remark = fields.Text(readonly=True)
    last_working_date = fields.Date(readonly=True)
    reg_id = fields.Many2one('kw_resignation')
