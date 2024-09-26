# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError,UserError
from lxml import etree

class kw_lv_meeting(models.Model):
    _name = 'kw_lv_meeting'
    _description = 'Local Visit Meeting'

    @api.model
    def _get_meeting_time_list(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=7, minute=45, second=0, microsecond=0)
        end_loop = dt.replace(hour=22, minute=0, second=0, microsecond=0)
        time_list = []
        while start_loop < end_loop:
            start_loop = (start_loop+relativedelta(minutes=+15))
            time_list.append((start_loop.strftime('%H:%M'),
                              start_loop.strftime('%I:%M %p')))
        return time_list
    
    organization = fields.Many2one(comodel_name='res.partner',string='Customer/Organization',required=True,ondelete='restrict')
    contact_person = fields.Many2one(comodel_name='res.partner',string='Contact Person',required=True,ondelete='restrict')
    from_time = fields.Selection(string='From Time',selection='_get_meeting_time_list',required=True)
    to_time = fields.Selection(string='To Time',selection='_get_meeting_time_list',required=True)
    visit_place = fields.Char(string='Place of Visit',required=True)
    subject = fields.Char(string='Subject',required=True)
    details = fields.Text(string='Details',required=True)
    business_id = fields.Many2one(comodel_name='kw_lv_business',string='Business Id',ondelete='restrict')

    @api.onchange('organization')
    def _set_organisation_and_contact(self):
        self.contact_person = False
        if self.organization:
            return {'domain': {'contact_person': [('parent_id', 'in', self.organization.ids)]}}
        else:
            pass
    
    # @api.constrains('from_time','to_time')
    # def validate_meeting_time(self):
    #     if 'tz' in self._context:
    #         user_tz = pytz.timezone(self._context.get('tz') if self._context.get('tz') != False else 'Asia/Kolkata')
    #     else:
    #         pass
    #     dt = datetime.now(user_tz)
    #     current_time = dt.strftime('%H:%M')
    #     if self.from_time and self.from_time < current_time:
    #         raise ValidationError(f'Meeting From-time should be greater than current time.')
    #     elif self.from_time and self.to_time and self.from_time >= self.to_time:
    #         raise ValidationError(f'Meeting To-time should be less than From-time.')
    #     else:
    #         pass