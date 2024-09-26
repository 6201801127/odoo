# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class WalkinMeetingDetails(models.Model):

    _name = "kw_walk_in_meeting_details"
    _description = "Details Of Walk In Meeting scheduled with applicants."

    walk_in_meeting_id  = fields.Many2one('kw_recruitment_walk_in_meeting',string="Walk In Meeting",required=True,ondelete='cascade')
    applicant_id        = fields.Many2one('hr.applicant',string="Applicant",required=True)
    meeting_url         = fields.Char("Meeting URL",required=True)

