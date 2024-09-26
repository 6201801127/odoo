# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
import re


class CounsellingMeetingScheduleIn(models.Model):
    _inherit = "kw_meeting_events"

    # def isValidURL(self, url):
    #     # Regex to check valid URL
    #     regex = ("((http|https)://)(www.)?" +
    #              "[a-zA-Z0-9@:%._\\-+~#?&//=]" +
    #              "{2,256}\\.[a-z]" +
    #              "{2,6}\\b([-a-zA-Z0-9@:%" +
    #              "._\\+~#?&//=]*)")

    #     # Compile the ReGex
    #     p = re.compile(regex)

    #     # If the string is empty
    #     # return false
    #     if (url == None):
    #         return False

    #     # Return if the string
    #     # matched the ReGex
    #     if (re.search(p, url)):
    #         return True
    #     else:
    #         return False

    # @api.constrains('other_meeting_url')
    # def validate_other_meeting_url(self):
    #     if self.other_meeting_url:
    #         if not (self.isValidURL(self.other_meeting_url) == True):
    #             raise ValidationError("Please use a proper URL.")

    @api.model
    def create(self, values):
        meeting = super(CounsellingMeetingScheduleIn, self).create(values)
        try:
            if 'active_model' in self._context and 'active_id' in self._context:

                counselling_rec = []
                if 'active_model' in self._context and self._context['active_model'] == 'kw_pip_counselling_details':
                    counselling_rec = self.env['kw_pip_counselling_details'].browse(self._context['active_id'])
                if counselling_rec and counselling_rec.in_observe == False:
                    data = {
                        'meeting_id': meeting.id,
                        'assessment_date': meeting.kw_start_meeting_date,
                        'feedback_status': '1'
                    }
                    counselling_rec.write(data)
                    self.env['counselling_configuration_log'].create({
                        'config_details_id': counselling_rec.id,
                        'meeting_id': meeting.id
                    })
                else:
                    data = {
                        'meeting_id': meeting.id,
                        'assessment_date': meeting.kw_start_meeting_date,
                        'feedback_status': '4'
                    }
                    counselling_rec.write(data)
                    self.env['counselling_configuration_log'].create({
                        'config_details_id': counselling_rec.id,
                        'meeting_id': meeting.id
                    })

        except Exception as e:
            pass

        return meeting

    @api.multi
    def write(self, values):
        result = super(CounsellingMeetingScheduleIn, self).write(values)
        try:

            for meeting in self:
                details_counselling = self.env['kw_pip_counselling_details'].sudo().search(
                    [('meeting_id', '=', meeting.id)])

                data = {
                    'counselling_date': meeting.kw_start_meeting_date,
                }

                if details_counselling:
                    details_counselling.write(data)

        except Exception as e:
            pass
        return result
