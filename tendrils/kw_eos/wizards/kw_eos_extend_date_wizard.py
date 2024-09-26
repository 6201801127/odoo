import json
import requests
from datetime import datetime, date, timedelta
from ast import literal_eval
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class kw_eos_extend_date(models.TransientModel):
    _name = 'kw_eos_extend_date'
    _description = "EOS wizard"

    resignation_id = fields.Many2one('kw_resignation', string="Resignation ID",
                                     default=lambda self: self.env.context.get('current_record_id'))
    extend_date = fields.Date(string="Extend Date")

    @api.multi
    def validate_extend_date(self):
        # offboarding
        self.resignation_id.last_working_date = self.extend_date
        # KT
        kt_record = self.env['kw_kt_view'].sudo().search(
            [('applicant_id', '=', self.resignation_id.applicant_id.id),
             ('kt_type_id', '=', self.resignation_id.offboarding_type.id)], limit=1)
        if kt_record:
            kt_record.last_working_date = self.extend_date
        self.env.user.notify_success(message='Last Working Date Extended.')
