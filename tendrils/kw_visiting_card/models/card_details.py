# -*- coding: utf-8 -*-
from datetime import date, datetime
import werkzeug
from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError


class ApplyCardDetails(models.Model):
    _name = 'kw_visiting_card_details'
    _description = 'Apply Card Details'

    card_id = fields.Many2one('kw_visiting_card_apply', string='Card ID', ondelete='cascade')
    action_date = fields.Date(string='Action Taken On', default=fields.Date.context_today)
    action_status = fields.Char('Status')
    action_uid = fields.Many2one('res.users', string='Action Taken By', default=lambda self: self.env.user.id)
    remarks = fields.Char(string='Remarks', required=True)
